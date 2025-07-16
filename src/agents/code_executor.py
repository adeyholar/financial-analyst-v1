# D:\AI\Gits\financial-analyst-v1\src/agents/code_executor.py
from pydantic import BaseModel, Field
from pydantic.config import ConfigDict  # Added import
from crewai import Agent
from crewai_tools import CodeInterpreterTool

class ExecutionOutput(BaseModel):
    result: str = Field(..., description="Result of code execution")
    model_config = ConfigDict(json_schema_extra={"required": ["result"]})

class CodeExecutorAgent(Agent):
    def __init__(self, llm):
        try:
            code_interpreter = CodeInterpreterTool()
        except Exception as e:
            print(f"Warning: CodeInterpreterTool initialization failed: {e}. Falling back to local execution.")
            code_interpreter = None
        super().__init__(
            llm=llm,
            role="Senior Code Execution Expert",
            goal="Review and execute code to generate outputs",
            backstory="An expert in reviewing and executing Python code in a secure environment.",
            tools=[code_interpreter] if code_interpreter else []
        )

    def execute(self, code: str) -> ExecutionOutput:
        if self.tools and len(self.tools) > 0:
            try:
                result = self.tools[0].run(code)
                return ExecutionOutput(result=f"Plot generated: {result}")
            except AttributeError:
                print("Warning: Tool method 'run' not found or failed. Falling back to local execution.")
            except Exception as e:
                print(f"Warning: Tool execution failed: {e}. Falling back to local execution.")
        
        try:
            local_namespace = {
                "yf": __import__("yfinance"),
                "plt": __import__("matplotlib.pyplot"),
                "__builtins__": {}  # Restrict builtins for security
            }
            exec(code, local_namespace)
            return ExecutionOutput(result="Plot generated successfully (local execution)")
        except Exception as e:
            return ExecutionOutput(result=f"Execution failed: {str(e)}")