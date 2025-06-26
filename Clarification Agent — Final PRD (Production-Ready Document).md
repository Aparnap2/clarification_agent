# 🧠 Clarification Agent — Final PRD (Production-Ready Document)

### Owner: Aparna Pradhan

### Version: `v1.0`

### Purpose: Personal developer tool to clarify, scope, validate, and scaffold fullstack/AI projects before coding begins

### Output Format: `.clarity/*.json`, `.plan.yml`, `mcp.yaml`, `README.md`, `architecture.md`

### Usage Mode: Run before every new project or feature cycle

------

## 📌 1. Objective

Create a **self-aware AI assistant** that guides me (Aparna) through all stages of planning a project — so I don't fall into vibe-coding, scope creep, or unclear design.

> The agent will **clarify**, **trim**, **validate**, **reason**, **plan**, and **output** structured data for further development using Windsurf and `mcp`.

------

## 🧠 2. Core Functionalities

| Function                  | Description                                                  |
| ------------------------- | ------------------------------------------------------------ |
| 🧠 Clarification           | Asks structured questions to deeply understand the project goal |
| 🚫 Scope Reduction         | Detects and removes anything not part of the MVP             |
| 🔍 Hallucination Detection | Uses Crawl4AI or pattern-based checks to spot false assumptions |
| 🧠 Memory Structuring      | Stores goals, tools, features, tasks into `.clarity/project.json` and Neo4j |
| 📂 File Mapping            | Maps each feature to folders, components, and code responsibilities |
| 📋 Task Planning           | Outputs `.plan.yml` with atomic dev tasks                    |
| 🧾 Documentation           | Outputs auto-generated `README.md`, `architecture.md`, `mcp.yaml` |



------

## 🔁 3. Workflow (LangGraph-based)

```
mermaidCopyEditgraph TD
Start[Start New or Existing Project] --> ClarifyIntent
ClarifyIntent --> NotBuilder[Trim Non-MVP Ideas]
NotBuilder --> MVPScoper
MVPScoper --> StackSelector
StackSelector --> Reasoner[Explain Tool/Stack Decisions]
Reasoner --> FileMapBuilder
FileMapBuilder --> TaskPlanner
TaskPlanner --> Exporter[Write all to disk]
Exporter --> End[User opens Windsurf]
```

------

## 🧩 4. LangGraph Node Definitions

| Node ID          | Role & Description                                           |
| ---------------- | ------------------------------------------------------------ |
| `Start`          | Check if `.clarity/project.json` exists; else begin fresh    |
| `ClarifyIntent`  | Ask: “What is this project?”, “Who's it for?”, “What's the expected result?” |
| `NotBuilder`     | Ask: “What **won’t** be included in MVP?” Filter out non-essential features |
| `MVPScoper`      | Define and confirm MVP features with rationale               |
| `StackSelector`  | Ask for stack/tools; validate necessity; offer leaner alternatives if needed |
| `Reasoner`       | For each decision, ask “Why?”; reject unjustified tools      |
| `FileMapBuilder` | Maps features to code modules, e.g. `src/components/BotUI.tsx` |
| `TaskPlanner`    | Breaks down the clarified MVP into atomic dev tasks in `.plan.yml` |
| `Exporter`       | Writes `.clarity/project.json`, `.plan.yml`, `mcp.yaml`, `README.md`, etc. |



------

## 📂 5. Output Folder Structure

```
bashCopyEditclarifier-agent-output/
├── chatbot-builder/
│   ├── .clarity.json             # Memory object of goals, stack, features
│   ├── .plan.yml                 # Modular task list
│   ├── mcp.yaml                  # Tool config for MCP agent
│   ├── README.md                 # Clean summary, goals, features, tech
│   ├── architecture.md           # File mapping + decisions
│   └── memory.graphml            # Optional Graphiti/Neo4j export
```

------

## ✅ 6. Output Contract Example

### `.clarity/chatbot-builder.json`

```
jsonCopyEdit{
  "project": "chatbot-builder",
  "goals": ["Build a chatbot SaaS for Slack & WhatsApp"],
  "mvp_features": [
    "Drag-drop flow editor",
    "Integration manager (Slack/WA)",
    "Realtime message simulator"
  ],
  "excluded_features": [
    "Multilingual NLP",
    "Custom domain",
    "Voice support"
  ],
  "target_user": "non-technical founders",
  "tech_stack": [
    "Next.js",
    "Supabase",
    "LangGraph",
    "Pinecone",
    "OpenRouter"
  ],
  "decisions": {
    "vector_db": "Pinecone chosen over Redis for semantic search",
    "frontend": "Next.js for SSR + static hosting on Vercel",
    "auth": "Supabase magic link for MVP simplicity"
  },
  "file_map": {
    "src/pages/index.tsx": "Main dashboard",
    "src/components/FlowEditor.tsx": "Drag-drop UI",
    "src/lib/pinecone.ts": "Vector embedding helper",
    "src/api/integrations/slack.ts": "Slack webhook receiver"
  }
}
```

------

### `.plan.yml`

```
yamlCopyEditplan:
  - title: "Build drag-drop editor"
    file: "src/components/FlowEditor.tsx"
    estimate: "2h"
    priority: 1
  - title: "Set up Pinecone indexing"
    file: "src/lib/pinecone.ts"
    estimate: "1.5h"
    priority: 2
```

------

### `mcp.yaml`

```
yamlCopyEditproject: chatbot-builder
stack:
  frontend: Next.js
  backend: API Routes (Next)
  db: Supabase
  vector: Pinecone
  auth: Supabase magic links
scripts:
  dev: next dev
  build: next build
```

