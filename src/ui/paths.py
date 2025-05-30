import os

# Ruta base del proyecto (opcional, si quieres construir rutas absolutas)
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# Rutas más utilizadas
JSON_PATH = os.path.join(BASE_DIR, "data", "patientData", "patient_data.json")
CSV_PATH = os.path.join(BASE_DIR, "data", "processed", "processed_patient_data.csv")
RAW_AUDIO_DIR = os.path.join(BASE_DIR, "data", "raw")
TIMELINE_DIR = os.path.join(BASE_DIR, "data", "processed", "timelines")
REPORT_FOLDER = os.path.join(BASE_DIR, "docs")