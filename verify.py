#!/usr/bin/env python3
"""
Verification script for the Clarification Agent.
This script tests the basic functionality to ensure everything works.
"""
import os
import sys
from clarification_agent.core.conversation_agent import ConversationAgent
from clarification_agent.utils.llm_helper import LLMHelper

def main():
    """Run verification tests"""
    print("Running verification tests...")
    
    # Create .clarity directory if it doesn't exist
    os.makedirs(".clarity", exist_ok=True)
    
    # Test 1: Create LLMHelper
    print("\nTest 1: Creating LLMHelper...")
    try:
        llm = LLMHelper()
        print("✅ LLMHelper created successfully")
    except Exception as e:
        print(f"❌ Error creating LLMHelper: {str(e)}")
        return
    
    # Test 2: Generate suggestions
    print("\nTest 2: Generating suggestions...")
    try:
        suggestion = llm.generate_suggestions("Test prompt", {"description": "Test description"})
        print(f"✅ Generated suggestion: {suggestion[:50]}...")
    except Exception as e:
        print(f"❌ Error generating suggestions: {str(e)}")
        return
    
    # Test 3: Generate file structure
    print("\nTest 3: Generating file structure...")
    try:
        file_structure = llm.generate_file_structure({"tech_stack": ["React", "Node.js"]})
        print(f"✅ Generated file structure with {len(file_structure)} files")
    except Exception as e:
        print(f"❌ Error generating file structure: {str(e)}")
        return
    
    # Test 4: Generate tasks
    print("\nTest 4: Generating tasks...")
    try:
        tasks = llm.generate_tasks({"mvp_features": ["Feature 1", "Feature 2"]})
        print(f"✅ Generated {len(tasks)} tasks")
    except Exception as e:
        print(f"❌ Error generating tasks: {str(e)}")
        return
    
    # Test 5: Create ConversationAgent
    print("\nTest 5: Creating ConversationAgent...")
    try:
        agent = ConversationAgent(project_name="test_project")
        print("✅ ConversationAgent created successfully")
    except Exception as e:
        print(f"❌ Error creating ConversationAgent: {str(e)}")
        return
    
    # Test 6: Process user input
    print("\nTest 6: Processing user input...")
    try:
        response, is_complete = agent.process_user_input("")
        print(f"✅ Processed empty input, response: {response[:50]}...")
    except Exception as e:
        print(f"❌ Error processing user input: {str(e)}")
        return
    
    print("\nAll tests passed! The Clarification Agent is working correctly.")

if __name__ == "__main__":
    main()