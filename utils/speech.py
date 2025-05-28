"""
Speech recognition and text-to-speech functionality for JARVIS
"""
import pyttsx3
import speech_recognition as sr
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import VOICE_RATE, VOICE_VOLUME

def speak(text):
    """
    Convert text to speech
    
    Args:
        text (str): Text to be spoken
    """
    print(f"JARVIS: {text}")
    
    # Log the spoken text
    try:
        from brain.memory import log_event
        log_event("SPEECH_OUTPUT", text)
    except ImportError:
        # If memory module not available, just continue
        pass
        
    engine = pyttsx3.init()
    engine.setProperty('rate', VOICE_RATE)
    engine.setProperty('volume', VOICE_VOLUME)
    
    # Get available voices and set a male voice if available
    voices = engine.getProperty('voices')
    for voice in voices:
        if "male" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
    
    engine.say(text)
    engine.runAndWait()

def listen():
    """
    Listen for voice commands
    
    Returns:
        str: Recognized speech text or empty string if recognition fails
    """
    recognizer = sr.Recognizer()
    
    recognizer.energy_threshold = 250  # Increase for noisy environments (default 300)
    recognizer.dynamic_energy_threshold = True
    recognizer.dynamic_energy_adjustment_ratio = 1.5
    recognizer.pause_threshold = 0.8  # Seconds of silence before considering phrase complete
    
    with sr.Microphone() as source:
        print("Listening...")
        # Adjust for ambient noise
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        # Set timeout and phrase time limit
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
    try:
        print("Recognizing...")
        text = recognizer.recognize_google(audio)
        print(f"User: {text}")
        
        # Log the recognized speech
        try:
            from brain.memory import log_event
            log_event("SPEECH_RECOGNITION", text)
        except ImportError:
            pass
        return text.lower()
    except sr.UnknownValueError:
        print("Could not understand audio")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return ""
    except Exception as e:
        print(f"Error in speech recognition: {e}")
        return ""

def listen_with_timeout(timeout=5):
    """
    Listen for voice commands with a timeout
    
    Args:
        timeout (int): Timeout duration in seconds
        
    Returns:
        str: Recognized speech text or empty string if recognition fails
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening (with timeout)...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=timeout)
            text = recognizer.recognize_google(audio)
            print(f"User: {text}")
            return text.lower()
        except (sr.WaitTimeoutError, sr.UnknownValueError):
            return ""
        except Exception as e:
            print(f"Error in speech recognition: {e}")
            return ""

def listen_for_wake_word(wake_words):
    """
    Listen continuously until one of the wake words is detected
    
    Args:
        wake_words (list): List of wake word phrases to listen for (e.g., ["hey jarvis", "hello jarvis"])
        
    Returns:
        bool: True if wake word was detected, False otherwise
    """
    recognizer = sr.Recognizer()
    
    while True:
        with sr.Microphone() as source:
            # Reduce adjustment duration for more responsive detection
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            try:
                audio = recognizer.listen(source, timeout=2, phrase_time_limit=4)
                
                try:
                    # Use recognize_google for more accurate recognition
                    text = recognizer.recognize_google(audio).lower()
                    print(f"Heard: {text}")
                    
                    for wake_word in wake_words:
                        if wake_word.lower() in text:
                            print(f"Wake word detected: {wake_word}")
                            
                            # Log the wake word detection
                            try:
                                from brain.memory import log_event
                                log_event("SYSTEM", f"Wake word detected: {wake_word}")
                            except ImportError:
                                pass
                                
                            return True
                    
                    # If we get here, no wake word was detected in this phrase
                    continue
                        
                except sr.UnknownValueError:
                    # Continue listening if speech recognition couldn't understand the audio
                    continue
                except sr.RequestError:
                    # Continue listening if there was an error connecting to Google's API
                    print("Network error. Continuing to listen...")
                    continue
                
            except sr.WaitTimeoutError:
                # Continue listening if timeout occurred
                continue
            except Exception as e:
                print(f"Error in wake word detection: {e}")
                continue
