from collections import defaultdict
from typing import Dict, List, Any
from backend.app.llm_clients.groq_client import call_groq
from backend.app.services.summary_service import generate_graded_summary, extract_number
from concurrent.futures import ThreadPoolExecutor, as_completed

def score_articles_sync(articles: Dict[str, Dict[str, Any]], 
                       query: str, 
                       n: int = 3, 
                       threshold: int = 20) -> List[Dict[str, Any]]:
    """
    Synchronously score articles for relevance to a query and generate summaries.

    This function evaluates each article's relevance to the given query by:
    1. Scoring each article n times using an LLM
    2. Calculating the average score for each article
    3. Filtering out articles with an average score below the threshold
    4. Generating a summary for each article that passes the threshold

    Args:
        articles (Dict[str, Dict[str, Any]]): Dictionary of articles, where each value contains:
            - news_title: Title of the article
            - news_summary: Summary of the article
            - news_content: Full content of the article
            - date: Publication date
        query (str): The search query to evaluate relevance against
        n (int, optional): Number of times to score each article. Defaults to 3.
        threshold (int, optional): Minimum average score to include an article. Defaults to 20.

    Returns:
        List[Dict[str, Any]]: List of scored articles sorted by average score, each containing:
            - id: Article ID
            - title: Article title
            - date: Publication date
            - score: Average relevance score
            - content: Full article content
            - generated_summary: Generated summary based on the score

    Note:
        Scoring criteria:
        - 90-100: Completely relevant, directly addresses the query
        - 70-89: Highly relevant, closely related but slightly off-core
        - 50-69: Partially relevant, some content related to query
        - 0-49: Not relevant, minimal or no relation to query
    """
    scored_articles = defaultdict(lambda: {"scores": [],})

    for news_id, article in articles.items(): 
        news_title = article["news_title"]
        news_summary = article["news_summary"]
        news_date = article["date"]

        print(f"\n📰 評分新聞：{news_title}（日期：{news_date}）")

        for i in range(n):
            prompt = f"""
            你是一位專業的新聞分析助手，請評估以下新聞對查詢主題的相關性：
            
            查詢：{query}
            日期：{news_date}
            標題：{news_title}
            摘要：{news_summary}...
            
            依據新聞與查詢的相關性，給出一個分數（0-100）。
            - 90-100 分：完全相關，直接探討查詢主題。
            - 70-89 分：高度相關，與查詢主題密切相關，但可能稍微偏離核心。
            - 50-69 分：部分相關，新聞內容有部分涉及查詢主題，但並非核心內容。
            - 0-49 分：不相關，新聞內容與查詢主題無關或關聯性極低。
            
            只輸出一個數字（0 到 100 之間）不要額外解釋
            """

            response = call_groq(prompt)
            score = extract_number(response)
            scored_articles[news_id]["scores"].append(score)

        avg_score = sum(scored_articles[news_id]["scores"]) / len(scored_articles[news_id]["scores"])
        print(f"✅ 平均分數：{avg_score:.2f}")

    final_scores = [
        {
            "id": news_id, 
            "title": article["news_title"], 
            "date": article["date"],
            "score": sum(data["scores"]) / len(data["scores"]),
            "content": article["news_content"],
            "generated_summary": generate_graded_summary(article, sum(data["scores"]) / len(data["scores"]))
        }
        for news_id, data in scored_articles.items()
        if sum(data["scores"]) / len(data["scores"]) >= threshold
    ]

    return sorted(final_scores, key=lambda x: x["score"], reverse=True)


def score_articles_with_thread_pool(articles, query, n=3, threshold=20, max_workers=5):
    """
    Score articles for relevance to a query and generate summaries using multithreading.

    This function evaluates each article's relevance to the given query by:
    1. Using a thread pool to concurrently score each article n times with an LLM
    2. Calculating the average score for each article
    3. Filtering out articles with an average score below the threshold
    4. Generating a summary for each article that passes the threshold

    Args:
        articles (Dict[str, Dict[str, Any]]): Dictionary of articles, where each value contains:
            - news_title: Title of the article
            - news_summary: Summary of the article
            - news_content: Full content of the article
            - date: Publication date
        query (str): The search query to evaluate relevance against
        n (int, optional): Number of times to score each article. Defaults to 3.
        threshold (int, optional): Minimum average score to include an article. Defaults to 20.
        max_workers (int, optional): Maximum number of threads to use. Defaults to 5.

    Returns:
        List[Dict[str, Any]]: List of scored articles sorted by average score, each containing:
            - id: Article ID
            - title: Article title
            - date: Publication date
            - score: Average relevance score (rounded)
            - content: Full article content
            - generated_summary: Generated summary based on the score

    Note:
        Scoring criteria:
        - 90-100: Completely relevant, directly addresses the query
        - 70-89: Highly relevant, closely related but slightly off-core
        - 50-69: Partially relevant, some content related to query
        - 0-49: Not relevant, minimal or no relation to query
    """

    def score_one_article(news_id, article):
        scores = []
        for _ in range(n):
            prompt = f"""
            你是一位專業的新聞分析助手，請評估以下新聞對查詢主題的相關性：

            查詢：{query}
            日期：{article['date']}
            標題：{article['news_title']}
            摘要：{article['news_summary']}...

            依據新聞與查詢的相關性，給出一個分數（0-100）：
            - 90-100 分：完全相關
            - 70-89 分：高度相關
            - 50-69 分：部分相關
            - 0-49 分：不相關

            只輸出一個數字（0 到 100 之間）不要額外解釋。
            """
            response = call_groq(prompt)
            scores.append(extract_number(response))
        
        avg_score = sum(scores) / len(scores)
        if avg_score >= threshold:
            summary = generate_graded_summary(article, avg_score)
            return {
                "id": news_id,
                "title": article["news_title"],
                "date": article["date"],
                "score": round(avg_score, 0),
                "content": article["news_content"],
                "generated_summary": summary
            }
        return None

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(score_one_article, news_id, article) for news_id, article in articles.items()]
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)

    return sorted(results, key=lambda x: x["score"], reverse=True)
