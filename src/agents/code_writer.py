# D:\AI\Gits\financial-analyst-v1\src/agents/code_writer.py
from pydantic import BaseModel, Field
from pydantic.config import ConfigDict
from crewai import Agent

class CodeOutput(BaseModel):
    code: str = Field(..., description="Executable Python code for stock visualization")
    model_config = ConfigDict(json_schema_extra={"required": ["code"]})

class CodeWriterAgent(Agent):
    def __init__(self, llm):
        super().__init__(
            llm=llm,
            role="Senior Python Developer",
            goal="Write executable Python code to visualize stock data",
            backstory="A senior developer specializing in stock market data visualization and writing production-ready Python code."
        )

    def write_code(self, analysis: dict) -> CodeOutput:
        plot_output_dir = "plots"
        plot_filename = "stock_gains_plot.png"

        code = f"""
import yfinance as yf
import matplotlib.pyplot as plt
import os
import pandas as pd

# Create the plot directory if it doesn't exist
output_dir = "{plot_output_dir}"
os.makedirs(output_dir, exist_ok=True)

stocks = {analysis['symbols']}
timeframe = "{analysis['timeframe']}"

try:
    data = yf.download(stocks, period=timeframe)['Adj Close']
    
    if data.empty:
        print(f"No data downloaded for stocks: {{stocks}} in timeframe: {{timeframe}}")
        exit(1)

    if timeframe.lower() == 'ytd':
        if isinstance(data, pd.Series):
            data = data.to_frame()

        if not data.empty and len(data.index) > 1:
            data = data.sort_index()
            first_day_values = data.iloc[0]
            last_day_values = data.iloc[-1]
            
            ytd_gains = ((last_day_values - first_day_values) / first_day_values.replace(0, 1)) * 100
            
            plt.figure(figsize=(10, 6))
            if len(stocks) > 1:
                normalized_data = data / data.iloc[0] * 100
                normalized_data.plot(ax=plt.gca())
                plt.title(f'YTD Normalized Stock Performance for {{", ".join(stocks).upper()}} (Base: 100)')
                plt.ylabel('Normalized Value (%)')
            else:
                data.plot(ax=plt.gca())
                plt.title(f'YTD Stock Price for {{", ".join(stocks).upper()}}')
                plt.ylabel('Adjusted Close Price')
            
            plt.xlabel('Date')
            plt.grid(True, linestyle='--', alpha=0.7)
            
        else:
            print("Not enough data to calculate meaningful YTD gains. Plotting raw prices.")
            data.plot(title=f'Stock Prices for {{", ".join(stocks).upper()}} - Not enough data for YTD analysis', figsize=(10, 6))
            plt.ylabel('Adjusted Close Price')
            plt.grid(True, linestyle='--', alpha=0.7)
            
    else: # For other timeframes, just plot the prices
        # FIXED: Escaped timeframe.upper() with double curly braces
        data.plot(title=f'Stock Prices for {{", ".join(stocks).upper()}} ({{timeframe.upper()}})', figsize=(10, 6))
        plt.ylabel('Adjusted Close Price')
        plt.grid(True, linestyle='--', alpha=0.7)

    plot_path = os.path.join(output_dir, "{plot_filename}")
    plt.savefig(plot_path)
    print(f"Plot saved successfully to: {{plot_path}}")
    plt.close('all')
except Exception as e:
    print(f"Error generating plot: {{e}}")
    exit(1)

"""
        return CodeOutput(code=code)