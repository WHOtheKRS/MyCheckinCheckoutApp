import csv
import os
import base64
import re
from backend.face_recognition import save_uploaded_image


DATA_FILE = "employees.csv"
FACE_DATA_FOLDER = "face_data"

if not os.path.exists(FACE_DATA_FOLDER):
    os.makedirs(FACE_DATA_FOLDER)

def save_employee_data(employee_data, uploaded_file=None):
    try:
        email = employee_data["Email"]
        filename = f"{email}.jpg" 
        image_path = os.path.join(FACE_DATA_FOLDER, filename)

        
        if "Face Image" in employee_data or uploaded_file:
            image_data = employee_data.pop("Face Image", None)  
            saved_image_path = save_uploaded_image(image_data if image_data else uploaded_file)
            if saved_image_path:
                os.rename(saved_image_path, image_path)  
                print(f"Image saved as: {image_path}")

        
        file_exists = os.path.isfile(DATA_FILE)

        with open(DATA_FILE, "a", newline="") as file:
            fieldnames = employee_data.keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader() 

            writer.writerow(employee_data)

        print(f"Employee data saved successfully: {email}")

    except Exception as e:
        print(f"Error saving employee data: {e}")


