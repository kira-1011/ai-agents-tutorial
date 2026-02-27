# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A from-scratch AI agent framework in Python. Implements a simple agent loop that connects to a local LLM server (llama.cpp-compatible OpenAI API) with tool use and conversation memory.

## Commands

```bash
# Install dependencies (uses uv package manager)
uv sync

# Run the agent
uv run python main.py
```

## Architecture

The project has two files:

- **`agent.py`** — Core framework with four classes:
  - `Tool` — wraps a name, description, and callable function
  - `Memory` — fixed-size FIFO conversation history buffer
  - `Model` — holds model name, base URL, and generation params (max_tokens, temperature)
  - `Agent` — composes the above; builds a system prompt that includes tool descriptions and memory, then sends chat completions via `requests.post` to an OpenAI-compatible endpoint

- **`main.py`** — Entry point. Configures a model pointing at `localhost:12434` (Cortex or similar local LLM server), registers tools, and runs an interactive chat loop (ESC to exit).

## Key Details

- Python 3.12, managed with uv
- Dependencies: `requests` (HTTP), `keyboard` (input detection)
- The LLM server must be running locally before starting the agent (`http://localhost:12434/engines/llama.cpp/v1/chat/completions`)
- Default model: `ai/smollm2`
- Agent instructs the LLM to return tool calls as JSON (`{"tool": "name", "arguments": {...}}`) but tool execution is not yet wired up — the agent currently only generates completions
