#!/usr/bin/env python3
"""
Demo script showing GraphMemory functionality.

This script demonstrates how to use the GraphMemory class for session
management and state persistence in the AI Strategy Assistant.
"""

import sys
import os
from datetime import datetime

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory import GraphMemory
from models.data_models import ProductState, BusinessModel, FeatureSpec
from models.enums import MVPPriority


def main():
    """Demonstrate GraphMemory functionality."""
    print("=== AI Strategy Assistant - Memory Demo ===\n")
    
    # Initialize memory system
    print("1. Initializing GraphMemory...")
    memory = GraphMemory("demo_memory.pkl")
    print(f"   Memory initialized with path: {memory.memory_path}")
    
    # Generate session ID
    print("\n2. Generating session ID...")
    session_id = memory.generate_session_id()
    print(f"   Generated session ID: {session_id}")
    
    # Create sample product state
    print("\n3. Creating sample ProductState...")
    business_model = BusinessModel(
        value_proposition="AI-powered development assistant for faster coding",
        target_customer="Software developers and development teams",
        revenue_streams=["subscription", "enterprise_licenses"],
        key_metrics=["monthly_active_users", "code_completion_rate"]
    )
    
    feature_spec = FeatureSpec(
        name="Code Completion",
        user_story="As a developer, I want intelligent code completion, so that I can write code faster",
        acceptance_criteria=[
            "WHEN user types code THEN system SHALL provide relevant completions",
            "WHEN completion is selected THEN system SHALL insert correct code",
            "WHEN context changes THEN system SHALL update completion suggestions"
        ],
        mvp_priority=MVPPriority.CORE,
        effort_estimate="L",
        business_impact="Critical"
    )
    
    product_state = ProductState(
        user_query="Build an AI assistant that helps developers write code faster",
        business_model=business_model,
        feature_specifications=[feature_spec],
        current_phase="planning"
    )
    
    print(f"   Created ProductState with query: '{product_state.user_query}'")
    print(f"   Business model value prop: '{product_state.business_model.value_proposition}'")
    print(f"   Features: {len(product_state.feature_specifications)}")
    
    # Save session
    print("\n4. Saving session...")
    save_result = memory.save_session(session_id, product_state)
    print(f"   Save result: {'Success' if save_result else 'Failed'}")
    
    # List sessions
    print("\n5. Listing all sessions...")
    sessions = memory.list_sessions()
    for sid, info in sessions.items():
        print(f"   Session {sid[:8]}...")
        print(f"     Query: {info['user_query']}")
        print(f"     Phase: {info['current_phase']}")
        print(f"     Timestamp: {info['timestamp']}")
    
    # Load session
    print("\n6. Loading session...")
    loaded_state = memory.load_session(session_id)
    if loaded_state:
        print(f"   Loaded successfully!")
        print(f"   Query: '{loaded_state.user_query}'")
        print(f"   Phase: {loaded_state.current_phase}")
        print(f"   Features: {len(loaded_state.feature_specifications)}")
        print(f"   Session ID: {loaded_state.session_id}")
    else:
        print("   Failed to load session")
    
    # Update state and save again
    print("\n7. Updating state and saving...")
    if loaded_state:
        loaded_state.current_phase = "mvp_design"
        loaded_state.market_validation = {
            "problem_score": "8",
            "market_size": "Large",
            "competition": "Moderate"
        }
        
        update_result = memory.save_session(session_id, loaded_state)
        print(f"   Update result: {'Success' if update_result else 'Failed'}")
    
    # Get memory statistics
    print("\n8. Memory statistics...")
    stats = memory.get_memory_stats()
    print(f"   Total sessions: {stats['total_sessions']}")
    print(f"   Memory file size: {stats['memory_file_size']} bytes")
    print(f"   Oldest session: {stats['oldest_session']}")
    print(f"   Newest session: {stats['newest_session']}")
    
    # Demonstrate backward compatibility
    print("\n9. Testing backward compatibility...")
    # Simulate old format data
    old_session_id = memory.generate_session_id()
    old_session_data = {
        'state': {
            'user_query': 'Legacy project idea',
            'current_phase': 'discovery'
            # Missing newer fields like session_id, research_data, etc.
        },
        'timestamp': datetime.now(),
        'version': '0.9'
    }
    
    # Manually add to memory to simulate old data
    memory.memory[old_session_id] = old_session_data
    
    # Try to load - should handle missing fields gracefully
    legacy_state = memory.load_session(old_session_id)
    if legacy_state:
        print(f"   Legacy session loaded successfully!")
        print(f"   Query: '{legacy_state.user_query}'")
        print(f"   Session ID: {legacy_state.session_id}")
        print(f"   Research data: {legacy_state.research_data}")
    else:
        print("   Failed to load legacy session")
    
    print("\n=== Demo completed successfully! ===")
    print(f"\nMemory file created at: {memory.memory_path}")
    print("You can inspect the pickle file or run this demo again to see persistence in action.")


if __name__ == "__main__":
    main()