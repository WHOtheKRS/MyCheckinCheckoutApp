import cv2
import face_recognition
import numpy as np
import sqlite3
import os
from mtcnn import MTCNN  # Importing MTCNN for more accurate face detection

DB_NAME = "database.db"
FACE_DATA_FOLDER = "face_data"

if not os.path.exists(FACE_DATA_FOLDER):
    os.makedirs(FACE_DATA_FOLDER)

detector = MTCNN()  # Initialize MTCNN detector


def preprocess_image(image):
    """Convert image to grayscale, normalize, and resize for better recognition."""
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    image = cv2.equalizeHist(image)  # Improve contrast
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)  # Convert back to 3-channel
    return image


def capture_face():
    """Capture a face from the webcam and return the face region with alignment."""
    video_capture = cv2.VideoCapture(0)
    
    while True:
        ret, frame = video_capture.read()
        if not ret:
            continue
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = detector.detect_faces(rgb_frame)  # Detect faces using MTCNN
        
        if faces:
            # Extract the largest face
            largest_face = max(faces, key=lambda f: f['box'][2] * f['box'][3])
            x, y, w, h = largest_face['box']
            
            face_region = frame[y:y + h, x:x + w]  # Crop the face region
            face_region = preprocess_image(face_region)  # Preprocess the face

            video_capture.release()
            return face_region  # Return preprocessed face
        
        cv2.imshow('Capturing Face - Press Q to Exit', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    return None


def register_face(employee_id):
    """Register an employee's face by capturing and storing the face encoding."""
    face = capture_face()
    if face is None:
        return False
    
    encoding = face_recognition.face_encodings(face)
    if not encoding:
        return False  # No encoding found

    encoding = encoding[0]  # Extract the first encoding

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Store the face encoding as a binary blob
    cursor.execute("UPDATE employees SET face_encoding=? WHERE employee_id=?", (encoding.tobytes(), employee_id))
    conn.commit()
    conn.close()
    
    return True


def verify_face(employee_id, captured_image):
    """Verify if the captured face matches the stored face encoding."""
    # Decode captured image
    np_image = np.frombuffer(captured_image, dtype=np.uint8)
    captured_img = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

    captured_img = preprocess_image(captured_img)  # Preprocess before encoding
    captured_encoding = face_recognition.face_encodings(captured_img)

    if not captured_encoding:
        return False  # No face detected in the captured image
    
    captured_encoding = captured_encoding[0]

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT face_encoding FROM employees WHERE employee_id=?", (employee_id,))
    stored_encoding = cursor.fetchone()
    conn.close()

    if stored_encoding:
        stored_encoding = np.frombuffer(stored_encoding[0], dtype=np.float64)
        
        # Compare faces with a stricter threshold
        match = face_recognition.compare_faces([stored_encoding], captured_encoding, tolerance=0.4)
        return match[0]

    return False

# import cv2
# import face_recognition
# import numpy as np
# import sqlite3
# import os
# from mtcnn import MTCNN  # Using MTCNN for more accurate face detection
# from kivy.graphics.texture import Texture  # For Kivy image handling (Mobile)
# from kivy.clock import Clock

# DB_NAME = "database.db"
# FACE_DATA_FOLDER = "face_data"

# if not os.path.exists(FACE_DATA_FOLDER):
#     os.makedirs(FACE_DATA_FOLDER)

# detector = MTCNN()  # Initialize MTCNN detector


# def preprocess_image(image):
#     """Convert image to grayscale, normalize, and resize for better recognition."""
#     image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
#     image = cv2.equalizeHist(image)  # Improve contrast
#     image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)  # Convert back to 3-channel
#     return image


# def capture_face(use_kivy_camera=False):
#     """Capture a face using OpenCV (PC) or return Kivy-compatible texture for mobile."""
#     video_capture = cv2.VideoCapture(0)
    
#     while True:
#         ret, frame = video_capture.read()
#         if not ret:
#             continue
        
#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         faces = detector.detect_faces(rgb_frame)  # Detect faces using MTCNN
        
#         if faces:
#             # Extract the largest face
#             largest_face = max(faces, key=lambda f: f['box'][2] * f['box'][3])
#             x, y, w, h = largest_face['box']
            
#             face_region = frame[y:y + h, x:x + w]  # Crop the face region
#             face_region = preprocess_image(face_region)  # Preprocess the face

#             video_capture.release()
            
#             if use_kivy_camera:
#                 return convert_frame_to_texture(face_region)  # Return texture for Kivy UI
#             else:
#                 return face_region  # Return preprocessed face for PC

#         cv2.imshow('Capturing Face - Press Q to Exit', frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     video_capture.release()
#     cv2.destroyAllWindows()
#     return None


# def convert_frame_to_texture(frame):
#     """Convert OpenCV frame to Kivy-compatible texture."""
#     buf = cv2.flip(frame, 0).tobytes()
#     texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
#     texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
#     return texture


# def register_face(employee_id, use_kivy_camera=False):
#     """Register an employee's face, capturing from either OpenCV (PC) or Kivy (Mobile)."""
#     face = capture_face(use_kivy_camera)
#     if face is None:
#         return False

#     encoding = face_recognition.face_encodings(face)
#     if not encoding:
#         return False  # No encoding found

#     encoding = encoding[0]  # Extract the first encoding

#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
    
#     # Store the face encoding as a binary blob
#     cursor.execute("UPDATE employees SET face_encoding=? WHERE employee_id=?", (encoding.tobytes(), employee_id))
#     conn.commit()
#     conn.close()
    
#     return True


# def verify_face(employee_id, captured_image, use_kivy_camera=False):
#     """Verify if the captured face matches the stored face encoding."""
#     if use_kivy_camera:
#         # Convert Kivy texture to OpenCV image
#         np_image = np.frombuffer(captured_image, dtype=np.uint8)
#         captured_img = cv2.imdecode(np_image, cv2.IMREAD_COLOR)
#     else:
#         # OpenCV image (PC)
#         np_image = np.frombuffer(captured_image, dtype=np.uint8)
#         captured_img = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

#     captured_img = preprocess_image(captured_img)  # Preprocess before encoding
#     captured_encoding = face_recognition.face_encodings(captured_img)

#     if not captured_encoding:
#         return False  # No face detected in the captured image
    
#     captured_encoding = captured_encoding[0]

#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
#     cursor.execute("SELECT face_encoding FROM employees WHERE employee_id=?", (employee_id,))
#     stored_encoding = cursor.fetchone()
#     conn.close()

#     if stored_encoding:
#         stored_encoding = np.frombuffer(stored_encoding[0], dtype=np.float64)
        
#         # Compare faces with a stricter threshold
#         match = face_recognition.compare_faces([stored_encoding], captured_encoding, tolerance=0.4)
#         return match[0]

#     return False

# def recognize_face(employee_id, use_kivy_camera=False):
#     """
#     Recognizes an employee's face and checks if it matches the stored face encoding.
#     """
#     captured_face = capture_face(use_kivy_camera)
#     if captured_face is None:
#         return False
    
#     encoding = face_recognition.face_encodings(captured_face)
#     if not encoding:
#         return False  # No encoding found
    
#     captured_encoding = encoding[0]

#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
#     cursor.execute("SELECT face_encoding FROM employees WHERE employee_id=?", (employee_id,))
#     stored_encoding = cursor.fetchone()
#     conn.close()

#     if stored_encoding:
#         stored_encoding = np.frombuffer(stored_encoding[0], dtype=np.float64)

#         # Compare faces with a stricter threshold
#         match = face_recognition.compare_faces([stored_encoding], captured_encoding, tolerance=0.4)
#         return match[0]

#     return False

# def save_face_encoding(employee_id, face_image):
#     """
#     Saves an employee's face encoding in the database.
#     """
#     encoding = face_recognition.face_encodings(face_image)
#     if not encoding:
#         print("No face encoding found.")
#         return False  # No face encoding detected

#     encoding = encoding[0]  # Get the first encoding

#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
    
#     # Save the face encoding as a binary blob
#     cursor.execute("UPDATE employees SET face_encoding=? WHERE employee_id=?", (encoding.tobytes(), employee_id))
#     conn.commit()
#     conn.close()
    
#     print(f"Face encoding saved for Employee ID: {employee_id}")
#     return True
