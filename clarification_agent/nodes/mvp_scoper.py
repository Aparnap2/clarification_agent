from typing import Dict, Any
from clarification_agent.nodes.base_node import BaseNodeHandler
from clarification_agent.models.project import Project

class MVPScoperNode(BaseNodeHandler):
    """
    Node for defining the MVP features.
    """
    
    def get_ui_data(self, project: Project) -> Dict[str, Any]:
        """Get UI data for the MVPScoper node"""
        return {
            "title": "MVP Feature Scoping",
            "description": "Now, let's define the core features that will be included in the MVP.",
            "questions": [
                {
                    "id": "mvp_features",
                    "question": "What are the essential features for the MVP? (One per line)",
                    "type": "text",
                    "value": "\\n".join(project.mvp_features) if project.mvp_features else ""
                },
                {
                    "id": "target_user",
                    "question": "Who is the target user for this MVP?",
                    "type": "text",
                    "value": project.target_user or ""
                }
            ]
        }
    
    def process_responses(self, project: Project, responses: Dict[str, Any]) -> None:
        """Process responses for the MVPScoper node"""
        # Process MVP features (split by newlines)
        features_text = responses.get("mvp_features", "")
        project.mvp_features = [feature.strip() for feature in features_text.split("\\n") if feature.strip()]
        
        # Set target user
        project.target_user = responses.get("target_user", "")