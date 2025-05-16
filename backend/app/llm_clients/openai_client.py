from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def call_openai(prompt: str) -> str:
    """
    Call OpenAI API to generate a response.
    
    Args:
        prompt (str): The prompt to send to OpenAI
        
    Returns:
        str: The generated response
        
    Raises:
        Exception: If OPENAI_API_KEY is not set or API call fails
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise Exception("OPENAI_API_KEY environment variable is not set")
    
    client = OpenAI(api_key=api_key)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"OpenAI API call failed: {str(e)}")
