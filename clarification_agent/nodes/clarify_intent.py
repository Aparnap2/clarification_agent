from typing import Dict, Any
from clarification_agent.nodes.base_node import BaseNode
from clarification_agent.utils.llm_helper import LLMHelper
from clarification_agent.core.clarity_validator import ClarityValidator
from langchain_core.messages import AIMessage

class ClarificationNode(BaseNode):
    """Node for clarifying the user's intent."""

    def __init__(self):
        """Initialize the clarification node with helpers."""
        self.llm_helper = LLMHelper()
        self.clarity_validator = ClarityValidator()

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes the user's query and asks for clarification if needed."""
        messages = state.get("messages", [])
        if not messages:
            # No messages to process
            return state

        # Initialize context if not present
        if "context" not in state:
            state["context"] = {}

        user_input = messages[-1].content
        
        # Use the validator to analyze the query
        analysis_result = self.clarity_validator.analyze_query(user_input) if hasattr(self.clarity_validator, "analyze_query") else None
        
        # If we don't have analysis results or the method doesn't exist, fall back to LLM
        if not analysis_result:
            # Use the LLM to check for ambiguity
            prompt = f"Is the following user query ambiguous or does it need more detail? Answer with only 'yes' or 'no'.\n\nQuery: {user_input}"
            is_ambiguous_response = self.llm_helper.generate(prompt).strip().lower()
            is_ambiguous = "yes" in is_ambiguous_response
        else:
            is_ambiguous = analysis_result.get("is_ambiguous", False)
            
        # Store analysis in context for other nodes to use
        state["context"]["query_analysis"] = {
            "is_ambiguous": is_ambiguous,
            "search_intent": analysis_result.get("search_intent", False) if analysis_result else False,
            "reasoning_intent": analysis_result.get("reasoning_intent", False) if analysis_result else False,
            "confidence": analysis_result.get("confidence", 0.5) if analysis_result else 0.5
        }

        if is_ambiguous:
            # Generate a clarifying question based on the ambiguity
            # Ask LLM to generate a helpful clarifying question
            clarification_prompt = f"""
            The following user query is ambiguous or needs more detail: '{user_input}'
            
            As an AI assistant, ask a specific, targeted question to clarify what the user meant.
            Focus on the most ambiguous part of their query.
            
            Your clarifying question should be friendly and conversational, and should help you
            understand exactly what the user is looking for.
            """
            clarifying_question = self.llm_helper.generate(clarification_prompt)
            new_message = AIMessage(content=clarifying_question)
        else:
            # The query is clear - provide a brief acknowledgment
            # We use a minimal message since this node is not the final responder
            new_message = AIMessage(content="I understand your query. Let me process that for you.")

        state["messages"].append(new_message)
        return state
