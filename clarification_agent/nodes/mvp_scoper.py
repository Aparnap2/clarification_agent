from typing import Dict, Any
from clarification_agent.nodes.base_node import BaseNodeHandler
from clarification_agent.models.project import Project
from clarification_agent.utils.llm_helper import LLMHelper

class MVPScoperNode(BaseNodeHandler):
    """
    Node for defining the MVP features.
    """
    
    def get_ui_data(self, project: Project) -> Dict[str, Any]:
        """Get UI data for the MVPScoper node"""
        # Generate AI suggestions for MVP features based on goals
        ai_suggestions = ""
        if project.goals and not project.mvp_features:
            llm_helper = LLMHelper()
            suggestion = llm_helper.generate_suggestions(
                "Based on these project goals, suggest 3-7 essential MVP features that would deliver core value:",
                {"goals": project.goals, "description": project.description}
            )
            ai_suggestions = f"\n\nAI-Suggested MVP Features:\n{suggestion}"
        
        return {
            "title": "MVP Feature Scoping",
            "description": f"Now, let's define the core features that will be included in the MVP.{ai_suggestions}",
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