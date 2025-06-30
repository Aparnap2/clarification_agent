import os
import json
from openrouter import Client
from schemas import Task, Project # Assuming schemas.py is in the parent directory or PYTHONPATH is set
from typing import List

# Attempt to load environment variables if python-dotenv is present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass # python-dotenv not installed, environment variables should be set manually

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# Recommended model, but can be changed.
OPENROUTER_MODEL = os.getenv("OPENROUTER_PLANNER_MODEL", "mistralai/mistral-7b-instruct:free")


class PlannerAgent:
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or OPENROUTER_API_KEY
        if not self.api_key:
            raise ValueError("OpenRouter API key not provided. Set OPENROUTER_API_KEY environment variable.")
        self.client = Client(api_key=self.api_key)
        self.model = model or OPENROUTER_MODEL
        if not self.model:
            self.model = "mistralai/mistral-7b-instruct:free" # Default


    def generate_initial_plan(self, goal: str, project_id: str, project_context: str = "") -> List[Task]:
        """
        Generates a list of actionable tasks based on a goal using an LLM.
        """
        prompt = f"""The user's project goal is: "{goal}".
Project context: {project_context if project_context else "General context related to the goal."}

You are an AI Project Planner. Your task is to break down this goal into a list of 3-5 high-level, actionable tasks.
For each task, provide a concise 'name' and a brief 'description'.
The tasks should be logical steps towards achieving the overall goal.
Focus on the initial planning phase.

Output the tasks as a JSON list of objects, where each object has a "name" and a "description" key.
Example JSON format:
[
  {{"name": "Task 1 Name", "description": "Brief description of task 1."}},
  {{"name": "Task 2 Name", "description": "Brief description of task 2."}}
]

Generate only the JSON list of tasks.
"""
        tasks = []

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an AI Project Planner that generates a list of tasks in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}, # Request JSON output if model supports it
                max_tokens=500, # Allow more tokens for a list of tasks
                temperature=0.5 # More deterministic for planning
            )
            if response.choices and response.choices[0].message.content:
                content = response.choices[0].message.content.strip()
                # The LLM should return a JSON string representing a list of tasks.
                # Sometimes, the LLM might wrap the JSON in markdown (```json ... ```)
                if content.startswith("```json"):
                    content = content[7:-3].strip() # Remove markdown fences
                elif content.startswith("```"): # A less specific markdown fence
                     content = content[3:-3].strip()

                # The model might return a dict with a key like "tasks" or "plan"
                # We need to find the actual list of tasks.
                parsed_json = json.loads(content)

                task_list_data = []
                if isinstance(parsed_json, list):
                    task_list_data = parsed_json
                elif isinstance(parsed_json, dict):
                    # Try to find a list within the dict (common pattern)
                    for key, value in parsed_json.items():
                        if isinstance(value, list):
                            task_list_data = value
                            break
                    if not task_list_data:
                        # If it's a dict but no list found, maybe it's a single task object? Unlikely for this prompt.
                         print(f"Warning: LLM returned a dictionary but no clear list of tasks: {parsed_json}")


                for task_data in task_list_data:
                    if isinstance(task_data, dict) and "name" in task_data and "description" in task_data:
                        tasks.append(Task(
                            name=task_data["name"],
                            description=task_data["description"],
                            project_id=project_id,
                            priority=1 # Default to medium for now
                        ))
                    else:
                        print(f"Warning: Skipping malformed task data from LLM: {task_data}")
            else:
                print(f"Warning: LLM returned no content for PlannerAgent. Response: {response}")

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from OpenRouter API in PlannerAgent: {e}")
            print(f"LLM Raw Output: {content if 'content' in locals() else 'No content available'}")
        except Exception as e:
            print(f"Error calling OpenRouter API or processing response in PlannerAgent: {e}")

        # Fallback to dummy tasks if LLM fails or returns no valid tasks
        if not tasks:
            print("PlannerAgent: Falling back to dummy tasks.")
            tasks.extend([
                Task(name=f"Define scope for '{goal}'", description="Clearly outline the objectives, deliverables, and boundaries.", project_id=project_id, priority=2),
                Task(name=f"Research options for '{goal}'", description="Gather information and explore solutions.", project_id=project_id, priority=1),
                Task(name=f"Create initial draft for '{goal}'", description="Develop a first version or outline.", project_id=project_id, priority=1)
            ])
        return tasks

if __name__ == "__main__":
    # Example Usage (Requires OPENROUTER_API_KEY to be set)
    print(f"Attempting to use model: {OPENROUTER_MODEL}")
    if not OPENROUTER_API_KEY:
        print("OPENROUTER_API_KEY not set. Please set it in your environment or a .env file to run this example.")
        exit()

    agent = PlannerAgent()
    # Create a dummy project for context
    test_project = Project(name="E-commerce Platform Revamp", description="Overhaul the existing online store for better UX and performance.")

    goals = [
        "Develop a new feature for user authentication with two-factor auth",
        "Organize a team workshop on Agile methodologies",
        "Create a content marketing strategy for Q3",
        "Migrate the customer database to a new cloud provider",
        "Design a loyalty program for returning customers"
    ]

    for user_goal in goals:
        print(f"\nUser Goal: {user_goal}")
        plan = agent.generate_initial_plan(user_goal, test_project.id, project_context=test_project.description)
        print("Generated Plan:")
        if plan:
            for i, task in enumerate(plan):
                print(f"  Task {i+1}: {task.name}")
                print(f"    Description: {task.description}")
                print(f"    Project ID: {task.project_id}, Priority: {task.priority}, Status: {task.status}")
        else:
            print("  No plan generated.")
        print("-" * 30)
