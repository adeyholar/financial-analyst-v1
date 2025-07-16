# D:\AI\Gits\financial-analyst-v1\src\agents\code_writer.py
from pydantic import BaseModel, Field
from crewai import Agent

class CodeOutput(BaseModel):
    code: str = Field(..., description="Executable Python code for stock visualization")

    class Config:
        json_schema_extra = {
            "required": ["code"]
        }

class CodeWriterAgent(Agent):
    def __init__(self, llm):
        super().__init__(
            llm=llm,
            role="Senior Python Developer",
            goal="Write executable Python code to visualize stock data",
            backstory="A senior developer specializing in stock market data visualization and writing production-ready Python code."
        )

    def write_code(self, analysis: dict) -> CodeOutput:
        # Placeholder for code generation logic (to be implemented)
        code = """
import yfinance as yf
import matplotlib.pyplot as plt

stocks = {symbols}
data = yf.download(stocks, period={timeframe})['Adj Close']
data.plot(title=f'YTD Stock Gains for {stocks}')
plt.show()
""".format(symbols=analysis['symbols'], timeframe=analysis['timeframe'])
        return CodeOutput(code=code)