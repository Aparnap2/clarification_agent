"""
Node configuration loader and manager.
Provides dynamic node configuration from YAML files.
"""
import yaml
import os
from typing import Dict, Any, List, Optional
from pathlib import Path


class NodeConfigManager:
    """Manages node configurations loaded from YAML files."""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = Path(__file__).parent / "nodes.yaml"
        
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Node configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in configuration file: {e}")
    
    def get_node_config(self, node_id: str) -> Dict[str, Any]:
        """Get configuration for a specific node."""
        if node_id not in self.config["nodes"]:
            raise ValueError(f"Node '{node_id}' not found in configuration")
        return self.config["nodes"][node_id]
    
    def get_all_nodes(self) -> Dict[str, Dict[str, Any]]:
        """Get all node configurations."""
        return self.config["nodes"]
    
    def get_workflow_config(self) -> Dict[str, Any]:
        """Get workflow-level configuration."""
        return self.config.get("workflow", {})
    
    def get_node_order(self) -> List[str]:
        """Get the order of nodes in the workflow."""
        nodes = self.config["nodes"]
        ordered_nodes = []
        
        # Start with the start node
        current = self.get_workflow_config().get("start_node", "start")
        visited = set()
        
        while current and current not in visited:
            ordered_nodes.append(current)
            visited.add(current)
            
            # Get next node from default transition
            node_config = nodes.get(current, {})
            transitions = node_config.get("transitions", {})
            current = transitions.get("default")
            
            # Break if we reach the end
            if current == "complete" or current is None:
                break
        
        return ordered_nodes
    
    def get_next_node(self, current_node: str, transition_type: str = "default") -> Optional[str]:
        """Get the next node based on transition type."""
        node_config = self.get_node_config(current_node)
        transitions = node_config.get("transitions", {})
        return transitions.get(transition_type)
    
    def is_node_optional(self, node_id: str) -> bool:
        """Check if a node is optional."""
        node_config = self.get_node_config(node_id)
        return node_config.get("optional", False)
    
    def can_retry_node(self, node_id: str) -> bool:
        """Check if a node can be retried."""
        node_config = self.get_node_config(node_id)
        return node_config.get("retry", False)
    
    def can_skip_node(self, node_id: str) -> bool:
        """Check if a node can be skipped."""
        node_config = self.get_node_config(node_id)
        return node_config.get("skip", False)
    
    def get_parallel_nodes(self, node_id: str) -> List[str]:
        """Get parallel nodes for a given node."""
        node_config = self.get_node_config(node_id)
        return node_config.get("parallel_nodes", [])
    
    def should_enable_web_search(self, node_id: str) -> bool:
        """Check if web search should be enabled for this node."""
        node_config = self.get_node_config(node_id)
        return node_config.get("web_search", False)
    
    def get_search_query_template(self, node_id: str) -> Optional[str]:
        """Get search query template for a node."""
        node_config = self.get_node_config(node_id)
        return node_config.get("search_query")
    
    def reload_config(self):
        """Reload configuration from file."""
        self.config = self._load_config()


# Global instance for easy access
_config_manager = None

def get_node_config_manager() -> NodeConfigManager:
    """Get the global node configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = NodeConfigManager()
    return _config_manager