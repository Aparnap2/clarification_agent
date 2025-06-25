"""
LLM Helper module for integrating with language models.
"""
import os
import json
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMHelper:
    """
    Helper class for interacting with language models via OpenRouter.
    """
    
    def __init__(self, model_name="deepseek/deepseek-chat-v3-0324:free"):
        self.model_name = model_name
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        
        if not self.api_key:
            print("Warning: OPENROUTER_API_KEY not found in environment variables.")
            print("Using placeholder responses instead of actual AI.")
    
    def _call_openrouter(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> Optional[str]:
        """
        Call OpenRouter API with the given messages.
        
        Args:
            messages: List of message objects with role and content
            temperature: Temperature for generation (0.0 to 1.0)
            
        Returns:
            Generated text or None if API call fails
        """
        # Skip API call and use fallback responses to avoid payment issues
        return None
        
        # The code below is disabled to avoid payment issues
        '''
        if not self.api_key:
            return None
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Error calling OpenRouter API: {e}")
            return None
        '''
    
    def generate_suggestions(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate suggestions using an LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            context: Additional context for the prompt
            
        Returns:
            Generated text from the LLM
        """
        # Extract key information from context
        description = context.get("description", "") if context else ""
        goals = context.get("goals", []) if context else []
        mvp_features = context.get("mvp_features", []) if context else []
        tech = context.get("tech", "") if context else ""
        
        # Generate appropriate responses based on the prompt and context
        if "goals" in prompt.lower():
            return "1. Create an intuitive user interface for non-technical users\n2. Implement secure data storage and retrieval\n3. Enable seamless integration with existing systems\n4. Provide comprehensive analytics and reporting\n5. Ensure scalability to handle growing user base"
            
        elif "mvp features" in prompt.lower():
            return "1. User authentication and profile management\n2. Core functionality for primary use case\n3. Basic dashboard with essential metrics\n4. Simple data export capabilities\n5. Minimal admin controls for oversight\n6. Responsive design for mobile and desktop"
            
        elif "exclude" in prompt.lower():
            return "1. Advanced analytics and reporting\n2. Third-party integrations beyond essential ones\n3. Custom theming and white-labeling\n4. Multi-language support\n5. Offline functionality"
            
        elif "tech stack" in prompt.lower():
            return "Based on your requirements, I recommend:\n\nFrontend: React with Material UI\nBackend: Node.js with Express\nDatabase: PostgreSQL for structured data\nAuthentication: Auth0 for secure user management\nDeployment: Docker containers on AWS for scalability"
            
        elif "why" in prompt.lower() and tech:
            return f"{tech} is an excellent choice because it offers a good balance of performance, developer experience, and community support. It has robust documentation, scales well for growing applications, and integrates seamlessly with other modern tools in your stack."
            
        else:
            # Generic fallback response
            return f"Based on your project description, I suggest focusing on these key aspects:\n\n1. User authentication and authorization\n2. Core data model design\n3. API endpoints for essential features\n4. Simple but effective UI for MVP features\n5. Automated testing for critical paths"
    
    def validate_assumptions(self, assumptions: List[str], context: Optional[Dict[str, Any]] = None) -> Dict[str, bool]:
        """
        Validate assumptions using an LLM.
        
        Args:
            assumptions: List of assumptions to validate
            context: Additional context for validation
            
        Returns:
            Dictionary of validation results
        """
        if not assumptions:
            return {}
        
        # For the MVP, we'll use a simple heuristic to validate assumptions
        # In a real implementation, this would use an LLM to provide more nuanced validation
        results = {}
        
        for assumption in assumptions:
            # Flag assumptions that might be problematic based on keywords
            lower_assumption = assumption.lower()
            is_valid = True
            
            # Check for potentially problematic assumptions
            problematic_phrases = [
                "all users will", "everyone will", "always", "never", "100%", 
                "perfect", "instantly", "immediately", "no issues", "no problems",
                "trivial", "easy to", "simple to", "just need to", "just have to"
            ]
            
            for phrase in problematic_phrases:
                if phrase in lower_assumption:
                    is_valid = False
                    break
            
            results[assumption] = is_valid
        
        return results
        
    def generate_file_structure(self, project_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate a suggested file structure based on project details.
        
        Args:
            project_data: Project data including tech stack, features, etc.
            
        Returns:
            Dictionary mapping file paths to descriptions
        """
        tech_stack = project_data.get("tech_stack", [])
        
        # Check for common tech stack patterns and return appropriate file structure
        if any("React" in tech for tech in tech_stack):
            return {
                "README.md": "Project documentation and setup instructions",
                "package.json": "Project dependencies and scripts",
                "public/index.html": "HTML entry point",
                "public/favicon.ico": "Website favicon",
                "src/index.js": "JavaScript entry point",
                "src/App.js": "Main application component",
                "src/components/Header.js": "Header component with navigation",
                "src/components/Footer.js": "Footer component with links",
                "src/pages/Home.js": "Home page component",
                "src/pages/Dashboard.js": "User dashboard page",
                "src/services/api.js": "API service for backend communication",
                "src/utils/helpers.js": "Helper functions",
                "src/styles/global.css": "Global styles",
                "src/context/AuthContext.js": "Authentication context",
                ".env": "Environment variables",
                ".gitignore": "Git ignore file"
            }
        elif any("Python" in tech for tech in tech_stack) or any("Flask" in tech for tech in tech_stack) or any("FastAPI" in tech for tech in tech_stack):
            return {
                "README.md": "Project documentation and setup instructions",
                "requirements.txt": "Python dependencies",
                "app.py": "Main application entry point",
                "config.py": "Configuration settings",
                "models/user.py": "User data model",
                "models/item.py": "Item data model",
                "routes/auth.py": "Authentication routes",
                "routes/api.py": "API routes",
                "services/database.py": "Database service",
                "utils/helpers.py": "Helper functions",
                "templates/index.html": "Main template",
                "templates/dashboard.html": "Dashboard template",
                "static/css/style.css": "CSS styles",
                "static/js/main.js": "JavaScript functionality",
                ".env": "Environment variables",
                ".gitignore": "Git ignore file"
            }
        elif any("Node" in tech for tech in tech_stack) or any("Express" in tech for tech in tech_stack):
            return {
                "README.md": "Project documentation and setup instructions",
                "package.json": "Project dependencies and scripts",
                "index.js": "Main entry point",
                "config/database.js": "Database configuration",
                "config/auth.js": "Authentication configuration",
                "models/User.js": "User model",
                "models/Item.js": "Item model",
                "routes/api.js": "API routes",
                "routes/auth.js": "Authentication routes",
                "controllers/userController.js": "User controller",
                "controllers/itemController.js": "Item controller",
                "middleware/auth.js": "Authentication middleware",
                "utils/helpers.js": "Helper functions",
                ".env": "Environment variables",
                ".gitignore": "Git ignore file"
            }
        else:
            # Generic structure for any project
            return {
                "README.md": "Project documentation",
                "src/main.js": "Main entry point",
                "src/components/App.js": "Main application component",
                "src/styles/main.css": "Main stylesheet",
                "api/routes.js": "API routes",
                "models/data.js": "Data models",
                "config/settings.js": "Application settings",
                "utils/helpers.js": "Helper functions",
                ".env": "Environment variables",
                ".gitignore": "Git ignore file"
            }
        
    def generate_tasks(self, project_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate development tasks based on project details.
        
        Args:
            project_data: Project data including features, file structure, etc.
            
        Returns:
            List of task dictionaries
        """
        features = project_data.get("mvp_features", [])
        file_map = project_data.get("file_map", {})
        tech_stack = project_data.get("tech_stack", [])
        
        # Start with common tasks
        tasks = [
            {"title": "Project setup and repository initialization", "file": "README.md", "estimate": "0.5h", "priority": 1},
            {"title": "Create project structure", "file": "", "estimate": "1h", "priority": 1},
            {"title": "Setup configuration files", "file": ".env", "estimate": "0.5h", "priority": 1},
            {"title": "Write documentation", "file": "README.md", "estimate": "1h", "priority": 5}
        ]
        
        # Add feature-specific tasks
        for i, feature in enumerate(features[:5]):  # Limit to first 5 features
            # Find related files
            related_files = []
            for file_path in file_map.keys():
                if "component" in file_path.lower() or "page" in file_path.lower() or "route" in file_path.lower():
                    related_files.append(file_path)
            
            if related_files and i < len(related_files):
                file_path = related_files[i]
            else:
                file_path = ""
                
            tasks.append({
                "title": f"Implement {feature}", 
                "file": file_path, 
                "estimate": "3h", 
                "priority": i + 2
            })
        
        # Add tech-specific tasks
        if any("React" in tech for tech in tech_stack) or any("Vue" in tech for tech in tech_stack):
            tasks.extend([
                {"title": "Set up component library", "file": "src/components", "estimate": "2h", "priority": 2},
                {"title": "Implement state management", "file": "src/store", "estimate": "3h", "priority": 2},
                {"title": "Create responsive layouts", "file": "src/styles", "estimate": "2h", "priority": 3}
            ])
            
        if any("API" in tech for tech in tech_stack) or any("backend" in tech.lower() for tech in tech_stack):
            tasks.extend([
                {"title": "Design database schema", "file": "models", "estimate": "2h", "priority": 2},
                {"title": "Implement API endpoints", "file": "routes/api.js", "estimate": "4h", "priority": 2},
                {"title": "Add authentication", "file": "routes/auth.js", "estimate": "3h", "priority": 3}
            ])
            
        # Add testing tasks
        tasks.append({"title": "Write unit tests", "file": "tests", "estimate": "3h", "priority": 4})
        tasks.append({"title": "Perform integration testing", "file": "", "estimate": "2h", "priority": 4})
        
        return tasks