import sounddevice as sd
import soundfile as sf
import os
import json

DB_PATH = "data/patientData/patient_data.json"

def get_next_session_number():
    with open(DB_PATH, "r") as f:
        db = json.load(f)

    session_num = db["patient"]["recordedSesions"]
    return session_num

def increment_session_number():
    with open(DB_PATH, "r+") as f:
        db = json.load(f)
        db["patient"]["recordedSesions"] += 1
        f.seek(0)
        json.dump(db, f, indent=4)
        f.truncate()

def record_audio(duration, mic_index, sample_rate=44100):
    session_num = get_next_session_number()
    session_dir = os.path.join("data", "raw", f"Session{session_num}")
    os.makedirs(session_dir, exist_ok=True)
    file_path = os.path.join(session_dir, "audio.wav")

    print(f"Recording Session #{session_num} from mic index {mic_index}...")

    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16', device=mic_index)
    sd.wait()
    sf.write(file_path, audio, sample_rate)

    print(f"Audio saved to {file_path}")

    increment_session_number()
    return file_path


