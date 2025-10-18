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
def predict_posture(img_path, default_position="unknown"):
    
    # Read the image
    image = cv2.imread(img_path)
    if image is None:
        raise ValueError(f"Could not load image: {img_path}")

    # Get image dimensions
    height, width, _ = image.shape

    # Convert to RGB
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Process with MediaPipe
    results = pose.process(rgb)

    if not results.pose_landmarks:
        print("[WARNING] No joints detected in image. Returning default position.")
        return default_position  # safe fallback

    # Extract 33 joints (x, y, z, visibility) and convert to float
    landmarks = results.pose_landmarks.landmark
    row = []
    for lm in landmarks:
        # Multiply by image dimensions to get absolute coordinates
        row.extend([
            float(lm.x * width),
            float(lm.y * height),
            float(lm.z * max(width, height)),  # scale z proportionally
            float(lm.visibility)
        ])

    # Convert to array for the model
    modelArray = np.array(row, dtype=np.float64).reshape(1, -1)

    # Prediction
    pred = clf.predict(modelArray)[0]

    # Prediction probability
    proba = clf.predict_proba(modelArray)[0]
    print("The prediction probability is: ", proba)

    return pred







'''
     THIS SOLUTION FOR THIS MODULE USES OPENCV COMPILED WITH CUDA, TO USE IT, INSTALL OPENCV WITH CUDA

"""
This module is in charged of analyse and process each taken picture 
"""
import cv2              # OpenCV con CUDA
import mediapipe as mp  # MediaPipe para pose estimation
import joblib           # Cargar modelo sklearn
import numpy as np


# Load trained model
clf = joblib.load("data/models/pose_classifier_rf.pkl")

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True, model_complexity=2)

def predict_posture(img_path, default_position="unknown"):
    """
    Predict the sleeping position from a single image using MediaPipe and a pre-trained sklearn model.
    Optimized with OpenCV CUDA for faster image preprocessing on Jetson Nano.
    """

    # Load image using OpenCV
    image_cpu = cv2.imread(img_path)
    if image_cpu is None:
        raise ValueError(f"Could not load image: {img_path}")

    # Upload image to GPU
    gpu_image = cv2.cuda_GpuMat()
    gpu_image.upload(image_cpu)

    # Convert BGR to RGB on GPU
    gpu_rgb = cv2.cuda.cvtColor(gpu_image, cv2.COLOR_BGR2RGB)

    # Optional: resize to smaller resolution for faster MediaPipe processing
    resized_gpu = cv2.cuda.resize(gpu_rgb, (256, 256))  # adjust size if needed

    # Download to CPU for MediaPipe
    rgb = resized_gpu.download()

    # Process image with MediaPipe Pose
    results = pose.process(rgb)

    if not results.pose_landmarks:
        print("[WARNING] No joints detected in image. Returning default position.")
        return default_position

    # Extract 33 joints (x, y, z, visibility) and scale to original image dimensions
    height, width, _ = image_cpu.shape
    landmarks = results.pose_landmarks.landmark
    row = []
    for lm in landmarks:
        row.extend([
            float(lm.x * width),
            float(lm.y * height),
            float(lm.z * max(width, height)),
            float(lm.visibility)
        ])

    # Convert to NumPy array for sklearn model
    modelArray = np.array(row, dtype=np.float64).reshape(1, -1)

    # Prediction
    pred = clf.predict(modelArray)[0]

    # Prediction probability
    proba = clf.predict_proba(modelArray)[0]
    print(f"[INFO] Prediction probability: {proba}")

    return pred


'''