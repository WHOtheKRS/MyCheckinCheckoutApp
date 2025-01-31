import sqlite3
from backend.database import DB_NAME
from backend.face_recognition import verify_face


def check_in_out(employee_id, action, reason):
    if not verify_face(employee_id):
        return "Face mismatch! Check-in/out denied."
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO attendance (employee_id, action, reason) VALUES (?, ?, ?)", 
                   (employee_id, action, reason))
    conn.commit()
    conn.close()
    return f"{action} successful!"
