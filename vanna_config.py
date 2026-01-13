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
        # Increase timeout for model pulling (10 minutes = 600 seconds)
        config.setdefault("ollama_timeout", 600.0)
        
        # Initialize parent classes
        ChromaDB_VectorStore.__init__(self, config=config)
        
        # Initialize Ollama with error handling for model pulling
        try:
            Ollama.__init__(self, config=config)
        except Exception as e:
            # If model pulling fails (timeout, network issues, etc.), 
            # try to continue anyway - model might already be available
            error_msg = str(e)
            if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                print(f"⚠️  Warning: Model pull timed out during initialization.")
                print(f"   Model: {config.get('model')}")
                print(f"   The model will be pulled automatically on first use if needed.")
                print(f"   Continuing with initialization...")
                
                # Manually initialize Ollama without pulling model
                self._init_ollama_without_pull(config)
            else:
                # For other errors, re-raise
                raise
    
    def _init_ollama_without_pull(self, config):
        """Initialize Ollama client without pulling model."""
        import ollama
        from httpx import Timeout
        
        self.host = config.get("ollama_host", "http://ollama:11434")
        self.model = config["model"]
        if ":" not in self.model:
            self.model += ":latest"
        
        self.ollama_timeout = config.get("ollama_timeout", 600.0)
        self.ollama_client = ollama.Client(
            self.host, timeout=Timeout(self.ollama_timeout)
        )
        self.keep_alive = config.get("keep_alive", None)
        self.ollama_options = config.get("options", {})
        self.num_ctx = self.ollama_options.get("num_ctx", 2048)
        
        # Set log function (ChromaDB_VectorStore already has log from parent class)
        # If not available, use a simple print-based logger
        if not hasattr(self, 'log'):
            self.log = lambda x: print(f"[Vanna] {x}") if x else None


def get_default_config():
    """Returns default configuration for Vanna AI."""
    return {
        "ollama_host": "http://ollama:11434",
        "model": "qwen2.5-coder:7b",
        "path": "./chroma_db"
    }
