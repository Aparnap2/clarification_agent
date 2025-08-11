"""Product Development Orchestrator using LangGraph for workflow management."""

import asyncio
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from models.data_models import ProductState
from agents.bpa_agent import BPAAgent
from agents.gtm_strategy_agent import GTMStrategyAgent
from agents.web_research_agent import WebResearchAgent
from agents.product_transition_agent import ProductTransitionAgent
from memory.graph_memory import GraphMemory
from utils.error_handler import ErrorHandler, ErrorType

# Configure structured logging with enhanced format and error tracking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('orchestrator.log', mode='a')
    ]
)

# Add separate error handler
error_handler = logging.FileHandler('orchestrator_errors.log', mode='a')
error_handler.setLevel(logging.ERROR)
logging.getLogger().addHandler(error_handler)

# Create logger with structured context
logger = logging.getLogger(__name__)

# Add custom formatter for structured logging
class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging with workflow context."""
    
    def format(self, record):
        # Add workflow context if available
        if hasattr(record, 'session_id'):
            record.msg = f"[session:{record.session_id}] {record.msg}"
        if hasattr(record, 'node_name'):
            record.msg = f"[node:{record.node_name}] {record.msg}"
        if hasattr(record, 'request_id'):
            record.msg = f"[req:{record.request_id}] {record.msg}"
        
        return super().format(record)

# Apply structured formatter to handlers
structured_formatter = StructuredFormatter(
    '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
)
for handler in logger.handlers:
    handler.setFormatter(structured_formatter)


class ProductDevelopmentOrchestrator:
    """
    Main orchestrator for the product development workflow using LangGraph.
    
    Manages the sequential workflow with validation gates and conditional routing
    to ensure business-first development approach.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "moonshotai/kimi-k2:free", enable_debug: bool = False):
        """
        Initialize the orchestrator with agents and workflow.
        
        Args:
            api_key: OpenAI API key (if None, will use environment variable)
            model: LLM model to use for all agents
            enable_debug: Whether to enable debug mode for error handling
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        
        # Initialize error handler
        self.error_handler = ErrorHandler(enable_debug=enable_debug)
        
        # Initialize agents
        self.bpa_agent = BPAAgent(api_key=self.api_key, model=self.model)
        self.gtm_agent = GTMStrategyAgent(api_key=self.api_key, model=self.model)
        self.transition_agent = ProductTransitionAgent(api_key=self.api_key, model=self.model)
        
        # Initialize memory system
        self.memory = GraphMemory()
        
        # Build the workflow graph
        self.graph = self._build_product_graph()
        
        logger.info(f"ProductDevelopmentOrchestrator initialized with model: {model}, debug: {enable_debug}")
    
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
        
        # Compile without checkpointer for now to avoid compatibility issues
        compiled_graph = workflow.compile()
        
        logger.info("Product development workflow graph compiled successfully")
        return compiled_graph
    
    async def execute_workflow(self, user_query: str, session_id: Optional[str] = None) -> ProductState:
        """
        Execute the complete product development workflow with enhanced error handling.
        
        Args:
            user_query: User's project description/query
            session_id: Optional session ID for state persistence
            
        Returns:
            Final ProductState after workflow execution
            
        Requirements: 10.1, 10.4 (error handling and workflow recovery)
        """
        # Create structured logging context
        workflow_start_time = datetime.now()
        logger.info(f"Starting workflow execution for query: {user_query[:100]}...", 
                   extra={'session_id': session_id, 'workflow_start': workflow_start_time.isoformat()})
        
        try:
            # Generate session ID if not provided
            if not session_id:
                session_id = self.memory.generate_session_id()
                logger.info(f"Generated new session ID: {session_id}", extra={'session_id': session_id})
            
            # Create initial state
            initial_state = ProductState(
                user_query=user_query,
                session_id=session_id,
                current_phase="discovery"
            )
            
            logger.info("Initial state created", extra={'session_id': session_id, 'phase': 'discovery'})
            
            # Save initial state with error handling
            try:
                self.memory.save_session(session_id, initial_state)
            except Exception as save_error:
                error_response = await self.error_handler.handle_persistence_error(
                    save_error, "save", session_id
                )
                logger.warning(f"Initial state save failed [{error_response.request_id}]: {error_response.message}")
                # Continue with in-memory state
            
            # Execute workflow with enhanced error recovery
            config = {"configurable": {"thread_id": session_id}}
            
            try:
                # Run the workflow with thread_id for SQLite checkpointer
                result = await self.graph.ainvoke(initial_state, config=config)
                
                # Ensure result is a ProductState object
                if isinstance(result, dict):
                    logger.warning("Workflow returned dict instead of ProductState, converting...")
                    try:
                        final_state = ProductState(**result)
                    except Exception as conversion_error:
                        logger.error(f"Failed to convert workflow result to ProductState: {conversion_error}")
                        # Use initial state with error information
                        final_state = initial_state
                        final_state.market_validation["workflow_conversion_error"] = str(conversion_error)
                        final_state.market_validation["workflow_conversion_timestamp"] = datetime.now().isoformat()
                elif isinstance(result, ProductState):
                    final_state = result
                else:
                    logger.error(f"Workflow returned unexpected type: {type(result)}")
                    final_state = initial_state
                    final_state.market_validation["workflow_type_error"] = f"Unexpected result type: {type(result)}"
                    final_state.market_validation["workflow_type_timestamp"] = datetime.now().isoformat()
                
                # Save final state with error handling
                try:
                    self.memory.save_session(session_id, final_state)
                    logger.info("Final state saved successfully", 
                               extra={'session_id': session_id, 'phase': final_state.current_phase})
                except Exception as save_error:
                    error_response = await self.error_handler.handle_persistence_error(
                        save_error, "save", session_id
                    )
                    logger.warning(f"Final state save failed [{error_response.request_id}]: {error_response.message}",
                                 extra={'session_id': session_id, 'request_id': error_response.request_id})
                    # Add error info to state but continue
                    final_state.market_validation["save_error"] = error_response.message
                    final_state.market_validation["save_error_timestamp"] = datetime.now().isoformat()
                
                # Log workflow completion metrics
                workflow_duration = (datetime.now() - workflow_start_time).total_seconds()
                logger.info(f"Workflow completed successfully for session {session_id}",
                           extra={
                               'session_id': session_id, 
                               'workflow_duration_seconds': workflow_duration,
                               'final_phase': final_state.current_phase,
                               'feature_count': len(final_state.feature_specifications),
                               'validation_score': final_state.market_validation.get("overall_score", "N/A")
                           })
                return final_state
                
            except Exception as workflow_error:
                # Handle workflow error with structured error handling
                error_response = await self.error_handler.handle_workflow_error(
                    workflow_error, session_id, state=initial_state
                )
                
                logger.error(f"Workflow execution failed [{error_response.request_id}]: {error_response.message}")
                self.error_handler.log_error_metrics(error_response)
                
                # Attempt recovery by loading last known good state
                try:
                    recovered_state = self.memory.load_session(session_id)
                    if recovered_state:
                        # Add structured error information to state
                        recovered_state.market_validation.update({
                            "workflow_error": error_response.message,
                            "workflow_error_timestamp": error_response.timestamp.isoformat(),
                            "workflow_error_id": error_response.request_id,
                            "recovery_suggestions": error_response.recovery_suggestions
                        })
                        recovered_state.update_timestamp()
                        
                        # Save recovered state
                        try:
                            self.memory.save_session(session_id, recovered_state)
                        except Exception as save_error:
                            logger.warning(f"Failed to save recovered state: {save_error}")
                        
                        logger.info(f"Workflow recovered to last known state for session {session_id}")
                        return recovered_state
                    else:
                        # Return initial state with error information
                        initial_state.market_validation.update({
                            "workflow_error": error_response.message,
                            "workflow_error_timestamp": error_response.timestamp.isoformat(),
                            "workflow_error_id": error_response.request_id,
                            "recovery_suggestions": error_response.recovery_suggestions
                        })
                        return initial_state
                        
                except Exception as recovery_error:
                    logger.error(f"State recovery failed: {recovery_error}")
                    # Return initial state with both errors
                    initial_state.market_validation.update({
                        "workflow_error": error_response.message,
                        "recovery_error": str(recovery_error),
                        "workflow_error_timestamp": error_response.timestamp.isoformat(),
                        "workflow_error_id": error_response.request_id
                    })
                    return initial_state
                    
        except Exception as e:
            logger.error(f"Critical workflow failure: {e}")
            # Create structured error response for critical failures
            try:
                error_response = await self.error_handler.handle_workflow_error(
                    e, session_id or "unknown", state=None
                )
                self.error_handler.log_error_metrics(error_response)
                
                # Return minimal error state with structured error info
                error_state = ProductState(
                    user_query=user_query,
                    session_id=session_id or "error",
                    current_phase="discovery"
                )
                error_state.market_validation.update({
                    "critical_error": error_response.message,
                    "critical_error_timestamp": error_response.timestamp.isoformat(),
                    "critical_error_id": error_response.request_id,
                    "recovery_suggestions": error_response.recovery_suggestions
                })
                return error_state
                
            except Exception as handler_error:
                logger.error(f"Error handler failed: {handler_error}")
                # Fallback to basic error state
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
        Problem validation node - validates business viability with enhanced error handling.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with validation results
            
        Requirements: 1.1, 1.3 (validation gates)
        """
        logger.info("Executing problem validation node", 
                   extra={'session_id': state.session_id, 'node_name': 'problem_validation'})
        
        try:
            # Use BPA agent for problem validation
            logger.debug("Starting BPA agent analysis", 
                        extra={'session_id': state.session_id, 'node_name': 'problem_validation'})
            updated_state = await self.bpa_agent.analyze_business_viability(state)
            
            # Save intermediate state with error handling
            if updated_state.session_id:
                try:
                    self.memory.save_session(updated_state.session_id, updated_state)
                except Exception as save_error:
                    error_response = await self.error_handler.handle_persistence_error(
                        save_error, "save", updated_state.session_id
                    )
                    logger.warning(f"State save failed in problem validation [{error_response.request_id}]: {error_response.message}")
                    # Continue without failing the node
            
            logger.info("Problem validation completed", 
                       extra={
                           'session_id': updated_state.session_id, 
                           'node_name': 'problem_validation',
                           'validation_score': updated_state.market_validation.get("overall_score", "N/A"),
                           'should_continue': updated_state.market_validation.get("should_continue", False)
                       })
            return updated_state
            
        except Exception as e:
            # Handle error with structured error handling
            error_response = await self.error_handler.handle_workflow_error(
                e, state.session_id or "unknown", "problem_validation", state
            )
            
            logger.error(f"Problem validation node failed [{error_response.request_id}]: {error_response.message}")
            self.error_handler.log_error_metrics(error_response)
            
            # Use fallback response for problem validation
            fallback_data = self.error_handler.create_fallback_response("problem_validation", {})
            
            # Add structured error and fallback to state
            state.market_validation.update({
                "problem_validation_error": error_response.message,
                "problem_validation_error_timestamp": error_response.timestamp.isoformat(),
                "problem_validation_error_id": error_response.request_id,
                "recovery_suggestions": error_response.recovery_suggestions,
                **fallback_data
            })
            state.update_timestamp()
            return state
    
    async def _business_analysis_node(self, state: ProductState) -> ProductState:
        """
        Business analysis node with enhanced error handling.
        
        Args:
            state: Current workflow state
            
        Returns:
            State with business analysis completed
        """
        logger.info("Executing business analysis node", 
                   extra={'session_id': state.session_id, 'node_name': 'business_analysis'})
        
        try:
            # Business analysis is already done in problem validation
            # This node serves as a checkpoint and can add additional analysis if needed
            
            if not state.business_model:
                logger.warning("Business model not found, re-running BPA agent")
                try:
                    state = await self.bpa_agent.analyze_business_viability(state)
                except Exception as bpa_error:
                    error_response = await self.error_handler.handle_workflow_error(
                        bpa_error, state.session_id or "unknown", "business_analysis_bpa_retry", state
                    )
                    logger.error(f"BPA agent retry failed [{error_response.request_id}]: {error_response.message}")
                    
                    # Use fallback business model
                    fallback_data = self.error_handler.create_fallback_response("business_model", {})
                    state.market_validation.update({
                        "bpa_retry_error": error_response.message,
                        "bpa_retry_error_id": error_response.request_id,
                        "business_model_fallback": fallback_data
                    })
            
            # Update phase
            state.current_phase = "validation"
            state.update_timestamp()
            
            # Save state with error handling
            if state.session_id:
                try:
                    self.memory.save_session(state.session_id, state)
                except Exception as save_error:
                    error_response = await self.error_handler.handle_persistence_error(
                        save_error, "save", state.session_id
                    )
                    logger.warning(f"State save failed in business analysis [{error_response.request_id}]: {error_response.message}")
            
            logger.info("Business analysis completed", 
                       extra={
                           'session_id': state.session_id, 
                           'node_name': 'business_analysis',
                           'phase': state.current_phase,
                           'has_business_model': state.business_model is not None
                       })
            return state
            
        except Exception as e:
            # Handle error with structured error handling
            error_response = await self.error_handler.handle_workflow_error(
                e, state.session_id or "unknown", "business_analysis", state
            )
            
            logger.error(f"Business analysis node failed [{error_response.request_id}]: {error_response.message}")
            self.error_handler.log_error_metrics(error_response)
            
            # Add structured error to state
            state.market_validation.update({
                "business_analysis_error": error_response.message,
                "business_analysis_error_timestamp": error_response.timestamp.isoformat(),
                "business_analysis_error_id": error_response.request_id,
                "recovery_suggestions": error_response.recovery_suggestions
            })
            state.update_timestamp()
            return state
    
    async def _market_research_node(self, state: ProductState) -> ProductState:
        """
        Market research node with enhanced error handling.
        
        Args:
            state: Current workflow state
            
        Returns:
            State with market research data
            
        Requirements: 3.1, 3.2, 3.3, 3.4 (error handling)
        """
        logger.info("Executing market research node", 
                   extra={'session_id': state.session_id, 'node_name': 'market_research'})
        
        try:
            # Conduct web research using WebResearchAgent
            async with WebResearchAgent() as research_agent:
                # Generate research query based on business model
                research_query = self._generate_research_query(state)
                
                # Conduct research with error handling
                try:
                    research_results = await research_agent.research_topic(research_query)
                    
                    # Update state with research data
                    state.research_data = research_results
                    state.current_phase = "planning"
                    state.update_timestamp()
                    
                    logger.info(f"Market research completed with {len(research_results)} results",
                               extra={
                                   'session_id': state.session_id, 
                                   'node_name': 'market_research',
                                   'research_count': len(research_results),
                                   'phase': state.current_phase
                               })
                    
                except Exception as research_error:
                    # Handle research-specific errors
                    error_response = await self.error_handler.handle_workflow_error(
                        research_error, state.session_id or "unknown", "market_research_web", state
                    )
                    
                    logger.warning(f"Web research failed [{error_response.request_id}]: {error_response.message}")
                    
                    # Continue with fallback research data
                    state.research_data = [{
                        "url": "fallback",
                        "title": "Research Unavailable",
                        "content": f"Market research failed: {error_response.message}",
                        "timestamp": datetime.now().isoformat(),
                        "success": False,
                        "error_message": error_response.message,
                        "error_id": error_response.request_id,
                        "metadata": {"fallback": True, "recovery_suggestions": error_response.recovery_suggestions}
                    }]
                    state.current_phase = "planning"
                    state.update_timestamp()
                
                # Save state with error handling
                if state.session_id:
                    try:
                        self.memory.save_session(state.session_id, state)
                    except Exception as save_error:
                        error_response = await self.error_handler.handle_persistence_error(
                            save_error, "save", state.session_id
                        )
                        logger.warning(f"State save failed in market research [{error_response.request_id}]: {error_response.message}")
                
                return state
                
        except Exception as e:
            # Handle node-level errors
            error_response = await self.error_handler.handle_workflow_error(
                e, state.session_id or "unknown", "market_research", state
            )
            
            logger.error(f"Market research node failed [{error_response.request_id}]: {error_response.message}")
            self.error_handler.log_error_metrics(error_response)
            
            # Continue with fallback research data
            state.research_data = [{
                "url": "error",
                "title": "Research Failed",
                "content": f"Market research failed: {error_response.message}",
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error_message": error_response.message,
                "error_id": error_response.request_id,
                "metadata": {"fallback": True, "recovery_suggestions": error_response.recovery_suggestions}
            }]
            
            # Add structured error to state
            state.market_validation.update({
                "market_research_error": error_response.message,
                "market_research_error_timestamp": error_response.timestamp.isoformat(),
                "market_research_error_id": error_response.request_id,
                "recovery_suggestions": error_response.recovery_suggestions
            })
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
        logger.info("Executing MVP planning node", 
                   extra={'session_id': state.session_id, 'node_name': 'mvp_planning'})
        
        try:
            # MVP features are already generated by BPA agent
            # This node can refine or validate the feature specifications
            
            if not state.feature_specifications:
                logger.warning("Feature specifications not found, re-running BPA agent")
                try:
                    state = await self.bpa_agent.analyze_business_viability(state)
                except Exception as bpa_error:
                    error_response = await self.error_handler.handle_workflow_error(
                        bpa_error, state.session_id or "unknown", "mvp_planning_bpa_retry", state
                    )
                    logger.error(f"BPA agent retry failed in MVP planning [{error_response.request_id}]: {error_response.message}")
                    
                    # Use fallback MVP features
                    fallback_data = self.error_handler.create_fallback_response("mvp_features", {})
                    state.market_validation.update({
                        "mvp_bpa_retry_error": error_response.message,
                        "mvp_bpa_retry_error_id": error_response.request_id,
                        "mvp_features_fallback": fallback_data
                    })
            
            # Update phase
            state.current_phase = "mvp_design"
            state.update_timestamp()
            
            # Save state with error handling
            if state.session_id:
                try:
                    self.memory.save_session(state.session_id, state)
                except Exception as save_error:
                    error_response = await self.error_handler.handle_persistence_error(
                        save_error, "save", state.session_id
                    )
                    logger.warning(f"State save failed in MVP planning [{error_response.request_id}]: {error_response.message}")
            
            logger.info(f"MVP planning completed with {len(state.feature_specifications)} features",
                       extra={
                           'session_id': state.session_id, 
                           'node_name': 'mvp_planning',
                           'feature_count': len(state.feature_specifications),
                           'phase': state.current_phase
                       })
            return state
            
        except Exception as e:
            # Handle error with structured error handling
            error_response = await self.error_handler.handle_workflow_error(
                e, state.session_id or "unknown", "mvp_planning", state
            )
            
            logger.error(f"MVP planning node failed [{error_response.request_id}]: {error_response.message}")
            self.error_handler.log_error_metrics(error_response)
            
            # Add structured error to state
            state.market_validation.update({
                "mvp_planning_error": error_response.message,
                "mvp_planning_error_timestamp": error_response.timestamp.isoformat(),
                "mvp_planning_error_id": error_response.request_id,
                "recovery_suggestions": error_response.recovery_suggestions
            })
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
        logger.info("Executing technical architecture node", 
                   extra={'session_id': state.session_id, 'node_name': 'technical_architecture'})
        
        try:
            # Generate basic technical architecture based on features
            tech_architecture = self._generate_technical_architecture(state)
            
            state.technical_architecture = tech_architecture
            state.update_timestamp()
            
            # Save state with error handling
            if state.session_id:
                try:
                    self.memory.save_session(state.session_id, state)
                except Exception as save_error:
                    error_response = await self.error_handler.handle_persistence_error(
                        save_error, "save", state.session_id
                    )
                    logger.warning(f"State save failed in technical architecture [{error_response.request_id}]: {error_response.message}")
            
            logger.info("Technical architecture completed",
                       extra={
                           'session_id': state.session_id, 
                           'node_name': 'technical_architecture',
                           'architecture_type': tech_architecture.get('architecture_type', 'unknown')
                       })
            return state
            
        except Exception as e:
            # Handle error with structured error handling
            error_response = await self.error_handler.handle_workflow_error(
                e, state.session_id or "unknown", "technical_architecture", state
            )
            
            logger.error(f"Technical architecture node failed [{error_response.request_id}]: {error_response.message}")
            self.error_handler.log_error_metrics(error_response)
            
            # Add structured error to state
            state.market_validation.update({
                "tech_architecture_error": error_response.message,
                "tech_architecture_error_timestamp": error_response.timestamp.isoformat(),
                "tech_architecture_error_id": error_response.request_id,
                "recovery_suggestions": error_response.recovery_suggestions
            })
            state.update_timestamp()
            return state
    
    async def _gtm_strategy_node(self, state: ProductState) -> ProductState:
        """
        GTM strategy node with enhanced error handling.
        
        Args:
            state: Current workflow state
            
        Returns:
            State with GTM strategy
            
        Requirements: 5.1, 5.2, 5.3, 5.4
        """
        logger.info("Executing GTM strategy node", 
                   extra={'session_id': state.session_id, 'node_name': 'gtm_strategy'})
        
        try:
            # Use GTM agent to develop strategy
            updated_state = await self.gtm_agent.develop_gtm_strategy(state)
            
            # Save state with error handling
            if updated_state.session_id:
                try:
                    self.memory.save_session(updated_state.session_id, updated_state)
                except Exception as save_error:
                    error_response = await self.error_handler.handle_persistence_error(
                        save_error, "save", updated_state.session_id
                    )
                    logger.warning(f"State save failed in GTM strategy [{error_response.request_id}]: {error_response.message}")
            
            logger.info("GTM strategy completed",
                       extra={
                           'session_id': updated_state.session_id, 
                           'node_name': 'gtm_strategy',
                           'has_gtm_strategy': updated_state.gtm_strategy is not None
                       })
            return updated_state
            
        except Exception as e:
            # Handle error with structured error handling
            error_response = await self.error_handler.handle_workflow_error(
                e, state.session_id or "unknown", "gtm_strategy", state
            )
            
            logger.error(f"GTM strategy node failed [{error_response.request_id}]: {error_response.message}")
            self.error_handler.log_error_metrics(error_response)
            
            # Add structured error to state
            state.market_validation.update({
                "gtm_strategy_error": error_response.message,
                "gtm_strategy_error_timestamp": error_response.timestamp.isoformat(),
                "gtm_strategy_error_id": error_response.request_id,
                "recovery_suggestions": error_response.recovery_suggestions
            })
            state.update_timestamp()
            return state
    
    async def _execution_roadmap_node(self, state: ProductState) -> ProductState:
        """
        Execution roadmap node with enhanced error handling.
        
        Args:
            state: Current workflow state
            
        Returns:
            State with execution roadmap
            
        Requirements: 7.1, 7.2, 7.3, 7.4
        """
        logger.info("Executing execution roadmap node", 
                   extra={'session_id': state.session_id, 'node_name': 'execution_roadmap'})
        
        try:
            # Use transition agent to generate roadmap
            updated_state = await self.transition_agent.generate_product_roadmap(state)
            
            # Final phase update
            updated_state.current_phase = "gtm_planning"
            updated_state.update_timestamp()
            
            # Save final state with error handling
            if updated_state.session_id:
                try:
                    self.memory.save_session(updated_state.session_id, updated_state)
                except Exception as save_error:
                    error_response = await self.error_handler.handle_persistence_error(
                        save_error, "save", updated_state.session_id
                    )
                    logger.warning(f"Final state save failed in execution roadmap [{error_response.request_id}]: {error_response.message}")
                    # Add save error to state but continue
                    updated_state.market_validation["final_save_error"] = error_response.message
                    updated_state.market_validation["final_save_error_id"] = error_response.request_id
            
            logger.info("Execution roadmap completed - workflow finished successfully",
                       extra={
                           'session_id': updated_state.session_id, 
                           'node_name': 'execution_roadmap',
                           'final_phase': updated_state.current_phase,
                           'roadmap_phases': len(updated_state.mvp_roadmap)
                       })
            return updated_state
            
        except Exception as e:
            # Handle error with structured error handling
            error_response = await self.error_handler.handle_workflow_error(
                e, state.session_id or "unknown", "execution_roadmap", state
            )
            
            logger.error(f"Execution roadmap node failed [{error_response.request_id}]: {error_response.message}")
            self.error_handler.log_error_metrics(error_response)
            
            # Add structured error to state
            state.market_validation.update({
                "execution_roadmap_error": error_response.message,
                "execution_roadmap_error_timestamp": error_response.timestamp.isoformat(),
                "execution_roadmap_error_id": error_response.request_id,
                "recovery_suggestions": error_response.recovery_suggestions
            })
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
        logger.info("Executing rejection report node", 
                   extra={'session_id': state.session_id, 'node_name': 'rejection_report'})
        
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
            
            # Save state with error handling
            if state.session_id:
                try:
                    self.memory.save_session(state.session_id, state)
                except Exception as save_error:
                    error_response = await self.error_handler.handle_persistence_error(
                        save_error, "save", state.session_id
                    )
                    logger.warning(f"State save failed in rejection report [{error_response.request_id}]: {error_response.message}")
            
            logger.info("Rejection report completed",
                       extra={
                           'session_id': state.session_id, 
                           'node_name': 'rejection_report',
                           'workflow_status': 'rejected',
                           'validation_score': state.market_validation.get("overall_score", "N/A")
                       })
            return state
            
        except Exception as e:
            # Handle error with structured error handling
            error_response = await self.error_handler.handle_workflow_error(
                e, state.session_id or "unknown", "rejection_report", state
            )
            
            logger.error(f"Rejection report node failed [{error_response.request_id}]: {error_response.message}")
            self.error_handler.log_error_metrics(error_response)
            
            # Add structured error to state
            state.market_validation.update({
                "rejection_report_error": error_response.message,
                "rejection_report_error_timestamp": error_response.timestamp.isoformat(),
                "rejection_report_error_id": error_response.request_id,
                "recovery_suggestions": error_response.recovery_suggestions
            })
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