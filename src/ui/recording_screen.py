import os
import customtkinter as ctk
import soundfile as sf
import json
import time
import sounddevice as sd
import traceback
import numpy as np
from tkinter import messagebox
from dataAcquisition.microphoneInput import get_next_session_number, increment_session_number
from utils.custom_messagebox import CustomMessageBox
from signalProcessing.process_and_label_audio import process_audio_and_update_dataset # forma de importar metodos desde otras carpetas

DB_PATH = "data/patientData/patient_data.json"

# Al principio de la clase agrega esta función de color:
def get_volume_color(volume):
    r = int(min(255, volume * 2 * 255))
    g = int(min(255, (1 - volume) * 2 * 255))
    return f'#{r:02x}{g:02x}00'

class RecordingScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.recording = False
        self.timer_running = False
        self.start_time = None
        self.stream = None
        self.volume_level = 0.0
        self.audio_data = []
        self.sample_rate = 44100


        self.configure(fg_color="#1e1e2f")  # Fondo oscuro general

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)
        self.grid_rowconfigure(4, weight=0)
        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self,
            text="Recording session",
            font=ctk.CTkFont(size=40, weight="bold"),
            text_color="white"
        )
        self.title_label.grid(row=1, column=0, pady=(20, 10))

        self.timer_label = ctk.CTkLabel(
            self,
            text="00:00:00",
            font=ctk.CTkFont(size=34, weight="bold"),
            text_color="#a0a0ff"
        )
        self.timer_label.grid(row=2, column=0, pady=10)

        self.audio_level = ctk.CTkProgressBar(
            self,
            orientation="horizontal",
            width=300,
            height=16,
            fg_color="#2a2a3d",  # fondo del progress bar
            progress_color="green"  # se actualizará dinámicamente
        )
        self.audio_level.set(0)
        self.audio_level.grid(row=3, column=0, pady=(0, 10))

        self.input_devices = self.get_input_devices()
        self.selected_device = ctk.StringVar(value=self.input_devices[0] if self.input_devices else "No mic found")

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

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=5, column=0, pady=(10, 40))

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


    def get_input_devices(self):
        devices = sd.query_devices()
        input_devices = [device['name'] for device in devices if device['max_input_channels'] > 0]
        return input_devices if input_devices else ["No input device found"]

    def on_show(self):
        self.recording = False
        self.timer_running = False
        self.start_time = None
        self.timer_label.configure(text="00:00:00")
        self.title_label.configure(text="Session Recorder")
        self.record_button.configure(text="Start", fg_color="green", hover_color="#006600")
        self.input_devices = self.get_input_devices()
        self.device_selector.configure(values=self.input_devices)
        self.selected_device.set(self.input_devices[0] if self.input_devices else "No mic found")
        self.audio_level.set(0)

    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.audio_data = []  # Limpia grabaciones anteriores
        self.recording = True
        self.timer_running = True
        self.start_time = time.time()
        self.record_button.configure(text="Stop", fg_color="red", hover_color="#990000")
        self.title_label.configure(text="Recording Session...")
        self.update_timer()
        self.start_audio_stream()
        self.update_audio_level_ui()

    def get_selected_device_index(self):
        selected_mic = self.selected_device.get()
        for idx, device in enumerate(sd.query_devices()):
            if device['name'] == selected_mic and device['max_input_channels'] > 0:
                return idx
        return None

    def audio_callback(self, indata, frames, time_info, status):
        if status:
            print(status)
        volume = np.linalg.norm(indata) / np.sqrt(len(indata))
        self.volume_level = min(volume * 5, 1.0)
        self.audio_data.append(indata.copy())  # ← Guarda fragmento de audio


    def start_audio_stream(self):
        mic_index = self.get_selected_device_index()
        if mic_index is None:
            CustomMessageBox(self, title="Error", message="Invalid microphone selected.")
            return
        self.stream = sd.InputStream(callback=self.audio_callback, channels=1, samplerate=44100, device=mic_index)
        self.stream.start()

    def update_audio_level_ui(self):
        if self.recording:
            self.audio_level.set(self.volume_level)
            self.audio_level.configure(progress_color=get_volume_color(self.volume_level))
            self.after(100, self.update_audio_level_ui)
        else:
            self.audio_level.set(0)

    def update_timer(self):
        if not self.timer_running:
            return
        elapsed = int(time.time() - self.start_time)
        h, m, s = elapsed // 3600, (elapsed % 3600) // 60, elapsed % 60
        self.timer_label.configure(text=f"{h:02d}:{m:02d}:{s:02d}")
        self.after(1000, self.update_timer)

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.timer_running = False

            # Cambiar texto y color del botón a "Saving..."
            self.record_button.configure(text="Saving...", fg_color="blue", hover_color="#0000AA")
            self.record_button.configure(state="disabled")
            self.cancel_button.configure(state="disabled")

            # Cambiar título de la pantalla
            self.title_label.configure(text="Saving Session...")

            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None

            self.audio_level.set(0)

            duration = int(time.time() - self.start_time)
            mic_index = self.get_selected_device_index()

            if mic_index is not None:
                # Guardado asincrónico con after
                self.after(100, self.save_buffered_audio)
            else:
                CustomMessageBox(self, title="Error", message="Invalid microphone selected.")
                self.parent.show_frame("StartScreen")

    def save_buffered_audio(self):
        try:
            audio_np = np.concatenate(self.audio_data, axis=0)
            session_num = get_next_session_number()

            session_dir = os.path.join("data", "raw", f"Session{session_num}")
            os.makedirs(session_dir, exist_ok=True)

            file_path = os.path.join(session_dir, "audio.wav")
            sf.write(file_path, audio_np, self.sample_rate)

            # Verifica que el archivo de audio fue guardado correctamente
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"Archivo de audio no encontrado: {file_path}")

            # Asegura que la carpeta de salida para los CSV existe
            processed_dir = os.path.join("data", "processed")
            os.makedirs(processed_dir, exist_ok=True)

            output_csv = os.path.join(processed_dir, f"Session{session_num}_segments.csv")

            # Procesa el audio y guarda resultados en CSV
            process_audio_and_update_dataset(
                wav_path=file_path
            )

            increment_session_number()
            CustomMessageBox(self, title="Session Saved", message="This session has been saved.")

        except Exception as e:
            error_trace = traceback.format_exc()
            CustomMessageBox(
                self,
                title="Error",
                message=f"Error saving session:\n{e}\n\nTraceback:\n{error_trace}"
            )
            print(str(e) + "\n" + error_trace)

        finally:
            self.record_button.configure(state="normal")
            self.cancel_button.configure(state="normal")
            self.parent.show_frame("StartScreen")



    def confirm_cancel(self):
        confirm = messagebox.askyesno("Cancel session", "Are you sure you want to cancel this session?\nAll progress will be lost.")
        if confirm:
            self.cancel_recording()

    def cancel_recording(self):
        self.recording = False
        self.timer_running = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        self.audio_level.set(0)
        self.parent.show_frame("StartScreen")
