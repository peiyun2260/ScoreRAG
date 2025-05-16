from pydantic import BaseModel
from typing import List

class NewsQuery(BaseModel):
    query: str
    top_k: int = 5

class ScoredNews(BaseModel):
    id: str
    title: str
    date: str
    score: float
    generated_summary: str

class NewsQueryResponse(BaseModel):
    query: str
    generated_article: str
    references: List[ScoredNews]