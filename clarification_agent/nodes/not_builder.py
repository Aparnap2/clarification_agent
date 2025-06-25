from typing import Dict, Any
from clarification_agent.nodes.base_node import BaseNodeHandler
from clarification_agent.models.project import Project

class NotBuilderNode(BaseNodeHandler):
    """
    Node for identifying what will NOT be included in the MVP.
    """
    
    def get_ui_data(self, project: Project) -> Dict[str, Any]:
        """Get UI data for the NotBuilder node"""
        return {
            "title": "Scope Reduction",
            "description": "Let's identify what will NOT be included in the MVP to keep the scope focused.",
            "questions": [
                {
                    "id": "excluded_features",
                    "question": "What features or capabilities will NOT be included in the MVP? (One per line)",
                    "type": "text",
                    "value": "\\n".join(project.excluded_features) if project.excluded_features else ""
                },
                {
                    "id": "constraints",
                    "question": "Are there any constraints or limitations to consider? (One per line)",
                    "type": "text",
                    "value": "\\n".join(project.constraints) if project.constraints else ""
                }
            ]
        }
    
    def process_responses(self, project: Project, responses: Dict[str, Any]) -> None:
        """Process responses for the NotBuilder node"""
        # Process excluded features (split by newlines)
        excluded_text = responses.get("excluded_features", "")
        project.excluded_features = [feature.strip() for feature in excluded_text.split("\\n") if feature.strip()]
        
        # Process constraints (split by newlines)
        constraints_text = responses.get("constraints", "")
        project.constraints = [constraint.strip() for constraint in constraints_text.split("\\n") if constraint.strip()]