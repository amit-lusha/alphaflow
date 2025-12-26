from alphaflow.utils import get_finance_llm
from langchain_core.messages import SystemMessage, HumanMessage
from alphaflow.state import AgentState, StockQuery

def reason_about_query(state: AgentState):
    """
    Node 1: Analyze the user's input and extract the Ticker.
    """
    llm = get_finance_llm()
    all_messages = state["messages"]
    
    if len(all_messages) > 20:
        recent_messages = all_messages[-20:]
    else:
        recent_messages = all_messages
    # We add a system prompt to guide behavior
    system_msg = SystemMessage(content="""
    You are a financial analyst. 
    You have access to stock market tools. 
    1. If the user asks for a price, call 'get_stock_price'.
    2. If the user asks for company info, call 'get_company_profile'.
    3. If you have the data, answer directly.
    """)
    
    # Invoke the LLM with the bound tools
    response = llm.invoke([system_msg] + recent_messages)
    
    # We simply return the message. 
    # If the LLM decided to call a tool, 'response.tool_calls' will be populated.
    return {"messages": [response]}
    
    # Return updates to the state
    return {"query_data": result}

def generate_report(state: AgentState):
    """
    Node 2: Mock generation of a report based on gathered data.
    """
    ticker = state["query_data"].symbol
    
    # Mocking logic for Phase 1
    return {
        "messages": [HumanMessage(content=f"Finished analyzing {ticker}.")],
        "final_report": {
            "summary": f"Basic analysis for {ticker} complete.",
            "recommendation": "Hold",
            "risk_level": "Medium"
        }
    }