"""
JARVIS Configuration Interface
Launch script for the JARVIS web configuration interface
"""
import os
import sys
import subprocess
import webbrowser
import time

def main():
    """Main function to launch the web interface"""
    # Get the directory path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    web_server_path = os.path.join(script_dir, "web", "server.py")
    
    # Check if server.py exists
    if not os.path.exists(web_server_path):
        print("Error: Web server file not found!")
        return
    
    print("Starting JARVIS Configuration Interface...")
    
    # Start the web server in a separate process
    server_process = subprocess.Popen([sys.executable, web_server_path])
    
    # Give the server time to start up
    time.sleep(2)
    
    # Open the web browser
    print("Opening web interface in your default browser...")
    webbrowser.open('http://localhost:5000')
    
    print("JARVIS Configuration Interface is running.")
    print("Press Ctrl+C to stop the server when you're done.")
    
    try:
        # Keep the script running until interrupted
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping server...")
        server_process.terminate()
        print("Server stopped. Configuration changes have been saved.")

if __name__ == "__main__":
    main()
