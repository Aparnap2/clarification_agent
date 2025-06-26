from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

class Project(BaseModel):
    """
    Project data model that stores all information gathered during the clarification process.
    """
    name: str
    goals: List[str] = Field(default_factory=list)
    mvp_features: List[str] = Field(default_factory=list)
    excluded_features: List[str] = Field(default_factory=list)
    target_user: str = ""
    tech_stack: List[str] = Field(default_factory=list)
    decisions: Dict[str, str] = Field(default_factory=dict)
    file_map: Dict[str, str] = Field(default_factory=dict)
    tasks: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Additional fields for project context
    description: str = ""
    purpose: str = ""
    constraints: List[str] = Field(default_factory=list)
    
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "project": self.name,
            "goals": self.goals,
            "mvp_features": self.mvp_features,
            "excluded_features": self.excluded_features,
            "target_user": self.target_user,
            "tech_stack": self.tech_stack,
            "decisions": self.decisions,
            "file_map": self.file_map,
            "tasks": self.tasks,
            "description": self.description,
            "purpose": self.purpose,
            "constraints": self.constraints
        }
    
    def load_from_dict(self, data: Dict[str, Any]):
        """Load project data from a dictionary"""
        self.name = data.get("project", self.name)
        self.goals = data.get("goals", [])
        self.mvp_features = data.get("mvp_features", [])
        self.excluded_features = data.get("excluded_features", [])
        self.target_user = data.get("target_user", "")
        self.tech_stack = data.get("tech_stack", [])
        self.decisions = data.get("decisions", {})
        self.file_map = data.get("file_map", {})
        self.tasks = data.get("tasks", [])
        self.description = data.get("description", "")
        self.purpose = data.get("purpose", "")
        self.constraints = data.get("constraints", [])