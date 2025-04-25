# src/utils/custom_messagebox.py
import customtkinter as ctk

class CustomMessageBox(ctk.CTkToplevel):
    def __init__(self, parent, title="Message", message=""):
        super().__init__(parent)

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

        # Label directamente sobre el Toplevel
        self.label = ctk.CTkLabel(self, text=message, font=ctk.CTkFont(size=25), wraplength=260, justify="center")
        self.label.place(relx=0.5, rely=0.35, anchor="center")

        # Botón directamente sobre el Toplevel
        self.ok_button = ctk.CTkButton(self, text="OK", command=self._on_ok)
        self.ok_button.place(relx=0.5, rely=0.75, anchor="center")

        self.protocol("WM_DELETE_WINDOW", self._on_ok)

    def _on_ok(self):
        self.grab_release()
        self.destroy()
