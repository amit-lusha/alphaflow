from typing import List, Dict, Literal
from pydantic import BaseModel, Field

class Metric(BaseModel):
    label: str = Field(description="Name of the metric (e.g., 'PE Ratio')")
    value: str = Field(description="Value of the metric (e.g., '45.2' or '$135')")

class Source(BaseModel):
    title: str
    url: str

class FinancialReport(BaseModel):
    ticker: str = Field(description="The main stock ticker symbol analyzed")
    current_price: float | None = Field(default=None, description="The latest price found. None if not found.")

    sentiment: Literal["Bullish", "Bearish", "Neutral"]
    risk_score: int = Field(description="Risk score from 1-10")
    
    executive_summary: str = Field(description="High-level summary for the user")
    
    key_metrics: List[Metric]
    sources: List[Source]