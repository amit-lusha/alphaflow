from mcp.server.fastmcp import FastMCP
from langchain_core.messages import HumanMessage
from src.alphaflow.graph import build_graph
from dotenv import load_dotenv

# 1. Setup Environment
# We need to load keys because the server might run in a different process
load_dotenv()

# 2. Initialize the Server
# "AlphaFlow" is the name users will see
mcp = FastMCP("AlphaFlow")

# 3. Define the Capability
# We expose the ENTIRE agent as a single tool to the outside world.
@mcp.tool()
async def ask_market_analyst(query: str) -> str:
    """
    Consult the AlphaFlow Financial Agent. 
    Use this to get real-time stock prices, technical analysis, 
    news summaries, or web-based financial research.
    
    Args:
        query: The user's question (e.g., "Analyze TSLA stock", "Why is NVDA down?")
    """
    try:
        # A. Initialize the Graph
        app = build_graph()
        
        # B. Prepare the Input State
        initial_state = {
            "messages": [HumanMessage(content=query)]
        }
        
        # C. Run the Graph
        # We use .invoke() instead of .stream() because MCP tools expect a single final answer,
        # not a stream of tokens (for now).
        final_state = await app.ainvoke(initial_state)
        
        # D. Extract the Result
        # The final message in the list is the Agent's conclusion
        final_message = final_state["messages"][-1]
        
        return final_message.content

    except Exception as e:
        return f"AlphaFlow Error: {str(e)}"

# 4. Entry Point
if __name__ == "__main__":
    mcp.run()