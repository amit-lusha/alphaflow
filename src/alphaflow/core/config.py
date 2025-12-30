from pydantic_settings import BaseSettings
from pydantic import Field
import os

class Settings(BaseSettings):
    """
    Application configuration settings using Pydantic BaseSettings.
    Reads from environment variables or defaults.
    """

    google_api_key: str = Field(..., description="Google API Key for Gemini")
    llm_model_name: str = Field(default="gemini-2.0-flash", description="The Gemini model to use")
    llm_temperature: float = Field(default=0.0, description="Temperature for LLM generation")

    search_k_results: int = Field(default=3, description="Number of results to retrieve from search/RAG")

    chroma_path: str = Field(default="chroma_db", description="Path to ChromaDB directory")
    collection_name: str = Field(default="financial_news", description="Name of the ChromaDB collection")
    embedding_model: str = Field(default="models/text-embedding-004", description="Google Embedding model name")

    langchain_tracing_v2: str = Field(default="true")
    langchain_endpoint: str = Field(default="https://api.smith.langchain.com")
    langchain_api_key: str = Field(..., description="LangSmith API Key")
    langchain_project: str = Field(default="AlphaFlow-Dev")
    langchain_endpoint: str = Field(default="https://api.smith.langchain.com")

    user_agent: str = Field(default="AlphaFlow-Agent/1.0")
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()


os.environ["GOOGLE_API_KEY"] = settings.google_api_key
os.environ["LANGCHAIN_TRACING_V2"] = settings.langchain_tracing_v2
os.environ["LANGCHAIN_ENDPOINT"] = settings.langchain_endpoint
os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
os.environ["USER_AGENT"] = settings.user_agent
os.environ["LANGCHAIN_ENDPOINT"] = settings.langchain_endpoint