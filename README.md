# PRD: Clarification Agent (Code‑First, Python)

## Overview
Build a pre‑development “Clarification Agent” that ingests early requirements artifacts (PRD/BRD/user stories/notes), auto‑generates prioritized clarification questions, gap maps, and risk flags, and persists agent state across iterative sessions. The system is built with FastAPI backend, LangGraph for agent workflow, PydanticAI for typed tool-calling and structured outputs, OpenRouter for multi‑model LLM access, Crawl4AI for optional web context capture, SQLite for LangGraph checkpoints, Neo4j+Graphiti for knowledge-graph memory, and Streamlit for a lightweight analyst UI.[1][2][3][4][5][6][7][8][9][10][11][12][13][14][15][16]

## Goals and Non‑Goals
- Goals
  - Reduce ambiguous requirements by generating targeted questions and missing acceptance criteria automatically.[1]
  - Persist agent state per document/thread to support multi‑turn refinement and auditability.[6][7][8]
  - Enable optional web crawling to ground clarifications with public references when requested.[3][4][5]
  - Provide a simple UI for PM/BA usage and an API for integration with docs/Jira later.[13][14][15][16]
- Non‑Goals
  - Not a full ALM integration in v1 (Jira/Confluence connectors later).
  - Not a general-purpose RAG platform; focused on discovery/clarification.

## Users and Use Cases
- Primary: Product managers, business analysts, tech leads in discovery.
- Use cases
  - Upload PRD draft → get Top‑N clarification questions, gap map, risks.
  - Iterate with answers → agent updates state and re‑prioritizes.
  - Optional: crawl referenced URLs to validate constraints or gather definitions.[4][5][3]

## Key Product Requirements
- Input: text uploads or pasted content; optional list of URLs for context crawling.[3][13]
- Output:
  - Prioritized clarification questions with categories and rationales.
  - Gap map: functional vs non‑functional vs data vs integration vs compliance gaps.
  - Acceptance criteria suggestions (testable, measurable).
  - Risk flags with feasibility notes and next steps.
- Persistence:
  - Per‑thread state via LangGraph checkpointer on SQLite for local/dev; supports async use.[7][8][9][10][17][18][6]
  - History view with checkpoint list, resume from checkpoint.[17][6]
- Knowledge Memory:
  - Optional: extract entities/relations from inputs and store triples in Neo4j via Graphiti for cross‑document memory and queries.[11][12]
- API and UI:
  - FastAPI JSON endpoints for ingestion, analysis, state/history, and crawl; Streamlit UI for analysts.[14][15][16][13]
- Observability:
  - Typed outputs enforced by PydanticAI; model logs; error tracing; deterministic formats.[19][1]
- Privacy:
  - No data persistence beyond checkpoints and explicit graph storage unless enabled; redact secrets.

## Success Metrics
- ≥50% of generated questions accepted or lightly edited by pilot teams.
- 30% reduction in time to “clarity‑ready” PRD across pilot docs.
- ≤15s latency on 4–6 page documents with baseline model.

***

# System Architecture

## Components
- FastAPI service: core HTTP API, routers per domain.[15][14]
- LangGraph agent workflow: stateful graph of nodes (Heuristics → LLM Clarifier → Gap/Risk → Optional Crawl → Memory Upsert → Synthesis), checkpointed to SQLite.[8][9][10][18][6][7][17]
- PydanticAI agent shells around LLM calls with strict schemas and tool functions (crawl, KG upsert, rule checks).[19][1]
- OpenRouter LLM client for multi‑model routing/fallbacks.[2]
- Crawl4AI micro‑service or in‑process asynchronous crawler.[5][4][3]
- Neo4j via Graphiti for knowledge graph memory.[12][11]
- Streamlit front‑end that calls FastAPI endpoints.[16][13]

## Data Stores
- SQLite: LangGraph checkpointer tables for state/history.[6][7][8][17]
- Neo4j: entities, relations, episodes (optional feature flag).[11][12]

***

# Workflow (Happy Path)

1) Ingest
- POST /analyze with document text and optional URLs/model preferences.
- Create/get thread_id; run LangGraph with SqliteSaver checkpointer.[7][8][6]

2) Pre‑LLM Heuristics
- Rules detect vague terms (TBD, scalable, fast), missing AC, undefined actors. Writes recorded to checkpoint writes.[17][6]

3) LLM Clarifier
- PydanticAI agent calls OpenRouter to generate:
  - Top‑N questions (prioritized).
  - Acceptance criteria suggestions per requirement.
  - Initial gap and risk draft.[2][1]

