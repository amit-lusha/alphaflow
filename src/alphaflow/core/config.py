from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """
    Application configuration settings using Pydantic BaseSettings.
    Reads from environment variables or defaults.
    """
    # LLM Settings
    google_api_key: str = Field(..., description="Google API Key for Gemini")
    llm_model_name: str = Field(default="gemini-2.0-flash", description="The Gemini model to use")
    llm_temperature: float = Field(default=0.0, description="Temperature for LLM generation")

    # Search Settings
    search_k_results: int = Field(default=3, description="Number of results to retrieve from search/RAG")

    # Vector DB
    chroma_path: str = Field(default="chroma_db", description="Path to ChromaDB directory")
    collection_name: str = Field(default="financial_news", description="Name of the ChromaDB collection")
    embedding_model: str = Field(default="models/text-embedding-004", description="Google Embedding model name")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
