from typing import Annotated, List
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from clarification_agent.nodes.clarify_intent import ClarificationNode
from clarification_agent.nodes.reasoner import ReasonerNode
from clarification_agent.nodes.search_node import SearchNode
from clarification_agent.core.clarity_validator import ClarityValidator

class ConversationState(TypedDict):
    messages: Annotated[List, add_messages]
    context: dict

def get_agent():
    """Creates and configures the LangGraph-based clarification agent."""
    
    # Initialize nodes
    clarification_node = ClarificationNode()
    reasoner_node = ReasonerNode()
    search_node = SearchNode()

    # Define the graph
    graph_builder = StateGraph(ConversationState)

    # Add nodes to the graph
    graph_builder.add_node("clarify", clarification_node.execute)
    graph_builder.add_node("reason", reasoner_node.execute)
    graph_builder.add_node("search", search_node.execute)

    # Set the entry point
    graph_builder.set_entry_point("clarify")

    # Add conditional edges
    def should_continue(state: ConversationState):
        """Determine the next node based on the conversation state."""
        try:
            # Get the last message content
            last_message = state["messages"][-1].content.lower()
            
            # Check if we need more clarification
            needs_clarification = any([
                "?" in last_message,  # Ends with a question
                "clarify" in last_message,
                "not sure" in last_message,
                "don't know" in last_message,
                "confused" in last_message
            ])
            
            # Check if this is a search query
            is_search_query = any([
                "search" in last_message,
                "find" in last_message,
                "look up" in last_message,
                "information about" in last_message
            ])
            
            # Determine next node
            if needs_clarification:
                return "clarify"
            elif is_search_query:
                return "search"
            else:
                return "reason"
                
        except Exception as e:
            print(f"Error in should_continue: {e}")
            return "reason"  # Default to reason node on error

    # Add conditional edges
    graph_builder.add_conditional_edges(
        "clarify",
        should_continue,
        {
            "clarify": "clarify",
            "reason": "reason",
            "search": "search"
        },
    )
    
    # Add edges
    graph_builder.add_edge("reason", END)
    graph_builder.add_edge("search", "reason")  # After search, go to reason

    # Compile the graph into a runnable agent
    agent = graph_builder.compile()
    return agent
