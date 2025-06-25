from typing import Dict, Any
from clarification_agent.nodes.base_node import BaseNodeHandler
from clarification_agent.models.project import Project

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
        """Generate a suggested file structure based on the tech stack"""
        structure = "# Suggested structure (edit as needed):\\n"
        
        # Detect frontend framework
        frontend = next((tech for tech in project.tech_stack if tech in 
                        ["React", "Vue", "Angular", "Next.js", "Svelte"]), None)
        
        # Detect backend framework
        backend = next((tech for tech in project.tech_stack if tech in 
                       ["Node.js", "Python/Flask", "Python/FastAPI", "Python/Django", "Java/Spring", "Go", "Ruby on Rails"]), None)
        
        if frontend == "React":
            structure += "src/components/App.jsx: Main application component\\n"
            structure += "src/components/Header.jsx: Header component\\n"
            structure += "src/pages/Home.jsx: Home page\\n"
            structure += "src/styles/main.css: Main stylesheet\\n"
        elif frontend == "Next.js":
            structure += "pages/index.js: Home page\\n"
            structure += "pages/api/hello.js: Example API route\\n"
            structure += "components/Layout.js: Layout component\\n"
            structure += "styles/globals.css: Global styles\\n"
        
        if backend == "Python/Flask":
            structure += "app.py: Main Flask application\\n"
            structure += "routes/api.py: API routes\\n"
            structure += "models/user.py: User model\\n"
            structure += "templates/index.html: Main template\\n"
        elif backend == "Python/FastAPI":
            structure += "main.py: FastAPI application\\n"
            structure += "routers/api.py: API routes\\n"
            structure += "models/models.py: Pydantic models\\n"
            structure += "database/db.py: Database connection\\n"
        
        # Add common files
        structure += "README.md: Project documentation\\n"
        structure += "requirements.txt: Python dependencies\\n" if "Python" in str(project.tech_stack) else ""
        structure += "package.json: Node.js dependencies\\n" if any(js_tech in str(project.tech_stack) for js_tech in ["React", "Vue", "Angular", "Next.js", "Node.js"]) else ""
        
        return structure