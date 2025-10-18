"""
MAIN FILE OF THE APLICATION.
AUTHOR: MARIO JESUS CARRANZA CASTILLO
INSTITUTION: TECNOLOGICO DE COSTA RICA (TEC)
FINAL WORK FOR THE DEGREE OF LIC. EN INGENIERIA EN COMPUTADORES
II SEMESTER 2025
"""

import sys
import os
import json
import customtkinter as ctk
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.ui.start_screen import StartScreen
from src.ui.profile_form import ProfileForm
from src.ui.recording_screen import RecordingScreen
from src.ui.data_visualization import DataVisualization
from src.ui.terms_screen import TermsAndConditionsScreen
from src.utils.data_utils import is_profile_complete
from src.ui.paths import TERMS_PATH


"""
This is the main method of the application
"""
class App(ctk.CTk):
    # Window configuration
    def __init__(self):
        super().__init__()
        self.title("Sleep Apnea Detection System")
        self.geometry("800x600")
        self.minsize(600, 400)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # Determines what window to show first
        if not self.is_terms_accepted():
            self.show_frame("TermsAndConditionsScreen")
        elif not is_profile_complete():
            self.show_frame("ProfileForm")
        else:
            self.show_frame("StartScreen")

        self.after(0, self.center_window)

    """
    Verifies if the user already accepted terms and conditions.
    """
    def is_terms_accepted(self):
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

    """
    Shows a specific window creating it if necessary.
    """
    def show_frame(self, container):
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


    """
    Callback that is called when user accept terms and coditions.
    """
    def on_terms_accepted(self):
        if not is_profile_complete():
            self.show_frame("ProfileForm")
        else:
            self.show_frame("StartScreen")

    """
    Centers the window on the screen
    """
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

