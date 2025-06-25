# 🧠 Clarification Agent

A self-aware AI assistant that guides you through all stages of planning a project — so you don't fall into vibe-coding, scope creep, or unclear design.

## Overview

The Clarification Agent helps you:
- **Clarify** project goals and requirements
- **Trim** scope to focus on MVP features
- **Validate** assumptions and detect hallucinations
- **Reason** through technology choices
- **Plan** development tasks
- **Output** structured data for further development

## Getting Started

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Streamlit UI
streamlit run app.py

# Start a new project
python clarify_flow.py --project your-project-name
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
- OpenRouter (Gemini, Claude) - Language models