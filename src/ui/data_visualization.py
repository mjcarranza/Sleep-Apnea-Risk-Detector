import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox as messagebox
import pandas as pd
import json
import os
import wave
import subprocess
import simpleaudio as sa
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.reportGeneration.reportGenerator import generate_report, generate_full_report
from src.utils.data_utils import read_session_summary, delete_session_json, format_duration
import numpy as np
import shutil

# Paths to JSON, CSV, and audio data
JSON_PATH = "data/patientData/patient_data.json"
CSV_PATH = "data/processed/processed_patient_data.csv"
AUDIO_FOLDER = "data/raw"
SUMMARIES_DIR = "data/summaries"

# Mapa de claves JSON a nombres descriptivos
DATA_LABELS = {
    "eventsAOS": "Apnea events detected",
    "duration": "Total duration of apneas (s)",
    "Supine": "Supine postures detected",
    "Lateral": "Lateral postures detected",
    "Prone": "Prone postures detected",
    "Fetal": "Fetal postures detected"
}

"""
Window frame to visualize patient data and sleep history.
"""
class DataVisualization(ctk.CTkFrame):

    """
    Initialize frame, setup scrollable canvas and load data.
    """
    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color="#1E1E2F")

        # Main container frame
        self.main_container = ctk.CTkFrame(self, fg_color="#1E1E2F")
        self.main_container.pack(fill="both", expand=True)

        # Canvas for scrollable content
        self.canvas = tk.Canvas(self.main_container, bg="#1E1E2F", highlightthickness=0)
        self.scrollbar = ctk.CTkScrollbar(self.main_container, orientation="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Frame inside the canvas
        self.scrollable_frame = ctk.CTkFrame(self.canvas, fg_color="#1E1E2F")
        self.window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Bind events for scroll behavior
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

        # 'Main Menu' button
        self.bottom_button = ctk.CTkButton(
            self,
            text="Main Menu",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#3A3A55",
            hover_color="#5A5A75",
            text_color="white",
            corner_radius=10,
            command=self.on_back_button_click
        )
        self.bottom_button.pack(side="bottom", pady=10)

        self.current_play_obj = None  # Current audio playback object
        self.current_button = None   # Button currently controlling audio

        # Title label
        self.title_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Sleep History",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#CFCFFF"
        )
        self.title_label.pack(pady=(30, 20))

        self.load_patient_info()    # Load patient info section
        self.load_sleep_sessions()  # Load sleep sessions section

    """
    Update scroll region when frame size changes.
    """
    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    """
    Resize canvas window to match canvas size.
    """
    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.window, width=event.width)

    """
    Handle mouse wheel scrolling.
    """
    def _on_mousewheel(self, event):
        direction = 0
        if event.num == 5 or event.delta == -120:
            direction = 1
        elif event.num == 4 or event.delta == 120:
            direction = -1
        self.canvas.yview_scroll(direction, "units")

    """
    Navigate back to StartScreen.
    """
    def on_back_button_click(self):
        self.master.show_frame("StartScreen")

    """
    Load and display patient demographic data from JSON.
    """
    def load_patient_info(self):
        if not os.path.exists(JSON_PATH):
            return

        with open(JSON_PATH, "r") as file:
            data = json.load(file)["patient"]

        # Patient info frame
        info_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="#2C2C3E", corner_radius=15)
        info_frame.pack(fill="x", padx=20, pady=10)

        # Display patient data fields
        patient_info = [
            f"Name: {data.get('name', 'N/A')}",
            f"Age: {data.get('age', 'N/A')}",
            f"Sex: {data.get('sex', 'N/A')}",
            f"Weight: {data.get('weight_(kg)', 'N/A')}",
            f"Height: {data.get('height_(cm)', 'N/A')}",
            f"BMI: {data.get('bmi', 'N/A')}",
            f"Neck Circumference: {data.get('neck_circumference_(cm)', 'N/A')} cm",
            f"Alcohol use: {data.get('regular_alcohol_use', 'N/A')}",
            f"Sleep Difficulties: {data.get('regular_sleep_difficulties', 'N/A')}",
            f"Familiar Apnea History: {data.get('familiar_apnea_history', 'N/A')}"
        ]

        for info in patient_info:
            label = ctk.CTkLabel(info_frame, text=info, font=ctk.CTkFont(size=16), text_color="white", anchor="w")
            label.pack(fill="x", padx=10, pady=4)

        # Button to generate full report
        generate_report_button = ctk.CTkButton(
            info_frame,
            text="Generate Full Report",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#4A4A6A",
            hover_color="#6A6A8A",
            text_color="white",
            corner_radius=12,
            command=generate_full_report
        )
        generate_report_button.pack(pady=(10, 5))

    '''
    Create resume table
    '''
    def create_summary_table(self, parent_frame, session_summary, data_labels):
        table_container = ctk.CTkFrame(parent_frame, fg_color="transparent")
        table_container.pack(pady=(5, 20))
        
        table_frame = ctk.CTkFrame(table_container, fg_color="#1E1E2F", corner_radius=8)
        table_frame.grid(row=0, column=0)

        headers = ["Data", "Value"]
        header_font = ctk.CTkFont(size=20, weight="bold")
        cell_font = ctk.CTkFont(size=20)

        # Table headers
        for i, header in enumerate(headers):
            ctk.CTkLabel(
                table_frame, text=header, font=header_font, text_color="white"
            ).grid(row=0, column=i, padx=10, pady=6)

        # Table rows
        for row_idx, key in enumerate(data_labels.keys(), start=1):
            descriptive_name = data_labels[key]
            value = session_summary.get(key, 0)

            # ✅ Si es duración, convertir a HH:MM:SS
            if key.lower() == "duration":
                value = format_duration(int(value))

            ctk.CTkLabel(
                table_frame, text=descriptive_name, font=cell_font, text_color="white"
            ).grid(row=row_idx, column=0, padx=10, pady=4)

            ctk.CTkLabel(
                table_frame, text=str(value), font=cell_font, text_color="white"
            ).grid(row=row_idx, column=1, padx=10, pady=4)


    '''
    Load all sessions
    '''
    def load_sleep_sessions(self):
        # List JSON files and extract session numbers
        json_files = [f for f in os.listdir(SUMMARIES_DIR) if f.endswith(".json")]
        session_ids = sorted([int(f.replace("session_", "").replace(".json", "")) for f in json_files])

        for session_id in session_ids:
            # Create session's frame 
            session_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="#2C2C3E", corner_radius=15)
            session_frame.pack(fill="x", padx=20, pady=15)

            # Header frame
            header_frame = ctk.CTkFrame(session_frame, fg_color="transparent")
            header_frame.pack(fill="x", padx=10, pady=(10, 5))

            # Session title
            session_title = ctk.CTkLabel(
                header_frame,
                text=f"Session {session_id}",
                font=ctk.CTkFont(size=30, weight="bold"),
                text_color="#FFFFFF"
            )
            session_title.pack(side="left")

            stats_title = ctk.CTkLabel(
                session_frame,
                text="Session Statistics",
                font=ctk.CTkFont(size=22, weight="bold"),
                text_color="white"
            )
            stats_title.pack(pady=(10, 5))

            # Read session's resume
            session_summary = read_session_summary(session_id)
            if session_summary:
                # Create table for resume
                self.create_summary_table(session_frame, session_summary, DATA_LABELS)

            # Container for buttons
            button_container = ctk.CTkFrame(session_frame, fg_color="transparent")
            button_container.pack(pady=(5, 10))

            # Delete session
            delete_button = ctk.CTkButton(
                button_container,
                text="Delete Session",
                font=ctk.CTkFont(size=18),
                fg_color="red",
                hover_color="#cc0000",
                text_color="white",
                corner_radius=8,
                width=140,
                command=lambda sid=session_id: self.delete_session(sid)
            )
            delete_button.pack(side="right", padx=10)

            # Generate PDF
            report_button = ctk.CTkButton(
                button_container,
                text="Generate PDF Report",
                font=ctk.CTkFont(size=18),
                fg_color="green",
                hover_color="#009900",
                text_color="white",
                corner_radius=8,
                width=140,
                command=lambda sid=session_id: generate_report(sid)
            )
            report_button.pack(side="right")

            # See Images
            see_images_button = ctk.CTkButton(
                button_container,
                text="See Images",
                font=ctk.CTkFont(size=18),
                fg_color="#4a90e2",
                hover_color="#357ABD",
                text_color="white",
                corner_radius=8,
                width=140,
                command=lambda sid=session_id: self.open_session_images(sid)
            )
            see_images_button.pack(side="right", padx=10)

            # Open audio location
            audio_path = os.path.join(AUDIO_FOLDER, f"Session{session_id}", "audio.wav")
            if os.path.exists(audio_path):
                play_button_2 = ctk.CTkButton(
                    button_container,
                    text="Open Audio Location",
                    font=ctk.CTkFont(size=18),
                    width=180,
                    fg_color="#7b4fff",
                    hover_color="#a175ff",
                    text_color="white",
                    corner_radius=10,
                    command=lambda sid=session_id: self.openSessionFolder(sid)
                )
                play_button_2.pack(side="left", padx=5)


    """
    Read CSV file
    """
    def readCSV():
        # read CSV file
        if not os.path.exists(CSV_PATH):
            return
        
        df = pd.read_csv(CSV_PATH)
        df["Session"] = df.groupby((df['Start_Time'] == 0).cumsum()).ngroup() + 1
        return df
    
    """
    Opens the folder for the captured images.
    """
    def open_session_images(self, session_id):
        session_dir = os.path.join(AUDIO_FOLDER, f"Session{session_id}","Images")
        if os.path.exists(session_dir):
            try:
                subprocess.Popen(["xdg-open", session_dir])
            except Exception as e:
                messagebox.showerror("Error", f"Could not open folder:\n{e}")
        else:
            messagebox.showinfo("Info", "The requested folder does not exist.")

    """
    Opens the folder for the recorded audio.
    """
    def openSessionFolder(self, session_id):
        session_dir = os.path.join(AUDIO_FOLDER, f"Session{session_id}")
        if os.path.exists(session_dir):
            try:
                subprocess.Popen(["xdg-open", session_dir])
            except Exception as e:
                messagebox.showerror("Error", f"Could not open the containing folder:\n{e}")
        else:
            messagebox.showinfo("Info", "The requested folder does not exist.")

    """
    Delete session data and audio files.
    """
    def delete_session(self, session_id):
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Session {session_id}?")
        if not confirm:
            return

        try:
            # Remove session from CSV
            df = pd.read_csv(CSV_PATH)
            df["Session"] = df.groupby((df['Start_Time'] == 0).cumsum()).ngroup() + 1
            df = df[df["Session"] != session_id]
            df.drop(columns=["Session"], inplace=True)
            df.to_csv(CSV_PATH, index=False)

            # Remove session audio folder
            session_audio_folder = os.path.join(AUDIO_FOLDER, f"Session{session_id}")
            if os.path.exists(session_audio_folder):
                shutil.rmtree(session_audio_folder)

            # Remove Json File
            delete_session_json(session_id)

            messagebox.showinfo("Deleted", f"Session {session_id} has been deleted.")
            self.on_show()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete session: {e}")

    """
    Reload the view when the screen is shown again.
    """
    def on_show(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.title_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Sleep History",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#CFCFFF"
        )
        self.title_label.pack(pady=(30, 20))

        self.load_patient_info()
        self.load_sleep_sessions()
