import os
import queue
import threading
import customtkinter as ctk
import soundfile as sf
import time
import sounddevice as sd
import traceback
import numpy as np
import pygame
from tkinter import messagebox
from dataAcquisition.microphoneInput import get_next_session_number, increment_session_number, reset_photo_number
from utils.custom_messagebox import CustomMessageBox
from utils.custom_selectionbox import CustomTwoButtonMessageBox
from signalProcessing.process_and_label_audio import process_audio_and_update_dataset

# Paths for patient data and alarm sounds directory
DB_PATH = "data/patientData/patient_data.json"
ALARM_SOUNDS_DIR = "assets/alarm_sounds"

'''
This method gets the color for the sound bar depending on the input's volume level
'''
def get_volume_color(volume):
    r = int(min(255, volume * 2 * 255))
    g = int(min(255, (1 - volume) * 2 * 255))
    return f'#{r:02x}{g:02x}00'

'''
Class for recording the sleep sessions audio
'''
class RecordingScreen(ctk.CTkFrame):
    # Class configuration
    def __init__(self, parent):
        super().__init__(parent)
        pygame.mixer.init()
        self.parent = parent
        self.recording = False
        self.timer_running = False
        self.start_time = None
        self.stream = None
        self.volume_level = 0.0
        self.audio_data = []
        self.sample_rate = 44100
        self.alarm_set = False
        self.segment_duration = 10  # segundos
        self.segment_samples = self.segment_duration * self.sample_rate
        self.segment_buffer = []
        self.segment_index = 0

        # Set dark theme
        self.configure(fg_color="#1e1e2f")

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)
        self.grid_rowconfigure(4, weight=0)
        self.grid_rowconfigure(5, weight=0)
        self.grid_rowconfigure(6, weight=0)
        self.grid_rowconfigure(7, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Recording label
        self.title_label = ctk.CTkLabel(
            self,
            text="Recording session",
            font=ctk.CTkFont(size=40, weight="bold"),
            text_color="white"
        )
        self.title_label.grid(row=1, column=0, pady=(20, 10))

        # Chronometer label
        self.timer_label = ctk.CTkLabel(
            self,
            text="00:00:00",
            font=ctk.CTkFont(size=34, weight="bold"),
            text_color="#a0a0ff"
        )
        self.timer_label.grid(row=2, column=0, pady=10)

        # Progress bar for input volume
        self.audio_level = ctk.CTkProgressBar(
            self,
            orientation="horizontal",
            width=300,
            height=16,
            fg_color="#2a2a3d",
            progress_color="green"
        )
        self.audio_level.set(0)
        self.audio_level.grid(row=3, column=0, pady=(0, 10))

        # Get all available input devices
        self.input_devices = self.get_input_devices()
        self.selected_device = ctk.StringVar(value=self.input_devices[0] if self.input_devices else "No mic found")

        # Option menu for selecting the input device to use
        self.device_selector = ctk.CTkOptionMenu(
            self,
            variable=self.selected_device,
            values=self.input_devices,
            fg_color="#2e2e3f",
            button_color="#7b4fff",
            text_color="white",
            dropdown_fg_color="#2e2e3f",
            dropdown_text_color="white",
            dropdown_hover_color="#3a3a50"
        )
        self.device_selector.grid(row=4, column=0, pady=(0, 10))

        # Information label
        self.alarm_info_label = ctk.CTkLabel(
            self, 
            text="Seleccione la hora de la alarma y el tono deseado:", 
            font=ctk.CTkFont(size=16), 
            text_color="white"
        )
        self.alarm_info_label.grid(row=5, column=0, pady=(10, 0))

        # Frame for time and alarm sound
        self.alarm_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.alarm_frame.grid(row=6, column=0, pady=(5, 10))

        # Select alarm time
        self.hour_var = ctk.StringVar(value="00")
        self.minute_var = ctk.StringVar(value="00")

        # Alarm hour
        self.hour_menu = ctk.CTkOptionMenu(
            self.alarm_frame, 
            variable=self.hour_var, 
            values=[f"{i:02d}" for i in range(24)], 
            width=60,
            fg_color="#2e2e3f",
            button_color="#7b4fff",
            text_color="white",
            dropdown_fg_color="#2e2e3f",
            dropdown_text_color="white",
            dropdown_hover_color="#3a3a50"
        )
        self.hour_menu.pack(side="left", padx=5)

        # Alarm minute
        self.minute_menu = ctk.CTkOptionMenu(
            self.alarm_frame, 
            variable=self.minute_var, 
            values=[f"{i:02d}" for i in range(60)], 
            width=60,
            fg_color="#2e2e3f",
            button_color="#7b4fff",
            text_color="white",
            dropdown_fg_color="#2e2e3f",
            dropdown_text_color="white",
            dropdown_hover_color="#3a3a50"
        )
        self.minute_menu.pack(side="left", padx=5)

        # Alarm sound selection
        self.alarm_sounds = self.get_alarm_sounds()
        self.selected_alarm_sound = ctk.StringVar(
            value=self.alarm_sounds[0] if self.alarm_sounds else "No sound found"
        )
        self.sound_selector = ctk.CTkOptionMenu(
            self.alarm_frame, 
            variable=self.selected_alarm_sound, 
            values=self.alarm_sounds, 
            width=180,
            fg_color="#2e2e3f",
            button_color="#7b4fff",
            text_color="white",
            dropdown_fg_color="#2e2e3f",
            dropdown_text_color="white",
            dropdown_hover_color="#3a3a50"
        )
        self.sound_selector.pack(side="left", padx=5)

        # Record and cancel buttons
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=7, column=0, pady=(10, 40))

        # Record button
        self.record_button = ctk.CTkButton(
            self.button_frame,
            text="Start",
            text_color="white",
            fg_color="#7b4fff",
            hover_color="#a175ff",
            font=ctk.CTkFont(size=20, weight="bold"),
            width=150,
            height=60,
            corner_radius=20,
            command=self.toggle_recording
        )
        self.record_button.pack(side="left", padx=10)

        # Cancel button
        self.cancel_button = ctk.CTkButton(
            self.button_frame,
            text="Cancel",
            text_color="white",
            fg_color="#555555",
            hover_color="#777777",
            font=ctk.CTkFont(size=20, weight="bold"),
            width=150,
            height=60,
            corner_radius=20,
            command=self.confirm_cancel
        )
        self.cancel_button.pack(side="left", padx=10)

        # queue to save audio chunks 
        self.q = queue.Queue()
        self.segment_samples = self.sample_rate * 10
        self.segment_index = 0
        self.processor_thread = threading.Thread(target=self.segment_processor, daemon=True)
        self.processor_thread.start()

    '''
    Get all available input devices
    '''
    def get_input_devices(self):
        devices = sd.query_devices()
        return [device['name'] for device in devices if device['max_input_channels'] > 0] or ["No input device found"]

    '''
    Get all available alarm sounds
    '''
    def get_alarm_sounds(self):
        return [f for f in os.listdir(ALARM_SOUNDS_DIR) if f.endswith('.mp3')]

    '''
    Label configuration for the beginning
    '''
    def on_show(self):
        self.recording = False
        self.timer_running = False
        self.start_time = None
        self.alarm_triggered = False
        self.timer_label.configure(text="00:00:00")
        self.title_label.configure(text="Session Recorder")
        self.record_button.configure(text="Start", fg_color="green", hover_color="#006600")
        self.input_devices = self.get_input_devices()
        self.device_selector.configure(values=self.input_devices)
        self.selected_device.set(self.input_devices[0] if self.input_devices else "No mic found")
        self.audio_level.set(0)

    '''
    Modify function of the record button (Start or Stop)
    '''
    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()

    '''
    Recording funtionality:
    Modify labels and call recording methods
    '''
    def start_recording(self):
        self.audio_data = []
        self.recording = True
        self.timer_running = True
        self.start_time = time.time()
        self.alarm_triggered = False
        self.alarm_time = (int(self.hour_var.get()), int(self.minute_var.get()))
        self.record_button.configure(text="Stop", fg_color="red", hover_color="#990000")
        self.title_label.configure(text="Recording Session...")
        self.update_timer()
        self.start_audio_stream()
        self.update_audio_level_ui()
        self.check_alarm()

    '''
    Know what input device to use
    '''
    def get_selected_device_index(self):
        selected_mic = self.selected_device.get()
        for idx, device in enumerate(sd.query_devices()):
            if device['name'] == selected_mic and device['max_input_channels'] > 0:
                return idx
        return None

    '''
    In this method audio recordings of 10s each one are sent to the signal processing module, for it to check apnea episodes
    '''
    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status)
        volume = np.linalg.norm(indata) / np.sqrt(len(indata))
        self.volume_level = min(volume * 5, 1.0)
        self.audio_data.append(indata.copy())

        # 🚀 En lugar de procesar aquí, mandamos el chunk a la cola
        self.q.put(indata.copy())

    def segment_processor(self):
            """Corre en un hilo aparte: arma segmentos de 10s y los procesa"""
            buffer = []
            while True:
                chunk = self.q.get()  # Espera un bloque
                buffer.append(chunk)
                total_samples = sum(c.shape[0] for c in buffer)

                if total_samples >= self.segment_samples:
                    self.segment_index += 1
                    segment_np = np.concatenate(buffer, axis=0)[:self.segment_samples]

                    # Guardar archivo
                    session_num = get_next_session_number()
                    session_dir = os.path.join("data", "raw", f"Session{session_num}")
                    os.makedirs(session_dir, exist_ok=True)
                    file_path = os.path.join(session_dir, f"segment_{self.segment_index}.wav")
                    sf.write(file_path, segment_np, self.sample_rate)
                    print(f"[INFO] Segment {self.segment_index} saved in: {file_path}")

                    # Procesar archivo
                    try:
                        result = process_audio_and_update_dataset(file_path, False)
                        if result:
                            print("[INFO]: Bad position detected, please get another one!")
                            self.triggerEmergencyAlarm()
                        print(f"[INFO] Processed segment: {self.segment_index}")
                    except Exception as e:
                        print(f"[ERROR] Failed processing segment {self.segment_index}: {e}")

                    # Reiniciar buffer con muestras sobrantes
                    remaining = np.concatenate(buffer, axis=0)[self.segment_samples:]
                    buffer = [remaining] if remaining.size > 0 else []

    '''
    Start recordin audio
    '''
    def start_audio_stream(self):
        mic_index = self.get_selected_device_index()
        if mic_index is None:
            CustomMessageBox(self, title="Error", message="Invalid microphone selected.")
            return
        self.stream = sd.InputStream(callback=self.audio_callback, channels=1, samplerate=44100, device=mic_index)
        self.stream.start()

    '''
    Update audio's volume level 
    '''
    def update_audio_level_ui(self):
        if self.recording:
            self.audio_level.set(self.volume_level)
            self.audio_level.configure(progress_color=get_volume_color(self.volume_level))
            self.after(100, self.update_audio_level_ui)
        else:
            self.audio_level.set(0)

    '''
    Update timer with actual recording time
    '''
    def update_timer(self):
        if not self.timer_running:
            return
        elapsed = int(time.time() - self.start_time)
        h, m, s = elapsed // 3600, (elapsed % 3600) // 60, elapsed % 60
        self.timer_label.configure(text=f"{h:02d}:{m:02d}:{s:02d}")
        self.after(1000, self.update_timer)

    '''
    Check if it is time to play the selected alarm sound
    '''
    def check_alarm(self):
        if self.recording and not self.alarm_triggered:
            now = time.localtime()
            if (now.tm_hour, now.tm_min) == self.alarm_time:
                self.trigger_alarm()
        self.after(1000, self.check_alarm)

    '''
    Play alarm sound
    '''
    def trigger_alarm(self):
        self.alarm_triggered = True
        alarm_path = os.path.join(ALARM_SOUNDS_DIR, self.selected_alarm_sound.get())
        pygame.mixer.music.load(alarm_path)
        pygame.mixer.music.play()
        self.stop_recording()

    '''
    Stop playing alarm's sound
    '''
    def stop_alarm(self):
        if pygame.mixer.music.get_busy():  # Ckecks for actual playing music
            pygame.mixer.music.stop()      # Stops playing music
            self.alarm_triggered = False   # Resets alarm state

    '''
    Stop recording sleep session
    '''
    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.timer_running = False
            self.record_button.configure(text="Saving...", fg_color="blue", hover_color="#0000AA", state="disabled")
            self.cancel_button.configure(state="disabled")
            self.title_label.configure(text="Saving Session...")

            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None

            self.audio_level.set(0)

            if self.get_selected_device_index() is not None:
                self.after(100, self.save_buffered_audio)
            else:
                CustomMessageBox(self, title="Error", message="Invalid microphone selected.")
                self.parent.show_frame("StartScreen")

    '''
    Save the recorded audio
    '''
    def save_buffered_audio(self):
        # record the actual session
        try:
            audio_np = np.concatenate(self.audio_data, axis=0)
            session_num = get_next_session_number()
            session_dir = os.path.join("data", "raw", f"Session{session_num}")
            os.makedirs(session_dir, exist_ok=True)

            file_path = os.path.join(session_dir, "audio.wav")
            sf.write(file_path, audio_np, self.sample_rate)

            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"Archivo de audio no encontrado: {file_path}")

            processed_dir = os.path.join("data", "processed")
            os.makedirs(processed_dir, exist_ok=True)

            start = time.time()
            process_audio_and_update_dataset(file_path, True) # wav_path=file_path??

            # reset photo index to 1 for next session
            reset_photo_number()

            # Delete audio segments
            for f in os.listdir(session_dir):
                if f.startswith("segment_") and f.endswith(".wav"):
                    try:
                        os.remove(os.path.join(session_dir, f))
                        print(f"[INFO] Deleted temporal segment: {f}")
                    except Exception as e:
                        print(f"[WARN] Couldn't delete temporal segment {f}: {e}")


            end = time.time()
            print(f"Audio processing time: {end - start:.4f} seconds")
            increment_session_number()
            CustomMessageBox(self, title="Session Saved", message="This session has been saved.", on_ok=self.stop_alarm)
        # In case there's an error saving the actual session
        except Exception as e:
            error_trace = traceback.format_exc()
            CustomMessageBox(self, title="Error", message=f"Error saving session:\n{e}\n\nTraceback:\n{error_trace}")
            print(str(e) + "\n" + error_trace)
        # End recording process and show main screen
        finally:
            self.record_button.configure(state="normal")
            self.cancel_button.configure(state="normal")
            self.parent.show_frame("StartScreen")

    '''
    Confirm to end the reccording session
    '''
    def confirm_cancel(self):
        CustomTwoButtonMessageBox(parent=self, title="Confirm Action",
                         message="Do you want to proceed?",
                         on_accept=self.cancel_recording,
                         on_cancel=self.on_cancel_action)
    
    '''
    Information on cancel selection
    '''
    def on_cancel_action():
        print("Action Canceled")

    '''
    Cancel all recording session
    '''
    def cancel_recording(self):
        self.recording = False
        self.timer_running = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        self.audio_level.set(0)
        self.parent.show_frame("StartScreen")

    '''
    Set an alarm for emergency
    '''
    def triggerEmergencyAlarm(self):
        # Initialize mixer
        pygame.mixer.init()
        # Play alarm
        alarm_path = os.path.join(ALARM_SOUNDS_DIR, "Alarm 1.mp3")
        pygame.mixer.music.load(alarm_path)
        pygame.mixer.music.play()
        
        # Play for 5 seconds (check for usability) (just play alarm for 5 seconds) 
        # time.sleep(5)
        
        # Custom message to stop music manually
        CustomMessageBox(self, title="Information", message="Bad position a Snoring detected, please change your sleeping position. \n Ok to stop alarm!", on_ok=self.stop_alarm)



#CustomMessageBox(self, title="Session Saved", message="This session has been saved.", on_ok=self.stop_alarm)