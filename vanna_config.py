"""
Vanna AI Configuration Module
Contains the MyVanna class that combines ChromaDB and Ollama for RAG-based Text-to-SQL.
"""
from vanna.legacy.ollama import Ollama
from vanna.legacy.chromadb import ChromaDB_VectorStore


class MyVanna(ChromaDB_VectorStore, Ollama):
    """Custom Vanna class combining ChromaDB for vector storage and Ollama for LLM."""
    
    def __init__(self, config=None):
        if config is None:
            config = {}
        
        # Set default config values
        config.setdefault("ollama_host", "http://ollama:11434")
        config.setdefault("model", "qwen2.5-coder:7b")
        config.setdefault("path", "./chroma_db")
        
        # Initialize parent classes
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)


def get_default_config():
    """Returns default configuration for Vanna AI."""
    return {
        "ollama_host": "http://ollama:11434",
        "model": "qwen2.5-coder:7b",
        "path": "./chroma_db"
    }
