"""Tests for ProductTransitionAgent."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agents.product_transition_agent import ProductTransitionAgent, RoadmapPhase, ExecutionChecklist
from models.data_models import BusinessModel, FeatureSpec, GTMStrategy, ProductState
from models.enums import MVPPriority, MarketValidationLevel


@pytest.fixture
def sample_business_model():
    """Sample business model for testing."""
    return BusinessModel(
        value_proposition="Streamline business processes efficiently",
        target_customer="Small to medium businesses",
        revenue_streams=["Subscription fees", "Professional services"],
        cost_structure=["Development", "Marketing", "Operations"],
        key_metrics=["MRR", "CAC", "LTV"]
    )


@pytest.fixture
def sample_feature_specs():
    """Sample feature specifications for testing."""
    return [
        FeatureSpec(
            name="User Authentication",
            user_story="As a user, I want to securely log in, so that I can access my account",
            acceptance_criteria=[
                "WHEN user enters valid credentials THEN system SHALL authenticate successfully",
                "WHEN user enters invalid credentials THEN system SHALL show error message",
                "GIVEN authenticated user WHEN session expires THEN system SHALL require re-authentication"
            ],
            mvp_priority=MVPPriority.CORE,
            effort_estimate="S",
            business_impact="High",
            validation_level=MarketValidationLevel.ASSUMPTION
        ),
        FeatureSpec(
            name="Dashboard Analytics",
            user_story="As a business owner, I want to view analytics, so that I can make informed decisions",
            acceptance_criteria=[
                "WHEN user accesses dashboard THEN system SHALL display key metrics",
                "WHEN data is updated THEN dashboard SHALL refresh automatically",
                "GIVEN user permissions WHEN viewing analytics THEN system SHALL show relevant data only"
            ],
            mvp_priority=MVPPriority.IMPORTANT,
            effort_estimate="M",
            business_impact="Medium",
            validation_level=MarketValidationLevel.ASSUMPTION
        )
    ]


@pytest.fixture
def sample_gtm_strategy():
    """Sample GTM strategy for testing."""
    return GTMStrategy(
        distribution_channels=["Direct sales", "Content marketing", "Partner network"],
        pricing_strategy="Subscription - $99/month",
        launch_timeline={
            "mvp_launch": "8-12 weeks: Core features, Beta testing",
            "growth": "3-6 months: Scale acquisition, Feature expansion",
            "expansion": "6-12 months: Market expansion, Partnerships"
        },
        success_metrics=["MRR growth 20%", "CAC < $100", "NPS > 50"],
        competitive_positioning="Premium solution with superior UX",
        budget_requirements="$50K initial investment"
    )


@pytest.fixture
def sample_product_state(sample_business_model, sample_feature_specs, sample_gtm_strategy):
    """Sample product state for testing."""
    return ProductState(
        user_query="Build a business process automation tool",
        business_model=sample_business_model,
        feature_specifications=sample_feature_specs,
        gtm_strategy=sample_gtm_strategy,
        current_phase="planning"
    )


class TestProductTransitionAgent:
    """Test cases for ProductTransitionAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance for testing."""
        with patch('openai.OpenAI'):
            return ProductTransitionAgent(api_key="test-key")
    
    @pytest.mark.asyncio
    async def test_generate_product_roadmap_success(self, agent, sample_product_state):
        """Test successful roadmap generation."""
        # Mock LLM responses
        mock_roadmap_response = {
            "phases": [
                {
                    "phase_name": "MVP Launch",
                    "timeline": "8-12 weeks",
                    "description": "Launch MVP with core features",
                    "key_features": ["User Authentication", "Core Dashboard"],
                    "success_criteria": ["10 paying customers", "Product-market fit signals", "Core features validated"],
                    "key_learnings": ["Customer behavior", "Product-market fit", "Core value validation"],
                    "deliverables": ["Working MVP", "Customer feedback", "Initial revenue"],
                    "risks_and_mitigation": ["Low adoption: Improve UX", "Technical issues: Testing"]
                },
                {
                    "phase_name": "Product Growth",
                    "timeline": "3-6 months",
                    "description": "Scale customer base and features",
                    "key_features": ["Advanced Analytics", "Integrations"],
                    "success_criteria": ["100 active users", "Positive unit economics", "Feature adoption > 60%"],
                    "key_learnings": ["Scaling challenges", "Customer acquisition", "Feature prioritization"],
                    "deliverables": ["Scaled product", "Growth metrics", "Optimized processes"],
                    "risks_and_mitigation": ["Scaling issues: Infrastructure", "Competition: Differentiation"]
                },
                {
                    "phase_name": "Market Expansion",
                    "timeline": "6-12 months",
                    "description": "Achieve market leadership",
                    "key_features": ["Enterprise Features", "API Platform"],
                    "success_criteria": ["Market leadership", "Strategic partnerships", "Sustainable growth"],
                    "key_learnings": ["Market dynamics", "Partnership value", "Long-term strategy"],
                    "deliverables": ["Market presence", "Partnerships", "Product ecosystem"],
                    "risks_and_mitigation": ["Market saturation: New segments", "Resources: Focus"]
                }
            ]
        }
        
        mock_checklist_response = {
            "checklists": [
                {
                    "category": "Product Development",
                    "validation_items": [
                        "Core features implemented and tested",
                        "User acceptance testing completed",
                        "Performance benchmarks met"
                    ],
                    "priority": "High",
                    "responsible_role": "Development Team"
                },
                {
                    "category": "Market Validation",
                    "validation_items": [
                        "Customer interviews conducted (min 20)",
                        "Product-market fit metrics established",
                        "Pricing strategy validated"
                    ],
                    "priority": "High",
                    "responsible_role": "Product Manager"
                },
                {
                    "category": "Business Operations",
                    "validation_items": [
                        "Revenue model validated",
                        "Unit economics positive",
                        "Customer support established",
                        "Legal requirements met"
                    ],
                    "priority": "Medium",
                    "responsible_role": "Business Operations"
                }
            ]
        }
        
        # Mock the OpenAI client responses
        def mock_create(*args, **kwargs):
            # Determine which call this is based on the prompt content
            messages = kwargs.get('messages', [])
            if messages and 'roadmap' in str(messages).lower():
                # Roadmap response
                mock_response = MagicMock()
                mock_response.choices = [MagicMock()]
                mock_response.choices[0].message.content = json.dumps(mock_roadmap_response)
                return mock_response
            else:
                # Checklist response
                mock_response = MagicMock()
                mock_response.choices = [MagicMock()]
                mock_response.choices[0].message.content = json.dumps(mock_checklist_response)
                return mock_response
        
        agent.client.chat.completions.create = AsyncMock(side_effect=mock_create)
        
        # Execute the method
        result_state = await agent.generate_product_roadmap(sample_product_state)
        
        # Verify the results
        assert result_state.current_phase == "mvp_design"
        assert len(result_state.mvp_roadmap) == 3
        assert result_state.mvp_roadmap[0]["phase_name"] == "MVP Launch"
        assert "10 paying customers" in result_state.mvp_roadmap[0]["success_criteria"]
        assert "Product-market fit signals" in result_state.mvp_roadmap[0]["success_criteria"]
        
        # Verify execution checklist is stored
        assert "execution_checklist" in result_state.market_validation
        checklist_data = json.loads(result_state.market_validation["execution_checklist"])
        assert len(checklist_data) >= 3  # Should have at least 3 categories
        
        # Verify total validation items >= 10
        total_items = sum(len(item["validation_items"]) for item in checklist_data)
        assert total_items >= 10
    
    @pytest.mark.asyncio
    async def test_generate_product_roadmap_no_business_model(self, agent):
        """Test roadmap generation fails without business model."""
        state = ProductState(user_query="Test query")
        
        with pytest.raises(ValueError, match="Business model is required"):
            await agent.generate_product_roadmap(state)
    
    @pytest.mark.asyncio
    async def test_generate_roadmap_phases_default_fallback(self, agent, sample_business_model, sample_feature_specs):
        """Test roadmap phase generation with fallback to defaults."""
        # Mock LLM to raise an exception
        agent.client.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))
        
        # Execute the method
        phases = await agent._generate_roadmap_phases(sample_business_model, sample_feature_specs, None)
        
        # Verify fallback behavior
        assert len(phases) == 3
        assert phases[0].phase_name == "MVP Launch"
        assert phases[1].phase_name == "Product Growth"
        assert phases[2].phase_name == "Market Expansion"
        
        # Verify Phase 1 has required success criteria
        phase1_criteria = phases[0].success_criteria
        assert any("10 paying customers" in criterion for criterion in phase1_criteria)
        assert any("Product-market fit signals" in criterion for criterion in phase1_criteria)
    
    @pytest.mark.asyncio
    async def test_generate_execution_checklist_default_fallback(self, agent, sample_business_model, sample_feature_specs):
        """Test execution checklist generation with fallback to defaults."""
        # Create sample roadmap phases
        phases = [
            RoadmapPhase(
                phase_name="MVP Launch",
                timeline="8-12 weeks",
                description="Test phase",
                key_features=["Feature 1"],
                success_criteria=["Criteria 1"],
                key_learnings=["Learning 1"],
                deliverables=["Deliverable 1"]
            )
        ]
        
        # Mock LLM to raise an exception
        agent.client.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))
        
        # Execute the method
        checklists = await agent._generate_execution_checklist(phases, sample_business_model, sample_feature_specs)
        
        # Verify fallback behavior
        assert len(checklists) >= 3
        
        # Count total validation items
        total_items = sum(len(checklist.validation_items) for checklist in checklists)
        assert total_items >= 10
        
        # Verify categories are present
        categories = [checklist.category for checklist in checklists]
        assert "Product Development & Technical" in categories
        assert "Market Validation & Customer" in categories
        assert "Business Operations & Finance" in categories
    
    def test_get_roadmap_summary_success(self, agent, sample_product_state):
        """Test roadmap summary generation."""
        # Add roadmap data to state
        sample_product_state.mvp_roadmap = [
            {
                "phase_name": "MVP Launch",
                "timeline": "8-12 weeks",
                "key_features": ["Feature 1", "Feature 2"],
                "success_criteria": ["Criteria 1", "Criteria 2"],
                "deliverables": ["Deliverable 1"]
            }
        ]
        
        # Add execution checklist
        checklist_data = [
            {
                "category": "Development",
                "validation_items": ["Item 1", "Item 2", "Item 3"],
                "priority": "High",
                "responsible_role": "Dev Team"
            }
        ]
        sample_product_state.market_validation["execution_checklist"] = json.dumps(checklist_data)
        
        # Execute the method
        summary = agent.get_roadmap_summary(sample_product_state)
        
        # Verify the summary
        assert summary["total_phases"] == 1
        assert len(summary["phases"]) == 1
        assert summary["phases"][0]["name"] == "MVP Launch"
        assert summary["phases"][0]["key_features_count"] == 2
        assert summary["phases"][0]["success_criteria_count"] == 2
        assert summary["phases"][0]["deliverables_count"] == 1
        
        # Verify execution checklist summary
        assert "execution_checklist" in summary
        assert summary["execution_checklist"]["categories"] == 1
        assert summary["execution_checklist"]["total_validation_items"] == 3
    
    def test_get_roadmap_summary_no_roadmap(self, agent):
        """Test roadmap summary when no roadmap exists."""
        state = ProductState(user_query="Test query")
        
        summary = agent.get_roadmap_summary(state)
        
        assert "error" in summary
        assert summary["error"] == "No roadmap generated"


class TestRoadmapPhase:
    """Test cases for RoadmapPhase model."""
    
    def test_roadmap_phase_creation(self):
        """Test RoadmapPhase model creation."""
        phase = RoadmapPhase(
            phase_name="Test Phase",
            timeline="4 weeks",
            description="Test description",
            key_features=["Feature 1", "Feature 2"],
            success_criteria=["Criteria 1", "Criteria 2"],
            key_learnings=["Learning 1", "Learning 2"],
            deliverables=["Deliverable 1", "Deliverable 2"]
        )
        
        assert phase.phase_name == "Test Phase"
        assert phase.timeline == "4 weeks"
        assert len(phase.key_features) == 2
        assert len(phase.success_criteria) == 2
        assert len(phase.key_learnings) == 2
        assert len(phase.deliverables) == 2
        assert len(phase.risks_and_mitigation) == 0  # Default empty list


class TestExecutionChecklist:
    """Test cases for ExecutionChecklist model."""
    
    def test_execution_checklist_creation(self):
        """Test ExecutionChecklist model creation."""
        checklist = ExecutionChecklist(
            category="Development",
            validation_items=["Item 1", "Item 2", "Item 3"],
            priority="High",
            responsible_role="Dev Team"
        )
        
        assert checklist.category == "Development"
        assert len(checklist.validation_items) == 3
        assert checklist.priority == "High"
        assert checklist.responsible_role == "Dev Team"