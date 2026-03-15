# ChatWilly: My AI Interview Agent

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Deployed_with-Docker-2496ED?style=flat&logo=docker)](https://www.docker.com/)
[![Mistral AI](https://img.shields.io/badge/Model-Mistral_AI-FF6000?style=flat&logo=mistralai)](https://mistral.ai/)
[![Qdrant](https://img.shields.io/badge/Vector_DB-Qdrant-FE3C88?style=flat&logo=qdrant)](https://qdrant.tech/)
[![React](https://img.shields.io/badge/Frontend-React-61DAFB?style=flat&logo=react)](https://reactjs.org/)
[![Tailwind CSS](https://img.shields.io/badge/Styling-Tailwind_CSS-38B2AC?style=flat&logo=tailwind-css)](https://tailwindcss.com/)

## What is this?
**ChatWilly** is a full-stack, Agentic RAG (Retrieval-Augmented Generation) application designed to act as my digital clone for job interviews.

Instead of reading a static PDF resume, recruiters and engineering managers can chat directly with this AI. The agent uses my real background, projects, and skills to answer technical, behavioral, and logistical questions exactly as I would.

<p align="center">
  <img src="./assets/chatwilly_logo.png" width="800" alt="Application Screenshot">
</p>


## Architecture & Tech Stack
This project is built as a **Monorepo** following Clean Architecture principles, strictly separating the offline data ingestion from the runtime API.

*   **Runtime Backend:** Python 3.13+, FastAPI, LangGraph, **LiteLLM**.
*   **Data Pipeline (ETL):** Python, LangChain, Pydantic Structured Output.
*   **Vector Database:** Qdrant.
*   **Caching & Rate Limiting:** Redis.
*   **Frontend:** React (Vite), Tailwind CSS, Server-Sent Events (SSE) for streaming.

### Monorepo Structure
```text
.
├── backend/            # FastAPI Server, LangGraph Agent, and API routes
├── knowledge_base/     # Offline ETL Pipeline (CV parsing & Qdrant ingestion)
├── frontend/           # UI for the chat interface
└── docker-compose.yaml
```

## Key Features (Production-Ready)

1.  **Agentic Tool Calling (ReAct):** The AI doesn't just read a massive text file. It dynamically chooses between tools (e.g., `search_hard_skills`, `search_experiences`, `search_hr_questions`) based on the user's intent, querying specific metadata categories in the vector database.
2.  **High-Fidelity Data Pipeline (ETL):** My raw CVs and portfolios are processed by an offline pipeline. An LLM acts as my "Biographer", extracting self-contained narrative chunks (STAR method) and generating global summaries to prevent RAG "Context Loss" (Contextual Embeddings). Data is staged in YAML for human review and synced idempotently to Qdrant via MD5 hashing.
3.  **Cost & Context Guardrails:**
    *   A lightweight LLM router intercepts the user's input before hitting the main Agent. If the question is off-topic (e.g., *"Write me a recipe"*), the request is blocked, saving tokens and keeping the AI in character.
4.  **Strict Rate Limiting (Anti-Abuse):** The FastAPI backend connects to Redis to track incoming requests.
5.  **Model-Agnostic via LiteLLM:** Switching from Mistral to OpenAI or Anthropic is a 1-line change in the `.env` file, thanks to the LiteLLM abstraction layer.
---

## Running with Docker Compose

### 1️⃣ Prerequisites

Make sure you have installed:
- Docker
- Docker Compose (v2+)

Verify installation:
```bash
docker --version
docker compose version
```

### 2️⃣ Feed the Brain (Data Ingestion)
Before starting the backend, the AI needs its knowledge base! You must process the documents and load them into Qdrant.
👉 **[Read the Knowledge Base / ETL instructions here](./knowledge_base/README.md)**

### 3️⃣ Configure Environment Variables

Inside the `backend/` folder, create a `.env` file:
```
backend/.env
```

Example `.env`:
```env
DEBUG=True
APP_PORT=8000

# Database
REDIS__URL="redis://redis:6379"

# Guardrail Model (LiteLLM Format)
GUARDRAIL_MODEL__API_KEY="your-mistral-api-key"
GUARDRAIL_MODEL__BASE_URL="https://api.mistral.ai/v1/"
GUARDRAIL_MODEL__MODEL_NAME="mistral/mistral-small-2506"

# Response Agent Model (Mistral Large)
RESPONSE_AGENT_MODEL__API_KEY="your-mistral-api-key"
RESPONSE_AGENT_MODEL__BASE_URL="https://api.mistral.ai/v1/"
RESPONSE_AGENT_MODEL__MODEL_NAME="mistral/mistral-large-2512"

# Embedding Model (Example: Local Qwen via LM Studio/Ollama)
EMBEDDING_MODEL__BASE_URL="http://localhost:1234/v1"
EMBEDDING_MODEL__MODEL_NAME="text-embedding-qwen3-embedding-0.6b"
EMBEDDING_MODEL__API_KEY="not-needed"

# Qdrant Vector DB
QDRANT__URL="http://localhost:6333"
QDRANT__VECTOR_SIZE=1024
QDRANT__COLLECTION_NAME="chatwilly_brain"
```
*Note: Do **not** commit real API keys. Environment variables override values in `config.yaml`. Nested configuration uses `__` as delimiter (e.g. `REDIS__URL`).*

### 4️⃣ Optional: Edit `config.yaml`

File location:
```
backend/config.yaml
```
This file contains default configuration values such as Redis settings, model defaults (temperature, max tokens), and rate limits.

⚠ Configuration precedence (highest → lowest):
1. Environment variables (`.env`)
2. `config.yaml`
3. Default values in `settings.py`

### 5️⃣ Build and Start the Services

From the **project root directory** (where `docker-compose.yaml` is located):

```bash
docker compose up --build
```

This will:
- Build the backend image
- Start Redis & Qdrant
- Start the FastAPI backend
- Automatically connect backend to the databases

### 6️⃣ Access the Application

Once running:
- **API:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/docs

---

## Stop the Services

Stop containers:
```bash
docker compose down
```

Stop and remove volumes (including Redis and Qdrant data):
```bash
docker compose down -v
```

---
##  Let's Connect!
Feel free to ask ChatWilly anything about my skills, or reach out to me directly:
**LinkedIn:** [linkedin.com/in/william-simoni](https://www.linkedin.com/in/william-simoni-2b7127220/)
