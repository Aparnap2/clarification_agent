import streamlit as st
import os
from schemas import Project, Task, Idea, Clarification
from agents.clarifier_agent import ClarifierAgent
from agents.planner_agent import PlannerAgent

# Attempt to load environment variables for API keys
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass # python-dotenv not installed/needed if env vars are set externally

# --- Agent and State Initialization ---
def initialize_state():
    if 'projects' not in st.session_state:
        st.session_state.projects = []
    if 'current_project' not in st.session_state:
        st.session_state.current_project = None
    if 'user_input_key' not in st.session_state:
        st.session_state.user_input_key = 0
    # Active clarification is not used in the current simplified flow where planner uses original goal
    # if 'active_clarification' not in st.session_state:
    #     st.session_state.active_clarification = None

    # Initialize agents, handle potential API key errors gracefully for UI
    if 'clarifier_agent' not in st.session_state:
        try:
            st.session_state.clarifier_agent = ClarifierAgent()
        except ValueError as e: # Raised if API key is missing
            st.session_state.clarifier_agent = None
            st.session_state.clarifier_error = str(e)
    if 'planner_agent' not in st.session_state:
        try:
            st.session_state.planner_agent = PlannerAgent()
        except ValueError as e: # Raised if API key is missing
            st.session_state.planner_agent = None
            st.session_state.planner_error = str(e)

def handle_user_goal_input(user_goal: str):
    """Handles the initial user goal input using enhanced agents."""
    if not st.session_state.current_project:
        st.error("Please select or create a project first.")
        return

    # Check if agents are available
    if not st.session_state.clarifier_agent:
        st.error(f"Clarifier Agent not available: {st.session_state.get('clarifier_error', 'Unknown error')}. Please set OPENROUTER_API_KEY.")
        return
    if not st.session_state.planner_agent:
        st.error(f"Planner Agent not available: {st.session_state.get('planner_error', 'Unknown error')}. Please set OPENROUTER_API_KEY.")
        return

    project_ctx = st.session_state.current_project.description or st.session_state.current_project.name

    # Step 1: Clarifier Agent - Generates and logs a question
    with st.spinner("Clarifier Agent is thinking..."):
        clarification_obj = st.session_state.clarifier_agent.ask_question(user_goal, project_context=project_ctx)

    st.session_state.current_project.clarifications.append(clarification_obj)
    st.info(f"Clarifier Agent asks: {clarification_obj.question}")
    # For this iteration, we display the question but the Planner will use the original goal.
    # A future step could involve a button "Answer & Plan" or "Plan with this goal".

    # Step 2: Planner Agent - Generates tasks based on the original goal
    with st.spinner("Planner Agent is generating tasks..."):
        new_tasks = st.session_state.planner_agent.generate_initial_plan(
            goal=user_goal,
            project_id=st.session_state.current_project.id,
            project_context=project_ctx
        )

    if new_tasks:
        st.session_state.current_project.tasks.extend(new_tasks)
        st.success(f"Planner Agent generated {len(new_tasks)} tasks for '{user_goal}'.")
    else:
        st.warning("Planner Agent did not generate any tasks. You might need to refine the goal or check agent logs.")

    st.session_state.user_input_key += 1 # Reset input field by changing its key
    st.experimental_rerun()

def main():
    st.set_page_config(layout="wide", page_title="Personal AI Strategy Assistant")
    initialize_state() # Ensure all session state keys and agents are initialized

    st.title("Personal AI Strategy Assistant")

    # --- Sidebar for Project Creation and Selection ---
    st.sidebar.header("Projects")
    new_project_name = st.sidebar.text_input("New Project Name", key="new_project_name_input")
    if st.sidebar.button("Create Project"):
        if new_project_name:
            project = Project(name=new_project_name)
            st.session_state.projects.append(project)
            st.sidebar.success(f"Project '{new_project_name}' created!")
            # Select the newly created project
            st.session_state.current_project = project
            st.experimental_rerun()
        else:
            st.sidebar.error("Project name cannot be empty.")

    if st.session_state.projects:
        project_names = [p.name for p in st.session_state.projects]

        current_project_index = 0
        if st.session_state.current_project and st.session_state.current_project.name in project_names:
            current_project_index = project_names.index(st.session_state.current_project.name)

        selected_project_name = st.sidebar.selectbox("Select Project", project_names, index=current_project_index, key="project_selector")

        if st.session_state.current_project is None or selected_project_name != st.session_state.current_project.name:
            st.session_state.current_project = next((p for p in st.session_state.projects if p.name == selected_project_name), None)
            st.experimental_rerun() # Rerun if project selection changed
    else:
        st.session_state.current_project = None

    # --- Main Area for Project Details and Interaction ---
    if st.session_state.current_project:
        st.header(f"Project: {st.session_state.current_project.name}")

        st.subheader("Project Details")
        st.markdown(f"**ID:** `{st.session_state.current_project.id}`")
        # Allow editing description
        description = st.text_area("Description:", value=st.session_state.current_project.description or "", key=f"desc_{st.session_state.current_project.id}")
        if description != (st.session_state.current_project.description or ""): # check if changed
            st.session_state.current_project.description = description
            # No need to rerun here, text_area updates session_state automatically

        st.markdown("---")
        st.subheader("Define a Goal or Task for this Project")
        user_input = st.text_input(
            "e.g., 'Develop a new feature', 'Plan marketing campaign'",
            key=f"user_input_{st.session_state.user_input_key}" # Use key to allow resetting
        )
        if st.button("Process Goal"):
            if user_input:
                handle_user_goal_input(user_input)
            else:
                st.warning("Please enter a goal or task.")

        # Display active clarification if any (simplified)
        # if st.session_state.active_clarification and not st.session_state.active_clarification.answer:
        #     st.info(f"Clarifier asks: {st.session_state.active_clarification.question}")
        #     clarification_answer = st.text_input("Your answer:", key=f"clar_ans_{st.session_state.active_clarification.id}")
        #     if st.button("Submit Answer", key=f"clar_submit_{st.session_state.active_clarification.id}"):
        #         if clarification_answer:
        #             st.session_state.active_clarification.answer = clarification_answer
        #             # Potentially pass this back to a planner or another agent
        #             st.success("Answer recorded.")
        #             st.session_state.active_clarification = None # Clear active clarification
        #             st.experimental_rerun()


        st.markdown("---")
        st.subheader("Tasks")
        if st.session_state.current_project.tasks:
            for task in st.session_state.current_project.tasks:
                st.checkbox(f"{task.name} (Priority: {task.priority}, Status: {task.status})", key=f"task_{task.id}")
        else:
            st.write("No tasks yet for this project.")

        # Display other project components like Ideas, Clarifications (simplified for now)
        # st.subheader("Ideas")
        # ...
        # st.subheader("Clarifications")
        # ...
    else:
        st.info("Create or select a project from the sidebar to get started.")

    # --- Footer or Debug Info ---
    # st.sidebar.markdown("---")
    # st.sidebar.json(st.session_state.to_dict() if hasattr(st.session_state, 'to_dict') else {})


if __name__ == "__main__":
    main()
