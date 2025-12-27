import logging
import logging
from alphaflow.workflows.entrypoint import build_graph
from langchain_core.messages import HumanMessage


def run(user_id: str, user_input: str):
    print("Initializing AlphaFlow (Phase 2: Tools)...")
    app = build_graph()
    
    config = {"configurable": {"thread_id": user_id}} 

    print(f"👤 User: {user_input}")
    
    initial_state = {
        "messages": [HumanMessage(content=user_input)],
    }
    
    # Run the graph
    for output in app.stream(initial_state, config=config):
        for node_name, value in output.items():
            print(f"--- Step: {node_name} ---")
            
            # Inspect the last message to see what happened
            last_message = value["messages"][-1]
            
            # If the Analyst spoke (Tool Call or Final Answer)
            if node_name == "analyst":
                if getattr(last_message, "tool_calls", None):
                    for tc in last_message.tool_calls:
                        print(f"   🛠️  Analyst calling tool: {tc['name']} (Args: {tc['args']})")
                else:
                    print(f"   💬 Analyst: {last_message.content}")
            
            # If the Tool ran
            elif node_name == "tools":
                logging.debug(f"   📊 Tool Result: {last_message.content}")

def run_silent(user_id: str, user_input: str):
    app = build_graph()
    config = {"configurable": {"thread_id": user_id}}
    
    initial_state = {"messages": [HumanMessage(content=user_input)]}
    final_state = app.invoke(initial_state, config=config)
    
    return final_state["messages"][-1].content

if __name__ == "__main__":
    # run("cli_user", "What is the price of TSLA?\n\n")
    result = run_silent("cli_user", "Did i ask something before")
    logging.info("Message: %s", result)