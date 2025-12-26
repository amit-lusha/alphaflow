import sqlite3
from alphaflow.tools.finance import finance_tools
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from alphaflow.state import AgentState
from alphaflow.agents.analyst import reason_about_query  

def build_graph():
    """Constructs the Phase 2 Cyclic Graph (Reason <-> Act)."""
    
    workflow = StateGraph(AgentState)
    
    # Node 1: The Analyst (Decides what to do)
    # Note: I changed the name from 'reason_agent' to 'analyst' for clarity
    workflow.add_node("analyst", reason_about_query)
    
    # Node 2: The Tool Executor (Runs the function)
    workflow.add_node("tools", ToolNode(finance_tools))
    
    # Define the Flow
    workflow.set_entry_point("analyst")
    
    # CONDITIONAL EDGE:
    # Check if the analyst wants to call a tool or stop.
    workflow.add_conditional_edges(
        "analyst",
        tools_condition,  # Automatic check for 'tool_calls'
    )
    
    # CYCLIC EDGE:
    # If tools run, go back to analyst to interpret results
    workflow.add_edge("tools", "analyst")
    
    conn = sqlite3.connect("alphaflow_memory.sqlite", check_same_thread=False)
    memory = SqliteSaver(conn)

    return workflow.compile(checkpointer=memory)