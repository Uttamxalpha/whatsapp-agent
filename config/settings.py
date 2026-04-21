import os

from pydantic_settings import BaseSettings
from pydantic import Field

try:
    import streamlit as _st
    _secrets = dict(_st.secrets)
    for k, v in _secrets.items():
        if k not in os.environ:
            os.environ[k] = str(v)
except Exception:
    pass


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    GROQ_API_KEY: str = Field(..., description="API key for Groq LLM service")
    TAVILY_API_KEY: str = Field(..., description="API key for Tavily search")
    CHROMA_PERSIST_DIR: str = Field(default="./chroma_db", description="ChromaDB persistence directory")
    CHROMA_COLLECTION_NAME: str = Field(default="fact_checks", description="ChromaDB collection name")
    EMBEDDING_MODEL: str = Field(default="all-MiniLM-L6-v2", description="Sentence transformer model name")
    GROQ_MODEL: str = Field(default="llama-3.3-70b-versatile", description="Groq LLM model identifier")
    GROQ_TEMPERATURE: float = Field(default=0.1, description="LLM temperature setting")
    MAX_CLAIMS: int = Field(default=5, description="Maximum claims to extract per message")
    SEARCH_RESULTS_PER_CLAIM: int = Field(default=4, description="Web search results per claim")
    TOP_K_RAG: int = Field(default=3, description="Top-K results from RAG retriever")
    APP_HOST: str = Field(default="0.0.0.0", description="API server host")
    APP_PORT: int = Field(default=8000, description="API server port")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
