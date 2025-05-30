import customtkinter as ctk
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ui.start_screen import StartScreen
from ui.profile_form import ProfileForm
from ui.recording_screen import RecordingScreen
from ui.data_visualization import DataVisualization
from utils.data_utils import is_profile_complete



class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sleep Apnea Detection System")
        self.geometry("800x600")
        self.minsize(600, 400)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartScreen, ProfileForm, RecordingScreen, DataVisualization):
            frame = F(self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartScreen" if is_profile_complete() else "ProfileForm")

        # Centrar después de que la ventana se haya renderizado
        self.after(0, self.center_window)

    def show_frame(self, container):
        frame = self.frames[container]
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show()

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
