"""
Conversation-driven Clarification Agent using LangGraph.
"""
import os
import json
import yaml
from typing import Dict, Any, List, Tuple, Optional, TypedDict
from langgraph.graph import StateGraph, END
from clarification_agent.models.project import Project
from clarification_agent.utils.llm_helper import LLMHelper

# Define the state schema
class ConversationState(TypedDict):
    project: Dict[str, Any]
    conversation: List[Dict[str, str]]
    current_perspective: Optional[str]
    awaiting_response: bool
    complete: bool

class ConversationAgent:
    """
    Conversation-driven agent that guides users through project clarification.
    Uses multiple perspectives to ensure comprehensive understanding.
    """
    
    def __init__(self, project_name: str, project_data: Optional[Dict[str, Any]] = None):
        self.project_name = project_name
        self.project = Project(name=project_name)
        self.llm = LLMHelper()
        
        # Initialize project with default empty values
        self.project.description = ""
        self.project.mvp_features = []
        self.project.excluded_features = []
        self.project.tech_stack = []
        self.project.file_map = {}
        self.project.tasks = []
        
        # Load project data if provided
        if project_data:
            self.project.load_from_dict(project_data)
        
        # Initialize conversation history
        self.conversation_history = []
        
        # Define agent roles/perspectives
        self.perspectives = [
            "product_manager",  # Focus on user needs and product features
            "tech_lead",        # Focus on technical feasibility and architecture
            "business_analyst", # Focus on business value and market fit
            "ux_designer",      # Focus on user experience and interface
            "qa_engineer"       # Focus on quality, edge cases, and testing
        ]
        
        # Define conversation stages
        self.stages = [
            "clarify_project",
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
    
    def process_user_input(self, user_input: str, stream: bool = False):
        """
        Process user input and dynamically determine the next conversation step.
        
        Args:
            user_input: The user's input text
            stream: Whether to stream the response
            
        Returns:
            If stream=False: Tuple of (agent response, is_complete)
            If stream=True: Generator that yields chunks of the response, and a boolean indicating completion
        """
        # For the first message (empty input), just return the intro
        if not user_input and not self.conversation_history:
            intro_message = "I'm your AI Clarification Agent. I'll help you define and scope your project. What are you looking to build?"
            self.conversation_history.append({"role": "assistant", "content": intro_message})
            return intro_message, False
        
        # Add user input to conversation
        if user_input:
            self.conversation_history.append({"role": "user", "content": user_input})
        
        # Generate a direct response to the user's input using the LLM
        if stream:
            # For streaming, return a generator that yields chunks
            response_generator = self._generate_dynamic_response(user_input, stream=True)
            
            # Define a wrapper generator that collects the full response
            def process_stream():
                full_response = ""
                for chunk in response_generator:
                    full_response += chunk
                    yield chunk
                
                # After collecting the full response, process it
                is_complete = False
                if "complete" in full_response.lower() or "summary" in full_response.lower() or "finish" in full_response.lower():
                    self.complete = True
                    self._generate_output_files()
                    is_complete = True
                
                # Add the response to conversation history
                self.conversation_history.append({"role": "assistant", "content": full_response})
                
                # Update project data based on the conversation
                self._update_project_from_conversation()
                
                # Return completion status with the last chunk
                return is_complete
            
            return process_stream(), False
        else:
            # For non-streaming, return the full response
            response = self._generate_dynamic_response(user_input)
            
            # Check if we should complete the conversation
            is_complete = False
            if "complete" in response.lower() or "summary" in response.lower() or "finish" in response.lower():
                self.complete = True
                self._generate_output_files()
                summary = self._get_stage_message("summarize")
                self.conversation_history.append({"role": "assistant", "content": summary})
                return summary, True
            
            # Add the response to conversation history
            self.conversation_history.append({"role": "assistant", "content": response})
            
            # Update project data based on the conversation
            self._update_project_from_conversation()
            
            return response, False
        
    def _generate_dynamic_response(self, user_input: str, stream: bool = False):
        """
        Generate a dynamic response to the user's input using the LLM.
        
        Args:
            user_input: The user's latest input
            stream: Whether to stream the response
            
        Returns:
            If stream=False: A response string from the LLM
            If stream=True: A generator that yields chunks of the response
        """
        # Get the current project state
        project_state = {
            "description": self.project.description,
            "mvp_features": self.project.mvp_features,
            "excluded_features": self.project.excluded_features,
            "tech_stack": self.project.tech_stack,
            "file_map": bool(self.project.file_map),
            "tasks": bool(self.project.tasks)
        }
        
        # Build conversation context for the LLM
        conversation_context = []
        for i in range(max(0, len(self.conversation_history) - 4), len(self.conversation_history)):
            msg = self.conversation_history[i]
            conversation_context.append({"role": msg["role"], "content": msg["content"]})
        
        # Use the LLM helper to generate a response
        try:
            # Build a prompt for the LLM
            system_message = (
                "You are an AI assistant helping to clarify project requirements through conversation. "
                "Your goal is to help the user define their project, identify MVP features, exclude unnecessary features, "
                "select appropriate technologies, and plan development tasks. "
                "Respond directly to the user's input and ask relevant follow-up questions based on the conversation context. "
                "Don't follow a rigid script - be conversational and adapt to what the user needs help with. "
                "Stay up-to-date with the latest tech stacks, frameworks, and LLM developments."
            )
            
            # Add project state to system message if we have any information
            if any(project_state.values()):
                system_message += "\n\nCurrent project state:\n"
                if project_state["description"]:
                    system_message += f"- Description: {project_state['description']}\n"
                if project_state["mvp_features"]:
                    system_message += f"- MVP Features: {', '.join(project_state['mvp_features'])}\n"
                if project_state["excluded_features"]:
                    system_message += f"- Excluded Features: {', '.join(project_state['excluded_features'])}\n"
                if project_state["tech_stack"]:
                    system_message += f"- Tech Stack: {', '.join(project_state['tech_stack'])}\n"
                if project_state["file_map"]:
                    system_message += "- File structure has been defined\n"
                if project_state["tasks"]:
                    system_message += "- Development tasks have been defined\n"
            
            # Create messages for the LLM
            messages = [
                {"role": "system", "content": system_message}
            ]
            
            # Add conversation context
            messages.extend(conversation_context)
            
            # Call the LLM with or without streaming
            response = self.llm._call_openrouter(messages, stream=stream)
            
            if response:
                return response
        except Exception as e:
            print(f"Error generating dynamic response: {e}")
        
        # Fallback: Use the stage-based approach if LLM fails
        next_stage = self._determine_next_stage(user_input)
        return self._get_stage_message(next_stage)
        
    def _update_project_from_conversation(self):
        """
        Update project data based on the entire conversation context.
        """
        # Get the last few messages from the conversation
        recent_messages = self.conversation_history[-min(4, len(self.conversation_history)):]
        recent_text = "\n".join([msg["content"] for msg in recent_messages])
        
        # Use the LLM to extract project information
        try:
            # Build a prompt for the LLM
            system_message = "You are an AI assistant helping to extract project information from a conversation."
            
            user_message = "Based on the conversation, extract relevant project information.\n\n"
            user_message += "Conversation:\n"
            user_message += "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in recent_messages])
            
            user_message += "\n\nRespond with a JSON object containing these fields (only if mentioned in the conversation):\n"
            user_message += "- description: Project description\n"
            user_message += "- mvp_features: Array of MVP features\n"
            user_message += "- excluded_features: Array of features to exclude from MVP\n"
            user_message += "- tech_stack: Array of technologies\n"
            
            # Create messages for the LLM
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
            
            # Call the LLM
            response = self.llm._call_openrouter(messages)
            
            if response:
                # Extract JSON from the response if needed
                import json
                import re
                
                json_str = response
                if '```json' in response:
                    json_str = response.split('```json')[1].split('```')[0].strip()
                elif '```' in response:
                    json_str = response.split('```')[1].split('```')[0].strip()
                    
                updates = json.loads(json_str)
                
                # Update project fields
                if 'description' in updates and updates['description'] and not self.project.description:
                    self.project.description = updates['description']
                    
                if 'mvp_features' in updates and updates['mvp_features']:
                    # Handle both array and string formats
                    if isinstance(updates['mvp_features'], list):
                        self.project.mvp_features = updates['mvp_features']
                    elif isinstance(updates['mvp_features'], str):
                        # Parse features from string (one per line)
                        features = [line.strip().lstrip('- ').lstrip('* ').lstrip('1234567890. ') 
                                   for line in updates['mvp_features'].split('\n') 
                                   if line.strip()]
                        self.project.mvp_features = features
                        
                if 'excluded_features' in updates and updates['excluded_features']:
                    # Handle both array and string formats
                    if isinstance(updates['excluded_features'], list):
                        self.project.excluded_features = updates['excluded_features']
                    elif isinstance(updates['excluded_features'], str):
                        # Parse features from string (one per line)
                        features = [line.strip().lstrip('- ').lstrip('* ').lstrip('1234567890. ') 
                                   for line in updates['excluded_features'].split('\n') 
                                   if line.strip()]
                        self.project.excluded_features = features
                        
                if 'tech_stack' in updates and updates['tech_stack']:
                    # Handle both array and string formats
                    if isinstance(updates['tech_stack'], list):
                        self.project.tech_stack = updates['tech_stack']
                    elif isinstance(updates['tech_stack'], str):
                        # Parse tech stack from string (one per line)
                        techs = [line.strip().lstrip('- ').lstrip('* ').lstrip('1234567890. ') 
                                for line in updates['tech_stack'].split('\n') 
                                if line.strip()]
                        self.project.tech_stack = techs
                        
                # Save project state
                self._save_project_data()
                
        except Exception as e:
            print(f"Error updating project from conversation: {e}")
            # Fallback to the old method
            self._update_project_from_input(recent_text)
        
    def _determine_next_stage(self, user_input: str) -> str:
        """
        Use the LLM to determine the next conversation stage based on context.
        
        Args:
            user_input: The user's latest input
            
        Returns:
            The name of the next stage to execute
        """
        # If this is the first user input, it's the project description
        if len(self.conversation_history) <= 2:
            return "product_manager"
            
        # Get the current project state
        project_state = {
            "description": self.project.description,
            "mvp_features": self.project.mvp_features,
            "excluded_features": self.project.excluded_features,
            "tech_stack": self.project.tech_stack,
            "file_map": bool(self.project.file_map),  # Just indicate if we have a file map
            "tasks": bool(self.project.tasks)  # Just indicate if we have tasks
        }
        
        # Build conversation context for the LLM
        conversation_context = []
        for i in range(max(0, len(self.conversation_history) - 4), len(self.conversation_history)):
            msg = self.conversation_history[i]
            conversation_context.append(f"{msg['role'].capitalize()}: {msg['content'][:200]}..." if len(msg['content']) > 200 else f"{msg['role'].capitalize()}: {msg['content']}")
        
        # Define available stages
        available_stages = {
            "product_manager": "Ask about the most important features for the MVP",
            "scope_reduction": "Ask about features to exclude from the MVP",
            "business_analyst": "Ask about target users and market fit",
            "tech_selection": "Ask about technology choices",
            "tech_lead": "Ask about technical constraints and requirements",
            "file_mapping": "Suggest file structure for the project",
            "ux_designer": "Ask about user journeys and workflows",
            "task_planning": "Break down the project into actionable tasks",
            "qa_engineer": "Ask about critical functionality and edge cases",
            "summarize": "Summarize the project and complete the conversation"
        }
        
        # Use the LLM helper to determine the next stage
        try:
            # Build a prompt for the LLM
            system_message = "You are an AI assistant helping to determine the next step in a project clarification conversation."
            
            user_message = "Based on the conversation history and current project state, determine the most appropriate next stage.\n\n"
            user_message += "Current project state:\n"
            for key, value in project_state.items():
                user_message += f"- {key}: {value}\n"
            
            user_message += "\nRecent conversation:\n"
            user_message += "\n".join(conversation_context)
            
            user_message += "\n\nAvailable stages:\n"
            for stage, description in available_stages.items():
                user_message += f"- {stage}: {description}\n"
            
            user_message += "\nRespond with only the name of the next stage to execute."
            
            # Create messages for the LLM
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
            
            # Call the LLM
            response = self.llm._call_openrouter(messages)
            
            if response:
                # Extract just the stage name from the response
                for stage in available_stages.keys():
                    if stage.lower() in response.lower():
                        return stage
            
            # If LLM fails or returns invalid stage, use heuristics
        except Exception as e:
            print(f"Error determining next stage: {e}")
        
        # Fallback: Use heuristics to determine the next stage
        if not self.project.description:
            return "clarify_project"
        elif not self.project.mvp_features:
            return "product_manager"
        elif not self.project.excluded_features:
            return "scope_reduction"
        elif not self.project.tech_stack:
            return "tech_selection"
        elif not self.project.file_map:
            return "file_mapping"
        elif not self.project.tasks:
            return "task_planning"
        else:
            # If we have all the essential information, move to summary
            return "summarize"
    
    def _get_stage_message(self, stage: str) -> str:
        """Get the message for a specific stage"""
        if stage == "clarify_project":
            return (
                "I'm your AI Clarification Agent. I'll help you define and scope your project "
                "by asking questions from different perspectives. Let's start with the basics:\n\n"
                "What is the project you want to build? Please describe it briefly."
            )
        
        elif stage == "product_manager":
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
        
        elif stage == "summarize":
            project_data = self.project.dict()
            project_name = project_data.get('project', 'Project')
            description = project_data.get('description', '')
            
            # Handle MVP features
            mvp_features = project_data.get('mvp_features', [])
            mvp_features_text = "\n".join([f"- {feature}" for feature in mvp_features]) if mvp_features else "- No features specified"
            
            # Handle excluded features
            excluded_features = project_data.get('excluded_features', [])
            excluded_features_text = "\n".join([f"- {feature}" for feature in excluded_features]) if excluded_features else "- None specified"
            
            # Handle tech stack
            tech_stack = project_data.get('tech_stack', [])
            tech_stack_text = "\n".join([f"- {tech}" for tech in tech_stack]) if tech_stack else "- No technologies specified"
            
            summary = (
                f"# Project Summary: {project_name}\n\n"
                f"## Description\n{description}\n\n"
                f"## MVP Features\n{mvp_features_text}\n\n"
                f"## Excluded from MVP\n{excluded_features_text}\n\n"
                f"## Technology Stack\n{tech_stack_text}\n\n"
                f"## Next Steps\n"
                f"1. Review the generated files in the project directory\n"
                f"2. Start implementing the MVP based on the task plan\n"
                f"3. Iterate and refine as you build"
            )
            
            return f"Great! I've completed the project clarification process. Here's a summary:\n\n{summary}\n\nI've generated the necessary files for your project. You can find them in the project directory."
        
        else:
            return "Can you tell me more about your project?"
    
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
            
        elif current_stage == "business_analyst" or "target users" in last_content:
            # Extract target user information
            self.project.target_user = user_input
            
        elif current_stage == "tech_selection" or "technology" in last_content or "technologies" in last_content:
            # Extract tech stack
            techs = [line.strip().lstrip("- ").lstrip("1234567890. ") for line in user_input.split("\n") if line.strip()]
            self.project.tech_stack = techs
            
        elif current_stage == "tech_lead" or "technical" in last_content:
            # Store technical constraints
            self.project.constraints = [line.strip().lstrip("- ").lstrip("1234567890. ") for line in user_input.split("\n") if line.strip()]
            
        elif current_stage == "file_mapping" or "file structure" in last_content:
            # Always generate a file structure regardless of user feedback
            self.project.file_map = self.llm.generate_file_structure(self.project.dict())
                
        elif current_stage == "task_planning" or "tasks" in last_content:
            # Always generate tasks regardless of user feedback
            self.project.tasks = self.llm.generate_tasks(self.project.dict())
    
    def _save_project_data(self) -> None:
        """Save project data to disk"""
        os.makedirs(".clarity", exist_ok=True)
        with open(os.path.join(".clarity", f"{self.project_name}.json"), "w") as f:
            json.dump(self.project.dict(), f, indent=2)
    
    def _generate_output_files(self) -> None:
        """Generate output files based on project data"""
        try:
            # Save project data
            self._save_project_data()
            
            # Generate README.md
            readme_content = (
                f"# {self.project.name}\n\n"
                f"{self.project.description or ''}\n\n"
                f"## Features\n\n"
            )
            
            if self.project.mvp_features:
                for feature in self.project.mvp_features:
                    readme_content += f"- {feature}\n"
            else:
                readme_content += "- No features specified\n"
                
            readme_content += "\n## Tech Stack\n\n"
            
            if self.project.tech_stack:
                for tech in self.project.tech_stack:
                    readme_content += f"- {tech}\n"
            else:
                readme_content += "- No technologies specified\n"
                
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
                ] if self.project.tasks else []
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
            
            if self.project.file_map:
                for file_path, description in self.project.file_map.items():
                    arch_content += f"- `{file_path}`: {description}\n"
            else:
                arch_content += "- No file structure specified\n"
                
            with open("architecture.md", "w") as f:
                f.write(arch_content)
        except Exception as e:
            print(f"Error generating output files: {str(e)}")
            # Create minimal files to avoid errors
            with open("README.md", "w") as f:
                f.write(f"# {self.project.name}\n\nProject documentation\n")
            
            with open(".plan.yml", "w") as f:
                yaml.dump({"plan": []}, f, default_flow_style=False)
            
            with open("architecture.md", "w") as f:
                f.write(f"# {self.project.name} - Architecture\n\nProject architecture documentation\n")