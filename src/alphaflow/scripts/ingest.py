import asyncio
import httpx
import feedparser
from datetime import datetime
from langchain_core.documents import Document
from alphaflow.services.rag import get_vector_store

# Yahoo Finance RSS Feeds
URLS = {
    "General": "https://finance.yahoo.com/news/rssindex",
    "TSLA": "https://finance.yahoo.com/rss/headline?s=TSLA",
    "NVDA": "https://finance.yahoo.com/rss/headline?s=NVDA",
    "AAPL": "https://finance.yahoo.com/rss/headline?s=AAPL",
    "GOOGL": "https://finance.yahoo.com/rss/headline?s=GOOGL",
    "MSFT": "https://finance.yahoo.com/rss/headline?s=MSFT"
}

# Yahoo usually blocks bots, so we look like a browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

async def fetch_feed_async(client: httpx.AsyncClient, category: str, url: str):
    """Fetches a single feed asynchronously."""
    print(f"📡 Requesting {category}...")
    try:
        # Await the network call
        response = await client.get(url, headers=HEADERS, timeout=10.0, follow_redirects=True)
        response.raise_for_status()
        
        # Parse content (feedparser is sync, but fast enough for text)
        feed = feedparser.parse(response.content)
        
        documents = []
        for entry in feed.entries:
            title = entry.get("title", "No Title")
            link = entry.get("link", "")
            summary = entry.get("summary", "")
            published = entry.get("published", str(datetime.now()))
            
            page_content = f"Title: {title}\nSummary: {summary}\nPublished: {published}"
            
            doc = Document(
                page_content=page_content,
                metadata={
                    "source": "Yahoo Finance",
                    "category": category,
                    "url": link,
                    "date": published
                }
            )
            documents.append(doc)
        
        print(f"✅ {category}: Found {len(documents)} articles.")
        return documents

    except Exception as e:
        print(f"⚠️ Failed to fetch {category}: {e}")
        return []

async def main():
    print("🚀 Starting Async Ingestion...")
    
    # 1. Create a single Async Client for all requests
    async with httpx.AsyncClient() as client:
        # 2. Create a list of tasks (one per URL)
        tasks = [fetch_feed_async(client, cat, url) for cat, url in URLS.items()]
        
        # 3. Fire them all at once and wait for results
        results = await asyncio.gather(*tasks)
    
    # Flatten the list of lists [[docs], [docs]] -> [docs]
    total_docs = [doc for batch in results for doc in batch]
    
    if not total_docs:
        print("❌ No news found.")
        return

    # 4. Save to DB (ChromaDB operations are usually sync/fast enough locally)
    # Deduplicate by URL
    ids = [doc.metadata["url"] for doc in total_docs]
    
    vector_store = get_vector_store()
    print(f"💾 Saving {len(total_docs)} articles to ChromaDB...")
    vector_store.add_documents(total_docs, ids=ids)
    print("🎉 Ingestion Complete!")

if __name__ == "__main__":
    asyncio.run(main())