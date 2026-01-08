from vanna.legacy.ollama import Ollama
from vanna.legacy.chromadb import ChromaDB_VectorStore
from vanna.legacy.flask import VannaFlaskApp


class MyVanna(ChromaDB_VectorStore, Ollama):
    """Custom Vanna class combining ChromaDB for vector storage and Ollama for LLM."""
    
    def __init__(self, config=None):
        if config is None:
            config = {}
        
        # Set default config values
        config.setdefault("ollama_host", "http://ollama:11434")
        config.setdefault("model", "llama3")
        config.setdefault("path", "./chroma_db")
        
        # Initialize parent classes
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)


# Create Vanna instance
config = {
    "ollama_host": "http://ollama:11434",
    "model": "llama3",
    "path": "./chroma_db"
}

vn = MyVanna(config=config)

# Add dummy training data (employees table DDL and example SQL)
employees_ddl = """
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    department VARCHAR(50),
    salary DECIMAL(10, 2),
    hire_date DATE
);
"""

example_sql = "SELECT name, department, salary FROM employees WHERE department = 'Engineering' ORDER BY salary DESC;"
example_question = "Show me all employees in the Engineering department sorted by salary"

# Train with DDL
vn.train(ddl=employees_ddl)

# Train with question-SQL pair
vn.train(question=example_question, sql=example_sql)

# Create and run Flask app
app = VannaFlaskApp(vn=vn, debug=False)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8084)
