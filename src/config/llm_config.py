# src/config/llm_config.py
import os
from langchain_community.chat_models import ChatOllama
from src.callbacks.llm_logging_callback import LLMLoggingCallbackHandler

try:
    llm_callbacks = [LLMLoggingCallbackHandler()] # This is correctly a list of BaseCallbackHandler subclasses

    llm = ChatOllama(
        model="llama3:8b",
        base_url="http://localhost:11434",
        temperature=0.7,
        callbacks=llm_callbacks # This should now be seen as compatible by Pylance
    )
    print("Successfully configured Ollama LLM using LangChain's ChatOllama with custom logging callback.")

except Exception as e:
    print(f"Error initializing Ollama ChatOllama: {e}")
    print("Please ensure Ollama server is running and 'llama3:8b' model is pulled.")
    print("Run: ollama run llama3:8b")
    llm = None

if llm is None:
    raise ValueError("LLM is not configured. Please ensure Ollama is running and the model is available.")

__all__ = ['llm']