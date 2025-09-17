import cv2
import os
import time

import pygame
from dataAcquisition.microphoneInput import get_next_session_number, get_next_photo_number, increment_photo_number


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
    time.sleep(1)

    # Read some frames "dummy"
    for _ in range(5):
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


# test
#takePhoto()
#triggerEmergencyAlarm()
"""
time.sleep(1) → espera 1 segundo tras abrir la cámara.

Lee 5 frames descartados antes de capturar el bueno.

Esto permite que la cámara ajuste exposición, balance de blancos y nitidez.
"""