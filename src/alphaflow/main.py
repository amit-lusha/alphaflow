from langchain_core.messages import HumanMessage
from langgraph.types import Command
import logging

from alphaflow.workflows.entrypoint import build_graph



def run(thread_id: str, prompt: str):
    print(f"🚀 AlphaFlow (Thread: {thread_id})")
    print(f"👤 User: {prompt}")
    
    app = build_graph()
    
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {"messages": [HumanMessage(content=prompt)]}
    
    print("\n--- 🤖 Agent Working ---")
    
    for output in app.stream(initial_state, config=config):
        for node_name, value in output.items():
            print(f"--- Step: {node_name} ---")
            
            if "next" in value:
                print(f"   🚦 Supervisor routed to: {value['next']}")
            
            if "messages" in value:
                last_message = value["messages"][-1]
                
                if getattr(last_message, "tool_calls", None):
                     for tc in last_message.tool_calls:
                        print(f"   🛠️  {node_name} calling tool: {tc['name']}")
    
                elif last_message.type == "tool":
                     print(f"   📊 Tool Output: {str(last_message.content)[:100]}...")

                else:
                    print(f"   💬 {node_name}: {last_message.content}")

    snapshot = app.get_state(config)
    
    if snapshot.values and "final_report" in snapshot.values:
        report = snapshot.values["final_report"]
        
        if report:
            
            print("\n📊 [DRAFT GENERATED] - Please Review")
            print("------------------------------------------------")
            print(report.json())
            print("------------------------------------------------")
            
            review = input("\nType 'approve' to finish, or provide feedback: ")
            
            if review.lower() == "approve":
                print("✅ Report Finalized.")
                return report

            else:
                print("↩️ Sending feedback...")
                app.update_state(config, {"messages": [HumanMessage(content=f"Feedback: {review}")]})
                
                for output in app.stream(None, config=config):
                    pass

if __name__ == "__main__":    
    t_id = "cli_manager_1"
    user_prompt = "Get the current stock price of NVIDIA (NVDA) and look up recent news to explain why it is moving."
    
    run(thread_id=t_id, prompt=user_prompt)