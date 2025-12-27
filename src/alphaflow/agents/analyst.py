
from alphaflow.services.llm import get_finance_llm
from alphaflow.core.prompts import get_analyst_system_message
from langchain_core.messages import SystemMessage, HumanMessage
from alphaflow.core.state import AgentState, StockQuery

def reason_about_query(state: AgentState):
    """
    Node 1: Analyze the user's input and extract the Ticker.
    """
    llm = get_finance_llm()
    messages = state["messages"]
    
    system_msg = get_analyst_system_message()
    
    response = llm.invoke([system_msg] + messages)
    
    return {"messages": [response]}

def generate_report(state: AgentState):
    ticker = state["query_data"].symbol
    
    return {
        "messages": [HumanMessage(content=f"Finished analyzing {ticker}.")],
        "final_report": {
            "summary": f"Basic analysis for {ticker} complete.",
            "recommendation": "Hold",
            "risk_level": "Medium"
        }
    }