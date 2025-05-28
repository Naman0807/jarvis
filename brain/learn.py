"""
Autolearning functionality for JARVIS
Allows JARVIS to learn from unknown tasks
"""
import json
import os
import sys
import datetime
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from brain.llm import query_llm

# Path to knowledge database
KNOWLEDGE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "knowledge.json")

def ensure_knowledge_file():
    """
    Ensure the knowledge JSON file exists
    
    Returns:
        bool: True if file created or exists, False if error
    """
    try:
        os.makedirs(os.path.dirname(KNOWLEDGE_PATH), exist_ok=True)
        if not os.path.exists(KNOWLEDGE_PATH):
            with open(KNOWLEDGE_PATH, 'w') as f:
                json.dump({}, f, indent=4)
        return True
    except Exception as e:
        print(f"Error creating knowledge file: {e}")
        return False

def save_unknown(task, status="unknown"):
    """
    Save an unknown task to the knowledge database
    
    Args:
        task (str): The unknown task
        status (str): Status of task (unknown, learning, learned)
    
    Returns:
        bool: True if successful, False otherwise
    """
    ensure_knowledge_file()
    
    # Log this learning action
    try:
        from brain.memory import log_event
        log_event("LEARNING", f"Saving unknown task to knowledge base: '{task}' with status: {status}")
    except ImportError:
        pass
    
    try:
        with open(KNOWLEDGE_PATH, 'r+') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
            
            if task not in data:
                data[task] = {
                    "status": status,
                    "timestamp": str(datetime.datetime.now()),
                    "attempts": 0,
                    "solution": None
                }
            else:
                data[task]["attempts"] += 1
            
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving unknown task: {e}")
        return False

def get_solution(task):
    """
    Get solution for a task if available
    
    Args:
        task (str): The task to get solution for
    
    Returns:
        str: Solution or None
    """
    ensure_knowledge_file()
    
    try:
        with open(KNOWLEDGE_PATH, 'r') as f:
            data = json.load(f)
            if task in data and data[task]["solution"]:
                return data[task]["solution"]
    except Exception as e:
        print(f"Error getting solution: {e}")
    
    return None

def find_similar_task(task):
    """
    Find a similar task in the knowledge base
    
    Args:
        task (str): The task to find similar matches for
    
    Returns:
        str: Most similar task or None
    """
    ensure_knowledge_file()
    
    try:
        with open(KNOWLEDGE_PATH, 'r') as f:
            data = json.load(f)
            # Very basic similarity: check if any known task is a subset
            for known_task in data.keys():
                if known_task in task or task in known_task:
                    return known_task
    except Exception as e:
        print(f"Error finding similar task: {e}")
    
    return None

def learn_from_llm(task):
    """
    Learn how to do a task by asking the LLM
    
    Args:
        task (str): The task to learn
    
    Returns:
        str: Solution from LLM
    """
    prompt = f"""I need to learn how to handle this command in an AI assistant: "{task}"
    
    Please give me step-by-step instructions on how to implement code that can handle this command.
    Keep the answer concise and focused on the implementation details."""
    
    try:
        solution = query_llm(prompt)
        if solution:
            # Save the learned solution
            ensure_knowledge_file()
            with open(KNOWLEDGE_PATH, 'r+') as f:
                data = json.load(f)
                if task in data:
                    data[task]["status"] = "learned"
                    data[task]["solution"] = solution
                    data[task]["learned_timestamp"] = str(datetime.datetime.now())
                else:
                    data[task] = {
                        "status": "learned",
                        "timestamp": str(datetime.datetime.now()),
                        "learned_timestamp": str(datetime.datetime.now()),
                        "attempts": 0,
                        "solution": solution
                    }
                
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=4)
            
            return solution
    except Exception as e:
        print(f"Error learning from LLM: {e}")
    
    return None

