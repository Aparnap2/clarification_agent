"""Tests for GTM Strategy Agent."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from agents.gtm_strategy_agent import GTMStrategyAgent, ChannelAnalysis, PricingAnalysis, LaunchMilestone
from models.data_models import BusinessModel, GTMStrategy, ProductState, FeatureSpec
from models.enums import MVPPriority, MarketValidationLevel


@pytest.fixture
def sample_business_model():
    """Sample business model for testing."""
    return BusinessModel(
        value_proposition="Streamline business processes for SMBs",
        target_customer="Small to medium businesses with 10-100 employees",
        revenue_streams=["Monthly subscription", "Professional services"],
        cost_structure=["Development", "Marketing", "Support"],
        key_metrics=["MRR", "CAC", "LTV"]
    )


@pytest.fixture
def sample_competitive_analysis():
    """Sample competitive analysis for testing."""
    return [
        {
            "competitor_name": "CompetitorA",
            "value_proposition": "Business automation platform",
            "target_market": "SMBs",
            "pricing_model": "$99/month subscription",
            "key_strengths": ["Established brand", "Feature rich"],
            "market_gaps": ["Complex UI", "Poor support"],
            "differentiation_opportunities": ["Simpler interface", "Better support"]
        },
        {
            "competitor_name": "CompetitorB",
            "value_proposition": "Workflow optimization tool",
            "target_market": "Mid-market",
            "pricing_model": "$199/month",
            "key_strengths": ["Advanced features"],
            "market_gaps": ["Expensive", "Overkill for SMBs"],
            "differentiation_opportunities": ["Lower cost", "SMB focus"]
        }
    ]


@pytest.fixture
def sample_feature_specs():
    """Sample feature specifications for testing."""
    return [
        FeatureSpec(
            name="User Dashboard",
            user_story="As a business owner, I want a dashboard, so that I can see key metrics",
            acceptance_criteria=[
                "WHEN user logs in THEN dashboard SHALL display key metrics",
                "WHEN data updates THEN dashboard SHALL refresh automatically",
                "GIVEN user permissions WHEN accessing dashboard THEN appropriate data SHALL be shown"
            ],
            mvp_priority=MVPPriority.CORE,
            effort_estimate="M",
            business_impact="High",
            validation_level=MarketValidationLevel.ASSUMPTION,
            dependencies=[]
        ),
        FeatureSpec(
            name="Process Automation",
            user_story="As a manager, I want to automate workflows, so that I can save time",
            acceptance_criteria=[
                "WHEN user creates workflow THEN system SHALL save configuration",
                "WHEN trigger occurs THEN workflow SHALL execute automatically",
                "GIVEN workflow error WHEN execution fails THEN user SHALL be notified"
            ],
            mvp_priority=MVPPriority.CORE,
            effort_estimate="L",
            business_impact="Critical",
            validation_level=MarketValidationLevel.ASSUMPTION,
            dependencies=["User Dashboard"]
        )
    ]


@pytest.fixture
def sample_product_state(sample_business_model, sample_competitive_analysis, sample_feature_specs):
    """Sample product state for testing."""
    return ProductState(
        user_query="Build a business process automation platform for SMBs",
        business_model=sample_business_model,
        competitive_analysis=sample_competitive_analysis,
        feature_specifications=sample_feature_specs,
        current_phase="planning"
    )


class TestGTMStrategyAgent:
    """Test cases for GTM Strategy Agent."""
    
    @pytest.fixture
    def gtm_agent(self):
        """GTM Strategy Agent instance for testing."""
        return GTMStrategyAgent(api_key="test-key")
    
    @pytest.mark.asyncio
    async def test_develop_gtm_strategy_success(self, gtm_agent, sample_product_state):
        """Test successful GTM strategy development."""
        # Mock the LLM responses
        mock_responses = [
            # Channel identification response
            MagicMock(choices=[MagicMock(message=MagicMock(content='''```json
            {
                "channels": [
                    {
                        "channel_name": "Content Marketing",
                        "rationale": "Build authority with target SMBs",
                        "target_audience": "Business owners and managers",
                        "cost_estimate": "Medium ongoing investment",
                        "timeline": "3-6 months to see results",
                        "success_metrics": ["Organic traffic", "Lead generation", "Content engagement"]
                    },
                    {
                        "channel_name": "Direct Sales",
                        "rationale": "High-touch approach for enterprise deals",
                        "target_audience": "Decision makers in target companies",
                        "cost_estimate": "High initial investment",
                        "timeline": "2-3 months to establish",
                        "success_metrics": ["Conversion rate", "Average deal size", "Sales cycle"]
                    },
                    {
                        "channel_name": "Partner Network",
                        "rationale": "Leverage existing relationships",
                        "target_audience": "Partner ecosystems",
                        "cost_estimate": "Low initial, revenue share",
                        "timeline": "4-6 months",
                        "success_metrics": ["Partner acquisition", "Joint deals", "Revenue share"]
                    }
                ]
            }
            ```'''))]),
            
            # Pricing strategy response
            MagicMock(choices=[MagicMock(message=MagicMock(content='''```json
            {
                "pricing_model": "Subscription",
                "price_point": "$79/month",
                "competitive_positioning": "Value pricing",
                "value_justification": "Priced below competitors while delivering core value",
                "pricing_tiers": [
                    {
                        "tier_name": "Starter",
                        "price": "$49/month",
                        "features": "Basic automation"
                    },
                    {
                        "tier_name": "Professional",
                        "price": "$79/month",
                        "features": "Full automation + support"
                    }
                ]
            }
            ```'''))]),
            
            # Launch timeline response
            MagicMock(choices=[MagicMock(message=MagicMock(content='''```json
            {
                "milestones": [
                    {
                        "phase": "MVP Launch",
                        "timeline": "8-10 weeks",
                        "key_activities": ["Complete core features", "Beta testing", "Initial marketing"],
                        "success_criteria": ["10 paying customers", "Product-market fit signals", "Core functionality validated"],
                        "deliverables": ["MVP product", "Customer feedback", "Initial revenue"]
                    },
                    {
                        "phase": "Product Growth",
                        "timeline": "3-4 months",
                        "key_activities": ["Scale customer acquisition", "Feature expansion", "Channel optimization"],
                        "success_criteria": ["100 customers", "Positive unit economics", "Channel efficiency"],
                        "deliverables": ["Scaled product", "Optimized channels", "Growth metrics"]
                    },
                    {
                        "phase": "Market Expansion",
                        "timeline": "6-9 months",
                        "key_activities": ["Market expansion", "Partnership development", "Product diversification"],
                        "success_criteria": ["Market leadership", "Sustainable growth", "Competitive advantage"],
                        "deliverables": ["Market presence", "Strategic partnerships", "Product portfolio"]
                    }
                ]
            }
            ```'''))]),
            
            # Success metrics response
            MagicMock(choices=[MagicMock(message=MagicMock(content='''```json
            {
                "success_metrics": [
                    "Monthly Recurring Revenue (MRR) growth of 25%",
                    "Customer Acquisition Cost (CAC) under $150",
                    "Customer Lifetime Value (LTV) > 3x CAC",
                    "Monthly active users growth of 20%",
                    "Net Promoter Score (NPS) > 60",
                    "Market share growth in SMB segment"
                ]
            }
            ```'''))]),
            
            # Competitive positioning response
            MagicMock(choices=[MagicMock(message=MagicMock(content="Unlike complex enterprise solutions, we deliver streamlined business process automation specifically designed for SMBs, providing enterprise-grade functionality at an affordable price point that grows with your business."))])
        ]
        
        with patch.object(gtm_agent.client.chat.completions, 'create', side_effect=mock_responses):
            result_state = await gtm_agent.develop_gtm_strategy(sample_product_state)
        
        # Verify GTM strategy was created
        assert result_state.gtm_strategy is not None
        assert isinstance(result_state.gtm_strategy, GTMStrategy)
        
        # Verify distribution channels
        assert len(result_state.gtm_strategy.distribution_channels) >= 3
        assert len(result_state.gtm_strategy.distribution_channels) <= 5
        assert "Content Marketing" in result_state.gtm_strategy.distribution_channels
        
        # Verify pricing strategy
        assert "Subscription" in result_state.gtm_strategy.pricing_strategy
        assert "$79/month" in result_state.gtm_strategy.pricing_strategy
        
        # Verify launch timeline
        assert len(result_state.gtm_strategy.launch_timeline) >= 3
        assert "mvp_launch" in result_state.gtm_strategy.launch_timeline
        assert "growth" in result_state.gtm_strategy.launch_timeline
        assert "expansion" in result_state.gtm_strategy.launch_timeline
        
        # Verify success metrics
        assert len(result_state.gtm_strategy.success_metrics) >= 5
        assert any("MRR" in metric for metric in result_state.gtm_strategy.success_metrics)
        assert any("CAC" in metric for metric in result_state.gtm_strategy.success_metrics)
        
        # Verify competitive positioning
        assert result_state.gtm_strategy.competitive_positioning is not None
        assert len(result_state.gtm_strategy.competitive_positioning) > 50
        
        # Verify budget requirements
        assert result_state.gtm_strategy.budget_requirements is not None
        
        # Verify state updates
        assert result_state.current_phase == "gtm_planning"
        assert result_state.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_develop_gtm_strategy_no_business_model(self, gtm_agent):
        """Test GTM strategy development fails without business model."""
        state = ProductState(
            user_query="Test query",
            current_phase="planning"
        )
        
        with pytest.raises(ValueError, match="Business model is required"):
            await gtm_agent.develop_gtm_strategy(state)
    
    @pytest.mark.asyncio
    async def test_identify_channels_success(self, gtm_agent, sample_business_model, sample_competitive_analysis):
        """Test successful channel identification."""
        mock_response = MagicMock(choices=[MagicMock(message=MagicMock(content='''```json
        {
            "channels": [
                {
                    "channel_name": "LinkedIn Marketing",
                    "rationale": "Target B2B decision makers",
                    "target_audience": "Business owners and managers",
                    "cost_estimate": "Medium",
                    "timeline": "2-3 months",
                    "success_metrics": ["Lead generation", "Engagement rate", "Conversion rate"]
                },
                {
                    "channel_name": "Industry Events",
                    "rationale": "Network with target customers",
                    "target_audience": "SMB owners at trade shows",
                    "cost_estimate": "High",
                    "timeline": "3-6 months",
                    "success_metrics": ["Leads generated", "Brand awareness", "Partnership opportunities"]
                },
                {
                    "channel_name": "Referral Program",
                    "rationale": "Leverage satisfied customers",
                    "target_audience": "Existing customer network",
                    "cost_estimate": "Low",
                    "timeline": "1-2 months",
                    "success_metrics": ["Referral rate", "Customer acquisition", "Program participation"]
                }
            ]
        }
        ```'''))])
        
        with patch.object(gtm_agent.client.chat.completions, 'create', return_value=mock_response):
            channels = await gtm_agent._identify_channels(sample_business_model, sample_competitive_analysis)
        
        assert len(channels) == 3
        assert all(isinstance(channel, ChannelAnalysis) for channel in channels)
        assert channels[0].channel_name == "LinkedIn Marketing"
        assert len(channels[0].success_metrics) >= 3
    
    @pytest.mark.asyncio
    async def test_develop_pricing_success(self, gtm_agent, sample_business_model, sample_competitive_analysis, sample_feature_specs):
        """Test successful pricing strategy development."""
        mock_response = MagicMock(choices=[MagicMock(message=MagicMock(content='''```json
        {
            "pricing_model": "Tiered Subscription",
            "price_point": "$89/month",
            "competitive_positioning": "Competitive",
            "value_justification": "Balanced pricing for SMB market with strong feature set",
            "pricing_tiers": [
                {
                    "tier_name": "Basic",
                    "price": "$49/month",
                    "features": "Core automation features"
                },
                {
                    "tier_name": "Pro",
                    "price": "$89/month",
                    "features": "Advanced automation + analytics"
                }
            ]
        }
        ```'''))])
        
        with patch.object(gtm_agent.client.chat.completions, 'create', return_value=mock_response):
            pricing = await gtm_agent._develop_pricing(sample_business_model, sample_competitive_analysis, sample_feature_specs)
        
        assert isinstance(pricing, PricingAnalysis)
        assert pricing.pricing_model == "Tiered Subscription"
        assert pricing.price_point == "$89/month"
        assert pricing.competitive_positioning == "Competitive"
        assert len(pricing.pricing_tiers) == 2
    
    @pytest.mark.asyncio
    async def test_create_launch_sequence_success(self, gtm_agent, sample_business_model, sample_feature_specs):
        """Test successful launch timeline creation."""
        channels = [
            ChannelAnalysis(
                channel_name="Content Marketing",
                rationale="Build authority",
                target_audience="SMB owners",
                cost_estimate="Medium",
                timeline="3-6 months",
                success_metrics=["Traffic", "Leads", "Engagement"]
            )
        ]
        
        mock_response = MagicMock(choices=[MagicMock(message=MagicMock(content='''```json
        {
            "milestones": [
                {
                    "phase": "MVP Launch",
                    "timeline": "10 weeks",
                    "key_activities": ["Feature completion", "Testing", "Launch prep"],
                    "success_criteria": ["10 customers", "Validation", "Revenue"],
                    "deliverables": ["Product", "Feedback", "Metrics"]
                },
                {
                    "phase": "Growth Phase",
                    "timeline": "4 months",
                    "key_activities": ["Scale acquisition", "Optimize", "Expand"],
                    "success_criteria": ["100 customers", "Economics", "Efficiency"],
                    "deliverables": ["Scale", "Optimization", "Growth"]
                },
                {
                    "phase": "Expansion",
                    "timeline": "8 months",
                    "key_activities": ["Market expansion", "Partnerships", "Diversification"],
                    "success_criteria": ["Leadership", "Growth", "Advantage"],
                    "deliverables": ["Presence", "Partners", "Portfolio"]
                }
            ]
        }
        ```'''))])
        
        with patch.object(gtm_agent.client.chat.completions, 'create', return_value=mock_response):
            milestones = await gtm_agent._create_launch_sequence(sample_business_model, sample_feature_specs, channels)
        
        assert len(milestones) == 3
        assert all(isinstance(milestone, LaunchMilestone) for milestone in milestones)
        assert milestones[0].phase == "MVP Launch"
        assert len(milestones[0].key_activities) >= 3
        assert len(milestones[0].success_criteria) >= 3
    
    @pytest.mark.asyncio
    async def test_define_success_metrics_success(self, gtm_agent, sample_business_model):
        """Test successful success metrics definition."""
        channels = [
            ChannelAnalysis(
                channel_name="Content Marketing",
                rationale="Build authority",
                target_audience="SMB owners",
                cost_estimate="Medium",
                timeline="3-6 months",
                success_metrics=["Traffic", "Leads", "Engagement"]
            )
        ]
        
        pricing = PricingAnalysis(
            pricing_model="Subscription",
            price_point="$79/month",
            competitive_positioning="Value",
            value_justification="Good value for SMBs"
        )
        
        mock_response = MagicMock(choices=[MagicMock(message=MagicMock(content='''```json
        {
            "success_metrics": [
                "MRR growth of 30% monthly",
                "CAC under $120",
                "LTV/CAC ratio > 3:1",
                "Customer retention > 90%",
                "NPS score > 70",
                "Market share growth in SMB segment"
            ]
        }
        ```'''))])
        
        with patch.object(gtm_agent.client.chat.completions, 'create', return_value=mock_response):
            metrics = await gtm_agent._define_success_metrics(sample_business_model, channels, pricing)
        
        assert len(metrics) == 6
        assert any("MRR" in metric for metric in metrics)
        assert any("CAC" in metric for metric in metrics)
        assert any("LTV" in metric for metric in metrics)
    
    @pytest.mark.asyncio
    async def test_create_competitive_positioning_success(self, gtm_agent, sample_business_model, sample_competitive_analysis):
        """Test successful competitive positioning creation."""
        pricing = PricingAnalysis(
            pricing_model="Subscription",
            price_point="$79/month",
            competitive_positioning="Value",
            value_justification="Good value for SMBs"
        )
        
        mock_response = MagicMock(choices=[MagicMock(message=MagicMock(content="Unlike enterprise-focused competitors, we deliver streamlined automation specifically for SMBs at a price point that makes sense for growing businesses."))])
        
        with patch.object(gtm_agent.client.chat.completions, 'create', return_value=mock_response):
            positioning = await gtm_agent._create_competitive_positioning(sample_business_model, sample_competitive_analysis, pricing)
        
        assert isinstance(positioning, str)
        assert len(positioning) > 50
        assert "SMBs" in positioning or "small" in positioning.lower()
    
    def test_estimate_budget_requirements(self, gtm_agent):
        """Test budget requirements estimation."""
        channels = [
            ChannelAnalysis(
                channel_name="Content Marketing",
                rationale="Build authority",
                target_audience="SMB owners",
                cost_estimate="Medium investment required",
                timeline="3-6 months",
                success_metrics=["Traffic", "Leads"]
            ),
            ChannelAnalysis(
                channel_name="Direct Sales",
                rationale="High-touch approach",
                target_audience="Decision makers",
                cost_estimate="High initial investment",
                timeline="2-3 months",
                success_metrics=["Conversion", "Deal size"]
            )
        ]
        
        pricing = PricingAnalysis(
            pricing_model="Subscription",
            price_point="$79/month",
            competitive_positioning="Value",
            value_justification="Good value for SMBs"
        )
        
        budget = gtm_agent._estimate_budget_requirements(channels, pricing)
        
        assert isinstance(budget, str)
        assert "$" in budget
        assert "investment" in budget.lower()
        assert len(budget) > 50
    
    @pytest.mark.asyncio
    async def test_error_handling_llm_failure(self, gtm_agent, sample_product_state):
        """Test error handling when LLM calls fail."""
        with patch.object(gtm_agent.client.chat.completions, 'create', side_effect=Exception("API Error")):
            result_state = await gtm_agent.develop_gtm_strategy(sample_product_state)
        
        # Should handle error gracefully by using default values
        # Individual methods fail but return defaults, so main method succeeds
        assert result_state.gtm_strategy is not None
        assert isinstance(result_state.gtm_strategy, GTMStrategy)
        
        # Should have default channels when API fails
        assert "Digital Marketing" in result_state.gtm_strategy.distribution_channels
        assert "Partnership Sales" in result_state.gtm_strategy.distribution_channels
        
        # Should have default pricing
        assert "Subscription" in result_state.gtm_strategy.pricing_strategy
        
        # Should have required timeline phases
        assert "mvp_launch" in result_state.gtm_strategy.launch_timeline
        assert "growth" in result_state.gtm_strategy.launch_timeline
        assert "expansion" in result_state.gtm_strategy.launch_timeline
    
    @pytest.mark.asyncio
    async def test_fallback_to_defaults_on_json_parse_error(self, gtm_agent, sample_business_model, sample_competitive_analysis):
        """Test fallback to default values when JSON parsing fails."""
        mock_response = MagicMock(choices=[MagicMock(message=MagicMock(content="Invalid JSON response"))])
        
        with patch.object(gtm_agent.client.chat.completions, 'create', return_value=mock_response):
            channels = await gtm_agent._identify_channels(sample_business_model, sample_competitive_analysis)
        
        # Should return default channels
        assert len(channels) == 3
        assert all(isinstance(channel, ChannelAnalysis) for channel in channels)
        assert channels[0].channel_name == "Digital Marketing"