from tkinter import messagebox
from PIL import Image
import customtkinter as ctk
from utils.data_utils import save_patient_data, load_patient_data, is_profile_complete
from utils.custom_messagebox import CustomMessageBox

ICON_PATH = "assets/user_profile_icon.png"

class ProfileForm(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.fields = {}
        self.field_keys = {
            "Name": "name",
            "Age": "age",
            "Sex": "sex",
            "Weight (kg)": "weight_(kg)",
            "Height (cm)": "height_(cm)",
            "BMI": "bmi",
            "Neck Circumference (cm)": "neck_circumference_(cm)",
            "Regular Alcohol Use": "regular_alcohol_use",
            "Regular Sleep Difficulties": "regular_sleep_difficulties",
            "Familiar Apnea History": "familiar_apnea_history"
        }
        self.is_editing = False

        self.configure(fg_color="#1e1e2f")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(pady=20)

        try:
            icon = Image.open(ICON_PATH)
            icon = icon.resize((25, 25), Image.Resampling.LANCZOS)
            icon_tk = ctk.CTkImage(light_image=icon, dark_image=icon)
            self.profile_icon_label = ctk.CTkLabel(
                title_frame,
                text=" User Profile",
                image=icon_tk,
                compound="left",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="white"
            )
            self.profile_icon_label.pack()
        except Exception as e:
            print(f"Error loading icon: {e}")
            self.profile_icon_label = ctk.CTkLabel(
                title_frame,
                text="User Profile",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="white"
            )
            self.profile_icon_label.pack()

        form_frame = ctk.CTkFrame(self, fg_color="#2a2a3d", corner_radius=15)
        form_frame.pack(padx=40, pady=20, fill="both", expand=True)

        for label in self.field_keys.keys():
            row = ctk.CTkFrame(form_frame, fg_color="transparent")
            row.pack(fill="x", pady=5)

            label_widget = ctk.CTkLabel(
                row,
                text=label + ":",
                width=180,
                anchor="w",
                text_color="white",
                font=ctk.CTkFont(size=16)
            )
            label_widget.pack(side="left")

            if label == "Sex":
                entry = ctk.CTkOptionMenu(
                    row,
                    values=["Select an option", "Male", "Female", "Other"],
                    fg_color="#3a3a50",
                    text_color="white",
                    button_color="#7b4fff",
                    dropdown_fg_color="#3a3a50",
                    dropdown_text_color="white",
                    dropdown_hover_color="#4f4f7a"
                )
                entry.set("Select an option")
            elif label in ["Regular Alcohol Use", "Regular Sleep Difficulties", "Familiar Apnea History"]:
                entry = ctk.CTkOptionMenu(
                    row,
                    values=["Select an option", "True", "False"],
                    fg_color="#3a3a50",
                    text_color="white",
                    button_color="#7b4fff",
                    dropdown_fg_color="#3a3a50",
                    dropdown_text_color="white",
                    dropdown_hover_color="#4f4f7a"
                )
                entry.set("Select an option")
            else:
                entry = ctk.CTkEntry(
                    row,
                    fg_color="#3a3a50",
                    text_color="white",
                    placeholder_text="Enter value",
                    border_color="#7b4fff",
                    border_width=1
                )

            entry.pack(side="left", fill="x", expand=True, padx=5)
            if label in ["Weight (kg)", "Height (cm)"]:
                entry.bind("<KeyRelease>", lambda event: self.update_bmi())
            self.fields[label] = entry

        self.buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.buttons_frame.pack(pady=10)

        self.edit_save_button = ctk.CTkButton(
            self.buttons_frame,
            text="Edit",
            command=self.toggle_edit_save,
            width=200,
            height=50,
            corner_radius=15,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white",
            fg_color="#7b4fff",
            hover_color="#a175ff"
        )
        self.edit_save_button.grid(row=0, column=0, padx=10)

        self.cancel_back_button = ctk.CTkButton(
            self.buttons_frame,
            text="Back to Main Menu",
            command=self.cancel_or_back,
            width=200,
            height=50,
            corner_radius=15,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white",
            fg_color="#555555",
            hover_color="#777777"
        )
        self.cancel_back_button.grid(row=0, column=1, padx=10)
        self.cancel_back_button.grid_remove()

        self.update_profile_label()

    def update_bmi(self, *args):
        try:
            weight = float(self.fields["Weight (kg)"].get())
            height = float(self.fields["Height (cm)"].get())

            if 0 < weight <= 500 and 0 < height <= 300:
                bmi = round(weight / ((height / 100) ** 2), 2)
                self.fields["BMI"].configure(state="normal")
                self.fields["BMI"].delete(0, "end")
                self.fields["BMI"].insert(0, str(bmi))
                self.fields["BMI"].configure(state="disabled")
            else:
                raise ValueError
        except ValueError:
            self.fields["BMI"].configure(state="normal")
            self.fields["BMI"].delete(0, "end")
            self.fields["BMI"].insert(0, "")
            self.fields["BMI"].configure(state="disabled")

    def on_show(self):
        self.load_data_into_form()

        if is_profile_complete():
            self.set_fields_state(disabled=True)
            self.edit_save_button.configure(text="Edit")
            self.cancel_back_button.configure(text="Back to Main Menu")
            self.cancel_back_button.grid()
            self.is_editing = False
        else:
            self.set_fields_state(disabled=False)
            self.edit_save_button.configure(text="Save Data")
            self.cancel_back_button.grid_remove()
            self.is_editing = True

    def load_data_into_form(self):
        data = load_patient_data()
        if not data:
            print("Database is empty. Please enter patient information.")
            return

        for label, entry in self.fields.items():
            key = self.field_keys[label]
            value = data.get(key, "")
            if isinstance(entry, ctk.CTkOptionMenu):
                entry.set(value if value else "Select an option")
            else:
                entry.delete(0, "end")
                entry.insert(0, value)

    def update_profile_label(self):
        patient_data = load_patient_data()
        patient_name = patient_data.get("name", "Unknown User")
        self.profile_icon_label.configure(text=f" {patient_name}")

    def toggle_edit_save(self):
        if not self.is_editing:
            self.set_fields_state(disabled=False)
            self.edit_save_button.configure(text="Save Data")
            self.cancel_back_button.configure(text="Cancel")
            self.is_editing = True
        else:
            data = {}
            for label, widget in self.fields.items():
                key = self.field_keys[label]
                if isinstance(widget, ctk.CTkOptionMenu):
                    value = widget.get()
                    if value == "Select an option":
                        CustomMessageBox(self, title="Input Error", message=f"Please select a valid option for {label}.")
                        return
                    data[key] = value
                else:
                    value = widget.get()
                    if not value.strip():
                        CustomMessageBox(self, title="Input Error", message=f"Please fill in the {label} field.")
                        return
                    if key == "name" and not value.strip():
                        CustomMessageBox(self, title="Input Error", message="Name cannot be empty.")
                        return
                    if key in ["age", "weight_(kg)", "height_(cm)", "neck_circumference_(cm)"]:
                        try:
                            number = float(value)
                        except ValueError:
                            CustomMessageBox(self, title="Input Error", message=f"{label} must be a numeric value.")
                            return
                        if key == "age" and not (0 <= number <= 100):
                            CustomMessageBox(self, title="Input Error", message=f"{label} must be between 0 and 100.")
                            return
                        if key == "weight_(kg)" and not (0 <= number <= 500):
                            CustomMessageBox(self, title="Input Error", message=f"{label} must be between 0 and 500 kg.")
                            return
                        if key == "height_(cm)" and not (0 <= number <= 300):
                            CustomMessageBox(self, title="Input Error", message=f"{label} must be between 0 and 300 cm.")
                            return
                        if key == "neck_circumference_(cm)" and not (0 <= number <= 100):
                            CustomMessageBox(self, title="Input Error", message=f"{label} must be between 0 and 100 cm.")
                            return
                    data[key] = value

            patient_data = load_patient_data()
            recorded_sessions = patient_data.get("recordedSessions", 0)
            data["recordedSessions"] = recorded_sessions

            save_patient_data(data)
            CustomMessageBox(self, title="Success", message="Patient data saved successfully.")

            self.load_data_into_form()
            self.set_fields_state(disabled=True)
            self.edit_save_button.configure(text="Edit")
            self.cancel_back_button.configure(text="Back to Main Menu")
            self.cancel_back_button.grid()
            self.is_editing = False

    def cancel_or_back(self):
        if self.is_editing:
            self.load_data_into_form()
            self.set_fields_state(disabled=True)
            self.edit_save_button.configure(text="Edit")
            self.cancel_back_button.configure(text="Back to Main Menu")
            self.is_editing = False
        else:
            self.parent.show_frame("StartScreen")

    def set_fields_state(self, disabled=True):
        state = "disabled" if disabled else "normal"
        for widget in self.fields.values():
            widget.configure(state=state)

    def update_profile_label(self):
        patient_data = load_patient_data()
        patient_name = patient_data.get("name", "Unknown User")
        self.profile_icon_label.configure(text=f" {patient_name}")

    def load_data_into_form(self):
        data = load_patient_data()
        if not data:
            print("Database is empty. Please enter patient information.")
            return

        for label, entry in self.fields.items():
            key = self.field_keys[label]
            value = data.get(key, "")
            if isinstance(entry, ctk.CTkOptionMenu):
                entry.set(value if value else "Select an option")
            else:
                entry.delete(0, "end")
                entry.insert(0, value)
