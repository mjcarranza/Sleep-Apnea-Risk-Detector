'''
This code is used to get all 33 joints in the human body per image and generates a CSV file that is used to train 
the IA Classifier Model.
'''

import os
import cv2
import mediapipe as mp
import pandas as pd
from tqdm import tqdm


# Dataset's route (with sub-folders: fetal, side, prone, supine)
DATASET_DIR = "ImageDataset"
OUTPUT_CSV = "posturesJointsDataset.csv"

# Initialize MediaPipe Pose
mpPose = mp.solutions.pose
pose = mpPose.Pose(static_image_mode=True, model_complexity=2)

# List for saving data
data = []

# Goes through each pose folder 
for label in os.listdir(DATASET_DIR):
    posePath = os.path.join(DATASET_DIR, label)

    # If the path is not recognized
    if not os.path.isdir(posePath):
        continue
    
    print(f"[INFO] Processing: {label} class.")
    
    # Goes through each image contained in the folder
    for imgFile in tqdm(os.listdir(posePath)):
        imgPath = os.path.join(posePath, imgFile)
        image = cv2.imread(imgPath)
        if image is None:
            continue

        # Convert to RGB
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Process using MediaPipe
        results = pose.process(rgb)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            row = []
            # Get each landmark in the row list
            for lm in landmarks:
                row.extend([lm.x, lm.y, lm.z, lm.visibility])
            
            # Add class label to the row (diferentiates the class where the image belongs)
            row.append(label)
            data.append(row)

# Create DataFrame
columns = []
for i in range(33):
    columns.extend([f"x_{i}", f"y_{i}", f"z_{i}", f"vis_{i}"])
columns.append("label")

df = pd.DataFrame(data, columns=columns)

# Save in CSV
df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
print(f"[INFO] Generated CSV: {OUTPUT_CSV} with {len(df)} samples.")
