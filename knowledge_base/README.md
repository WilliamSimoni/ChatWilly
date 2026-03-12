# 🧠 ChatWilly Knowledge Base (ETL Pipeline)

This module contains the **Offline Data Pipeline (ETL)** for ChatWilly, an AI Assistant built with RAG (Retrieval-Augmented Generation) that acts as my digital clone.

Following **Clean Architecture** principles, this data ingestion pipeline is strictly separated from the Runtime API (FastAPI/LangGraph). It is responsible for parsing raw documents (CVs, cover letters, project descriptions), structuring them semantically using LLMs, and injecting them into a Vector Database (Qdrant).

## 🏗 Architecture & Workflow

The pipeline is split into a **2-Step Process** to allow for a "Human-in-the-loop" review phase and guarantee data quality.

### Step 1: Semantic Extraction (`processor.py`)
1. Reads raw documents (`.pdf`, `.docx`, `.txt`) from the `/docs` folder.
2. Uses an LLM (via LangChain) to generate a **Global Document Summary**.
3. Extracts self-contained narrative chunks based on the **STAR method** (Situation, Task, Action, Result) in the first person.
4. Categorizes data and generates keywords for future Hybrid Search.
5. Saves the output as easily readable `.yaml` files in the `/staging` folder.

> 💡 **Why Staging?** Saving to YAML allows manual review, editing, and anonymization of sensitive data (NDA compliance) before vectorizing.

### Step 2: Vector Ingestion (`loader.py`)
1. Reads the parsed `.yaml` files from the `/staging` folder.
2. Applies the **Contextual Embeddings** technique: it prepends the global summary to each chunk during the embedding phase to prevent "Context Loss", but saves them as separate metadata fields in the database.
3. Generates deterministic UUIDs via MD5 hashing to ensure **Idempotency** (rerunning the script won't duplicate data).
4. Cleans up orphaned vectors (if a staging file is deleted, its vectors are automatically removed from Qdrant).
5. Upserts vectors and metadata payloads to **Qdrant**.

## 🚀 Key Engineering Features
* **Metadata Filtering:** Creates Qdrant payload indexes for `category`, `keywords`, and `filename` for lightning-fast retrieval.
* **Context Preservation:** Avoids the classic RAG issue of "fragmented sentences" by forcing the LLM to act as a biographer, preserving the "Tone of Voice" and human anecdotes.
* **Agnostic Models:** Fully configurable via Pydantic Settings. Easily switch between OpenAI APIs and Local Models (e.g., LM Studio, Ollama).
