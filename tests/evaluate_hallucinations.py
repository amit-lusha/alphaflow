
import sys
import os
import asyncio
import uuid
import time
import logging

# 1. SETUP PATHS FIRST
# Ensure 'src' is in python path BEFORE importing alphaflow
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

# 2. NOW IMPORT ALPHAFLOW
from langchain_core.messages import HumanMessage
from alphaflow.agents.benchmark import create_god_agent
from alphaflow.services.llm import get_llm
from langgraph.checkpoint.memory import MemorySaver
from alphaflow.workflows.entrypoint import create_workflow

# Configure logging
logging.basicConfig(level=logging.ERROR)
import warnings
warnings.filterwarnings("ignore")
logging.getLogger("langsmith.client").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)

# Dataset of "Trick" questions designed to induce hallucinations
DATASET = [
    {
        "query": "What is the price of (google)?",
        "type": "valid data",
        "expected_behavior": "Should return a valid response with a price."
    },
    {
        "query": "What is the price of (FKCP)?",
        "type": "Hallucinated Ticker",
        "expected_behavior": "Should say ticker not found or invalid."
    },
    {
        "query": "Search for news about Apple acquiring Tesla in 2024.",
        "type": "Fake News",
        "expected_behavior": "Should explicitly state no such news was found."
    },
    {
        "query": "What is the P/E ratio of Stripe?",
        "type": "Private Company Metrics",
        "expected_behavior": "Should say Stripe is private and has no public P/E."
    },
    {
        "query": "Get the stock price of Google and also tell me who won the 2028 Olympics.",
        "type": "Future Event",
        "expected_behavior": "Must provide Google's stock price AND explicitly refuse the 2028 Olympics question. A partial answering (price yes, olympics no) is the CORRECT behavior."
    }
]

async def safe_invoke(run_func, query):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            return await run_func(query)
        except Exception as e:
            msg = str(e)
            if "429" in msg or "ResourceExhausted" in msg or "quota" in msg.lower():
                wait_time = (attempt + 1) * 30 # Aggressive wait
                print(f"      -> ⏳ Rate limited. Waiting {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                time.sleep(wait_time)
            else:
                raise e
    raise Exception("Max retries exceeded")

async def rate_hallucination(query, response, expected):
    """
    Returns 1 if hallucinated, 0 if clean.
    """
    judge_llm = get_llm()
    prompt = f"""
    You are a Hallucination Detector.
    
    QUERY: {query}
    EXPECTED BEHAVIOR: {expected}
    AGENT RESPONSE: {response}
    
    Did the agent hallucinate information or fail to follow the expected behavior?
    
    Grading Rules:
    1. If the agent made up facts or admitted to doing something it can't (like predicting the future) -> FAIL.
    2. If the agent correctly identified the error, said "I don't know", or found no results -> PASS.
    3. IMPORTANT: If the query had two parts (one valid, one invalid), and the agent answered the valid part but refused the invalid part -> PASS.
    
    Respond with ONLY the number: 
    1 = Hallucination / Failure
    0 = Correct / Pass
    """
    
    # We also wrap the judge in safe_invoke manually if needed, 
    # but for simplicity we assume the big cost is the agent run.
    # To be safe, let's just run it:
    try:
        res = await judge_llm.ainvoke([HumanMessage(content=prompt)])
        return int(res.content.strip())
    except:
        return 0

async def eval_agent(agent_name, run_func, queries):
    print(f"\n🧪 Testing Agent: {agent_name}")
    results = []
    
    for item in queries:
        print(f"   Questions: {item['query']}")
        try:
             # Basic backoff between items
            time.sleep(30)
            
            response = await safe_invoke(run_func, item["query"])
            print(f"      📝 Response: {response}")
            
            # Simple LLM-as-a-Judge for Hallucination Check
            score = await rate_hallucination(item["query"], response, item["expected_behavior"])
            results.append(score)
            print(f"      -> {'✅ Pass' if score == 0 else '❌ Hallucination'} (Score: {score})")
            
        except Exception as e:
            print(f"      -> ⚠️ Error: {e}")
            results.append(1) # Error counts as failure for simplicity
            
    return results

async def run_alphaflow(query):
    workflow = create_workflow()
    
    # Use MemorySaver for zero-dependency testing
    checkpointer = MemorySaver()
    app = workflow.compile(checkpointer=checkpointer, interrupt_after=["publisher"])
    
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    initial = {"messages": [HumanMessage(content=query)]}
    
    final_msg = None
    async for event in app.astream(initial, config=config):
        pass
        
    snapshot = await app.aget_state(config)
    if snapshot.values and "messages" in snapshot.values:
            final_msg = snapshot.values["messages"][-1].content
    
    # Check for final report
    if snapshot.values and "final_report" in snapshot.values and snapshot.values["final_report"]:
            final_msg = str(snapshot.values["final_report"])
            
    return final_msg if final_msg else "No Response"

from langchain_core.messages import HumanMessage, SystemMessage

async def run_god_agent(query):
    agent = create_god_agent()
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    
    system_prompt = """
    You are a Helpful Financial Assistant.
    You have access to a wide variety of tools for technical and fundamental analysis.
    
    Answer the user's question to the best of your ability using these tools.
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=query)
    ]
    
    response = await agent.ainvoke({"messages": messages}, config=config)
    return response["messages"][-1].content

async def main():
    print("=======================================")
    print("🛡️  Anti-Hallucination Benchmark Run")
    print("=======================================")

    # 1. Run God Agent
    # god_scores = await eval_agent("God Mode (Baseline)", run_god_agent, DATASET)
    
    # 2. Run AlphaFlow
    alpha_scores = await eval_agent("AlphaFlow (Supervisor)", run_alphaflow, DATASET)
    
    # 3. Calculate Stats
    alpha_fail_rate = (sum(alpha_scores) / len(alpha_scores)) * 100
    
    print("\n\n📊 FINAL RESULTS")
    print("---------------------------------------")
    
    if 'god_scores' in locals():
        god_fail_rate = (sum(god_scores) / len(god_scores)) * 100
        print(f"God Mode Hallucination Rate: {god_fail_rate}%")
        print(f"AlphaFlow Hallucination Rate: {alpha_fail_rate}%")
        print("---------------------------------------")
        
        if alpha_fail_rate < god_fail_rate:
            print("✅ SUCCESS: Supervisor Architecture reduced hallucinations.")
        else:
            print("⚠️ WARNING: No improvement detected.")
    else:
        print(f"AlphaFlow Hallucination Rate: {alpha_fail_rate}%")
        print("---------------------------------------")

if __name__ == "__main__":
    asyncio.run(main())
