from typing import Dict, Any
from clarification_agent.nodes.base_node import BaseNodeHandler
from clarification_agent.models.project import Project
from clarification_agent.utils.llm_helper import LLMHelper

class ClarifyIntentNode(BaseNodeHandler):
    """
    Node for clarifying the project intent and goals.
    """
    
    def get_ui_data(self, project: Project) -> Dict[str, Any]:
        """Get UI data for the ClarifyIntent node"""
        # Generate AI suggestions if we have some initial description
        ai_suggestions = ""
        if project.description and not project.goals:
            llm_helper = LLMHelper()
            suggestion = llm_helper.generate_suggestions(
                "Based on this project description, suggest 3-5 clear project goals:",
                {"description": project.description}
            )
            ai_suggestions = f"\n\nAI Suggestions:\n{suggestion}"
        
        return {
            "title": "Clarify Project Intent",
            "description": f"Let's understand what this project is about.{ai_suggestions}",
            "questions": [
                {
                    "id": "description",
                    "question": "What is this project?",
                    "type": "text",
                    "value": project.description or ""
                },
                {
                    "id": "purpose",
                    "question": "Who's it for and what's the expected result?",
                    "type": "text",
                    "value": project.purpose or ""
                },
                {
                    "id": "goals",
                    "question": "What are the main goals of this project? (One per line)",
                    "type": "text",
                    "value": "\\n".join(project.goals) if project.goals else ""
                }
            ]
        }
    
    def process_responses(self, project: Project, responses: Dict[str, Any]) -> None:
        """Process responses for the ClarifyIntent node"""
        project.description = responses.get("description", "")
        project.purpose = responses.get("purpose", "")
        
        # Process goals (split by newlines)
        goals_text = responses.get("goals", "")
        project.goals = [goal.strip() for goal in goals_text.split("\\n") if goal.strip()]