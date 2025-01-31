import sqlite3
import os
import base64

DB_NAME = "database.db"
IMAGE_FOLDER = "employee_faces"

# Ensure the folder exists
os.makedirs(IMAGE_FOLDER, exist_ok=True)

def is_employee_registered(employee_id):
    """Check if an employee ID already exists in the database"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE employee_id=?", (employee_id,))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def save_employee(employee_id, password, face_image):
    """Save employee details in the database with a manually captured image"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Save face image if provided
    image_path = None
    if face_image:
        image_data = base64.b64decode(face_image.split(',')[1])
        image_path = os.path.join(IMAGE_FOLDER, f"{employee_id}.jpg")
        with open(image_path, "wb") as f:
            f.write(image_data)

    cursor.execute("INSERT INTO users (employee_id, password, role, face_image) VALUES (?, ?, ?, ?)", 
                   (employee_id, password, "employee", image_path))
    conn.commit()
    conn.close()
