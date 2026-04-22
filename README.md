# Text-to-SQL — Natural Language Database Query System

A production-grade Text-to-SQL system that converts natural language questions into executable PostgreSQL queries using a schema-aware RAG pipeline, LLM orchestration, and a self-correction loop.

**Live Demo:** [texttosql-frontend.vercel.app](https://texttosql-frontend.vercel.app)  
**API Docs:** [texttosql-production-b579.up.railway.app/docs](https://texttosql-production-b579.up.railway.app/docs)

---

## What makes this different from a tutorial project

Most Text-to-SQL demos dump the entire schema into a prompt and call an LLM. This system does something meaningfully different:

- **Schema-aware RAG** — only retrieves the 3-4 most relevant tables for each question, not the entire schema. Scales to large databases without blowing the context window.
- **SQL validation layer** — every generated query is safety-checked and dry-run with `EXPLAIN` before execution. Dangerous operations (`DROP`, `DELETE`, `UPDATE`) are blocked.
- **Self-correction loop** — if the LLM generates invalid SQL, the error is fed back into a multi-turn conversation so the LLM can fix it.
- **Evaluation framework** — a 17-question golden test set with execution accuracy scoring broken down by query complexity.

---

## Architecture

```
User question
     │
     ▼
[RAG Retriever]
  Embed question → similarity search → retrieve top-4 relevant table schemas
     │
     ▼
[Prompt Builder]
  Inject retrieved schema + rules into structured prompt
     │
     ▼
[LLM — Groq Llama 3.1]
  Generate SQL
     │
     ▼
[Validator]
  Safety check (forbidden keywords) + syntax check (EXPLAIN)
  If invalid → self-correction loop → retry
     │
     ▼
[PostgreSQL]
  Execute query → return results
     │
     ▼
[React Frontend]
  Display SQL + retrieved tables + results table
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Database | PostgreSQL 16 |
| Vector store | ChromaDB (persistent, local) |
| Embeddings | fastembed (`BAAI/bge-small-en-v1.5`) |
| LLM | Groq API — Llama 3.1 8B Instant |
| Backend | FastAPI + Pydantic |
| Frontend | React + Vite |
| Backend deployment | Railway |
| Frontend deployment | Vercel |

---

## Database Schema

A SaaS metrics domain with 7 tables and ~17,000 rows of realistic seed data.

```
companies ──< subscriptions >── plans
     │              │
     └──< users     └──< invoices
          │         └──< subscription_events
          └──< feature_usage
```

Tables: `companies`, `users`, `plans`, `subscriptions`, `invoices`, `subscription_events`, `feature_usage`

---

## RAG Pipeline

The core differentiator of this project. Schema retrieval works in two phases:

**Offline (indexing):** Each table is converted into a rich text chunk containing column names, types, foreign key relationships, sample rows, and a plain-English description of what business questions it answers. These chunks are embedded and stored in ChromaDB.

**Online (per query):** The user's question is embedded using the same model. ChromaDB performs cosine similarity search and returns the top-4 most relevant table schemas. Only those schemas are injected into the LLM prompt.

This means a question like *"which companies cancelled recently?"* retrieves `companies` + `subscriptions` — not `feature_usage` or `invoices` — keeping the prompt focused and accurate.

---

## Evaluation Results

Tested against a 17-question golden set with execution accuracy scoring (result set comparison, order-independent):

| Complexity | Score |
|---|---|
| Simple (single table) | 5/5 — 100% |
| Medium (2-table joins) | 2/5 — 40% |
| Hard (3+ tables, aggregations) | 0/7 — 0% |
| **Overall** | **7/17 — 41%** |

**Key finding:** Simple queries are fully reliable. Complex multi-table aggregations exceed the reliable capability of a 3B local model without fine-tuning. The primary failure modes are:
1. Retrieval misses — a critical table scores below the top-k cutoff due to vocabulary mismatch
2. Aggregate misuse — LLM places aggregate functions in `WHERE` instead of `HAVING`
3. Non-determinism — same question retrieves slightly different tables on different runs

---

## Project Structure

```
TexttoSQL/
├── app/
│   ├── api/
│   │   ├── main.py          # FastAPI app, lifespan, CORS
│   │   └── models.py        # Pydantic request/response models
│   ├── db/
│   │   └── connection.py    # PostgreSQL connection
│   ├── llm/
│   │   ├── prompt_builder.py  # Prompt template with schema injection
│   │   ├── sql_generator.py   # Groq API + self-correction loop
│   │   └── validator.py       # Safety checks + EXPLAIN validation
│   └── rag/
│       ├── extractor.py     # Live schema introspection
│       ├── embedder.py      # ChromaDB indexing
│       └── retriever.py     # Similarity search
├── evaluation/
│   ├── golden_set.py        # 17 question/SQL pairs
│   └── evaluator.py         # Execution accuracy scoring
├── frontend/                # React + Vite
├── seed.py                  # Faker-based data generation
├── schema.sql               # Database schema
├── Dockerfile
└── railway.toml
```

---

## Running Locally

**Prerequisites:** Python 3.10+, Node.js 18+, PostgreSQL 16, Docker (optional)

**1. Start the database**
```bash
docker run --name saas-db \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=saas_metrics \
  -p 5432:5432 -d postgres:16
```

**2. Set up the backend**
```bash
python -m venv env && source env/bin/activate
pip install -r requirements.txt

# Create .env
cp .env.example .env
# Add GROQ_API_KEY, DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT

# Create tables and seed data
psql -h localhost -U postgres -d saas_metrics -f schema.sql
python seed.py

# Index schema into ChromaDB
python -m app.rag.embedder

# Start the API
uvicorn app.api.main:app --reload
```

**3. Start the frontend**
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`

---

## Example Queries

```
how many active subscriptions are there?
which companies have cancelled their subscriptions?
what is the total revenue collected per plan?
which users have never logged in?
which features are used most by enterprise customers?
```

---

## Deployment

- **Backend:** Dockerized FastAPI on Railway. Schema is auto-indexed on startup via a background thread.
- **Frontend:** React/Vite on Vercel with `VITE_API_URL` environment variable pointing to the Railway backend.
- **Database:** Railway managed PostgreSQL, seeded with ~17,000 rows.