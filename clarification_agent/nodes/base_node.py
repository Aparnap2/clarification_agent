from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseNode(ABC):
    """Base class for all nodes in the LangGraph agent."""

    @abstractmethod
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the node's logic.

        Args:
            state: The current state of the conversation graph.

        Returns:
            An updated state dictionary.
        """
        pass

class BaseNodeHandler(BaseNode):
    """
    Abstract base class for all node handlers in the Clarification Agent.
    Provides the interface for UI data and response processing.
    """

    @abstractmethod
    def get_ui_data(self, project) -> Dict[str, Any]:
        """
        Returns UI data for the node.
        """
        pass

    @abstractmethod
    def process_responses(self, project, responses: Dict[str, Any]) -> None:
        """
        Processes user responses and updates the project.
        """
        pass