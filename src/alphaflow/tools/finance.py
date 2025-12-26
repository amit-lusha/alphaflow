import logging
import yfinance as yf
from langchain_core.tools import tool
from alphaflow.rag import get_vector_store
from langchain_community.document_loaders import WebBaseLoader

@tool
def get_stock_price(symbol: str):
    """
    Fetches the current stock price and currency for a given ticker symbol.
    Useful for answering questions about "how much is X?" or "current price of X".
    """
    try:
        ticker = yf.Ticker(symbol)
        price = ticker.fast_info.last_price
        currency = ticker.fast_info.currency
        return {"symbol": symbol, "price": price, "currency": currency}
    except Exception as e:
        return f"Error fetching price for {symbol}: {str(e)}"

@tool
def get_company_profile(symbol: str):
    """
    Fetches fundamental company information: sector, summary, and market cap.
    Useful for "what does X do?" or fundamental analysis.
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return {
            "symbol": symbol,
            "name": info.get("longName"),
            "sector": info.get("sector"),
            "market_cap": info.get("marketCap"),
            "summary": info.get("longBusinessSummary")[:500] + "..." # Truncate for token efficiency
        }
    except Exception as e:
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
        # 1. Connect to DB
        db = get_vector_store()
        
        # 2. Perform Similarity Search
        # k=3 means "Give me the top 3 most relevant matches"
        results = db.similarity_search(query, k=3)
        
        if not results:
            return "No relevant news found in the database."
            
        # 3. Format Output
        # The LLM needs text, not objects. We format it nicely.
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
        return f"Error querying news database: {str(e)}"

@tool
def read_website_content(url: str):
    """
    Reads text from a specific URL. 
    Use this when the user provides a link (http/https) and asks you to analyze it.
    """
    try:
        logging.info(f"Reading website: {url}")
        loader = WebBaseLoader(url)
        docs = loader.load()
        # Combine content and clean whitespace
        content = "\n\n".join([d.page_content for d in docs])
        return " ".join(content.split())[:20000] # Limit size for safety
    except Exception as e:
        logging.error(f"Error reading website: {str(e)}")
        return f"Error reading website: {str(e)}"


finance_tools = [
    get_stock_price, 
    get_company_profile, 
    search_financial_news,
    read_website_content,
    ]