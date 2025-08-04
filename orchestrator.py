"""Product Development Orchestrator using LangGraph for workflow management."""

import asyncio
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from models.data_models import ProductState
from agents.bpa_agent import BPAAgent
from agents.gtm_strategy_agent import GTMStrategyAgent
from agents.web_research_agent import WebResearchAgent
from agents.product_transition_agent import ProductTransitionAgent
from memory.graph_memory import GraphMemory

# Configure logging
logger = logging.getLogger(__name__)


class ProductDevelopmentOrchestrator:
    """
    Main orchestrator for the product development workflow using LangGraph.
    
    Manages the sequential workflow with validation gates and conditional routing
    to ensure business-first development approach.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "openai/gpt-4o-mini"):
        """
        Initialize the orchestrator with agents and workflow.
        
        Args:
            api_key: OpenAI API key (if None, will use environment variable)
            model: LLM model to use for all agents
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        
        # Initialize agents
        self.bpa_agent = BPAAgent(api_key=self.api_key, model=self.model)
        self.gtm_agent = GTMStrategyAgent(api_key=self.api_key, model=self.model)
        self.transition_agent = ProductTransitionAgent(api_key=self.api_key, model=self.model)
        
        # Initialize memory system
        self.memory = GraphMemory()
        
        # Build the workflow graph
        self.graph = self._build_product_graph()
        
        logger.info("ProductDevelopmentOrchestrator initialized")
    
    def _build_product_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow with sequential nodes and conditional routing.
        
        Returns:
            Compiled StateGraph for the product development workflow
            
        Requirements: 10.1, 10.2
        """
        logger.debug("Building product development workflow graph")
        
        # Create workflow with ProductState
        workflow = StateGraph(ProductState)
        
        # Add workflow nodes
        workflow.add_node("problem_validation", self._problem_validation_node)
        workflow.add_node("business_analysis", self._business_analysis_node)
        workflow.add_node("market_research", self._market_research_node)
        workflow.add_node("mvp_planning", self._mvp_planning_node)
        workflow.add_node("technical_architecture", self._technical_architecture_node)
        workflow.add_node("gtm_strategy", self._gtm_strategy_node)
        workflow.add_node("execution_roadmap", self._execution_roadmap_node)
        workflow.add_node("rejection_report", self._rejection_report_node)
        
        # Set entry point
        workflow.set_entry_point("problem_validation")
        
        # Add conditional routing with validation gates
        workflow.add_conditional_edges(
            "problem_validation",
            self._should_continue_development,
            {
                "continue": "business_analysis",
                "stop": "rejection_report"
            }
        )
        
        # Sequential flow for successful validation
        workflow.add_edge("business_analysis", "market_research")
        workflow.add_edge("market_research", "mvp_planning")
        workflow.add_edge("mvp_planning", "technical_architecture")
        workflow.add_edge("technical_architecture", "gtm_strategy")
        workflow.add_edge("gtm_strategy", "execution_roadmap")
        
        # Terminal nodes
        workflow.add_edge("execution_roadmap", END)
        workflow.add_edge("rejection_report", END)
        
        # Compile with memory checkpointer
        checkpointer = MemorySaver()
        compiled_graph = workflow.compile(checkpointer=checkpointer)
        
        logger.info("Product development workflow graph compiled successfully")
        return compiled_graph
    
    async def execute_workflow(self, user_query: str, session_id: Optional[str] = None) -> ProductState:
        """
        Execute the complete product development workflow.
        
        Args:
            user_query: User's project description/query
            session_id: Optional session ID for state persistence
            
        Returns:
            Final ProductState after workflow execution
            
        Requirements: 10.1, 10.4 (error handling and workflow recovery)
        """
        logger.info(f"Starting workflow execution for query: {user_query[:100]}...")
        
        try:
            # Generate session ID if not provided
            if not session_id:
                session_id = self.memory.generate_session_id()
            
            # Create initial state
            initial_state = ProductState(
                user_query=user_query,
                session_id=session_id,
                current_phase="discovery"
            )
            
            # Save initial state
            self.memory.save_session(session_id, initial_state)
            
            # Execute workflow with error recovery
            config = {"configurable": {"thread_id": session_id}}
            
            try:
                # Run the workflow
                final_state = await self.graph.ainvoke(initial_state, config=config)
                
                # Save final state
                self.memory.save_session(session_id, final_state)
                
                logger.info(f"Workflow completed successfully for session {session_id}")
                return final_state
                
            except Exception as workflow_error:
                logger.error(f"Workflow execution failed: {workflow_error}")
                
                # Attempt recovery by loading last known good state
                recovered_state = self.memory.load_session(session_id)
                if recovered_state:
                    # Add error information to state
                    recovered_state.market_validation["workflow_error"] = str(workflow_error)
                    recovered_state.market_validation["workflow_error_timestamp"] = datetime.now().isoformat()
                    recovered_state.update_timestamp()
                    
                    # Save recovered state
                    self.memory.save_session(session_id, recovered_state)
                    
                    logger.info(f"Workflow recovered to last known state for session {session_id}")
                    return recovered_state
                else:
                    # Return initial state with error information
                    initial_state.market_validation["workflow_error"] = str(workflow_error)
                    initial_state.market_validation["workflow_error_timestamp"] = datetime.now().isoformat()
                    return initial_state
                    
        except Exception as e:
            logger.error(f"Critical workflow failure: {e}")
            # Return minimal error state
            error_state = ProductState(
                user_query=user_query,
                session_id=session_id or "error",
                current_phase="discovery"
            )
            error_state.market_validation["critical_error"] = str(e)
            error_state.market_validation["critical_error_timestamp"] = datetime.now().isoformat()
            return error_state
    
    async def _problem_validation_node(self, state: ProductState) -> ProductState:
        """
        Problem validation node - validates business viability.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with validation results
            
        Requirements: 1.1, 1.3 (validation gates)
        """
        logger.info("Executing problem validation node")
        
        try:
            # Use BPA agent for problem validation
            updated_state = await self.bpa_agent.analyze_business_viability(state)
            
            # Save intermediate state
            if updated_state.session_id:
                self.memory.save_session(updated_state.session_id, updated_state)
            
            logger.info("Problem validation completed")
            return updated_state
            
        except Exception as e:
            logger.error(f"Problem validation node failed: {e}")
            # Add error to state but continue workflow
            state.market_validation["problem_validation_error"] = str(e)
            state.market_validation["problem_validation_error_timestamp"] = datetime.now().isoformat()
            state.update_timestamp()
            return state
    
    async def _business_analysis_node(self, state: ProductState) -> ProductState:
        """
        Business analysis node - already handled by BPA agent in problem validation.
        
        Args:
            state: Current workflow state
            
        Returns:
            State with business analysis completed
        """
        logger.info("Executing business analysis node")
        
        try:
            # Business analysis is already done in problem validation
            # This node serves as a checkpoint and can add additional analysis if needed
            
            if not state.business_model:
                logger.warning("Business model not found, re-running BPA agent")
                state = await self.bpa_agent.analyze_business_viability(state)
            
            # Update phase
            state.current_phase = "validation"
            state.update_timestamp()
            
            # Save state
            if state.session_id:
                self.memory.save_session(state.session_id, state)
            
            logger.info("Business analysis completed")
            return state
            
        except Exception as e:
            logger.error(f"Business analysis node failed: {e}")
            state.market_validation["business_analysis_error"] = str(e)
            state.market_validation["business_analysis_error_timestamp"] = datetime.now().isoformat()
            state.update_timestamp()
            return state
    
    async def _market_research_node(self, state: ProductState) -> ProductState:
        """
        Market research node - conducts web research for competitive analysis.
        
        Args:
            state: Current workflow state
            
        Returns:
            State with market research data
            
        Requirements: 3.1, 3.2, 3.3, 3.4 (error handling)
        """
        logger.info("Executing market research node")
        
        try:
            # Conduct web research using WebResearchAgent
            async with WebResearchAgent() as research_agent:
                # Generate research query based on business model
                research_query = self._generate_research_query(state)
                
                # Conduct research
                research_results = await research_agent.research_topic(research_query)
                
                # Update state with research data
                state.research_data = research_results
                state.current_phase = "planning"
                state.update_timestamp()
                
                # Save state
                if state.session_id:
                    self.memory.save_session(state.session_id, state)
                
                logger.info(f"Market research completed with {len(research_results)} results")
                return state
                
        except Exception as e:
            logger.error(f"Market research node failed: {e}")
            # Continue with limited research data
            state.research_data = [{
                "url": "error",
                "title": "Research Failed",
                "content": f"Market research failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error_message": str(e),
                "metadata": {"fallback": True}
            }]
            state.market_validation["market_research_error"] = str(e)
            state.market_validation["market_research_error_timestamp"] = datetime.now().isoformat()
            state.update_timestamp()
            return state
    
    async def _mvp_planning_node(self, state: ProductState) -> ProductState:
        """
        MVP planning node - feature specifications are already handled by BPA agent.
        
        Args:
            state: Current workflow state
            
        Returns:
            State with MVP planning completed
        """
        logger.info("Executing MVP planning node")
        
        try:
            # MVP features are already generated by BPA agent
            # This node can refine or validate the feature specifications
            
            if not state.feature_specifications:
                logger.warning("Feature specifications not found, re-running BPA agent")
                state = await self.bpa_agent.analyze_business_viability(state)
            
            # Update phase
            state.current_phase = "mvp_design"
            state.update_timestamp()
            
            # Save state
            if state.session_id:
                self.memory.save_session(state.session_id, state)
            
            logger.info(f"MVP planning completed with {len(state.feature_specifications)} features")
            return state
            
        except Exception as e:
            logger.error(f"MVP planning node failed: {e}")
            state.market_validation["mvp_planning_error"] = str(e)
            state.market_validation["mvp_planning_error_timestamp"] = datetime.now().isoformat()
            state.update_timestamp()
            return state
    
    async def _technical_architecture_node(self, state: ProductState) -> ProductState:
        """
        Technical architecture node - placeholder for technical architecture planning.
        
        Args:
            state: Current workflow state
            
        Returns:
            State with technical architecture
        """
        logger.info("Executing technical architecture node")
        
        try:
            # Generate basic technical architecture based on features
            tech_architecture = self._generate_technical_architecture(state)
            
            state.technical_architecture = tech_architecture
            state.update_timestamp()
            
            # Save state
            if state.session_id:
                self.memory.save_session(state.session_id, state)
            
            logger.info("Technical architecture completed")
            return state
            
        except Exception as e:
            logger.error(f"Technical architecture node failed: {e}")
            state.market_validation["tech_architecture_error"] = str(e)
            state.market_validation["tech_architecture_error_timestamp"] = datetime.now().isoformat()
            state.update_timestamp()
            return state
    
    async def _gtm_strategy_node(self, state: ProductState) -> ProductState:
        """
        GTM strategy node - develops go-to-market strategy.
        
        Args:
            state: Current workflow state
            
        Returns:
            State with GTM strategy
            
        Requirements: 5.1, 5.2, 5.3, 5.4
        """
        logger.info("Executing GTM strategy node")
        
        try:
            # Use GTM agent to develop strategy
            updated_state = await self.gtm_agent.develop_gtm_strategy(state)
            
            # Save state
            if updated_state.session_id:
                self.memory.save_session(updated_state.session_id, updated_state)
            
            logger.info("GTM strategy completed")
            return updated_state
            
        except Exception as e:
            logger.error(f"GTM strategy node failed: {e}")
            state.market_validation["gtm_strategy_error"] = str(e)
            state.market_validation["gtm_strategy_error_timestamp"] = datetime.now().isoformat()
            state.update_timestamp()
            return state
    
    async def _execution_roadmap_node(self, state: ProductState) -> ProductState:
        """
        Execution roadmap node - creates 3-phase roadmap.
        
        Args:
            state: Current workflow state
            
        Returns:
            State with execution roadmap
            
        Requirements: 7.1, 7.2, 7.3, 7.4
        """
        logger.info("Executing execution roadmap node")
        
        try:
            # Use transition agent to generate roadmap
            updated_state = await self.transition_agent.generate_product_roadmap(state)
            
            # Final phase update
            updated_state.current_phase = "gtm_planning"
            updated_state.update_timestamp()
            
            # Save final state
            if updated_state.session_id:
                self.memory.save_session(updated_state.session_id, updated_state)
            
            logger.info("Execution roadmap completed - workflow finished successfully")
            return updated_state
            
        except Exception as e:
            logger.error(f"Execution roadmap node failed: {e}")
            state.market_validation["execution_roadmap_error"] = str(e)
            state.market_validation["execution_roadmap_error_timestamp"] = datetime.now().isoformat()
            state.update_timestamp()
            return state
    
    async def _rejection_report_node(self, state: ProductState) -> ProductState:
        """
        Rejection report node - creates report for failed validations.
        
        Args:
            state: Current workflow state
            
        Returns:
            State with rejection report
            
        Requirements: 10.2 (conditional routing), 1.3 (validation gates)
        """
        logger.info("Executing rejection report node")
        
        try:
            # Generate rejection report based on validation results
            rejection_report = self._generate_rejection_report(state)
            
            # Store rejection report in market_validation
            state.market_validation["rejection_report"] = rejection_report
            state.market_validation["rejection_timestamp"] = datetime.now().isoformat()
            state.market_validation["workflow_status"] = "rejected"
            
            # Update phase to indicate rejection
            state.current_phase = "validation"
            state.update_timestamp()
            
            # Save state
            if state.session_id:
                self.memory.save_session(state.session_id, state)
            
            logger.info("Rejection report completed")
            return state
            
        except Exception as e:
            logger.error(f"Rejection report node failed: {e}")
            state.market_validation["rejection_report_error"] = str(e)
            state.market_validation["rejection_report_error_timestamp"] = datetime.now().isoformat()
            state.update_timestamp()
            return state
    
    def _should_continue_development(self, state: ProductState) -> str:
        """
        Validation gate - determines if development should continue based on business score.
        
        Args:
            state: Current workflow state
            
        Returns:
            "continue" if validation passes, "stop" if it fails
            
        Requirements: 10.2 (conditional routing), 1.3 (validation gates with score < 7)
        """
        try:
            # Extract overall score from market validation
            overall_score_str = state.market_validation.get("overall_score", "0")
            
            try:
                overall_score = float(overall_score_str)
            except (ValueError, TypeError):
                logger.warning(f"Invalid overall score: {overall_score_str}, defaulting to 0")
                overall_score = 0.0
            
            # Check should_continue flag as well
            should_continue_str = state.market_validation.get("should_continue", "false")
            should_continue = should_continue_str.lower() == "true"
            
            # Business validation gate: score must be >= 7 AND should_continue must be True
            if overall_score >= 7.0 and should_continue:
                logger.info(f"Validation passed with score {overall_score} - continuing development")
                return "continue"
            else:
                logger.warning(f"Validation failed with score {overall_score}, should_continue: {should_continue} - stopping development")
                return "stop"
                
        except Exception as e:
            logger.error(f"Error in validation gate: {e}")
            # Default to stop on error for safety
            return "stop"
    
    def _generate_research_query(self, state: ProductState) -> str:
        """
        Generate research query based on business model.
        
        Args:
            state: Current workflow state
            
        Returns:
            Research query string
        """
        if state.business_model:
            return f"{state.business_model.value_proposition} {state.business_model.target_customer} market analysis competitors"
        else:
            return f"{state.user_query} market analysis competitors"
    
    def _generate_technical_architecture(self, state: ProductState) -> Dict[str, Any]:
        """
        Generate basic technical architecture based on features.
        
        Args:
            state: Current workflow state
            
        Returns:
            Technical architecture dictionary
        """
        try:
            # Basic architecture based on feature count and complexity
            feature_count = len(state.feature_specifications)
            
            # Determine architecture complexity
            if feature_count <= 3:
                architecture_type = "monolithic"
            elif feature_count <= 8:
                architecture_type = "modular_monolith"
            else:
                architecture_type = "microservices"
            
            # Generate basic architecture
            architecture = {
                "architecture_type": architecture_type,
                "frontend": "React/Vue.js SPA",
                "backend": "REST API (Node.js/Python)",
                "database": "PostgreSQL/MongoDB",
                "hosting": "Cloud (AWS/GCP/Azure)",
                "authentication": "JWT/OAuth2",
                "monitoring": "Application monitoring and logging",
                "deployment": "CI/CD pipeline",
                "estimated_complexity": "medium" if feature_count <= 5 else "high",
                "development_timeline": f"{max(8, feature_count * 2)} weeks",
                "team_size": f"{max(2, feature_count // 3)} developers"
            }
            
            return architecture
            
        except Exception as e:
            logger.error(f"Technical architecture generation failed: {e}")
            return {
                "architecture_type": "monolithic",
                "frontend": "Web application",
                "backend": "API server",
                "database": "Database",
                "error": str(e)
            }
    
    def _generate_rejection_report(self, state: ProductState) -> str:
        """
        Generate rejection report for failed validations.
        
        Args:
            state: Current workflow state
            
        Returns:
            Rejection report string
        """
        try:
            overall_score = state.market_validation.get("overall_score", "0")
            reasoning = state.market_validation.get("reasoning", "No reasoning provided")
            
            report = f"""
