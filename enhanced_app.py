"""
Enhanced Clarification Agent with robust node configuration and improved visualizations.
Modular architecture that extends existing functionality without code duplication.
"""
import streamlit as st
import time
from clarification_agent.core.conversation_agent import ConversationAgent
from clarification_agent.core.clarity_validator import ClarityValidator
from clarification_agent.config.node_config import get_node_config_manager
from clarification_agent.ui.animations import inject_chat_animations, show_typing_indicator, create_animated_container
from clarification_agent.ui.process_tracker import ProcessTracker
from clarification_agent.ui.visualizations import render_enhanced_workflow_sidebar, render_enhanced_process_details, render_project_completion_summary
from clarification_agent.utils.web_search import WebSearchHelper


def initialize_enhanced_session_state():
    """Initialize session state with enhanced features."""
    config_manager = get_node_config_manager()
    workflow_config = config_manager.get_workflow_config()
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "agent" not in st.session_state:
        st.session_state.agent = None
        st.session_state.project_name = None
        st.session_state.complete = False
        st.session_state.current_node = workflow_config.get("start_node", "start")
        st.session_state.completed_nodes = set()
        st.session_state.current_node_started = False
    
    ProcessTracker.initialize()
    
    if "web_search" not in st.session_state:
        st.session_state.web_search = WebSearchHelper()
    
    if "clarity_validator" not in st.session_state:
        st.session_state.clarity_validator = ClarityValidator()
    
    if "config_manager" not in st.session_state:
        st.session_state.config_manager = config_manager


def get_current_node_config():
    """Get current node configuration."""
    return st.session_state.config_manager.get_node_config(st.session_state.current_node)


def process_user_input_enhanced(user_input: str):
    """Enhanced user input processing with validation and tracking."""
    current_node_config = get_current_node_config()
    
    ProcessTracker.set_current_step(f"Processing {current_node_config['label']}")
    
    typing_placeholder = st.empty()
    typing_placeholder.markdown(show_typing_indicator(f"Processing {current_node_config['label']}..."), unsafe_allow_html=True)
    
    try:
        # Enhanced clarity validation
        is_clear, clarity_score, feedback = st.session_state.clarity_validator.validate_response(
            st.session_state.current_node, 
            user_input,
            context={"project_name": st.session_state.project_name}
        )
        
        if not is_clear:
            typing_placeholder.empty()
            return feedback, False
        
        # Process with existing agent
        agent_response, is_complete = st.session_state.agent.process_user_input(user_input)
        
        # Log interaction
        ProcessTracker.log_llm_call(
            prompt=f"Node: {current_node_config['label']}, Input: {user_input}",
            response=agent_response
        )
        
        # Optional web search
        if current_node_config.get("web_search", False) and st.session_state.get("enable_web_search", False):
            search_template = current_node_config.get("search_query", "{project_name} {node_label}")
            search_query = search_template.format(
                project_name=st.session_state.project_name,
                node_label=current_node_config['label'].lower()
            )
            search_results = st.session_state.web_search.search_for_context(search_query, 1)
            
            for result in search_results:
                ProcessTracker.add_citation(result["url"], result["title"], result["snippet"])
        
        typing_placeholder.empty()
        
        # Enhanced completion logic
        enhanced_is_complete = is_complete or clarity_score > 0.8
        
        return agent_response, enhanced_is_complete
        
    except Exception as e:
        typing_placeholder.empty()
        st.error(f"Error: {str(e)}")
        return "I encountered an error. Please try again.", False


