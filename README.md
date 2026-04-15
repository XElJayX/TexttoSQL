# Schema-Aware RAG for Text-to-SQL

A production-style Text-to-SQL system that uses **schema-aware Retrieval-Augmented Generation (RAG)** to scale across large databases. Instead of dumping entire schemas into the prompt, this system intelligently retrieves only the most relevant tables before generating SQL.

---

## 🚀 Why This Project?

Most Text-to-SQL demos fail in real-world settings because they:
- Include the entire database schema in the prompt ❌
- Don’t scale beyond a handful of tables ❌
- Lack evaluation and observability ❌

This project solves those problems by:
- ✅ Retrieving only relevant schema components using embeddings
- ✅ Generating accurate SQL with minimal context
- ✅ Evaluating performance with a structured benchmark
- ✅ Tracking LLM behavior with observability tools

---

## 🧠 Key Features

### 1. Schema-Aware RAG
- Converts database schema (tables, columns, relationships) into embeddings
- Uses similarity search to retrieve only relevant tables
- Reduces prompt size and improves SQL accuracy

### 2. End-to-End Text-to-SQL Pipeline
- Natural language → relevant schema → SQL query → execution → result
- Built with modular and extensible architecture

### 3. Evaluation Framework
- 50+ benchmark questions across:
  - Simple SELECT queries
  - Aggregations
  - JOINs
  - Nested queries
- Metrics:
  - Execution accuracy
  - Query correctness
  - Complexity-based breakdown

### 4. Observability (LangSmith)
- Trace LLM calls
- Debug prompt failures
- Analyze retrieval quality

### 5. Production-Ready Deployment
- FastAPI backend
- Dockerized services
- Deployable on Railway or similar platforms

---

## 🏗️ Tech Stack

| Layer              | Tools Used                          |
|-------------------|------------------------------------|
| Database          | PostgreSQL                         |
| ORM               | SQLAlchemy                         |
| Vector Store      | pgvector                           |
| LLM Orchestration | LangChain / LlamaIndex             |
| API               | FastAPI                            |
| Deployment        | Docker + Railway                   |
| Observability     | LangSmith                          |

