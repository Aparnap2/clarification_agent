#!/usr/bin/env python3
import os
import json
import argparse
from clarification_agent.core.agent_manager import ClarificationAgentManager

def main():
    """Main entry point for the Clarification Agent CLI"""
    parser = argparse.ArgumentParser(description="Clarification Agent - Project planning tool")
    parser.add_argument("--project", required=True, help="Project name")
    parser.add_argument("--update", action="store_true", help="Update existing project")
    
    args = parser.parse_args()
    
    project_name = args.project
    project_data = None
    
    # Check if project exists
    if args.update or os.path.exists(os.path.join(".clarity", f"{project_name}.json")):
        try:
            with open(os.path.join(".clarity", f"{project_name}.json"), "r") as f:
                project_data = json.load(f)
            print(f"Loaded existing project: {project_name}")
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Creating new project: {project_name}")
    else:
        print(f"Creating new project: {project_name}")
    
    # Initialize agent manager
    agent_manager = ClarificationAgentManager(
        project_name=project_name,
        project_data=project_data
    )
    
    # Process each node in sequence
    current_node = "Start"
    while current_node != "End":
        print(f"\n--- Processing: {current_node} ---")
        
        # Get node data
        node_data = agent_manager.process_node(current_node)
        
        # Display node information
        print(f"\n{node_data.get('title', current_node)}")
        print(node_data.get('description', ''))
        
        # Handle questions
        responses = {}
        if "questions" in node_data:
            for question in node_data["questions"]:
                prompt = question["question"]
                if "value" in question and question["value"]:
                    prompt += f" [Current: {question['value']}]"
                
                if question.get("type") == "select":
                    print(f"\n{prompt}")
                    for i, option in enumerate(question["options"]):
                        print(f"{i+1}. {option}")
                    
                    choice = input("Enter number: ")
                    try:
                        index = int(choice) - 1
                        if 0 <= index < len(question["options"]):
                            responses[question["id"]] = question["options"][index]
                        else:
                            responses[question["id"]] = choice
                    except ValueError:
                        responses[question["id"]] = choice
                
                elif question.get("type") == "multiselect":
                    print(f"\n{prompt}")
                    for i, option in enumerate(question["options"]):
                        print(f"{i+1}. {option}")
                    
                    choices = input("Enter numbers (comma-separated): ")
                    selected = []
                    for choice in choices.split(","):
                        try:
                            index = int(choice.strip()) - 1
                            if 0 <= index < len(question["options"]):
                                selected.append(question["options"][index])
                        except ValueError:
                            pass
                    
                    responses[question["id"]] = selected
                
                else:  # text input
                    if question.get("value"):
                        print(f"\n{prompt}")
                        print(f"Current value:\n{question['value']}")
                        change = input("Change? (y/n): ")
                        if change.lower() == "y":
                            print("Enter new value (empty line to finish):")
                            lines = []
                            while True:
                                line = input()
                                if line == "":
                                    break
                                lines.append(line)
                            responses[question["id"]] = "\n".join(lines)
                        else:
                            responses[question["id"]] = question["value"]
                    else:
                        print(f"\n{prompt}")
                        print("Enter value (empty line to finish):")
                        lines = []
                        while True:
                            line = input()
                            if line == "":
                                break
                            lines.append(line)
                        responses[question["id"]] = "\n".join(lines)
        
        # Process responses and get next node
        next_node = agent_manager.submit_responses(current_node, responses)
        current_node = next_node
    
    # Export all files
    print("\n--- Exporting Files ---")
    agent_manager.export_all()
    print("Files exported successfully!")
    print(f"\nProject planning complete for: {project_name}")
    print("Generated files:")
    print(f"  - .clarity/{project_name}.json")
    print("  - .plan.yml")
    print("  - README.md")
    print("  - architecture.md")

if __name__ == "__main__":
    main()