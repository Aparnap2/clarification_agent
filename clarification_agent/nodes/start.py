from typing import Dict, Any
from clarification_agent.nodes.base_node import BaseNodeHandler
from clarification_agent.models.project import Project

class StartNode(BaseNodeHandler):
    """
    Starting node that checks if a project exists and initializes it.
    """
    
    def get_ui_data(self, project: Project) -> Dict[str, Any]:
        """Get UI data for the Start node"""
        return {
            "title": "Starting Project",
            "description": f"Initializing project: {project.name}",
            "questions": []
        }
    
    def process_responses(self, project: Project, responses: Dict[str, Any]) -> None:
        """Process responses for the Start node"""
        # Nothing to process here, just initialization
        pass