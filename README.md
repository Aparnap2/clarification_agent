# 🧠 Clarification Agent

A self-aware AI assistant that guides you through all stages of planning a project — so you don't fall into vibe-coding, scope creep, or unclear design.

## Overview

The Clarification Agent helps you:
- **Clarify** project goals and requirements with AI-powered suggestions
- **Trim** scope to focus on MVP features
- **Validate** assumptions and detect hallucinations
- **Reason** through technology choices with AI-generated rationales
- **Plan** development tasks with AI assistance
- **Output** structured data for further development

## AI-Powered Features

- **Goal Suggestions**: AI analyzes your project description to suggest clear goals
- **MVP Feature Recommendations**: AI recommends essential features based on your goals
- **Scope Reduction**: AI suggests features to exclude from the MVP
- **Tech Stack Recommendations**: AI recommends appropriate technologies for your project
- **File Structure Generation**: AI creates a logical file structure based on your tech stack
- **Task Planning**: AI breaks down your project into atomic development tasks

## Getting Started

```bash
# Option 1: Use the run script (recommended)
./run.sh

# Option 2: Manual setup
# Install dependencies
pip install -r requirements.txt

# Run the Streamlit UI
streamlit run app.py

# Option 3: Use the CLI
python clarify_flow.py --project your-project-name
```

### Note on AI Features

This demo version uses simulated AI responses and doesn't require an API key. In a production environment, you would need to set up an OpenRouter API key:

```bash
cp .env.example .env
# Edit .env with your API key
```

## Output

The agent generates:
- `.clarity/*.json` - Project memory and structure
- `.plan.yml` - Development tasks
- `README.md` - Project documentation
- `architecture.md` - Technical decisions and file mapping

## Tech Stack

- LangGraph - Agent workflow
- Streamlit - User interface
- Pydantic - Data models
- OpenRouter (Claude, Gemini) - AI assistance