import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def call_groq(prompt: str, model_name: str = "llama-3.3-70b-versatile") -> str:
    """
    Call Groq API to generate a response based on the given prompt.
    
    Args:
        prompt (str): The input prompt to send to the model
        model_name (str, optional): The name of the Groq model to use. 
                                  Defaults to 'llama-3.3-70b-versatile'.
    
    Returns:
        str: The generated response from the model
    
    Raises:
        Exception: If the API call fails, if API key is not set, or if the response is not successful
    """
    if not GROQ_API_KEY:
        raise Exception("GROQ_API_KEY environment variable is not set")
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }
    data = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}]
    }
    res = requests.post(url, headers=headers, json=data)
    if res.status_code == 200:
        return res.json()["choices"][0]["message"]["content"]
    raise Exception(f"Groq API Error {res.status_code}: {res.text}")
