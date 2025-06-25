from typing import Optional
from clarification_agent.nodes.base_node import BaseNodeHandler
from clarification_agent.nodes.clarify_intent import ClarifyIntentNode
from clarification_agent.nodes.not_builder import NotBuilderNode
from clarification_agent.nodes.mvp_scoper import MVPScoperNode
from clarification_agent.nodes.stack_selector import StackSelectorNode
from clarification_agent.nodes.reasoner import ReasonerNode
from clarification_agent.nodes.file_map_builder import FileMapBuilderNode
from clarification_agent.nodes.task_planner import TaskPlannerNode
from clarification_agent.nodes.exporter import ExporterNode
from clarification_agent.nodes.start import StartNode

def get_node_handler(node_name: str) -> Optional[BaseNodeHandler]:
    """
    Factory function to get the appropriate node handler.
    
    Args:
        node_name: Name of the node
        
    Returns:
        Node handler instance or None if not found
    """
    node_map = {
        "Start": StartNode(),
        "ClarifyIntent": ClarifyIntentNode(),
        "NotBuilder": NotBuilderNode(),
        "MVPScoper": MVPScoperNode(),
        "StackSelector": StackSelectorNode(),
        "Reasoner": ReasonerNode(),
        "FileMapBuilder": FileMapBuilderNode(),
        "TaskPlanner": TaskPlannerNode(),
        "Exporter": ExporterNode()
    }
    
    return node_map.get(node_name)