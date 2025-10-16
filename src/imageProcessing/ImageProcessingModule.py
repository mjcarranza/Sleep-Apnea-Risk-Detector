"""
This module is in charged of analyse and process each taken picture 
"""
import cv2
import mediapipe as mp
import joblib
import numpy as np

# Load trained model
clf = joblib.load("data/models/pose_classifier_rf.pkl")

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True, model_complexity=2)

'''
This method requires an image to be processed and gives the predicted Sleeping Position'''
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
    # Prediction probability
    proba = clf.predict_proba(modelArray)[0]
    print("The prediction probability is: " + proba)
    
    return pred