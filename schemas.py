from typing import Optional, List
from pydantic import BaseModel, Field
import uuid

class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    status: str = "pending"  # e.g., pending, in_progress, completed
    priority: int = 0       # e.g., 0 (low), 1 (medium), 2 (high)
    project_id: Optional[str] = None

class Idea(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    summary: str
    details: Optional[str] = None
    related_project_id: Optional[str] = None

class Clarification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
    answer: Optional[str] = None
    context: Optional[str] = None

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    tasks: List[Task] = []
    ideas: List[Idea] = []
    clarifications: List[Clarification] = []

# Example Usage (optional, for testing)
if __name__ == "__main__":
    # Create a project
    project1 = Project(name="Personal AI Strategy Assistant Development", description="Build an AI assistant for project management.")
    print(f"Project created: {project1.name} (ID: {project1.id})")

    # Add an idea to the project
    idea1 = Idea(summary="Use LangGraph for agent orchestration", related_project_id=project1.id)
    project1.ideas.append(idea1)
    print(f"Idea added: {idea1.summary}")

    # Add a task to the project
    task1 = Task(name="Define Pydantic Schemas", description="Create schemas for Project, Task, Idea, Clarification.", project_id=project1.id, priority=2)
    project1.tasks.append(task1)
    print(f"Task added: {task1.name}, Status: {task1.status}")

    # Add a clarification
    clarification1 = Clarification(question="What is the primary goal of the Planner Agent?", context="Agent Design")
    project1.clarifications.append(clarification1)
    print(f"Clarification added: {clarification1.question}")

    print("\nProject Details:")
    print(project1.model_dump_json(indent=2))