4) Optional Crawl
- If URLs provided or user toggles “auto‑context,” Crawl4AI fetches pages concurrently; converts to Markdown/JSON snippets for grounding.[4][5][3]

5) Knowledge Graph Upsert (optional)
- Extract entities/relationships from doc and generated outputs; upsert to Neo4j via Graphiti; store “Episode” provenance.[12][11]

6) Synthesis
- Combine heuristics, LLM outputs, crawl snippets, and KG pointers into structured Pydantic response; write checkpoint.

7) UI/Iteration
- Streamlit displays questions/gaps/risks; user answers questions; POST /answer updates thread state; re‑run steps 3–6 focusing on unresolved items.[13][16][6]

***

# Detailed Requirements

## Functional
- Create thread: POST /threads → thread_id.
- Analyze: POST /analyze {thread_id?, document, urls?, options} → structured report.
- Answer follow‑up: POST /threads/{thread_id}/answers → re‑prioritized report.
- Fetch state/history: GET /threads/{thread_id}/state, /history → list of checkpoints and snapshots.[6][17]
- Crawl: POST /crawl {urls} → parsed markdown/JSON.[5][3][4]
- Graph search: GET /graph/query?q=… (optional) to surface related prior entities/episodes.[11][12]

## Non‑Functional
- Performance: ≤15s p50 for standard docs; crawl budget controlled.
- Concurrency: Async endpoints for crawling/LLM calls where viable.[14][17][6]
- Reliability: Checkpointer ensures resumability; typed responses via schemas.[1][6]
- Security: API key via headers; redact secrets; allow local mode with no remote calls.
- Observability: request IDs, checkpoint IDs, model and cost metadata.

***

# Technical Design (Code‑First)

## Key Libraries
- FastAPI, Uvicorn, Pydantic v2, PydanticAI, LangGraph, langgraph‑checkpoint‑sqlite, OpenRouter SDK/HTTP, Crawl4AI, Neo4j Python driver, Graphiti‑core, Streamlit.[8][16][2][3][4][5][7][12][13][14][1][6][11]

## Package Layout
- app/
  - main.py (FastAPI init, routers)[15][14]
  - routers/
    - threads.py (create/list/history/state)
    - analyze.py (ingest, answer)
    - crawl.py
    - graph.py
  - agent/
    - graph.py (LangGraph definition, nodes, edges)
    - schemas.py (Pydantic models for IO)[1]
    - llm.py (PydanticAI agent + OpenRouter client)[2][1]
    - heuristics.py (regex/keyword checks)
    - memory.py (Graphiti integration)[12][11]
    - checkpoint.py (SqliteSaver init)[7][8][17][6]
  - services/
    - crawl.py (Crawl4AI async functions)[3][4][5]
    - state.py (wrap LangGraph invoke/ainvoke)
  - config.py (env, model map)
- ui/
  - app.py (Streamlit; calls FastAPI)[16][13]
- infra/
  - neo4j_setup.py (build indices/constraints)[11]

## LangGraph Checkpointing
- Use langgraph‑checkpoint‑sqlite’s SqliteSaver/AsyncSqliteSaver; configure thread_id per doc and retain history; beware import path changes across versions.[9][10][18][8][17][6][7]
- StateSnapshot retrieval via graph.get_state(thread_config).[6]

## PydanticAI Agent
- Define strict output schemas: ClarificationQuestion, GapItem, RiskItem, ClarificationReport; enforce JSON outputs; tool functions for crawl and KG write.[19][1]

## OpenRouter LLM
- Single endpoint, multi‑model routing with fallbacks; include model hints per task (e.g., general clarifier vs critic); pass system prompt and few‑shot; handle API key in headers.[2]

## Crawl4AI
- AsyncWebCrawler with BrowserConfig and CrawlerRunConfig; convert to Markdown; CacheMode control; per‑URL timeouts.[4][5][3]

## Graphiti + Neo4j
- Initialize Graphiti, build indices once; upsert triples with provenance “Episode”; secure Neo4j credentials; expose minimal query endpoint.[12][11]

## Streamlit
- Sidebar for model selection and crawl toggle; upload text; table of questions with status; buttons to send answers back to FastAPI; long‑running calls via async or polling.[13][16]

***

# API Sketches

