from typing import Dict, Any, List
from clarification_agent.nodes.base_node import BaseNode
from clarification_agent.models.project import Project
from clarification_agent.utils.llm_helper import LLMHelper

class DynamicNode(BaseNode):
    """
    A dynamic node that uses LLM to generate questions based on project state.
    This allows for more flexible conversation flow.
    """
    
    def __init__(self, node_type: str):
        """
        Initialize the dynamic node with a specific type.
        
        Args:
            node_type: The type of node (e.g., "clarify_intent", "tech_selection")
        """
        self.node_type = node_type
        self.llm = LLMHelper()
        
    def get_ui_data(self, project: Project) -> Dict[str, Any]:
        """
        Generate UI data dynamically based on project state.
        
        Args:
            project: The current project state
            
        Returns:
            Dictionary with UI elements
        """
        # Get project state as dictionary
        project_state = project.dict()
        
        # Build a prompt for the LLM
        system_message = "You are an AI assistant helping to generate questions for a project clarification workflow."
        
        user_message = f"Generate questions for the '{self.node_type}' stage of project clarification.\\n\\n"
        user_message += "Current project state:\\n"
        user_message += f"- Name: {project_state.get('name', 'Not provided')}\\n"
        user_message += f"- Description: {project_state.get('description', 'Not provided')}\\n"
        user_message += f"- MVP Features: {project_state.get('mvp_features', [])}\\n"
        user_message += f"- Excluded Features: {project_state.get('excluded_features', [])}\\n"
        user_message += f"- Tech Stack: {project_state.get('tech_stack', [])}\\n"
        
        user_message += "\\nRespond with a JSON object containing 'title', 'description', and 'questions' array. Each question should have 'id', 'question', 'type', and 'required' fields."
        
        # Create messages for the LLM
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        # Call the LLM
        response = self.llm._call_openrouter(messages)
        
        # Parse the response or use fallback
        try:
            if response:
                # Extract JSON from the response if needed
                import json
                import re
                
                json_str = response
                if '```json' in response:
                    json_str = response.split('```json')[1].split('```')[0].strip()
                elif '```' in response:
                    json_str = response.split('```')[1].split('```')[0].strip()
                    
                ui_data = json.loads(json_str)
                
                # Ensure required fields are present
                if 'title' not in ui_data:
                    ui_data['title'] = self.node_type.replace('_', ' ').title()
                if 'description' not in ui_data:
                    ui_data['description'] = f"Please provide information about {self.node_type.replace('_', ' ')}."
                if 'questions' not in ui_data:
                    ui_data['questions'] = []
                    
                return ui_data
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
        
        # Fallback UI data
        return {
            "title": self.node_type.replace('_', ' ').title(),
            "description": f"Please provide information about {self.node_type.replace('_', ' ')}.",
            "questions": [
                {
                    "id": "dynamic_input",
                    "question": f"What are your thoughts on {self.node_type.replace('_', ' ')}?",
                    "type": "text",
                    "required": True
                }
            ]
        }
        
    def process_responses(self, project: Project, responses: Dict[str, Any]) -> None:
        """
        Process user responses and update the project state.
        
        Args:
            project: The project to update
            responses: User responses to questions
        """
        # Build a prompt for the LLM to process responses
        system_message = "You are an AI assistant helping to update project state based on user responses."
        
        user_message = f"Process user responses for the '{self.node_type}' stage and extract relevant information to update the project state.\\n\\n"
        user_message += "Current project state:\\n"
        project_state = project.dict()
        user_message += f"- Name: {project_state.get('name', 'Not provided')}\\n"
        user_message += f"- Description: {project_state.get('description', 'Not provided')}\\n"
        user_message += f"- MVP Features: {project_state.get('mvp_features', [])}\\n"
        user_message += f"- Excluded Features: {project_state.get('excluded_features', [])}\\n"
        user_message += f"- Tech Stack: {project_state.get('tech_stack', [])}\\n"
        
        user_message += "\\nUser responses:\\n"
        for key, value in responses.items():
            user_message += f"- {key}: {value}\\n"
            
        user_message += "\\nRespond with a JSON object containing updated project fields. Only include fields that should be updated."
        
        # Create messages for the LLM
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        # Call the LLM
        response = self.llm._call_openrouter(messages)
        
        # Parse the response and update project
        try:
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
                if 'description' in updates and updates['description']:
                    project.description = updates['description']
                    
                if 'mvp_features' in updates and updates['mvp_features']:
                    # Handle both array and string formats
                    if isinstance(updates['mvp_features'], list):
                        project.mvp_features = updates['mvp_features']
                    elif isinstance(updates['mvp_features'], str):
                        # Parse features from string (one per line)
                        features = [line.strip().lstrip('- ').lstrip('* ').lstrip('1234567890. ') 
                                   for line in updates['mvp_features'].split('\\n') 
                                   if line.strip()]
                        project.mvp_features = features
                        
                if 'excluded_features' in updates and updates['excluded_features']:
                    # Handle both array and string formats
                    if isinstance(updates['excluded_features'], list):
                        project.excluded_features = updates['excluded_features']
                    elif isinstance(updates['excluded_features'], str):
                        # Parse features from string (one per line)
                        features = [line.strip().lstrip('- ').lstrip('* ').lstrip('1234567890. ') 
                                   for line in updates['excluded_features'].split('\\n') 
                                   if line.strip()]
                        project.excluded_features = features
                        
                if 'tech_stack' in updates and updates['tech_stack']:
                    # Handle both array and string formats
                    if isinstance(updates['tech_stack'], list):
                        project.tech_stack = updates['tech_stack']
                    elif isinstance(updates['tech_stack'], str):
                        # Parse tech stack from string (one per line)
                        techs = [line.strip().lstrip('- ').lstrip('* ').lstrip('1234567890. ') 
                                for line in updates['tech_stack'].split('\\n') 
                                if line.strip()]
                        project.tech_stack = techs
                
                return
        except Exception as e:
            print(f"Error processing responses with LLM: {e}")
        
        # Fallback: Basic processing of responses
        for key, value in responses.items():
            if key == "dynamic_input" and value:
                # Try to determine what kind of input this is based on the node type
                if self.node_type == "clarify_intent":
                    project.description = value
                elif self.node_type == "mvp_scoper" or "feature" in self.node_type.lower():
                    # Parse features from text (one per line)
                    features = [line.strip().lstrip('- ').lstrip('* ').lstrip('1234567890. ') 
                               for line in value.split('\n') 
                               if line.strip()]
                    project.mvp_features = features
                elif "exclude" in self.node_type.lower():
                    # Parse excluded features from text (one per line)
                    features = [line.strip().lstrip('- ').lstrip('* ').lstrip('1234567890. ') 
                               for line in value.split('\n') 
                               if line.strip()]
                    project.excluded_features = features
                elif "tech" in self.node_type.lower() or "stack" in self.node_type.lower():
                    # Parse tech stack from text (one per line)
                    techs = [line.strip().lstrip('- ').lstrip('* ').lstrip('1234567890. ') 
                            for line in value.split('\n') 
                            if line.strip()]
                    project.tech_stack = techs