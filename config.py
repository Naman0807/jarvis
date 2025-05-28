import os
from dotenv import load_dotenv

# Configuration file for JARVIS AI Assistant
# API Keys for LLM services
# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Voice settings
VOICE_RATE = 180
VOICE_VOLUME = 2

# Application paths (customize based on your system)
APPLICATIONS = {
    "edge": "msedge",
    "brave": "brave",
    "notepad": "notepad",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "outlook": "outlook",
    "command prompt": "command prompt",
    "powershell": "powershell",
    "file explorer": "explorer",
    "calculator": "calc",
    "task manager": "taskmgr",
    "control panel": "control",
    "settings": "ms-settings:",
    "camera": "camera",
    "spotify": "spotify",
    "teams": "teams",
    "zoom": "zoom",
    "paint": "mspaint",
    "snipping tool": "snippingtool",
    "terminal": "wt"
}

# Web search settings
DEFAULT_SEARCH_ENGINE = "https://duckduckgo.com/?q="

# Vision settings
WEBCAM_INDEX = 0  # Default camera index
