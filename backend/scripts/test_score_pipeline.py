"""
Script to test the complete news processing pipeline.

This script demonstrates the complete workflow:
1. Initialize embedding model and vector database
2. Search for relevant news articles
3. Retrieve full article content
4. Score articles for relevance
5. Generate summaries based on scores
6. Create a comprehensive news report

Example:
    python test_score_pipeline.py
"""

from backend.app.db.chroma_connector import get_chroma_db, query_chroma
from backend.app.services.CoT_service import score_articles_with_consistency
from backend.app.services.generation_service import generated_news_with_CoT
from backend.app.db.mongo_connector import get_full_article

# Initialize the vector database
db = get_chroma_db()

# Define search query and retrieve similar documents
query = "馬斯克訪華"
docs = query_chroma(query, k=5)  # Get top 5 most similar articles
print(f"找到 {len(docs)} 篇相關文章")

# Retrieve full article content from MongoDB
ids = [doc.metadata['news_id'] for doc in docs]
dates = [doc.metadata['date'] for doc in docs]
full_articles = get_full_article(ids, dates)
print(f"成功獲取 {len(full_articles)} 篇完整文章")

# Score articles and generate summaries
# This will:
# 1. Evaluate relevance of each article
# 2. Generate summaries based on relevance scores
# 3. Sort articles by score
results = score_articles_with_consistency(full_articles, query)
print(f"完成評分，共有 {len(results)} 篇文章通過評分標準")

# Display individual article results with titles, scores, and generated summaries
print("\n文章評分結果：")
for r in results:
    print(f"\n📰 {r['title']} ({r['score']:.1f})\n摘要：{r['generated_summary']}")

# Generate and display a comprehensive news report
# This will:
# 1. Combine information from all relevant articles
# 2. Create a coherent narrative
# 3. Maintain proper citations and references
print("\n專題生成：")
report = generated_news_with_CoT(query, results)
print(report)
print("=" * 80)  # Separator line for better readability