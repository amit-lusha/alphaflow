import os
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from alphaflow.core.config import settings

RAW_DB_URI = os.getenv("POSTGRES_URI", "postgresql://alpha_user:alpha_pass@localhost:5432/alphaflow_db")

# Driver for SQLAlchemy
# SQLAlchemy needs "postgresql+psycopg://" to know we are using the new v3 driver.
DB_CONNECTION = RAW_DB_URI.replace("postgresql://", "postgresql+psycopg://")
COLLECTION_NAME = "financial_news"

def get_embedding_function():
    return GoogleGenerativeAIEmbeddings(
        model=settings.embedding_model,
        google_api_key=settings.google_api_key
    )

def get_vector_store():
    return PGVector(
        embeddings=get_embedding_function(),
        collection_name=COLLECTION_NAME,
        connection=DB_CONNECTION,
        use_jsonb=True,
    )