"""
Web browsing functionality for JARVIS
"""
import webbrowser
import requests
import sys
import os
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DEFAULT_SEARCH_ENGINE

def search_web(query):
    """
    Search the web using the default search engine
    
    Args:
        query (str): Search query
    """
    # Log this web action
    try:
        from brain.memory import log_event
        log_event("WEB_ACTION", f"Searching web for: {query}")
    except ImportError:
        pass
        
    encoded_query = urllib.parse.quote_plus(query)
    url = f"{DEFAULT_SEARCH_ENGINE}{encoded_query}"
    webbrowser.open(url)
    return f"Searching for {query}"

def open_website(website):
    """
    Open a specific website
    
    Args:
        website (str): Website URL or name
    """
    # Log this web action
    try:
        from brain.memory import log_event
        log_event("WEB_ACTION", f"Opening website: {website}")
    except ImportError:
        pass
    
    # Add https:// if not present and not a known domain
    if not website.startswith(('http://', 'https://')):
        if not website.endswith(('.com', '.org', '.net', '.edu', '.gov', '.io')):
            website = f"https://{website}.com"
        else:
            website = f"https://{website}"
    
    try:
        webbrowser.open(website)
        return f"Opening {website}"
    except Exception as e:
        try:
            from brain.memory import log_event
            log_event("ERROR", f"Failed to open website {website}: {str(e)}")
        except ImportError:
            pass
        return f"Failed to open {website}: {e}"

def check_internet_connection():
    """
    Check if internet connection is available
    
    Returns:
        bool: True if connected, False otherwise
    """
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False
    except:
        return False

def browse_with_selenium(url):
    """
    Browse a website using Selenium for automated interactions
    
    Args:
        url (str): Website URL
    
    Returns:
        webdriver: Selenium WebDriver instance
    """
    try:
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        # Comment out the next line to see the browser window
        # chrome_options.add_argument("--headless")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        return driver
    except Exception as e:
        print(f"Error launching browser with Selenium: {e}")
        return None

def extract_webpage_content(url):
    """
    Extract text content from a webpage
    
    Args:
        url (str): Website URL
    
    Returns:
        str: Webpage text content
    """
    try:
        driver = browse_with_selenium(url)
        if driver:
            time.sleep(2)  # Wait for page to load
            content = driver.find_element(By.TAG_NAME, "body").text
            driver.quit()
            return content
        return "Failed to load page content"
    except Exception as e:
        return f"Error extracting content: {e}"
