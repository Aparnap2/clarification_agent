from typing import Dict, Any
from clarification_agent.nodes.base_node import BaseNodeHandler
from clarification_agent.models.project import Project
from clarification_agent.utils.llm_helper import LLMHelper

class FileMapBuilderNode(BaseNodeHandler):
    """
    Node for mapping features to file structure.
    """
    
    def get_ui_data(self, project: Project) -> Dict[str, Any]:
        """Get UI data for the FileMapBuilder node"""
        # Generate suggested file structure based on tech stack
        suggested_structure = self._generate_suggested_structure(project)
        
        return {
            "title": "File Structure Mapping",
            "description": "Map your features to a file structure. Each line should be in the format: path/to/file.ext: Description",
            "questions": [
                {
                    "id": "file_map",
                    "question": "File Structure (suggested structure below):",
                    "type": "text",
                    "value": suggested_structure + "\\n" + "\\n".join([f"{path}: {desc}" for path, desc in project.file_map.items()])
                }
            ]
        }
    
    def process_responses(self, project: Project, responses: Dict[str, Any]) -> None:
        """Process responses for the FileMapBuilder node"""
        # Clear existing file map
        project.file_map = {}
        
        # Process file map
        file_map_text = responses.get("file_map", "")
        lines = file_map_text.split("\\n")
        
        for line in lines:
            if ":" in line:
                file_path, description = line.split(":", 1)
                file_path = file_path.strip()
                description = description.strip()
                
                if file_path and description and not file_path.startswith("#"):
                    project.file_map[file_path] = description
    
    def _generate_suggested_structure(self, project: Project) -> str:
        """Generate a suggested file structure based on the tech stack using AI"""
        structure = "# AI-suggested structure (edit as needed):\\n"
        
        # Use AI to generate file structure
        llm_helper = LLMHelper()
        ai_structure = llm_helper.generate_file_structure(project.dict())
        
        # Convert AI structure to the expected format
        for file_path, description in ai_structure.items():
            structure += f"{file_path}: {description}\\n"
        
        # Add common files if AI didn't provide them
        if not any("README.md" in path for path in ai_structure.keys()):
            structure += "README.md: Project documentation\\n"
        
        if "Python" in str(project.tech_stack) and not any("requirements.txt" in path for path in ai_structure.keys()):
            structure += "requirements.txt: Python dependencies\\n"
            
        if any(js_tech in str(project.tech_stack) for js_tech in ["React", "Vue", "Angular", "Next.js", "Node.js"]) and not any("package.json" in path for path in ai_structure.keys()):
            structure += "package.json: Node.js dependencies\\n"
        
        return structure