from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_query_news_thread_mode():
    response = client.post("/api/query?mode=thread", json={"query": "馬斯克訪華", "top_k": 3})
    assert response.status_code == 200
    data = response.json()

    assert "query" in data
    assert "generated_article" in data
    assert "references" in data
    assert isinstance(data["references"], list)

    if data["references"]:
        ref = data["references"][0]
        assert "id" in ref
        assert "title" in ref
        assert "score" in ref
        assert "generated_summary" in ref

def test_query_news_sync_mode():
    response = client.post("/api/query?mode=sync", json={"query": "馬斯克訪華", "top_k": 3})
    assert response.status_code == 200
    data = response.json()

    assert "query" in data
    assert "generated_article" in data
    assert "references" in data
    assert isinstance(data["references"], list)
