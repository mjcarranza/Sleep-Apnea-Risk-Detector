import librosa
import numpy as np
import pandas as pd

def predict_apnea(mfcc_features):
    """
    Función simulada para predecir la etiqueta de apnea a partir de características MFCC.
    """
    return np.random.choice(['Normal', 'Apnea'])

def extract_additional_features(segment, sample_rate):
    """
    Extrae características adicionales relacionadas con ronquido, flujo nasal y energía general.
    """
    zcr = np.mean(librosa.feature.zero_crossing_rate(y=segment))  # Flujo nasal (aproximación)
    rms = np.mean(librosa.feature.rms(y=segment))  # Intensidad del ronquido (aproximación)
    spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=segment, sr=sample_rate))
    return rms, zcr, spectral_centroid

def process_audio_and_label(wav_path: str, output_csv: str, sample_rate: int = 16000, segment_duration: int = 15, n_mfcc: int = 13):
    print(f"[INFO] Cargando audio desde {wav_path}")
    audio, sr = librosa.load(wav_path, sr=sample_rate)
    samples_per_segment = segment_duration * sample_rate

    all_rows = []

    print(f"[INFO] Procesando audio en segmentos de {segment_duration} segundos...")

    for i in range(0, len(audio), samples_per_segment):
        segment = audio[i:i + samples_per_segment]
        if len(segment) == samples_per_segment:
            segment = segment / np.max(np.abs(segment))  # Normalización

            mfcc = librosa.feature.mfcc(y=segment, sr=sample_rate, n_mfcc=n_mfcc)
            mfcc_mean = np.mean(mfcc, axis=1)

            snoring_intensity, nasal_airflow_proxy, spectral_centroid = extract_additional_features(segment, sample_rate)
            predicted_label = predict_apnea(mfcc_mean)

            start_sec = i // sample_rate
            end_sec = (i + samples_per_segment) // sample_rate

            row = [start_sec, end_sec] + mfcc_mean.tolist() + [snoring_intensity, nasal_airflow_proxy, spectral_centroid, predicted_label]
            all_rows.append(row)

    column_names = (
        ['start_time', 'end_time'] +
        [f'mfcc_{i}' for i in range(n_mfcc)] +
        ['snoring_intensity', 'nasal_airflow_proxy', 'spectral_centroid', 'label']
    )

    df = pd.DataFrame(all_rows, columns=column_names)
    df.to_csv(output_csv, index=False)
    print(f"[INFO] Proceso finalizado. CSV guardado en: {output_csv}")
