"""Tests for Business Process Analysis (BPA) Agent."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from agents.bpa_agent import BPAAgent, ProblemValidationResult, CompetitorAnalysis
from models.data_models import ProductState, BusinessModel, FeatureSpec
from models.enums import MVPPriority, MarketValidationLevel


class TestBPAAgent:
    """Test cases for BPA Agent functionality."""
    
    @pytest.fixture
    def bpa_agent(self):
        """Create a BPA agent instance for testing."""
        return BPAAgent(api_key="test-key")
    
    @pytest.fixture
    def sample_product_state(self):
        """Create a sample product state for testing."""
        return ProductState(
            user_query="Build an AI-powered project management tool for small teams",
            session_id="test-session",
            current_phase="discovery"
        )
    
    @pytest.fixture
    def sample_problem_validation(self):
        """Create a sample problem validation result."""
        return ProblemValidationResult(
            problem_score=8,
            market_size_score=7,
            solution_fit_score=8,
            overall_score=7.7,
            reasoning="Strong problem with good market potential",
            recommendations=["Validate with target customers", "Research competitors"],
            should_continue=True,
            validation_questions=["What specific pain points do teams face?"]
        )
    
    @pytest.fixture
    def sample_business_model(self):
        """Create a sample business model."""
        return BusinessModel(
            value_proposition="AI-powered project management for small teams",
            target_customer="Small tech teams (5-20 people) struggling with project coordination",
            revenue_streams=["Monthly subscription", "Premium features"],
            cost_structure=["Development", "AI API costs", "Marketing"],
            key_metrics=["Monthly Recurring Revenue", "Customer Acquisition Cost", "Churn Rate"]
        )
    
    @pytest.fixture
    def sample_competitors(self):
        """Create sample competitor analysis."""
        return [
            CompetitorAnalysis(
                competitor_name="Asana",
                value_proposition="Team collaboration and project tracking",
                target_market="Small to medium teams",
                pricing_model="Freemium with paid tiers",
                key_strengths=["Established brand", "Feature rich"],
                market_gaps=["Limited AI features", "Complex for small teams"],
                differentiation_opportunities=["AI automation", "Simpler UX"]
            )
        ]
    
    @pytest.mark.asyncio
    async def test_analyze_business_viability_success(self, bpa_agent, sample_product_state):
        """Test successful business viability analysis."""
        # Mock the internal methods
        with patch.object(bpa_agent, '_validate_problem_space') as mock_validate, \
             patch.object(bpa_agent, '_generate_business_model') as mock_business, \
             patch.object(bpa_agent, '_analyze_competitors') as mock_competitors, \
             patch.object(bpa_agent, '_generate_mvp_features') as mock_features:
            
            # Setup mocks
            mock_validate.return_value = ProblemValidationResult(
                problem_score=8, market_size_score=7, solution_fit_score=8,
                overall_score=7.7, reasoning="Good opportunity",
                recommendations=["Proceed"], should_continue=True
            )
            
            mock_business.return_value = BusinessModel(
                value_proposition="Test value prop",
                target_customer="Test customer",
                revenue_streams=["Subscription"],
                key_metrics=["MRR"]
            )
            
            mock_competitors.return_value = []
            mock_features.return_value = []
            
            # Execute
            result = await bpa_agent.analyze_business_viability(sample_product_state)
            
            # Verify
            assert result.current_phase == "planning"
            assert "overall_score" in result.market_validation
            assert result.business_model is not None
            assert mock_validate.called
            assert mock_business.called
            assert mock_competitors.called
            assert mock_features.called
    
    @pytest.mark.asyncio
    async def test_analyze_business_viability_low_score(self, bpa_agent, sample_product_state):
        """Test business viability analysis with low score (should stop)."""
        with patch.object(bpa_agent, '_validate_problem_space') as mock_validate:
            # Setup mock with low score
            mock_validate.return_value = ProblemValidationResult(
                problem_score=3, market_size_score=4, solution_fit_score=5,
                overall_score=4.0, reasoning="Weak opportunity",
                recommendations=["Reconsider"], should_continue=False
            )
            
            # Execute
            result = await bpa_agent.analyze_business_viability(sample_product_state)
            
            # Verify - should stop at validation phase
            assert result.current_phase == "validation"
            assert result.market_validation["overall_score"] == "4.0"
            assert result.market_validation["should_continue"] == "False"
            assert result.business_model is None  # Should not proceed to business model
    
    @pytest.mark.asyncio
    async def test_validate_problem_space_success(self, bpa_agent):
        """Test successful problem space validation."""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '''
        {
            "problem_score": 8,
            "market_size_score": 7,
            "solution_fit_score": 8,
            "overall_score": 7.7,
            "reasoning": "Strong problem with good market potential",
            "recommendations": ["Validate with customers", "Research competitors"],
            "should_continue": true,
            "validation_questions": ["What specific pain points?", "How do teams currently solve this?"]
        }
        '''
        
        with patch.object(bpa_agent.client.chat.completions, 'create', return_value=mock_response):
            with patch('asyncio.to_thread', side_effect=lambda func, *args, **kwargs: func(*args, **kwargs)):
                result = await bpa_agent._validate_problem_space("Test project idea")
                
                assert result.problem_score == 8
                assert result.market_size_score == 7
                assert result.solution_fit_score == 8
                assert result.overall_score == 7.7
                assert result.should_continue is True
                assert len(result.recommendations) == 2
                assert len(result.validation_questions) == 2
    
    @pytest.mark.asyncio
    async def test_validate_problem_space_error_handling(self, bpa_agent):
        """Test problem space validation error handling."""
        # Mock OpenAI to raise an exception
        with patch.object(bpa_agent.client.chat.completions, 'create', side_effect=Exception("API Error")):
            with patch('asyncio.to_thread', side_effect=Exception("API Error")):
                result = await bpa_agent._validate_problem_space("Test project idea")
                
                # Should return low-score result
                assert result.overall_score == 3.0
                assert result.should_continue is False
                assert "API Error" in result.reasoning
    
    @pytest.mark.asyncio
    async def test_generate_business_model_success(self, bpa_agent, sample_problem_validation):
        """Test successful business model generation."""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '''
        {
            "value_proposition": "AI project management for teams",
            "target_customer": "Small tech teams needing better coordination",
            "revenue_streams": ["Monthly subscription", "Premium features"],
            "cost_structure": ["Development", "AI costs"],
            "key_metrics": ["MRR", "CAC", "Churn"]
        }
        '''
        
        with patch.object(bpa_agent.client.chat.completions, 'create', return_value=mock_response):
            with patch('asyncio.to_thread', side_effect=lambda func, *args, **kwargs: func(*args, **kwargs)):
                result = await bpa_agent._generate_business_model("Test query", sample_problem_validation)
                
                assert isinstance(result, BusinessModel)
                assert result.value_proposition == "AI project management for teams"
                assert len(result.revenue_streams) == 2
                assert len(result.key_metrics) == 3
    
    @pytest.mark.asyncio
    async def test_generate_business_model_error_handling(self, bpa_agent, sample_problem_validation):
        """Test business model generation error handling."""
        with patch.object(bpa_agent.client.chat.completions, 'create', side_effect=Exception("API Error")):
            with patch('asyncio.to_thread', side_effect=Exception("API Error")):
                result = await bpa_agent._generate_business_model("Test query", sample_problem_validation)
                
                # Should return minimal valid business model
                assert isinstance(result, BusinessModel)
                assert result.value_proposition == "Solve customer problems efficiently"
                assert len(result.revenue_streams) >= 1
                assert len(result.key_metrics) >= 1
    
    @pytest.mark.asyncio
    async def test_analyze_competitors_success(self, bpa_agent):
        """Test successful competitor analysis."""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '''
        {
            "competitors": [
                {
                    "competitor_name": "Asana",
                    "value_proposition": "Team collaboration platform",
                    "target_market": "Small to medium teams",
                    "pricing_model": "Freemium",
                    "key_strengths": ["Established", "Feature-rich"],
                    "market_gaps": ["Limited AI", "Complex UI"],
                    "differentiation_opportunities": ["AI automation", "Simpler UX"]
                }
            ]
        }
        '''
        
        with patch.object(bpa_agent.client.chat.completions, 'create', return_value=mock_response):
            with patch('asyncio.to_thread', side_effect=lambda func, *args, **kwargs: func(*args, **kwargs)):
                result = await bpa_agent._analyze_competitors("Small teams", "Project management tool")
                
                assert len(result) == 1
                assert isinstance(result[0], CompetitorAnalysis)
                assert result[0].competitor_name == "Asana"
                assert len(result[0].key_strengths) == 2
                assert len(result[0].market_gaps) == 2
    
    @pytest.mark.asyncio
    async def test_generate_mvp_features_success(self, bpa_agent, sample_business_model, sample_competitors):
        """Test successful MVP feature generation."""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '''
        {
            "features": [
                {
                    "name": "User Registration",
                    "user_story": "As a team member, I want to create an account, so that I can access the platform",
                    "acceptance_criteria": [
                        "WHEN user provides valid email THEN system SHALL create account",
                        "WHEN registration succeeds THEN system SHALL send confirmation",
                        "GIVEN existing email WHEN user registers THEN system SHALL show error"
                    ],
                    "mvp_priority": "CORE",
                    "effort_estimate": "S",
                    "business_impact": "High",
                    "dependencies": []
                },
                {
                    "name": "Project Creation",
                    "user_story": "As a team lead, I want to create projects, so that I can organize work",
                    "acceptance_criteria": [
                        "WHEN user creates project THEN system SHALL save project data",
                        "WHEN project is created THEN system SHALL assign owner permissions",
                        "GIVEN valid project data WHEN user submits THEN system SHALL confirm creation"
                    ],
                    "mvp_priority": "CORE",
                    "effort_estimate": "M",
                    "business_impact": "Critical",
                    "dependencies": ["User Registration"]
                }
            ]
        }
        '''
        
        with patch.object(bpa_agent.client.chat.completions, 'create', return_value=mock_response):
            with patch('asyncio.to_thread', side_effect=lambda func, *args, **kwargs: func(*args, **kwargs)):
                result = await bpa_agent._generate_mvp_features(sample_business_model, sample_competitors)
                
                assert len(result) == 2
                assert all(isinstance(feature, FeatureSpec) for feature in result)
                
                # Check first feature
                feature1 = result[0]
                assert feature1.name == "User Registration"
                assert feature1.mvp_priority == MVPPriority.CORE
                assert feature1.effort_estimate == "S"
                assert feature1.business_impact == "High"
                assert len(feature1.acceptance_criteria) == 3
                
                # Check that user story follows format
                assert "As a" in feature1.user_story
                assert "I want" in feature1.user_story
                assert "so that" in feature1.user_story
    
    @pytest.mark.asyncio
    async def test_generate_mvp_features_core_limit(self, bpa_agent, sample_business_model, sample_competitors):
        """Test that MVP feature generation limits core features to 3."""
        # Mock response with 5 CORE features
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '''
        {
            "features": [
                {
                    "name": "Feature 1",
                    "user_story": "As a user, I want feature 1, so that I can do something",
                    "acceptance_criteria": ["WHEN x THEN y SHALL z", "WHEN a THEN b SHALL c", "WHEN d THEN e SHALL f"],
                    "mvp_priority": "CORE",
                    "effort_estimate": "S",
                    "business_impact": "High",
                    "dependencies": []
                },
                {
                    "name": "Feature 2",
                    "user_story": "As a user, I want feature 2, so that I can do something",
                    "acceptance_criteria": ["WHEN x THEN y SHALL z", "WHEN a THEN b SHALL c", "WHEN d THEN e SHALL f"],
                    "mvp_priority": "CORE",
                    "effort_estimate": "S",
                    "business_impact": "High",
                    "dependencies": []
                },
                {
                    "name": "Feature 3",
                    "user_story": "As a user, I want feature 3, so that I can do something",
                    "acceptance_criteria": ["WHEN x THEN y SHALL z", "WHEN a THEN b SHALL c", "WHEN d THEN e SHALL f"],
                    "mvp_priority": "CORE",
                    "effort_estimate": "S",
                    "business_impact": "High",
                    "dependencies": []
                },
                {
                    "name": "Feature 4",
                    "user_story": "As a user, I want feature 4, so that I can do something",
                    "acceptance_criteria": ["WHEN x THEN y SHALL z", "WHEN a THEN b SHALL c", "WHEN d THEN e SHALL f"],
                    "mvp_priority": "CORE",
                    "effort_estimate": "S",
                    "business_impact": "High",
                    "dependencies": []
                },
                {
                    "name": "Feature 5",
                    "user_story": "As a user, I want feature 5, so that I can do something",
                    "acceptance_criteria": ["WHEN x THEN y SHALL z", "WHEN a THEN b SHALL c", "WHEN d THEN e SHALL f"],
                    "mvp_priority": "CORE",
                    "effort_estimate": "S",
                    "business_impact": "High",
                    "dependencies": []
                }
            ]
        }
        '''
        
        with patch.object(bpa_agent.client.chat.completions, 'create', return_value=mock_response):
            with patch('asyncio.to_thread', side_effect=lambda func, *args, **kwargs: func(*args, **kwargs)):
                result = await bpa_agent._generate_mvp_features(sample_business_model, sample_competitors)
                
                # Count core features - should be limited to 3
                core_features = [f for f in result if f.mvp_priority == MVPPriority.CORE]
                assert len(core_features) <= 3
    
    def test_problem_validation_result_model(self):
        """Test ProblemValidationResult model validation."""
        # Valid data
        valid_data = {
            "problem_score": 8,
            "market_size_score": 7,
            "solution_fit_score": 9,
            "overall_score": 8.0,
            "reasoning": "Strong opportunity",
            "recommendations": ["Proceed with development"],
            "should_continue": True
        }
        
        result = ProblemValidationResult(**valid_data)
        assert result.problem_score == 8
        assert result.should_continue is True
        
        # Invalid score (out of range)
        with pytest.raises(ValueError):
            ProblemValidationResult(
                problem_score=11,  # Invalid - should be 1-10
                market_size_score=7,
                solution_fit_score=8,
                overall_score=8.0,
                reasoning="Test",
                recommendations=["Test"],
                should_continue=True
            )
    
    def test_competitor_analysis_model(self):
        """Test CompetitorAnalysis model validation."""
        valid_data = {
            "competitor_name": "Test Competitor",
            "value_proposition": "Test value prop",
            "target_market": "Test market"
        }
        
        competitor = CompetitorAnalysis(**valid_data)
        assert competitor.competitor_name == "Test Competitor"
        assert competitor.key_strengths == []  # Default empty list
        assert competitor.market_gaps == []  # Default empty list