BUSINESS VALIDATION REJECTION REPORT

Project: {state.user_query}
Overall Score: {overall_score}/10
Validation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

REJECTION REASON:
The project scored {overall_score}/10 in business validation, which is below the required threshold of 7.0.

DETAILED ANALYSIS:
{reasoning}

RECOMMENDATIONS:
1. Revisit the problem statement and ensure it addresses a significant pain point
2. Conduct more thorough market research to validate demand
3. Consider pivoting to a more viable market opportunity
4. Gather more customer feedback before proceeding with development
5. Refine the value proposition to better address customer needs

NEXT STEPS:
- Do not proceed with development until these issues are addressed
- Consider conducting customer interviews to validate assumptions
- Research successful competitors and identify differentiation opportunities
- Reassess the market size and opportunity

This rejection is designed to prevent wasted development effort on unviable projects.
            """.strip()
            
            return report
            
        except Exception as e:
            logger.error(f"Rejection report generation failed: {e}")
            return f"Rejection report generation failed: {str(e)}"
    
    def get_workflow_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get current workflow status for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with workflow status information
        """
        try:
            state = self.memory.load_session(session_id)
            if not state:
                return {"error": "Session not found"}
            
            status = {
                "session_id": session_id,
                "current_phase": state.current_phase,
                "user_query": state.user_query,
                "created_at": state.created_at.isoformat() if state.created_at else None,
                "updated_at": state.updated_at.isoformat() if state.updated_at else None,
                "has_business_model": state.business_model is not None,
                "feature_count": len(state.feature_specifications),
                "has_gtm_strategy": state.gtm_strategy is not None,
                "roadmap_phases": len(state.mvp_roadmap),
                "research_results": len(state.research_data),
                "validation_score": state.market_validation.get("overall_score", "N/A"),
                "workflow_status": state.market_validation.get("workflow_status", "in_progress")
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get workflow status for {session_id}: {e}")
            return {"error": str(e)}
    
    def list_sessions(self) -> Dict[str, Any]:
        """
        List all workflow sessions.
        
        Returns:
            Dictionary with session information
        """
        return self.memory.list_sessions()
    
    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """
        Clean up old workflow sessions.
        
        Args:
            days_old: Number of days after which sessions are considered old
            
        Returns:
            Number of sessions cleaned up
        """
        return self.memory.cleanup_old_sessions(days_old)