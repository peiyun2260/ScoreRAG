from pymongo import MongoClient
import os
import urllib.parse
from typing import List, Dict, Any
from langchain.schema import Document
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

MONGO_USER = urllib.parse.quote_plus(os.getenv("MONGO_USER", ""))
MONGO_PASSWORD = urllib.parse.quote_plus(os.getenv("MONGO_PASSWORD", ""))

def connect_db() -> Any:
    """
    Establish a connection to the MongoDB database.
    
    Returns:
        Any: MongoDB database instance for 'news_db'
        
    Raises:
        Exception: If connection to MongoDB fails
    """
    client = MongoClient(f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@localhost:27017/")
    return client["news_db"]

def get_full_article(news_ids: List[str], dates: List[str]) -> Dict[int, Dict[str, Any]]:
    """
    Retrieve full article details from MongoDB based on news IDs and dates.
    
    Args:
        news_ids (List[str]): List of news IDs to retrieve
        dates (List[str]): List of dates corresponding to the news IDs
        
    Returns:
        Dict[int, Dict[str, Any]]: Dictionary mapping news IDs to their full article details
    """
    db = connect_db()
    full_articles = {}
    for news_id, date in zip(news_ids, dates):
        year = date.split("-")[0]
        result = db[year].find_one({"news_id": int(news_id)}, {
            "news_id": 1, "date": 1, "news_title": 1, "news_summary": 1, "news_content": 1})
        if result:
            result.pop("_id", None)
            full_articles[result["news_id"]] = result
    return full_articles

def fetch_full_articles(retrieved_docs: List[Document]) -> Dict[int, Dict[str, Any]]:
    """
    Fetch full articles for a list of retrieved documents.
    
    Args:
        retrieved_docs (List[Document]): List of Document objects containing news metadata
        
    Returns:
        Dict[int, Dict[str, Any]]: Dictionary mapping news IDs to their full article details
    """
    ids = [doc.metadata['news_id'] for doc in retrieved_docs]
    dates = [doc.metadata["date"] for doc in retrieved_docs]
    return get_full_article(ids, dates)
