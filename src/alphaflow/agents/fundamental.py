from alphaflow.agents.agent import FundamentalPersona
from alphaflow.core.prompts import get_fundamental_system_message
from alphaflow.core.state import AgentState
from alphaflow.services.llm import get_llm
from alphaflow.tools.finance import search_financial_news, read_website_content

# 1. Define Tools strictly for this agent
fund_tools = [search_financial_news, read_website_content]

# 2. Bind Tools
llm = get_llm().bind_tools(fund_tools)

def fundamental_analyst_node(state: AgentState):
    """
    Worker node that deals with qualitative data (RAG, Web).
    """
    messages = state["messages"]
    
    system_msg = FundamentalPersona().get_system_message()
    
    response = llm.invoke([system_msg] + messages)
    
    return {"messages": [response]}