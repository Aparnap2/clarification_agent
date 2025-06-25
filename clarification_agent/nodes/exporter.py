from typing import Dict, Any
from clarification_agent.nodes.base_node import BaseNodeHandler
from clarification_agent.models.project import Project
from clarification_agent.output.exporter import Exporter

class ExporterNode(BaseNodeHandler):
    """
    Node for exporting the final project files.
    """
    
    def get_ui_data(self, project: Project) -> Dict[str, Any]:
        """Get UI data for the Exporter node"""
        return {
            "title": "Export Project Files",
            "description": "Your project planning is complete! Click 'Continue' to export all files.",
            "questions": []
        }
    
    def process_responses(self, project: Project, responses: Dict[str, Any]) -> None:
        """Process responses for the Exporter node"""
        # Export all files
        exporter = Exporter(project)
        exporter.export_all()