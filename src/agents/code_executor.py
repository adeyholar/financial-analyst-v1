# D:\AI\Gits\financial-analyst-v1\src/agents/code_executor.py
from pydantic import BaseModel, Field
from pydantic.config import ConfigDict
from crewai import Agent
from crewai_tools import CodeInterpreterTool
import subprocess
import os
import sys
import logging
from typing import Optional, List # NEW: Import List for explicit type hinting

logger = logging.getLogger(__name__)

class ExecutionOutput(BaseModel):
    result: str = Field(..., description="Result of code execution")
    model_config = ConfigDict(json_schema_extra={"required": ["result"]})

class CodeExecutorAgent(Agent):
    # Ensure code_interpreter_tool is a Pydantic Field
    code_interpreter_tool: Optional[CodeInterpreterTool] = Field(None, exclude=True)
    # Pylance might infer 'tools' can be None if its base class has it as Optional.
    # To be explicit, though crewai sets it as a list.
    # This explicit type hint for `tools` is not strictly necessary for runtime,
    # but can help Pylance understand the type better.
    # tools: List[any] # No, this can conflict with Agent's internal type definition.

    def __init__(self, llm):
        super().__init__(
            llm=llm,
            role="Senior Code Execution Expert",
            goal="Review and execute code to generate outputs",
            backstory="An expert in reviewing and executing Python code in a secure environment.",
            tools=[], # Initialize empty, will be updated below
            allow_delegation=False
        )
        
        try:
            initialized_tool = CodeInterpreterTool()
            self.code_interpreter_tool = initialized_tool # Assign to the Pydantic field

            # --- FIX FOR PYLANCE WARNING ---
            # Ensure self.tools is treated as a list.
            # While `super().__init__` typically initializes it as a list,
            # Pylance might be overzealous. An explicit check or cast can resolve this.
            if self.tools is None: # This check is defensive, crewai usually ensures it's a list.
                self.tools = []
            self.tools.append(initialized_tool) # Now Pylance knows self.tools is not None here
            # --- END FIX ---

            logger.info("CodeInterpreterTool initialized successfully.")
        except Exception as e:
            logger.warning(f"CodeInterpreterTool initialization failed: {e}. Falling back to local execution.")
            self.code_interpreter_tool = None
            # If the tool failed to initialize, it should not be added to self.tools.
            # self.tools remains empty if the tool failed.


    def execute_code(self, code: str) -> ExecutionOutput:
        script_path = "temp_generated_plot_script.py"
        plot_output_dir = "plots"
        plot_filename = "stock_gains_plot.png"
        full_plot_path = os.path.join(plot_output_dir, plot_filename)

        if os.path.exists(full_plot_path):
            os.remove(full_plot_path)
            logger.debug(f"Removed old plot file: {full_plot_path}")

        # Use the initialized tool if available and functional
        # Check `self.code_interpreter_tool` directly, which is the Pydantic field
        # and also confirm it's actually in `self.tools` if the agent framework uses `self.tools`
        if self.code_interpreter_tool and (self.code_interpreter_tool in self.tools if self.tools is not None else False):
            try:
                result_str = self.code_interpreter_tool.run(code)
                logger.debug(f"CodeInterpreterTool Raw Output: {result_str}")

                if "Plot saved successfully to:" in result_str:
                    return ExecutionOutput(result=f"CodeInterpreterTool executed code. {result_str}")
                else:
                    if os.path.exists(full_plot_path):
                        return ExecutionOutput(result=f"CodeInterpreterTool executed code successfully. Plot generated at {full_plot_path}.")
                    else:
                        return ExecutionOutput(result=f"CodeInterpreterTool executed code, but plot not explicitly confirmed or found locally. Tool Output: {result_str[:500]}...")

            except Exception as e:
                logger.warning(f"CodeInterpreterTool execution failed: {e}. Falling back to local execution.")
        
        logger.info("Attempting local code execution...")
        try:
            with open(script_path, "w") as f:
                f.write(code)

            process = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.debug(f"Local script stdout:\n{process.stdout}")
            if process.stderr:
                logger.warning(f"Local script stderr:\n{process.stderr}")

            if os.path.exists(full_plot_path):
                return ExecutionOutput(result=f"Plot '{plot_filename}' generated successfully at '{full_plot_path}'. Script output: {process.stdout.strip()}")
            else:
                return ExecutionOutput(result=f"Code executed locally, but plot file '{plot_filename}' not found at '{full_plot_path}'. " \
                                       f"Script output: {process.stdout.strip()}\nErrors: {process.stderr.strip()}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Error executing script locally (Exit Code: {e.returncode}): {e}")
            logger.error(f"Script stdout: \n{e.stdout}")
            logger.error(f"Script stderr: \n{e.stderr}")
            return ExecutionOutput(result=f"Local execution failed. Subprocess error: {e.stderr.strip()} (Exit Code: {e.returncode})")
        except Exception as e:
            logger.error(f"An unexpected error occurred during local code execution: {e}")
            return ExecutionOutput(result=f"An unexpected error occurred during local code execution: {e}")
        finally:
            if os.path.exists(script_path):
                os.remove(script_path)
                logger.debug(f"Removed temporary script file: {script_path}")