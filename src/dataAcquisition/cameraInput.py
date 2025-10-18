"""
This module allows to take aphoto using an available camera in the system
"""
import cv2
import os
import time
import pygame
from datetime import datetime
from src.dataAcquisition.microphoneInput import get_next_session_number, get_next_photo_number, increment_photo_number

# Where to find the alarm sounds
ALARM_SOUNDS_DIR = "assets/alarm_sounds"

'''
# Function to get an image and send it to the sleeping pose detection model
# Return true for a bad position or false for a good one.
# Return the actual sleeping position
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
    time.sleep(2)

    # Read some frames "dummy"
    for _ in range(15):
        cap.read()

    ret, frame = cap.read()
    if not ret:
        print("[INFO]: Couldn't get the frame")
        cap.release()
        return None

    # Get date and time
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Write date and time in the photo
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    color = (0, 255, 0)  # Green color
    thickness = 2
    margin = 20

    # Get text size to paste it
    (text_width, text_height), _ = cv2.getTextSize(timestamp, font, font_scale, thickness)
    x = frame.shape[1] - text_width - margin
    y = frame.shape[0] - margin

    cv2.putText(frame, timestamp, (x, y), font, font_scale, color, thickness, cv2.LINE_AA)

    # Get actual session folder direction
    session_num = get_next_session_number()
    session_dir = os.path.join("data", "raw", f"Session{session_num}", "Images")
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
    return file_path

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
    time.sleep(5)
    # Stop music
    pygame.mixer.music.stop()


'''
Get date and time when the photo was taken
'''
def getPhotoDatetime(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No se encontró la foto: {file_path}")

    # Fecha de última modificación (puedes cambiar a getctime para creación)
    timestamp = os.path.getmtime(file_path)
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

"""
Returns a list with the names of the files in a folder
"""
def getFileNames(folder_path):
    if not os.path.exists(folder_path):
        print(f"[INFO] Carpeta no encontrada: {folder_path}")
        return []

    # Solo nombres (sin rutas completas)
    return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]