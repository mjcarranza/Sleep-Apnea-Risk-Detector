"""
This module is in charged of user's audio processing such as audio feature extraction and user's dataset update.
"""

import librosa
import numpy as np
import pandas as pd
import os
import json
import joblib
from scipy.signal import butter, lfilter
from imageProcessing.ImageProcessingModule import predict_posture
from dataAcquisition.cameraInput import takePhoto, triggerEmergencyAlarm

# Cargar modelos previamente entrenados
apnea_model = joblib.load("data/models/apnea-prediction-model.pkl")
treatment_model = joblib.load("data/models/treatment_required_model.pkl")

# Ruta del archivo CSV acumulativo 
output_csv = "data/processed/processed_patient_data.csv"
# Ruta del archivo JSON con datos del paciente
json_path = "data/patientData/patient_data.json"

# determination of sleeping position
positionList = []

"""
Creates a Butterworth bandpass filter and returns the coeficients (b, a) for the filter as a touple
"""
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

"""
Apply bandpass filter to an audio signal. Returns fitered signal
"""
def bandpass_filter(data, lowcut=20, highcut=3000, fs=16000, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    return lfilter(b, a, data)

"""
Estimates noise level (RMS) of the first 5 seconds of the recording
"""
def estimate_noise(audio, sample_rate, duration=3):
    noise_segment = audio[:duration * sample_rate]
    return np.mean(librosa.feature.rms(y=noise_segment))

"""
Extracts the energy of the defined snore band (100-500 Hz) using FFT
"""
def extract_frequency_features(segment, sample_rate):
    fft = np.fft.fft(segment)
    freqs = np.fft.fftfreq(len(fft), 1/sample_rate)
    magnitude = np.abs(fft)
    snore_band = magnitude[(freqs >= 100) & (freqs <= 500)]
    return np.sum(snore_band)

"""
Gets the dB level for a given audio segment
"""
def calculate_decibels(segment):
    rms = np.sqrt(np.mean(segment**2))
    if rms == 0:
        return -np.inf
    return 20 * np.log10(rms)

"""
Rescale the obtained zero crossing rate (ZCR) to the AI model's expected range 
"""
def rescale_zcr(zcr_value, old_min=0.0, old_max=0.15, new_min=0.2, new_max=0.5):
    scaled = (zcr_value - old_min) / (old_max - old_min)
    scaled = np.clip(scaled, 0, 1)
    return new_min + (scaled * (new_max - new_min))

"""
Detects if there is a strong snore in the audio segment
"""
def detect_snoring(rms_value, snore_energy, noise_threshold, decibel_level, min_decibel_threshold=-18, energy_threshold=0.1):
    return (rms_value > noise_threshold) and \
           (snore_energy > energy_threshold) and \
           (decibel_level <= min_decibel_threshold)

"""
Extract acoustic features from a given audio segment. 
Retorns a touple (RMS, ZCR reescalado, Centroide espectral, Energía de ronquido, Nivel dB).
"""
def extract_features(segment, sample_rate):
    rms = np.mean(librosa.feature.rms(y=segment))
    zcr = np.mean(librosa.feature.zero_crossing_rate(y=segment, frame_length=512, hop_length=256))
    zcr_rescaled = rescale_zcr(zcr)
    spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=segment, sr=sample_rate))
    snore_energy = extract_frequency_features(segment, sample_rate)
    decibel_level = calculate_decibels(segment)
    print(f"[DEBUG] ZCR original: {zcr:.5f} | ZCR reescalado (Nasal_Airflow): {zcr_rescaled:.5f}")
    return rms, zcr_rescaled, spectral_centroid, snore_energy, decibel_level

"""
Process audio in WAV format, extracts features, predicts apnea and treatment, and updates user's dataset
"""
def process_audio_and_update_dataset(wav_path, finished, sample_rate=16000, segment_duration=5):
    
    # load audio segment
    print(f"[INFO] Loading audio from {wav_path}")
    audio, sr = librosa.load(wav_path, sr=sample_rate)
    # Segments per audio
    samples_per_segment = segment_duration * sample_rate

    audio = bandpass_filter(audio, lowcut=20, highcut=3000, fs=sample_rate)

    noise_threshold = estimate_noise(audio, sample_rate)
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

    print(f"[INFO] Processing audio in segments of {segment_duration} seconds...")

    # Process user's (audio) data
    for i in range(0, len(audio), samples_per_segment):
        segment = audio[i:i + samples_per_segment]
        if len(segment) == samples_per_segment:
            segment = segment / np.max(np.abs(segment))

            snoring_rms, nasal_airflow, spectral_centroid, snore_energy, decibel_level = extract_features(segment, sample_rate)
            print(f"[DEBUG] Decibel level: {decibel_level:.2f} dB")
            has_snoring = detect_snoring(snoring_rms, snore_energy, noise_threshold, decibel_level)


            input_data = pd.DataFrame([{
                'Age': age,
                'Gender': gender,
                'BMI': bmi,
                'Nasal_Airflow': nasal_airflow,
                'Snoring': has_snoring
            }])

            # Prediction models for apnea episodes and treatment required
            has_apnea = bool(apnea_model.predict(input_data)[0])
            needs_treatment = bool(treatment_model.predict(input_data)[0])

            # In case snoring or apnea is detected, call the module to take a picture
            # Previously has_snoring is set to True or False
            # determination of sleeping position
            if (not finished) and (has_snoring or has_apnea):
                # call module to take a photo
                print("[INFO]: Breathing problems detected. \nTaking a picture...")
                img_dir = takePhoto()
                # call Image processing module/predict posture
                prediction = predict_posture(img_dir)
                # Add prediction to a list of predictions using the JSON file

                # in case it is a bad position
                if prediction == "supine":
                    # call method to trigger emergency alarm
                    print("[INFO]: Bad position detected: ", prediction)
                    positionList.append(True)
                    triggerEmergencyAlarm()
                else:
                    print("[INFO]: No bad positions detected.\nThe prediction is: ", prediction)
        
            else:
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
                    'Decibel_Level_dB': decibel_level,
                    'Has_Apnea': has_apnea,
                    'Treatment_Required': needs_treatment
                }

                all_rows.append(row)

    # In case the session is finished, save the processed data 
    if finished:
        df_new = pd.DataFrame(all_rows)

        # Save new data
        if os.path.exists(output_csv):
            df_existing = pd.read_csv(output_csv)
            df_updated = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_updated = df_new

        df_updated.to_csv(output_csv, index=False)
        print(f"[INFO] Dataset Updated: {output_csv}")
    
    # In case there is a bad position detected
    if len(positionList) > 0:
        positionList = [] # clear list
        return True
    
    # if there is not bad positions detected
    else: return False
