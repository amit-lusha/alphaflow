from alphaflow.core.prompts import get_supervisor_system_message
from typing import Literal
from pydantic import BaseModel
from langchain_core.messages import SystemMessage
from alphaflow.core.state import AgentState
from alphaflow.services.llm import get_llm

# 1. Define the Schema for the Router
class RouteResponse(BaseModel):
    next: Literal["technical_analyst", "fundamental_analyst", "publisher"]

def supervisor_node(state: AgentState):
    messages = state["messages"]
    
    # 2. Force the LLM to return JSON matching RouteResponse
    llm = get_llm().with_structured_output(RouteResponse)
    
    system_msg = get_supervisor_system_message()
    
    response = llm.invoke([system_msg] + messages)
    
    return {"next": response.next}