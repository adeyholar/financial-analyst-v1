# D:\AI\Gits\financial-analyst-v1\src\agents\query_parser.py
from pydantic import BaseModel, Field
from crewai import Agent

class QueryAnalysisOutput(BaseModel):
    symbols: list[str] = Field(..., description="List of stock ticker symbols")  # Removed required=True
    timeframe: str = Field(..., description="Time period for the analysis")     # Removed required=True
    action: str = Field(..., description="Action to be performed")              # Removed required=True

    class Config:
        json_schema_extra = {
            "examples": [
                {"symbols": ["TSLA", "NVDA"], "timeframe": "YTD", "action": "plot"}
            ]
        }

class QueryParserAgent(Agent):
    def __init__(self, llm):
        super().__init__(
            llm=llm,
            role="Stock Data Analyst",
            goal="Extract stock details from user queries",
            backstory="A financial analyst specializing in stock market data retrieval."
        )

    def parse_query(self, query: str) -> QueryAnalysisOutput:
        # Placeholder implementation: parse query and return a sample output
        if "Plot" in query and "vs" in query:
            symbols = query.split("vs")[0].replace("Plot", "").strip().split()
            other_symbol = query.split("vs")[1].strip().split()[0]
            symbols.append(other_symbol)
            return QueryAnalysisOutput(
                symbols=symbols,
                timeframe="YTD",  # Default timeframe
                action="plot"
            )
        raise ValueError("Unsupported query format. Use 'Plot [symbol] vs [symbol]' format.")