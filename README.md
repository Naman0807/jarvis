# JARVIS AI Assistant

JARVIS is a Python-based voice-controlled AI assistant inspired by the iconic assistant from Iron Man. This project aims to create a versatile assistant that can understand voice commands, control your computer, perform computer vision tasks, and interact with LLM APIs.

## Features

- **Voice Control**: Understand and respond to voice commands
- **Application Control**: Launch and close applications
- **Web Browsing**: Search the web and open websites
- **Mouse & Keyboard Control**: Move the cursor and type text
- **Computer Vision**: Detect objects and faces via webcam
- **Screen Analysis**: Read what's on your screen
- **LLM Integration**: Query multiple AI models with automatic fallback (Groq → Gemini → OpenAI)
- **Memory System**: Keep track of recent interactions and commands
- **Auto-learning**: Save and learn from unknown commands

## Getting Started

1. Install required packages:

   ```bash
   pip install -r requirements.txt
   ```

2. Set up API keys in `.env` file:

   ```
   GROQ_API_KEY="your_groq_key"
   GEMINI_API_KEY="your_gemini_key"
   OPENAI_API_KEY="your_openai_key"
   ```

3. Run JARVIS:
   ```bash
   python main.py
   ```

## Usage

Say "Hey JARVIS" to wake up the assistant, then speak your command:

- "Open Chrome"
- "Search for Python tutorials"
- "What time is it?"
- "Move mouse to 500 400"
- "Click"
- "What's on my screen?"
- "What do you see?" (webcam analysis)
- "Take a screenshot"
- "Press alt tab" (window switching)

## Project Structure

```
jarvis/
│
├── main.py               # Main entry point
├── config.py             # API keys and configurations
├── requirements.txt      # Project dependencies
├── brain/
│   ├── llm.py            # Handles LLM fallback
│   ├── tasks.py          # Task processing (app launching, etc.)
│   ├── vision.py         # Object detection & screen reading
│   ├── memory.py         # Memory and logging system
│   └── learn.py          # Autolearning & saving unknown tasks
├── utils/
│   ├── speech.py         # Speech recognition & TTS
│   ├── mouse_control.py  # Mouse and keyboard control
│   └── browser.py        # Web browsing and search
├── data/
│   ├── knowledge.json    # Stores new learned actions
│   └── jarvis_log.txt    # Activity and interaction logs
├── face/
│   └── detected_faces.jpg # Storage for facial recognition
└── README.md             # This file
```

## Requirements

- Python 3.8+
- Internet connection for LLM APIs and speech recognition
- Webcam for vision features
- Windows OS (some features are Windows-specific)
- Required Python packages (see requirements.txt):
  - pyttsx3 (Text-to-Speech)
  - SpeechRecognition (Voice recognition)
  - pyautogui (Screen control)
  - opencv-python (Computer vision)
  - pytesseract (Screen text recognition)
  - requests & selenium (Web interaction)
  - python-dotenv (Environment variables)
  - keyboard (Keyboard control)

## Configuration

JARVIS uses a `config.py` file for settings including:

- API keys for LLM services (loaded from .env)
- Voice settings (rate, volume)
- Application paths for quick launching
- Default responses and wake word settings

## Auto-Learning System

JARVIS can learn from unknown commands:

1. When an unknown command is received, it's logged to `knowledge.json`
2. JARVIS attempts to understand and implement it
3. Once learned, the solution is stored for future use

## Future Improvements

- Contextual awareness for better conversation flow
- Integration with home automation systems
- Calendar and email integration
- Custom skill plugins
- Enhanced vision capabilities with more advanced models
