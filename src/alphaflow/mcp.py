from mcp.server.fastmcp import FastMCP
from langchain_core.messages import HumanMessage
from alphaflow.workflows.entrypoint import build_graph
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("AlphaFlow")

@mcp.tool()
async def ask_market_analyst(query: str) -> str:
    try:
        app = build_graph()
        initial_state = {
            "messages": [HumanMessage(content=query)]
        }

        final_state = await app.ainvoke(initial_state)
        final_message = final_state["messages"][-1]
        return final_message.content

    except Exception as e:
        return f"AlphaFlow Error: {str(e)}"


if __name__ == "__main__":
    mcp.run()