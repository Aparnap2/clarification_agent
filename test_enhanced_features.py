"""
Test script for enhanced clarification agent features.
Validates the modular components work correctly.
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_node_config():
    """Test node configuration loading."""
    print("Testing node configuration...")
    
    try:
        from clarification_agent.config.node_config import get_node_config_manager
        
        config_manager = get_node_config_manager()
        
        # Test basic functionality
        nodes = config_manager.get_all_nodes()
        print(f"✓ Loaded {len(nodes)} nodes")
        
        # Test specific node
        start_config = config_manager.get_node_config("start")
        print(f"✓ Start node: {start_config['label']} - {start_config['purpose']}")
        
        # Test node order
        node_order = config_manager.get_node_order()
        print(f"✓ Node order: {' -> '.join(node_order)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Node config test failed: {e}")
        return False


def test_clarity_validator():
    """Test clarity validation."""
    print("\nTesting clarity validator...")
    
    try:
        from clarification_agent.core.clarity_validator import ClarityValidator
        
        validator = ClarityValidator()
        
        # Test simple validation
        is_clear, score, feedback = validator.validate_response("start", "I want to build a task management app", {})
        print(f"✓ Validation result: clear={is_clear}, score={score:.2f}")
        
        # Test insufficient input
        is_clear, score, feedback = validator.validate_response("start", "app", {})
        print(f"✓ Short input validation: clear={is_clear}, feedback='{feedback}'")
        
        return True
        
    except Exception as e:
        print(f"✗ Clarity validator test failed: {e}")
        return False


def test_process_tracker():
    """Test process tracking."""
    print("\nTesting process tracker...")
    
    try:
        from clarification_agent.ui.process_tracker import ProcessTracker
        
        ProcessTracker.initialize()
        
        # Test logging
        ProcessTracker.log_llm_call("Test prompt", "Test response", "test-model")
        ProcessTracker.add_citation("https://example.com", "Test Title", "Test snippet")
        ProcessTracker.set_current_step("Testing")
        
        # Test stats
        stats = ProcessTracker.get_stats()
        print(f"✓ Process tracking stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"✗ Process tracker test failed: {e}")
        return False


def test_web_search():
    """Test web search helper."""
    print("\nTesting web search...")
    
    try:
        from clarification_agent.utils.web_search import WebSearchHelper
        
        search_helper = WebSearchHelper()
        
        # Test search (will use mock results if Crawl4AI not available)
        results = search_helper.search_for_context("React best practices", 1)
        print(f"✓ Search returned {len(results)} results")
        
        if results:
            print(f"✓ First result: {results[0]['title']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Web search test failed: {e}")
        return False


def test_animations():
    """Test animation components."""
    print("\nTesting animations...")
    
    try:
        from clarification_agent.ui.animations import inject_chat_animations, show_typing_indicator, create_animated_container
        
        # Test CSS generation
        css = inject_chat_animations()
        print("✓ Animation CSS generated")
        
        # Test typing indicator
        typing_html = show_typing_indicator("Testing...")
        print("✓ Typing indicator HTML generated")
        
        # Test animated container
        container_html = create_animated_container("Test content", is_active=True)
        print("✓ Animated container HTML generated")
        
        return True
        
    except Exception as e:
        print(f"✗ Animation test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Testing Enhanced Clarification Agent Components")
    print("=" * 50)
    
    tests = [
        test_node_config,
        test_clarity_validator,
        test_process_tracker,
        test_web_search,
        test_animations
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced features are working correctly.")
        print("\nTo run the enhanced app:")
        print("  streamlit run enhanced_app.py")
        print("  or")
        print("  ./run_enhanced_chat.sh")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
        print("\nYou can still run the basic app:")
        print("  streamlit run app.py")


if __name__ == "__main__":
    main()