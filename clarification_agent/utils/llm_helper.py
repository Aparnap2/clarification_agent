"""
LLM Helper module for integrating with language models.
"""
import os
import json
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import re

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
    
    def _call_openrouter(self, messages: List[Dict[str, str]], temperature: float = 0.7, stream: bool = False) -> Optional[str]:
        """
        Call OpenRouter API with the given messages.
        
        Args:
            messages: List of message objects with role and content
            temperature: Temperature for generation (0.0 to 1.0)
            stream: Whether to stream the response
            
        Returns:
            Generated text or None if API call fails
            If stream=True, returns a generator that yields chunks of text
        """
        if not self.api_key:
            return None
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "stream": stream
        }
        
        try:
            if stream:
                # Streaming mode
                response = requests.post(self.api_url, headers=headers, json=data, stream=True)
                response.raise_for_status()
                
                # Return a generator that yields chunks of text
                def generate():
                    collected_chunks = []
                    collected_messages = []
                    
                    for chunk in response.iter_lines():
                        if chunk:
                            chunk = chunk.decode('utf-8')
                            if chunk.startswith('data: '):
                                chunk = chunk[6:]  # Remove 'data: ' prefix
                                
                                # Skip [DONE] message
                                if chunk == '[DONE]':
                                    break
                                    
                                try:
                                    chunk_data = json.loads(chunk)
                                    choices = chunk_data.get('choices', [])
                                    if choices and len(choices) > 0:
                                        delta = choices[0].get('delta', {})
                                        if 'content' in delta and delta['content']:
                                            content = delta['content']
                                            collected_chunks.append(chunk)
                                            collected_messages.append(content)
                                            yield content
                                except Exception as e:
                                    print(f"Error parsing chunk: {e}")
                    
                    # Return the full message when done
                    return ''.join(collected_messages)
                
                return generate()
            else:
                # Non-streaming mode
                response = requests.post(self.api_url, headers=headers, json=data)
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Error calling OpenRouter API: {e}")
            return None
    
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
        perspective = context.get("perspective", "") if context else ""
        
        # Build a prompt for the LLM based on context
        system_message = "You are an AI assistant helping to clarify project requirements and provide suggestions."
        
        # Add perspective-specific instructions
        if perspective:
            system_message += f" You are acting as a {perspective.replace('_', ' ')}."
        
        # Create messages for the LLM
        messages = [
            {"role": "system", "content": system_message}
        ]
        
        # Add context to the user message
        user_message = prompt + "\n\n"
        
        if description:
            user_message += f"Project description: {description}\n\n"
        
        if mvp_features:
            user_message += f"MVP features: {', '.join(mvp_features)}\n\n"
        
        if tech:
            user_message += f"Technology: {tech}\n\n"
        
        messages.append({"role": "user", "content": user_message})
        
        # Call the LLM
        response = self._call_openrouter(messages)
        
        # If LLM call fails, use fallback responses
        if not response:
            # Fallback to static responses if API call fails
            if perspective == "product_manager" or "goals" in prompt.lower():
                desc_preview = description[:50] + "..." if description and len(description) > 50 else description or "your project"
                return f"Based on your description of {desc_preview}, I recommend these goals:\n\n1. Create an intuitive user interface for non-technical users\n2. Implement secure data storage and retrieval\n3. Enable seamless integration with existing systems\n4. Provide comprehensive analytics and reporting\n5. Ensure scalability to handle growing user base"
                
            elif perspective == "business_analyst" or "mvp features" in prompt.lower():
                return "Looking at this from a business perspective, these features would deliver the most value in your MVP:\n\n1. User authentication and profile management\n2. Core functionality for primary use case\n3. Basic dashboard with essential metrics\n4. Simple data export capabilities\n5. Minimal admin controls for oversight\n6. Responsive design for mobile and desktop"
                
            elif "exclude" in prompt.lower():
                return "To keep your MVP focused, I recommend excluding these features for now:\n\n1. Advanced analytics and reporting\n2. Third-party integrations beyond essential ones\n3. Custom theming and white-labeling\n4. Multi-language support\n5. Offline functionality"
                
            elif perspective == "tech_lead" or "tech stack" in prompt.lower():
                desc_preview = description[:30] + "..." if description and len(description) > 30 else description or "your project"
                return f"Based on your requirements for {desc_preview}, I recommend this tech stack:\n\nFrontend: React with Material UI\nBackend: Node.js with Express\nDatabase: PostgreSQL for structured data\nAuthentication: Auth0 for secure user management\nDeployment: Docker containers on AWS for scalability"
                
            elif perspective == "ux_designer":
                return "From a UX perspective, I recommend focusing on these key user journeys:\n\n1. Onboarding flow - Keep it simple with minimal steps\n2. Core functionality - Make the primary action obvious and accessible\n3. Dashboard - Present key information at a glance\n4. Settings/Profile - Keep configuration options organized and intuitive\n5. Feedback loop - Make it easy for users to report issues or suggest improvements"
                
            elif perspective == "qa_engineer":
                return "From a quality assurance standpoint, these areas need particular attention:\n\n1. User authentication edge cases (password reset, account recovery)\n2. Data validation and error handling\n3. Performance under load, especially for database operations\n4. Cross-browser and responsive design testing\n5. Security testing for common vulnerabilities"
                
            elif "why" in prompt.lower() and tech:
                return f"{tech} is an excellent choice because it offers a good balance of performance, developer experience, and community support. It has robust documentation, scales well for growing applications, and integrates seamlessly with other modern tools in your stack."
                
            else:
                # Generic fallback response based on description
                if description:
                    desc_preview = description[:50] + "..." if len(description) > 50 else description
                    return f"Based on your project description '{desc_preview}', I suggest focusing on these key aspects:\n\n1. User authentication and authorization\n2. Core data model design\n3. API endpoints for essential features\n4. Simple but effective UI for MVP features\n5. Automated testing for critical paths"
                else:
                    return "I'd be happy to help clarify your project. Could you tell me more about what you're trying to build?"
        
        return response
    
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
        
        # Try to use the LLM for validation
        description = context.get("description", "") if context else ""
        
        # Build a prompt for the LLM
        system_message = "You are an AI assistant helping to validate project assumptions. For each assumption, determine if it's reasonable or potentially problematic."
        
        # Create messages for the LLM
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Project description: {description}\n\nPlease validate these assumptions and respond with a JSON object where the keys are the assumptions and the values are boolean (true for valid, false for problematic):\n\n{assumptions}"}
        ]
        
        # Call the LLM
        response = self._call_openrouter(messages)
        
        # If LLM call fails or doesn't return valid JSON, use fallback validation
        if not response:
            # Fallback to simple heuristic validation
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
        
        # Try to parse the LLM response as JSON
        try:
            # Extract JSON from the response if needed
            json_str = response
            if '```json' in response:
                json_str = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                json_str = response.split('```')[1].split('```')[0].strip()
                
            validation_results = json.loads(json_str)
            
            # Ensure all assumptions are in the results
            results = {}
            for assumption in assumptions:
                if assumption in validation_results:
                    results[assumption] = bool(validation_results[assumption])
                else:
                    # Use fallback for missing assumptions
                    lower_assumption = assumption.lower()
                    is_valid = True
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
        except Exception as e:
            print(f"Error parsing LLM response as JSON: {e}")
            # Fall back to simple heuristic validation
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
        # Extract relevant project information
        project_name = project_data.get("name", "")
        description = project_data.get("description", "")
        tech_stack = project_data.get("tech_stack", [])
        mvp_features = project_data.get("mvp_features", [])
        tech_stack_str = ", ".join(tech_stack) if tech_stack else ""
        
        # Build a prompt for the LLM
        system_message = "You are an AI assistant helping to generate a file structure for a software project."
        
        user_message = f"Project name: {project_name}\n\n"
        if description:
            user_message += f"Description: {description}\n\n"
        if tech_stack:
            user_message += f"Technology stack: {tech_stack_str}\n\n"
        if mvp_features:
            user_message += f"Features: {', '.join(mvp_features)}\n\n"
            
        user_message += "Please generate a file structure for this project. Respond with a JSON object where keys are file paths and values are brief descriptions of each file's purpose. Include only the JSON object in your response."
        
        # Create messages for the LLM
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        # Call the LLM
        response = self._call_openrouter(messages)
        
        # If LLM call fails or doesn't return valid JSON, use fallback structure
        if not response:
            # Fallback to static file structure
            # Default structure for any project
            file_structure = {
                "README.md": "Project documentation",
                ".gitignore": "Git ignore file"
            }
            
            # Add React-specific files
            if any(tech.lower() in ["react", "reactjs"] for tech in tech_stack):
                file_structure.update({
                    "package.json": "Project dependencies and scripts",
                    "public/index.html": "HTML entry point",
                    "src/index.js": "JavaScript entry point",
                    "src/App.js": "Main application component",
                    "src/components/Header.js": "Header component",
                    "src/styles/global.css": "Global styles"
                })
            
            # Add Python-specific files
            if any(tech.lower() in ["python", "flask", "fastapi", "django"] for tech in tech_stack):
                file_structure.update({
                    "requirements.txt": "Python dependencies",
                    "app.py": "Main application entry point",
                    "models/__init__.py": "Models package",
                    "utils/__init__.py": "Utilities package"
                })
            
            # Add Node.js-specific files
            if any(tech.lower() in ["node", "nodejs", "express"] for tech in tech_stack):
                file_structure.update({
                    "package.json": "Project dependencies and scripts",
                    "index.js": "Main entry point",
                    "routes/index.js": "API routes",
                    "models/index.js": "Data models"
                })
            
            return file_structure
        
        # Try to parse the LLM response as JSON
        try:
            # Extract JSON from the response if needed
            json_str = response
            if '```json' in response:
                json_str = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                json_str = response.split('```')[1].split('```')[0].strip()
                
            file_structure = json.loads(json_str)
            
            # Ensure we have at least README.md and .gitignore
            if "README.md" not in file_structure:
                file_structure["README.md"] = "Project documentation"
            if ".gitignore" not in file_structure:
                file_structure[".gitignore"] = "Git ignore file"
                
            return file_structure
        except Exception as e:
            print(f"Error parsing LLM response as JSON: {e}")
            # Fall back to static file structure
            file_structure = {
                "README.md": "Project documentation",
                ".gitignore": "Git ignore file"
            }
            
            # Add React-specific files
            if any(tech.lower() in ["react", "reactjs"] for tech in tech_stack):
                file_structure.update({
                    "package.json": "Project dependencies and scripts",
                    "public/index.html": "HTML entry point",
                    "src/index.js": "JavaScript entry point",
                    "src/App.js": "Main application component",
                    "src/components/Header.js": "Header component",
                    "src/styles/global.css": "Global styles"
                })
            
            # Add Python-specific files
            if any(tech.lower() in ["python", "flask", "fastapi", "django"] for tech in tech_stack):
                file_structure.update({
                    "requirements.txt": "Python dependencies",
                    "app.py": "Main application entry point",
                    "models/__init__.py": "Models package",
                    "utils/__init__.py": "Utilities package"
                })
            
            # Add Node.js-specific files
            if any(tech.lower() in ["node", "nodejs", "express"] for tech in tech_stack):
                file_structure.update({
                    "package.json": "Project dependencies and scripts",
                    "index.js": "Main entry point",
                    "routes/index.js": "API routes",
                    "models/index.js": "Data models"
                })
            
            return file_structure
        
    def generate_tasks(self, project_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate development tasks based on project details.
        
        Args:
            project_data: Project data including features, file structure, etc.
            
        Returns:
            List of task dictionaries
        """
        # Extract relevant project information
        project_name = project_data.get("name", "")
        description = project_data.get("description", "")
        tech_stack = project_data.get("tech_stack", [])
        mvp_features = project_data.get("mvp_features", [])
        file_map = project_data.get("file_map", {})
        
        # Build a prompt for the LLM
        system_message = "You are an AI assistant helping to generate development tasks for a software project."
        
        user_message = f"Project name: {project_name}\n\n"
        if description:
            user_message += f"Description: {description}\n\n"
        if tech_stack:
            user_message += f"Technology stack: {', '.join(tech_stack)}\n\n"
        if mvp_features:
            user_message += f"Features: {', '.join(mvp_features)}\n\n"
        if file_map:
            user_message += "File structure:\n"
            for file_path, file_desc in file_map.items():
                user_message += f"- {file_path}: {file_desc}\n"
            user_message += "\n"
            
        user_message += "Please generate a list of development tasks for this project. Each task should include a title, file path (if applicable), time estimate, and priority (1-5, where 1 is highest). Respond with a JSON array of task objects. Include only the JSON array in your response."
        
        # Create messages for the LLM
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        # Call the LLM
        response = self._call_openrouter(messages)
        
        # If LLM call fails or doesn't return valid JSON, use fallback tasks
        if not response:
            # Fallback to static tasks
            tasks = [
                {"title": "Project setup and repository initialization", "file": "README.md", "estimate": "0.5h", "priority": 1},
                {"title": "Create project structure", "file": "", "estimate": "1h", "priority": 1},
                {"title": "Write documentation", "file": "README.md", "estimate": "1h", "priority": 5}
            ]
            
            # Add feature-specific tasks
            features = project_data.get("mvp_features", [])
            for i, feature in enumerate(features[:5]):  # Limit to first 5 features
                tasks.append({
                    "title": f"Implement {feature}", 
                    "file": "", 
                    "estimate": "3h", 
                    "priority": i + 2
                })
            
            # Add testing task
            tasks.append({"title": "Write tests", "file": "", "estimate": "3h", "priority": 4})
            
            return tasks
        
        # Try to parse the LLM response as JSON
        try:
            # Extract JSON from the response if needed
            json_str = response
            if '```json' in response:
                json_str = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                json_str = response.split('```')[1].split('```')[0].strip()
                
            tasks = json.loads(json_str)
            
            # Ensure we have at least some basic tasks
            if not tasks:
                tasks = [
                    {"title": "Project setup and repository initialization", "file": "README.md", "estimate": "0.5h", "priority": 1},
                    {"title": "Create project structure", "file": "", "estimate": "1h", "priority": 1},
                    {"title": "Write documentation", "file": "README.md", "estimate": "1h", "priority": 5}
                ]
                
            return tasks
        except Exception as e:
            print(f"Error parsing LLM response as JSON: {e}")
            # Fall back to static tasks
            tasks = [
                {"title": "Project setup and repository initialization", "file": "README.md", "estimate": "0.5h", "priority": 1},
                {"title": "Create project structure", "file": "", "estimate": "1h", "priority": 1},
                {"title": "Write documentation", "file": "README.md", "estimate": "1h", "priority": 5}
            ]
            
            # Add feature-specific tasks
            features = project_data.get("mvp_features", [])
            for i, feature in enumerate(features[:5]):  # Limit to first 5 features
                tasks.append({
                    "title": f"Implement {feature}", 
                    "file": "", 
                    "estimate": "3h", 
                    "priority": i + 2
                })
            
            # Add testing task
            tasks.append({"title": "Write tests", "file": "", "estimate": "3h", "priority": 4})
            
            return tasks