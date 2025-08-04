"""Demo script for ProductTransitionAgent usage."""

import asyncio
import json
import os
from datetime import datetime

from agents.product_transition_agent import ProductTransitionAgent
from models.data_models import BusinessModel, FeatureSpec, GTMStrategy, ProductState
from models.enums import MVPPriority, MarketValidationLevel


async def demo_product_transition_agent():
    """Demonstrate ProductTransitionAgent functionality."""
    print("=== Product Transition Agent Demo ===\n")
    
    # Initialize the agent
    agent = ProductTransitionAgent(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="openai/gpt-4o-mini"
    )
    
    # Create sample business model
    business_model = BusinessModel(
        value_proposition="Streamline business processes with AI automation",
        target_customer="Small to medium businesses in professional services",
        revenue_streams=["Monthly subscription", "Professional services", "Enterprise licenses"],
        cost_structure=["Development", "Marketing", "Customer support", "Infrastructure"],
        key_metrics=["Monthly Recurring Revenue", "Customer Acquisition Cost", "Customer Lifetime Value", "Churn Rate"]
    )
    
    # Create sample feature specifications
    feature_specs = [
        FeatureSpec(
            name="User Authentication & Authorization",
            user_story="As a business user, I want to securely access the platform, so that my data is protected",
            acceptance_criteria=[
                "WHEN user provides valid credentials THEN system SHALL authenticate successfully",
                "WHEN user session expires THEN system SHALL require re-authentication",
                "GIVEN user permissions WHEN accessing features THEN system SHALL enforce authorization"
            ],
            mvp_priority=MVPPriority.CORE,
            effort_estimate="S",
            business_impact="High",
            validation_level=MarketValidationLevel.ASSUMPTION
        ),
        FeatureSpec(
            name="Process Automation Dashboard",
            user_story="As a business owner, I want to view automated processes, so that I can monitor efficiency gains",
            acceptance_criteria=[
                "WHEN user accesses dashboard THEN system SHALL display active automations",
                "WHEN automation completes THEN dashboard SHALL update status in real-time",
                "GIVEN automation errors WHEN viewing dashboard THEN system SHALL highlight issues"
            ],
            mvp_priority=MVPPriority.CORE,
            effort_estimate="M",
            business_impact="Critical",
            validation_level=MarketValidationLevel.ASSUMPTION
        ),
        FeatureSpec(
            name="Advanced Analytics & Reporting",
            user_story="As a manager, I want detailed analytics, so that I can make data-driven decisions",
            acceptance_criteria=[
                "WHEN user requests report THEN system SHALL generate within 30 seconds",
                "WHEN viewing analytics THEN system SHALL provide drill-down capabilities",
                "GIVEN time period selection WHEN generating reports THEN system SHALL filter data accordingly"
            ],
            mvp_priority=MVPPriority.IMPORTANT,
            effort_estimate="L",
            business_impact="Medium",
            validation_level=MarketValidationLevel.ASSUMPTION
        )
    ]
    
    # Create sample GTM strategy
    gtm_strategy = GTMStrategy(
        distribution_channels=["Direct sales", "Content marketing", "Partner network", "Industry conferences"],
        pricing_strategy="Tiered subscription - Starting at $99/month",
        launch_timeline={
            "mvp_launch": "10 weeks: Core features, Beta testing, Initial customers",
            "growth": "4 months: Scale acquisition, Feature expansion, Channel optimization",
            "expansion": "8 months: Market expansion, Strategic partnerships, Product diversification"
        },
        success_metrics=["MRR growth 25%", "CAC < $150", "LTV > $1500", "NPS > 60", "Churn < 5%"],
        competitive_positioning="Premium automation solution with superior user experience",
        budget_requirements="$75K initial investment for development and marketing"
    )
    
    # Create product state
    product_state = ProductState(
        user_query="Build an AI-powered business process automation platform for SMBs",
        business_model=business_model,
        feature_specifications=feature_specs,
        gtm_strategy=gtm_strategy,
        current_phase="planning"
    )
    
    print("Initial Product State:")
    print(f"- User Query: {product_state.user_query}")
    print(f"- Business Model: {product_state.business_model.value_proposition}")
    print(f"- Features: {len(product_state.feature_specifications)} specifications")
    print(f"- GTM Strategy: {len(product_state.gtm_strategy.distribution_channels)} channels")
    print(f"- Current Phase: {product_state.current_phase}")
    print()
    
    try:
        print("Generating 3-phase product roadmap...")
        updated_state = await agent.generate_product_roadmap(product_state)
        
        print(f"✅ Roadmap generation completed!")
        print(f"- Updated Phase: {updated_state.current_phase}")
        print(f"- Roadmap Phases: {len(updated_state.mvp_roadmap)}")
        print()
        
        # Display roadmap phases
        print("=== PRODUCT ROADMAP ===")
        for i, phase in enumerate(updated_state.mvp_roadmap, 1):
            print(f"\n{i}. {phase['phase_name']} ({phase['timeline']})")
            print(f"   Description: {phase['description']}")
            print(f"   Key Features: {', '.join(phase['key_features'][:3])}")
            print(f"   Success Criteria:")
            for criterion in phase['success_criteria'][:3]:
                print(f"     • {criterion}")
            print(f"   Key Learnings:")
            for learning in phase['key_learnings'][:2]:
                print(f"     • {learning}")
        
        # Display execution checklist
        if "execution_checklist" in updated_state.market_validation:
            print("\n=== EXECUTION CHECKLIST ===")
            checklist_data = json.loads(updated_state.market_validation["execution_checklist"])
            total_items = 0
            
            for category_data in checklist_data:
                print(f"\n{category_data['category']} ({category_data['priority']} Priority)")
                print(f"Responsible: {category_data['responsible_role']}")
                for item in category_data['validation_items']:
                    print(f"  ☐ {item}")
                    total_items += 1
            
            print(f"\nTotal Validation Items: {total_items}")
        
        # Get roadmap summary
        summary = agent.get_roadmap_summary(updated_state)
        print(f"\n=== ROADMAP SUMMARY ===")
        print(f"Total Phases: {summary['total_phases']}")
        if 'execution_checklist' in summary:
            print(f"Checklist Categories: {summary['execution_checklist']['categories']}")
            print(f"Total Validation Items: {summary['execution_checklist']['total_validation_items']}")
        
        print("\n✅ Product Transition Agent demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during roadmap generation: {e}")
        return False
    
    return True


if __name__ == "__main__":
    # Run the demo
    success = asyncio.run(demo_product_transition_agent())
    if success:
        print("\n🎉 Demo completed successfully!")
    else:
        print("\n💥 Demo failed!")