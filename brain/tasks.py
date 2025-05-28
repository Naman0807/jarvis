"""
Task processing functionality for JARVIS - handling various commands
"""
import re
import os
import sys
import pyautogui
import subprocess
import webbrowser
import time
import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.speech import speak
from utils.mouse_control import move_mouse, click
from utils.browser import search_web, open_website
from brain.vision import read_screen, detect_object
from brain.llm import query_llm
from brain.memory import log_event
from config import APPLICATIONS

def process_command(command):
    """
    Process user's voice command
    
    Args:
        command (str): User's voice command
        
    Returns:
        str: Response to the command
    """
    # Log the user command
    log_event("USER_COMMAND", command)
    
    command = command.lower().strip()
    
    # General commands
    if command in ["hello", "hi", "hey"]:
        return "Hello! How can I help you today?"
    
    elif command in ["goodbye", "bye"]:
        return "Goodbye! Let me know if you need anything else."
        
    elif command in ["thank you", "thanks"]:
        return "You're welcome!"
    
    elif command in ["what's your name", "who are you"]:
        return "I'm JARVIS, your AI assistant."
    
    elif command in ["what time is it", "current time"]:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        return f"The current time is {current_time}"
    
    elif command in ["what day is it", "what's the date", "current date"]:
        current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
        return f"Today is {current_date}"
    
    # Application control
    elif re.match(r"open (.*)", command):
        app_name = re.match(r"open (.*)", command).group(1).strip()
        result = open_application(app_name)
        log_event("ACTION", f"Attempted to open application: {app_name}")
        return result
    
    elif re.match(r"close (.*)", command):
        app_name = re.match(r"close (.*)", command).group(1).strip()
        result = close_application(app_name)
        log_event("ACTION", f"Attempted to close application: {app_name}")
        return result
    
    # Web browsing
    elif re.match(r"search for (.*)", command):
        query = re.match(r"search for (.*)", command).group(1).strip()
        log_event("ACTION", f"Searching web for: {query}")
        return search_web(query)
        
    elif re.match(r"open website (.*)", command):
        website = re.match(r"open website (.*)", command).group(1).strip()
        log_event("ACTION", f"Opening website: {website}")
        return open_website(website)
    
    # Mouse control
    elif re.match(r"move mouse to (\d+) (\d+)", command):
        match = re.match(r"move mouse to (\d+) (\d+)", command)
        x, y = int(match.group(1)), int(match.group(2))
        if move_mouse(x, y):
            log_event("ACTION", f"Moved mouse to coordinates ({x}, {y})")
            return f"Moved mouse to coordinates ({x}, {y})"
        else:
            log_event("ERROR", f"Failed to move mouse to ({x}, {y})")
            return "Failed to move mouse"
    
    elif command == "click":
        click()
        log_event("ACTION", "Performed mouse click")
        return "Clicked"
        
    elif command == "double click":
        click(clicks=2)
        log_event("ACTION", "Performed mouse double-click")
        return "Double clicked"
        
    elif command == "right click":
        click(button='right')
        log_event("ACTION", "Performed mouse right-click")
        return "Right clicked"

    
    # Vision capabilities
    elif command in ["what's on my screen", "read screen"]:
        text = read_screen()
        log_event("ACTION", "Screen analyzed. Text extracted.")
        log_event("VISION_DATA", f"Screen text: {text[:100]}..." if len(text) > 100 else f"Screen text: {text}")
        return f"I see the following text on your screen: {text}"
        
    elif command in ["what's in front of me", "detect object"]:
        result = detect_object()
        log_event("ACTION", "Object detection performed")
        return result
    
    # Type text
    elif re.match(r"type (.*)", command):
        text = re.match(r"type (.*)", command).group(1).strip()
        pyautogui.write(text)
        log_event("ACTION", f"Typed text: {text[:20]}..." if len(text) > 20 else f"Typed text: {text}")
        return f"Typed: {text}"
    
    # System commands
    elif command in ["screenshot", "take screenshot"]:
        pyautogui.screenshot("ss/jarvis_screenshot.png")
        log_event("ACTION", "Screenshot taken and saved to ss/jarvis_screenshot.png")
        return "Screenshot taken and saved"
    
    elif command in ["system info", "about system"]:
        import platform
        system_info = f"OS: {platform.system()} {platform.version()}\n"
        system_info += f"Machine: {platform.machine()}\n"
        system_info += f"Processor: {platform.processor()}"
        log_event("ACTION", "Retrieved system information")
        return system_info
        
    # Memory query commands
    elif re.match(r"what did I say (\d+) minutes ago", command):
        from brain.memory import get_events_by_timeframe
        minutes = int(re.match(r"what did I say (\d+) minutes ago", command).group(1))
        past_events = get_events_by_timeframe(minutes)
        log_event("ACTION", f"Retrieved memory from past {minutes} minutes")
        
        if not past_events:
            return f"I don't have any records from {minutes} minutes ago."
        
        # Extract only USER_COMMAND events
        user_commands = []
        for line in past_events.split('\n'):
            if "(USER_COMMAND)" in line:
                user_commands.append(line)
                
        if user_commands:
            return f"In the past {minutes} minutes, you said:\n" + "\n".join(user_commands)
        else:
            return f"I don't have any record of you speaking in the past {minutes} minutes."
            
    # Fall back to LLM for unknown commands   
    else:
        try:
            # We'll try to use the autolearning feature in learn.py first
            from brain.learn import handle_unknown_command
            log_event("ACTION", f"Attempting to handle unknown command via learning module: {command}")
            result = handle_unknown_command(command)
            if result:
                log_event("ACTION", "Successfully handled via learning module")
                return result
        except Exception as e:
            log_event("ERROR", f"Error in learning module: {str(e)}")
            print(f"Error handling unknown command: {e}")
        
        # If no specialized handler, fall back to LLM
        log_event("ACTION", "Falling back to LLM for response")
        return query_llm(command)

def open_application(app_name):
    """
    Open an application
    
    Args:
        app_name (str): Name of the application to open
        
    Returns:
        str: Response message
    """
    app_name = app_name.lower()
    
    # Check if app is in predefined list (from config)
    try:
        if app_name in APPLICATIONS:
            specific_command = APPLICATIONS[app_name]
            subprocess.Popen(specific_command)
            return f"Opening {app_name}"
    except Exception as e:
        log_event("ERROR", f"Error opening predefined app {app_name}: {str(e)}")
    
    # Try to use direct command if not in dict
    try:
        pyautogui.press('win')
        time.sleep(0.5)
        pyautogui.write(app_name)
        time.sleep(0.5)
        pyautogui.press('enter')
        return f"Attempting to open {app_name}"
    except Exception as e:
        log_event("ERROR", f"Failed to open {app_name}: {str(e)}")
        return f"Failed to open {app_name}: {e}"

def close_application(app_name):
    """
    Close an application (tries to focus and then use Alt+F4)
    
    Args:
        app_name (str): Name of the application to close
        
    Returns:
        str: Response message
    """
    try:       
        # Then try to close it with Alt+F4
        pyautogui.hotkey('alt', 'f4')
        return f"Attempting to close {app_name}"
    except Exception as e:
        log_event("ERROR", f"Failed to close {app_name}: {str(e)}")
        return f"Failed to close {app_name}: {e}"
