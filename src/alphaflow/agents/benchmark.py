from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent
from alphaflow.services.llm import get_llm
from alphaflow.agents.technical import tech_tools
from alphaflow.agents.fundamental import fund_tools

def create_god_agent():
    """
    Creates a standard ReAct agent that has access to ALL tools.
    This serves as a baseline to demonstrate why splitting tools 
    and responsibilities (Supervisor) is better.
    """
    
    # Merge all tools into one massive list
    all_tools = tech_tools + fund_tools
    
    llm = get_llm()
    
    system_message = """
    You are a Helpful Financial Assistant.
    You have access to a wide variety of tools for technical and fundamental analysis.
    
    Answer the user's question to the best of your ability using these tools.
    """
    
    # Create a simple ReAct agent (Graph)
    agent_graph = create_react_agent(llm, tools=all_tools)
    
    return agent_graph
