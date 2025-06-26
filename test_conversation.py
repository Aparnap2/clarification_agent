#!/usr/bin/env python3
"""
Simple test script for the Clarification Agent.
"""
from clarification_agent.core.conversation_agent import ConversationAgent

def main():
    """Test the conversation agent"""
    print("Testing Clarification Agent...")
    
    # Initialize agent
    agent = ConversationAgent(project_name="test_project")
    
    # Get initial message
    response, is_complete = agent.process_user_input("")
    print(f"Agent: {response}\n")
    
    # Test with a sample conversation
    test_inputs = [
        "I want to build a task management app for teams",
        "Task creation, assignment, due dates, comments, and progress tracking",
        "Advanced analytics, mobile app, and integrations",
        "Small to medium teams who find existing tools too complex",
        "React, Node.js, MongoDB",
        "We need to support about 100 users initially",
        "The file structure looks good",
        "Creating tasks, viewing assigned tasks, updating status",
        "The tasks look good",
        "Task assignment and due dates must work correctly"
    ]
    
    for user_input in test_inputs:
        print(f"User: {user_input}\n")
        response, is_complete = agent.process_user_input(user_input)
        print(f"Agent: {response}\n")
        
        if is_complete:
            break
    
    print("Test complete!")

if __name__ == "__main__":
    main()