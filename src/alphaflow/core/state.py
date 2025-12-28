import operator
from typing import Annotated, List
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from alphaflow.core.schema import FinancialReport


class StockQuery(BaseModel):
    """Extracted intent from user query."""
    symbol: str = Field(..., description="The stock ticker symbol (e.g., AAPL)")
    request_type: str = Field(..., description="Type of analysis: technical, fundamental, or general")

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

    query_data: StockQuery | None = None
    next: str | None = None 
    final_report: FinancialReport | None = None 