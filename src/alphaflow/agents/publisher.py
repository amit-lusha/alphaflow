from langchain_core.messages import AIMessage
from alphaflow.core.state import AgentState

def publisher_node(state: AgentState):
    last_message = state["messages"][-1]
    
    print(f"\n📢 [SYSTEM] Publishing Report to External API...\n")

    return {
        "messages": [AIMessage(content=f"APPROVED REPORT: {last_message.content}")]
    }