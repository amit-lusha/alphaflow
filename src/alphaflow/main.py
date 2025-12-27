from langgraph.types import Command
import logging
import logging
from alphaflow.workflows.entrypoint import build_graph
from langchain_core.messages import HumanMessage



def run(thread_id: str, prompt: str):
    """
    Runs the AlphaFlow agent with a specific thread ID and prompt.
    """
    print(f"🚀 AlphaFlow (Thread: {thread_id})")
    print(f"👤 User: {prompt}")
    
    app = build_graph()
    
    # Use the passed thread_id for persistence
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {"messages": [HumanMessage(content=prompt)]}
    
    print("\n--- 🤖 Agent Working ---")
    
    # 1. RUN THE GRAPH
    # We iterate through the stream of events
    for output in app.stream(initial_state, config=config):
        for node_name, value in output.items():
            print(f"--- Step: {node_name} ---")
            
            # CASE A: Supervisor (Routing Decision)
            if "next" in value:
                print(f"   🚦 Supervisor routed to: {value['next']}")
            
            # CASE B: Workers (Chat Messages)
            if "messages" in value:
                last_message = value["messages"][-1]
                
                # Check for Tool Calls
                if getattr(last_message, "tool_calls", None):
                     for tc in last_message.tool_calls:
                        print(f"   🛠️  {node_name} calling tool: {tc['name']}")
                # Check for Tool Outputs
                elif last_message.type == "tool":
                     print(f"   📊 Tool Output: {str(last_message.content)[:100]}...")
                # Normal Text
                else:
                    print(f"   💬 {node_name}: {last_message.content}")

    # 2. CHECK FOR PAUSE (Publisher Node)
    # The graph stops before 'publisher'. We check the state to see if we are paused.
    snapshot = app.get_state(config)
    
    if snapshot.next and "publisher" in snapshot.next:
        print("\n✋ [PAUSED] Report Drafted.")
        print("--- DRAFT ---")
        
        # Get the draft (Last message in history)
        draft = snapshot.values["messages"][-1].content
        print(draft)
        print("-------------")
        
        # Interactive Review
        # (If you are calling this from an API, you would remove this input() 
        # and handle the pause in the API logic instead)
        review = input("\nType 'yes' to publish, or feedback: ")
        
        if review.lower() in ["yes", "y", "approve"]:
            print("\n✅ Approving...")
            # Resume with an approval command
            for output in app.stream(Command(resume="Approve"), config=config):
                 print("⚡ Publishing...")
        else:
            print(f"\n↩️ Feedback: '{review}'")
            # Inject feedback and resume
            app.update_state(config, {"messages": [HumanMessage(content=f"Feedback: {review}")]})
            for output in app.stream(None, config=config):
                 pass # Let it loop back to the supervisor

if __name__ == "__main__":
    # Example Usage:
    # 1. Default run
    # 2. Or pass arguments via CLI: python main.py "thread_123" "What is NVDA price?"
    
    t_id = "cli_manager_1"
    user_prompt = "Get the current stock price of NVIDIA (NVDA) and look up recent news to explain why it is moving."
    
    run(thread_id=t_id, prompt=user_prompt)