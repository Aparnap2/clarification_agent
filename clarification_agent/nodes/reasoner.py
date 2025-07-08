from typing import Dict, Any, List
from clarification_agent.nodes.base_node import BaseNode
from clarification_agent.utils.llm_helper import LLMHelper
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

class ReasonerNode(BaseNode):
    """Node for generating a final answer based on the clarified query and available context."""
    
    def __init__(self):
        """Initialize the reasoner node with helper."""
        self.llm_helper = LLMHelper()

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generates a final response using the conversation history and search context."""
        messages = state.get("messages", [])
        context = state.get("context", {})
        
        if not messages:
            return state
            
        # Check if we have search results in the context
        search_results = context.get("search_results", [])
        context_text = ""
        
        if search_results:
            # Format search results as context
            context_text = "\n\nRelevant information from search:\n"
            for i, result in enumerate(search_results, 1):
                source = result.get("source", "Web")
                title = result.get("title", "Search Result")
                snippet = result.get("snippet", "No preview available")
                url = result.get("url", "")
                
                context_text += f"\n[{i}] {title}\n"
                context_text += f"Source: {source}\n"
                context_text += f"Content: {snippet}\n"
                if url:
                    context_text += f"URL: {url}\n"
        
        # Create a prompt for the LLM to generate a final answer
        system_prompt = f"""Based on the following conversation, provide a comprehensive answer to the user's query. 
        The user's intent should now be clear.{context_text}
        
        If search results are provided, use them to enhance your answer.
        Provide a thoughtful, accurate, and helpful response that directly addresses the user's needs.
        """
        
        # Prepare messages for the LLM
        formatted_messages = [SystemMessage(content=system_prompt)]
        
        # Add conversation history
        for msg in messages:
            if msg.type == "human":
                formatted_messages.append(HumanMessage(content=msg.content))
            elif msg.type == "ai":
                formatted_messages.append(AIMessage(content=msg.content))
        
        # Generate the final answer
        response = self.llm_helper.llm.invoke(formatted_messages)
        final_answer = response.content
        
        # Add the final answer to the message list
        new_message = AIMessage(content=final_answer)
        state["messages"].append(new_message)
        
        return state
