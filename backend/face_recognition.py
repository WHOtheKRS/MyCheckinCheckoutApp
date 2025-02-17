import os
import base64
import cv2
import numpy as np
from deepface import DeepFace

FACE_DATA_FOLDER = "face_data"

def save_uploaded_image(image_data, filename=None):
    try:
        if not image_data:
            print("Error: No image data provided.")
            return None

        if isinstance(image_data, str) and image_data.startswith("data:image"):
            #  Base64 image (Captured from Camera)
            image_bytes = base64.b64decode(image_data.split(",")[1])
            if not filename:
                filename = "temp_image.jpg"
            image_path = os.path.join(FACE_DATA_FOLDER, filename)

            with open(image_path, "wb") as f:
                f.write(image_bytes)

            print(f"Captured image saved successfully: {image_path}")
            return image_path

        elif hasattr(image_data, "filename"):  
            #  Uploaded File
            if not filename:
                filename = image_data.filename
            image_path = os.path.join(FACE_DATA_FOLDER, filename)
            image_data.save(image_path)

            print(f" Uploaded image saved successfully: {image_path}")
            return image_path  

        else:
            print(" Error: Invalid image format provided.")
            return None

    except Exception as e:
        print(f" Error saving uploaded image: {e}")
        return None


def recognize_employee(image_data):
    """
    Recognizes an employee based on uploaded or captured image.
    Uses multiple DeepFace models for robust recognition.
    """
    temp_image_path = save_uploaded_image(image_data)

    if not temp_image_path:
        print("Error: No temporary image created for recognition.")
        return None

    recognized_employee = None  

    deepface_models = ["VGG-Face", "Facenet", "OpenFace", "DeepFace", "ArcFace"]

    for filename in os.listdir(FACE_DATA_FOLDER):
        stored_image_path = os.path.join(FACE_DATA_FOLDER, filename)

        try:
            for model in deepface_models:
                result = DeepFace.verify(
                    img1_path=temp_image_path,
                    img2_path=stored_image_path,
                    model_name=model,
                    enforce_detection=True  
                )

                print(f"[{model}] Comparing with {stored_image_path}: Match = {result['verified']}")  

                if result["verified"]:
                    recognized_employee = os.path.splitext(filename)[0]  
                    break  

            if recognized_employee:
                break  

        except Exception as e:
            print(f"Error recognizing face with {stored_image_path}: {e}")

    # Clean up temporary file
    if os.path.exists(temp_image_path):
        os.remove(temp_image_path)

    if recognized_employee:
        print(f"Employee Recognized: {recognized_employee}")
        return recognized_employee

    print("No matching face found.") 
    return None