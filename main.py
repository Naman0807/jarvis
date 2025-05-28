"""
JARVIS - AI Personal Assistant
Main entry point for the JARVIS application
"""
import os
import sys
import time
import threading
import json

# Add the project directory to the path to enable proper imports
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Import components
from utils.speech import speak, listen, listen_for_wake_word
from brain.tasks import process_command
from brain.learn import ensure_knowledge_file
from brain.llm import query_llm
from brain.vision import detect_faces
from brain.memory import log_event

# Create the data directory and knowledge file if they don't exist
os.makedirs(os.path.join(project_dir, "data"), exist_ok=True)
ensure_knowledge_file()

# Ensure the log file exists
log_file = os.path.join(project_dir, "data", "jarvis_log.txt")
if not os.path.exists(log_file):
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("")  # Create empty log file

# Constants
WAKE_WORD = ["hey jarvis","hello jarvis","hey jar"]
STANDBY_PHRASES = ["stop listening", "go to sleep", "standby", "stand by", "stop"]
EXIT_PHRASES = ["goodbye", "bye", "exit", "quit", "shutdown"]

def display_banner():
    """Display a welcome banner"""
    banner = """
    ╔════════════════════════════════════════════════╗
    ║                                                ║
    ║       J A R V I S   A I   A S S I S T A N T    ║
    ║                                                ║
    ║                      v1.0                      ║
    ║                                                ║
    ╚════════════════════════════════════════════════╝
    """
    print(banner)

def initialize():
    """Initialize JARVIS"""
    display_banner()
    
    # Log system startup
    log_event("SYSTEM", "JARVIS AI system initializing...")
    
    speak("JARVIS AI system initializing...")
    
    # Check if required API keys are set
    try:
        from config import GROQ_API_KEY, GEMINI_API_KEY, OPENAI_API_KEY
        api_status = []
        
        if GROQ_API_KEY and GROQ_API_KEY != "your_groq_key":
            api_status.append("Groq")
        if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_key":
            api_status.append("Gemini")
        if OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_key":
            api_status.append("OpenAI")
            
        if api_status:
            print(f"Connected LLM services: {', '.join(api_status)}")
        else:
            print("Warning: No LLM API keys configured. Voice commands will work but advanced AI capabilities will be limited.")
    except ImportError:
        print("Warning: Config file not found or incomplete.")
    
    # Perform face detection to ensure camera is working
    face_result = detect_faces()
    print(face_result)
    
    # Start the main system
    speak("JARVIS is now online and ready to assist.")
    print("\nJARVIS is in standby mode. Say 'Hey JARVIS' to wake me up.")

def wake_word_listening_mode():
    """Main loop that waits for wake word, then processes commands until told to standby or exit"""
    running = True
    
    # Log start of wake word mode
    log_event("SYSTEM", "Starting wake word listening mode")
    
    while running:
        # Wait for the wake word
        print("\nIn standby mode. Waiting for wake word...")
        log_event("SYSTEM", "In standby mode waiting for wake word")
        wake_detected = listen_for_wake_word(WAKE_WORD)
        if wake_detected:
            log_event("SYSTEM", "Wake word detected, entering active listening mode")
            speak("Yes, I'm listening")
            print("Active listening mode. Say 'stop listening' to return to standby or 'goodbye' to exit.")
            
            # Enter active listening loop
            active = True
            while active:
                command = listen()
                
                if not command:
                    continue
                
                # Check for standby phrases
                if any(phrase in command.lower() for phrase in STANDBY_PHRASES):
                    log_event("SYSTEM", "Returning to standby mode")
                    speak("Going to standby mode")
                    active = False
                    continue
                # Check for exit phrases
                elif any(phrase in command.lower() for phrase in EXIT_PHRASES):
                    log_event("SYSTEM", "Received exit command, shutting down JARVIS")
                    speak("Shutting down JARVIS. Goodbye.")
                    active = False
                    running = False
                    continue
                
                # Process regular commands
                response = process_command(command)
                speak(response)

def continuous_listening_mode():
    """Legacy continuous listening mode without wake word"""
    # Log mode start
    log_event("SYSTEM", "Starting continuous listening mode")
    
    while True:
        command = listen()
        
        if not command:
            continue
            
        if command.lower() in ["exit", "quit", "stop", "shutdown"]:
            log_event("SYSTEM", "Shutting down JARVIS")
            speak("Shutting down JARVIS. Goodbye.")
            break
            
        response = process_command(command)
        speak(response)

def query_mode():
    """Interactive mode for testing and debugging"""
    print("\n=== JARVIS Interactive Mode ===")
    print("Type your commands or 'exit' to quit")
    
    # Log mode start
    log_event("SYSTEM", "Starting interactive query mode")
    
    while True:
        command = input("\nCommand > ")
        
        # Log typed command explicitly since we're not using listen()
        log_event("USER_INPUT", command)
        
        if command.lower() in ["exit", "quit", "stop", "shutdown"]:
            log_event("SYSTEM", "Shutting down JARVIS")
            speak("Shutting down JARVIS. Goodbye.")
            break
            
        response = process_command(command)
        print(f"JARVIS: {response}")
        speak(response)

if __name__ == "__main__":
    initialize()
    
    wake_word_listening_mode()
