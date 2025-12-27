
from alphaflow.tools.finance import finance_tools
from langchain_google_genai import ChatGoogleGenerativeAI
from alphaflow.core.config import settings

_llm_instance = None

def get_llm():
    global _llm_instance

    if _llm_instance is None:    
        _llm_instance = ChatGoogleGenerativeAI(
            model=settings.llm_model_name,
            temperature=settings.llm_temperature,
            api_key=settings.google_api_key
        )

    return _llm_instance

def get_finance_llm():
    return get_llm().bind_tools(finance_tools)