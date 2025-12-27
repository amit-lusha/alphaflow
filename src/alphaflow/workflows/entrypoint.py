import sqlite3
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver

from alphaflow.core.state import AgentState
from alphaflow.agents.analyst import reason_about_query
from alphaflow.agents.publisher import publisher_node # <--- Import
from alphaflow.tools.finance import finance_tools

def build_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("analyst", reason_about_query)
    workflow.add_node("tools", ToolNode(finance_tools))
    workflow.add_node("publisher", publisher_node)
    
    workflow.set_entry_point("analyst")

    workflow.add_conditional_edges(
        "analyst",
        tools_condition,
        {
            "tools": "tools",
            END: "publisher"
        }
    )
    
    workflow.add_edge("tools", "analyst")
    workflow.add_edge("publisher", END)
    
    conn = sqlite3.connect("alphaflow_memory.sqlite", check_same_thread=False)
    memory = SqliteSaver(conn)
    
    return workflow.compile(
        checkpointer=memory,
        interrupt_before=["publisher"]
    )