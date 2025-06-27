
import streamlit as st
from typing import TypedDict, List, Dict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json

load_dotenv()

# --- OpenRouter Configuration ---
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    st.error("OPENROUTER_API_KEY not found in environment variables. Please set it.")
    st.stop()

llm = ChatOpenAI(
    model="microsoft/mai-ds-r1:free",  # You can choose other models from OpenRouter
    openai_api_key=OPENROUTER_API_KEY,
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0.7
)

# --- LangGraph State Definition ---
class ClarificationState(TypedDict):
    messages: Annotated[list, lambda x, y: x + y]
    requirements: List[str]
    ambiguities: List[str]
    stakeholder_responses: Dict[str, str]
    clarification_status: str
    project_context: str

# --- LangGraph Nodes ---
def requirements_analyzer_node(state: ClarificationState):
    st.write("Running Requirements Analyzer...")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert requirements analyst. Extract key requirements and identify potential gaps or unclear specifications from the given project description."),
        ("user", "Project Description: {project_context}")
    ])
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"project_context": state["project_context"]})
    
    # Simple parsing for demonstration; in a real app, use Pydantic for structured output
    requirements = [req.strip() for req in response.split("\n") if req.strip() and "requirement" in req.lower()]
    ambiguities = [amb.strip() for amb in response.split("\n") if amb.strip() and "unclear" in amb.lower() or "gap" in amb.lower()]
    
    return {"requirements": requirements, "ambiguities": ambiguities, "messages": [AIMessage(content=f"Requirements analyzed. Found {len(ambiguities)} ambiguities.")]}

def ambiguity_detector_node(state: ClarificationState):
    st.write("Running Ambiguity Detector...")
    if not state.get("requirements"):
        return {"ambiguities": [], "clarification_status": "complete", "messages": [AIMessage(content="No requirements to analyze.")]}

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an ambiguity detection specialist. Review the following requirements and identify any unclear, missing, or conflicting specifications. List them clearly."),
        ("user", "Requirements: {requirements}\n\nProject Context: {project_context}")
    ])
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"requirements": "\n".join(state["requirements"]), "project_context": state["project_context"]})
    
    # Simple parsing for demonstration
    ambiguities = [amb.strip() for amb in response.split("\n") if amb.strip()]
    
    return {"ambiguities": ambiguities, "messages": [AIMessage(content=f"Ambiguities detected: {', '.join(ambiguities) if ambiguities else 'None'}.")]}

def question_generator_node(state: ClarificationState):
    st.write("Running Question Generator...")
    if not state.get("ambiguities"):
        return {"messages": [AIMessage(content="No ambiguities to generate questions for.")]}

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a clarification question generator. Based on the identified ambiguities, create targeted, clear, and concise questions to get clarification from stakeholders. Prioritize critical elements."),
        ("user", "Ambiguities: {ambiguities}\n\nProject Context: {project_context}")
    ])
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"ambiguities": "\n".join(state["ambiguities"]), "project_context": state["project_context"]})
    
    questions = [q.strip() for q in response.split("\n") if q.strip()]
    
    return {"messages": [AIMessage(content="Please answer the following questions to clarify the requirements:\n" + "\n".join(questions))]}

def response_processor_node(state: ClarificationState):
    st.write("Running Response Processor...")
    latest_human_response = None
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            latest_human_response = msg.content
            break

    if not latest_human_response:
        return {"clarification_status": "incomplete", "messages": [AIMessage(content="No human response to process.")]}

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a response processor. Analyze the stakeholder's response to the clarification questions. Determine if the ambiguities are resolved or if further clarification is needed. If resolved, update the requirements. If not, state what is still unclear."),
        ("user", "Original Ambiguities: {ambiguities}\n\nStakeholder Response: {response}\n\nProject Context: {project_context}")
    ])
    chain = prompt | llm | StrOutputParser()
    response_analysis = chain.invoke({
        "ambiguities": "\n".join(state["ambiguities"]),
        "response": latest_human_response,
        "project_context": state["project_context"]
    })

    # Simple logic to determine status and update requirements/ambiguities
    new_ambiguities = []
    new_requirements = list(state.get("requirements", []))
    clarification_status = "complete"

    if "further clarification needed" in response_analysis.lower() or "unclear" in response_analysis.lower():
        clarification_status = "incomplete"
        # Attempt to extract new ambiguities if the model provides them
        new_ambiguities = [amb.strip() for amb in response_analysis.split("\n") if "unclear" in amb.lower() or "still ambiguous" in amb.lower()]
        if not new_ambiguities: # If model didn't list new ambiguities, keep old ones for re-asking
            new_ambiguities = state["ambiguities"]
    else:
        # Assume ambiguities are resolved and update requirements based on the response
        # This is a very simplified update. A real system would parse structured updates.
        new_requirements.append(f"Clarified based on: {latest_human_response}")
        
    return {
        "clarification_status": clarification_status,
        "ambiguities": new_ambiguities,
        "requirements": new_requirements,
        "messages": [AIMessage(content=f"Response processed. Status: {clarification_status}. Analysis: {response_analysis}")]
    }

