# Clarification Agent

This project is an AI-powered agent that clarifies ambiguous user queries, gathers missing information, and provides actionable, context-aware responses. It leverages LangGraph to create a modular and extensible architecture for building conversational AI applications.

## Features

- **Multi-Turn Clarification Dialog:** Asks follow-up questions to refine user intent.
- **Document & Web Search:** Retrieves information from local documents and the web.
- **Stateful Conversations:** Maintains conversation history for coherent interactions.
- **Tool-Calling & Conditional Routing:** Dynamically chooses between clarifying, searching, or answering.
- **Streamlit UI:** Provides a user-friendly interface for interacting with the agent.

## Getting Started

### Prerequisites

- Python 3.8+
- Poetry for dependency management

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/clarification-agent.git
   cd clarification-agent
   ```

2. **Install dependencies:**
   ```bash
   poetry install
   ```

3. **Set up environment variables:**
   Create a `.env` file in the root directory and add the following:
   ```
   OPENAI_API_KEY="your-openai-api-key"
   ```

### Running the Application

```bash
poetry run streamlit run app.py
```
