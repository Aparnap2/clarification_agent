# Dynamic Conversation Flow Implementation

## Overview

The Clarification Agent now supports dynamic conversation flow, where the LLM determines the next appropriate question or topic based on the current project state and conversation context. This provides a more natural and flexible planning experience compared to the static, predefined flow.

## Key Components

### 1. Dynamic Node Selection

The agent now uses the LLM to determine which node to execute next, rather than following a predefined sequence. This is implemented in:

- `_determine_next_node_with_llm()` in `agent_manager.py`
- `_determine_next_stage()` in `conversation_agent.py`

### 2. Dynamic Node Handler

A new `DynamicNode` class has been added that can generate questions and process responses based on the current project state. This allows for more flexible conversation flow and can handle node types that weren't predefined.

### 3. Enhanced LLM Integration

The `llm_helper.py` file has been updated to actually call the OpenRouter API instead of using static responses. This enables:

- Dynamic question generation
- Context-aware responses
- Intelligent project state updates

## How to Use

### Option 1: Dynamic CLI

Run the dynamic conversation CLI:

```bash
./dynamic_conversation.py
```

### Option 2: Streamlit UI

The Streamlit UI has been updated to support dynamic conversation flow:

```bash
streamlit run app_conversation.py
```

## Configuration

To use the LLM features, you need to set up an OpenRouter API key:

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your API key:
   ```
   OPENROUTER_API_KEY=your_api_key_here
   ```

## Fallback Mechanism

If the LLM call fails or returns invalid responses, the system will fall back to the static, predefined flow to ensure the conversation can continue.