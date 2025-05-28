"""
Mouse and keyboard control functionality for JARVIS
"""
import pyautogui
import keyboard
import re
import time

# Configure PyAutoGUI to have a small pause between actions for stability
pyautogui.PAUSE = 0.1
# Fail-safe feature: Moving mouse to corner will raise exception
pyautogui.FAILSAFE = True

def move_mouse(x, y):
    """
    Move mouse to specific coordinates
    
    Args:
        x (int): X coordinate
        y (int): Y coordinate
    """
    try:
        # Log this mouse action
        try:
            from brain.memory import log_event
            log_event("MOUSE_ACTION", f"Moving mouse to coordinates ({x}, {y})")
        except ImportError:
            pass
            
        x, y = int(x), int(y)
        screen_width, screen_height = pyautogui.size()
        
        # Ensure coordinates are within screen bounds
        if 0 <= x <= screen_width and 0 <= y <= screen_height:
            pyautogui.moveTo(x, y, duration=0.5)
            return True
        else:
            # Log error
            try:
                from brain.memory import log_event
                log_event("ERROR", f"Coordinates ({x}, {y}) are outside screen bounds ({screen_width}x{screen_height})")
            except ImportError:
                pass
                
            print(f"Coordinates ({x}, {y}) are outside screen bounds ({screen_width}x{screen_height})")
            return False
    except ValueError:
        # Log error
        try:
            from brain.memory import log_event
            log_event("ERROR", f"Invalid coordinates: {x}, {y}")
        except ImportError:
            pass
            
        print(f"Invalid coordinates: {x}, {y}")
        return False

def click(button='left', clicks=1):
    """
    Perform mouse click
    
    Args:
        button (str): Button to click ('left', 'right', or 'middle')
        clicks (int): Number of clicks
    """
    # Log this mouse action
    try:
        from brain.memory import log_event
        if clicks == 1:
            log_event("MOUSE_ACTION", f"Performing {button} mouse click")
        else:
            log_event("MOUSE_ACTION", f"Performing {button} mouse click ({clicks} times)")
    except ImportError:
        pass
        
    pyautogui.click(button=button, clicks=clicks)
    return True

def double_click():
    """Perform double-click"""
    return click(clicks=2)

def right_click():
    """Perform right-click"""
    return click(button='right')

def drag_to(x, y):
    """
    Drag mouse from current position to coordinates
    
    Args:
        x (int): X coordinate
        y (int): Y coordinate
    """
    try:
        x, y = int(x), int(y)
        pyautogui.dragTo(x, y, duration=0.5)
        return True
    except ValueError:
        print(f"Invalid coordinates: {x}, {y}")
        return False

def type_text(text):
    """
    Type text using keyboard
    
    Args:
        text (str): Text to type
    """
    pyautogui.write(text, interval=0.05)
    return True

def press_key(key):
    """
    Press a specific key
    
    Args:
        key (str): Key to press
    """
    try:
        pyautogui.press(key)
        return True
    except Exception as e:
        print(f"Error pressing key {key}: {e}")
        return False

def press_hotkey(*keys):
    """
    Press a hotkey combination
    
    Args:
        *keys: Keys to press simultaneously
    """
    try:
        pyautogui.hotkey(*keys)
        return True
    except Exception as e:
        print(f"Error pressing hotkey {keys}: {e}")
        return False

def scroll(amount):
    """
    Scroll up or down
    
    Args:
        amount (int): Amount to scroll (positive for up, negative for down)
    """
    try:
        pyautogui.scroll(amount)
        return True
    except Exception as e:
        print(f"Error scrolling: {e}")
        return False

def get_mouse_position():
    """
    Get current mouse position
    
    Returns:
        tuple: (x, y) coordinates of mouse
    """
    return pyautogui.position()

def parse_coordinate_command(command):
    """
    Parse a command for coordinates
    
    Args:
        command (str): Command containing coordinates
    
    Returns:
        tuple: (x, y) coordinates or (None, None) if parsing fails
    """
    pattern = r'(\d+)\s*,?\s*(\d+)'
    match = re.search(pattern, command)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None

def handle_press_alter_tab():
    """
    Simulates pressing Alt+Tab to switch between windows
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Log this keyboard action
        try:
            from brain.memory import log_event
            log_event("KEYBOARD_ACTION", "Executing Alt+Tab")
        except ImportError:
            pass
            
        pyautogui.keyDown('alt')
        pyautogui.press('tab')
        pyautogui.keyUp('alt')
        return True
    except Exception as e:
        print(f"Error executing Alt+Tab: {e}")
        try:
            from brain.memory import log_event
            log_event("ERROR", f"Failed to execute Alt+Tab: {str(e)}")
        except ImportError:
            pass
        return False
