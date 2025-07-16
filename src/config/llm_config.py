# D:\AI\Gits\financial-analyst-v1\src\config\llm_config.py
from crewai import LLM

# Configure the local LLM with Ollama and DeepSeek-R1
llm = LLM(model="ollama/deepseek-r1", base_url="http://localhost:11434")

# Export the LLM instance
__all__ = ['llm']