import csv
import os
import base64
import re

DATA_FILE = "employees.csv"
FACE_DATA_FOLDER = "face_data"

if not os.path.exists(FACE_DATA_FOLDER):
    os.makedirs(FACE_DATA_FOLDER)



def sanitize_filename(email):
    return re.sub(r'[^\w\-_]', '_', email) + ".jpg"



def save_employee_data(employee_data):
    try:
        image_data = employee_data.pop("Face Image", None)

        if image_data:
            filename = sanitize_filename(employee_data["Email"])
            image_path = os.path.join(FACE_DATA_FOLDER, filename)

            image_bytes = base64.b64decode(image_data.split(",")[1])
            with open(image_path, "wb") as f:
                f.write(image_bytes)

            print(f"Image saved successfully: {image_path}")  # Debugging log

        # Ensure CSV file exists before writing
        file_exists = os.path.isfile(DATA_FILE)

        with open(DATA_FILE, "a", newline="") as file:
            fieldnames = employee_data.keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()  # Write header only if file is new

            writer.writerow(employee_data)

        print(f"Employee data saved successfully: {employee_data['Email']}")  # Debugging log

    except Exception as e:
        print(f"Error saving employee data: {e}")
