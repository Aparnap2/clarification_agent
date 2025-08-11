"""Centralized error handling for AI Strategy Assistant components."""

import logging
import traceback
from datetime import datetime
from typing import Any, Dict, Optional, Union
from enum import Enum

import openai
from pydantic import BaseModel

from models.data_models import ProductState

logger = logging.getLogger(__name__)


class ErrorType(str, Enum):
    """Error type enumeration for categorization."""
    LLM_ERROR = "llm_error"
    PERSISTENCE_ERROR = "persistence_error"
    WORKFLOW_ERROR = "workflow_error"
    VALIDATION_ERROR = "validation_error"
    NETWORK_ERROR = "network_error"
    TIMEOUT_ERROR = "timeout_error"
    UNKNOWN_ERROR = "unknown_error"


class ErrorResponse(BaseModel):
    """Structured error response model."""
    error_type: ErrorType
    message: str
    request_id: str
    timestamp: datetime
    recovery_suggestions: list[str] = []
    debug_info: Optional[Dict[str, Any]] = None
    fallback_used: bool = False


class ErrorHandler:
    """
    Centralized error handling with recovery strategies for AI Strategy Assistant.
    
    Provides structured error handling for LLM calls, persistence operations,
    and workflow execution with fallback mechanisms and recovery suggestions.
    """
    
    def __init__(self, enable_debug: bool = False):
        """
        Initialize ErrorHandler with configuration.
        
        Args:
            enable_debug: Whether to include debug information in error responses
        """
        self.enable_debug = enable_debug
        self.request_counter = 0
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID for error tracking."""
        self.request_counter += 1
        return f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.request_counter:04d}"
    
    async def handle_llm_error(self, error: Exception, context: Dict[str, Any]) -> ErrorResponse:
        """
        Handle LLM API failures with fallbacks and recovery strategies.
        
        Args:
            error: The exception that occurred
            context: Context information (model, prompt, attempt_count, etc.)
            
        Returns:
            ErrorResponse with recovery suggestions and fallback data
        """
        request_id = self._generate_request_id()
        error_type = self._classify_llm_error(error)
        
        logger.error(f"LLM error [{request_id}]: {error} - Context: {context}")
        
        # Generate recovery suggestions based on error type
        recovery_suggestions = self._get_llm_recovery_suggestions(error, context)
        
        # Prepare debug info if enabled
        debug_info = None
        if self.enable_debug:
            debug_info = {
                "error_class": error.__class__.__name__,
                "error_details": str(error),
                "traceback": traceback.format_exc(),
                "context": context,
                "model": context.get("model", "unknown"),
                "attempt_count": context.get("attempt_count", 1)
            }
        
        # Determine if fallback was used
        fallback_used = context.get("fallback_used", False)
        
        return ErrorResponse(
            error_type=error_type,
            message=self._get_user_friendly_message(error, context),
            request_id=request_id,
            timestamp=datetime.now(),
            recovery_suggestions=recovery_suggestions,
            debug_info=debug_info,
            fallback_used=fallback_used
        )
    
    async def handle_persistence_error(self, error: Exception, operation: str, session_id: Optional[str] = None) -> ErrorResponse:
        """
        Handle persistence failures with recovery strategies.
        
        Args:
            error: The exception that occurred
            operation: The persistence operation that failed (save, load, delete)
            session_id: Optional session ID for context
            
        Returns:
            ErrorResponse with recovery suggestions
        """
        request_id = self._generate_request_id()
        
        logger.error(f"Persistence error [{request_id}]: {error} - Operation: {operation}, Session: {session_id}")
        
        # Generate recovery suggestions
        recovery_suggestions = self._get_persistence_recovery_suggestions(error, operation)
        
        # Prepare debug info if enabled
        debug_info = None
        if self.enable_debug:
            debug_info = {
                "error_class": error.__class__.__name__,
                "error_details": str(error),
                "traceback": traceback.format_exc(),
                "operation": operation,
                "session_id": session_id
            }
        
        return ErrorResponse(
            error_type=ErrorType.PERSISTENCE_ERROR,
            message=f"Storage operation '{operation}' failed: {str(error)}",
            request_id=request_id,
            timestamp=datetime.now(),
            recovery_suggestions=recovery_suggestions,
            debug_info=debug_info,
            fallback_used=False
        )
    
    async def handle_workflow_error(self, error: Exception, thread_id: str, node_name: Optional[str] = None, state: Optional[ProductState] = None) -> ErrorResponse:
        """
        Handle workflow execution failures with state recovery.
        
        Args:
            error: The exception that occurred
            thread_id: LangGraph thread ID
            node_name: Optional workflow node where error occurred
            state: Optional current state for recovery context
            
        Returns:
            ErrorResponse with recovery suggestions and state information
        """
        request_id = self._generate_request_id()
        
        logger.error(f"Workflow error [{request_id}]: {error} - Thread: {thread_id}, Node: {node_name}")
        
        # Generate recovery suggestions
        recovery_suggestions = self._get_workflow_recovery_suggestions(error, node_name, state)
        
        # Prepare debug info if enabled
        debug_info = None
        if self.enable_debug:
            debug_info = {
                "error_class": error.__class__.__name__,
                "error_details": str(error),
                "traceback": traceback.format_exc(),
                "thread_id": thread_id,
                "node_name": node_name,
                "current_phase": state.current_phase if state else "unknown",
                "session_id": state.session_id if state else None
            }
        
        return ErrorResponse(
            error_type=ErrorType.WORKFLOW_ERROR,
            message=f"Workflow execution failed at {node_name or 'unknown node'}: {str(error)}",
            request_id=request_id,
            timestamp=datetime.now(),
            recovery_suggestions=recovery_suggestions,
            debug_info=debug_info,
            fallback_used=False
        )
    
    def _classify_llm_error(self, error: Exception) -> ErrorType:
        """Classify LLM errors for appropriate handling."""
        if isinstance(error, openai.RateLimitError):
            return ErrorType.NETWORK_ERROR
        elif isinstance(error, openai.APITimeoutError):
            return ErrorType.TIMEOUT_ERROR
        elif isinstance(error, (openai.APIConnectionError, openai.APIError)):
            return ErrorType.NETWORK_ERROR
        elif isinstance(error, openai.AuthenticationError):
            return ErrorType.LLM_ERROR
        elif isinstance(error, (ValueError, KeyError)) and "json" in str(error).lower():
            return ErrorType.VALIDATION_ERROR
        else:
            return ErrorType.LLM_ERROR
    
    def _get_llm_recovery_suggestions(self, error: Exception, context: Dict[str, Any]) -> list[str]:
        """Generate recovery suggestions for LLM errors."""
        suggestions = []
        
        if isinstance(error, openai.RateLimitError):
            suggestions.extend([
                "Wait and retry with exponential backoff",
                "Switch to a different model with lower rate limits",
                "Use cached responses if available"
            ])
        elif isinstance(error, openai.APITimeoutError):
            suggestions.extend([
                "Retry with shorter timeout",
                "Break down the request into smaller parts",
                "Use a faster model variant"
            ])
        elif isinstance(error, openai.AuthenticationError):
            suggestions.extend([
                "Check API key configuration",
                "Verify API key permissions",
                "Use fallback model or cached response"
            ])
        elif isinstance(error, (openai.APIConnectionError, openai.APIError)):
            suggestions.extend([
                "Check network connectivity",
                "Retry with exponential backoff",
                "Use fallback model or offline mode"
            ])
        elif "json" in str(error).lower():
            suggestions.extend([
                "Retry with simplified prompt",
                "Use structured output format",
                "Parse response more flexibly"
            ])
        else:
            suggestions.extend([
                "Retry with different parameters",
                "Use fallback response",
                "Log error for investigation"
            ])
        
        # Add attempt-specific suggestions
        attempt_count = context.get("attempt_count", 1)
        if attempt_count > 1:
            suggestions.append(f"This is attempt {attempt_count} - consider using fallback")
        
        return suggestions
    
    def _get_persistence_recovery_suggestions(self, error: Exception, operation: str) -> list[str]:
        """Generate recovery suggestions for persistence errors."""
        suggestions = []
        
        if "permission" in str(error).lower() or "access" in str(error).lower():
            suggestions.extend([
                "Check file permissions",
                "Verify directory write access",
                "Use alternative storage location"
            ])
        elif "disk" in str(error).lower() or "space" in str(error).lower():
            suggestions.extend([
                "Free up disk space",
                "Use compression for storage",
                "Clean up old sessions"
            ])
        elif "corrupt" in str(error).lower() or "pickle" in str(error).lower():
            suggestions.extend([
                "Use backup file if available",
                "Reset storage and start fresh",
                "Migrate to new storage format"
            ])
        elif operation == "load":
            suggestions.extend([
                "Check if session exists",
                "Use default state if session not found",
                "Verify file integrity"
            ])
        elif operation == "save":
            suggestions.extend([
                "Retry save operation",
                "Use temporary file for atomic write",
                "Fall back to in-memory storage"
            ])
        else:
            suggestions.extend([
                "Retry operation with backoff",
                "Check storage system health",
                "Use alternative persistence method"
            ])
        
        return suggestions
    
    def _get_workflow_recovery_suggestions(self, error: Exception, node_name: Optional[str], state: Optional[ProductState]) -> list[str]:
        """Generate recovery suggestions for workflow errors."""
        suggestions = []
        
        if node_name:
            suggestions.append(f"Retry from {node_name} node")
            
            if "validation" in node_name:
                suggestions.extend([
                    "Check input data quality",
                    "Use fallback validation logic",
                    "Skip validation with warning"
                ])
            elif "research" in node_name:
                suggestions.extend([
                    "Continue without web research",
                    "Use cached research data",
                    "Retry with different search terms"
                ])
            elif "analysis" in node_name:
                suggestions.extend([
                    "Use simplified analysis",
                    "Continue with partial results",
                    "Retry with different model"
                ])
        
        if state:
            suggestions.extend([
                f"Resume from {state.current_phase} phase",
                "Use last known good state",
                "Continue with available data"
            ])
        
        suggestions.extend([
            "Restart workflow from beginning",
            "Use manual intervention mode",
            "Save current state and investigate"
        ])
        
        return suggestions
    
    def _get_user_friendly_message(self, error: Exception, context: Dict[str, Any]) -> str:
        """Generate user-friendly error messages."""
        if isinstance(error, openai.RateLimitError):
            return "API rate limit exceeded. Please wait a moment and try again."
        elif isinstance(error, openai.APITimeoutError):
            return "Request timed out. The analysis is taking longer than expected."
        elif isinstance(error, openai.AuthenticationError):
            return "Authentication failed. Please check your API configuration."
        elif isinstance(error, (openai.APIConnectionError, openai.APIError)):
            return "Unable to connect to AI service. Please check your internet connection."
        elif "json" in str(error).lower():
            return "Response parsing failed. The AI service returned an unexpected format."
        else:
            return f"An unexpected error occurred during {context.get('operation', 'processing')}: {str(error)}"
    
    def create_fallback_response(self, operation: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create fallback responses for failed operations.
        
        Args:
            operation: The operation that failed
            context: Context information for generating appropriate fallback
            
        Returns:
            Fallback response data
        """
        fallback_data = {
            "fallback": True,
            "operation": operation,
            "timestamp": datetime.now().isoformat(),
            "message": f"Using fallback response for {operation}"
        }
        
        if operation == "problem_validation":
            fallback_data.update({
                "problem_score": 3,
                "market_size_score": 3,
                "solution_fit_score": 3,
                "overall_score": 3.0,
                "reasoning": "Validation failed due to technical error. Manual review required.",
                "recommendations": ["Review project manually", "Retry validation later"],
                "should_continue": False,
                "validation_questions": ["What specific problem are you solving?"]
            })
        elif operation == "business_model":
            fallback_data.update({
                "value_proposition": "Solve customer problems efficiently",
                "target_customer": "Businesses needing efficiency solutions",
                "revenue_streams": ["Service fees"],
                "cost_structure": ["Development", "Operations"],
                "key_metrics": ["Revenue", "Customer satisfaction"]
            })
        elif operation == "competitor_analysis":
            fallback_data.update({
                "competitors": [{
                    "competitor_name": "Market Incumbent",
                    "value_proposition": "Established solution",
                    "target_market": "General market",
                    "key_strengths": ["Market presence"],
                    "market_gaps": ["Innovation opportunity"],
                    "differentiation_opportunities": ["Better user experience"]
                }]
            })
        elif operation == "mvp_features":
            fallback_data.update({
                "features": [{
                    "name": "Core Functionality",
                    "user_story": "As a user, I want basic functionality, so that I can solve my problem",
                    "acceptance_criteria": [
                        "WHEN user accesses system THEN it SHALL provide core functionality",
                        "WHEN user performs action THEN system SHALL respond appropriately"
                    ],
                    "mvp_priority": "CORE",
                    "effort_estimate": "M",
                    "business_impact": "High"
                }]
            })
        
        return fallback_data
    
    def log_error_metrics(self, error_response: ErrorResponse) -> None:
        """
        Log error metrics for monitoring and analysis.
        
        Args:
            error_response: The error response to log
        """
        try:
            metrics = {
                "request_id": error_response.request_id,
                "error_type": error_response.error_type.value,
                "timestamp": error_response.timestamp.isoformat(),
                "fallback_used": error_response.fallback_used,
                "recovery_suggestions_count": len(error_response.recovery_suggestions)
            }
            
            # Log as structured data for monitoring systems
            logger.info(f"ERROR_METRICS: {metrics}")
            
        except Exception as e:
            logger.error(f"Failed to log error metrics: {e}")