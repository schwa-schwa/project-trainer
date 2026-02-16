import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from core.common.config import load_config

# Ensure config is loaded
load_config()

def get_llm(model: str = "gemini-3-flash-preview", temperature: float = 0.5) -> ChatGoogleGenerativeAI:
    """Factory function to get an LLM instance"""
    return ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
        api_key=os.getenv("GOOGLE_API_KEY")
    )

def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Factory function to get Embeddings instance"""
    return GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
