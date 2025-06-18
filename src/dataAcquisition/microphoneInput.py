"""
This module allows to manage the session's data
"""

import json

DB_PATH = "data/patientData/patient_data.json"

"""
Gets the actual session number from the database
"""
def get_next_session_number():
    with open(DB_PATH, "r") as f:
        db = json.load(f)

    session_num = db["patient"]["recordedSessions"]
    return session_num

"""
Increments the session number to be used in the next session recording
"""
def increment_session_number():
    with open(DB_PATH, "r+") as f:
        db = json.load(f)
        db["patient"]["recordedSessions"] = int(db["patient"]["recordedSessions"]) + 1
        f.seek(0)
        json.dump(db, f, indent=4)
        f.truncate()


