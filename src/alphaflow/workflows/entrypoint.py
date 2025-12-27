import sqlite3
from alphaflow.tools.finance import finance_tools
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from alphaflow.core.state import AgentState
from alphaflow.agents.analyst import reason_about_query  

def build_graph():
    
    workflow = StateGraph(AgentState)
    
    workflow.add_node("analyst", reason_about_query)
    workflow.add_node("tools", ToolNode(finance_tools))
    workflow.set_entry_point("analyst")
    
    workflow.add_conditional_edges(
        "analyst",
        tools_condition,
    )
    
    workflow.add_edge("tools", "analyst")
    
    conn = sqlite3.connect("alphaflow_memory.sqlite", check_same_thread=False)
    memory = SqliteSaver(conn)

    return workflow.compile(checkpointer=memory)