def handle_unknown_command(command):
    """
    Handle an unknown command using the knowledge base and learning
    
    Args:
        command (str): The unknown command
    
    Returns:
        str: Response or None if can't handle
    """
    # Check if we already know this command
    solution = get_solution(command)
    if solution:
        # Try to execute the command if it's something we can execute
        executed = execute_learned_command(command)
        if executed:
            return f"I've executed the command: {command}"
        return f"I know how to handle this: {solution}"
    
    # Check for similar commands
    similar_task = find_similar_task(command)
    if similar_task:
        solution = get_solution(similar_task)
        if solution:
            # Log that we found a similar command
            try:
                from brain.memory import log_event
                log_event("LEARNING", f"Found similar task for '{command}': '{similar_task}'")
            except ImportError:
                pass
                
            # Try to execute the similar command if it's something we can execute
            executed = execute_learned_command(command)  # Try with original command first
            if not executed:
                executed = execute_learned_command(similar_task)  # Try with similar command
                
            if executed:
                return f"I've executed a similar command: {similar_task}"
            return f"I know something similar: {solution}"
    
    # Before giving up, try to generate a solution on the fly
    executed = try_generate_and_execute(command)
    if executed:
        return f"I've figured out how to execute: {command}"
    
    # Log the unknown command
    save_unknown(command)
    
    # Log this learning attempt
    try:
        from brain.memory import log_event
        log_event("LEARNING", f"Starting learning process for unknown command: '{command}'")
    except ImportError:
        pass
    
    # Try to learn it
    learned_solution = learn_from_llm(command)
    if learned_solution:
        # Now try to execute it immediately after learning
        executed = execute_learned_command(command)
        if executed:
            return f"I just learned and executed this command: {command}"
        return f"I just learned how to do this: {learned_solution}"
    
    return None

def execute_learned_command(command):
    """
    Attempt to execute a learned command
    
    Args:
        command (str): The command to execute
    
    Returns:
        bool: True if command was executed, False otherwise
    """
    command = command.lower()
    
    # Get the solution for this command
    solution = get_solution(command)
    if not solution:
        # Try to find a similar command
        similar_task = find_similar_task(command)
        if similar_task:
            solution = get_solution(similar_task)
            command = similar_task  # Use the known command instead
    
    # If we don't have a solution, we can't execute it
    if not solution:
        return False
        
    # Parse the solution to identify executable code
    # Look for Python code blocks in the solution
    import re
    code_blocks = re.findall(r'```(?:python)?\s*(.*?)```', solution, re.DOTALL)
    
    # Handle keyboard shortcuts - common patterns
    if ("key" in command.lower() or "press" in command.lower() or 
        "alt" in command.lower() or "ctrl" in command.lower() or 
        "tab" in command.lower() or "shift" in command.lower()):
        
        # Special case for Alt+Tab
        if "alter tab" in command or "alt tab" in command:
            try:
                from utils.mouse_control import handle_press_alter_tab
                result = handle_press_alter_tab()
                
                # Log this execution
                try:
                    from brain.memory import log_event
                    log_event("ACTION_EXECUTED", f"Executed Alt+Tab command via learning module")
                except ImportError:
                    pass
                    
                return result
            except Exception as e:
                print(f"Error executing Alt+Tab command: {e}")
        
        # For other keyboard commands, extract key combination and execute
        try:
            import pyautogui
            
            # Look for key combinations in the solution
            key_patterns = [
                r'press[^\n]*?[\'"`](.+?)[\'"`]',  # press('key')
                r'key(?:Down|Up|Press)[^\n]*?[\'"`](.+?)[\'"`]',  # keyDown('key')
                r'hotkey\([\'"`](.+?)[\'"`]',  # hotkey('key1', 'key2')
                r'(?:alt|ctrl|shift|win|cmd)\s*\+\s*([a-z0-9])',  # alt+key syntax
            ]
            
            for pattern in key_patterns:
                keys = re.findall(pattern, solution, re.IGNORECASE)
                if keys:
                    # Log this execution
                    try:
                        from brain.memory import log_event
                        log_event("ACTION_EXECUTED", f"Executing keyboard command: {keys}")
                    except ImportError:
                        pass
                    
                    for key in keys:
                        if '+' in key:  # Handle combinations like 'alt+tab'
                            key_parts = [k.strip() for k in key.split('+')]
                            pyautogui.hotkey(*key_parts)
                        else:
                            pyautogui.press(key)
                    return True
        except Exception as e:
            print(f"Error executing keyboard command: {e}")
    
    # Execute code blocks if found
    if code_blocks:
        try:
            # Log this execution
            try:
                from brain.memory import log_event
                log_event("ACTION_EXECUTED", f"Executing code from learned command: {command}")
            except ImportError:
                pass
            
            # Execute the first code block found
            # We use locals() to capture any functions defined in the code
            local_vars = {}
            exec(code_blocks[0], globals(), local_vars)
            
            # Try to find a function that matches the command name or a common handler pattern
            handler_patterns = [
                r'handle_([a-z_]+)',
                r'def ([a-z_]+_command)',
                r'def ([a-z_]+)',
            ]
            
            for pattern in handler_patterns:
                for func_name in local_vars.keys():
                    if re.match(pattern, func_name) and callable(local_vars[func_name]):
                        # Execute the function
                        local_vars[func_name]()
                        return True
            
            # If we didn't find a matching function but the code executed without errors
            return True
            
        except Exception as e:
            print(f"Error executing learned code: {e}")
            try:
                from brain.memory import log_event
                log_event("ERROR", f"Failed to execute learned code: {str(e)}")
            except ImportError:
                pass
    
    # Try to dynamically create a command handler for UI automation tasks
    return create_dynamic_handler(command, solution)

