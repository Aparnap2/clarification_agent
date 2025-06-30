# Personal AI Strategy Assistant

A Streamlit-based application that acts as a personal AI strategy assistant. It helps you define goals, get clarifying questions, and generate initial action plans for your projects.

## Current Features

*   Project creation and management (in-memory).
*   AI-powered Clarifier Agent: Asks dynamic questions to help you elaborate on your goals (uses OpenRouter).
*   AI-powered Planner Agent: Generates a list of initial tasks based on your goals (uses OpenRouter).
*   Simple Streamlit UI for interaction.

## Getting Started / Setup

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```
    (Replace `<repository_url>` and `<repository_directory>` with the actual URL and local directory name)

2.  **Create a Python virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure OpenRouter API Key:**
    This application uses [OpenRouter.ai](https://openrouter.ai/) to access various Large Language Models for its agent functionalities. You **must** have an OpenRouter API key.

    *   **Create a `.env` file:** In the root directory of the project, create a file named `.env`.
        *(If a `.env.example` file exists, you can copy it: `cp .env.example .env`)*
    *   **Add your API key:** Add the following line to your `.env` file, replacing `your_actual_api_key_here` with your real key:
        ```env
        OPENROUTER_API_KEY="your_actual_api_key_here"
        ```
    *   **(Optional) Configure Specific Models:** You can also specify preferred OpenRouter models for the Clarifier and Planner agents in the `.env` file. If not set, they default to free models (e.g., `mistralai/mistral-7b-instruct:free`).
        ```env
        # Example model overrides (uncomment and change as needed):
        # OPENROUTER_CLARIFIER_MODEL="openai/gpt-3.5-turbo"
        # OPENROUTER_PLANNER_MODEL="anthropic/claude-2"
        ```
        Refer to [OpenRouter Models](https://openrouter.ai/models) for available model IDs. The application will indicate in the UI if the API key is missing or invalid.

5.  **Run the Streamlit application:**
    ```bash
    streamlit run main.py
    ```
    The application should open in your web browser.

## Project Structure (Current)

*   `main.py`: Main Streamlit application file, UI logic.
*   `schemas.py`: Pydantic models for data structures (Project, Task, etc.).
*   `agents/`: Directory containing the AI agent logic.
    *   `clarifier_agent.py`: Agent responsible for asking clarifying questions.
    *   `planner_agent.py`: Agent responsible for generating task plans.
*   `requirements.txt`: Python package dependencies.
*   `.env` (you create this): For storing API keys and other environment variables.
*   `README.md`: This file.

## Original Clarification Agent Project Information (Preserved Below)

The following sections were part of the original README for the "Clarification Agent" project, which seems to be a more comprehensive system. This current "Personal AI Strategy Assistant" is a streamlined version focusing on core clarification and planning.

---

## Overview (Original Clarification Agent)

The Clarification Agent helps you through natural conversation:

- **Clarify** project goals and requirements through dialogue
- **Trim** scope to focus on MVP features with AI guidance
- **Validate** assumptions and detect hallucinations
- **Reason** through technology choices from multiple perspectives
- **Plan** development tasks with AI assistance
- **Output** structured data for further development

## Multi-Perspective Approach (Original Clarification Agent)

The agent takes on different roles during the conversation to provide comprehensive guidance:

- **Product Manager**: Focuses on user needs and product features
- **Tech Lead**: Evaluates technical feasibility and architecture
- **Business Analyst**: Considers business value and market fit
- **UX Designer**: Ensures good user experience and interface
- **QA Engineer**: Identifies potential issues and edge cases

*(The "Getting Started" for the original agent involving `./run.sh`, `app_conversation.py`, and `dynamic_conversation.py` might not apply directly to the current `main.py` based assistant but is preserved below for context.)*

### Original Getting Started Commands

```
# Option 1: Use the run script (recommended)
./run.sh

# Option 2: Manual setup
# Install dependencies
pip install -r requirements.txt

# Run the Streamlit UI
streamlit run app_conversation.py

# Option 3: Run the dynamic conversation CLI
./dynamic_conversation.py
```

### How It Works (Original Clarification Agent)

1. **Start a conversation** - Create a new project and start chatting with the agent
2. **Answer questions** - The agent will ask questions from different perspectives
3. **Review suggestions** - The agent will provide AI-powered suggestions
4. **Generate outputs** - When the conversation is complete, the agent generates all necessary files

### Note on AI Features (Original Clarification Agent)

The agent uses LangGraph to manage the conversation flow and OpenRouter for AI capabilities.
*(The `.env` setup is now covered in the main "Getting Started / Setup" section above for the current application).*

## Output (Original Clarification Agent)



After the conversation, the agent generates:

- `.clarity/*.json` - Project memory and structure
- `.plan.yml` - Development tasks
- `README.md` - Project documentation
- `architecture.md` - Technical decisions and file mapping

## Tech Stack



- LangGraph - Conversation workflow with multiple agent perspectives
- Streamlit - Interactive chat interface
- Pydantic - Data models
- OpenRouter - AI language model integration

## Implementation Notes



The agent supports two conversation modes:

1. **Staged Flow**: A structured conversation that guides the user through predefined stages, each representing a different perspective (Product Manager, Tech Lead, etc.).
2. **Dynamic Flow**: An LLM-powered conversation where the agent dynamically determines the next appropriate question or topic based on the current project state and conversation context. This provides a more natural and flexible planning experience.

### Troubleshooting



If you encounter any issues:

1. Run the verification script: `python verify.py`
2. Make sure the `.clarity` directory exists
3. Check that all dependencies are installed: `pip install -r requirements.txt`

## Example Conversation



See [examples/conversation_example.md](https://github.com/Aparnap2/clarification_agent/blob/main/examples/conversation_example.md) for a complete example of how the agent guides you through project planning.
