#!/usr/bin/env python3
"""
Test script for beautiful agent activity logging
"""
import asyncio
import time
import json
from agent_activity_logger import AgentActivityLogger, ActivityType, ActivityContext
from enhanced_web_search_app import SuperEnhancedConversationAgent

async def demo_beautiful_activities():
    """Demonstrate beautiful activity logging with various scenarios"""
    print("🎨 Testing Beautiful Agent Activity Logging")
    print("=" * 60)
    
    # Initialize activity logger
    logger = AgentActivityLogger()
    
    # Demo 1: Thinking Process
    print("\n1. 🤔 Simulating Thinking Process...")
    thinking_id = logger.start_activity(
        ActivityType.THINKING,
        "🤔 Analyzing User Request",
        "Processing complex user query about web frameworks"
    )
    
    await asyncio.sleep(1)
    
    logger.update_activity(
        thinking_id,
        description="Identifying key concepts and search requirements",
        details={"concepts_found": ["web frameworks", "performance", "2024"], "complexity": "medium"}
    )
    
    await asyncio.sleep(1)
    
    logger.complete_activity(
        thinking_id,
        "Analysis complete - proceeding with web search",
        {"decision": "perform_search", "confidence": 0.95}
    )
    
    # Demo 2: Web Search with Multiple Steps
    print("\n2. 🔍 Simulating Web Search Process...")
    search_id = logger.start_activity(
        ActivityType.SEARCH,
        "🔍 Web Search: Python frameworks 2024",
        "Initializing search with DuckDuckGo"
    )
    
    await asyncio.sleep(0.5)
    
    # Simulate crawler activities
    crawler_activities = []
    for i in range(3):
        crawler_id = logger.start_activity(
            ActivityType.TOOL_CALL,
            f"🕷️ Web Crawler #{i+1}",
            f"Crawling result page {i+1}"
        )
        crawler_activities.append(crawler_id)
        
        await asyncio.sleep(0.3)
        
        logger.complete_activity(
            crawler_id,
            f"Successfully crawled page {i+1}",
            {
                "url": f"https://example{i+1}.com/python-frameworks",
                "content_length": 1024 + i * 512,
                "title": f"Top Python Frameworks {2024 - i}"
            }
        )
    
    logger.complete_activity(
        search_id,
        "Search completed successfully",
        {"results_found": 3, "total_time": 2.1}
    )
    
    # Demo 3: LLM Generation Process
    print("\n3. 🧠 Simulating LLM Generation...")
    llm_id = logger.start_activity(
        ActivityType.GENERATION,
        "🧠 LLM Response Generation",
        "Generating comprehensive response with search results"
    )
    
    await asyncio.sleep(1.5)
    
    logger.update_activity(
        llm_id,
        description="Integrating search results with knowledge base",
        details={"tokens_processed": 2048, "context_length": 4096}
    )
    
    await asyncio.sleep(1)
    
    logger.complete_activity(
        llm_id,
        "Response generated successfully",
        {
            "response_length": 1250,
            "sources_integrated": 3,
            "confidence_score": 0.92
        }
    )
    
    # Demo 4: Analysis and Enhancement
    print("\n4. 📊 Simulating Analysis Process...")
    analysis_id = logger.start_activity(
        ActivityType.ANALYSIS,
        "📊 Response Enhancement",
        "Analyzing and enhancing response with citations"
    )
    
    await asyncio.sleep(0.8)
    
    logger.complete_activity(
        analysis_id,
        "Response enhanced with 3 citations",
        {"citations_added": 3, "enhancement_type": "source_integration"}
    )
    
    # Demo 5: Error Scenario
    print("\n5. ❌ Simulating Error Scenario...")
    error_id = logger.start_activity(
        ActivityType.TOOL_CALL,
        "🔧 External API Call",
        "Attempting to fetch additional data"
    )
    
    await asyncio.sleep(0.5)
    
    logger.fail_activity(
        error_id,
        "API call failed: Connection timeout",
        {"error_code": "TIMEOUT", "retry_count": 3, "endpoint": "api.example.com"}
    )
    
    # Demo 6: Complex Tool Call
    print("\n6. 🔧 Simulating Complex Tool Call...")
    tool_id = logger.log_tool_call(
        "document_generator",
        {
            "template": "project_readme",
            "data": {"name": "MyProject", "features": ["auth", "api", "ui"]},
            "format": "markdown"
        },
        result={
            "file_path": "README.md",
            "size_bytes": 2048,
            "sections": ["overview", "features", "installation", "usage"]
        }
    )
    
    print("\n✅ Beautiful activity logging demo completed!")
    print(f"Total activities logged: {len(logger.activity_logs) if hasattr(logger, 'activity_logs') else 'N/A'}")

