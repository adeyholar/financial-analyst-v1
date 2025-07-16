# D:\AI\Gits\financial-analyst-v1\src/crew\finance_crew.py
from crewai import Crew, Process, Task, LLM
from src.agents.query_parser import QueryParserAgent, QueryAnalysisOutput  # Import QueryAnalysisOutput
from src.agents.code_writer import CodeWriterAgent
from src.agents.code_executor import CodeExecutorAgent
from src.config.llm_config import llm
import logging
import json

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define agents
query_parser = QueryParserAgent(llm=llm)
code_writer = CodeWriterAgent(llm=llm)
code_executor = CodeExecutorAgent(llm=llm)

# Define tasks as Task objects with output_pydantic
tasks = [
    Task(
        agent=query_parser,
        description="Parse the user query and extract stock details",
        expected_output="A structured output with symbols, timeframe, and action",
        output_pydantic=QueryAnalysisOutput  # Correct parameter name
    ),
    Task(
        agent=code_writer,
        description="Write Python code to visualize stock data based on the parsed query",
        expected_output="An executable Python script"
    ),
    Task(
        agent=code_executor,
        description="Execute the generated Python code to produce a plot",
        expected_output="A confirmation of plot generation"
    )
]

# Create crew
crew = Crew(
    agents=[query_parser, code_writer, code_executor],
    tasks=tasks,
    process=Process.sequential
)

# Monkey patch LLM call to log request and response, handling non-serializable objects
original_call = llm.call
def patched_call(self, *args, **kwargs):
    serializable_kwargs = {k: v for k, v in kwargs.items() if not isinstance(v, type) or v.__name__ != 'TokenCalcHandler'}
    logger.debug(f"LLM Request: {json.dumps(serializable_kwargs)}")
    response = original_call(*args, **kwargs)
    logger.debug(f"LLM Response: {response}")
    return response
llm.call = patched_call.__get__(llm, LLM)

# Execute the crew
if __name__ == "__main__":
    logger.debug("Starting crew with query: Plot YTD stock gains for Tesla vs Nvidia")
    result = crew.kickoff(inputs={"query": "Plot YTD stock gains for Tesla vs Nvidia"})
    logger.debug(f"Result from crew: {result}")