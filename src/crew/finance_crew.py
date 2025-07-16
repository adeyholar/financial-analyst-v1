# D:\AI\Gits\financial-analyst-v1\src\crew\finance_crew.py
from crewai import Crew, Process, Task
from src.agents.query_parser import QueryParserAgent
from src.agents.code_writer import CodeWriterAgent
from src.agents.code_executor import CodeExecutorAgent
from src.config.llm_config import llm  # Assuming llm_config.py exports the LLM instance

# Step 6: Set up Crew and Kickoff
crew = Crew(
    agents=[QueryParserAgent(llm), CodeWriterAgent(llm), CodeExecutorAgent(llm)],
    tasks=[
        Task(
            description="Parse the user query and extract stock details.",
            expected_output="A structured output with stock symbols, timeframe, and action.",
            agent=QueryParserAgent(llm)
        ),
        Task(
            description="Write executable Python code to visualize stock data.",
            expected_output="A string containing executable Python code for stock visualization.",
            agent=CodeWriterAgent(llm)
        ),
        Task(
            description="Review and execute the Python code to generate a plot.",
            expected_output="A confirmation message or the generated plot data.",
            agent=CodeExecutorAgent(llm)
        ),
    ],
    process=Process.sequential
)

# Main execution block
if __name__ == "__main__":
    result = crew.kickoff(inputs={"query": "Plot YTD stock gains for Tesla vs Nvidia"})
    print(result)