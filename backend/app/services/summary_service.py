import re
from typing import Dict, Any
from backend.app.llm_clients.groq_client import call_groq

def extract_number(text: str) -> int:
    """
    Extract a number from text and ensure it's within the range of 0-100.
    
    Args:
        text (str): Text containing a number to extract
        
    Returns:
        int: Extracted number between 0 and 100, or 0 if no valid number found
    """
    match = re.search(r'\b(\d{1,3})\b', text) 
    if match:
        return max(0, min(100, int(match.group(1))))
    return 0


def generate_graded_summary(article: Dict[str, Any], score: float) -> str:
    """
    Generate a summary of varying length based on the article's score.
    
    Summary length guidelines:
    - Score > 70: 300-500 characters
    - Score 50-70: 150-300 characters
    - Score 30-50: 50-150 characters
    - Score 20-30: 30-50 characters
    
    Args:
        article (Dict[str, Any]): Dictionary containing article information with keys:
            - news_title: Title of the article
            - news_content: Full content of the article
        score (int): Score of the article (0-100) determining summary length
        
    Returns:
        str: Generated summary following the specified length and content guidelines
        
    Note:
        The summary generation follows these content rules based on score:
        - Score > 70: Includes core facts, key data, main quotes, background info, and impact assessment
        - Score 50-70: Includes core facts, key data, main quotes, and brief background
        - Score 30-50: Includes only core facts and most important data
        - Score 20-30: Includes only the most essential facts
    """
    summary_length = {
        (70, 101): (300, 500),
        (50, 70): (150, 300),
        (30, 50): (50, 150),
        (20, 30): (30, 50),
    }

    min_length, max_length = next(v for k, v in summary_length.items() if k[0] <= score < k[1])

    prompt = f"""
    你是一位專業的新聞摘要助手，請根據以下新聞內容生成 {min_length} 到 {max_length} 字的摘要：
    
    標題：{article["news_title"]}
    內容：{article["news_content"]}

    請遵守以下規則：
    - 長度應在 {min_length}-{max_length} 字內。
    - 保持新聞的關鍵事實、數據和重要引述（如果適用）。
    - 若分數高於 70，需要包含：核心事實、關鍵數據、主要引述、背景資訊和影響評估。
    - 若分數在 50-70，需要包含：核心事實、關鍵數據、主要引述和簡要背景。
    - 若分數在 30-50，只需包含：核心事實和最重要的數據。
    - 若分數在 20-30，只需包含：最核心的事實摘要。
    - 摘要需保持客觀，避免加入個人評價。
    - 保留原文的時間和地點資訊。
    - 如果原文有多個觀點，請確保摘要平衡呈現。

    直接輸出摘要內容，不要加上多餘的說明。
    """

    response = call_groq(prompt)
    return response