# ChatWilly: My AI Interview Agent

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Deployed_with-Docker-2496ED?style=flat&logo=docker)](https://www.docker.com/)
[![Qdrant](https://img.shields.io/badge/Vector_DB-Qdrant-FE3C88?style=flat&logo=qdrant)](https://qdrant.tech/)

## What is this?
**ChatWilly** is a full-stack, Agentic RAG (Retrieval-Augmented Generation) application designed to act as my digital clone for job interviews.

Instead of reading a static PDF resume, recruiters and engineering managers can chat directly with this AI. The agent uses my real background, projects, and skills to answer technical, behavioral, and logistical questions exactly as I would.

## Architecture & Tech Stack
This project is built as a **Monorepo** following Clean Architecture principles, strictly separating the offline data ingestion from the runtime API.

*   **Runtime Backend:** Python 3.13+, FastAPI, LangGraph.
*   **Data Pipeline (ETL):** Python, LangChain, Pydantic Structured Output.
*   **Vector Database:** Qdrant.
*   **Caching & Rate Limiting:** Redis.

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
    *   The frontend limits the conversation context to the last 5 messages.
4.  **Strict Rate Limiting (Anti-Abuse):** The FastAPI backend connects to Redis to track incoming requests.

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
REDIS__URL=redis://redis:6379

# Guardrail Model
GUARDRAIL_MODEL__API_KEY=YOURAPIKEY
GUARDRAIL_MODEL__BASE_URL=YOURBASEURL

# Response Agent Model
RESPONSE_AGENT_MODEL__API_KEY=YOURAPIKEY
RESPONSE_AGENT_MODEL__BASE_URL=YOURBASEURL

# Embedding Model & Qdrant (for RAG Retrieval)
EMBEDDING_MODEL__API_KEY=YOURAPIKEY
EMBEDDING_MODEL__MODEL_NAME=text-embedding-3-small
QDRANT__URL=http://qdrant:6333
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
