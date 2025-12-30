from langchain_core.messages.human import HumanMessage
from langgraph.types import Command
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from alphaflow.workflows.entrypoint import build_async_graph_context

load_dotenv()

graph_context = None
graph = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global graph, graph_context
    print("🔄 Initializing Async Graph...")
    
    graph_context = build_async_graph_context()
    graph = await graph_context.__aenter__()
    
    yield
    
    print("🛑 Closing Async Graph...")
    await graph_context.__aexit__(None, None, None)
app = FastAPI(title="AlphaFlow API", version="2.0", lifespan=lifespan)


class InitRequest(BaseModel):
    query: str
    thread_id: str

class ReviewRequest(BaseModel):
    thread_id: str
    action: str
    feedback: str = None

@app.get("/")
def health():
    return {"status": "active", "system": "AlphaFlow Multi-Agent"}

@app.post("/research")
async def start_research(payload: InitRequest):
    config = {"configurable": {"thread_id": payload.thread_id}}
    print(f"📥 Starting research for thread: {payload.thread_id}")
    
    try:
        # 1. Run the Graph
        initial_state = {"messages": [HumanMessage(content=payload.query)]}
        async for event in graph.astream(initial_state, config=config):
            pass 
        
        # 2. Get the Resulting State
        snapshot = await graph.aget_state(config)
        
        # FIX: Check for the DATA ('final_report'), not just the execution status ('next')
        if snapshot.values and "final_report" in snapshot.values:
            report = snapshot.values["final_report"]
            
            # If the report is None (e.g. early step), we keep processing
            if report:
                return {
                    "status": "review_required", # or "success"
                    "draft": report
                }

        # If we are here, the graph finished but produced no report (or is still working)
        return {"status": "processing", "message": "Agent is working, no report yet."}

    except Exception as e:
        print(f"Server Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/review")
async def review_research(payload: ReviewRequest):
    config = {"configurable": {"thread_id": payload.thread_id}}
    
    try:
        if payload.action == "approve":
            async for event in graph.astream(Command(resume="Approve"), config=config):
                pass
            
            snapshot = await graph.aget_state(config)
            if "final_report" in snapshot.values:
                return {"status": "published", "report": snapshot.values["final_report"]}
                
        else:
            feedback = HumanMessage(content=f"Feedback: {payload.feedback}")
            await graph.aupdate_state(config, {"messages": [feedback]})
            
            async for event in graph.astream(None, config=config):
                pass
            return {"status": "feedback_processing", "message": "Revising..."}

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("alphaflow.server:app", host="0.0.0.0", port=8000, reload=True)