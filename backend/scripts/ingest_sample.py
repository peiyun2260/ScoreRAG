"""
Script to ingest sample news data into the vector database.

This script processes news articles from JSON files and stores them in ChromaDB
for vector search functionality. It uses the embedding service to convert text
into vector representations.

Example:
    python -m backend.scripts.ingest_sample
"""

from backend.app.services.embedding_service import process_news_files
import os

# Get the absolute path to the example_data directory
current_dir = os.path.dirname(os.path.abspath(__file__))
example_data_dir = os.path.join(os.path.dirname(current_dir), "example_data")

# Process news articles from the example data directory
# This will:
# 1. Load news data from JSON files
# 2. Split articles into chunks
# 3. Generate embeddings
# 4. Store in ChromaDB
process_news_files(
    directory=example_data_dir,  # Directory containing news JSON files
    file_list=["news_202405.json"]  # List of JSON files to process
)