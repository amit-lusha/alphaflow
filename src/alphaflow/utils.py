from alphaflow.tools.finance import finance_tools
from langchain_google_genai import ChatGoogleGenerativeAI
import os

_llm_instance = None
def get_llm():

    """Returns a singleton instance of the Google Gemini LLM."""
    global _llm_instance
    if _llm_instance is None:
        # Ensure API key is present (optional check, but helpful)
        if not os.getenv("GOOGLE_API_KEY"):
            # Fallback or strict error, let's let LangChain handle the error but this comment notes it.
            pass
            
        _llm_instance = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0
        )
    return _llm_instance

def get_finance_llm():
    return get_llm().bind_tools(finance_tools)