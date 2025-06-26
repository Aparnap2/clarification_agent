import streamlit as st
import os
import json
import yaml
from clarification_agent.core.conversation_agent import ConversationAgent

st.set_page_config(
    page_title="🧠 Clarification Agent",
    page_icon="🧠",
    layout="wide"
)

def load_project_data(project_name):
    """Load project data from .clarity folder if it exists"""
    clarity_path = os.path.join(".clarity", f"{project_name}.json")
    if os.path.exists(clarity_path):
        with open(clarity_path, "r") as f:
            return json.load(f)
    return None

def main():
    st.title("🧠 Clarification Agent")
    st.write("Let's clarify your project through conversation.")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "agent" not in st.session_state:
        st.session_state.agent = None
        st.session_state.project_name = None
        st.session_state.complete = False
    
    # Sidebar for project selection/creation
    with st.sidebar:
        st.header("Project")
        project_action = st.radio("Choose an action:", ["Create New Project", "Load Existing Project"])
        
        if project_action == "Create New Project":
            project_name = st.text_input("Project Name:")
            if st.button("Start New Project") and project_name:
                # Initialize new conversation agent
                st.session_state.agent = ConversationAgent(project_name=project_name)
                st.session_state.project_name = project_name
                st.session_state.messages = []
                st.session_state.complete = False
                
                # Get initial message from agent
                initial_message, _ = st.session_state.agent.process_user_input("")
                st.session_state.messages.append({"role": "assistant", "content": initial_message})
                st.rerun()
        else:
            # List existing projects from .clarity folder
            if os.path.exists(".clarity"):
                projects = [f.replace(".json", "") for f in os.listdir(".clarity") if f.endswith(".json")]
                if projects:
                    selected_project = st.selectbox("Select a project:", projects)
                    if st.button("Load Project"):
                        project_data = load_project_data(selected_project)
                        st.session_state.agent = ConversationAgent(
                            project_name=selected_project,
                            project_data=project_data
                        )
                        st.session_state.project_name = selected_project
                        st.session_state.messages = []
                        st.session_state.complete = False
                        
                        # Get initial message from agent
                        initial_message, _ = st.session_state.agent.process_user_input("")
                        st.session_state.messages.append({"role": "assistant", "content": initial_message})
                        st.rerun()
                else:
                    st.info("No existing projects found.")
            else:
                st.info("No existing projects found.")
    
    # Display current project info if available
    if st.session_state.project_name:
        st.sidebar.subheader(f"Project: {st.session_state.project_name}")
        
        if st.session_state.complete:
            st.sidebar.success("Project planning complete!")
            if st.sidebar.button("View Generated Files"):
                st.sidebar.markdown("### Generated Files")
                st.sidebar.markdown("- README.md")
                st.sidebar.markdown("- .plan.yml")
                st.sidebar.markdown("- architecture.md")
                st.sidebar.markdown("- .clarity/*.json")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if st.session_state.agent and not st.session_state.complete:
        user_input = st.chat_input("Type your response here...")
        if user_input:
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Get agent response
            with st.spinner("Thinking..."):
                try:
                    agent_response, is_complete = st.session_state.agent.process_user_input(user_input)
                    st.session_state.messages.append({"role": "assistant", "content": agent_response})
                    st.session_state.complete = is_complete
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.session_state.messages.append({"role": "assistant", "content": "I'm sorry, I encountered an error. Let's continue with the next step."})
                    # Move to the next stage to recover from error
                    if hasattr(st.session_state.agent, 'current_stage_index'):
                        st.session_state.agent.current_stage_index += 1
            
            st.rerun()
    elif not st.session_state.agent:
        st.info("Create or load a project to start the conversation.")

if __name__ == "__main__":
    main()