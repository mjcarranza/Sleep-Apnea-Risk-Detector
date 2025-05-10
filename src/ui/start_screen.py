import customtkinter as ctk

class StartScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.configure(fg_color="#1E1E2F")  # Fondo oscuro

        # Layout principal
        self.grid_rowconfigure((0, 2, 4), weight=1)  # Espacios arriba y abajo
        self.grid_rowconfigure(1, weight=0)  # Botón central
        self.grid_rowconfigure(3, weight=0)  # Botones secundarios
        self.grid_columnconfigure(0, weight=1)

        # Título
        self.title = ctk.CTkLabel(
            self,
            text="Sleep Apnea Detection System",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#CFCFFF"
        )
        self.title.grid(row=0, column=0, pady=(40, 10))

        # Botón principal
        self.record_button = ctk.CTkButton(
            self,
            text="Record Sleep\nSession",
            font=ctk.CTkFont(size=20, weight="bold"),
            width=200,
            height=120,
            fg_color="green",
            hover_color="#009900",
            text_color="white",
            corner_radius=20,
            command=lambda: self.parent.show_frame("RecordingScreen")
        )
        self.record_button.grid(row=1, column=0, pady=10)

        # Separador visual
        self.separator = ctk.CTkLabel(self, text="", height=2)
        self.separator.grid(row=2, column=0)

        # Frame inferior con botones
        self.button_frame = ctk.CTkFrame(
            self,
            fg_color="#2C2C3E",
            corner_radius=15
        )
        self.button_frame.grid(row=3, column=0, pady=(10, 40), padx=20)

        # Botones secundarios
        self.history_button = ctk.CTkButton(
            self.button_frame,
            text="🕒  History",
            font=ctk.CTkFont(size=16),
            width=140,
            height=40,
            fg_color="#44445A",
            hover_color="#5A5A75",
            corner_radius=12
        )
        self.history_button.grid(row=0, column=0, padx=10, pady=10)

        self.profile_button = ctk.CTkButton(
            self.button_frame,
            text="👤  Profile",
            font=ctk.CTkFont(size=16),
            width=140,
            height=40,
            fg_color="#44445A",
            hover_color="#5A5A75",
            corner_radius=12,
            command=lambda: self.parent.show_frame("ProfileForm")
        )
        self.profile_button.grid(row=0, column=1, padx=10, pady=10)
