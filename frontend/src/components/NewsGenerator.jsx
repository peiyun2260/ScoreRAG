import React, { useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import "../App.css";

const API_BASE = "http://localhost:8000/api";

function NewsGenerator() {
  // State variables for user input, generated news, references, loading, and error message
  const [input, setInput] = useState("");
  const [generatedNews, setGeneratedNews] = useState("");
  const [references, setReferences] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  // Function to call backend API and generate news
  const generateNews = async () => {
    setLoading(true);
    setGeneratedNews("");
    setReferences([]);
    setErrorMessage("");

    try {
      const response = await axios.post(`${API_BASE}/query?mode=thread`, {
        query: input,
        top_k: 5,
      });
      setGeneratedNews(response.data.generated_article);
      setReferences(response.data.references);
    } catch (error) {
      console.error("Error generating news:", error);
      setErrorMessage(
        "❌ Generation failed. Please try again later or check the server status."
      );
    } finally {
      setLoading(false);
    }
  };

  // Function to load a sample result from a local JSON file
  const loadSampleResult = async () => {
    try {
      const response = await fetch("/sample_output.json");
      const data = await response.json();

      setInput(data.query);
      setGeneratedNews(data.generated_article);
      setReferences(data.references);
      setErrorMessage("");
    } catch (error) {
      console.error("Failed to load sample:", error);
      setErrorMessage(
        "❌ Unable to load sample result. Please make sure sample_output.json exists in the public folder."
      );
    }
  };

  return (
    <div className="news-generator">
      <h1 className="title">ScoreRAG 新聞生成AI</h1>
      <p className="description">
        ScoreRAG －
        請給我想要報導的新聞主題，我將為你參考過去的新聞資料，生成一篇完整的新聞文章，並提供我所參考的新聞內容
      </p>
      <p className="data-info">目前新聞資料有2018～2024的新聞資料</p>

      {/* User input section */}
      <div className="input-section">
        <textarea
          className="news-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="輸入新聞主題內容，如「俄烏戰爭自2022年2月24日開打已滿3年，雖然3年來美、歐各國持續給予烏克蘭經濟與軍事上的援助，烏克蘭也靠著無人機造成俄國大量損失，但俄羅斯仍控制著烏克蘭18%的領土，雙方死傷人數亦不明。據聯合國估計，這場戰爭造成近700萬人逃離家園，是全球僅次於敘利亞的難民危機，也將持續衝擊全球經貿。」"
          rows="5"
        />
      </div>

      {/* Action buttons */}
      <div className="button-section">
        <button
          className="generate-button"
          onClick={generateNews}
          disabled={loading}
        >
          生成新聞
        </button>
        <button className="sample-button" onClick={loadSampleResult}>
          範例新聞專題
        </button>
      </div>

      {/* Loading indicator */}
      {loading && (
        <div className="loading">
          <p>Loading...</p>
        </div>
      )}

      {/* Display generated news */}
      {generatedNews && (
        <div className="generated-news">
          <h2 className="generated-news-title">生成的新聞</h2>
          <ReactMarkdown>{generatedNews}</ReactMarkdown>
        </div>
      )}

      {/* Display error message */}
      {errorMessage && (
        <div className="error-message">
          <p>{errorMessage}</p>
        </div>
      )}

      {/* Display reference articles */}
      {references.length > 0 && (
        <div className="references">
          <h2>參考文章</h2>
          {references.map((article, index) => (
            <div key={index} className="reference-article">
              <p>
                {index + 1}. <strong>{article.date}</strong> {article.title}
              </p>
              <p>摘要: {article.generated_summary}</p>
              <p>相關性分數: {article.score}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default NewsGenerator;
