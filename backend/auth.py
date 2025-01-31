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

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()  # Ensure table exists

def save_employee(employee_id, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM employees WHERE employee_id = ?", (employee_id,))
        if cursor.fetchone():
            conn.close()
            return False
        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO employees (employee_id, password) VALUES (?, ?)", (employee_id, hashed_password))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("Error saving employee:", e)
        return False

def authenticate(employee_id, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM employees WHERE employee_id=?", (employee_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        stored_password = result[0]
        if isinstance(stored_password, str):  
            stored_password = stored_password.encode('utf-8')

        if bcrypt.checkpw(password.encode('utf-8'), stored_password):  
            return True

    return False

def verify_face_match(employee_id, captured_image):
    stored_image_path = os.path.join(FACE_DATA_FOLDER, f"{employee_id}.jpg")

    if not os.path.exists(stored_image_path):
        print("Stored image not found for:", employee_id)
        return False  

    try:
        # Decode Base64 captured image
        captured_image_data = captured_image.split(",")[1]
        image_bytes = base64.b64decode(captured_image_data)
        np_image = np.frombuffer(image_bytes, dtype=np.uint8)
        captured_img = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

        if captured_img is None:
            print("Error: Captured image is None")
            return False

        # 🛑 Apply MTCNN Face Detection to Extract Faces
        detector = MTCNN()

        # Detect face in captured image
        faces = detector.detect_faces(captured_img)
        if len(faces) == 0:
            print("No face detected in captured image")
            return False
        x, y, width, height = faces[0]['box']
        captured_face = captured_img[y:y+height, x:x+width]

        # Load stored image and detect face
        stored_img = cv2.imread(stored_image_path)
        if stored_img is None:
            print("Error: Stored image is None")
            return False

        stored_faces = detector.detect_faces(stored_img)
        if len(stored_faces) == 0:
            print("No face detected in stored image")
            return False
        sx, sy, sw, sh = stored_faces[0]['box']
        stored_face = stored_img[sy:sy+sh, sx:sx+sw]

        # ✅ Run DeepFace Verification
        result = DeepFace.verify(
            img1_path=captured_face, 
            img2_path=stored_face, 
            model_name="Facenet", 
            enforce_detection=False
        )

        return result["verified"]

    except Exception as e:
        print("DeepFace error:", e)
        return False




