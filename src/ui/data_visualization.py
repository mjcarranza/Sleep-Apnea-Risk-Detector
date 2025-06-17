import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox as messagebox
import pandas as pd
import json
import os
import wave
import simpleaudio as sa
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from reportGeneration.reportGenerator import generate_report, generate_full_report
import numpy as np
import shutil

JSON_PATH = "data/patientData/patient_data.json"
CSV_PATH = "data/processed/processed_patient_data.csv"
AUDIO_FOLDER = "data/raw"

class DataVisualization(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color="#1E1E2F")

        self.main_container = ctk.CTkFrame(self, fg_color="#1E1E2F")
        self.main_container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.main_container, bg="#1E1E2F", highlightthickness=0)
        self.scrollbar = ctk.CTkScrollbar(self.main_container, orientation="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.scrollable_frame = ctk.CTkFrame(self.canvas, fg_color="#1E1E2F")
        self.window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

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

        self.current_play_obj = None
        self.current_button = None

        self.title_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Sleep History",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#CFCFFF"
        )
        self.title_label.pack(pady=(30, 20))

        self.load_patient_info()
        self.load_sleep_sessions()

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.window, width=event.width)

    def _on_mousewheel(self, event):
        direction = 0
        if event.num == 5 or event.delta == -120:
            direction = 1
        elif event.num == 4 or event.delta == 120:
            direction = -1
        self.canvas.yview_scroll(direction, "units")

    def on_back_button_click(self):
        self.master.show_frame("StartScreen")

    def load_patient_info(self):
        if not os.path.exists(JSON_PATH):
            return

        with open(JSON_PATH, "r") as file:
            data = json.load(file)["patient"]

        info_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="#2C2C3E", corner_radius=15)
        info_frame.pack(fill="x", padx=20, pady=10)

        patient_info = [
            f"Name: {data.get('name', 'N/A')}",
            f"Age: {data.get('age', 'N/A')}",
            f"Sex: {data.get('sex', 'N/A')}",
            f"BMI: {data.get('bmi', 'N/A')}",
            f"Neck Circumference: {data.get('neck_circumference_(cm)', 'N/A')} cm"
        ]

        for info in patient_info:
            label = ctk.CTkLabel(info_frame, text=info, font=ctk.CTkFont(size=16), text_color="white", anchor="w")
            label.pack(fill="x", padx=10, pady=4)

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

    def load_sleep_sessions(self):
        if not os.path.exists(CSV_PATH):
            return

        df = pd.read_csv(CSV_PATH)
        df["Session"] = df.groupby((df['Start_Time'] == 0).cumsum()).ngroup() + 1

        for session_id, session_df in df.groupby("Session"):
            session_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="#2C2C3E", corner_radius=15)
            session_frame.pack(fill="x", padx=20, pady=15)

            header_frame = ctk.CTkFrame(session_frame, fg_color="transparent")
            header_frame.pack(fill="x", padx=10, pady=(10, 5))

            session_title = ctk.CTkLabel(
                header_frame,
                text=f"Session {session_id}",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="#FFFFFF"
            )
            session_title.pack(side="left")

            report_button = ctk.CTkButton(
                header_frame,
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

            delete_button = ctk.CTkButton(
                header_frame,
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

            apnea_events = session_df[session_df['Has_Apnea'] == True]

            if not apnea_events.empty:
                title_label = ctk.CTkLabel(
                    session_frame,
                    text="Apnea Events Detected",
                    font=ctk.CTkFont(size=15, weight="bold"),
                    text_color="white"
                )
                title_label.pack(pady=(10, 5))

                table_container = ctk.CTkFrame(session_frame, fg_color="transparent")
                table_container.pack(pady=(5, 20))

                table_frame = ctk.CTkFrame(table_container, fg_color="#1E1E2F", corner_radius=8)
                table_frame.grid(row=0, column=0)

                headers = ["Start Time (s)", "End Time (s)", "Snoring", "Treatment Required"]
                header_font = ctk.CTkFont(size=14, weight="bold")
                cell_font = ctk.CTkFont(size=13)

                for i, header in enumerate(headers):
                    header_label = ctk.CTkLabel(table_frame, text=header, font=header_font, text_color="white")
                    header_label.grid(row=0, column=i, padx=10, pady=6)

                for row_idx, (_, row) in enumerate(apnea_events.iterrows(), start=1):
                    values = [
                        f"{row['Start_Time']:.2f}",
                        f"{row['End_Time']:.2f}",
                        "Yes" if row['Snoring'] else "No",
                        "Yes" if row['Treatment_Required'] else "No"
                    ]
                    for col_idx, value in enumerate(values):
                        value_label = ctk.CTkLabel(table_frame, text=value, font=cell_font, text_color="white")
                        value_label.grid(row=row_idx, column=col_idx, padx=10, pady=4)
            else:
                no_apnea_label = ctk.CTkLabel(
                    session_frame,
                    text="No Apnea Events Detected",
                    font=ctk.CTkFont(size=15, weight="bold"),
                    text_color="#BBBBBB"
                )
                no_apnea_label.pack(pady=(10, 5))

            audio_path = os.path.join(AUDIO_FOLDER, f"Session{session_id}", "audio.wav")
            if os.path.exists(audio_path):
                try:
                    with wave.open(audio_path, 'rb') as wf:
                        framerate = wf.getframerate()
                        n_frames = wf.getnframes()
                        audio_signal = wf.readframes(n_frames)

                    audio_data = np.frombuffer(audio_signal, dtype=np.int16)
                    duration = n_frames / framerate
                    time_axis = np.linspace(0, duration, num=len(audio_data))

                    fig_wave, ax_wave = plt.subplots(figsize=(5, 1.5), dpi=100)
                    ax_wave.plot(time_axis, audio_data, color='white', linewidth=0.5)
                    ax_wave.set_xlim(0, duration)
                    ax_wave.set_ylim(-max(abs(audio_data)) * 1.1, max(abs(audio_data)) * 1.1)
                    ax_wave.set_facecolor("#1E1E2F")
                    fig_wave.patch.set_facecolor('#1E1E2F')
                    ax_wave.axis('off')

                    waveform_container = ctk.CTkFrame(session_frame, corner_radius=8, fg_color="#1E1E2F")
                    waveform_container.pack(fill="x", padx=10, pady=(0, 5))

                    canvas_wave = FigureCanvasTkAgg(fig_wave, master=waveform_container)
                    canvas_wave.draw()
                    canvas_wave.get_tk_widget().pack(fill="both", expand=True)

                    plt.close(fig_wave)

                except Exception as e:
                    print(f"[ERROR] Al procesar el audio: {e}")

                play_button = ctk.CTkButton(
                    session_frame,
                    text="▶ Play",
                    font=ctk.CTkFont(size=18),
                    width=80,
                    fg_color="#7b4fff",
                    hover_color="#a175ff",
                    text_color="white",
                    corner_radius=10,
                    command=lambda p=audio_path, b=None: self.toggle_audio(p, b)
                )
                play_button.configure(command=lambda p=audio_path, b=play_button: self.toggle_audio(p, b))
                play_button.pack(pady=(5, 10))

    def toggle_audio(self, path, button):
        if self.current_play_obj and self.current_play_obj.is_playing():
            self.current_play_obj.stop()
            if self.current_button:
                self.current_button.configure(
                    text="▶ Play",
                    command=lambda p=path, b=self.current_button: self.toggle_audio(p, b)
                )
            self.current_play_obj = None
            self.current_button = None
            return

        try:
            wave_obj = sa.WaveObject.from_wave_file(path)
            play_obj = wave_obj.play()

            self.current_play_obj = play_obj
            self.current_button = button

            button.configure(
                text="■ Stop",
                command=lambda p=path, b=button: self.toggle_audio(p, b)
            )

            self.after(100, self._check_audio_finished)
        except Exception as e:
            print(f"[ERROR] No se pudo reproducir el audio: {e}")

    def _check_audio_finished(self):
        if self.current_play_obj and not self.current_play_obj.is_playing():
            if self.current_button:
                self.current_button.configure(
                    text="▶ Play",
                    command=lambda p=self.current_button.cget("command"), b=self.current_button: self.toggle_audio(p, b)
                )
            self.current_play_obj = None
            self.current_button = None
        else:
            self.after(100, self._check_audio_finished)

    def delete_session(self, session_id):
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Session {session_id}?")
        if not confirm:
            return

        try:
            df = pd.read_csv(CSV_PATH)
            df["Session"] = df.groupby((df['Start_Time'] == 0).cumsum()).ngroup() + 1
            df = df[df["Session"] != session_id]
            df.drop(columns=["Session"], inplace=True)
            df.to_csv(CSV_PATH, index=False)

            session_audio_folder = os.path.join(AUDIO_FOLDER, f"Session{session_id}")
            if os.path.exists(session_audio_folder):
                shutil.rmtree(session_audio_folder)

            messagebox.showinfo("Deleted", f"Session {session_id} has been deleted.")
            self.on_show()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete session: {e}")

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
