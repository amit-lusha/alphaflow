# AlphaFlow

AlphaFlow is an AI-powered financial analysis agent that combines Large Language Models (LLM), Retrieval-Augmented Generation (RAG), and real-time financial tools to provide market insights. It is built with LangGraph and exposed as an MCP (Model Context Protocol) server.

## Features

- **Market Data**: Fetches real-time stock prices and currency info (via `yfinance`).
- **Company Profiles**: Retreives fundamental data (sector, market cap, summaries).
- **Financial RAG**: Embeds and searches financial news articles to provide context (e.g., "Why is TSLA moving?").
- **Web Analysis**: Reads and analyzes content from specific URLs.
- **MCP Server**: Exposes the full agent as a tool usable by other MCP clients (like Claude Desktop or Gemini).

## Architecture

The project follows a modular structure:

| Directory | Purpose |
| :--- | :--- |
| **`src/alphaflow/core/`** | Foundation: Config (`config.py`), State (`state.py`), Prompts (`prompts.py`). |
| **`src/alphaflow/services/`** | Integrations: LLM Factory (`llm.py`), Vector DB (`rag.py`). |
| **`src/alphaflow/workflows/`** | Orchestration: LangGraph definition (`entrypoint.py`). |
| **`src/alphaflow/agents/`** | Logic: The Analyst agent (`analyst.py`) deciding which actions to take. |
| **`src/alphaflow/tools/`** | Capabilities: Callable tools (`finance.py` for stock/news). |
| **`src/alphaflow/scripts/`** | Utilities: Helper scripts (e.g., `ingest.py`). |

## Installation & Setup

1.  **Prerequisites**: Python 3.10+ and `uv` (recommended) or `pip`.
2.  **Environment Variables**:
    Create a `.env` file in the root directory:
    ```env
    GOOGLE_API_KEY=your_gemini_api_key
    # Optional
    TAVILY_API_KEY=your_tavily_key
    ```
3.  **Install Dependencies**:
    ```bash
    uv sync
    # Or with pip
    pip install -r pyproject.toml
    ```

## Usage

### 1. Data Ingestion (RAG)
Before asking questions about news, ingest mock data (or connect your own source):
```bash
PYTHONPATH=src uv run src/alphaflow/scripts/ingest.py
```

### 2. CLI Interface
Run the agent directly in your terminal:
```bash
PYTHONPATH=src uv run src/alphaflow/main.py
```

### 3. MCP Server
Start the MCP server to expose the agent to other tools:
```bash
PYTHONPATH=src uv run src/alphaflow/server.py
```

## Configuration

Settings are managed in `src/alphaflow/core/config.py` using Pydantic. You can override defaults via environment variables.

*   `LLM_MODEL_NAME` (Default: `gemini-2.0-flash`)
*   `SEARCH_K_RESULTS` (Default: `3`)

## Development

*   **Logging**: Logs are printed to stdout with `INFO` level by default.
*   **Graph Visualization**: The agent uses a ReAct-style loop (Analyst <-> Tools).
