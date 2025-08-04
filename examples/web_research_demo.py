"""Demo script for WebResearchAgent functionality."""

import asyncio
import json
import sys
import os

# Add parent directory to path to import agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import WebResearchAgent


async def demo_web_research():
    """Demonstrate WebResearchAgent capabilities."""
    print("🔍 WebResearchAgent Demo")
    print("=" * 50)
    
    # Initialize the agent
    async with WebResearchAgent(max_concurrent_crawls=3, timeout=10) as agent:
        print("✅ WebResearchAgent initialized")
        
        # Demo 1: Basic research topic
        print("\n📊 Demo 1: Basic Research Topic")
        print("-" * 30)
        
        try:
            results = await agent.research_topic(
                query="e-commerce platform market analysis",
                urls=["https://httpbin.org/json"]  # Using a test URL that returns JSON
            )
            
            print(f"Research completed: {len(results)} results")
            for i, result in enumerate(results, 1):
                print(f"  {i}. URL: {result['url']}")
                print(f"     Success: {result['success']}")
                print(f"     Title: {result['title']}")
                if result['success']:
                    print(f"     Content preview: {result['content'][:100]}...")
                else:
                    print(f"     Error: {result['error_message']}")
                print()
                
        except Exception as e:
            print(f"❌ Research failed: {e}")
        
        # Demo 2: Competitor analysis
        print("\n🏢 Demo 2: Competitor Data Extraction")
        print("-" * 40)
        
        try:
            competitors = await agent.extract_competitor_data([
                "https://httpbin.org/html",  # Test URL
                "https://httpbin.org/json"   # Another test URL
            ])
            
            print(f"Competitor analysis completed: {len(competitors)} competitors")
            for i, competitor in enumerate(competitors, 1):
                print(f"  {i}. Company: {competitor.company_name}")
                print(f"     URL: {competitor.url}")
                print(f"     Value Prop: {competitor.value_proposition}")
                print(f"     Pricing: {competitor.pricing_info}")
                print(f"     Features: {len(competitor.key_features)} features")
                print()
                
        except Exception as e:
            print(f"❌ Competitor analysis failed: {e}")
        
        # Demo 3: Market trends analysis
        print("\n📈 Demo 3: Market Trends Analysis")
        print("-" * 35)
        
        try:
            trends = await agent.analyze_market_trends(
                industry="AI technology",
                trend_urls=["https://httpbin.org/json"]  # Test URL
            )
            
            print(f"Market trends analysis completed: {len(trends)} trends")
            for i, trend in enumerate(trends, 1):
                print(f"  {i}. Industry: {trend.industry}")
                print(f"     Trend: {trend.trend_title}")
                print(f"     Impact: {trend.impact_level}")
                print(f"     Timeline: {trend.time_horizon}")
                print(f"     Description: {trend.trend_description[:100]}...")
                print()
                
        except Exception as e:
            print(f"❌ Market trends analysis failed: {e}")
        
        # Demo 4: URL generation
        print("\n🔗 Demo 4: Research URL Generation")
        print("-" * 35)
        
        urls = agent._generate_research_urls("fintech startup")
        print(f"Generated {len(urls)} research URLs for 'fintech startup':")
        for i, url in enumerate(urls, 1):
            print(f"  {i}. {url}")
        
        print("\n✅ Demo completed successfully!")


async def demo_error_handling():
    """Demonstrate error handling capabilities."""
    print("\n🛡️  Error Handling Demo")
    print("=" * 30)
    
    async with WebResearchAgent(timeout=1) as agent:  # Very short timeout
        print("Testing error handling with invalid URLs...")
        
        results = await agent.research_topic(
            query="test error handling",
            urls=[
                "https://invalid-url-that-does-not-exist.com",
                "https://httpbin.org/delay/5",  # Will timeout
                "https://httpbin.org/status/404"  # 404 error
            ]
        )
        
        print(f"Results: {len(results)} (with graceful error handling)")
        for i, result in enumerate(results, 1):
            status = "✅ Success" if result['success'] else "❌ Failed"
            print(f"  {i}. {status}: {result['url']}")
            if not result['success']:
                print(f"     Error: {result['error_message']}")


if __name__ == "__main__":
    print("Starting WebResearchAgent demonstrations...")
    
    # Run the main demo
    asyncio.run(demo_web_research())
    
    # Run error handling demo
    asyncio.run(demo_error_handling())
    
    print("\n🎉 All demonstrations completed!")