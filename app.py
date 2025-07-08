import streamlit as st
import os
import json
from datetime import datetime
from clarification_agent.main import get_agent
from clarification_agent.core.agent_manager import ClarificationAgentManager
from clarification_agent.ui.process_tracker import ProcessTracker
import plotly.graph_objects as go
import time

# Set page config
st.set_page_config(
    page_title="Clarification Agent", 
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS for better message display
st.markdown("""
    <style>
        .stChatMessage {
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            max-width: 85%;
        }
        .stChatMessage[data-testid="stChatMessage"] {
            padding: 1rem;
        }
        .assistant-message {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
            white-space: pre-wrap;
        }
        .thinking {
            color: #666;
            font-style: italic;
            padding: 1rem;
        }
        .error-message {
            color: #d32f2f;
            background-color: #fde0e0;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        .stApp {
            background-color: #1E1E1E;
            color: #FFFFFF;
        }
        h1, h2, h3, h4, h5, h6, p, li {
            color: #FFFFFF;
        }
        .css-1d391kg {
            padding: 1rem 1rem 10rem;
        }
        .status-card {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        .chat-message {
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            max-width: 80%;
        }
        .user-message {
            background-color: #e3f2fd;
            margin-left: auto;
        }
        .assistant-message {
            background-color: #f5f5f5;
            margin-right: auto;
        }
    </style>
    """, unsafe_allow_html=True)

st.title("Clarification Agent")

def load_project(project_name):
    """Load a project from the .clarity directory"""
    try:
        file_path = os.path.join(".clarity", f"{project_name}.json")
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading project: {str(e)}")
    return None

def get_existing_projects():
    """Get list of existing projects"""
    if os.path.exists(".clarity"):
        return [f.replace(".json", "") for f in os.listdir(".clarity") if f.endswith(".json")]
    return []

def display_file_content(file_path):
    """Display the content of a project file"""
    try:
        with open(file_path, "r") as f:
            content = f.read()
            if file_path.endswith((".md", ".yml", ".yaml")):
                st.markdown(content)
            else:
                st.code(content, language="json")
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")

def initialize_session_state():
    """Initialize or reset the session state"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent" not in st.session_state:
        st.session_state.agent = None
    if "project_name" not in st.session_state:
        st.session_state.project_name = None
    if "project_data" not in st.session_state:
        st.session_state.project_data = None
    if "current_stage" not in st.session_state:
        st.session_state.current_stage = 0
    if "stages_completed" not in st.session_state:
        st.session_state.stages_completed = set()

def display_project_files():
    """Display project files in an expandable section"""
    if st.session_state.project_name:
        with st.expander("📁 Project Files", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Documentation")
                if os.path.exists("README.md"):
                    if st.button("View README"):
                        display_file_content("README.md")
                if os.path.exists("architecture.md"):
                    if st.button("View Architecture"):
                        display_file_content("architecture.md")
            
            with col2:
                st.markdown("### Configuration")
                if os.path.exists(".plan.yml"):
                    if st.button("View Plan"):
                        display_file_content(".plan.yml")
                clarity_file = os.path.join(".clarity", f"{st.session_state.project_name}.json")
                if os.path.exists(clarity_file):
                    if st.button("View Project Data"):
                        display_file_content(clarity_file)

def main():
    # Initialize session state
    initialize_session_state()
    
    # Sidebar
    with st.sidebar:
        st.title("🧠 Project Manager")
        st.markdown("---")
        
        # Project Selection/Creation
        project_action = st.radio("Choose an action:", ["Create New Project", "Load Existing Project"])
        
        if project_action == "Create New Project":
            with st.form("new_project_form"):
                project_name = st.text_input("Project Name:")
                submit_button = st.form_submit_button("Create Project")
                
                if submit_button and project_name:
                    st.session_state.project_name = project_name
                    st.session_state.agent = get_agent()
                    st.session_state.messages = []
                    st.session_state.current_stage = 0
                    st.session_state.stages_completed = set()
                    st.rerun()
        else:
            projects = get_existing_projects()
            if projects:
                selected_project = st.selectbox("Select a project:", projects)
                if st.button("Load Project"):
                    project_data = load_project(selected_project)
                    if project_data:
                        st.session_state.project_name = selected_project
                        st.session_state.project_data = project_data
                        st.session_state.agent = get_agent()
                        st.session_state.messages = []
                        st.rerun()
            else:
                st.info("No existing projects found.")
        
        # Project Status (if project is selected)
        if st.session_state.project_name:
            st.markdown("---")
            st.subheader("📊 Project Status")
            stages = ["Project Description", "Requirements", "MVP Scope", "Technology", "Architecture", "Tasks"]
            current_stage = st.session_state.current_stage
            progress = (len(st.session_state.stages_completed) / len(stages)) * 100
            st.progress(progress)
            st.caption(f"Stage {current_stage + 1} of {len(stages)}: {stages[current_stage]}")
    
    # Main content area
    if st.session_state.project_name:
        # Project header
        st.title(f"Project: {st.session_state.project_name}")
        
        # Display project status cards
        col1, col2, col3 = st.columns(3)
        with col1:
            with st.container():
                st.markdown('<div class="status-card">', unsafe_allow_html=True)
                st.subheader("🎯 Current Stage")
                stages = ["Project Description", "Requirements", "MVP Scope", "Technology", "Architecture", "Tasks"]
                st.info(stages[st.session_state.current_stage])
                st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            with st.container():
                st.markdown('<div class="status-card">', unsafe_allow_html=True)
                st.subheader("✅ Completed Steps")
                st.success(f"{len(st.session_state.stages_completed)} of {len(stages)}")
                st.markdown("</div>", unsafe_allow_html=True)
        
        with col3:
            with st.container():
                st.markdown('<div class="status-card">', unsafe_allow_html=True)
                st.subheader("📝 Project Files")
                file_count = len([f for f in os.listdir() if f.endswith((".md", ".yml", ".json"))])
                st.info(f"{file_count} files generated")
                st.markdown("</div>", unsafe_allow_html=True)
        
        # Display project files
        display_project_files()
        
        # Chat interface
        st.markdown("---")
        st.subheader("💬 Clarification Chat")
        
        # Display chat messages
        for message in st.session_state.messages:
            role = message["role"]
            with st.chat_message(role):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Type your message here..."):
            # Add user message to the chat and display it
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message immediately
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Show loading state
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.markdown("<div class='thinking'>🤔 Thinking...</div>", unsafe_allow_html=True)
                
                try:
                    full_response = ""
                    
                    # Process each chunk as it arrives
                    chunk_count = 0
                    last_update = time.time()
                    
                    for chunk in st.session_state.agent.stream({"messages": [("user", prompt)]}):
                        try:
                            chunk_count += 1
                            current_time = time.time()
                            
                            # Handle different chunk types
                            chunk_content = ""
                            
                            if hasattr(chunk, 'get'):  # Dictionary-like object
                                # Skip control flow chunks
                                if isinstance(chunk, dict) and ('clarify' in chunk or 'reason' in chunk):
                                    print(f"Skipping control flow chunk: {chunk}")
                                    continue
                                    
                                # Extract content from different possible structures
                                if 'messages' in chunk and chunk['messages']:
                                    chunk_content = chunk['messages'][-1].content or ""
                                elif 'content' in chunk:
                                    chunk_content = chunk['content'] or ""
                                elif hasattr(chunk, 'items'):
                                    # Try to find any string content in the chunk
                                    for k, v in chunk.items():
                                        if isinstance(v, str):
                                            chunk_content = v
                                            break
                                        elif hasattr(v, 'content'):
                                            chunk_content = v.content or ""
                                            break
                                        
                            elif hasattr(chunk, 'content'):  # Message object
                                chunk_content = chunk.content or ""
                            elif isinstance(chunk, str):  # String chunk
                                chunk_content = chunk
                            
                            # Update the response if we have new content
                            if chunk_content:
                                full_response += chunk_content
                                
                                # Only update the UI at most every 100ms to improve performance
                                if current_time - last_update > 0.1 or chunk_count % 5 == 0:
                                    message_placeholder.markdown(
                                        f"<div class='assistant-message'>{full_response}▌</div>", 
                                        unsafe_allow_html=True
                                    )
                                    last_update = current_time
                                
                        except Exception as e:
                            print(f"Error processing chunk: {e}")
                            continue
                    
                    # Update the final message without the cursor
                    if full_response.strip():
                        message_placeholder.markdown(
                            f"<div class='assistant-message'>{full_response}</div>", 
                            unsafe_allow_html=True
                        )
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                    else:
                        error_msg = "I couldn't generate a response. The answer might be empty or an error occurred."
                        message_placeholder.markdown(
                            f"<div class='error-message'>{error_msg}</div>",
                            unsafe_allow_html=True
                        )
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                
                except Exception as e:
                    error_msg = f"An error occurred: {str(e)}"
                    print(f"Error in chat: {error_msg}")
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": "I'm sorry, but I encountered an error. Please try again."})
                    
                    # Update progress if needed (based on response content)
                    if "completed" in full_response.lower():
                        st.session_state.stages_completed.add(st.session_state.current_stage)
                        if st.session_state.current_stage < len(stages) - 1:
                            st.session_state.current_stage += 1
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": "I apologize, but I encountered an error. Let's continue with the next step."
                    })
    else:
        # Welcome screen
        st.markdown("""
        # Welcome to the Clarification Agent! 👋
        
        I'm here to help you plan and scope your project through an interactive conversation.
        
        To get started:
        1. Create a new project or load an existing one from the sidebar
        2. Chat with me about your project requirements
        3. I'll guide you through the planning process step by step
        
        Let's build something amazing together! 🚀
        """)

if __name__ == "__main__":
    main()