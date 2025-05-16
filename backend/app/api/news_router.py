from fastapi import APIRouter
from backend.app.schemas.news import NewsQuery
from backend.app.db.chroma_connector import get_chroma_db, query_chroma
from backend.app.db.mongo_connector import get_full_article
from backend.app.services.embedding_service import initialize_embedding
from backend.app.services.CoT_service import score_articles_with_thread_pool, score_articles_sync
from backend.app.services.generation_service import generated_news_with_CoT
import logging

router = APIRouter()

# Initialize embedding model and vector database
embedding = initialize_embedding()
db = get_chroma_db()

@router.post("/query")
def query_news(request: NewsQuery, mode: str = "thread"):
    """
    Endpoint for querying news articles, scoring their relevance, and generating a summary article.

    This endpoint receives a query and returns:
    - A generated news article based on the query and reference articles
    - A list of reference articles with their scores and summaries

    Args:
        request (NewsQuery): The request body containing the query and top_k
        mode (str, optional): Scoring mode, either 'thread' (default) or 'sync'

    Returns:
        dict: Contains the query, generated article, and a list of reference articles
    """
    try:
        query = request.query
        top_k = request.top_k
        logging.info(f"🔍 Received query request: {query} (top_k={top_k}, mode={mode})")

        # Retrieve similar documents from the vector database
        docs = query_chroma(db, query=query, k=top_k)
        ids = [doc.metadata["news_id"] for doc in docs]
        dates = [doc.metadata["date"] for doc in docs]
        articles = get_full_article(ids, dates)

        # Score articles and generate summaries
        if mode == "sync":
            results = score_articles_sync(articles, query=query, n=1, threshold=20)
        else:
            results = score_articles_with_thread_pool(
                articles, query=query, n=1, threshold=20, max_workers=5
            )

        # Generate a comprehensive news article and format references
        generated_article, reference_articles = generated_news_with_CoT(query, results)
        logging.info(f"🔎 Number of full articles extracted: {len(articles)}")
        logging.info(f"✅ Number of reference articles passing the threshold: {len(results)}")

        formatted_references = [
            {
                "id": article["id"],
                "title": article["title"],
                "date": article["date"],
                "score": article["score"],
                "generated_summary": article["generated_summary"]
            }
            for article in reference_articles
        ]

        return {
            "query": query,
            "generated_article": generated_article,
            "references": formatted_references
        }

    except Exception as e:
        logging.error(f"❌ Query error: {str(e)}")
        return {
            "query": request.query,
            "generated_article": "❌ Generation failed",
            "references": []
        }