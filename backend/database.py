import sqlite3
import os

DB_NAME = "database.db"
IMAGE_FOLDER = "employee_faces"

# Ensure the folder for storing face images exists
os.makedirs(IMAGE_FOLDER, exist_ok=True)

def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create users table (Admin & Employee)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,  -- 'admin' or 'employee'
            face_image TEXT  -- Path to the stored face image
        )
    ''')

    # Create attendance table (for check-in/check-out records)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            action TEXT NOT NULL,  -- 'checkin' or 'checkout'
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            reason TEXT,
            FOREIGN KEY (employee_id) REFERENCES users (employee_id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Run function to initialize tables
create_tables()
