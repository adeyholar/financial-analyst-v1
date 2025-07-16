# D:\AI\Gits\financial-analyst-v1\src/crew\finance_crew.py
from crewai import Crew, Process, Task, Agent
from src.agents.query_parser import QueryParserAgent, QueryAnalysisOutput
from src.agents.code_writer import CodeWriterAgent, CodeOutput
from src.agents.code_executor import CodeExecutorAgent, ExecutionOutput
from src.config.llm_config import llm # We import the configured llm directly
import logging
import json
import sys
import os
import re

# Removed unnecessary imports
# from crewai.utilities.token_counter_callback import TokenCalcHandler

# Set up logging to ensure output to console
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
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
        output_pydantic=QueryAnalysisOutput
    ),
    Task(
        agent=code_writer,
        description=(
            "Write executable Python code to visualize stock data based on the parsed query. "
            "The code must use yfinance and matplotlib. It should save the plot to 'plots/stock_gains_plot.png'. "
            "The output must be a CodeOutput Pydantic model containing the complete Python script."
        ),
        expected_output="A CodeOutput Pydantic model containing an executable Python script",
        output_pydantic=CodeOutput
    ),
    Task(
        agent=code_executor,
        description=(
            "Execute the generated Python code to produce a plot. "
            "Verify that the plot file 'plots/stock_gains_plot.png' is created. "
            "The output must be an ExecutionOutput Pydantic model confirming plot generation and path or detailing errors."
        ),
        expected_output="An ExecutionOutput Pydantic model confirming plot generation and path or detailing errors.",
        output_pydantic=ExecutionOutput
    )
]

# Create crew
crew = Crew(
    agents=[query_parser, code_writer, code_executor],
    tasks=tasks,
    process=Process.sequential
)

# --- REMOVED THE ENTIRE MONKEY-PATCHING SECTION ---
# This functionality is now handled by the LangChain callback in llm_config.py

def custom_json_serializer(obj):
    """Custom JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (Task, Agent)):
        return f"<{obj.__class__.__name__} instance at {hex(id(obj))}>"
    if hasattr(obj, 'model_dump'):
        return obj.model_dump()
    if hasattr(obj, 'dict'):
        return obj.dict()
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    try:
        # Fallback to default serialization for basic types
        json.dumps(obj)
        return obj
    except TypeError:
        return f"<Unserializable object: {obj.__class__.__name__}>"
    except Exception:
        return f"<Unserializable object (error during serialization): {obj.__class__.__name__}>"

# We can keep clean_for_serialization_recursive if needed for other parts of the Crew.kickoff result logging,
# but it's not strictly for LLM request/response anymore.
def clean_for_serialization_recursive(item):
    if isinstance(item, dict):
        return {k: clean_for_serialization_recursive(v) for k, v in item.items()}
    elif isinstance(item, list):
        return [clean_for_serialization_recursive(elem) for elem in item]
    else:
        try:
            json.dumps(item)
            return item
        except TypeError:
            return custom_json_serializer(item)
        except Exception as e:
            return f"<Unserializable object: {item.__class__.__name__} - Error: {e}>"

# Execute the crew with error handling
if __name__ == "__main__":
    logger.debug("Starting crew with query: Plot YTD stock gains for Tesla vs Nvidia")
    try:
        result = crew.kickoff(inputs={"query": "Plot YTD stock gains for Tesla vs Nvidia"})
        logger.debug(f"Result from crew: {json.dumps(result, indent=2, default=custom_json_serializer)}")
        
        final_output_raw = result.raw
        logger.info(f"Final crew output: {final_output_raw}")

        plot_path_regex = r"Plot 'stock_gains_plot.png' generated successfully at '(.+?)'"
        match = re.search(plot_path_regex, final_output_raw)
        if match:
            plot_path = match.group(1)
            logger.info(f"SUCCESS: Plot is expected at: {plot_path}")
            if os.path.exists(plot_path):
                logger.info(f"CONFIRMED: Plot file exists at: {plot_path}")
            else:
                logger.warning(f"WARNING: Plot file was reported as generated but not found at: {plot_path}")
        else:
            logger.warning("WARNING: No explicit plot generation confirmation or path found in final output. Check logs for errors.")


    except Exception as e:
        logger.error(f"Crew execution failed: {str(e)}")