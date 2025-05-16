.PHONY: test run ingest pipeline reset-chroma dev-env

# Run backend tests
test:
	PYTHONPATH=. pytest backend/tests/

# Start FastAPI backend (for local dev)
run:
	uvicorn backend.app.main:app --reload

# Ingest sample news data into ChromaDB
ingest:
	python backend/scripts/ingest_sample.py

# Run the full news scoring pipeline
pipeline:
	python backend/scripts/test_score_pipeline.py

# Remove all ChromaDB vector storage (reset DB)
reset-chroma:
	rm -rf backend/storage/chromadb

# Copy .env.example to .env if not exists
dev-env:
	cp -n .env.example .env || echo ".env already exists"

# ===== Frontend =====

# Install frontend dependencies
frontend:
	cd frontend && npm install

# Start frontend dev server
frontend-dev:
	cd frontend && npm run dev

# Build frontend for production
build-frontend:
	cd frontend && npm run build

# Preview production build locally
preview-frontend:
	cd frontend && npm run preview