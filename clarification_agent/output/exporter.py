import os
import json
import yaml
from typing import Dict, Any
from clarification_agent.models.project import Project

class Exporter:
    """
    Handles exporting project data to various file formats.
    """
    
    def __init__(self, project: Project):
        self.project = project
    
    def export_all(self):
        """Export all project files"""
        self.export_clarity_json()
        self.export_plan_yml()
        self.export_readme()
        self.export_architecture_md()
        # MCP implementation is excluded from MVP as per requirements
    
    def export_clarity_json(self):
        """Export project data to .clarity/project.json"""
        os.makedirs(".clarity", exist_ok=True)
        
        with open(os.path.join(".clarity", f"{self.project.name}.json"), "w") as f:
            json.dump(self.project.dict(), f, indent=2)
    
    def export_plan_yml(self):
        """Export tasks to .plan.yml"""
        plan_data = {
            "plan": [
                {
                    "title": task["title"],
                    "file": task["file"],
                    "estimate": task["estimate"],
                    "priority": task["priority"]
                }
                for task in self.project.tasks
            ]
        }
        
        with open(".plan.yml", "w") as f:
            yaml.dump(plan_data, f, default_flow_style=False)
    
    def export_readme(self):
        """Export README.md"""
        readme_content = f"""# {self.project.name}

{self.project.description or ''}

{self.project.purpose or ''}

## 🧠 Features (MVP)

"""
        
        # Add MVP features
        for feature in self.project.mvp_features:
            readme_content += f"- {feature}\n"
        
        # Add tech stack
        if self.project.tech_stack:
            readme_content += "\n## 🔧 Tech Stack\n\n"
            for tech in self.project.tech_stack:
                readme_content += f"- {tech}\n"
        
        # Add excluded features
        if self.project.excluded_features:
            readme_content += "\n## ❌ Not Included\n\n"
            for feature in self.project.excluded_features:
                readme_content += f"- {feature}\n"
        
        # Add project structure
        if self.project.file_map:
            readme_content += "\n## 📁 Project Structure\n\n"
            for file_path, description in self.project.file_map.items():
                readme_content += f"- `{file_path}`: {description}\n"
        
        readme_content += "\n> Created with Clarifier Agent.\n"
        
        with open("README.md", "w") as f:
            f.write(readme_content)
    
    def export_architecture_md(self):
        """Export architecture.md"""
        arch_content = f"""# {self.project.name} - Architecture

## Overview

{self.project.description or ''}

## Design Decisions

"""
        
        # Add decisions
        for decision, reasoning in self.project.decisions.items():
            arch_content += f"### {decision}\n\n{reasoning}\n\n"
        
        # Add file structure
        if self.project.file_map:
            arch_content += "## File Structure\n\n"
            for file_path, description in self.project.file_map.items():
                arch_content += f"- `{file_path}`: {description}\n"
        
        with open("architecture.md", "w") as f:
            f.write(arch_content)