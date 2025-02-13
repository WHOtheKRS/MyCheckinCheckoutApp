import os
import base64
import cv2
import numpy as np
import re
from deepface import DeepFace

FACE_DATA_FOLDER = "face_data"



def sanitize_filename(email):
    return re.sub(r'[^\w\-_]', '_', email) + ".jpg"



def save_uploaded_image(image_data):
    try:
        image_bytes = base64.b64decode(image_data.split(",")[1])
        image_path = "temp_image.jpg"
        with open(image_path, "wb") as f:
            f.write(image_bytes)
        
        print(f"Captured image saved successfully: {image_path}")  # Debugging log
        return image_path

    except Exception as e:
        print(f"Error saving uploaded image: {e}")
        return None



def recognize_employee(image_data):
    temp_image_path = save_uploaded_image(image_data)

    if not temp_image_path:
        print("Error: No temporary image created for recognition.")
        return None

    for filename in os.listdir(FACE_DATA_FOLDER):
        stored_image_path = os.path.join(FACE_DATA_FOLDER, filename)

        try:
            result = DeepFace.verify(
                img1_path=temp_image_path,
                img2_path=stored_image_path,
                model_name="VGG-Face",
                enforce_detection=False
            )

            print(f"Comparing with {stored_image_path}: Match = {result['verified']}")  # Debugging log

            if result["verified"]:
                os.remove(temp_image_path)
                return os.path.splitext(filename)[0]  # Return Employee ID

        except Exception as e:
            print(f"Error recognizing face with {stored_image_path}: {e}")

    os.remove(temp_image_path)
    print("No matching face found.")  # Debugging log
    return None