def create_dynamic_handler(command, solution):
    """
    Dynamically create and execute a command handler based on the solution description
    
    Args:
        command (str): The command that was given
        solution (str): The solution description from the LLM
    
    Returns:
        bool: True if a handler was created and executed, False otherwise
    """
    command = command.lower()
    
    try:
        # Look for action keywords in the command and solution
        action_patterns = {
            # Format: (keywords, function_to_call, required_args)
            "open": (["open", "launch", "start"], "open_application", ["app_name"]),
            "close": (["close", "exit", "quit"], "close_application", ["app_name"]),
            "search": (["search", "look up", "find"], "search_web", ["query"]),
            "type": (["type", "write", "input"], "type_text", ["text"]),
            "click": (["click", "press", "select"], "click", []),
            "drag": (["drag", "move to"], "move_mouse", ["x", "y"]),
            "screenshot": (["screenshot", "capture screen"], "take_screenshot", [])
        }
        
        # Log attempt
        try:
            from brain.memory import log_event
            log_event("ACTION", f"Attempting to create dynamic handler for: {command}")
        except ImportError:
            pass
        
        # Look for a matching action
        for action_key, (keywords, function_name, required_args) in action_patterns.items():
            if any(keyword in command for keyword in keywords):
                # Import required modules
                import re
                
                # Extract arguments based on the action
                args = {}
                
                if "app_name" in required_args:
                    # Try to extract app name
                    app_match = re.search(r'(?:open|launch|start|close|exit|quit)\s+(?:the\s+)?(?:app|application\s+)?([a-zA-Z0-9\s]+)', 
                                          command, re.IGNORECASE)
                    if app_match:
                        args["app_name"] = app_match.group(1).strip()
                
                if "query" in required_args:
                    # Try to extract search query
                    query_match = re.search(r'(?:search|look up|find)\s+(?:for\s+)?([a-zA-Z0-9\s]+)', 
                                            command, re.IGNORECASE)
                    if query_match:
                        args["query"] = query_match.group(1).strip()
                
                if "text" in required_args:
                    # Try to extract text to type
                    text_match = re.search(r'(?:type|write|input)\s+(?:the\s+text\s+)?["\']?([a-zA-Z0-9\s]+)["\']?',
                                           command, re.IGNORECASE)
                    if text_match:
                        args["text"] = text_match.group(1).strip()
                
                if "x" in required_args and "y" in required_args:
                    # Try to extract coordinates
                    coord_match = re.search(r'(?:to|at)\s+(?:coordinates\s+)?(\d+)[,\s]+(\d+)',
                                            command, re.IGNORECASE)
                    if coord_match:
                        args["x"] = int(coord_match.group(1))
                        args["y"] = int(coord_match.group(2))
                
                # Check if we have all required arguments
                if all(arg in args for arg in required_args):
                    # Execute the appropriate function
                    if function_name == "open_application" and "app_name" in args:
                        from brain.tasks import open_application
                        open_application(args["app_name"])
                        return True
                    
                    elif function_name == "close_application" and "app_name" in args:
                        from brain.tasks import close_application
                        close_application(args["app_name"])
                        return True
                    
                    elif function_name == "search_web" and "query" in args:
                        from utils.browser import search_web
                        search_web(args["query"])
                        return True
                    
                    elif function_name == "type_text" and "text" in args:
                        import pyautogui
                        pyautogui.write(args["text"])
                        return True
                    
                    elif function_name == "click":
                        from utils.mouse_control import click
                        click()
                        return True
                    
                    elif function_name == "move_mouse" and "x" in args and "y" in args:
                        from utils.mouse_control import move_mouse
                        move_mouse(args["x"], args["y"])
                        return True
                    
                    elif function_name == "take_screenshot":
                        import pyautogui
                        pyautogui.screenshot("screenshot.png")
                        return True
        
        # If we reach here, we couldn't create a dynamic handler
        return False
                
    except Exception as e:
        print(f"Error creating dynamic handler: {e}")
        try:
            from brain.memory import log_event
            log_event("ERROR", f"Failed to create dynamic handler: {str(e)}")
        except ImportError:
            pass
        return False

