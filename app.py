import streamlit as st
from clarification_agent.core.agent_manager import ClarificationAgentManager
import os
import json

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
    st.write("Plan your projects with clarity before diving into code.")
    
    # Sidebar for project selection/creation
    with st.sidebar:
        st.header("Project")
        project_action = st.radio("Choose an action:", ["Create New Project", "Load Existing Project"])
        
        if project_action == "Create New Project":
            project_name = st.text_input("Project Name:")
            if st.button("Start New Project") and project_name:
                st.session_state.project_name = project_name
                st.session_state.project_data = None
                st.session_state.current_node = "ClarifyIntent"
                st.experimental_rerun()
        else:
            # List existing projects from .clarity folder
            if os.path.exists(".clarity"):
                projects = [f.replace(".json", "") for f in os.listdir(".clarity") if f.endswith(".json")]
                if projects:
                    selected_project = st.selectbox("Select a project:", projects)
                    if st.button("Load Project"):
                        st.session_state.project_name = selected_project
                        st.session_state.project_data = load_project_data(selected_project)
                        st.session_state.current_node = "Start"
                        st.experimental_rerun()
                else:
                    st.info("No existing projects found.")
            else:
                st.info("No existing projects found.")
    
    # Main content area
    if "project_name" in st.session_state:
        st.header(f"Project: {st.session_state.project_name}")
        
        # Initialize agent manager if needed
        if "agent_manager" not in st.session_state:
            st.session_state.agent_manager = ClarificationAgentManager(
                project_name=st.session_state.project_name,
                project_data=st.session_state.project_data
            )
        
        # Display current node and handle interaction
        current_node = st.session_state.get("current_node", "Start")
        agent_manager = st.session_state.agent_manager
        
        # Process current node
        node_result = agent_manager.process_node(current_node)
        
        # Display node content
        st.subheader(node_result.get("title", current_node))
        st.write(node_result.get("description", ""))
        
        # Handle node-specific UI
        if "questions" in node_result:
            with st.form(key=f"node_{current_node}"):
                responses = {}
                for q in node_result["questions"]:
                    if q.get("type") == "text":
                        responses[q["id"]] = st.text_area(q["question"], key=q["id"])
                    elif q.get("type") == "select":
                        responses[q["id"]] = st.selectbox(q["question"], q["options"], key=q["id"])
                    elif q.get("type") == "multiselect":
                        responses[q["id"]] = st.multiselect(q["question"], q["options"], key=q["id"])
                    else:
                        responses[q["id"]] = st.text_input(q["question"], key=q["id"])
                
                submit = st.form_submit_button("Continue")
                if submit:
                    next_node = agent_manager.submit_responses(current_node, responses)
                    st.session_state.current_node = next_node
                    st.experimental_rerun()
        
        # Display project progress
        st.sidebar.subheader("Progress")
        progress = agent_manager.get_progress()
        st.sidebar.progress(progress["percentage"])
        st.sidebar.write(f"{progress['completed']}/{progress['total']} steps completed")
        
        # Export options when complete
        if progress["percentage"] == 1.0:
            st.sidebar.success("Project planning complete!")
            if st.sidebar.button("Export All Files"):
                agent_manager.export_all()
                st.sidebar.success("Files exported successfully!")
    else:
        st.info("Select or create a project to get started.")

if __name__ == "__main__":
    main()