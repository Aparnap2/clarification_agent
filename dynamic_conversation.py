#!/usr/bin/env python3
"""
Dynamic conversation example for the Clarification Agent.
This version uses LLM to determine the conversation flow dynamically.
"""
import os
import sys
import json
from clarification_agent.core.conversation_agent import ConversationAgent

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the header"""
    print("=" * 80)
    print("🧠 Clarification Agent - Dynamic Conversation Mode")
    print("=" * 80)
    print("Type 'exit' to quit at any time.")
    print("-" * 80)

def load_project_data(project_name):
    """Load project data from .clarity folder if it exists"""
    clarity_path = os.path.join(".clarity", f"{project_name}.json")
    if os.path.exists(clarity_path):
        with open(clarity_path, "r") as f:
            return json.load(f)
    return None

def main():
    """Main CLI function"""
    clear_screen()
    print_header()
    
    # Get project name
    project_name = input("Enter project name: ")
    if not project_name:
        print("Project name is required.")
        return
    
    # Check if project exists
    project_data = None
    if os.path.exists(os.path.join(".clarity", f"{project_name}.json")):
        load_existing = input(f"Project '{project_name}' already exists. Load it? (y/n): ")
        if load_existing.lower() == 'y':
            project_data = load_project_data(project_name)
        else:
            overwrite = input("Overwrite existing project? (y/n): ")
            if overwrite.lower() != 'y':
                print("Exiting...")
                return
    
    # Initialize agent
    agent = ConversationAgent(project_name=project_name, project_data=project_data)
    
    # Start conversation
    print("\nStarting dynamic conversation...\n")
    
    # Get initial message
    response, is_complete = agent.process_user_input("")
    print(f"Agent: {response}\n")
    
    # Main conversation loop
    while not is_complete:
        user_input = input("You: ")
        
        if user_input.lower() == 'exit':
            print("Exiting...")
            break
        
        print("\nAgent is thinking...\n")
        try:
            response, is_complete = agent.process_user_input(user_input)
            print(f"Agent: {response}\n")
        except Exception as e:
            print(f"Error: {str(e)}")
            print("Agent: I'm sorry, I encountered an error. Let's continue with the next step.\n")
    
    if is_complete:
        print("\n" + "=" * 80)
        print("Project planning complete! Generated files:")
        print("- README.md")
        print("- .plan.yml")
        print("- architecture.md")
        print("- .clarity/*.json")
        print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)