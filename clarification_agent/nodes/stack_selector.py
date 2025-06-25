from typing import Dict, Any
from clarification_agent.nodes.base_node import BaseNodeHandler
from clarification_agent.models.project import Project

class StackSelectorNode(BaseNodeHandler):
    """
    Node for selecting the technology stack.
    """
    
    def get_ui_data(self, project: Project) -> Dict[str, Any]:
        """Get UI data for the StackSelector node"""
        # Common technology options
        frontend_options = ["React", "Vue", "Angular", "Next.js", "Svelte", "HTML/CSS/JS", "Other"]
        backend_options = ["Node.js", "Python/Flask", "Python/FastAPI", "Python/Django", "Java/Spring", "Go", "Ruby on Rails", "PHP", "Other"]
        database_options = ["PostgreSQL", "MySQL", "MongoDB", "SQLite", "Firebase", "DynamoDB", "Supabase", "Other"]
        ai_options = ["OpenAI API", "Hugging Face", "LangChain", "LangGraph", "TensorFlow", "PyTorch", "Other"]
        
        return {
            "title": "Technology Stack Selection",
            "description": "Select the technologies you plan to use for this project.",
            "questions": [
                {
                    "id": "frontend",
                    "question": "Frontend Technology",
                    "type": "select",
                    "options": frontend_options,
                    "value": next((tech for tech in project.tech_stack if tech in frontend_options), None)
                },
                {
                    "id": "backend",
                    "question": "Backend Technology",
                    "type": "select",
                    "options": backend_options,
                    "value": next((tech for tech in project.tech_stack if tech in backend_options), None)
                },
                {
                    "id": "database",
                    "question": "Database Technology",
                    "type": "select",
                    "options": database_options,
                    "value": next((tech for tech in project.tech_stack if tech in database_options), None)
                },
                {
                    "id": "ai_ml",
                    "question": "AI/ML Technologies (if applicable)",
                    "type": "multiselect",
                    "options": ai_options,
                    "value": [tech for tech in project.tech_stack if tech in ai_options]
                },
                {
                    "id": "other_tech",
                    "question": "Other Technologies (comma separated)",
                    "type": "text",
                    "value": ""
                }
            ]
        }
    
    def process_responses(self, project: Project, responses: Dict[str, Any]) -> None:
        """Process responses for the StackSelector node"""
        # Clear existing tech stack
        project.tech_stack = []
        
        # Add selected technologies
        for key in ["frontend", "backend", "database"]:
            if responses.get(key) and responses[key] != "Other":
                project.tech_stack.append(responses[key])
        
        # Add AI/ML technologies
        if responses.get("ai_ml"):
            for tech in responses["ai_ml"]:
                if tech != "Other":
                    project.tech_stack.append(tech)
        
        # Add other technologies
        if responses.get("other_tech"):
            other_techs = [tech.strip() for tech in responses["other_tech"].split(",") if tech.strip()]
            project.tech_stack.extend(other_techs)