def main():
    """Enhanced main function with modular components."""
    st.set_page_config(
        page_title="Enhanced Clarification Agent",
        page_icon="🧠",
        layout="wide"
    )
    
    inject_chat_animations()
    
    st.title("🧠 Enhanced Clarification Agent")
    st.write("Project clarification with robust node configuration and enhanced visualizations.")
    
    initialize_enhanced_session_state()
    
    # Sidebar
    with st.sidebar:
        st.header("📂 Project Setup")
        
        with st.expander("Project Configuration", expanded=not bool(st.session_state.project_name)):
            project_action = st.radio("Choose an action:", ["Create New Project", "Load Existing Project"])
            
            if project_action == "Create New Project":
                project_name = st.text_input("Project Name:")
                enable_web_search = st.checkbox("Enable web search for enhanced suggestions", value=False)
                
                if st.button("Start Enhanced Project") and project_name:
                    st.session_state.agent = ConversationAgent(project_name=project_name)
                    st.session_state.project_name = project_name
                    st.session_state.enable_web_search = enable_web_search
                    
                    # Reset state
                    st.session_state.messages = []
                    st.session_state.complete = False
                    st.session_state.current_node = st.session_state.config_manager.get_workflow_config().get("start_node", "start")
                    st.session_state.completed_nodes = set()
                    st.session_state.current_node_started = False
                    
                    # Clear process tracker
                    st.session_state.process_tracker = {
                        "llm_calls": [],
                        "citations": [],
                        "clarity_scores": {},
                        "current_step": None
                    }
                    
                    st.rerun()
        
        # Enhanced workflow visualization
        if st.session_state.project_name:
            st.sidebar.markdown("---")
            render_enhanced_workflow_sidebar(
                st.session_state.current_node,
                st.session_state.completed_nodes,
                st.session_state.process_tracker
            )
    
    # Display project info
    if st.session_state.project_name:
        st.sidebar.subheader(f"Project: {st.session_state.project_name}")
        
        if st.session_state.complete:
            st.sidebar.success("Project planning complete!")
    
    # Enhanced chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            content = create_animated_container(message["content"])
            st.markdown(content, unsafe_allow_html=True)
    
    # Enhanced chat input
    if st.session_state.agent and not st.session_state.complete:
        current_node_config = get_current_node_config()
        
        # Show current node with enhanced info
        st.markdown(f"### {current_node_config['emoji']} {current_node_config['label']}")
        st.info(current_node_config['purpose'])
        
        # Show node capabilities
        capabilities = []
        if current_node_config.get('optional'):
            capabilities.append("Optional")
        if current_node_config.get('retry'):
            capabilities.append("Can Retry")
        if current_node_config.get('skip'):
            capabilities.append("Can Skip")
        if current_node_config.get('web_search'):
            capabilities.append("Web Search Enabled")
        
        if capabilities:
            st.caption(f"Node capabilities: {', '.join(capabilities)}")
        
        user_input = st.chat_input("Type your response here...")
        
        if user_input:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Enhanced processing
            with st.spinner("Processing with enhanced features..."):
                agent_response, is_complete = process_user_input_enhanced(user_input)
                
                # Add assistant response
                st.session_state.messages.append({"role": "assistant", "content": agent_response})
                
                # Enhanced completion logic with node controls
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if is_complete or st.button("Complete Current Section"):
                        st.session_state.completed_nodes.add(st.session_state.current_node)
                        
                        # Get next node from configuration
                        next_node_id = st.session_state.config_manager.get_next_node(st.session_state.current_node)
                        
                        if next_node_id and next_node_id != "complete":
                            next_node_config = st.session_state.config_manager.get_node_config(next_node_id)
                            st.session_state.current_node = next_node_id
                            st.session_state.current_node_started = False
                            st.success(f"Moving to {next_node_config['label']}!")
                            time.sleep(1)
                        else:
                            st.session_state.complete = True
                            st.balloons()
                
                with col2:
                    # Retry button if supported
                    if current_node_config.get('retry') and st.button("Retry"):
                        if st.session_state.messages:
                            st.session_state.messages.pop()
                        st.info("You can provide a new response for this section.")
                
                with col3:
                    # Skip button if supported
                    if current_node_config.get('skip') and st.button("Skip"):
                        next_node_id = st.session_state.config_manager.get_next_node(st.session_state.current_node)
                        if next_node_id and next_node_id != "complete":
                            st.session_state.current_node = next_node_id
                            st.session_state.current_node_started = False
                            st.info("Skipped to next section.")
                
                st.rerun()
    
    # Enhanced completion
    elif st.session_state.complete:
        st.balloons()
        st.success("Enhanced project clarification complete!")
        
        # Show enhanced summary with project data
        if hasattr(st.session_state.agent, 'project'):
            render_project_completion_summary(st.session_state.agent.project.dict())
        
        # Show statistics
        stats = ProcessTracker.get_stats()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("LLM Calls", stats["total_calls"])
        with col2:
            st.metric("Citations", stats["total_citations"])
        with col3:
            st.metric("Total Tokens", stats["total_tokens"])
    
    # Initial state
    elif not st.session_state.agent:
        st.info("Please create or load a project to get started with enhanced features.")
    
    # Enhanced process details
    if st.session_state.project_name:
        st.markdown("---")
        render_enhanced_process_details(st.session_state.current_node, st.session_state.process_tracker)


if __name__ == "__main__":
    main()