def human_in_the_loop_node(state: ClarificationState):
    st.write("Awaiting human input for clarification...")
    # This node simply signals that human input is needed.
    # The Streamlit chat_input handles capturing this.
    return {"clarification_status": "incomplete"} # Keep status incomplete until human responds

# --- LangGraph Conditional Edge ---
def route_clarification(state: ClarificationState):
    if state.get('ambiguities') and len(state['ambiguities']) > 0 and state['clarification_status'] != "complete":
        return "question_generator"
    elif state['clarification_status'] == "incomplete":
        # If incomplete and no new questions generated, it means we are waiting for human input
        # or processing human input. Route to response_processor after human_in_the_loop.
        return "human_in_the_loop" 
    else:
        return END

# --- Build LangGraph Workflow ---
workflow = StateGraph(ClarificationState)

workflow.add_node("requirements_analyzer", requirements_analyzer_node)
workflow.add_node("ambiguity_detector", ambiguity_detector_node)
workflow.add_node("question_generator", question_generator_node)
workflow.add_node("response_processor", response_processor_node)
workflow.add_node("human_in_the_loop", human_in_the_loop_node)

workflow.set_entry_point("requirements_analyzer")

workflow.add_edge("requirements_analyzer", "ambiguity_detector")
workflow.add_conditional_edges(
    "ambiguity_detector",
    route_clarification,
    {
        "question_generator": "question_generator",
        "human_in_the_loop": "human_in_the_loop", # This path is taken if no new questions but still incomplete
        END: END
    }
)
workflow.add_edge("question_generator", "human_in_the_loop") # After generating question, wait for human input
workflow.add_edge("human_in_the_loop", "response_processor") # After human input, process response
workflow.add_edge("response_processor", "ambiguity_detector") # Re-evaluate after processing response

memory = SqliteSaver.from_conn_string("sqlite:///clarification_history.db")
graph = workflow.compile(checkpointer=memory)

# --- Streamlit UI ---
st.title("Clarification AI Agent")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "run_id" not in st.session_state:
    st.session_state.run_id = None

for message in st.session_state.messages:
    with st.chat_message(message.type):
        st.markdown(message.content)

if prompt := st.chat_input("Enter project description or clarification:"):
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    # Initial run or continue existing run
    config = {"configurable": {"thread_id": "1"}}
    
    # If it's a new conversation or the previous one ended, start fresh
    if st.session_state.run_id is None or graph.get_state(config) is None:
        inputs = {"project_context": prompt, "messages": [HumanMessage(content=prompt)]}
        st.session_state.run_id = "1" # Assign a fixed thread_id for simplicity
    else:
        # Continue the existing run with human input
        inputs = {"stakeholder_responses": {"human_input": prompt}, "messages": [HumanMessage(content=prompt)]}

    try:
        for s in graph.stream(inputs, config=config):
            for key, value in s.items():
                if key != "__end__":
                    st.write(f"Node: {key}, State: {value}")
                    if "messages" in value:
                        for msg in value["messages"]:
                            if isinstance(msg, AIMessage):
                                with st.chat_message("assistant"):
                                    st.markdown(msg.content)
                                st.session_state.messages.append(msg)
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.session_state.run_id = None # Reset run_id on error to allow starting fresh
