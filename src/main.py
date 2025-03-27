import sys
import os
import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import speech_recognition as sr
import threading
import webbrowser
import googletrans
from googletrans import Translator
import pyttsx3
import ctypes

# ✅ Fix Unicode Error (for Windows Terminal)
sys.stdout.reconfigure(encoding='utf-8')
os.system('chcp 65001')

# ✅ Initialize Text-to-Speech Engine
engine = pyttsx3.init()
engine.say("Optimouse – Navigate smarter, click faster, and experience seamless, hands-free control with precision, efficiency, and ease for ultimate productivity. Let me know if you want any tweaks! 🚀")
engine.runAndWait()

# ✅ Initialize Mediapipe FaceMesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1)

# ✅ Initialize video capture
video_capture = cv2.VideoCapture(0)
if not video_capture.isOpened():
    print("❌ Error: Could not open video stream.")
    exit()

# ✅ Get screen dimensions
screen_width, screen_height = pyautogui.size()

# ✅ Define eye landmarks for blink detection
LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]

# ✅ Track blink events and dwell time
dwell_start_time = None
dwell_threshold = 1.5  # Time in seconds to trigger a click
blink_threshold = 0.2  # EAR threshold for blink detection

# ✅ Initialize Speech Recognition
recognizer = sr.Recognizer()
voice_command_active = False

def activate_voice_command():
    global voice_command_active
    with sr.Microphone() as source:
        print("🎤 Say 'Hey Google' to activate voice commands...")
        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio).lower()
            if "hey google" in command:
                print("✅ Voice command activated!")
                voice_command_active = True
        except sr.UnknownValueError:
            pass
        except sr.RequestError:
            print("⚠ Speech Recognition service error.")

def listen_for_command():
    global voice_command_active
    while True:
        if not voice_command_active:
            activate_voice_command()
        if voice_command_active:
            with sr.Microphone() as source:
                print("🎤 Listening for commands...")
                try:
                    audio = recognizer.listen(source, timeout=5)
                    command = recognizer.recognize_google(audio).lower()
                    print(f"🗣 Recognized Command: {command}")
                    if "click" in command:
                        pyautogui.click()
                    elif "scroll up" in command:
                        pyautogui.scroll(200)
                    elif "scroll down" in command:
                        pyautogui.scroll(-200)
                    elif "close window" in command:
                        pyautogui.hotkey('alt', 'f4')
                    elif "open browser" in command:
                        webbrowser.open("https://www.google.com", new=2)
                    elif "open youtube" in command:
                        webbrowser.open("https://www.youtube.com", new=2)
                    elif "open gmail" in command:
                        webbrowser.open("https://mail.google.com", new=2)
                    elif "open google maps" in command:
                        webbrowser.open("https://www.google.com/maps", new=2)
                    elif "search for" in command:
                        query = command.replace("search for", "").strip()
                        webbrowser.open(f"https://www.google.com/search?q={query}", new=2)
                    elif "play music" in command:
                        webbrowser.open("https://music.youtube.com", new=2)
                    elif "increase volume" in command:
                        pyautogui.press("volumeup")
                    elif "decrease volume" in command:
                        pyautogui.press("volumedown")
                    elif "mute volume" in command:
                        pyautogui.press("volumemute")
                    elif "stop program" in command:
                        print("🛑 Stopping program.")
                        os._exit(0)
                    elif "ok google" in command or "stop listening" in command:
                        print("🔇 Voice command deactivated.")
                        voice_command_active = False
                except sr.UnknownValueError:
                    pass
                except sr.RequestError:
                    print("⚠ Speech Recognition service error.")

def map_to_screen(x, y):
    return int(x * screen_width), int(y * screen_height)

def eye_aspect_ratio(eye_points, landmarks):
    A = np.linalg.norm(np.array([landmarks[eye_points[1]].x, landmarks[eye_points[1]].y]) -
                        np.array([landmarks[eye_points[5]].x, landmarks[eye_points[5]].y]))
    B = np.linalg.norm(np.array([landmarks[eye_points[2]].x, landmarks[eye_points[2]].y]) -
                        np.array([landmarks[eye_points[4]].x, landmarks[eye_points[4]].y]))
    C = np.linalg.norm(np.array([landmarks[eye_points[0]].x, landmarks[eye_points[0]].y]) -
                        np.array([landmarks[eye_points[3]].x, landmarks[eye_points[3]].y]))
    EAR = (A + B) / (2.0 * C)
    return EAR

print("🎯 Eye Tracker Started. Move your eyes to control the cursor. Blink *both eyes once* or dwell to click. Press 'Q' to exit.")

voice_thread = threading.Thread(target=listen_for_command, daemon=True)
voice_thread.start()

while True:
    ret, frame = video_capture.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            try:
                left_eye = np.mean([(face_landmarks.landmark[i].x, face_landmarks.landmark[i].y) for i in LEFT_EYE], axis=0)
                pyautogui.moveTo(*map_to_screen(left_eye[0], left_eye[1]), duration=0.1)
                left_ear = eye_aspect_ratio(LEFT_EYE, face_landmarks.landmark)
                right_ear = eye_aspect_ratio(RIGHT_EYE, face_landmarks.landmark)
                if left_ear < blink_threshold and right_ear < blink_threshold:
                    pyautogui.click()
                    time.sleep(0.3)
            except:
                pass
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
video_capture.release()
cv2.destroyAllWindows()