"""
Vision functionality for JARVIS - Object detection and screen analysis
"""
import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageGrab
import sys
import os
import time
import pyautogui
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import WEBCAM_INDEX

# Set path to tesseract executable if needed
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def take_screenshot():
    """
    Capture the entire screen
    
    Returns:
        PIL.Image: Screenshot as PIL Image object
    """
    return ImageGrab.grab()

def save_screenshot(filename="ss/jarvis_screenshot.png"):
    """
    Take a screenshot and save it to file
    
    Args:
        filename (str): Path to save the screenshot
    
    Returns:
        str: Path where screenshot was saved
    """
    img = take_screenshot()
    img.save(filename)
    return f"Screenshot saved as {filename}"

def read_screen():
    """
    Capture screen and extract text using OCR
    
    Returns:
        str: Text extracted from the screen
    """
    try:
        # Log this vision action
        try:
            from brain.memory import log_event
            log_event("VISION_ACTION", "Reading screen text with OCR")
        except ImportError:
            pass
            
        img = take_screenshot()
        text = pytesseract.image_to_string(img)
        
        # Log the extracted text (abbreviated if too long)
        try:
            from brain.memory import log_event
            if text.strip():
                log_event("VISION_DATA", f"Screen text: {text[:150]}..." if len(text) > 150 else f"Screen text: {text}")
            else:
                log_event("VISION_DATA", "No text detected on screen")
        except ImportError:
            pass
            
        return text if text.strip() else "No text detected on screen"
    except Exception as e:
        return f"Error reading screen: {e}"

def detect_object():
    """
    Capture image from webcam and detect objects (placeholder for actual model)
    
    Returns:
        str: Description of detected objects or error message
    """
    # Log this vision action
    try:
        from brain.memory import log_event
        log_event("VISION_ACTION", "Capturing and analyzing webcam image")
    except ImportError:
        pass
        
    try:
        cam = cv2.VideoCapture(WEBCAM_INDEX)
        if not cam.isOpened():
            try:
                from brain.memory import log_event
                log_event("VISION_ERROR", "Could not access webcam")
            except ImportError:
                pass
            return "Could not access webcam"
        
        ret, frame = cam.read()
        if not ret:
            try:
                from brain.memory import log_event
                log_event("VISION_ERROR", "Failed to capture image")
            except ImportError:
                pass
            return "Failed to capture image"
        
        # Save the captured frame
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"object_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        
        # Log the capture
        try:
            from brain.memory import log_event
            log_event("VISION_DATA", f"Captured webcam image saved to {filename}")
        except ImportError:
            pass
        
        # Use a pre-trained object detection model YOLO
        # Load YOLO
        net = cv2.dnn.readNet("model/yolov3-tiny.weights", "model/yolov3-tiny.cfg")
        layer_names = net.getLayerNames()
        output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers().flatten()]
        
        # Load classes
        with open("model/coco.names", "r") as f:
            classes = [line.strip() for line in f.readlines()]
            
        # Prepare the image for YOLO
        height, width, channels = frame.shape
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        
        # Feed the image to the network
        net.setInput(blob)
        outs = net.forward(output_layers)
        
        # Get detection information
        class_ids = []
        confidences = []
        boxes = []
        
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    # Object detected
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    
                    # Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
        
        # Apply non-maximum suppression
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        
        # Draw bounding boxes and labels
        detected_objects = []
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(classes[class_ids[i]])
                detected_objects.append(label)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"{label} {confidences[i]:.2f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Save the result image with detections
        result_filename = f"object_detected_{timestamp}.jpg"
        cv2.imwrite(result_filename, frame)
        
        cam.release()
        
        # Log the detection results
        try:
            from brain.memory import log_event
            if detected_objects:
                objects_str = ", ".join(set(detected_objects))
                log_event("VISION_DATA", f"Detected objects: {objects_str}")
            else:
                log_event("VISION_DATA", "No objects detected")
        except ImportError:
            pass
        
        if detected_objects:
            return f"Detected: {', '.join(set(detected_objects))}"
        else:
            return "No objects detected in the image."
    except Exception as e:
        return f"Error in object detection: {e}"

def detect_faces():
    """
    Detect faces in webcam feed using Haar Cascade classifier
    
    Returns:
        str: Number of faces detected or error message
    """
    # Log this vision action
    try:
        from brain.memory import log_event
        log_event("VISION_ACTION", "Detecting faces with webcam")
    except ImportError:
        pass
        
    try:
        cam = cv2.VideoCapture(WEBCAM_INDEX)
        if not cam.isOpened():
            try:
                from brain.memory import log_event
                log_event("VISION_ERROR", "Could not access webcam")
            except ImportError:
                pass
            return "Could not access webcam"
        
        ret, frame = cam.read()
        if not ret:
            try:
                from brain.memory import log_event
                log_event("VISION_ERROR", "Failed to capture image")
            except ImportError:
                pass
            return "Failed to capture image"
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Load the face cascade
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        # Draw rectangles around detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        # Save the frame with detected faces
        cv2.imwrite("face/detected_faces.jpg", frame)
        
        cam.release()
        face_count = len(faces)
        result = ""
        if face_count > 0:
            result = f"Detected {face_count} {'faces' if face_count > 1 else 'face'} in front of camera."
            try:
                from brain.memory import log_event
                log_event("VISION_DATA", result)
            except ImportError:
                pass
        else:
            result = "No faces detected."
            try:
                from brain.memory import log_event
                log_event("VISION_DATA", "No faces detected in webcam image")
            except ImportError:
                pass
                
        return result
    except Exception as e:
        error_msg = f"Error in face detection: {e}"
        try:
            from brain.memory import log_event
            log_event("VISION_ERROR", error_msg)
        except ImportError:
            pass
        return error_msg

def find_on_screen(image_path, confidence=0.7):
    """
    Find an image on screen
    
    Args:
        image_path (str): Path to the image to find
        confidence (float): Confidence threshold (0-1)
    
    Returns:
        tuple: (x, y) coordinates of found image or None
    """
    # Log this vision action
    try:
        from brain.memory import log_event
        log_event("VISION_ACTION", f"Searching screen for image: {image_path}")
    except ImportError:
        pass
        
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        if location:
            point = pyautogui.center(location)
            try:
                from brain.memory import log_event
                log_event("VISION_DATA", f"Found image '{image_path}' at position {point}")
            except ImportError:
                pass
            return point
            
        # If not found
        try:
            from brain.memory import log_event
            log_event("VISION_DATA", f"Image '{image_path}' not found on screen")
        except ImportError:
            pass
        return None
    except Exception as e:
        error_msg = f"Error finding image on screen: {e}"
        print(error_msg)
        try:
            from brain.memory import log_event
            log_event("VISION_ERROR", error_msg)
        except ImportError:
            pass
        return None