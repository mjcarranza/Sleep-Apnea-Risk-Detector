import customtkinter as ctk

class CustomMessageBox(ctk.CTkToplevel):
    def __init__(self, parent, title="Message", message="", on_ok=None):
        super().__init__(parent)

        self.on_ok_callback = on_ok  # Nueva línea: almacena la función callback

        self.title(title)
        self.geometry("300x150")
        self.configure(fg_color="#2b2b2b")
        self.resizable(False, False)

        # Centrar respecto a la ventana principal
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - 150
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - 75
        self.geometry(f"+{x}+{y}")

        # Hacer que esta ventana bloquee la principal
        self.grab_set()
        self.focus()

        # Label
        self.label = ctk.CTkLabel(self, text=message, font=ctk.CTkFont(size=25), wraplength=260, justify="center")
        self.label.place(relx=0.5, rely=0.35, anchor="center")

        # Botón OK
        self.ok_button = ctk.CTkButton(self, text="OK", command=self._on_ok)
        self.ok_button.place(relx=0.5, rely=0.75, anchor="center")

        self.protocol("WM_DELETE_WINDOW", self._on_ok)

    def _on_ok(self):
        if self.on_ok_callback:   # Si se pasó un callback
            self.on_ok_callback() # Llama al callback
        self.grab_release()
        self.destroy()
