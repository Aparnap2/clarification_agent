"""Demo script for GTM Strategy Agent functionality."""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.gtm_strategy_agent import GTMStrategyAgent
from models.data_models import BusinessModel, ProductState, FeatureSpec
from models.enums import MVPPriority, MarketValidationLevel


async def main():
    """Demonstrate GTM Strategy Agent functionality."""
    print("=== GTM Strategy Agent Demo ===\n")
    
    # Create sample business model
    business_model = BusinessModel(
        value_proposition="Streamline business processes for SMBs",
        target_customer="Small to medium businesses with 10-100 employees in service industries",
        revenue_streams=["Monthly subscription", "Professional services", "Training"],
        cost_structure=["Development", "Marketing", "Support", "Infrastructure"],
        key_metrics=["MRR", "CAC", "LTV", "Churn Rate", "NPS"]
    )
    
    # Create sample competitive analysis
    competitive_analysis = [
        {
            "competitor_name": "ProcessPro",
            "value_proposition": "Enterprise process automation platform",
            "target_market": "Large enterprises",
            "pricing_model": "$299/month per user",
            "key_strengths": ["Comprehensive features", "Enterprise integrations"],
            "market_gaps": ["Too complex for SMBs", "Expensive pricing"],
            "differentiation_opportunities": ["Simpler interface", "SMB-focused pricing"]
        },
        {
            "competitor_name": "WorkflowWiz",
            "value_proposition": "Simple workflow automation tool",
            "target_market": "Small businesses",
            "pricing_model": "$49/month flat rate",
            "key_strengths": ["Easy to use", "Affordable"],
            "market_gaps": ["Limited features", "No advanced analytics"],
            "differentiation_opportunities": ["More features", "Better analytics"]
        }
    ]
    
    # Create sample feature specifications
    feature_specs = [
        FeatureSpec(
            name="Process Designer",
            user_story="As a business owner, I want to design custom workflows, so that I can automate my specific processes",
            acceptance_criteria=[
                "WHEN user accesses designer THEN drag-and-drop interface SHALL be available",
                "WHEN user creates workflow THEN system SHALL validate process logic",
                "GIVEN valid workflow WHEN user saves THEN system SHALL store configuration"
            ],
            mvp_priority=MVPPriority.CORE,
            effort_estimate="L",
            business_impact="Critical",
            validation_level=MarketValidationLevel.ASSUMPTION,
            dependencies=[]
        ),
        FeatureSpec(
            name="Analytics Dashboard",
            user_story="As a manager, I want to see process performance metrics, so that I can optimize operations",
            acceptance_criteria=[
                "WHEN user views dashboard THEN key metrics SHALL be displayed",
                "WHEN process completes THEN metrics SHALL update automatically",
                "GIVEN time period WHEN user filters THEN relevant data SHALL be shown"
            ],
            mvp_priority=MVPPriority.CORE,
            effort_estimate="M",
            business_impact="High",
            validation_level=MarketValidationLevel.ASSUMPTION,
            dependencies=["Process Designer"]
        )
    ]
    
    # Create product state
    product_state = ProductState(
        user_query="Build a business process automation platform for SMBs",
        business_model=business_model,
        competitive_analysis=competitive_analysis,
        feature_specifications=feature_specs,
        current_phase="planning"
    )
    
    print("Initial Product State:")
    print(f"- Business Model: {business_model.value_proposition}")
    print(f"- Target Customer: {business_model.target_customer}")
    print(f"- Competitors: {len(competitive_analysis)} analyzed")
    print(f"- Features: {len(feature_specs)} specified")
    print()
    
    # Initialize GTM Strategy Agent
    # Note: In a real scenario, you would set your OpenAI API key
    # For demo purposes, we'll show what would happen
    try:
        gtm_agent = GTMStrategyAgent(api_key=os.getenv("OPENAI_API_KEY"))
        
        print("Developing GTM Strategy...")
        print("This would normally call the LLM to generate:")
        print("1. Distribution channels (3-5 specific channels)")
        print("2. Pricing strategy based on competitive analysis")
        print("3. Launch timeline with 3 phases")
        print("4. Success metrics and KPIs")
        print("5. Competitive positioning statement")
        print()
        
        # In a real scenario with API key:
        # result_state = await gtm_agent.develop_gtm_strategy(product_state)
        
        # For demo, show what the structure would look like
        print("Expected GTM Strategy Structure:")
        print("- Distribution Channels: ['Content Marketing', 'Direct Sales', 'Partner Network', 'Industry Events', 'Referral Program']")
        print("- Pricing Strategy: 'Subscription - $79/month'")
        print("- Launch Timeline:")
        print("  * mvp_launch: '8-12 weeks: Complete core features, Beta testing'")
        print("  * growth: '3-6 months: Scale customer acquisition, Feature expansion'")
        print("  * expansion: '6-12 months: Market expansion, Partnership development'")
        print("- Success Metrics: ['MRR growth of 25%', 'CAC under $150', 'LTV > 3x CAC', ...]")
        print("- Competitive Positioning: 'Unlike complex enterprise solutions, we deliver...'")
        print("- Budget Requirements: 'Medium investment required ($20K-50K) for initial 6-month GTM execution'")
        
    except Exception as e:
        print(f"Demo note: {e}")
        print("To run this demo with actual LLM calls, set your OPENAI_API_KEY environment variable.")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    asyncio.run(main())