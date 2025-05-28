"""
LLM (Language Model) integration with fallback for JARVIS
"""
import requests
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GROQ_API_KEY, GEMINI_API_KEY, OPENAI_API_KEY

def query_groq(prompt, model="llama3-70b-8192"):
    """
    Query Groq LLM API
    
    Args:
        prompt (str): The input prompt
        model (str): Model name to use
    
    Returns:
        str: Response from Groq
    """
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_key":
        raise ValueError("Groq API key not set")
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messages": [{"role": "user", "content": prompt}],
        "model": model
    }
    
    response = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                            headers=headers, 
                            json=data)
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content'].strip()
    else:
        raise Exception(f"Groq API Error: {response.status_code}, {response.text}")

def query_gemini(prompt, model="gemini-2.0-flash"):
    """
    Query Google's Gemini LLM API
    
    Args:
        prompt (str): The input prompt
        model (str): Model name to use
    
    Returns:
        str: Response from Gemini
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_key":
        raise ValueError("Gemini API key not set")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        response_json = response.json()
        return response_json['candidates'][0]['content']['parts'][0]['text'].strip()
    else:
        raise Exception(f"Gemini API Error: {response.status_code}, {response.text}")

def query_openai(prompt, model="gpt-4o-mini"):
    """
    Query OpenAI API
    
    Args:
        prompt (str): The input prompt
        model (str): Model name to use
    
    Returns:
        str: Response from OpenAI
    """
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_key":
        raise ValueError("OpenAI API key not set")
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    response = requests.post("https://api.openai.com/v1/chat/completions", 
                            headers=headers, 
                            json=data)
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content'].strip()
    else:
        raise Exception(f"OpenAI API Error: {response.status_code}, {response.text}")

def query_llm(prompt, system_message = (
    "You are JARVIS, an efficient AI assistant. Respond only with complete, functional Python code. Do not include explanations, steps, markdown formatting, or extra text. Use relative paths when needed. For GUI automation, use only the pyautogui module. Assume all required packages are installed. Output only Python code. If the question is related to the weather or like question just reply with normal answer.")
, include_memory=True):
    """
    Query LLMs with fallback mechanism
    
    Args:
        prompt (str): User's query
        system_message (str): System message to prepend
        include_memory (bool): Whether to include recent memory/context
    
    Returns:
        str: Response from one of the LLMs or an error message
    """
    from brain.memory import get_last_n_events, log_event
    
    # Log this query
    log_event("LLM_QUERY", prompt)
    
    # Get recent context if enabled
    context = ""
    if include_memory:
        context = get_last_n_events(10)
    
    # Format the complete prompt with system message and context
    if context:
        full_prompt = f"{system_message}\n\nRecent history:\n{context}\n\nUser: {prompt}"
    else:
        full_prompt = f"{system_message}\n\nUser: {prompt}"
    # Try each LLM in order
    from brain.memory import log_event
    
    try:
        print("Trying Groq API...")
        response = query_groq(full_prompt)
        log_event("LLM_RESPONSE", response)
        return response
    except Exception as e:
        print(f"Groq API failed: {e}")
        try:
            print("Trying Gemini API...")
            response = query_gemini(full_prompt)
            log_event("LLM_RESPONSE", response)
            return response
        except Exception as e:
            print(f"Gemini API failed: {e}")
            try:
                print("Trying OpenAI API...")
                response = query_openai(full_prompt)
                log_event("LLM_RESPONSE", response)
                return response
            except Exception as e:
                print(f"OpenAI API failed: {e}")
                error_msg = "I'm sorry, I couldn't connect to my knowledge base at the moment. Please check your API keys and internet connection."
                log_event("LLM_ERROR", str(e))
                return error_msg
