"""
Simple conversation-driven Clarification Agent.
"""
import os
import json
import yaml
from typing import Dict, Any, List, Tuple, Optional
from clarification_agent.models.project import Project
from clarification_agent.utils.llm_helper import LLMHelper

class SimpleConversationAgent:
    """
    Simple conversation-driven agent that guides users through project clarification.
    Uses multiple perspectives to ensure comprehensive understanding.
    """
    
    def __init__(self, project_name: str, project_data: Optional[Dict[str, Any]] = None):
        self.project_name = project_name
        self.project = Project(name=project_name)
        self.llm = LLMHelper()
        
        if project_data:
            self.project.load_from_dict(project_data)
        
        # Initialize conversation history
        self.conversation_history = []
        
        # Define conversation stages
        self.stages = [
            "intro",
            "product_manager",
            "scope_reduction",
            "business_analyst",
            "tech_selection",
            "tech_lead",
            "file_mapping",
            "ux_designer",
            "task_planning",
            "qa_engineer",
            "summarize"
        ]
        
        self.current_stage_index = 0
        self.complete = False
    
    def process_user_input(self, user_input: str) -> Tuple[str, bool]:
        """
        Process user input and advance the conversation.
        
        Args:
            user_input: The user's input text
            
        Returns:
            Tuple of (agent response, is_complete)
        """
        # For the first message (empty input), just return the intro
        if not user_input and not self.conversation_history:
            intro_message = self._get_intro_message()
            self.conversation_history.append({"role": "assistant", "content": intro_message})
            return intro_message, False
        
        # Add user input to conversation
        if user_input:
            self.conversation_history.append({"role": "user", "content": user_input})
            
            # Update project data based on user input
            self._update_project_from_input(user_input)
        
        # Move to the next stage
        self.current_stage_index += 1
        if self.current_stage_index >= len(self.stages):
            self.complete = True
            self._generate_output_files()
            summary = self._get_summary()
            self.conversation_history.append({"role": "assistant", "content": summary})
            return summary, True
        
        # Get the next message for the current stage
        current_stage = self.stages[self.current_stage_index]
        next_message = self._get_stage_message(current_stage)
        
        # Add to conversation history
        self.conversation_history.append({"role": "assistant", "content": next_message})
        
        return next_message, False
    
    def _get_intro_message(self) -> str:
        """Get the introduction message"""
        return (
            "I'm your AI Clarification Agent. I'll help you define and scope your project "
            "by asking questions from different perspectives. Let's start with the basics:\n\n"
            "What is the project you want to build? Please describe it briefly."
        )
    
    def _get_stage_message(self, stage: str) -> str:
        """Get the message for a specific stage"""
        if stage == "product_manager":
            return self.llm.generate_suggestions(
                "Ask about the most important features for the MVP",
                {"perspective": "product_manager", "description": self.project.description}
            )
        
        elif stage == "scope_reduction":
            return (
                "Now let's focus on scope reduction. For an MVP (Minimum Viable Product), "
                "it's important to identify what features are essential and what can be left for later versions.\n\n"
                "What features or capabilities do you think should NOT be included in the initial MVP?"
            )
        
        elif stage == "business_analyst":
            return self.llm.generate_suggestions(
                "Ask about target users and market fit",
                {"perspective": "business_analyst", "description": self.project.description}
            )
        
        elif stage == "tech_selection":
            tech_suggestions = self.llm.generate_suggestions(
                "Suggest appropriate technologies for this project",
                {"description": self.project.description, "mvp_features": self.project.mvp_features}
            )
            
            return (
                "Let's talk about technology choices. Based on your project description, "
                f"here are some suggestions:\n\n{tech_suggestions}\n\n"
                "What technologies would you like to use for this project? Feel free to choose from these suggestions "
                "or specify your own preferences."
            )
        
        elif stage == "tech_lead":
            return self.llm.generate_suggestions(
                "Ask about technical constraints and requirements",
                {"perspective": "tech_lead", "description": self.project.description}
            )
        
        elif stage == "file_mapping":
            file_structure = self.llm.generate_file_structure(self.project.dict())
            file_structure_text = "\n".join([f"- {path}: {desc}" for path, desc in file_structure.items()])
            
            return (
                "Based on your technology choices, here's a suggested file structure for your project:\n\n"
                f"{file_structure_text}\n\n"
                "Does this structure look good to you? Would you like to make any changes or additions?"
            )
        
        elif stage == "ux_designer":
            return self.llm.generate_suggestions(
                "Ask about user journeys and workflows",
                {"perspective": "ux_designer", "description": self.project.description}
            )
        
        elif stage == "task_planning":
            tasks = self.llm.generate_tasks(self.project.dict())
            tasks_text = "\n".join([f"- {task['title']} ({task['estimate']}, priority: {task['priority']})" for task in tasks[:5]])
            
            return (
                "Let's break down the project into actionable tasks. Here are the key tasks I recommend:\n\n"
                f"{tasks_text}\n\n"
                "Do these tasks cover the essential work needed for your MVP? Would you like to add or modify any tasks?"
            )
        
        elif stage == "qa_engineer":
            return self.llm.generate_suggestions(
                "Ask about critical functionality and edge cases",
                {"perspective": "qa_engineer", "description": self.project.description}
            )
        
        else:
            return "Can you tell me more about your project?"
    
    def _get_summary(self) -> str:
        """Generate a summary of the project"""
        project_data = self.project.dict()
        
        summary = (
            f"# Project Summary: {project_data['project']}\n\n"
            f"## Description\n{project_data.get('description', '')}\n\n"
            f"## MVP Features\n" + "\n".join([f"- {feature}" for feature in project_data.get('mvp_features', [])]) + "\n\n"
            f"## Excluded from MVP\n" + "\n".join([f"- {feature}" for feature in project_data.get('excluded_features', [])]) + "\n\n"
            f"## Technology Stack\n" + "\n".join([f"- {tech}" for tech in project_data.get('tech_stack', [])]) + "\n\n"
            f"## Next Steps\n"
            f"1. Review the generated files in the project directory\n"
            f"2. Start implementing the MVP based on the task plan\n"
            f"3. Iterate and refine as you build"
        )
        
        return f"Great! I've completed the project clarification process. Here's a summary:\n\n{summary}\n\nI've generated the necessary files for your project. You can find them in the project directory."
    
    def _update_project_from_input(self, user_input: str) -> None:
        """Update project data based on user input"""
        # Get the current conversation context
        if not self.conversation_history or len(self.conversation_history) < 2:
            # First user input - this is the project description
            self.project.description = user_input
            return
        
        # Get the last agent message to understand context
        last_agent_message = None
        for message in reversed(self.conversation_history[:-1]):  # Skip the user's message we just added
            if message["role"] != "user":
                last_agent_message = message
                break
        
        if not last_agent_message:
            return
            
        # Extract information based on context
        last_content = last_agent_message["content"].lower()
        current_stage = self.stages[self.current_stage_index] if self.current_stage_index < len(self.stages) else ""
        
        # Update project based on context
        if current_stage == "product_manager" or "features" in last_content and "mvp" in last_content:
            # Extract MVP features
            features = [line.strip().lstrip("- ").lstrip("1234567890. ") for line in user_input.split("\n") if line.strip()]
            self.project.mvp_features = features
            
        elif current_stage == "scope_reduction" or "not be included" in last_content:
            # Extract excluded features
            excluded = [line.strip().lstrip("- ").lstrip("1234567890. ") for line in user_input.split("\n") if line.strip()]
            self.project.excluded_features = excluded
            
        elif current_stage == "tech_selection" or "technology" in last_content or "technologies" in last_content:
            # Extract tech stack
            techs = [line.strip().lstrip("- ").lstrip("1234567890. ") for line in user_input.split("\n") if line.strip()]
            self.project.tech_stack = techs
            
        elif current_stage == "file_mapping" or "file structure" in last_content:
            # Extract file structure feedback
            if "yes" in user_input.lower() or "good" in user_input.lower() or "looks good" in user_input.lower():
                # User accepted the suggested structure
                self.project.file_map = self.llm.generate_file_structure(self.project.dict())
            else:
                # User provided custom structure or feedback
                # For simplicity, we'll just store this as a note
                self.project.file_map = self.llm.generate_file_structure(self.project.dict())
                
        elif current_stage == "task_planning" or "tasks" in last_content:
            # Extract task feedback
            if "yes" in user_input.lower() or "good" in user_input.lower() or "cover" in user_input.lower():
                # User accepted the suggested tasks
                self.project.tasks = self.llm.generate_tasks(self.project.dict())
            else:
                # User provided custom tasks or feedback
                # For simplicity, we'll just store this as a note
                self.project.tasks = self.llm.generate_tasks(self.project.dict())
    
    def _save_project_data(self) -> None:
        """Save project data to disk"""
        os.makedirs(".clarity", exist_ok=True)
        with open(os.path.join(".clarity", f"{self.project_name}.json"), "w") as f:
            json.dump(self.project.dict(), f, indent=2)
    
    def _generate_output_files(self) -> None:
        """Generate output files based on project data"""
        # Save project data
        self._save_project_data()
        
        # Generate README.md
        readme_content = (
            f"# {self.project.name}\n\n"
            f"{self.project.description or ''}\n\n"
            f"## Features\n\n"
        )
        
        for feature in self.project.mvp_features:
            readme_content += f"- {feature}\n"
            
        readme_content += "\n## Tech Stack\n\n"
        
        for tech in self.project.tech_stack:
            readme_content += f"- {tech}\n"
            
        with open("README.md", "w") as f:
            f.write(readme_content)
            
        # Generate .plan.yml
        plan_data = {
            "plan": [
                {
                    "title": task.get("title", ""),
                    "file": task.get("file", ""),
                    "estimate": task.get("estimate", ""),
                    "priority": task.get("priority", 1)
                }
                for task in self.project.tasks
            ]
        }
        
        with open(".plan.yml", "w") as f:
            yaml.dump(plan_data, f, default_flow_style=False)
            
        # Generate architecture.md
        arch_content = (
            f"# {self.project.name} - Architecture\n\n"
            f"## Overview\n\n"
            f"{self.project.description or ''}\n\n"
            f"## File Structure\n\n"
        )
        
        for file_path, description in self.project.file_map.items():
            arch_content += f"- `{file_path}`: {description}\n"
            
        with open("architecture.md", "w") as f:
            f.write(arch_content)