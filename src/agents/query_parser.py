# D:\AI\Gits\financial-analyst-v1\src\agents\query_parser.py
from pydantic import BaseModel, Field
from typing import List
from crewai import Agent

class QueryAnalysisOutput(BaseModel):
    symbols: List[str] = Field(..., description="List of stock ticker symbols")
    timeframe: str = Field(..., description="Time period")
    action: str = Field(..., description="Action to be performed")

    class Config:
        json_schema_extra = {
            "required": ["symbols", "timeframe", "action"]
        }

class QueryParserAgent(Agent):
    def __init__(self, llm):
        super().__init__(
            llm=llm,
            role="Query Parser",
            goal="Parse user queries into structured data",
            backstory="A skilled data analyst specializing in extracting stock market details from natural language."
        )

    def parse(self, query: str) -> QueryAnalysisOutput:
        # Placeholder for parsing logic (to be implemented based on crewai tools)
        return QueryAnalysisOutput(symbols=["TSLA", "NVDA"], timeframe="YTD", action="plot")