import os
import chromadb
from langchain_chroma import Chroma
from backend.app.services.embedding_service import initialize_embedding


def get_chroma_db(persist_directory: str = "./backend/storage/chromadb"):
    """
    Initialize and return a ChromaDB instance.
    
    Args:
        persist_directory (str): Directory to persist the database.
                               Defaults to "./backend/storage/chromadb".
    
    Returns:
        Chroma: Initialized ChromaDB instance
    """
    # Create directory if it doesn't exist
    os.makedirs(persist_directory, exist_ok=True)
    
    try:
        embedding = initialize_embedding()
        client = chromadb.PersistentClient(path=persist_directory)
        return Chroma(
            client=client,
            embedding_function=embedding,
            collection_name="news_collection"
        )
    except Exception as e:
        raise ConnectionError(f"無法連接到 ChromaDB: {str(e)}")

def query_chroma(query: str, k: int = 5, persist_directory: str = "./backend/storage/chromadb"):
    """
    Query the ChromaDB for similar documents.
    
    Args:
        query (str): The search query
        k (int, optional): Number of results to return. Defaults to 5.
        persist_directory (str, optional): Directory where the database is persisted.
                                         Defaults to "./backend/storage/chromadb".
    
    Returns:
        list: List of similar documents
    """
    db = get_chroma_db(persist_directory)
    return db.similarity_search(query, k=k)
