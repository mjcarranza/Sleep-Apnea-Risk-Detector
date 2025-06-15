import customtkinter as ctk

class CustomTwoButtonMessageBox(ctk.CTkToplevel):
    def __init__(self, parent, title="Message", message="", on_accept=None, on_cancel=None):
        super().__init__(parent)

        self.on_accept_callback = on_accept  # Callback para botón Accept
        self.on_cancel_callback = on_cancel  # Callback para botón Cancel

        self.title(title)
        self.geometry("300x150")
        self.configure(fg_color="#2b2b2b")
        self.resizable(False, False)

        # Centrar respecto a la ventana principal
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - 150
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - 75
        self.geometry(f"+{x}+{y}")

        # Bloquea la ventana principal
        self.grab_set()
        self.focus()

        # Mensaje
        self.label = ctk.CTkLabel(self, text=message, font=ctk.CTkFont(size=20), wraplength=260, justify="center")
        self.label.place(relx=0.5, rely=0.35, anchor="center")

        # Botón Accept
        self.accept_button = ctk.CTkButton(self, text="Accept", command=self._on_accept)
        self.accept_button.place(relx=0.25, rely=0.75, anchor="center")  # más a la izquierda

        # Botón Cancel
        self.cancel_button = ctk.CTkButton(self, text="Cancel", command=self._on_cancel)
        self.cancel_button.place(relx=0.75, rely=0.75, anchor="center")  # más a la derecha

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)  # Al cerrar con la X se llama cancel

    def _on_accept(self):
        if self.on_accept_callback:
            self.on_accept_callback()  # Ejecuta callback si existe
        self.grab_release()
        self.destroy()

    def _on_cancel(self):
        self.grab_release()
        self.destroy()
