"""Tests for ProductDevelopmentOrchestrator."""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from orchestrator import ProductDevelopmentOrchestrator
from models.data_models import ProductState, BusinessModel, FeatureSpec, GTMStrategy
from models.enums import MVPPriority, MarketValidationLevel


class TestProductDevelopmentOrchestrator:
    """Test suite for ProductDevelopmentOrchestrator."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance for testing."""
        return ProductDevelopmentOrchestrator(api_key="test-key")
    
    @pytest.fixture
    def sample_state(self):
        """Create sample ProductState for testing."""
        return ProductState(
            user_query="Build a project management tool for small teams",
            session_id="test-session-123",
            current_phase="discovery"
        )
    
    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initializes correctly."""
        assert orchestrator.api_key == "test-key"
        assert orchestrator.model == "openai/gpt-4o-mini"
        assert orchestrator.bpa_agent is not None
        assert orchestrator.gtm_agent is not None
        assert orchestrator.transition_agent is not None
        assert orchestrator.memory is not None
        assert orchestrator.graph is not None
    
    def test_build_product_graph(self, orchestrator):
        """Test workflow graph is built correctly."""
        graph = orchestrator._build_product_graph()
        assert graph is not None
        
        # Check that graph has the expected structure
        # Note: LangGraph internal structure testing is limited
        # We mainly verify it compiles without errors
    
    def test_should_continue_development_pass(self, orchestrator, sample_state):
        """Test validation gate passes with high score."""
        # Set high validation score
        sample_state.market_validation = {
            "overall_score": "8.5",
            "should_continue": "true"
        }
        
        result = orchestrator._should_continue_development(sample_state)
        assert result == "continue"
    
    def test_should_continue_development_fail_low_score(self, orchestrator, sample_state):
        """Test validation gate fails with low score."""
        # Set low validation score
        sample_state.market_validation = {
            "overall_score": "5.0",
            "should_continue": "false"
        }
        
        result = orchestrator._should_continue_development(sample_state)
        assert result == "stop"
    
    def test_should_continue_development_fail_should_continue_false(self, orchestrator, sample_state):
        """Test validation gate fails when should_continue is false."""
        # Set high score but should_continue false
        sample_state.market_validation = {
            "overall_score": "8.0",
            "should_continue": "false"
        }
        
        result = orchestrator._should_continue_development(sample_state)
        assert result == "stop"
    
    def test_should_continue_development_invalid_score(self, orchestrator, sample_state):
        """Test validation gate handles invalid score gracefully."""
        # Set invalid score
        sample_state.market_validation = {
            "overall_score": "invalid",
            "should_continue": "true"
        }
        
        result = orchestrator._should_continue_development(sample_state)
        assert result == "stop"  # Should default to stop on error
    
    def test_generate_research_query_with_business_model(self, orchestrator, sample_state):
        """Test research query generation with business model."""
        sample_state.business_model = BusinessModel(
            value_proposition="Streamline team collaboration",
            target_customer="Small development teams",
            revenue_streams=["Subscription"],
            key_metrics=["MRR"]
        )
        
        query = orchestrator._generate_research_query(sample_state)
        assert "Streamline team collaboration" in query
        assert "Small development teams" in query
        assert "market analysis competitors" in query
    
    def test_generate_research_query_without_business_model(self, orchestrator, sample_state):
        """Test research query generation without business model."""
        query = orchestrator._generate_research_query(sample_state)
        assert sample_state.user_query in query
        assert "market analysis competitors" in query
    
    def test_generate_technical_architecture(self, orchestrator, sample_state):
        """Test technical architecture generation."""
        # Add some features to test architecture complexity
        sample_state.feature_specifications = [
            FeatureSpec(
                name="User Auth",
                user_story="As a user, I want to login",
                acceptance_criteria=[
                    "WHEN user enters credentials THEN system SHALL authenticate",
                    "WHEN authentication fails THEN system SHALL show error message",
                    "WHEN user is authenticated THEN system SHALL redirect to dashboard"
                ],
                mvp_priority=MVPPriority.CORE,
                effort_estimate="S",
                business_impact="High"
            ),
            FeatureSpec(
                name="Task Management",
                user_story="As a user, I want to create tasks",
                acceptance_criteria=[
                    "WHEN user creates task THEN system SHALL save it",
                    "WHEN task is saved THEN system SHALL show confirmation",
                    "WHEN task creation fails THEN system SHALL show error"
                ],
                mvp_priority=MVPPriority.CORE,
                effort_estimate="M",
                business_impact="Critical"
            )
        ]
        
        architecture = orchestrator._generate_technical_architecture(sample_state)
        
        assert "architecture_type" in architecture
        assert "frontend" in architecture
        assert "backend" in architecture
        assert "database" in architecture
        assert architecture["architecture_type"] == "monolithic"  # 2 features = monolithic
    
    def test_generate_rejection_report(self, orchestrator, sample_state):
        """Test rejection report generation."""
        sample_state.market_validation = {
            "overall_score": "4.5",
            "reasoning": "Market is too saturated with existing solutions"
        }
        
        report = orchestrator._generate_rejection_report(sample_state)
        
        assert "BUSINESS VALIDATION REJECTION REPORT" in report
        assert "4.5/10" in report
        assert "Market is too saturated" in report
        assert "RECOMMENDATIONS:" in report
        assert "NEXT STEPS:" in report
    
    @pytest.mark.asyncio
    async def test_problem_validation_node_success(self, orchestrator, sample_state):
        """Test problem validation node with successful validation."""
        # Mock the BPA agent
        mock_result = ProductState(
            user_query=sample_state.user_query,
            session_id=sample_state.session_id,
            current_phase="validation",
            market_validation={
                "overall_score": "8.0",
                "should_continue": "true",
                "reasoning": "Strong market opportunity"
            }
        )
        
        with patch.object(orchestrator.bpa_agent, 'analyze_business_viability', new_callable=AsyncMock) as mock_analyze:
            mock_analyze.return_value = mock_result
            
            result = await orchestrator._problem_validation_node(sample_state)
            
            assert result.market_validation["overall_score"] == "8.0"
            assert result.market_validation["should_continue"] == "true"
            mock_analyze.assert_called_once_with(sample_state)
    
    @pytest.mark.asyncio
    async def test_problem_validation_node_error_handling(self, orchestrator, sample_state):
        """Test problem validation node handles errors gracefully."""
        # Mock the BPA agent to raise an exception
        with patch.object(orchestrator.bpa_agent, 'analyze_business_viability', new_callable=AsyncMock) as mock_analyze:
            mock_analyze.side_effect = Exception("API error")
            
            result = await orchestrator._problem_validation_node(sample_state)
            
            assert "problem_validation_error" in result.market_validation
            assert result.market_validation["problem_validation_error"] == "API error"
    
    @pytest.mark.asyncio
    async def test_market_research_node_success(self, orchestrator, sample_state):
        """Test market research node with successful research."""
        mock_research_results = [
            {
                "url": "https://example.com",
                "title": "Market Analysis",
                "content": "Competitive landscape analysis",
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        # Mock WebResearchAgent
        mock_agent = AsyncMock()
        mock_agent.research_topic.return_value = mock_research_results
        
        with patch('orchestrator.WebResearchAgent') as mock_research_class:
            mock_research_class.return_value.__aenter__.return_value = mock_agent
            
            result = await orchestrator._market_research_node(sample_state)
            
            assert len(result.research_data) == 1
            assert result.research_data[0]["title"] == "Market Analysis"
            assert result.current_phase == "planning"
    
    @pytest.mark.asyncio
    async def test_market_research_node_error_handling(self, orchestrator, sample_state):
        """Test market research node handles errors gracefully."""
        # Mock WebResearchAgent to raise an exception
        with patch('orchestrator.WebResearchAgent') as mock_research_class:
            mock_research_class.return_value.__aenter__.side_effect = Exception("Network error")
            
            result = await orchestrator._market_research_node(sample_state)
            
            assert len(result.research_data) == 1
            assert result.research_data[0]["success"] is False
            assert "Network error" in result.research_data[0]["error_message"]
            assert "market_research_error" in result.market_validation
    
    @pytest.mark.asyncio
    async def test_gtm_strategy_node_success(self, orchestrator, sample_state):
        """Test GTM strategy node with successful strategy development."""
        # Add required business model to state
        sample_state.business_model = BusinessModel(
            value_proposition="Test value prop",
            target_customer="Test customer",
            revenue_streams=["Subscription"],
            key_metrics=["MRR"]
        )
        
        mock_gtm_strategy = GTMStrategy(
            distribution_channels=["Direct sales", "Content marketing", "Partnerships"],
            pricing_strategy="Subscription - $99/month",
            launch_timeline={
                "mvp_launch": "8-12 weeks: Core features",
                "growth": "3-6 months: Scale acquisition",
                "expansion": "6-12 months: Market expansion"
            },
            success_metrics=["MRR growth", "CAC", "LTV"],
            competitive_positioning="Premium solution"
        )
        
        mock_result = ProductState(
            user_query=sample_state.user_query,
            session_id=sample_state.session_id,
            business_model=sample_state.business_model,
            gtm_strategy=mock_gtm_strategy,
            current_phase="gtm_planning"
        )
        
        with patch.object(orchestrator.gtm_agent, 'develop_gtm_strategy', new_callable=AsyncMock) as mock_develop:
            mock_develop.return_value = mock_result
            
            result = await orchestrator._gtm_strategy_node(sample_state)
            
            assert result.gtm_strategy is not None
            assert len(result.gtm_strategy.distribution_channels) == 3
            assert result.gtm_strategy.pricing_strategy == "Subscription - $99/month"
            mock_develop.assert_called_once_with(sample_state)
    
    @pytest.mark.asyncio
    async def test_execution_roadmap_node_success(self, orchestrator, sample_state):
        """Test execution roadmap node with successful roadmap generation."""
        # Add required business model to state
        sample_state.business_model = BusinessModel(
            value_proposition="Test value prop",
            target_customer="Test customer",
            revenue_streams=["Subscription"],
            key_metrics=["MRR"]
        )
        
        mock_roadmap = [
            {
                "phase_name": "MVP Launch",
                "timeline": "8-12 weeks",
                "success_criteria": ["10 paying customers", "Product-market fit signals"]
            }
        ]
        
        mock_result = ProductState(
            user_query=sample_state.user_query,
            session_id=sample_state.session_id,
            business_model=sample_state.business_model,
            mvp_roadmap=mock_roadmap,
            current_phase="gtm_planning"
        )
        
        with patch.object(orchestrator.transition_agent, 'generate_product_roadmap', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = mock_result
            
            result = await orchestrator._execution_roadmap_node(sample_state)
            
            assert len(result.mvp_roadmap) == 1
            assert result.mvp_roadmap[0]["phase_name"] == "MVP Launch"
            assert result.current_phase == "gtm_planning"
            mock_generate.assert_called_once_with(sample_state)
    
    @pytest.mark.asyncio
    async def test_rejection_report_node(self, orchestrator, sample_state):
        """Test rejection report node creates proper report."""
        sample_state.market_validation = {
            "overall_score": "3.5",
            "reasoning": "Insufficient market demand"
        }
        
        result = await orchestrator._rejection_report_node(sample_state)
        
        assert "rejection_report" in result.market_validation
        assert "rejection_timestamp" in result.market_validation
        assert result.market_validation["workflow_status"] == "rejected"
        assert "BUSINESS VALIDATION REJECTION REPORT" in result.market_validation["rejection_report"]
    
    def test_get_workflow_status_success(self, orchestrator, sample_state):
        """Test workflow status retrieval."""
        # Mock memory load
        with patch.object(orchestrator.memory, 'load_session') as mock_load:
            mock_load.return_value = sample_state
            
            status = orchestrator.get_workflow_status("test-session")
            
            assert status["session_id"] == "test-session"
            assert status["current_phase"] == sample_state.current_phase
            assert status["user_query"] == sample_state.user_query
            assert status["has_business_model"] is False  # No business model in sample
            assert status["feature_count"] == 0
    
    def test_get_workflow_status_not_found(self, orchestrator):
        """Test workflow status when session not found."""
        # Mock memory load to return None
        with patch.object(orchestrator.memory, 'load_session') as mock_load:
            mock_load.return_value = None
            
            status = orchestrator.get_workflow_status("nonexistent-session")
            
            assert "error" in status
            assert status["error"] == "Session not found"
    
    @pytest.mark.asyncio
    async def test_execute_workflow_error_recovery(self, orchestrator):
        """Test workflow execution with error recovery."""
        test_query = "Test project"
        
        # Mock the graph to raise an exception
        with patch.object(orchestrator.graph, 'ainvoke', new_callable=AsyncMock) as mock_invoke:
            mock_invoke.side_effect = Exception("Workflow error")
            
            # Mock memory operations
            with patch.object(orchestrator.memory, 'generate_session_id') as mock_gen_id:
                mock_gen_id.return_value = "test-session"
                
                with patch.object(orchestrator.memory, 'save_session') as mock_save:
                    with patch.object(orchestrator.memory, 'load_session') as mock_load:
                        # Return None for recovery attempt
                        mock_load.return_value = None
                        
                        result = await orchestrator.execute_workflow(test_query)
                        
                        assert result.user_query == test_query
                        assert "workflow_error" in result.market_validation
                        assert result.market_validation["workflow_error"] == "Workflow error"
    
    def test_list_sessions(self, orchestrator):
        """Test session listing."""
        mock_sessions = {
            "session1": {"current_phase": "discovery", "user_query": "Test 1"},
            "session2": {"current_phase": "validation", "user_query": "Test 2"}
        }
        
        with patch.object(orchestrator.memory, 'list_sessions') as mock_list:
            mock_list.return_value = mock_sessions
            
            sessions = orchestrator.list_sessions()
            
            assert len(sessions) == 2
            assert "session1" in sessions
            assert "session2" in sessions
    
    def test_cleanup_old_sessions(self, orchestrator):
        """Test old session cleanup."""
        with patch.object(orchestrator.memory, 'cleanup_old_sessions') as mock_cleanup:
            mock_cleanup.return_value = 5
            
            result = orchestrator.cleanup_old_sessions(30)
            
            assert result == 5
            mock_cleanup.assert_called_once_with(30)