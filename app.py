"""
Vanna AI Flask Application
Main entry point for the Flask web application.
Automatically initializes database if it doesn't exist.
"""
import os
import subprocess
import sys
import time
import requests
from vanna.legacy.flask import VannaFlaskApp
from vanna_config import MyVanna, get_default_config


def wait_for_ollama(ollama_host="http://ollama:11434", max_retries=30, retry_delay=2):
    """Wait for Ollama service to be ready."""
    print(f"⏳ Waiting for Ollama service at {ollama_host}...")
    for i in range(max_retries):
        try:
            response = requests.get(f"{ollama_host}/api/tags", timeout=5)
            if response.status_code == 200:
                print(f"✅ Ollama service is ready!")
                return True
        except (requests.exceptions.RequestException, requests.exceptions.ConnectionError):
            if i < max_retries - 1:
                print(f"   Retry {i+1}/{max_retries}...")
                time.sleep(retry_delay)
            else:
                print(f"⚠️  Ollama service not ready after {max_retries} retries, continuing anyway...")
                return False
    return False


def initialize_database_if_needed(db_path):
    """Initialize database if it doesn't exist."""
    if not os.path.exists(db_path):
        print("=" * 60)
        print("⚠️  Database not found. Initializing database...")
        print("=" * 60)
        try:
            # Run init_db.py
            result = subprocess.run(
                [sys.executable, "/app/init_db.py"],
                check=True,
                capture_output=True,
                text=True
            )
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            print("✅ Database initialization completed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error initializing database: {e}")
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
            raise
        except Exception as e:
            print(f"❌ Unexpected error during database initialization: {e}")
            raise


# Wait for Ollama service to be ready
ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
wait_for_ollama(ollama_host)

# Initialize Vanna instance
print("🔧 Initializing Vanna AI instance...")
try:
    config = get_default_config()
    print(f"   Config: model={config.get('model')}, host={config.get('ollama_host')}")
    vn = MyVanna(config=config)
    print("✅ Vanna AI instance initialized successfully")
except Exception as e:
    print(f"❌ Error initializing Vanna AI: {e}")
    import traceback
    traceback.print_exc()
    raise

# Connect to SQLite database (auto-initialize if needed)
db_path = os.path.join("/app/db_data", "employees.db")
try:
    # Auto-initialize database if it doesn't exist
    initialize_database_if_needed(db_path)
    
    # Connect to database
    vn.connect_to_sqlite(db_path)
    print(f"✅ Connected to SQLite database at {db_path}")
except Exception as e:
    print(f"❌ Error connecting to database: {e}")
    raise

# Create and run Flask app
print("🚀 Starting Flask application...")
try:
    app = VannaFlaskApp(vn=vn, debug=True)
    print("✅ Flask application created successfully")
    print("=" * 60)
    print("🌐 Vanna AI is ready! Access the web UI at http://localhost:8084")
    print("=" * 60)
except Exception as e:
    print(f"❌ Error creating Flask app: {e}")
    import traceback
    traceback.print_exc()
    raise

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8084)
