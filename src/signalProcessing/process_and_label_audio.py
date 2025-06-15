import librosa
import numpy as np
import pandas as pd
import os
import json
import joblib
from scipy.signal import butter, lfilter

# Cargar modelos previamente entrenados
apnea_model = joblib.load("data/models/apnea-prediction-model.pkl")
treatment_model = joblib.load("data/models/treatment_required_model.pkl")

# Ruta del archivo CSV acumulativo 
output_csv = "data/processed/processed_patient_data.csv"
# Ruta del archivo JSON
json_path = "data/patientData/patient_data.json"

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs  # frecuencia de Nyquist
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def bandpass_filter(data, lowcut=20, highcut=3000, fs=16000, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def estimate_noise(audio, sample_rate, duration=3):
    noise_segment = audio[:duration * sample_rate]
    return np.mean(librosa.feature.rms(y=noise_segment))

def extract_frequency_features(segment, sample_rate):
    # FFT para obtener energía por banda
    fft = np.fft.fft(segment)
    freqs = np.fft.fftfreq(len(fft), 1/sample_rate)
    magnitude = np.abs(fft)

    # Energía en bandas típicas de ronquido (100-500 Hz)
    snore_band = magnitude[(freqs >= 100) & (freqs <= 500)]
    snore_energy = np.sum(snore_band)

    return snore_energy

def detect_snoring(rms_value, snore_energy, noise_threshold, energy_threshold=0.1):
    # Debe superar tanto el ruido de fondo como la energía de banda
    return rms_value > noise_threshold and snore_energy > energy_threshold

def extract_features(segment, sample_rate):
    rms = np.mean(librosa.feature.rms(y=segment))
    zcr = np.mean(librosa.feature.zero_crossing_rate(y=segment))
    spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=segment, sr=sample_rate))
    snore_energy = extract_frequency_features(segment, sample_rate)
    return rms, zcr, spectral_centroid, snore_energy

def process_audio_and_update_dataset(wav_path, sample_rate=16000, segment_duration=15):
    print(f"[INFO] Cargando audio desde {wav_path}")
    audio, sr = librosa.load(wav_path, sr=sample_rate)
    samples_per_segment = segment_duration * sample_rate

    # Filtrado paso banda para eliminar ruido fuera de rango
    audio = bandpass_filter(audio, lowcut=20, highcut=3000, fs=sample_rate)

    # Calibrar ruido de fondo
    noise_threshold = estimate_noise(audio, sample_rate)
    print(f"[INFO] Umbral de ruido RMS estimado: {noise_threshold:.5f}")

    all_rows = []

    # Cargar datos paciente
    with open(json_path, "r") as file:
        data = json.load(file)
        patient_data = data["patient"]

    age = int(patient_data["age"])
    gender_str = patient_data["sex"]
    bmi = float(patient_data["bmi"])
    session = int(patient_data["recordedSesions"])

    gender = 1 if gender_str.lower() == "female" else 0 if gender_str.lower() == "male" else 2

    print(f"[INFO] Procesando audio en segmentos de {segment_duration} segundos...")

    for i in range(0, len(audio), samples_per_segment):
        segment = audio[i:i + samples_per_segment]
        if len(segment) == samples_per_segment:
            segment = segment / np.max(np.abs(segment))  # Normalización

            # Extraer características
            snoring_rms, nasal_airflow, spectral_centroid, snore_energy = extract_features(segment, sample_rate)
            has_snoring = detect_snoring(snoring_rms, snore_energy, noise_threshold)

            # Datos para el modelo
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

            row = {
                'Sleep_Session': session,
                'Start_Time': i // sample_rate,
                'End_Time': (i + samples_per_segment) // sample_rate,
                'Age': age,
                'Gender': gender,
                'BMI': bmi,
                'Snoring_Intensity': snoring_rms,
                'Snoring': has_snoring,
                'Nasal_Airflow': nasal_airflow,
                'Spectral_Centroid': spectral_centroid,
                'Snore_Energy': snore_energy,
                'Has_Apnea': has_apnea,
                'Treatment_Required': needs_treatment
            }

            all_rows.append(row)

    df_new = pd.DataFrame(all_rows)

    if os.path.exists(output_csv):
        df_existing = pd.read_csv(output_csv)
        df_updated = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_updated = df_new

    df_updated.to_csv(output_csv, index=False)
    print(f"[INFO] Dataset actualizado: {output_csv}")
