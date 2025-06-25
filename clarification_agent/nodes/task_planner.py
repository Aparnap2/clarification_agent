from typing import Dict, Any
from clarification_agent.nodes.base_node import BaseNodeHandler
from clarification_agent.models.project import Project

class TaskPlannerNode(BaseNodeHandler):
    """
    Node for planning development tasks.
    """
    
    def get_ui_data(self, project: Project) -> Dict[str, Any]:
        """Get UI data for the TaskPlanner node"""
        # Generate suggested tasks based on features and file map
        suggested_tasks = self._generate_suggested_tasks(project)
        
        # Format existing tasks
        existing_tasks = ""
        for task in project.tasks:
            existing_tasks += f"{task.get('title', '')}: {task.get('file', '')}: {task.get('estimate', '')}: {task.get('priority', '')}\\n"
        
        return {
            "title": "Development Task Planning",
            "description": "Break down the project into atomic development tasks. Format: Task Title: file/path.ext: Time Estimate: Priority (1-5)",
            "questions": [
                {
                    "id": "tasks",
                    "question": "Development Tasks:",
                    "type": "text",
                    "value": suggested_tasks + "\\n" + existing_tasks
                }
            ]
        }
    
    def process_responses(self, project: Project, responses: Dict[str, Any]) -> None:
        """Process responses for the TaskPlanner node"""
        # Clear existing tasks
        project.tasks = []
        
        # Process tasks
        tasks_text = responses.get("tasks", "")
        lines = tasks_text.split("\\n")
        
        for line in lines:
            if ":" in line and not line.startswith("#"):
                parts = [part.strip() for part in line.split(":")]
                
                if len(parts) >= 4:
                    title, file_path, estimate, priority = parts[:4]
                    
                    try:
                        priority_num = int(priority)
                    except ValueError:
                        priority_num = 3  # Default priority
                    
                    project.tasks.append({
                        "title": title,
                        "file": file_path,
                        "estimate": estimate,
                        "priority": priority_num
                    })
    
    def _generate_suggested_tasks(self, project: Project) -> str:
        """Generate suggested tasks based on features and file map"""
        tasks = "# Suggested tasks (edit as needed):\\n"
        
        # Add setup tasks
        tasks += "Project setup: README.md: 0.5h: 1\\n"
        tasks += "Create project structure: : 1h: 1\\n"
        
        # Add tasks for each feature
        for i, feature in enumerate(project.mvp_features):
            # Find related files
            related_files = []
            for file_path, description in project.file_map.items():
                if any(word.lower() in description.lower() for word in feature.lower().split()):
                    related_files.append(file_path)
            
            if related_files:
                for file_path in related_files:
                    tasks += f"Implement {feature}: {file_path}: 2h: {i+2}\\n"
            else:
                tasks += f"Implement {feature}: : 2h: {i+2}\\n"
        
        # Add testing tasks
        tasks += "Write tests: : 3h: 4\\n"
        tasks += "Documentation: README.md: 1h: 5\\n"
        
        return tasks