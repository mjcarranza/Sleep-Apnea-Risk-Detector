import customtkinter as ctk
import time
import sounddevice as sd
from dataAcquisition.microphoneInput import record_audio
from tkinter import messagebox

from utils.custom_messagebox import CustomMessageBox

class RecordingScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.recording = False
        self.start_time = None
        self.timer_running = False

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)
        self.grid_rowconfigure(4, weight=0)
        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(self, text="Recording session", font=ctk.CTkFont(size=30, weight="bold"))
        self.title_label.grid(row=1, column=0, pady=(20, 10))

        self.timer_label = ctk.CTkLabel(self, text="00:00:00", font=ctk.CTkFont(size=40, weight="bold"))
        self.timer_label.grid(row=2, column=0, pady=10)

        # Micrófonos disponibles
        self.input_devices = self.get_input_devices()
        self.selected_device = ctk.StringVar(value=self.input_devices[0] if self.input_devices else "No mic found")

        self.device_selector = ctk.CTkOptionMenu(self, variable=self.selected_device, values=self.input_devices)
        self.device_selector.grid(row=3, column=0, pady=(0, 10))

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=4, column=0, pady=(10, 40))

        self.record_button = ctk.CTkButton(
            self.button_frame,
            text="Start",
            text_color="white",
            fg_color="green",
            hover_color="#006600",
            font=ctk.CTkFont(size=20, weight="bold"),
            width=150,
            height=60,
            command=self.toggle_recording
        )
        self.record_button.pack(side="left", padx=10)

        self.cancel_button = ctk.CTkButton(
            self.button_frame,
            text="Cancel",
            text_color="white",
            fg_color="gray",
            hover_color="#555555",
            font=ctk.CTkFont(size=20, weight="bold"),
            width=150,
            height=60,
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
        self.title_label.configure(text="Recording session")
        self.record_button.configure(text="Start", fg_color="green", hover_color="#006600")
        self.input_devices = self.get_input_devices()
        self.device_selector.configure(values=self.input_devices)
        self.selected_device.set(self.input_devices[0] if self.input_devices else "No mic found")

    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.recording = True
        self.timer_running = True
        self.start_time = time.time()
        self.record_button.configure(text="Stop", fg_color="red", hover_color="#990000")
        self.update_timer()

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

            # Llamar a la grabación de audio usando el micrófono seleccionado
            duration = int(time.time() - self.start_time)
            selected_mic = self.selected_device.get()
            mic_index = None

            # Buscar el índice del dispositivo por nombre
            for idx, device in enumerate(sd.query_devices()):
                if device['name'] == selected_mic and device['max_input_channels'] > 0:
                    mic_index = idx
                    break
            
            if mic_index is not None:
                try:
                    record_audio(duration=duration, mic_index=mic_index)
                    CustomMessageBox(self, title="Session Saved", message="This session has been saved.")
                except Exception as e:
                    CustomMessageBox(self, title="Error", message=f"Error saving session:\n{e}")

            else:
                CustomMessageBox(self, title="Error", message="Invalid microphone selected.")

        self.parent.show_frame("StartScreen")


    def finish_stop(self):
        self.recording = False
        self.title_label.configure(text="Recording session")
        messagebox.showinfo("Session Saved", "This session has been saved.")
        self.parent.show_frame("StartScreen")

    def confirm_cancel(self):
        confirm = messagebox.askyesno("Cancel session", "Are you sure you want to cancel this session?\nAll progress will be lost.")
        if confirm:
            self.cancel_recording()

    def cancel_recording(self):
        self.recording = False
        self.timer_running = False
        self.parent.show_frame("StartScreen")
