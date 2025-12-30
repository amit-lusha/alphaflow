# 📈 AlphaFlow: Autonomous Financial Research System

**AlphaFlow** is a production-grade, multi-agent AI system designed to conduct deep financial research. Unlike simple chatbots, AlphaFlow orchestrates a team of specialized agents to combine quantitative market data (Technical) with qualitative news analysis (Fundamental), all managed by a Supervisor.

It features **Human-in-the-Loop** control, **State Persistence** via PostgreSQL, and full interoperability via the **Model Context Protocol (MCP)**.

---

## 🚀 Key Features

*   **🤖 Multi-Agent Orchestration**: A "Star Topology" graph where a Supervisor delegates tasks to specialized workers:
    *   **Technical Analyst**: Fetches live prices, market caps, and profiles (via `yfinance`).
    *   **Fundamental Researcher**: Performs RAG search on financial news and reads web content.
    *   **Publisher**: Synthesizes data into a structured JSON report.
*   **🧠 Hybrid Memory & RAG**:
    *   **Short-term**: Stateful conversation history stored in **PostgreSQL**.
    *   **Long-term**: Semantic search using **pgvector** to query ingested news articles.
*   **✋ Human-in-the-Loop (HITL)**: The agent drafts a report and **pauses execution**, waiting for human approval before publishing.
*   **🔌 MCP Integration**: Runs as an MCP Server, allowing it to be used natively inside **Claude Desktop**, **Cursor**, or the **Gemini CLI**.
*   **🐳 Production Ready**: Fully containerized with Docker, FastAPI, and Postgres.

---

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Language** | Python 3.12 (Managed by `uv`) |
| **Brain** | Google Gemini 2.0 Flash |
| **Orchestration** | LangGraph (Cyclic State Machine) |
| **Framework** | LangChain / Pydantic |
| **Database** | PostgreSQL 16 + `pgvector` extension |
| **API** | FastAPI (Async) |
| **Observability** | LangSmith (Tracing & Evaluation) |

---

## 📂 Project Structure

```text
src/alphaflow/
├── agents/             # The AI Personas
│   ├── supervisor.py   # Router logic
│   ├── technical.py    # Quantitative worker
│   ├── fundamental.py  # Qualitative worker
│   └── publisher.py    # Report generator
├── core/               # Configuration & Schemas
│   ├── prompts.py      # OOP-based Prompt definitions
│   └── schema.py       # Pydantic models for JSON output
├── services/           # External Integrations
│   ├── llm.py          # Gemini Singleton
│   └── rag.py          # Postgres Vector Store logic
├── workflows/          # The Graph
│   └── entrypoint.py   # LangGraph definition & wiring
├── tools/              # Capabilities (Search, WebReader, YFinance)
├── scripts/            # Utilities (Ingestion pipeline)
├── server.py           # FastAPI Application
└── main.py             # CLI Entrypoint