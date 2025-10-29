import os
import json

DB_PATH = "data/patientData/patient_data.json"
summaries_dir = "data/summaries"

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

"""
Reads the JSON file of the session and returns its data.
"""
def read_session_summary(session_number):
    
    file_path = os.path.join(summaries_dir, f"session_{session_number}.json")
    
    if not os.path.exists(file_path):
        # Create one if it does not exist using initial state
        summary = {
            "eventsAOS": 0,
            "duration": 0,
            "Supine": 0,
            "Lateral": 0,
            "Prone": 0,
            "Fetal": 0
        }
        with open(file_path, "w") as f:
            json.dump(summary, f, indent=4)
        return summary
    
    with open(file_path, "r") as f:
        summary = json.load(f)
    
    return summary

"""
Update session adding a value to a specific key
"""
def update_session_summary(session_number, key, value_to_add):

    summary = read_session_summary(session_number)
    
    if key not in summary:
        raise KeyError(f"Key '{key}' does not exist in the resume for this session.")
    
    summary[key] += value_to_add
    
    file_path = os.path.join(summaries_dir, f"session_{session_number}.json")
    with open(file_path, "w") as f:
        json.dump(summary, f, indent=4)

    return summary


"""
Deletes the sesion's JSON file
"""
def delete_session_json(session_number):
    file_path = os.path.join(summaries_dir, f"session_{session_number}.json")
    
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"File {file_path} deleted.")
        return True
    else:
        print(f"File {file_path} not found.")
        return False