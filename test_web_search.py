#!/usr/bin/env python3
"""
Test script for the web search functionality
"""
import asyncio
import json
import logging
from web_search_app import WebSearchTool, EnhancedConversationAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_web_search():
    """Test the web search functionality"""
    print("🔍 Testing Web Search Tool...")
    print("=" * 50)
    
    # Initialize web search tool
    search_tool = WebSearchTool()
    
    # Test queries
    test_queries = [
        "Python web frameworks 2024",
        "React vs Vue.js comparison",
        "Docker best practices",
        "Machine learning tutorials"
    ]
    
    for query in test_queries:
        print(f"\n🔎 Searching for: '{query}'")
        print("-" * 30)
        
        try:
            # Perform search
            results = await search_tool.search_web(query, engine="duckduckgo", max_results=3)
            
            # Display results
            print(f"Query: {results['query']}")
            print(f"Engine: {results['engine']}")
            print(f"Results found: {len(results['results'])}")
            print(f"Timestamp: {results['timestamp']}")
            
            if results['results']:
                print("\nResults:")
                for i, result in enumerate(results['results'], 1):
                    print(f"  {i}. {result['title']}")
                    print(f"     URL: {result['url']}")
                    print(f"     Content: {result['content'][:100]}...")
                    print()
                
                print("Citations:")
                for citation in results['citations']:
                    print(f"  - {citation}")
            else:
                print("No results found.")
                
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print("\n" + "=" * 50)

async def test_enhanced_agent():
    """Test the enhanced conversation agent"""
    print("\n🤖 Testing Enhanced Conversation Agent...")
    print("=" * 50)
    
    # Initialize enhanced agent
    agent = EnhancedConversationAgent("test_project")
    
    # Test inputs that should trigger search
    test_inputs = [
        "What are the latest Python web frameworks?",
        "I want to build a modern web app with the best practices",
        "Can you help me compare React and Vue.js?",
        "What are the current trends in machine learning?"
    ]
    
    for user_input in test_inputs:
        print(f"\n👤 User: {user_input}")
        print("-" * 30)
        
        try:
            response, is_complete, search_results = await agent.process_user_input_with_search(
                user_input, enable_search=True
            )
            
            print(f"🤖 Agent: {response[:200]}...")
            print(f"Complete: {is_complete}")
            
            if search_results:
                print(f"Search performed: {search_results['query']}")
                print(f"Results found: {len(search_results['results'])}")
            else:
                print("No search performed")
                
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print("\n" + "=" * 50)

async def main():
    """Main test function"""
    print("🧪 Web Search App Test Suite")
    print("=" * 50)
    
    # Test web search tool
    await test_web_search()
    
    # Test enhanced agent
    await test_enhanced_agent()
    
    print("\n✅ Tests completed!")

if __name__ == "__main__":
    asyncio.run(main())