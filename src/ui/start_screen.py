import customtkinter as ctk

class StartScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # Configurar el layout general
        self.grid_rowconfigure((0, 2), weight=1)  # Espacio arriba y abajo del botón
        self.grid_rowconfigure(1, weight=0)       # Fila del botón
        self.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(self, text="Welcome to the Sleep Apnea Detection System", font=("Arial", 20))
        title.grid(row=0, column=0, pady=20, sticky="n")

        self.record_button = ctk.CTkButton(
            self,
            text="Record New\nSleep Session",
            text_color="white",
            fg_color="green",
            hover_color="#009900",
            font=ctk.CTkFont(size=20, weight="bold"),
            width=150,
            height=130,
            corner_radius=30,
            command=lambda: self.parent.show_frame("RecordingScreen")
        )
        self.record_button.grid(row=1, column=0, pady=20)

        # Botones extra
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=3, column=0, pady=20)

        #ctk.CTkButton(button_frame, text="Start Recording Session").grid(row=0, column=0, padx=10)
        ctk.CTkButton(button_frame, text="View Session History").grid(row=0, column=1, padx=10)
        ctk.CTkButton(button_frame, text="Access User Profile", command=lambda: self.parent.show_frame("ProfileForm")).grid(row=0, column=2, padx=10)