------

### `README.md` (Auto-generated)

```
markdownCopyEdit# Chatbot Builder SaaS

A no-code chatbot builder that allows users to create and deploy bots on Slack and WhatsApp. Built for non-technical founders.

## 🧠 Features (MVP)

- Drag & drop flow editor
- Slack and WhatsApp integration
- Realtime message testing

## 🔧 Tech Stack

- Next.js
- Supabase
- LangGraph (for agent flows)
- Pinecone (vector memory)
- OpenRouter (LLMs)

## ❌ Not Included

- Voice
- NLP support
- Multilingual

## 📁 Project Structure

- `src/components/FlowEditor.tsx`: Bot editor UI
- `src/api/integrations/slack.ts`: Slack handler
- `src/lib/pinecone.ts`: Vector ops

> Created with Clarifier Agent.
```

------

## 🔁 7. Coding Agent Integration Plan

| Tool                | How it uses Clarifier Output                                 |
| ------------------- | ------------------------------------------------------------ |
| **Windsurf**        | Reads `.clarity.json` for memory; uses `.plan.yml` to guide coding session |
| **MCP**             | Uses `mcp.yaml` and `.plan.yml` to scaffold folders and logic |
| **LangGraph Agent** | Can re-run flow if clarification is updated mid-build        |
| **Streamlit UI**    | Renders agent chat, memory graph, and export tools           |
| **Graphiti/Neo4j**  | (Optional) Loads clarified decision graph for querying or visualization |



------

## 🚦 8. Command Flow (for Agent Execution)

```
bashCopyEdit# Start from scratch
python clarify_flow.py --project ocr-health-app

# Update memory only
python clarify_flow.py --update chatbot-builder

# View Streamlit clarification UI
streamlit run app.py

# Scaffold project after clarification
mcp plan chatbot-builder
windsurf generate scaffold --from .plan.yml
```

------





------

## 🛠️ 9. Tech Stack (Clarification Agent)

| Layer                         | Tool / Library                      | Purpose                                                      |
| ----------------------------- | ----------------------------------- | ------------------------------------------------------------ |
| **UI**                        | `Streamlit`                         | Minimal, interactive chat + memory view interface            |
| **Agent Framework**           | `LangGraph`                         | Graph-based modular decision engine for clarifier flow       |
| **Agent Roles**               | `CrewAI`                            | Define Clarifier, Validator, Reasoner, Reflector, Planner    |
| **Data Models**               | `Pydantic`                          | Structuring goals, plans, features, constraints              |
| **Embedding / LLMs**          | `OpenRouter` (`deepseek/deepseek-chat-v3-0324:free`)   | Language modeling, reasoning, clarifying                     |
| **Web Crawler Tool**          | `Crawl4AI`                          | Hallucination detection via validation against real-world docs |
| **Vector Memory**             | `Graphiti` + `Neo4j`                | Store and visualize decision-memory as a queryable graph     |
| **Filesystem Output**         | `.clarity/*.json`, `.plan.yml`      | Agent output spec; used by downstream tools (`mcp`, Windsurf) |
| **File Generator**            | `mcp`                               | Scaffolds dev folders, files, and planning from agent output |
| **Editor Integration**        | `Windsurf`                          | Dev environment; shows clarifier memory; enforces decisions  |
| **Optional OCR/Docs**         | `Tesseract.js`, `pdf2image`, `docx` | For OCR-based project types (e.g., Health OCR App)           |
| **Vector Search (if needed)** | `Pinecone`, `Qdrant`, `Weaviate`    | For projects needing semantic search / memory recall         |



------

### 🧩 Module-wise Breakdown

| Module                     | Tech Used                                                    |
| -------------------------- | ------------------------------------------------------------ |
| `streamlit UI`             | `streamlit`, `st-chat`, `matplotlib` (for graph view)        |
| `langgraph_flow.py`        | `LangGraph`, `CrewAI`, `openai-function-calling` schema      |
| `schema/knowledge.py`      | `Pydantic`, `typing`                                         |
| `memory/graphiti_store.py` | `Neo4j`, `graphiti-python-client`                            |
| `validation/`              | `Crawl4AI`, `regex`, `requests`                              |
| `codegen/`                 | `mcp`, `fs`, `os`, `jinja2` (for templating files)           |
| `windsurf_plugin.ts`       | VS Code sidebar extension for inline memory + scope enforcement |



------

### 📦 Environment Setup

Python `requirements.txt`:

```
txtCopyEditlanggraph
crewai
openrouter
pydantic
streamlit
neo4j
graphiti
crawl4ai
jinja2
pyyaml
```

JS (for Windsurf plugin):

```
tsCopyEdit"@types/node": "^20.x",
"react": "^18.x",
"vscode": "latest"
```

------

With this stack, the Clarifier Agent is fully:

- **Agentic** (graph-based decisions)
- **Grounded** (fact-checked)
- **Memory-aware** (persistent and queryable)
- **Workflow-integrated** (feeds `mcp`, Windsurf, VS Code)
- **Self-contained** (can run locally or be hosted)

## 🧠 Final Notes for Agent Builders

- Never generate or scaffold anything until:
  - MVP is **explicitly confirmed**
  - Stack/tool choices are **justified**
  - Every feature is **mapped to a file**
- All memory must be exportable to `.clarity/*.json`
- If any feature or stack is unjustified, the agent must:
  - Ask “Do you need this?”
  - Suggest leaner options
- Prefer modular output (one module → one feature → one file)
- Never insert external LLM calls in code unless confirmed



