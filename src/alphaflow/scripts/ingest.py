from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

from alphaflow.services.rag import get_vector_store

def ingest_mock_news():
    news_articles = [
        Document(
            page_content="Tesla (TSLA) shares jumped 5% today after Elon Musk announced a new 'Infinite Battery' technology that charges in 5 minutes.",
            metadata={"source": "TechCrunch", "ticker": "TSLA", "date": "2025-01-10"}
        ),
        Document(
            page_content="NVIDIA (NVDA) stock is down slightly as the EU announces an investigation into AI chip monopoly concerns.",
            metadata={"source": "Bloomberg", "ticker": "NVDA", "date": "2025-01-12"}
        ),
        Document(
            page_content="Apple (AAPL) is rumored to release a folding iPhone later this year, causing a rally in supplier stocks.",
            metadata={"source": "MacRumors", "ticker": "AAPL", "date": "2025-01-15"}
        ),
    ]
    
    vector_store = get_vector_store()
    
    print(f"📊 Adding {len(news_articles)} articles to ChromaDB...")
    vector_store.add_documents(news_articles)
    
    print("✅ Ingestion Complete. The Agent now 'knows' this news.")

if __name__ == "__main__":
    ingest_mock_news()