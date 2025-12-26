from alphaflow.graph import build_graph
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

load_dotenv()

def run():
    print("Initializing AlphaFlow (Phase 2: Tools)...")
    app = build_graph()
    
    config = {"configurable": {"thread_id": "cli_test_user"}} 
    # Let's ask a question that requires a tool
    user_input = "check for NVDA as well?"
    # user_input = "can you tell me what was the last question i asked"

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
                if last_message.tool_calls:
                    print(f"   🛠️  Analyst calling tool: {last_message.tool_calls[0]['name']}")
                else:
                    print(f"   💬 Analyst: {last_message.content}")
            
            # If the Tool ran
            elif node_name == "tools":
                print(f"   📊 Tool Result: {last_message.content}")

if __name__ == "__main__":
    run()