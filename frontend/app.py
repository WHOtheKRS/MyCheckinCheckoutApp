from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import csv
import os
import base64
import cv2
import numpy as np
import re
import requests
from datetime import datetime
from deepface import DeepFace
from backend.auth import authenticate, verify_face_match
from backend.register import save_employee_data

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.secret_key = os.urandom(24)

EMPLOYEE_CSV = "attendance.csv"
FACE_DATA_FOLDER = "face_data"
ELEVEN_LABS_API_KEY = "sk_9367f3f9d5bdb2f61355ac741f38a9eeb266e900bcdf8743" 

if not os.path.exists(EMPLOYEE_CSV):
    with open(EMPLOYEE_CSV, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Employee ID", "Action", "Timestamp"])

if not os.path.exists(FACE_DATA_FOLDER):
    os.makedirs(FACE_DATA_FOLDER)

if not os.path.exists("frontend/static"):
    os.makedirs("frontend/static")

def sanitize_filename(email):
    return re.sub(r'[^\w\-_]', '_', email) + ".jpg"

from flask import send_from_directory

@app.route('/favicon.ico')
def favicon():
    return send_from_directory("frontend/static", "favicon.ico", mimetype="image/vnd.microsoft.icon")


def speak_message(text):
    try:
        url = "https://api.elevenlabs.io/v1/text-to-speech/tnSpp4vdxKPjI9w0GnoV"
        headers = {
            "xi-api-key": ELEVEN_LABS_API_KEY,
            "Content-Type": "application/json"
        }
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "stability": 0.5,
            "similarity_boost": 0.5,
            "style": 0.5,
            "use_speaker_boost": True
        }

        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            speech_path = "frontend/static/speech.mp3"

            os.makedirs(os.path.dirname(speech_path), exist_ok=True)

            with open(speech_path, "wb") as f:
                f.write(response.content)

            print(f"Speech generated and saved at: {speech_path}")
            return url_for('static', filename='speech.mp3')  # Correct path for frontend

        else:
            print("❌ Error generating speech:", response.json())
            return None
    except Exception as e:
        print("❌ Eleven Labs API Error:", e)
        return None



@app.route("/employee_check", methods=["GET", "POST"])
def employee_check():
    if request.method == "POST":
        try:
            if request.content_type != "application/json":
                return jsonify({"message": "Unsupported Media Type. Use 'application/json'"}), 415

            data = request.get_json()
            if not data:
                return jsonify({"message": "No JSON data received!"}), 400

            image_data = data.get("captured_image")
            if not image_data:
                return jsonify({"message": "No image provided!"}), 400

            print("Received Image Data Successfully")  # Debugging Log

            employee_id = recognize_employee(image_data)

            if employee_id:
                first_name = employee_id.split(" ")[0]  # Extract first name
                last_action = get_last_action(employee_id)
                action = "checkout" if last_action == "checkin" else "checkin"
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                with open(EMPLOYEE_CSV, "a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([employee_id, action, timestamp])

                # Generate personalized speech message
                if action == "checkin":
                    speech_text = f"Hey thanks for checking in! Have a nice day!"
                else:
                    speech_text = f"Thanks for checking out!, See you soon"

                speech_url = speak_message(speech_text)

                return jsonify({"message": f"Thanks {employee_id}, you have {action} at {timestamp}", "speech_url": speech_url})

            return jsonify({"message": "Face not recognized!"})

        except Exception as e:
            print("Error in Employee Check:", e)
            return jsonify({"message": "Internal Server Error"}), 500

    return render_template("employee_check.html")


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        employee_id = request.form["employee_id"]
        password = request.form["password"]

        if employee_id == "hr@softshala" and password == "softshala":
            session["role"] = "hr"
            return redirect(url_for("dashboard"))

        elif authenticate(employee_id, password):
            session["employee_id"] = employee_id
            return redirect(url_for("employee_check"))

        return "Invalid credentials!", 401

    return render_template("login.html")


def recognize_employee(image_data):
    try:
        image_data = image_data.split(",")[1]  # Remove header
        image_bytes = base64.b64decode(image_data)
        np_image = np.frombuffer(image_bytes, dtype=np.uint8)
        captured_img = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

        for filename in os.listdir(FACE_DATA_FOLDER):
            stored_img_path = os.path.join(FACE_DATA_FOLDER, filename)

            try:
                result = DeepFace.verify(
                    img1_path=captured_img,
                    img2_path=stored_img_path,
                    model_name="Facenet",
                    enforce_detection=False
                )

                if result["verified"]:
                    return os.path.splitext(filename)[0]  # Return employee ID

            except Exception as e:
                print("DeepFace Error:", e)

    except Exception as e:
        print("Error Processing Image:", e)

    return None


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "role" not in session or session["role"] != "hr":
        return redirect(url_for("login"))

    if request.method == "POST":
        employee_data = {
            "First Name": request.form["first_name"],
            "Last Name": request.form["last_name"],
            "Gender": request.form["gender"],
            "Contact Number": request.form["contact"],
            "Birthday": request.form["birth_date"],
            "Father Name": request.form["father_name"],
            "Mother Name": request.form["mother_name"],
            "Guardian Contact": request.form["guardian_contact"],
            "Age": request.form["age"],
            "Email": request.form["email"],
            "Permanent Address": request.form["address"],
            "Skills": request.form["skills"],
            "Blood Group": request.form["blood_group"],
            "Joining Date": request.form["joining_date"],
            "Aadhar Card": request.form["aadhar"],
            "PAN Card": request.form["pan"],
        }

        image_data = request.form["captured_image"]
        sanitized_filename = sanitize_filename(employee_data["Email"])
        image_path = os.path.join(FACE_DATA_FOLDER, sanitized_filename)
        save_base64_image(image_data, image_path)

        save_employee_data(employee_data)
        return redirect(url_for("dashboard"))

    return render_template("dashboard.html")


def save_base64_image(image_data, file_path):
    try:
        image_data = image_data.split(",")[1]  # Remove header
        image_bytes = base64.b64decode(image_data)
        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        cv2.imwrite(file_path, image)
        print(f"Image saved successfully: {file_path}")

    except Exception as e:
        print(f"Error Saving Image: {e}")


def get_last_action(employee_id):
    try:
        with open(EMPLOYEE_CSV, "r") as file:
            reader = csv.reader(file)
            rows = list(reader)
            for row in reversed(rows):
                if row[0] == employee_id:
                    return row[1]  # Return last action
    except FileNotFoundError:
        return None
    return None


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)