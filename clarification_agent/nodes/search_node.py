from typing import Dict, Any, List
from clarification_agent.nodes.base_node import BaseNode
from clarification_agent.utils.llm_helper import LLMHelper
from clarification_agent.utils.web_search import WebSearchHelper
from langchain_core.messages import AIMessage

class SearchNode(BaseNode):
    """Node for performing web searches and retrieving relevant information."""

    def __init__(self):
        """Initialize the search node with web search helper."""
        self.web_search = WebSearchHelper()
        self.llm_helper = LLMHelper()

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs a web search based on the user's query and adds relevant information to the state.
        
        Args:
            state: The current conversation state including messages and context
            
        Returns:
            The updated state with search results and a message informing the user
        """
        messages = state.get("messages", [])
        if not messages:
            return state
            
        # Initialize context if not present
        if "context" not in state:
            state["context"] = {}
        
        # Get the last user message
        user_query = ""
        for message in reversed(messages):
            if message.type == "human":
                user_query = message.content
                break
                
        if not user_query:
            # No user query found
            new_message = AIMessage(content="I couldn't find a query to search for. Could you please provide a specific question?")
            state["messages"].append(new_message)
            return state
            
        # Refine the search query to be more effective
        search_prompt = f"""
        Based on the following user query, create a search-optimized version that will yield 
        the most relevant results from a web search. Keep it concise and focused on the key terms.
        
        User query: {user_query}
        
        Search query:
        """
        
        optimized_query = self.llm_helper.generate(search_prompt).strip()
        
        # Perform the web search
        search_results = self.web_search.search_for_context(optimized_query)
        
        # Store search results in the state context
        state["context"]["search_results"] = search_results
        
        # If no results found
        if not search_results:
            new_message = AIMessage(content="I searched for information but couldn't find relevant results. Let me try to answer based on my knowledge.")
            state["messages"].append(new_message)
            return state
            
        # Format search results for the user
        result_summaries = []
        for result in search_results:
            source = result.get("source", "Web")
            title = result.get("title", "Search Result")
            snippet = result.get("snippet", "No preview available")
            url = result.get("url", "")
            
            result_summaries.append(f"Source: {source}\nTitle: {title}\nPreview: {snippet}\nURL: {url}")
        
        # Use LLM to prepare a message about the search
        context_builder = "\n\n".join(result_summaries)
        search_summary_prompt = f"""
        I've searched for information about the user's query: "{user_query}"
        
        Here are the search results:
        
        {context_builder}
        
        Based on these search results, write a brief message (2-3 sentences) to let the user know 
        you've found some information. Don't answer their question yet - just acknowledge that 
        you've found relevant information that will help you answer.
        """
        
        search_message = self.llm_helper.generate(search_summary_prompt)
        new_message = AIMessage(content=search_message)
        state["messages"].append(new_message)
        
        return state
