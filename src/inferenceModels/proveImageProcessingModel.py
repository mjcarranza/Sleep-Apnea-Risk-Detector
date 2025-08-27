import cv2
import mediapipe as mp
import joblib
import numpy as np

# 🔹 Cargar modelo entrenado
clf = joblib.load("data/models/pose_classifier_rf.pkl")

# 🔹 Inicializar MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True, model_complexity=2)

def predict_posture(img_path):
    # Leer imagen
    image = cv2.imread(img_path)
    if image is None:
        raise ValueError(f"No se pudo cargar la imagen: {img_path}")

    # Convertir a RGB
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Procesar con MediaPipe
    results = pose.process(rgb)

    if not results.pose_landmarks:
        return "No se detectaron joints"

    # Extraer 33 joints (x, y, z, visibility)
    landmarks = results.pose_landmarks.landmark
    row = []
    for lm in landmarks:
        row.extend([lm.x, lm.y, lm.z, lm.visibility])

    # Convertir a array para el modelo
    X = np.array(row).reshape(1, -1)

    # Predicción
    pred = clf.predict(X)[0]
    proba = clf.predict_proba(X)[0]

    return pred, proba

# 🔹 Ejemplo de uso
imagen = "assets/lateralBlnkt.png"  # cambia por tu ruta
postura, probabilidades = predict_posture(imagen)
print(f"🔎 Predicción: {postura}")
print(f"📊 Probabilidades: {probabilidades}")
