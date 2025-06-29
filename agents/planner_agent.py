from schemas import Task, Project # Assuming schemas.py is in the parent directory or PYTHONPATH is set
from typing import List

class PlannerAgent:
    def __init__(self):
        pass

    def generate_initial_plan(self, goal: str, project_id: str) -> List[Task]:
        """
        Generates a basic, high-level plan based on a goal.
        For now, it's a very basic implementation creating a few dummy tasks.
        """
        tasks = []

        # Dummy tasks - in a real scenario, this would involve LLM calls,
        # task decomposition logic, etc.
        tasks.append(Task(
            name=f"Define scope for '{goal}'",
            description="Clearly outline the objectives, deliverables, and boundaries of this goal.",
            project_id=project_id,
            priority=2 # High
        ))
        tasks.append(Task(
            name=f"Research phase for '{goal}'",
            description="Gather necessary information, explore existing solutions, and identify potential challenges.",
            project_id=project_id,
            priority=1 # Medium
        ))
        tasks.append(Task(
            name=f"Develop prototype/MVP for '{goal}'",
            description="Build a first version to test core functionality.",
            project_id=project_id,
            priority=1 # Medium
        ))
        tasks.append(Task(
            name=f"Test and iterate on '{goal}'",
            description="Gather feedback and make improvements.",
            project_id=project_id,
            priority=1 # Medium
        ))
        tasks.append(Task(
            name=f"Finalize and deploy '{goal}'",
            description="Prepare for launch or final implementation.",
            project_id=project_id,
            priority=0 # Low (can be adjusted)
        ))

        return tasks

if __name__ == "__main__":
    # Example Usage
    agent = PlannerAgent()
    test_project = Project(name="Test Project for Planning")

    user_goal1 = "Develop a new feature for user authentication"
    print(f"User Goal: {user_goal1}")
    plan1 = agent.generate_initial_plan(user_goal1, test_project.id)
    print("Generated Plan:")
    for task in plan1:
        print(f"- {task.name} (Priority: {task.priority}, Project ID: {task.project_id})")
    print("-" * 20)

    user_goal2 = "Organize a team workshop"
    print(f"User Goal: {user_goal2}")
    plan2 = agent.generate_initial_plan(user_goal2, test_project.id)
    print("Generated Plan:")
    for task in plan2:
        print(f"- {task.name} (Priority: {task.priority}, Project ID: {task.project_id})")
    print("-" * 20)
