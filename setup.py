import platform, subprocess, sys, time
from shutil import which 

def load_config():
    import yaml
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

def install_dependencies():
    """Install Python dependencies from requirements.txt"""
    print("Installing Python dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("Dependencies installed successfully.")

def is_ollama_installed():
    """Check if Ollama is installed"""
    return which("ollama") is not None

def is_ollama_running():
    """Try to get the version to confirm Ollama is responsive"""
    try:
        subprocess.check_call(["ollama", "version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False

def start_ollama():
    """Start Ollama based on the platform"""
    system = platform.system().lower()

    if system == "linux":
        print("Starting Ollama in serve mode for Linux...")
        subprocess.Popen(["ollama", "serve"])
    elif system == "darwin":
        print("Starting Ollama as a background service on macOS...")
        subprocess.call(["brew", "services", "start", "ollama"])
    else:
        print("Please start the Ollama app manually.")

    # Give some time for the service to start
    time.sleep(5)

def install_ollama():
    """Install Ollama based on the platform"""
    system = platform.system().lower()
    print(f"Detected system: {system}")

    if system == "linux":
        print("Installing Ollama for Linux...")
        subprocess.check_call("curl -fsSL https://ollama.com/install.sh | sh", shell=True)

    elif system == "darwin":
        print("Installing Ollama on macOS via Homebrew...")
        subprocess.check_call(["brew", "install", "--cask", "ollama"])

    elif system == "windows":
        print("For Windows, please install Ollama manually from https://ollama.com/download")
        sys.exit(1)

    else:
        print(f"Unsupported platform: {system}")
        sys.exit(1)

    print("Ollama installed successfully.")
    start_ollama()

def pull_model(model_name):
    """Pull the specified model using Ollama"""
    print(f"Pulling model: {model_name}...")
    try:
        subprocess.check_call(["ollama", "pull", model_name])
        print(f"Model {model_name} pulled successfully.")
    except subprocess.CalledProcessError:
        print(f"Failed to pull model {model_name}. Make sure Ollama is running.")
        sys.exit(1)

def main():
    install_dependencies()

    if not is_ollama_installed():
        print("Ollama is not installed. Installing...")
        install_ollama()
    elif not is_ollama_running():
        print("Ollama is installed but not running. Starting now...")
        start_ollama()
    else:
        print("Ollama is already installed and running.")
    
    model_name = load_config().get("model", {}).get("name", "phi")
    pull_model(model_name)

    print("\nSetup completed successfully!")
    print("To start the application, run: python main.py")

if __name__ == "__main__":
    main()