def try_generate_and_execute(command):
    """
    Try to generate a solution on the fly and execute it
    
    Args:
        command (str): The unknown command
    
    Returns:
        bool: True if generated and executed successfully, False otherwise
    """
    try:
        # Log this attempt
        try:
            from brain.memory import log_event
            log_event("ACTION", f"Attempting to generate and execute on-the-fly solution for: {command}")
        except ImportError:
            pass
            
        # Check for common command patterns without consulting the LLM
        command = command.lower()
        
        # Handle keyboard shortcuts
        if "press" in command:
            key_matches = {
                "escape": "esc",
                "enter": "enter",
                "space": "space",
                "spacebar": "space",
                "backspace": "backspace",
                "delete": "delete",
                "tab": "tab",
                "up": "up",
                "down": "down",
                "left": "left",
                "right": "right",
                "home": "home",
                "end": "end",
                "page up": "pageup",
                "page down": "pagedown"
            }
            
            # Check for modifier keys
            modifiers = []
            if "ctrl" in command or "control" in command:
                modifiers.append("ctrl")
            if "alt" in command:
                modifiers.append("alt")
            if "shift" in command:
                modifiers.append("shift")
            if "win" in command or "windows" in command:
                modifiers.append("win")
                
            # Check for specific keys
            for key_name, key_code in key_matches.items():
                if key_name in command:
                    try:
                        import pyautogui
                        if modifiers:
                            # Use hotkey for modifier combinations
                            keys = modifiers + [key_code]
                            pyautogui.hotkey(*keys)
                        else:
                            # Just press the key
                            pyautogui.press(key_code)
                            
                        # Log successful execution
                        try:
                            from brain.memory import log_event
                            log_event("ACTION_EXECUTED", f"Generated and executed keyboard command: {key_name} with modifiers {modifiers}")
                        except ImportError:
                            pass
                            
                        return True
                    except Exception as e:
                        print(f"Error executing generated keyboard command: {e}")
            
            # Check for letter/number keys
            key_pattern = r'press\s+(?:the\s+)?(?:letter|key)?\s*[\'""]?([a-z0-9])[\'""]?'
            key_match = re.search(key_pattern, command, re.IGNORECASE)
            if key_match:
                key = key_match.group(1).lower()
                try:
                    import pyautogui
                    if modifiers:
                        # Use hotkey for modifier combinations
                        keys = modifiers + [key]
                        pyautogui.hotkey(*keys)
                    else:
                        # Just press the key
                        pyautogui.press(key)
                    return True
                except Exception as e:
                    print(f"Error executing generated keyboard command: {e}")
        
        # Handle mouse actions
        if "click" in command:
            try:
                from utils.mouse_control import click
                # Check for double click
                if "double" in command:
                    click(clicks=2)
                # Check for right click
                elif "right" in command:
                    click(button='right')
                else:
                    click()
                return True
            except Exception as e:
                print(f"Error executing generated mouse command: {e}")
        
        # Try mouse movement
        if "move mouse" in command:
            match = re.search(r'move\s+(?:the\s+)?mouse\s+to\s+(\d+)\s*,?\s*(\d+)', command)
            if match:
                try:
                    x, y = int(match.group(1)), int(match.group(2))
                    from utils.mouse_control import move_mouse
                    move_mouse(x, y)
                    return True
                except Exception as e:
                    print(f"Error executing generated mouse movement: {e}")
        
        # If we reached here, we couldn't generate a solution on the fly
        return False
        
    except Exception as e:
        print(f"Error in try_generate_and_execute: {e}")
        return False
