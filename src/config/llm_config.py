# D:\AI\Gits\financial-analyst-v1\src\config\llm_config.py
from crewai import LLM

# Configure the local LLM with Ollama and llama3:8b, using chat endpoint
llm = LLM(
    model="ollama/llama3:8b",
    base_url="http://localhost:11434",
    options={
        "stream": False,
        "endpoint": "/api/chat"  # Explicitly use chat endpoint
    }
)

# Export the LLM instance
__all__ = ['llm']