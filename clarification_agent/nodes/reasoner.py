from typing import Dict, Any
from clarification_agent.nodes.base_node import BaseNodeHandler
from clarification_agent.models.project import Project
from clarification_agent.utils.llm_helper import LLMHelper

class ReasonerNode(BaseNodeHandler):
    """
    Node for reasoning through technology choices and decisions.
    """
    
    def get_ui_data(self, project: Project) -> Dict[str, Any]:
        """Get UI data for the Reasoner node"""
        # Create questions for each technology in the stack
        questions = []
        
        # Generate AI suggestions for technology reasoning
        llm_helper = LLMHelper()
        ai_suggestions = ""
        
        for i, tech in enumerate(project.tech_stack):
            # Get AI-suggested reasoning if not already provided
            suggested_reason = ""
            if not project.decisions.get(tech):
                suggested_reason = llm_helper.generate_suggestions(
                    f"Explain why {tech} would be a good choice for this project:",
                    {"tech": tech, "mvp_features": project.mvp_features, "description": project.description}
                )
                # Extract just the first paragraph for brevity
                if suggested_reason:
                    suggested_reason = suggested_reason.split("\n\n")[0]
                    ai_suggestions += f"\n\n{tech}: {suggested_reason}"
            
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
        
        description = "Explain the reasoning behind your technology choices."
        if ai_suggestions:
            description += f"\n\nAI-Suggested Reasoning:{ai_suggestions}"
        
        return {
            "title": "Technology Decision Reasoning",
            "description": description,
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