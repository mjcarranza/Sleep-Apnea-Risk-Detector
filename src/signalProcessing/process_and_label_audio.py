"""
This module processes user's audio using PyTorch + torchaudio for GPU acceleration,
extracts features, and updates the user's dataset.
"""

import torch
import torchaudio
import numpy as np
import pandas as pd
import os
import json
import joblib
from src.imageProcessing.ImageProcessingModule import predict_posture
from src.dataAcquisition.cameraInput import takePhoto, triggerEmergencyAlarm
from src.dataAcquisition.microphoneInput import get_next_photo_number

# Device: GPU if available
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# Load pretrained sklearn models
apnea_model = joblib.load("data/models/apnea-prediction-model.pkl")
treatment_model = joblib.load("data/models/treatment_required_model.pkl")

# File paths
output_csv = "data/processed/processed_patient_data.csv"
json_path = "data/patientData/patient_data.json"

# Helper functions
def rescale_zcr(zcr_value, old_min=0.0, old_max=0.15, new_min=0.2, new_max=0.5):
    scaled = (zcr_value - old_min) / (old_max - old_min)
    scaled = np.clip(scaled, 0, 1)
    return new_min + (scaled * (new_max - new_min))

def calculate_decibels(segment):
    rms = torch.sqrt(torch.mean(segment ** 2))
    if rms == 0:
        return -float('inf')
    return 20 * torch.log10(rms).item()

def extract_frequency_features(segment, sample_rate):
    fft = torch.fft.fft(segment)
    freqs = torch.fft.fftfreq(len(fft), 1 / sample_rate)
    magnitude = torch.abs(fft)
    snore_band = magnitude[(freqs >= 100) & (freqs <= 500)]
    return torch.sum(snore_band).item()

def detect_snoring(rms_value, snore_energy, noise_threshold, decibel_level,
                   min_decibel_threshold=-18, energy_threshold=0.1):
    return (rms_value > noise_threshold) and (snore_energy > energy_threshold) and (decibel_level <= min_decibel_threshold)

def extract_features(segment, sample_rate):
    """
    Extract acoustic features from a given audio segment using PyTorch on GPU.
    Returns a tuple: (RMS, ZCR rescaled, Spectral Centroid, Snore Energy, Decibel Level)
    """

    # RMS
    rms = torch.sqrt(torch.mean(segment ** 2)).item()

    # ZCR
    zcr = torch.mean(torch.abs(segment[1:] * segment[:-1] < 0).float()).item()
    zcr_rescaled = rescale_zcr(zcr)

    # FFT and magnitude
    fft_vals = torch.fft.fft(segment)
    magnitude_spectrum = torch.abs(fft_vals)

    # Ensure frequency tensor is on same device as segment
    freqs = torch.fft.fftfreq(len(segment), 1 / sample_rate).to(segment.device)

    # Spectral centroid
    spectral_centroid = (torch.sum(freqs * magnitude_spectrum) / torch.sum(magnitude_spectrum)).item()

    # Snore energy (100-500 Hz)
    snore_band = magnitude_spectrum[(freqs >= 100) & (freqs <= 500)]
    snore_energy = torch.sum(snore_band).item()

    # Decibel level
    decibel_level = 20 * torch.log10(torch.sqrt(torch.mean(segment ** 2))).item() if rms > 0 else -float('inf')

    # Debug print (optional)
    print(f"[DEBUG] ZCR original: {zcr:.5f} | ZCR rescaled: {zcr_rescaled:.5f}")

    return rms, zcr_rescaled, spectral_centroid, snore_energy, decibel_level


def process_audio_and_update_dataset(wav_path, finished, sample_rate=16000, segment_duration=5):
    print(f"[INFO] Loading audio from {wav_path}")
    audio, sr = torchaudio.load(wav_path)
    
    # Resample if needed
    if sr != sample_rate:
        resampler = torchaudio.transforms.Resample(sr, sample_rate)
        audio = resampler(audio)
    
    # Convert to mono
    if audio.shape[0] > 1:
        audio = torch.mean(audio, dim=0, keepdim=True)
    audio = audio.squeeze(0).to(device)
    
    samples_per_segment = segment_duration * sample_rate
    noise_threshold = torch.sqrt(torch.mean(audio[:3 * sample_rate] ** 2)).item()
    print(f"[INFO] Estimated RMS noise threshold: {noise_threshold:.5f}")
    
    all_rows = []

    with open(json_path, "r") as file:
        data = json.load(file)
        patient_data = data["patient"]

    age = int(patient_data["age"])
    gender_str = patient_data["sex"]
    bmi = float(patient_data["bmi"])
    session = int(patient_data["recordedSessions"])
    gender = 1 if gender_str.lower() == "female" else 0 if gender_str.lower() == "male" else 2

    positionList = []

    # Process segments
    for i in range(0, len(audio), samples_per_segment):
        segment = audio[i:i + samples_per_segment]
        if len(segment) == samples_per_segment:
            segment = segment / torch.max(torch.abs(segment))  # normalize

            rms, nasal_airflow, spectral_centroid, snore_energy, decibel_level = extract_features(segment, sample_rate)
            has_snoring = detect_snoring(rms, snore_energy, noise_threshold, decibel_level)

            input_data = pd.DataFrame([{
                'Age': age,
                'Gender': gender,
                'BMI': bmi,
                'Nasal_Airflow': nasal_airflow,
                'Snoring': has_snoring
            }])
            for col in input_data.columns:
                input_data[col] = pd.to_numeric(input_data[col], errors='coerce')

            # Predictions
            has_apnea = bool(apnea_model.predict(input_data)[0])
            needs_treatment = bool(treatment_model.predict(input_data)[0])

            # Image capture if needed
            if (not finished) and (has_snoring or has_apnea):
                print("[INFO]: Breathing problems detected. Taking a picture...")
                img_dir = takePhoto()
                prediction = predict_posture(img_dir)
                print(f"[INFO] Posture prediction: {prediction}")
                imgIdx = get_next_photo_number() - 1
                renameImage(img_dir, f"{prediction}_{imgIdx}")
                if prediction == "supine":
                    print("[INFO]: Bad position detected!")
                    positionList.append(True)
                    triggerEmergencyAlarm()

            # Store segment data
            row = {
                'Sleep_Session': session,
                'Start_Time': i // sample_rate,
                'End_Time': (i + samples_per_segment) // sample_rate,
                'Age': age,
                'Gender': gender,
                'BMI': bmi,
                'Snoring_Intensity': rms,
                'Snoring': has_snoring,
                'Nasal_Airflow': nasal_airflow,
                'Spectral_Centroid': spectral_centroid,
                'Snore_Energy': snore_energy,
                'Decibel_Level_dB': decibel_level,
                'Has_Apnea': has_apnea,
                'Treatment_Required': needs_treatment
            }
            all_rows.append(row)

    # Save CSV if session finished
    if finished:
        df_new = pd.DataFrame(all_rows)
        if os.path.exists(output_csv):
            df_existing = pd.read_csv(output_csv)
            df_updated = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_updated = df_new
        df_updated.to_csv(output_csv, index=False)
        print(f"[INFO] Dataset Updated: {output_csv}")

    return bool(positionList)

def renameImage(old_path, new_name):
    folder = os.path.dirname(old_path)
    extension = os.path.splitext(old_path)[1]
    new_path = os.path.join(folder, new_name + extension)
    os.rename(old_path, new_path)
    print(f"✅ Image renamed: {old_path} -> {new_path}")
