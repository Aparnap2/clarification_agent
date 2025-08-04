"""Demo script for Business Process Analysis (BPA) Agent."""

import asyncio
import os
from dotenv import load_dotenv

from agents.bpa_agent import BPAAgent
from models.data_models import ProductState

# Load environment variables
load_dotenv()


async def demo_bpa_agent():
    """Demonstrate BPA Agent functionality."""
    print("🚀 BPA Agent Demo")
    print("=" * 50)
    
    # Create a sample project idea
    project_idea = """
    Build an AI-powered code review assistant that automatically analyzes pull requests,
    identifies potential bugs, suggests improvements, and learns from team preferences.
    Target developers and engineering teams who want to improve code quality and reduce
    review time while maintaining high standards.
    """
    
    print(f"📝 Project Idea: {project_idea.strip()}")
    print("\n" + "=" * 50)
    
    # Initialize BPA Agent
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ Error: OPENROUTER_API_KEY environment variable not set")
        print("Please set your OpenRouter API key to run this demo")
        return
    
    bpa_agent = BPAAgent(api_key=api_key)
    
    # Create initial product state
    initial_state = ProductState(
        user_query=project_idea.strip(),
        session_id="demo-session",
        current_phase="discovery"
    )
    
    print("🔍 Starting Business Process Analysis...")
    print("-" * 30)
    
    try:
        # Run business viability analysis
        result_state = await bpa_agent.analyze_business_viability(initial_state)
        
        # Display results
        print("\n📊 VALIDATION RESULTS:")
        print("-" * 30)
        
        if "overall_score" in result_state.market_validation:
            score = float(result_state.market_validation["overall_score"])
            print(f"Overall Score: {score}/10")
            print(f"Should Continue: {result_state.market_validation.get('should_continue', 'Unknown')}")
            
            if score >= 7.0:
                print("✅ Project passed validation gate!")
            else:
                print("❌ Project failed validation gate (score < 7)")
                
            print(f"\nReasoning: {result_state.market_validation.get('reasoning', 'N/A')}")
        
        # Display business model if generated
        if result_state.business_model:
            print("\n💼 BUSINESS MODEL:")
            print("-" * 30)
            print(f"Value Proposition: {result_state.business_model.value_proposition}")
            print(f"Target Customer: {result_state.business_model.target_customer}")
            print(f"Revenue Streams: {', '.join(result_state.business_model.revenue_streams)}")
            print(f"Key Metrics: {', '.join(result_state.business_model.key_metrics)}")
        
        # Display competitive analysis
        if result_state.competitive_analysis:
            print(f"\n🏆 COMPETITIVE ANALYSIS ({len(result_state.competitive_analysis)} competitors):")
            print("-" * 30)
            for i, comp in enumerate(result_state.competitive_analysis[:2], 1):  # Show first 2
                print(f"{i}. {comp.get('competitor_name', 'Unknown')}")
                print(f"   Value Prop: {comp.get('value_proposition', 'N/A')}")
                if comp.get('market_gaps'):
                    print(f"   Market Gaps: {', '.join(comp['market_gaps'][:2])}")
                print()
        
        # Display MVP features
        if result_state.feature_specifications:
            print(f"\n🎯 MVP FEATURES ({len(result_state.feature_specifications)} features):")
            print("-" * 30)
            
            # Group by priority
            core_features = [f for f in result_state.feature_specifications if f.mvp_priority.value == "core"]
            important_features = [f for f in result_state.feature_specifications if f.mvp_priority.value == "important"]
            
            if core_features:
                print("🔥 CORE Features:")
                for feature in core_features:
                    print(f"  • {feature.name} ({feature.effort_estimate}, {feature.business_impact} impact)")
                    print(f"    Story: {feature.user_story}")
                    print()
            
            if important_features:
                print("⭐ IMPORTANT Features:")
                for feature in important_features[:2]:  # Show first 2
                    print(f"  • {feature.name} ({feature.effort_estimate}, {feature.business_impact} impact)")
                    print(f"    Story: {feature.user_story}")
                    print()
        
        print(f"\n📈 Current Phase: {result_state.current_phase}")
        print(f"🕒 Analysis completed at: {result_state.updated_at}")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        print("This might be due to API connectivity or configuration issues.")


if __name__ == "__main__":
    asyncio.run(demo_bpa_agent())