import librosa
import numpy as np
import pandas as pd
import os
import random

"""  SUSTITUIR EL METODO DE ABAJO POR ESTE CUANDO EL MODELO ESTA LISTO

def predict_apnea(mfcc_features: np.ndarray) -> int:
    prediction = model.predict(mfcc_features.reshape(1, -1))  # ejemplo con sklearn
    return int(prediction[0])
"""

def predict_apnea(mfcc_features: np.ndarray) -> int:
    """
    Función provisional para simular el modelo IA. Devuelve una etiqueta aleatoria.
    En el futuro, aquí se cargará y usará el modelo real.
    """
    return random.randint(0, 1)  # Simulación: 0 = no apnea, 1 = apnea

def process_audio_and_label(wav_path: str, output_csv: str,sample_rate: int = 16000, segment_duration: int = 5, n_mfcc: int = 13):
    """
    Procesa un archivo .wav largo, lo divide en segmentos, extrae MFCCs,
    predice la etiqueta con un modelo provisional, y guarda todo en un CSV.

    Parámetros:
        wav_path (str): Ruta del archivo de audio .wav
        output_csv (str): Ruta del archivo CSV a generar
        sample_rate (int): Frecuencia de muestreo a usar
        segment_duration (int): Duración de cada segmento en segundos
        n_mfcc (int): Número de coeficientes MFCC a extraer
    """
    

    # Cargar el audio completo
    print(f"[INFO] Cargando audio desde {wav_path}")
    audio, sr = librosa.load(wav_path, sr=sample_rate)
    samples_per_segment = segment_duration * sample_rate

    all_rows = []

    print(f"[INFO] Procesando audio en segmentos de {segment_duration} segundos...")

    for i in range(0, len(audio), samples_per_segment):
        segment = audio[i:i + samples_per_segment]
        if len(segment) == samples_per_segment:
            # Normalizar
            segment = segment / np.max(np.abs(segment))

            # Extraer MFCCs
            mfcc = librosa.feature.mfcc(y=segment, sr=sample_rate, n_mfcc=n_mfcc)
            mfcc_mean = np.mean(mfcc, axis=1)  # Vector de longitud n_mfcc


            # Predicción del modelo simulado
            predicted_label = predict_apnea(mfcc_mean)

            # Calcular tiempos
            start_sec = i // sample_rate
            end_sec = (i + samples_per_segment) // sample_rate

            # Guardar fila: [start_time, end_time, mfcc_0, ..., mfcc_n, label]
            row = [start_sec, end_sec] + mfcc_mean.tolist() + [predicted_label]
            all_rows.append(row)

    # Crear DataFrame
    column_names = ['start_time', 'end_time'] + [f'mfcc_{i}' for i in range(len(all_rows[0]) - 3)] + ['label']
    df = pd.DataFrame(all_rows, columns=column_names)

    # Guardar CSV
    df.to_csv(output_csv, index=False)
    print(f"[INFO] Proceso finalizado. CSV guardado en: {output_csv}")
