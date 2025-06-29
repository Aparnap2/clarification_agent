import streamlit as st
from schemas import Project, Task, Idea, Clarification
from agents.clarifier_agent import ClarifierAgent
from agents.planner_agent import PlannerAgent

# In-memory storage & agent initialization
if 'projects' not in st.session_state:
    st.session_state.projects = []
if 'clarifier_agent' not in st.session_state:
    st.session_state.clarifier_agent = ClarifierAgent()
if 'planner_agent' not in st.session_state:
    st.session_state.planner_agent = PlannerAgent()
if 'current_project' not in st.session_state:
    st.session_state.current_project = None
if 'user_input_key' not in st.session_state: # To reset input field
    st.session_state.user_input_key = 0
if 'active_clarification' not in st.session_state: # To hold pending clarification
    st.session_state.active_clarification = None


def handle_user_goal_input(user_goal: str):
    """Handles the initial user goal input."""
    if st.session_state.current_project:
        # Step 1: Clarifier Agent (Conceptual - for now, we'll directly generate a question)
        # In a more complex flow, we might await user response to clarification
        clarification_obj = st.session_state.clarifier_agent.ask_question(user_goal, context=st.session_state.current_project.name)
        st.session_state.current_project.clarifications.append(clarification_obj)
        st.session_state.active_clarification = clarification_obj # Store for potential follow-up

        st.info(f"Clarifier Agent asks: {clarification_obj.question}")
        # For this basic flow, we'll assume the initial goal is clear enough
        # and proceed to planning. Or, we can add a button "Proceed with this goal"

        # Step 2: Planner Agent
        new_tasks = st.session_state.planner_agent.generate_initial_plan(user_goal, st.session_state.current_project.id)
        st.session_state.current_project.tasks.extend(new_tasks)
        st.success(f"Planner Agent generated {len(new_tasks)} tasks for '{user_goal}'.")
        st.session_state.user_input_key += 1 # Reset input field by changing its key
        st.experimental_rerun() # Refresh UI to show new tasks and clear input
    else:
        st.error("Please select or create a project first.")

def main():
    st.set_page_config(layout="wide", page_title="Personal AI Strategy Assistant")
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
