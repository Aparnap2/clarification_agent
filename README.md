# 🧠 Clarification Agent

A conversational AI assistant that guides you through all stages of planning a project — so you don't fall into vibe-coding, scope creep, or unclear design.

## Overview

The Clarification Agent helps you through natural conversation:
- **Clarify** project goals and requirements through dialogue
- **Trim** scope to focus on MVP features with AI guidance
- **Validate** assumptions and detect hallucinations
- **Reason** through technology choices from multiple perspectives
- **Plan** development tasks with AI assistance
- **Output** structured data for further development

## Multi-Perspective Approach

The agent takes on different roles during the conversation to provide comprehensive guidance:

- **Product Manager**: Focuses on user needs and product features
- **Tech Lead**: Evaluates technical feasibility and architecture
- **Business Analyst**: Considers business value and market fit
- **UX Designer**: Ensures good user experience and interface
- **QA Engineer**: Identifies potential issues and edge cases

## Getting Started

```bash
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

### How It Works

1. **Start a conversation** - Create a new project and start chatting with the agent
2. **Answer questions** - The agent will ask questions from different perspectives
3. **Review suggestions** - The agent will provide AI-powered suggestions
4. **Generate outputs** - When the conversation is complete, the agent generates all necessary files

### Note on AI Features

The agent uses LangGraph to manage the conversation flow and OpenRouter for AI capabilities. In a production environment, you would need to set up an OpenRouter API key:

```bash
cp .env.example .env
# Edit .env with your API key
```

## Output

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

See [examples/conversation_example.md](examples/conversation_example.md) for a complete example of how the agent guides you through project planning.