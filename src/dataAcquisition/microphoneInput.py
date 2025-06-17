
import json

DB_PATH = "data/patientData/patient_data.json"

def get_next_session_number():
    with open(DB_PATH, "r") as f:
        db = json.load(f)

    session_num = db["patient"]["recordedSessions"]
    return session_num

def increment_session_number():
    with open(DB_PATH, "r+") as f:
        db = json.load(f)
        db["patient"]["recordedSessions"] = int(db["patient"]["recordedSessions"]) + 1
        f.seek(0)
        json.dump(db, f, indent=4)
        f.truncate()