- POST /threads → {thread_id}
- GET /threads/{thread_id}/history → [{checkpoint_id, ts}][17][6]
- GET /threads/{thread_id}/state?checkpoint_id=… → StateSnapshot[6]
- POST /analyze
  - Body: {thread_id?, text, urls?, options{top_n, crawl, use_kg}}
  - Resp: ClarificationReport {questions[], gaps[], risks[], acceptanceCriteria[], provenance}
- POST /threads/{thread_id}/answers
  - Body: {answers:[{question_id, answer_text}]}
  - Resp: updated ClarificationReport
- POST /crawl {urls[]} → [{url, markdown, meta}][5][3][4]
- GET /graph/query?q=… → {entities, relations, episodes}[11][12]

***

# Data Models (Pydantic)

- ClarificationQuestion: id, text, category, priority, rationale, blocking(bool).
- GapItem: id, type(functional|nfr|data|integration|compliance), description, impact, suggested_AC?.
- RiskItem: id, severity, area, rationale, mitigation.
- AcceptanceCriterion: id, story_ref?, criterion, measurable(bool), test_outline?.
- ClarificationReport: questions[], gaps[], risks[], acceptanceCriteria[], sources[], checkpoint_id.

Schemas validated by PydanticAI agent for dependable structure.[19][1]

***

# LangGraph DAG (v1)

- Nodes:
  - preprocess_rules (heuristics)[—]
  - generate_questions (LLM via PydanticAI → OpenRouter)[1][2]
  - derive_gaps_and_risks (LLM with schema)[1]
  - optional_crawl (tool node → Crawl4AI)[3][4][5]
  - kg_upsert (tool node → Graphiti/Neo4j)[12][11]
  - synthesize_report (merge, sort, dedupe, assign priorities)
- Edges:
  - preprocess_rules → generate_questions → derive_gaps_and_risks
  - options.crawl? → optional_crawl → synthesize_report
  - options.use_kg? → kg_upsert (side‑effect) → synthesize_report
- Checkpointer: SqliteSaver with thread_id; list/get state for resume.[10][18][9][8][7][17][6]

***

# Prompts and Guardrails

- System role: “Requirements analyst + senior engineer; produce testable, prioritized clarifications and gaps; be concise; output strictly JSON to schema.”
- Few‑shot: Examples of vague requirement → pointed questions, measurable AC.
- Policies:
  - Limit to Top‑10 unless user increases.
  - Tag each question with category, rationale, and blocking flag.
  - Prefer measurable AC (with clear thresholds).
- Validation:
  - PydanticAI validates model outputs; retry/repair on schema errors.[1]

***

# Deployment Plan

- Dev
  - Local SQLite for checkpoints; local Neo4j Desktop or Aura free tier for KG; .env for OpenRouter key.[8][7][2][6][11][12]
- Run
  - Uvicorn for FastAPI; Streamlit separate process; CORS enabled for localhost.[14][16][13]
- Prod (phase 2)
  - Containerize services; move to Postgres checkpointer if needed; managed Neo4j; add auth and rate limiting.[6]
  
***

# Risks and Mitigations

- LLM output variance → enforce schemas with PydanticAI, constrain prompts, and add repair step.[1]
- Checkpointer version drift/import changes → pin langgraph and checkpoint lib versions; follow current import paths.[9][10][7][8][6]
- Crawl reliability/latency → strict timeouts, concurrency limits; cache strategy.[4][5][3]
- KG complexity → feature flag KG; provide minimal upsert and simple query first.[11][12]

***

# Milestones

- Week 1: Core API + LangGraph + SQLite checkpoints + PydanticAI schemas + OpenRouter integration; Streamlit MVP.[16][7][8][13][2][6][1]
- Week 2: Crawl4AI optional context; Graphiti KG optional; history/resume; basic auth.[5][3][4][12][11]
- Week 3: Pilot, metrics instrumentation, prompt tuning.

***

# Example Configuration Snippets

- Initialize SqliteSaver checkpointer (sync/async) and attach to graph; use thread_id in config for state tracking; ensure version‑correct import paths and async variants when streaming.[10][9][7][8][17][6]
- PydanticAI agent definition with tools for crawl() and kg_upsert(); model routed via OpenRouter with fallback policy.[2][1]
- Crawl4AI AsyncWebCrawler with BrowserConfig and CrawlerRunConfig; export markdown snippets; CacheMode as BYPASS for freshness.[3][4][5]
- Graphiti setup: build indices/constraints once; upsert triples with Episode metadata.[12][11]
- Streamlit consuming FastAPI endpoints with simple forms and tables; dual‑app pattern (backend API + Streamlit UI).[13][16]

