from langgraph.types import Command
import logging
import logging
from alphaflow.workflows.entrypoint import build_graph
from langchain_core.messages import HumanMessage

def check_keys():
    from dotenv import load_dotenv
    import os

    load_dotenv()

    key = os.getenv("LANGCHAIN_API_KEY")

    print(f"--- DEBUG INFO ---")
    if key:
        print(f"Key Found: Yes")
        print(f"Length: {len(key)}")
        print(f"Starts with: {key[:5]}...")
        print(f"Ends with: ...{key[-5:]}")
        
        # Check for hidden whitespace
        if key.strip() != key:
            print("❌ CRITICAL ERROR: Your key has hidden spaces at the start or end!")
        else:
            print("✅ No hidden spaces found.")
    else:
        print("❌ Key NOT found in os.environ")

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

def run_interactive(user_id: str, user_input: str):
    print("🚀 AlphaFlow (Human-in-the-Loop Mode)")
    app = build_graph()
    
    # Use a specific thread so we can resume it
    config = {"configurable": {"thread_id": user_id}}
    
    initial_state = {"messages": [HumanMessage(content=user_input)]}
    
    print("\n--- 🤖 Agent Working ---")
    
    # 1. RUN UNTIL INTERRUPT
    # stream() will run until it hits "publisher" and then stop automatically.
    for output in app.stream(initial_state, config=config):
        for key, value in output.items():
            print(f"⚡ {key} finished.")

    # 2. CHECK STATUS
    # We look at the current state of the graph
    snapshot = app.get_state(config)
    
    # If the next step is "publisher", we are paused!
    if snapshot.next and "publisher" in snapshot.next:
        print("\n✋ [PAUSED] Agent has drafted a response.")
        print("--- DRAFT ---")
        print(snapshot.values["messages"][-1].content)
        print("-------------")
        
        # 3. HUMAN DECISION
        review = input("\nType 'yes' to publish, or type feedback to edit: ")
        
        if review.lower() in ["yes", "y", "approve"]:
            print("\n✅ Approving...")
            # Resume execution (None means "continue as planned")
            for output in app.stream(Command(resume="Approve"), config=config):
                 for key, value in output.items():
                    print(f"⚡ {key} finished.")
                    
        else:
            print(f"\n↩️ Sending feedback: '{review}'...")
            # We inject the human feedback as a new message
            # and the graph will loop back to Analyst because Publisher didn't run.
            feedback_message = HumanMessage(content=f"Reviewer Feedback: {review}")
            
            # Update state with feedback
            app.update_state(config, {"messages": [feedback_message]})
            
            # Resume (The Analyst will see the feedback and try again)
            for output in app.stream(None, config=config):
                 for key, value in output.items():
                    print(f"⚡ {key} finished.")

if __name__ == "__main__":
    # run("cli_user", "What is the price of TSLA?\n\n")
    # result = run_silent("cli_user", "what is the latest news about TSLA?")
    # logging.info("Message: %s", result)
    run_interactive("cli_user", "what is the latest news about TSLA?")