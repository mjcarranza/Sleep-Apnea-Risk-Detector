import json
import os

def load_patient_data(path):
    """Carga un archivo JSON desde la ruta dada."""
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"[ERROR] JSON file not found: {path}")
        return {}
    except json.JSONDecodeError:
        print(f"[ERROR] JSON decode error in file: {path}")
        return {}

def save_json(path, data):
    """Guarda un diccionario como archivo JSON."""
    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"[ERROR] Could not save JSON to {path}: {e}")

def ensure_directory(path):
    """Crea el directorio si no existe."""
    os.makedirs(path, exist_ok=True)

def format_bmi(weight_kg, height_cm):
    """Calcula el BMI si se dan peso (kg) y altura (cm)."""
    try:
        height_m = height_cm / 100
        return round(weight_kg / (height_m ** 2), 2)
    except ZeroDivisionError:
        return None