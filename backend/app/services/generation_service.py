from typing import List, Dict, Any
from backend.app.llm_clients.openai_client import call_openai

def generated_news_with_CoT(query: str, final_sorted_articles: List[Dict[str, Any]]) -> str:
    """
    Generate a comprehensive news article based on a query and reference articles.
    
    This function creates a news article by:
    1. Formatting reference articles with their titles, dates, and summaries
    2. Using an LLM to generate a coherent article that:
       - Follows the main query topic
       - Incorporates relevant reference materials
       - Maintains objective journalistic style
       - Properly cites sources
    
    Args:
        query (str): The main topic or theme for the news article
        final_sorted_articles (List[Dict[str, Any]]): List of reference articles, each containing:
            - title: Article title
            - date: Publication date
            - generated_summary: Summary of the article
            
    Returns:
        str: A complete news article that integrates information from reference materials
        
    Note:
        The generated article will:
        - Maintain objective journalistic tone
        - Follow standard news writing conventions
        - Cite references using the format: 'Reference X (Source: Title)'
        - Ensure consistency with reference materials
        - Consider the temporal context of references
    """
    references = []
    for idx, article in enumerate(final_sorted_articles, start=1):
        references.append(f"{idx}.（標題：{article['title']}），日期：{article['date']}）內容：{article['generated_summary']}")

    prompt = f"""
    你是一位專業的新聞專題生成助理，請跟據「報導主題」，以及過去的「參考資料」，為讀者生成一篇完整的專題報導。生成時請評估參考資料是否與報導主題相關，報導內容需貫徹「報導主題」，於必要時引入「參考資料」增強文章。當需要引用參考資料時，注意文章與提供的參考資料一致，並注意參考資料的時間，流暢統整文章，報導語氣客觀、符合新聞寫作標準，避免口語化或冗長表述。
    引用的方式請使用以下格式：'參考資料第X篇（來源：標題）'，其中X代表該新聞在參考資料中的編號，第一篇為1第二篇為2，以此類推。報導主題：{query}，參考資料{references}"
    """

    response = call_openai(prompt)
    return response