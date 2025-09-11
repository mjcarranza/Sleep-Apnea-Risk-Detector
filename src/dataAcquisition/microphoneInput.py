"""
This module allows to manage the session's data
"""

import json

DB_PATH = "data/patientData/patient_data.json"
IMG_DB_PATH = "data/patientData/imageIdx.json"

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


"""
Gets the actual image number
"""
def get_next_photo_number():
    with open(IMG_DB_PATH, "r") as f:
        db = json.load(f)

    imageIdx = db["SessionIdx"]["index"]
    return imageIdx

"""
Increments the image index to be used in the next image
"""
def increment_photo_number():
    with open(IMG_DB_PATH, "r+") as f:
        db = json.load(f)
        db["SessionIdx"]["index"] = int(db["SessionIdx"]["index"]) + 1
        f.seek(0)
        json.dump(db, f, indent=4)
        f.truncate()


"""
Reset the image index to be used in the next image
"""
def reset_photo_number():
    with open(IMG_DB_PATH, "r+") as f:
        db = json.load(f)
        db["SessionIdx"]["index"] = 1
        f.seek(0)
        json.dump(db, f, indent=4)
        f.truncate()