import os
import json

DB_PATH = "data/patientData/patient_data.json"

def load_patient_data():
    if not os.path.exists(DB_PATH):
        return {}
    with open(DB_PATH, "r") as file:
        try:
            data = json.load(file)
            return data.get("patient", {})
        except json.JSONDecodeError:
            return {}

def is_profile_complete():
    required_fields = ["age", "sex", "weight_(kg)", "height_(cm)", "bmi", "neck_circumference_(cm)"]
    data = load_patient_data()
    return all(data.get(field) and str(data.get(field)).strip() for field in required_fields)

def save_patient_data(data):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(DB_PATH, "w") as file:
        json.dump({"patient": data}, file, indent=4)
