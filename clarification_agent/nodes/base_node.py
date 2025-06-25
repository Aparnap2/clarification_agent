from abc import ABC, abstractmethod
from typing import Dict, Any
from clarification_agent.models.project import Project

class BaseNodeHandler(ABC):
    """
    Base class for all node handlers in the workflow.
    """
    
    @abstractmethod
    def get_ui_data(self, project: Project) -> Dict[str, Any]:
        """
        Get the UI data for this node.
        
        Args:
            project: The current project state
            
        Returns:
            Dictionary with UI elements like title, description, questions
        """
        pass
    
    @abstractmethod
    def process_responses(self, project: Project, responses: Dict[str, Any]) -> None:
        """
        Process the user responses for this node.
        
        Args:
            project: The current project state
            responses: User responses to the questions
        """
        pass