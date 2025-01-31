from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import cv2
import numpy as np
import os
from backend.auth import authenticate, register_employee
from backend.checkin_checkout import check_in_out
from backend.face_recognition import recognize_face, save_face_encoding

import sys
import os

# Add parent directory to Python path so it finds 'backend'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now you can import backend modules
from backend.auth import authenticate, register_employee


class CheckInApp(App):
    def build(self):
        self.capture = None  # Camera instance
        self.user_id = None  # Store logged-in user ID

        layout = BoxLayout(orientation='vertical', spacing=10)

        # Employee ID & Password Inputs
        self.emp_id = TextInput(hint_text="Employee ID", multiline=False)
        self.password = TextInput(hint_text="Password", password=True, multiline=False)

        # Buttons
        self.register_button = Button(text="Register", on_press=self.register)
        self.login_button = Button(text="Login", on_press=self.login)
        self.checkin_button = Button(text="Check-in", on_press=self.check_in)
        self.checkout_button = Button(text="Check-out", on_press=self.check_out)
        
        # Camera Feed & Capture Button
        self.image_widget = Image()
        self.capture_button = Button(text="Capture Face", on_press=self.capture_face)

        layout.add_widget(self.emp_id)
        layout.add_widget(self.password)
        layout.add_widget(self.register_button)
        layout.add_widget(self.login_button)
        layout.add_widget(self.image_widget)
        layout.add_widget(self.capture_button)
        layout.add_widget(self.checkin_button)
        layout.add_widget(self.checkout_button)

        return layout

    def start_camera(self):
        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0 / 30.0)  # Update at 30 FPS

    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.flip(frame, 0)  # Flip image for correct orientation
            buf = frame.tobytes()
            image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.image_widget.texture = image_texture

    def capture_face(self, instance):
        if self.capture:
            ret, frame = self.capture.read()
        if ret:
            encoding_path = os.path.join("face_data", f"{self.emp_id.text}.jpg")
            cv2.imwrite(encoding_path, frame)
            register_face(self.emp_id.text, use_kivy_camera=True)
            print("Face Registered!")



    def register(self, instance):
        emp_id = self.emp_id.text
        password = self.password.text
        if emp_id and password:
            register_employee(emp_id, password)
            self.start_camera()
        else:
            print("Enter Employee ID & Password")

    def login(self, instance):
        emp_id = self.emp_id.text
        password = self.password.text
        if authenticate(emp_id, password):
            if recognize_face(emp_id):
                self.user_id = emp_id
                print("Login Successful!")
            else:
                print("Face not recognized!")
        else:
            print("Invalid Credentials!")

    def check_in(self, instance):
        if self.user_id:
            msg = check_in_out(self.user_id, "Check-in", "Work Start")
            print(msg)
        else:
            print("Login First!")

    def check_out(self, instance):
        if self.user_id:
            msg = check_in_out(self.user_id, "Check-out", "Leaving")
            print(msg)
        else:
            print("Login First!")

if __name__ == '__main__':
    CheckInApp().run()
