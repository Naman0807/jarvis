---
applyTo: "**"
---
name: JARVIS
description: |
  Create a JARVIS-like AI assistant in Python that can understand voice commands, launch applications, perform object detection, and interact with LLMs.
author: "Naman Parmar"
version: "1.0.0"
tags: ["AI", "Voice Assistant", "Python", "Automation", "Object Detection", "LLM"]
category: "AI & Automation"
keywords: ["JARVIS", "AI Assistant", "Voice Commands", "Python Automation", "Object Detection", "LLM Integration"]
---

# 🧠 JARVIS-like AI Assistant – Instruction Manual

## 📝 Summary

This is a step-by-step guide to create a **JARVIS-like AI assistant** in Python that can:

* Understand and respond to your voice.
* Launch applications using PyAutoGUI.
* Perform object detection via camera.
* Analyze what's on the screen and act accordingly.
* Use TTS (Text-to-Speech) via `pyttsx3`.
* Use speech recognition.
* Query LLMs with fallback from **Groq → Gemini → OpenAI**.
* Auto-learn by logging unknown tasks and prompting for help.
* Control mouse and keyboard.
* Open websites and search the web.

---

## 🛠️ Requirements

Install the following packages:

```bash
pip install pyttsx3 SpeechRecognition pyautogui opencv-python pillow pygetwindow numpy pytesseract requests selenium keyboard
```

### For LLM integration:

* **Groq**: Get your [Groq API key](https://console.groq.com/)
* **Gemini**: Get your [Gemini API key](https://aistudio.google.com/app/apikey)
* **OpenAI**: Get your [OpenAI API key](https://platform.openai.com/account/api-keys)

---

## 📁 Folder Structure

```
JARVIS_AI/
│
├── main.py               # Main entry point
├── brain/
│   ├── llm.py            # Handles LLM fallback
│   ├── tasks.py          # Task processing (app launching, etc.)
│   ├── vision.py         # Object detection & screen reading
│   └── learn.py          # Autolearning & saving unknown tasks
├── utils/
│   ├── speech.py         # Speech recognition & TTS
│   ├── mouse_control.py  # Mouse and keyboard control
│   └── browser.py        # Web browsing and search
├── data/
│   └── knowledge.json    # Stores new learned actions
├── instruction.md        # This file
└── config.py             # API keys and configurations
```

---

## 🧠 Main Features

### 1. 🗣️ Voice Interaction

* **TTS:** Uses `pyttsx3`
* **Speech Recognition:** Uses `speech_recognition`

```python
# utils/speech.py
import pyttsx3, speech_recognition as sr

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except:
        return ""
```

---

### 2. 🧠 LLM Fallback

```python
# brain/llm.py
def query_llm(prompt):
    try:
        return query_groq(prompt)
    except:
        try:
            return query_gemini(prompt)
        except:
            return query_openai(prompt)
```

---

### 3. 🚀 Launching Applications

```python
# brain/tasks.py
import pyautogui
import subprocess

def open_app(app_name):
    pyautogui.press('win')
    pyautogui.write(app_name)
    pyautogui.press('enter')
```

---

### 4. 🎥 Object Detection

```python
# brain/vision.py
import cv2

def detect_object():
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    # Apply object detection models here (YOLO or pretrained models)
    cv2.imwrite("object.jpg", frame)
    cam.release()
    return "Object image saved"
```

---

### 5. 🧾 Screen Analysis

```python
# brain/vision.py (continued)
import pytesseract
from PIL import ImageGrab

def read_screen():
    img = ImageGrab.grab()
    text = pytesseract.image_to_string(img)
    return text
```

---

### 6. 🖱️ Mouse & Keyboard Control

```python
# utils/mouse_control.py
import pyautogui

def move_mouse(x, y):
    pyautogui.moveTo(x, y)

def click():
    pyautogui.click()
```

---

### 7. 🌐 Web Browsing

```python
# utils/browser.py
import webbrowser

def search_web(query):
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
```

---

### 8. 🧠 Autolearning

```python
# brain/learn.py
import json

def save_unknown(task):
    with open("data/knowledge.json", "r+") as f:
        data = json.load(f)
        if task not in data:
            data[task] = "unknown"
            f.seek(0)
            json.dump(data, f, indent=4)
```

---

## 🚀 Run the Assistant

```bash
python main.py
```

---

## ✅ Example Commands

| You Say                          | What JARVIS Does                               |
| -------------------------------- | ---------------------------------------------- |
| "Open Chrome"                    | Launches Chrome using PyAutoGUI                |
| "Search Python tutorials"        | Opens browser and searches Google              |
| "What is on my screen?"          | Reads visible text using OCR                   |
| "What is in front of me?"        | Takes webcam snapshot and processes it         |
| "Move mouse to 200 300"          | Moves the mouse to (200, 300)                  |
| "Click"                          | Performs a click                               |
| "Write a script to open Notepad" | Writes & runs PyAutoGUI script to open Notepad |

---

## 🔐 config.py

```python
GROQ_API_KEY = "your_groq_key"
GEMINI_API_KEY = "your_gemini_key"
OPENAI_API_KEY = "your_openai_key"
```

---

## 🧩 Suggestions

* Use **YOLOv5** or **MediaPipe** for better object detection.
* Use **LangChain** or **AutoGen** for advanced LLM chaining (optional).
* Log all commands for training later using GPTs.

---
