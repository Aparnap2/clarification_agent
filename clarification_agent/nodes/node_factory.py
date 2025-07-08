from typing import Optional
from clarification_agent.nodes.base_node import BaseNodeHandler
from clarification_agent.nodes.clarify_intent import ClarificationNode
from clarification_agent.nodes.not_builder import NotBuilderNode
from clarification_agent.nodes.mvp_scoper import MVPScoperNode
from clarification_agent.nodes.stack_selector import StackSelectorNode
from clarification_agent.nodes.reasoner import ReasonerNode
from clarification_agent.nodes.file_map_builder import FileMapBuilderNode
from clarification_agent.nodes.task_planner import TaskPlannerNode
from clarification_agent.nodes.exporter import ExporterNode
from clarification_agent.nodes.start import StartNode
from clarification_agent.nodes.dynamic_node import DynamicNode

def get_node_handler(node_name: str) -> Optional[BaseNodeHandler]:
    """
    Factory function to get the appropriate node handler.
    
    Args:
        node_name: Name of the node
        
    Returns:
        Node handler instance or None if not found
    """
    # Standard node handlers
    node_map = {
        "Start": StartNode(),
        "ClarifyIntent": ClarificationNode(),
        "NotBuilder": NotBuilderNode(),
        "MVPScoper": MVPScoperNode(),
        "StackSelector": StackSelectorNode(),
        "Reasoner": ReasonerNode(),
        "FileMapBuilder": FileMapBuilderNode(),
        "TaskPlanner": TaskPlannerNode(),
        "Exporter": ExporterNode()
    }
    
    # Check if we have a standard handler
    handler = node_map.get(node_name)
    if handler:
        return handler
    
    # If not a standard node, try to create a dynamic node
    # This allows for flexible node types determined by the LLM
    try:
        # Convert node name to a type string for the dynamic node
        node_type = node_name.lower()
        return DynamicNode(node_type)
    except Exception as e:
        print(f"Error creating dynamic node for {node_name}: {e}")
        return None