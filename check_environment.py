
import requests
import json
import asyncio
from vanna import Agent
from vanna.integrations.ollama import OllamaLlmService

# ANSI escape codes for colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_status(message, status):
    """Prints a status message with color."""
    if status == "success":
        print(f"{GREEN}✓ {message}{RESET}")
    elif status == "error":
        print(f"{RED}✗ {message}{RESET}")
    elif status == "warning":
        print(f"{YELLOW}! {message}{RESET}")

def check_ollama_server():
    """Checks if the Ollama server is running."""
    print("Step 1: Checking Ollama server...")
    try:
        response = requests.get("http://localhost:11434")
        response.raise_for_status()
        print_status("Ollama server is running.", "success")
        return True
    except requests.exceptions.RequestException as e:
        print_status(f"Ollama server is not accessible at http://localhost:11434.", "error")
        print(f"  Error details: {e}")
        return False

def check_ollama_model(model_name='llama3'):
    """Checks if the specified model is available in Ollama."""
    print(f"Step 2: Checking for model '{model_name}'...")
    try:
        response = requests.get("http://localhost:11434/api/tags")
        response.raise_for_status()
        models = response.json().get('models', [])

        for model in models:
            if model['name'].split(':')[0] == model_name:
                print_status(f"Model '{model_name}' is available.", "success")
                return True

        print_status(f"Model '{model_name}' not found.", "error")
        print(f"  Available models: {[m['name'] for m in models]}")
        print(f"  You can pull the model with: ollama pull {model_name}")
        return False
    except requests.exceptions.RequestException as e:
        print_status("Could not query Ollama for models.", "error")
        print(f"  Error details: {e}")
        return False

async def test_vanna_connection(model_name='llama3'):
    """Tests the connection to Vanna with a simple query."""
    print("Step 3: Testing Vanna connection...")
    try:
        llm = OllamaLlmService(model=model_name)
        agent = Agent(llm_service=llm)

        response_generator = await agent.ask(question="Hello")

        full_response = ""
        async for chunk in response_generator:
            if chunk.content:
                full_response += chunk.content

        if full_response and full_response.strip():
            print_status("Vanna connection successful.", "success")
            print(f"  Ollama's response: '{full_response.strip()}'")
            return True
        else:
            print_status("Vanna received an empty or invalid response.", "error")
            return False

    except Exception as e:
        print_status("Failed to connect to Vanna.", "error")
        print(f"  Error details: {e}")
        return False

if __name__ == "__main__":
    print("="*50)
    print("Vanna & Ollama Environment Check")
    print("="*50)

    server_ok = check_ollama_server()
    model_ok = False
    vanna_ok = False

    if server_ok:
        model_ok = check_ollama_model()
    else:
        print_status("Skipping model check due to server issue.", "warning")

    if model_ok:
        # Run the async function
        vanna_ok = asyncio.run(test_vanna_connection())
    else:
        print_status("Skipping Vanna connection test due to model issue.", "warning")

    print("="*50)
    print("Check Summary:")
    if server_ok and model_ok and vanna_ok:
        print_status("All checks passed! Your environment is ready.", "success")
    else:
        print_status("Some checks failed. Please review the output above.", "error")
    print("="*50)
