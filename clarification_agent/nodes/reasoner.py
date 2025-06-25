from typing import Dict, Any
from clarification_agent.nodes.base_node import BaseNodeHandler
from clarification_agent.models.project import Project

class ReasonerNode(BaseNodeHandler):
    """
    Node for reasoning through technology choices and decisions.
    """
    
    def get_ui_data(self, project: Project) -> Dict[str, Any]:
        """Get UI data for the Reasoner node"""
        # Create questions for each technology in the stack
        questions = []
        
        for i, tech in enumerate(project.tech_stack):
            questions.append({
                "id": f"reason_{i}",
                "question": f"Why did you choose {tech}?",
                "type": "text",
                "value": project.decisions.get(tech, "")
            })
        
        # Add a question for additional decisions
        questions.append({
            "id": "additional_decisions",
            "question": "Any other architectural decisions to document? (Format: Decision: Reasoning)",
            "type": "text",
            "value": ""
        })
        
        return {
            "title": "Technology Decision Reasoning",
            "description": "Explain the reasoning behind your technology choices.",
            "questions": questions
        }
    
    def process_responses(self, project: Project, responses: Dict[str, Any]) -> None:
        """Process responses for the Reasoner node"""
        # Process technology reasons
        for i, tech in enumerate(project.tech_stack):
            reason = responses.get(f"reason_{i}", "")
            if reason:
                project.decisions[tech] = reason
        
        # Process additional decisions
        additional = responses.get("additional_decisions", "")
        if additional:
            lines = additional.split("\\n")
            for line in lines:
                if ":" in line:
                    decision, reasoning = line.split(":", 1)
                    project.decisions[decision.strip()] = reasoning.strip()