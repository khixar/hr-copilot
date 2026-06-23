# HR Copilot

A multi-tenant RAG (Retrieval-Augmented Generation) system for HR document Q&A. Upload PDFs per tenant, ask questions in natural language, get accurate answers with source citations.

## Architecture

```
PDF Upload → Parse → Chunk → Embed (OpenAI) → Store (pgvector)
                                                       │
Query → Embed query ──────────────────────────────────┤
      → BM25 search ──────────────────────────────────┤
                                                       ↓
                                          RRF merge → Cohere rerank → GPT-4o-mini → Answer
```

**Retrieval pipeline:**
- **Vector search** — cosine similarity via pgvector HNSW index (`text-embedding-3-small`, 1536 dims)
- **BM25** — keyword search with `rank-bm25` loaded in-memory per query
- **RRF** — Reciprocal Rank Fusion (k=60) merges both ranked lists
- **Cohere reranker** — `rerank-english-v3.0` cross-encoder as final pass

**Stack:** FastAPI · PostgreSQL 16 + pgvector · SQLAlchemy (async) · Alembic · Docker Compose

---

## Eval Results

Baseline evaluation — hybrid retrieval + Cohere reranker, 10 questions across 2 documents:

| Metric | Score |
|---|---|
| Retrieval accuracy | 100% (8/8) |
| Answer accuracy | 90% (9/10) |
| Test dataset | 10 questions, 2 documents |

Run the eval suite yourself: `python eval_runner.py --tenant-id <uuid>`

---

## Setup

### Prerequisites

- Docker + Docker Compose
- OpenAI API key
- Cohere API key

### 1. Configure environment

Create a `.env` file in the project root:

```env
POSTGRES_USER=hrcopilot
POSTGRES_PASSWORD=...
POSTGRES_DB=hrcopilot
DATABASE_URL=postgresql+asyncpg://{user}:{password}@db:5432/{db}
OPENAI_API_KEY=sk-...
COHERE_API_KEY=...
```

> `.env` is gitignored — never commit it.

### 2. Start services

```bash
docker compose up --build
```

This starts:
- `db` — PostgreSQL 16 with pgvector on port `5432`
- `api` — FastAPI on port `8000` with hot reload
- `pgadmin` — pgAdmin 4 on port `5050`

### 3. Run migrations

```bash
docker compose exec api alembic upgrade head
```

### 4. Verify

```
http://localhost:8000/docs
```

---

## API

### Create a tenant

```bash
curl -X POST http://localhost:8000/api/v1/tenants/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Acme Corp"}'
```

### Upload a document

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "tenant_id=<uuid>" \
  -F "file=@/path/to/document.pdf"
```

### Query

```bash
curl -X POST http://localhost:8000/api/v1/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "<uuid>",
    "question": "What is the notice period for termination?",
    "top_k": 5
  }'
```

**Response:**
```json
{
  "answer": "The agreement requires 14 days notice for termination.",
  "sources": [
    {
      "document_title": "Contract.pdf",
      "page_number": 3,
      "content": "...",
      "rrf_score": 0.032787,
      "relevance_score": 0.891234
    }
  ]
}
```

`rrf_score` — combined rank from vector + BM25 fusion (higher = retrieved by more signals).  
`relevance_score` — Cohere cross-encoder score (semantic relevance to the question).

---

## Database

pgAdmin is available at `http://localhost:5050`:

| Field | Value |
|---|---|
| Login email | `admin@admin.com` |
| Login password | set in `docker-compose.yml` |
| Host | `db` |
| Port | `5432` |
| Database | set in `.env` (`POSTGRES_DB`) |
| Username | set in `.env` (`POSTGRES_USER`) |
| Password | set in `.env` (`POSTGRES_PASSWORD`) |

---

## Eval

The eval suite runs all questions in `eval.json` against a live tenant, scores retrieval and answer quality, and prints a report.

```bash
# Run from inside the container
docker compose exec api python eval_runner.py --tenant-id <uuid>

# Or locally with a running DB
python eval_runner.py --tenant-id <uuid>
python eval_runner.py --tenant-id <uuid> --eval-file path/to/custom_eval.json
```

**Retrieval scoring** — checks whether the expected source document and page appear in the returned sources.

**Answer scoring** — LLM-as-judge (GPT-4o-mini) gives `PASS`/`FAIL` with a one-sentence reason, judging semantic correctness rather than exact match.

**Negative cases** (`should_retrieve: false`) — verifies the pipeline correctly returns no relevant results and the answer acknowledges the gap rather than hallucinating.

---

## Project Structure

```
hr-copilot/
├── app/
│   ├── api/v1/endpoints/   # tenants, documents, query
│   ├── core/config.py      # Pydantic settings
│   ├── db/session.py       # async SQLAlchemy engine
│   ├── models/             # Tenant, Document, Chunk (pgvector)
│   ├── schemas/            # Pydantic request/response models
│   └── services/
│       ├── parsing.py          # PDF → pages → chunks
│       ├── embedding_service.py # OpenAI embeddings
│       ├── bm25_service.py     # BM25 in-memory search
│       ├── rrf.py              # Reciprocal Rank Fusion
│       ├── reranker_service.py # Cohere reranker
│       └── query_service.py    # full pipeline orchestration
├── alembic/                # DB migrations
├── eval.json               # eval dataset (10 questions)
├── eval_runner.py          # eval runner with LLM-as-judge
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```
