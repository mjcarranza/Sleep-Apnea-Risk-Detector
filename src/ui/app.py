#TERMS_PATH = "data/config/terms.json"
import customtkinter as ctk
import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ui.start_screen import StartScreen
from ui.profile_form import ProfileForm
from ui.recording_screen import RecordingScreen
from ui.data_visualization import DataVisualization
from ui.terms_screen import TermsAndConditionsScreen
from utils.data_utils import is_profile_complete
from ui.paths import TERMS_PATH  # Ahora sí toma de paths.py

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sleep Apnea Detection System")
        self.geometry("800x600")
        self.minsize(600, 400)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # Determinar cuál pantalla mostrar primero
        if not self.is_terms_accepted():
            self.show_frame("TermsAndConditionsScreen")
        elif not is_profile_complete():
            self.show_frame("ProfileForm")
        else:
            self.show_frame("StartScreen")

        self.after(0, self.center_window)

    def is_terms_accepted(self):
        """Verifica si el usuario ya aceptó los términos y condiciones."""
        try:
            if not os.path.exists(TERMS_PATH):
                os.makedirs(os.path.dirname(TERMS_PATH), exist_ok=True)
                with open(TERMS_PATH, "w") as f:
                    json.dump({"accepted": False}, f, indent=4)
                return False
            with open(TERMS_PATH, "r") as f:
                data = json.load(f)
                return data.get("accepted", False)
        except Exception as e:
            print(f"Error loading JSON for terms: {e}")
            return False

    def show_frame(self, container):
        """Muestra una pantalla específica, creándola si es necesario."""
        if container not in self.frames:
            if container == "StartScreen":
                frame = StartScreen(self)
            elif container == "ProfileForm":
                frame = ProfileForm(self)
            elif container == "RecordingScreen":
                frame = RecordingScreen(self)
            elif container == "DataVisualization":
                frame = DataVisualization(self)
            elif container == "TermsAndConditionsScreen":
                frame = TermsAndConditionsScreen(self, on_accept_callback=self.on_terms_accepted)
            else:
                raise ValueError(f"Unknown frame: {container}")

            self.frames[container] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        frame = self.frames[container]
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show()

    def on_terms_accepted(self):
        """Callback que se llama cuando el usuario acepta los términos."""
        if not is_profile_complete():
            self.show_frame("ProfileForm")
        else:
            self.show_frame("StartScreen")

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    app = App()
    app.mainloop()