async def demo_context_manager():
    """Demonstrate the activity context manager"""
    print("\n🔄 Testing Activity Context Manager...")
    print("-" * 40)
    
    logger = AgentActivityLogger()
    
    # Successful operation
    with ActivityContext(
        logger,
        ActivityType.ANALYSIS,
        "📈 Data Processing",
        "Processing user data with context manager"
    ) as activity:
        await asyncio.sleep(1)
        activity.update(
            "Processing 50% complete",
            {"progress": 0.5, "items_processed": 500}
        )
        await asyncio.sleep(1)
        activity.update(
            "Processing 100% complete",
            {"progress": 1.0, "items_processed": 1000}
        )
    
    # Failed operation
    try:
        with ActivityContext(
            logger,
            ActivityType.TOOL_CALL,
            "⚠️ Risky Operation",
            "Attempting operation that might fail"
        ) as activity:
            await asyncio.sleep(0.5)
            activity.update("Performing risky calculation...")
            raise ValueError("Simulated error for demo")
    except ValueError:
        pass  # Error automatically logged by context manager
    
    print("✅ Context manager demo completed!")

async def demo_real_conversation():
    """Demonstrate with a real conversation agent"""
    print("\n🤖 Testing with Real Conversation Agent...")
    print("-" * 50)
    
    try:
        # Initialize enhanced agent
        agent = SuperEnhancedConversationAgent("demo_project")
        
        # Test queries that will trigger various activities
        test_queries = [
            "What are the latest React alternatives for 2024?",
            "I need help choosing between FastAPI and Django",
            "Can you help me plan a modern web application?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Testing query: '{query}'")
            
            try:
                response, is_complete, search_results = await agent.process_user_input_with_logging(
                    query, enable_search=True
                )
                
                print(f"   ✅ Response generated (length: {len(response)})")
                if search_results:
                    print(f"   🔍 Search results: {len(search_results.get('results', []))} found")
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        print("\n✅ Real conversation demo completed!")
        
    except ImportError as e:
        print(f"⚠️ Skipping real conversation demo: {e}")

def demo_activity_types():
    """Demonstrate all activity types and their visual styles"""
    print("\n🎨 Demonstrating All Activity Types...")
    print("-" * 45)
    
    logger = AgentActivityLogger()
    
    activity_demos = [
        (ActivityType.THINKING, "🤔 Deep Thought Process", "Contemplating the meaning of code"),
        (ActivityType.TOOL_CALL, "🔧 API Integration", "Calling external service"),
        (ActivityType.SEARCH, "🔍 Knowledge Discovery", "Searching for latest information"),
        (ActivityType.ANALYSIS, "📊 Data Analysis", "Analyzing patterns and trends"),
        (ActivityType.GENERATION, "🧠 Content Creation", "Generating intelligent response"),
        (ActivityType.ERROR, "❌ Error Handling", "Managing unexpected situation"),
        (ActivityType.SUCCESS, "✅ Task Completion", "Successfully completed operation"),
        (ActivityType.INFO, "ℹ️ Information", "Providing helpful context")
    ]
    
    for activity_type, title, description in activity_demos:
        activity_id = logger.start_activity(activity_type, title, description)
        
        # Simulate some work
        time.sleep(0.1)
        
        # Complete with relevant details
        details = {
            "demo": True,
            "activity_type": activity_type.value,
            "visual_test": "success"
        }
        
        if activity_type == ActivityType.ERROR:
            logger.fail_activity(activity_id, "Simulated error for visual testing", details)
        else:
            logger.complete_activity(activity_id, f"{title} completed successfully", details)
    
    print("✅ All activity types demonstrated!")

async def main():
    """Main demo function"""
    print("🎨 Beautiful Agent Activity Logging Demo")
    print("=" * 60)
    print("This demo showcases the beautiful UI for agent activity tracking")
    print("=" * 60)
    
    # Run all demos
    await demo_beautiful_activities()
    await demo_context_manager()
    demo_activity_types()
    await demo_real_conversation()
    
    print("\n" + "=" * 60)
    print("🎉 All demos completed successfully!")
    print("Run the enhanced_web_search_app.py to see the beautiful UI in action!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())