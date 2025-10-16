''' This file provides important and no changing paths to files and folders'''

import os

# Project's base path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Data Paths
JSON_PATH = os.path.join(BASE_DIR, "data", "patientData", "patient_data.json")
CSV_PATH = os.path.join(BASE_DIR, "data", "processed", "processed_patient_data.csv")
RAW_AUDIO_DIR = os.path.join(BASE_DIR, "data", "raw")
TIMELINE_DIR = os.path.join(BASE_DIR, "data", "processed", "timelines")
REPORT_FOLDER = os.path.join(BASE_DIR, "docs")
TERMS_PATH = os.path.join(BASE_DIR, "data", "config", "terms.json")
