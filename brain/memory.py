import datetime
import json
import os

LOG_FILE = "data/jarvis_log.txt"

def log_event(event_type, content):
    """
    Log an event to the JARVIS log file
    
    Args:
        event_type (str): Type of event (USER_COMMAND, ACTION, LLM_QUERY, etc.)
        content (str): The content of the event
    """
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] ({event_type}) {content}\n")

def get_last_n_events(n=10):
    """
    Get the last n events from the log file
    
    Args:
        n (int): Number of events to retrieve
        
    Returns:
        str: The last n events as a string
    """
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            return "".join(lines[-n:]) if lines else ""
    except FileNotFoundError:
        # Create the file if it doesn't exist
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("")
        return ""

def get_events_by_timeframe(minutes=5):
    """
    Get events from the past X minutes
    
    Args:
        minutes (int): How many minutes to look back
        
    Returns:
        str: Events in the specified timeframe
    """
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if not lines:
                return ""
                
            now = datetime.datetime.now()
            cutoff_time = now - datetime.timedelta(minutes=minutes)
            
            recent_events = []
            for line in lines:
                try:
                    # Extract timestamp from log line
                    timestamp_str = line.split(']')[0].replace('[', '')
                    timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    
                    if timestamp >= cutoff_time:
                        recent_events.append(line)
                except (ValueError, IndexError):
                    # Skip lines with invalid format
                    continue
                    
            return "".join(recent_events)
    except FileNotFoundError:
        return ""

def get_events_by_type(event_type, limit=10):
    """
    Get events of a specific type
    
    Args:
        event_type (str): The type of event to filter by
        limit (int): Maximum number of events to return
        
    Returns:
        list: List of matching event contents
    """
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
            matching_events = []
            for line in reversed(lines):  # Start from most recent
                if f"({event_type})" in line:
                    # Extract the content part
                    try:
                        content = line.split(")", 1)[1].strip()
                        matching_events.append(content)
                        if len(matching_events) >= limit:
                            break
                    except IndexError:
                        continue
                    
            return matching_events
    except FileNotFoundError:
        return []

def search_memory(query, limit=10):
    """
    Search memory for events containing the query string
    
    Args:
        query (str): Search term
        limit (int): Maximum number of events to return
        
    Returns:
        list: List of matching log lines
    """
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
            matches = []
            for line in reversed(lines):  # Start from most recent
                if query.lower() in line.lower():
                    matches.append(line.strip())
                    if len(matches) >= limit:
                        break
                    
            return matches
    except FileNotFoundError:
        return []

def summarize_day(date=None):
    """
    Summarize events from a specific day
    
    Args:
        date (datetime.date): Date to summarize (None for today)
        
    Returns:
        dict: Summary of different event types for that day
    """
    if date is None:
        date = datetime.datetime.now().date()
        
    date_str = date.strftime("%Y-%m-%d")
    
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
            summary = {
                "USER_COMMAND": 0,
                "LLM_QUERY": 0,
                "ACTION": 0,
                "SPEECH_OUTPUT": 0,
                "VISION_ACTION": 0,
                "LEARNING": 0,
                "ERROR": 0,
                "total_events": 0
            }
            
            # Track some example events
            examples = {
                "USER_COMMAND": [],
                "ACTION": []
            }
            
            for line in lines:
                if date_str in line:
                    summary["total_events"] += 1
                    
                    # Count by event type
                    for event_type in summary.keys():
                        if f"({event_type})" in line:
                            summary[event_type] += 1
                            
                            # Save a few examples
                            if event_type in examples and len(examples[event_type]) < 3:
                                try:
                                    content = line.split(")", 1)[1].strip()
                                    examples[event_type].append(content)
                                except:
                                    pass
            
            summary["examples"] = examples
            return summary
    except FileNotFoundError:
        return {"total_events": 0, "error": "No log file found"}