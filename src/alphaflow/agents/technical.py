from alphaflow.core.prompts import get_technical_system_message
from langchain_core.messages import SystemMessage
from alphaflow.core.state import AgentState
from alphaflow.services.llm import get_llm
from alphaflow.tools.finance import get_stock_price, get_company_profile

tech_tools = [get_stock_price, get_company_profile]

llm = get_llm().bind_tools(tech_tools)

def technical_analyst_node(state: AgentState):
    """
    Worker node that deals with quantitative data.
    """
    messages = state["messages"]
    
    system_msg = get_technical_system_message()
    
    response = llm.invoke([system_msg] + messages)
    
    return {"messages": [response]}