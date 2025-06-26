import os
import json
import yaml
from typing import Dict, Any, Optional, List
from langgraph.graph import StateGraph
from clarification_agent.models.project import Project
from clarification_agent.nodes.node_factory import get_node_handler
from clarification_agent.output.exporter import Exporter

class ClarificationAgentManager:
    """
    Main manager class for the Clarification Agent.
    Handles the workflow, state management, and node transitions.
    """
    
    def __init__(self, project_name: str, project_data: Optional[Dict[str, Any]] = None):
        self.project_name = project_name
        self.project = Project(name=project_name)
        
        if project_data:
            self.project.load_from_dict(project_data)
        
        self.workflow = self._build_workflow()
        self.current_state = {"node": "Start", "project": self.project.dict()}
        self.exporter = Exporter(self.project)
        
        # Define the workflow nodes and their order
        self.nodes = [
            "Start",
            "ClarifyIntent",
            "NotBuilder",
            "MVPScoper",
            "StackSelector",
            "Reasoner",
            "FileMapBuilder",
            "TaskPlanner",
            "Exporter"
        ]
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        # This is a simplified version without actual LangGraph implementation
        # In a real implementation, this would create the full StateGraph
        
        # Define all possible transitions between nodes
        workflow = {"current_node": "Start", "transitions": {
            "Start": self._determine_next_node("Start"),
            "ClarifyIntent": self._determine_next_node("ClarifyIntent"),
            "NotBuilder": self._determine_next_node("NotBuilder"),
            "MVPScoper": self._determine_next_node("MVPScoper"),
            "StackSelector": self._determine_next_node("StackSelector"),
            "Reasoner": self._determine_next_node("Reasoner"),
            "FileMapBuilder": self._determine_next_node("FileMapBuilder"),
            "TaskPlanner": self._determine_next_node("TaskPlanner"),
            "Exporter": "End"
        }}
        
        return workflow
        
    def _determine_next_node(self, current_node: str) -> str:
        """Dynamically determine the next node based on project state and context"""
        # Define all available nodes
        available_nodes = [
            "ClarifyIntent",
            "NotBuilder",
            "MVPScoper",
            "StackSelector",
            "Reasoner",
            "FileMapBuilder",
            "TaskPlanner",
            "Exporter"
        ]
        
        # For now, use a simple heuristic based on project state
        # In a full implementation, this would use an LLM to determine the next node
        
        if current_node == "Start":
            return "ClarifyIntent"
            
        # Get current index and return next node in sequence
        try:
            current_index = self.nodes.index(current_node)
            next_index = current_index + 1
            if next_index < len(self.nodes):
                return self.nodes[next_index]
            else:
                return "End"
        except ValueError:
            # If node not found in sequence, default to ClarifyIntent
            return "ClarifyIntent"
    
    def process_node(self, node_name: str) -> Dict[str, Any]:
        """Process the current node and return UI information"""
        node_handler = get_node_handler(node_name)
        if node_handler:
            return node_handler.get_ui_data(self.project)
        return {"title": node_name, "description": "Node handler not implemented yet."}
    
    def submit_responses(self, node_name: str, responses: Dict[str, Any]) -> str:
        """Process user responses and dynamically determine the next node"""
        node_handler = get_node_handler(node_name)
        if node_handler:
            node_handler.process_responses(self.project, responses)
            
            # Save project state
            self._save_project_state()
            
            # Dynamically determine the next node based on project state and responses
            next_node = self._determine_next_node_with_llm(node_name, responses)
            
            # Update current state
            self.current_state["node"] = next_node
            self.current_state["project"] = self.project.dict()
            
            return next_node
        return node_name
        
    def _determine_next_node_with_llm(self, current_node: str, responses: Dict[str, Any]) -> str:
        """Use LLM to determine the next node based on project state and user responses"""
        # For now, we'll use the predefined transitions as a fallback
        fallback_next_node = self.workflow["transitions"].get(current_node, "End")
        
        # In a full implementation, this would use an LLM to analyze the project state and responses
        # to determine the most appropriate next node
        
        # Get project state summary
        project_state = self.project.dict()
        
        # Create an LLM helper
        try:
            from clarification_agent.utils.llm_helper import LLMHelper
            llm = LLMHelper()
            
            # Build a prompt for the LLM
            system_message = "You are an AI assistant helping to determine the next step in a project clarification workflow."
            
            user_message = "Based on the current project state and user responses, determine the most appropriate next node.\n\n"
            user_message += f"Current node: {current_node}\n\n"
            user_message += "Project state summary:\n"
            user_message += f"- Description: {project_state.get('description', 'Not provided')}\n"
            user_message += f"- MVP Features: {len(project_state.get('mvp_features', []))} defined\n"
            user_message += f"- Excluded Features: {len(project_state.get('excluded_features', []))} defined\n"
            user_message += f"- Tech Stack: {len(project_state.get('tech_stack', []))} technologies defined\n"
            user_message += f"- File Map: {'Defined' if project_state.get('file_map') else 'Not defined'}\n"
            user_message += f"- Tasks: {'Defined' if project_state.get('tasks') else 'Not defined'}\n\n"
            
            user_message += "User responses to current node:\n"
            for key, value in responses.items():
                user_message += f"- {key}: {value}\n"
            
            user_message += "\nAvailable nodes:\n"
            for node in self.nodes:
                user_message += f"- {node}\n"
            
            user_message += "\nRespond with only the name of the next node to execute."
            
            # Create messages for the LLM
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
            
            # Call the LLM
            response = llm._call_openrouter(messages)
            
            if response:
                # Extract just the node name from the response
                for node in self.nodes:
                    if node in response:
                        return node
        except Exception as e:
            print(f"Error determining next node with LLM: {e}")
        
        # If LLM fails or returns invalid node, use the fallback
        return fallback_next_node
    
    def _save_project_state(self):
        """Save the current project state to disk"""
        os.makedirs(".clarity", exist_ok=True)
        with open(os.path.join(".clarity", f"{self.project_name}.json"), "w") as f:
            json.dump(self.project.dict(), f, indent=2)
    
    def get_progress(self) -> Dict[str, Any]:
        """Get the current progress through the workflow"""
        if self.current_state["node"] == "End":
            return {"percentage": 1.0, "completed": len(self.nodes), "total": len(self.nodes)}
        
        try:
            current_index = self.nodes.index(self.current_state["node"])
            return {
                "percentage": current_index / (len(self.nodes) - 1),
                "completed": current_index,
                "total": len(self.nodes) - 1  # Exclude End
            }
        except ValueError:
            return {"percentage": 0.0, "completed": 0, "total": len(self.nodes) - 1}
    
    def export_all(self):
        """Export all project files"""
        self.exporter.export_all()