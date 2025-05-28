"""
Web interface for JARVIS configuration
This module provides a web interface for configuring JARVIS settings
"""
import os
import sys
import json
from flask import Flask, render_template, request, redirect, url_for, jsonify

# Add parent directory to path to enable proper imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import configuration
import config

app = Flask(__name__)

@app.route('/')
def index():
    """Render the main configuration page"""
    return render_template('index.html', 
                          groq_api_key=config.GROQ_API_KEY or '',
                          gemini_api_key=config.GEMINI_API_KEY or '',
                          openai_api_key=config.OPENAI_API_KEY or '',
                          voice_rate=config.VOICE_RATE,
                          voice_volume=config.VOICE_VOLUME,
                          default_search_engine=config.DEFAULT_SEARCH_ENGINE,
                          webcam_index=config.WEBCAM_INDEX,
                          applications=config.APPLICATIONS)

@app.route('/save_config', methods=['POST'])
def save_config():
    """Save configuration to .env file and update applications in knowledge.json"""
    # Update API keys in .env file
    env_path = os.path.join(parent_dir, '.env')
    env_data = {}
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as file:
            for line in file:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    env_data[key] = value
    
    # Update with form data
    env_data['GROQ_API_KEY'] = request.form.get('groq_api_key', '')
    env_data['GEMINI_API_KEY'] = request.form.get('gemini_api_key', '')
    env_data['OPENAI_API_KEY'] = request.form.get('openai_api_key', '')
    
    # Write back to .env file
    with open(env_path, 'w') as file:
        for key, value in env_data.items():
            file.write(f"{key}={value}\n")
    
    # Update voice settings and other configs directly in config.py
    config_path = os.path.join(parent_dir, 'config.py')
    with open(config_path, 'r') as file:
        config_content = file.read()
    
    # Update voice rate
    voice_rate = request.form.get('voice_rate', '180')
    config_content = config_content.replace(f"VOICE_RATE = {config.VOICE_RATE}", f"VOICE_RATE = {voice_rate}")
    
    # Update voice volume
    voice_volume = request.form.get('voice_volume', '2.0')
    config_content = config_content.replace(f"VOICE_VOLUME = {config.VOICE_VOLUME}", f"VOICE_VOLUME = {voice_volume}")
    
    # Update search engine
    search_engine = request.form.get('default_search_engine', 'https://duckduckgo.com/?q=')
    config_content = config_content.replace(f'DEFAULT_SEARCH_ENGINE = "{config.DEFAULT_SEARCH_ENGINE}"', 
                                           f'DEFAULT_SEARCH_ENGINE = "{search_engine}"')
    
    # Update webcam index
    webcam_index = request.form.get('webcam_index', '0')
    config_content = config_content.replace(f"WEBCAM_INDEX = {config.WEBCAM_INDEX}", f"WEBCAM_INDEX = {webcam_index}")
    
    # Write back to config.py
    with open(config_path, 'w') as file:
        file.write(config_content)
    
    # Update applications
    applications = {}
    for key in request.form:
        if key.startswith('app_name_'):
            index = key.replace('app_name_', '')
            app_name = request.form.get(key)
            app_command = request.form.get(f'app_command_{index}', '')
            if app_name and app_command:
                applications[app_name] = app_command
    
    # Update applications in config.py
    updated_apps = json.dumps(applications, indent=4)
    with open(config_path, 'r') as file:
        config_content = file.read()
    
    # Find the APPLICATIONS dictionary in the config file and replace it
    start_marker = "APPLICATIONS = {"
    end_marker = "}"
    start_index = config_content.find(start_marker)
    
    if start_index != -1:
        # Find the matching closing brace
        brace_count = 1
        end_index = start_index + len(start_marker)
        
        while brace_count > 0 and end_index < len(config_content):
            if config_content[end_index] == '{':
                brace_count += 1
            elif config_content[end_index] == '}':
                brace_count -= 1
            end_index += 1
        
        if end_index < len(config_content):
            # Replace the dictionary content with our updated version
            applications_str = "APPLICATIONS = " + updated_apps
            new_config = config_content[:start_index] + applications_str + config_content[end_index:]
            
            with open(config_path, 'w') as file:
                file.write(new_config)
    
    return redirect(url_for('index'))

@app.route('/api/applications', methods=['GET'])
def get_applications():
    """Return the current applications as JSON"""
    return jsonify(config.APPLICATIONS)

@app.route('/test_jarvis', methods=['POST'])
def test_jarvis():
    """Test JARVIS voice functionality"""
    try:
        # Import speech module
        from utils.speech import speak
        
        # Test JARVIS voice
        speak("Hello, I am JARVIS, your personal AI assistant. Configuration interface is now active.")
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
