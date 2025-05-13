import uvicorn
import argparse
import yaml
import os
import sys
import subprocess

def load_config(config_path="config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def check_ollama_running():
    """Check if Ollama is running"""
    try:
        import ollama
        ollama.list()
        return True
    except Exception:
        return False

def start_ollama():
    """Start Ollama if not running"""
    system = sys.platform
    
    try:
        if system.startswith('win'):
            print("Starting Ollama for Windows...")
            # Windows users would need to start Ollama manually
            print("Please start Ollama manually on Windows")
            return False
        else:
            print("Starting Ollama...")
            # Start Ollama as a background process
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
    except Exception as e:
        print(f"Error starting Ollama: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="ML-Ops Project for Legal Contract Suggestion Evaluation")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to config file")
    parser.add_argument("--setup", action="store_true", help="Run setup before starting server")
    args = parser.parse_args()
    
    # Run setup if requested
    if args.setup:
        print("Running setup...")
        setup_script = os.path.join(os.path.dirname(__file__), "setup.py")
        subprocess.check_call([sys.executable, setup_script])
    
    # Check if Ollama is running
    if not check_ollama_running():
        print("Ollama is not running. Attempting to start it...")
        if not start_ollama():
            print("Failed to start Ollama. Please make sure it's installed and start it manually.")
            print("You can install Ollama by running: python setup.py")
            sys.exit(1)
        
        # Wait a moment for Ollama to start
        import time
        print("Waiting for Ollama to start...")
        time.sleep(5)
    
    # Load configuration
    config = load_config(args.config)
    
    print(f"Starting API server at http://{config['api']['host']}:{config['api']['port']}")
    uvicorn.run(
        "src.api.app:app", 
        host=config["api"]["host"], 
        port=config["api"]["port"],
        reload=True
    )

if __name__ == "__main__":
    main()
