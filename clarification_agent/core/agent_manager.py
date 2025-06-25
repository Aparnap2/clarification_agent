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
        
        # For MVP, we'll use a simple linear flow
        workflow = {"current_node": "Start", "transitions": {
            "Start": "ClarifyIntent",
            "ClarifyIntent": "NotBuilder",
            "NotBuilder": "MVPScoper",
            "MVPScoper": "StackSelector",
            "StackSelector": "Reasoner",
            "Reasoner": "FileMapBuilder",
            "FileMapBuilder": "TaskPlanner",
            "TaskPlanner": "Exporter",
            "Exporter": "End"
        }}
        
        return workflow
    
    def process_node(self, node_name: str) -> Dict[str, Any]:
        """Process the current node and return UI information"""
        node_handler = get_node_handler(node_name)
        if node_handler:
            return node_handler.get_ui_data(self.project)
        return {"title": node_name, "description": "Node handler not implemented yet."}
    
    def submit_responses(self, node_name: str, responses: Dict[str, Any]) -> str:
        """Process user responses and determine the next node"""
        node_handler = get_node_handler(node_name)
        if node_handler:
            node_handler.process_responses(self.project, responses)
            
            # Save project state
            self._save_project_state()
            
            # Update current state
            next_node = self.workflow["transitions"].get(node_name, "End")
            self.current_state["node"] = next_node
            self.current_state["project"] = self.project.dict()
            
            return next_node
        return node_name
    
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