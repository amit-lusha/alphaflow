from contextlib import asynccontextmanager
import os
import aiosqlite
from alphaflow.agents.superviser import supervisor_node
import sqlite3
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from alphaflow.core.state import AgentState
from alphaflow.agents.technical import technical_analyst_node, tech_tools
from alphaflow.agents.fundamental import fundamental_analyst_node, fund_tools
from alphaflow.agents.publisher import publisher_node

DB_URI = os.getenv("POSTGRES_URI", "postgresql://alpha_user:alpha_pass@localhost:5432/alphaflow_db")
def create_workflow() -> StateGraph:
    """
    Defines the nodes and edges (Logic only, no memory).
    Returns the uncompiled StateGraph.
    """
    workflow = StateGraph(AgentState)
    
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("technical_analyst", technical_analyst_node)
    workflow.add_node("fundamental_analyst", fundamental_analyst_node)
    workflow.add_node("publisher", publisher_node)
    workflow.add_node("tech_tools", ToolNode(tech_tools))
    workflow.add_node("fund_tools", ToolNode(fund_tools))
    
    workflow.set_entry_point("supervisor")
    
    workflow.add_conditional_edges("supervisor", lambda x: x["next"], {
        "technical_analyst": "technical_analyst",
        "fundamental_analyst": "fundamental_analyst",
        "publisher": "publisher"
    })
    
    workflow.add_conditional_edges("technical_analyst", 
        lambda x: "tech_tools" if x["messages"][-1].tool_calls else "supervisor",
        {"tech_tools": "tech_tools", "supervisor": "supervisor"}
    )
    workflow.add_edge("tech_tools", "technical_analyst")
    
    workflow.add_conditional_edges("fundamental_analyst", 
        lambda x: "fund_tools" if x["messages"][-1].tool_calls else "supervisor",
        {"fund_tools": "fund_tools", "supervisor": "supervisor"}
    )
    workflow.add_edge("fund_tools", "fundamental_analyst")
    workflow.add_edge("publisher", END)
    
    return workflow

@asynccontextmanager
async def build_async_graph_context():
    workflow = create_workflow()

    async with AsyncPostgresSaver.from_conn_string(DB_URI) as checkpointer:
        await checkpointer.setup()
        app = workflow.compile(checkpointer=checkpointer, interrupt_after=["publisher"])
        
        yield app


def build_graph():
    workflow = create_workflow()
    
    with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
        checkpointer.setup()
        return workflow.compile(checkpointer=checkpointer, interrupt_after=["publisher"])