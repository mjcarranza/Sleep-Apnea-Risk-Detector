import customtkinter as ctk
import json
import os
from ui.paths import TERMS_PATH

'''
This is a class for a window in the application that is going to show the terms and conditions of using the application
'''
class TermsAndConditionsScreen(ctk.CTkFrame):
    def __init__(self, parent, on_accept_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.on_accept_callback = on_accept_callback

        # window configuration
        self.configure(fg_color="#2b2b2b")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(self, text="Terms and Conditions",
                                   font=ctk.CTkFont(size=24, weight="bold"),
                                   text_color="white")
        title_label.grid(row=0, column=0, pady=10, sticky="n")

        # Terms and contions' text
        terms_text = (
            "By using this application, you agree to the following terms and conditions.\n"
            "\n"
            "1. Acceptance of Terms\n"
            "By using this application, you agree to be bound by these Terms and Conditions. "
            "If you do not agree with any part of these terms, you must not use this application.\n"
            "\n"
            "2. Purpose of the Application\n"
            "This application is intended solely for the collection and analysis of data related to breathing, "
            "snoring, and sleeping posture in order to assist in the early detection of possible obstructive sleep apnea events. "
            "The results provided are for informational purposes only and do not constitute a final medical diagnosis.\n"
            "\n"
            "3. Data Collected\n"
            "During the use of the application, the following personal and physiological data may be collected to deliver a better diagnose:\n"
            "- Name and age\n"
            "- Gender\n"
            "- Body Mass Index (BMI)\n"
            "- Neck circumference\n"
            "- Audio recordings of breathing and snoring during sleep\n"
            "- Images captured by the camera to estimate body posture during sleep\n"
            "\n"
            "4. Use of Data\n"
            "The collected data will be used exclusively for the following purposes:\n"
            "- Processing and analysis through artificial intelligence algorithms\n"
            "- Detection of apnea events and identification of sleeping posture\n"
            "- Generation of individual reports and personalized recommendations\n"
            "- Improving the accuracy of the analysis models within the local application context\n" # may not be ok
            "\n"
            "The images captured for posture detection are processed locally on the device "
            "to extract body joint positions (key points) and are not transmitted, shared, or stored externally. "
            "These images remain exclusively on the user's device and are not used by the application beyond the extraction of body joints for posture prediction.\n"
            "\n"
            "5. Data Security\n"
            "Reasonable measures will be taken to protect the data stored on the device. "
            "However, the user is responsible for the physical security of their device and for controlling access to it.\n"
            "\n"
            "6. Limitation of Liability\n"
            "The application provides indicative results based on the analysis of audio, image, and physiological data, "
            "but it does not replace professional medical consultation, diagnosis, or treatment. "
            "The developer assumes no responsibility for health-related decisions made solely based on the application's results, since they are for informative purposes only.\n"
            "\n"
            "7. Copyright\n"
            "The application, its source code, interface, and functionalities are the property of the developer and are protected by copyright laws. "
            "Unauthorized copying, distribution, or modification is prohibited.\n"
            "\n"
            "8. Changes to Terms\n"
            "The developer reserves the right to modify these terms at any time. "
            "Updates will be notified within the application.\n"
        )


        # Text box
        self.text_box = ctk.CTkTextbox(self, wrap="word", fg_color="#3a3a3a",
                                       text_color="white", font=ctk.CTkFont(size=14))
        self.text_box.insert("1.0", terms_text)
        self.text_box.configure(state="disabled")
        self.text_box.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # Button frame
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=2, column=0, pady=10)

        # Accept button
        accept_button = ctk.CTkButton(button_frame, text="Accept", command=self.accept_terms,
                                      fg_color="#7b4fff", hover_color="#a175ff", width=120)
        accept_button.grid(row=0, column=0, padx=10)

        # Decline button
        decline_button = ctk.CTkButton(button_frame, text="Decline", command=self.decline_terms,
                                       fg_color="#555555", hover_color="#777777", width=120)
        decline_button.grid(row=0, column=1, padx=10)

        self.bind("<Configure>", self.on_resize)  # Bind resize event

    '''
    Adjust textbox size when the window resizes.
    '''
    def on_resize(self, event):
        new_width = event.width - 40  # Margin compensation
        new_height = event.height - 200  # Leave room for title and buttons
        if new_width > 300 and new_height > 200:
            self.text_box.configure(width=new_width, height=new_height)

    '''
    Call next window in case terms and contions are accepted
    '''
    def accept_terms(self):
        self.save_terms_status(True)
        if self.on_accept_callback:
            self.on_accept_callback()

    '''
    Close full application in case the terms and conditios are declined
    '''
    def decline_terms(self):
        self.parent.destroy()

    '''
    Funtion saves the state of 'Accepted' for terms and conditions in a JSON file'''
    @staticmethod
    def save_terms_status(status):
        os.makedirs(os.path.dirname(TERMS_PATH), exist_ok=True)
        with open(TERMS_PATH, "w") as file:
            json.dump({"accepted": status}, file, indent=4)
        print(f"Terms saved as: {status} in {TERMS_PATH}")
