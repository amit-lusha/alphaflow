import os
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# 1. Configuration
# We will save the database in a folder named 'chroma_db' inside your project
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "financial_news"

from alphaflow.core.config import settings

def get_embedding_function():
    return GoogleGenerativeAIEmbeddings(
        model=settings.embedding_model,
        google_api_key=settings.google_api_key
    )

def get_vector_store():
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embedding_function(),
        persist_directory=CHROMA_PATH,
    )