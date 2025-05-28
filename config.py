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
VOICE_VOLUME = 2.0

# Application paths (customize based on your system)
APPLICATIONS = {
    # Browsers
    "chrome": "chrome",
    "edge": "msedge",
    "firefox": "firefox",
    "brave": "brave",
    
    # Office applications
    "notepad": "notepad",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "outlook": "outlook",
    
    # System tools
    "cmd": "cmd",
    "powershell": "powershell",
    "file explorer": "explorer",
    "calculator": "calc",
    "task manager": "taskmgr",
    "control panel": "control",
    "settings": "ms-settings:",
    
    # Media
    "camera": "camera",
    "media player": "wmplayer",
    "spotify": "spotify",
    
    # Communication
    "teams": "teams",
    "zoom": "zoom",
    "discord": "discord",
    "skype": "skype",
    
    # Utilities
    "paint": "mspaint",
    "snipping tool": "snippingtool",
    "terminal": "wt"
}

# Web search settings
DEFAULT_SEARCH_ENGINE = "https://duckduckgo.com/?q="

# Vision settings
WEBCAM_INDEX = 0  # Default camera index
