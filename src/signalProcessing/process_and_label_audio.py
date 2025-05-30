import librosa
import numpy as np
import pandas as pd
import os
import json
import joblib

# Cargar modelos previamente entrenados
apnea_model = joblib.load("data/models/apnea-prediction-model.pkl")
treatment_model = joblib.load("data/models/treatment_required_model.pkl")


# Ruta del archivo CSV acumulativo 
output_csv = "data/processed/processed_patient_data.csv"
# Ruta del archivo JSON
json_path = "data/patientData/patient_data.json"


def extract_features(segment, sample_rate):
    rms = np.mean(librosa.feature.rms(y=segment))
    zcr = np.mean(librosa.feature.zero_crossing_rate(y=segment))
    spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=segment, sr=sample_rate))
    return rms, zcr, spectral_centroid

def detect_snoring(rms_value, threshold=0.01):
    return rms_value > threshold

def process_audio_and_update_dataset(wav_path, sample_rate=16000, segment_duration=15):
    print(f"[INFO] Cargando audio desde {wav_path}")
    audio, sr = librosa.load(wav_path, sr=sample_rate)
    samples_per_segment = segment_duration * sample_rate

    all_rows = []

    print(f"[INFO] Loading patient's physical information...")

    # Cargar el archivo
    with open(json_path, "r") as file:
        data = json.load(file)
        patient_data = data["patient"]

    # Extraer datos
    age = int(patient_data["age"])
    gender_str = patient_data["sex"]
    bmi = float(patient_data["bmi"])
    session = int(patient_data["recordedSesions"])

    # Opcional: convertir género a formato numérico (para IA)
    if gender_str.lower() == "female":
        gender = 1
    elif gender_str.lower() == "male":
        gender = 0
    else:
        gender = 2

    print(f"[INFO] Procesando audio en segmentos de {segment_duration} segundos...")

    for i in range(0, len(audio), samples_per_segment):
        segment = audio[i:i + samples_per_segment]
        if len(segment) == samples_per_segment:
            segment = segment / np.max(np.abs(segment))  # Normalización

            # Extraer características
            snoring_rms, nasal_airflow, spectral_centroid = extract_features(segment, sample_rate)
            has_snoring = detect_snoring(snoring_rms)

            # Preparar entrada para el modelo
            input_data = pd.DataFrame([{
                'Age': age,
                'Gender': gender,
                'BMI': bmi,
                'Nasal_Airflow': nasal_airflow,
                'Snoring': has_snoring
            }])

            # Predicciones
            has_apnea = bool(apnea_model.predict(input_data)[0])
            needs_treatment = bool(treatment_model.predict(input_data)[0])

            # Fila a guardar
            row = {
                'Sleep_Session':session,
                'Start_Time': i // sample_rate,
                'End_Time': (i + samples_per_segment) // sample_rate,
                'Age': age,
                'Gender': gender,
                'BMI': bmi,
                'Snoring_Intensity': snoring_rms,
                'Snoring': has_snoring,
                'Nasal_Airflow': nasal_airflow,
                'Spectral_Centroid': spectral_centroid,
                'Has_Apnea': has_apnea,
                'Treatment_Required': needs_treatment
            }

            all_rows.append(row)

    df_new = pd.DataFrame(all_rows)

    # Si el archivo ya existe, agregar filas; si no, crearlo
    if os.path.exists(output_csv):
        df_existing = pd.read_csv(output_csv)
        df_updated = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_updated = df_new

    df_updated.to_csv(output_csv, index=False)
    print(f"[INFO] Dataset actualizado: {output_csv}")
