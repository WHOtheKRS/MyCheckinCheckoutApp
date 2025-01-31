from flask import Flask, render_template, request, url_for, redirect, session
import os
import cv2
import base64
import numpy as np
from backend.auth import authenticate, save_employee, verify_face_match

app = Flask(__name__)
app.secret_key = "your_secret_key"

UPLOAD_FOLDER = "face_data"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/")
def home():
    return redirect(url_for("register"))  # Redirect to the register page

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        employee_id = request.form["employee_id"]
        password = request.form["password"]
        captured_image = request.form["captured_image"]

        if save_employee(employee_id, password):
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{employee_id}.jpg")
            save_base64_image(captured_image, image_path)

            return redirect("/login")  # Redirect to login after registration
        else:
            return "User already exists. Please login."

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        employee_id = request.form.get("employee_id")
        password = request.form.get("password")
        captured_image = request.form.get("captured_image")

        if not employee_id or not password or not captured_image:
            print("Missing login fields")
            return "Missing fields", 400

        if authenticate(employee_id, password):  # Check ID & password
            print("Password verified for", employee_id)
            if verify_face_match(employee_id, captured_image):  # Check face match
                print("Face matched successfully")
                return redirect(url_for("checkin"))  # Redirect to checkin.html
            else:
                print("Face verification failed for", employee_id)
                return "Face verification failed", 401
        else:
            print("Invalid credentials for", employee_id)
            return "Invalid credentials", 401

    return render_template("login.html")


@app.route("/checkin", methods=["GET", "POST"])
def checkin():
    if request.method == "POST":
        action = request.form["action"]
        reason = request.form["reason"]
        return f"Recorded {action} with reason: {reason}"

    return render_template("checkin.html")

def save_base64_image(image_data, file_path):
    """Convert Base64 image data to actual image and save"""
    image_data = image_data.split(",")[1]  # Remove header
    image_bytes = base64.b64decode(image_data)
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    
    # Improve image quality for facial recognition
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    image = cv2.equalizeHist(image)  # Enhance contrast
    cv2.imwrite(file_path, image)

if __name__ == "__main__":
    app.run(debug=True)
