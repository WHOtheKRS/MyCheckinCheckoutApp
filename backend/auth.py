import sqlite3
import bcrypt
import cv2
import numpy as np
import base64
import os
from deepface import DeepFace
from mtcnn import MTCNN

DB_PATH = "database.db"
FACE_DATA_FOLDER = "face_data"

if not os.path.exists(FACE_DATA_FOLDER):
    os.makedirs(FACE_DATA_FOLDER)


def authenticate(employee_id, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM employees WHERE employee_id=?", (employee_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        stored_password = result[0]
        if bcrypt.checkpw(password.encode("utf-8"), stored_password.encode("utf-8")):
            return True

    return False


def verify_face_match(employee_id, captured_image):
    stored_image_path = os.path.join(FACE_DATA_FOLDER, f"{employee_id}.jpg")

    if not os.path.exists(stored_image_path):
        return False

    try:
        captured_image_data = captured_image.split(",")[1]
        image_bytes = base64.b64decode(captured_image_data)
        np_image = np.frombuffer(image_bytes, dtype=np.uint8)
        captured_img = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

        result = DeepFace.verify(
            img1_path=captured_img,
            img2_path=stored_image_path,
            model_name="Facenet",
            enforce_detection=False
        )

        return result["verified"]

    except Exception as e:
        print("DeepFace error:", e)
        return False
