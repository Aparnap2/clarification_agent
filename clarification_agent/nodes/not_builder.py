from typing import Dict, Any
from clarification_agent.nodes.base_node import BaseNodeHandler
from clarification_agent.models.project import Project
from clarification_agent.utils.llm_helper import LLMHelper

class NotBuilderNode(BaseNodeHandler):
    """
    Node for identifying what will NOT be included in the MVP.
    """
    
    def get_ui_data(self, project: Project) -> Dict[str, Any]:
        """Get UI data for the NotBuilder node"""
        # Generate AI suggestions for features to exclude
        ai_suggestions = ""
        if project.description and not project.excluded_features:
            llm_helper = LLMHelper()
            suggestion = llm_helper.generate_suggestions(
                "Based on this project description, suggest 3-5 features that should be excluded from the MVP to keep the scope focused:",
                {"description": project.description, "goals": project.goals}
            )
            ai_suggestions = f"\n\nAI-Suggested Features to Exclude:\n{suggestion}"
        
        return {
            "title": "Scope Reduction",
            "description": f"Let's identify what will NOT be included in the MVP to keep the scope focused.{ai_suggestions}",
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