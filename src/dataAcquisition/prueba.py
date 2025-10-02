import cv2
import os
import time
import joblib
import mediapipe as mp
import joblib
import numpy as np
from datetime import datetime


import pygame
from microphoneInput import get_next_session_number, get_next_photo_number, increment_photo_number


ALARM_SOUNDS_DIR = "assets/alarm_sounds"

# Load trained model
clf = joblib.load("data/models/pose_classifier_rf.pkl")
# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True, model_complexity=2)
def predict_posture(img_path):
    # Read image
    image = cv2.imread(img_path)
    if image is None:
        raise ValueError(f"No se pudo cargar la imagen: {img_path}")

    # Convert to RGB
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Process with MediaPipe
    results = pose.process(rgb)

    if not results.pose_landmarks:
        return "No se detectaron joints"

    # Extract 33 joints (x, y, z, visibility)
    landmarks = results.pose_landmarks.landmark
    row = []
    for lm in landmarks:
        row.extend([lm.x, lm.y, lm.z, lm.visibility])

    # Convert to array for the model
    modelArray = np.array(row).reshape(1, -1)

    # Prediction
    pred = clf.predict(modelArray)[0]
    print("Holaa"+pred)

'''
# Function to get an image and send it to the sleeping pose detection model
# Return true for a bad position or false for a good one.
# Return the actual sleeping position
'''


def takePhoto():
    # Abrir cámara
    cap = cv2.VideoCapture("/dev/video0")

    if not cap.isOpened():
        print("[INFO]: Couldn't open external camera.")
        return None

    # Configura 1080p
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    # Wait one second for the camera to be ready
    time.sleep(2)

    # Read some frames "dummy"
    for _ in range(15):
        cap.read()

    ret, frame = cap.read()
    if not ret:
        print("[INFO]: Couldn't get the frame")
        cap.release()
        return None

    # Obtener fecha y hora
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Poner el texto en la esquina inferior derecha
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    color = (0, 255, 0)  # verde
    thickness = 2
    margin = 20

    # Obtener tamaño del texto para colocarlo
    (text_width, text_height), _ = cv2.getTextSize(timestamp, font, font_scale, thickness)
    x = frame.shape[1] - text_width - margin
    y = frame.shape[0] - margin

    cv2.putText(frame, timestamp, (x, y), font, font_scale, color, thickness, cv2.LINE_AA)

    # Crear carpeta de sesión
    session_num = get_next_session_number()
    session_dir = os.path.join("data", "raw", f"Session{session_num}", "Images")
    os.makedirs(session_dir, exist_ok=True)

    # Guardar foto
    imgIdx = get_next_photo_number()
    file_path = os.path.join(session_dir, f"capture_{imgIdx}.jpg")
    cv2.imwrite(file_path, frame)

    print(f"[INFO]: Saved photo with timestamp -> {file_path}")

    increment_photo_number()
    cap.release()
    cv2.destroyAllWindows()

    # Return image route
    triggerEmergencyAlarm()
    predict_posture(file_path)

    #return file_path

'''
Set an alarm for emergency
'''
def triggerEmergencyAlarm():
    # Initialize mixer
    pygame.mixer.init()
    # Play alarm
    alarm_path = os.path.join(ALARM_SOUNDS_DIR, "Alarm 1.mp3")
    pygame.mixer.music.load(alarm_path)
    pygame.mixer.music.play()
    # Play for 5 seconds
    time.sleep(2)
    # Stop music
    pygame.mixer.music.stop()



'''
Get date and time when the photo was taken
'''
def getPhotoDatetime(file_path: str) -> str:
    """
    Devuelve la fecha y hora en que fue creada/modificada la foto.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No se encontró la foto: {file_path}")

    # Fecha de última modificación (puedes cambiar a getctime para creación)
    timestamp = os.path.getmtime(file_path)
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


# test
takePhoto()
#print("\nThis is the date and time> "+getPhotoDatetime("data/raw/Session2/capture_21.jpg")+"\n")
#triggerEmergencyAlarm()
"""
time.sleep(1) → espera 1 segundo tras abrir la cámara.

Lee 5 frames descartados antes de capturar el bueno.

Esto permite que la cámara ajuste exposición, balance de blancos y nitidez.
"""




'''
def takePhoto():
    # Use webcam
    cap = cv2.VideoCapture("/dev/video0") #use video0 or video2

    if not cap.isOpened():
        print("[INFO]: Couldn't open external camera.")
        return None

    # Configure 1080p resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    # Wait one second for the camera to be ready
    time.sleep(5)

    # Read some frames "dummy"
    for _ in range(15):
        cap.read()

    ret, frame = cap.read()
    if not ret:
        print("[INFO]: Couldn't get the frame")
        cap.release()
        return None

    # Get actual session folder direction
    session_num = get_next_session_number()
    session_dir = os.path.join("data", "raw", f"Session{session_num}")
    os.makedirs(session_dir, exist_ok=True)

    # Get actual image index
    imgIdx = get_next_photo_number()

    # Save image in actual session
    file_path = os.path.join(session_dir, f"capture_{imgIdx}.jpg")
    cv2.imwrite(file_path, frame)
    print(f"[INFO]: Saved photo to -> {file_path}")

    # Increment photo index
    increment_photo_number()

    cap.release()
    cv2.destroyAllWindows()

    # Return image route
    triggerEmergencyAlarm()
    predict_posture(file_path)
    #return file_path
'''