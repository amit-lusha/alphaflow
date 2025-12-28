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
    
    if snapshot.values and "final_report" in snapshot.values:
        report = snapshot.values["final_report"]
        
        # Check if report exists (it might be None if we are in early steps)
        if report:
            
            print("\n📊 [DRAFT GENERATED] - Please Review")
            print("------------------------------------------------")
            print(report.json())
            print("------------------------------------------------")
            
            review = input("\nType 'approve' to finish, or provide feedback: ")
            
            if review.lower() == "approve":
                print("✅ Report Finalized.")
                # In a real app, you would return 'report.json()' to the API here
                return report
            else:
                print("↩️ Sending feedback...")
                app.update_state(config, {"messages": [HumanMessage(content=f"Feedback: {review}")]})
                # We need to route BACK to supervisor or analyst.
                # Since Publisher is a sink, we might need a conditional edge loop.
                # For simplicity in this phase, we just invoke again, 
                # but ideally, you'd wire Publisher -> Supervisor in entrypoint.py
                
                # Let's run the stream again
                for output in app.stream(None, config=config):
                    pass

if __name__ == "__main__":
    # Example Usage:
    # 1. Default run
    # 2. Or pass arguments via CLI: python main.py "thread_123" "What is NVDA price?"
    
    t_id = "cli_manager_1"
    user_prompt = "Get the current stock price of NVIDIA (NVDA) and look up recent news to explain why it is moving."
    
    run(thread_id=t_id, prompt=user_prompt)