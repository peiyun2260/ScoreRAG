# 📰 ScoreRAG — A Retrieval-Augmented Generation Framework with Consistency-Relevance Scoring and Structured Summarization for News Generation

**ScoreRAG** is a pipeline that combines retrieval, semantic scoring, and LLM-based summarization to generate high-quality news reports. It retrieves relevant historical news articles, re-ranks them based on relevance to a user-defined query, and composes a coherent summary and full-length report.

---

## 🚀 Features

- 🔍 Semantic retrieval using ChromaDB + HuggingFace Embeddings
- 📊 Multi-round relevance scoring with OpenAI GPT models
- 📝 Length-controlled summaries based on relevance score
- 📰 Full article generation with citation-style reference linking
- 🧪 Sample query mode (no DB required) for demo and visualization

---

## 📁 Project Structure

```
ScoreRAG/
├── backend/                  # FastAPI backend
│   ├── app/                  # Main application
│   │   ├── api/              # API routes
│   │   ├── db/               # Chroma & Mongo connectors
│   │   ├── services/         # Business logic (ScoreRAG core)
│   │   ├── schemas/          # Pydantic models
│   │   └── main.py           # FastAPI app entry
│   ├── scripts/              # CLI scripts (indexing, pipeline test)
│   ├── tests/                # Unit tests
│   └── sample_output/        # Real example outputs (for frontend demo)
├── frontend/                 # React + Vite frontend
│   └── public/sample_output.json
├── .env.template             # Environment variable template
├── pyproject.toml            # Dependency management (uv-compatible)
├── Makefile                  # Unified dev commands
└── README.md
```

---

## 🧰 Requirements

- Python 3.9+
- Node.js 18+
- `uv` for Python dependency management (or `pip`, optional)
- MongoDB (local, if full pipeline)
- ChromaDB (`chromadb` package)

---

## ⚙️ Setup Instructions

### 🐍 Backend (FastAPI)

```bash
make dev-env       # Create .env from .env.template
uv venv && source .venv/bin/activate
uv pip install -r pyproject.toml

make ingest        # Optional: build Chroma index
make run           # Start FastAPI at http://localhost:8000
```

### ⚛️ Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev        # Starts on http://localhost:5173
```

---

## 🧪 Sample Mode (No DB Required)

To demo without MongoDB or Chroma:

- Visit frontend
- Click **"Use Sample Query"**
- The app will load a pre-generated output (`public/sample_output.json`)

---

## 🧪 Test Commands

```bash
make test
# or individual test files:
PYTHONPATH=. pytest backend/tests/test_news_router.py
```

---

## 📦 Environment Variables

See `.env.template` for required variables:

```env
openai_api_key=sk-...
CHROMA_DIR=backend/storage/chromadb
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=news_db
```

---

## 📄 API Summary

### `POST /api/query`

```json
Request:
{
  "query": "Topic of interest",
  "top_k": 5
}

Response:
{
  "query": "...",
  "generated_article": "...",
  "references": [
    { "title": "...", "score": 88.5, "generated_summary": "..." }
  ]
}
```

---

## 📌 Development Notes

- LLM: Compatible with OpenAI (GPT-4o, GPT-3.5), Groq, etc.
- Embedding: Uses HuggingFace `intfloat/multilingual-e5-large`
- ChromaDB: Persisted locally, dynamic top-K retrieval

---

## ✨ Credits

Created by [Peiyun Lin](https://github.com/peiyun2260)  
Developed with ❤️ using FastAPI, React, LangChain, and OpenAI

---

## 📜 License

This project is for research and educational use. Contact the author for commercial licensing.
