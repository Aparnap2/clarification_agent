"""Demo script for ProductDevelopmentOrchestrator workflow execution."""

import asyncio
import logging
import os
from dotenv import load_dotenv

from orchestrator import ProductDevelopmentOrchestrator

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def demo_workflow():
    """Demonstrate the complete workflow execution."""
    
    # Sample project ideas for testing
    test_queries = [
        "Build a project management tool for small teams that integrates with Slack and helps track deadlines",
        "Create an AI-powered personal finance app that helps users optimize their spending and savings",
        "Develop a marketplace for freelance graphic designers to connect with small businesses"
    ]
    
    # Initialize orchestrator
    orchestrator = ProductDevelopmentOrchestrator()
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"DEMO {i}: {query}")
        print(f"{'='*80}")
        
        try:
            # Execute workflow
            result_state = await orchestrator.execute_workflow(query)
            
            # Display results
            print(f"\nWorkflow completed for session: {result_state.session_id}")
            print(f"Current phase: {result_state.current_phase}")
            print(f"Validation score: {result_state.market_validation.get('overall_score', 'N/A')}")
            
            if result_state.business_model:
                print(f"Value proposition: {result_state.business_model.value_proposition}")
                print(f"Target customer: {result_state.business_model.target_customer}")
            
            print(f"Features generated: {len(result_state.feature_specifications)}")
            print(f"Research results: {len(result_state.research_data)}")
            
            if result_state.gtm_strategy:
                print(f"GTM channels: {len(result_state.gtm_strategy.distribution_channels)}")
            
            print(f"Roadmap phases: {len(result_state.mvp_roadmap)}")
            
            # Check for errors
            errors = [key for key in result_state.market_validation.keys() if 'error' in key.lower()]
            if errors:
                print(f"Errors encountered: {errors}")
            
            # Check if workflow was rejected
            if result_state.market_validation.get("workflow_status") == "rejected":
                print("⚠️  WORKFLOW REJECTED - Business validation failed")
                print("Rejection report available in market_validation")
            else:
                print("✅ WORKFLOW COMPLETED SUCCESSFULLY")
                
        except Exception as e:
            logger.error(f"Demo {i} failed: {e}")
            print(f"❌ DEMO FAILED: {e}")
        
        # Small delay between demos
        await asyncio.sleep(2)
    
    # Display session summary
    print(f"\n{'='*80}")
    print("SESSION SUMMARY")
    print(f"{'='*80}")
    
    sessions = orchestrator.list_sessions()
    print(f"Total sessions created: {len(sessions)}")
    
    for session_id, session_info in sessions.items():
        print(f"\nSession: {session_id[:8]}...")
        print(f"  Phase: {session_info.get('current_phase', 'unknown')}")
        print(f"  Query: {session_info.get('user_query', 'No query')[:60]}...")
        print(f"  Timestamp: {session_info.get('timestamp', 'Unknown')}")


async def demo_validation_gate():
    """Demonstrate the validation gate with a low-scoring project."""
    
    print(f"\n{'='*80}")
    print("VALIDATION GATE DEMO - Testing rejection scenario")
    print(f"{'='*80}")
    
    # This should score low and trigger rejection
    low_score_query = "Build another social media app like Facebook but with no clear differentiation"
    
    orchestrator = ProductDevelopmentOrchestrator()
    
    try:
        result_state = await orchestrator.execute_workflow(low_score_query)
        
        print(f"Session: {result_state.session_id}")
        print(f"Validation score: {result_state.market_validation.get('overall_score', 'N/A')}")
        print(f"Should continue: {result_state.market_validation.get('should_continue', 'N/A')}")
        print(f"Workflow status: {result_state.market_validation.get('workflow_status', 'unknown')}")
        
        if result_state.market_validation.get("workflow_status") == "rejected":
            print("✅ VALIDATION GATE WORKING - Project correctly rejected")
            rejection_report = result_state.market_validation.get("rejection_report", "No report")
            print(f"Rejection report length: {len(rejection_report)} characters")
        else:
            print("⚠️  VALIDATION GATE ISSUE - Project should have been rejected")
            
    except Exception as e:
        logger.error(f"Validation gate demo failed: {e}")
        print(f"❌ VALIDATION GATE DEMO FAILED: {e}")


async def main():
    """Main demo function."""
    print("ProductDevelopmentOrchestrator Demo")
    print("This demo will test the complete LangGraph workflow with multiple scenarios")
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment")
        print("The demo will still run but may fail at LLM calls")
    
    # Run main workflow demos
    await demo_workflow()
    
    # Run validation gate demo
    await demo_validation_gate()
    
    print(f"\n{'='*80}")
    print("DEMO COMPLETED")
    print(f"{'='*80}")


if __name__ == "__main__":
    asyncio.run(main())