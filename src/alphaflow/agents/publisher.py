from alphaflow.services.llm import get_llm
from alphaflow.agents.agent import PublisherPersona
from alphaflow.core.state import AgentState
from alphaflow.core.schema import FinancialReport

def publisher_node(state: AgentState):
    messages = state["messages"]
    
    llm = get_llm().with_structured_output(FinancialReport)
    
    system_msg = PublisherPersona().get_system_message()
    
    report = llm.invoke([system_msg] + messages)
    return {"final_report": report}