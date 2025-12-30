import yfinance as yf
from langchain_core.tools import tool
from alphaflow.services.rag import get_vector_store
from langchain_community.document_loaders import WebBaseLoader
from alphaflow.core.config import settings
import logging


logger = logging.getLogger("alphaflow.tools")

@tool
def get_stock_price(symbol: str):
    """
    Fetches the current stock price and currency for a given ticker symbol.
    Useful for answering questions about "how much is X?" or "current price of X".
    """
    try:
        logger.debug(f"Fetching stock price for: {symbol}")
        ticker = yf.Ticker(symbol)
        price = ticker.fast_info.last_price
        currency = ticker.fast_info.currency
        return {"symbol": symbol, "price": price, "currency": currency}
    except Exception as e:
        logger.error(f"Error fetching price for {symbol}: {e}", exc_info=True)
        return f"Error fetching price for {symbol}: {str(e)}"

@tool
def get_company_profile(symbol: str):
    """
    Fetches fundamental company information: sector, summary, and market cap.
    Useful for "what does X do?" or fundamental analysis.
    """
    try:
        logger.debug(f"Fetching company profile for: {symbol}")
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return {
            "symbol": symbol,
            "name": info.get("longName"),
            "sector": info.get("sector"),
            "market_cap": info.get("marketCap"),
            "summary": info.get("longBusinessSummary")[:500] + "..." 
        }
    except Exception as e:
        logger.error(f"Error fetching profile for {symbol}: {e}", exc_info=True)
        return f"Error fetching profile for {symbol}: {str(e)}"

@tool
def search_financial_news(query: str):
    """
    Search for recent financial news, market rumors, or specific company events.
    Useful for answering "Why" a stock is moving or gathering qualitative context.
    
    Args:
        query: The search string (e.g., "Why is TSLA up?", "NVIDIA regulatory news")
    """
    try:
        logger.debug(f"Searching financial news for: {query}")
        db = get_vector_store()
        
        results = db.similarity_search(query, k=settings.search_k_results)
        
        if not results:
            logger.info("No news results found.")
            return "No relevant news found in the database."
            
        formatted_results = ""
        for doc in results:
            formatted_results += f"""

        ---
        Title/Source: {doc.metadata.get('source', 'Unknown')}
        Date: {doc.metadata.get('date', 'Unknown')}
        Content: {doc.page_content}
        """

        return formatted_results

    except Exception as e:
        logger.error(f"Error querying news database: {e}", exc_info=True)
        return f"Error querying news database: {str(e)}"

@tool
def read_website_content(url: str):
    """
    Reads text from a specific URL. 
    Use this when the user provides a link (http/https) and asks you to analyze it.
    """
    try:
        logger.debug(f"Reading website content: {url}")
        loader = WebBaseLoader(url)
        docs = loader.load()
        content = "\n\n".join([d.page_content for d in docs])
        return " ".join(content.split())[:20000]
        
    except Exception as e:
        logger.error(f"Error reading website {url}: {e}", exc_info=True)
        return f"Error reading website: {str(e)}"


finance_tools = [
    get_stock_price, 
    get_company_profile, 
    search_financial_news,
    read_website_content,
    ]