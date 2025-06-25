from typing import Dict, Any
from clarification_agent.nodes.base_node import BaseNodeHandler
from clarification_agent.models.project import Project

class ClarifyIntentNode(BaseNodeHandler):
    """
    Node for clarifying the project intent and goals.
    """
    
    def get_ui_data(self, project: Project) -> Dict[str, Any]:
        """Get UI data for the ClarifyIntent node"""
        return {
            "title": "Clarify Project Intent",
            "description": "Let's understand what this project is about.",
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