import tkinter as tk
from tkinter import filedialog
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from recommendation.recommendation_engine import generate_recommendations
import pandas as pd
import json
import os

# Import centralized paths for CSV and JSON data files
from ui.paths import CSV_PATH, JSON_PATH 

# Constants for data paths and output directory
JSON_PATH = "data/patientData/patient_data.json"
CSV_PATH = "data/processed/processed_patient_data.csv"
OUTPUT_DIR = "docs"

"""
Generates a PDF report for a specific sleep session.
Parameters:
    session_number (int): The session number to generate the report for.
"""
def generate_report(session_number):

    # Create output directory if it does not exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Load patient data from JSON file
    with open(JSON_PATH, "r") as f:
        patient_data = json.load(f)["patient"]

    # Load processed session data from CSV
    df = pd.read_csv(CSV_PATH)
    
    # Assign session numbers to data based on 'Start_Time' being zero (start of new segment)
    df["Session"] = df.groupby((df['Start_Time'] == 0).cumsum()).ngroup() + 1

    # Filter the data for the specified session
    session_df = df[df["Session"] == session_number]

    # Define columns to include in the report
    columns_required = ["Start_Time", "End_Time", "Snoring_Intensity", "Snoring",
                        "Nasal_Airflow", "Spectral_Centroid", "Has_Apnea", "Treatment_Required",
                        "Snore_Energy", "Decibel_Level_dB"]

    # Initialize hidden Tkinter root for file dialog
    root = tk.Tk()
    root.withdraw()

    # Open file dialog to specify PDF output path
    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        initialfile=f"Session{session_number}_report.pdf",
        title="Save Report As"
    )

    # Check if the user cancelled the save operation
    if not file_path:
        print("[INFO] Save operation cancelled.")
        return

    # Initialize PDF document
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Add report title and spacing
    elements.append(Paragraph(f"<b>Sleep Apnea Detection System</b>", styles["Title"]))
    elements.append(Spacer(1, 20))

    # Add session heading
    elements.append(Paragraph(f"Patient Report For Sleep Session Number {session_number}", styles["Heading2"]))

    # Add patient information section
    patient_info = f"""
    Name: {patient_data.get("name", "N/A")}<br/>
    Age: {patient_data.get("age", "N/A")}<br/>
    Sex: {patient_data.get("sex", "N/A")}<br/>
    Weight (Kg): {patient_data.get("weight_(kg)", "N/A")}<br/>
    Height (cm): {patient_data.get("height_(cm)", "N/A")}<br/>
    BMI: {patient_data.get("bmi", "N/A")}<br/>
    Neck Circumference: {patient_data.get("neck_circumference_(cm)", "N/A")} cm<br/>
    Regular alcohol use: {patient_data.get("regular_alcohol_use", "N/A")}<br/>
    Regular sleep difficulties: {patient_data.get("regular_sleep_difficulties", "N/A")}<br/>
    Familiar apnea history: {patient_data.get("familiar_apnea_history", "N/A")}<br/>
    """
    elements.append(Paragraph(patient_info, styles["Normal"]))
    elements.append(Spacer(1, 20))

    # Add session data section
    elements.append(Paragraph("Session Data", styles["Heading2"]))

    # Iterate over each row in the session and add data to the report
    for idx, row in session_df.iterrows():
        for col in columns_required:
            value = row[col] if col in row else "N/A"
            elements.append(Paragraph(f"<b>{col}:</b> {value}", styles["Normal"]))
        elements.append(Spacer(1, 10))

    # Generate personalized recommendations based on patient profile
    recommendations = generate_recommendations(
        age=patient_data.get("age", 0),
        sex=patient_data.get("sex", "N/A"),
        weight=patient_data.get("weight", 0),
        height=patient_data.get("height", 0),
        bmi=patient_data.get("bmi", 0),
        neck_circumference=patient_data.get("neck_circumference_(cm)", 0),
        alcohol_use=patient_data.get("regular_alcohol_use", False),
        apnea_history=patient_data.get("familiar_apnea_history", False),
        sleep_difficulties=patient_data.get("regular_sleep_difficulties", False)
    )

    # Add recommendations to the report
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Recommendations", styles["Heading2"]))
    for rec in recommendations:
        elements.append(Paragraph(f"- {rec}", styles["Normal"]))

    # Build and save the PDF document
    doc.build(elements)
    print(f"[INFO] Report saved to: {file_path}")

    # Close the hidden Tkinter root
    root.destroy()

"""
Generates a PDF report containing data from all recorded sleep sessions.
"""
def generate_full_report():

    # Check if CSV file exists
    if not os.path.exists(CSV_PATH):
        print("[ERROR] CSV file not found.")
        return

    # Load the entire processed dataset
    df = pd.read_csv(CSV_PATH)
    
    # Assign session numbers based on 'Start_Time' being zero
    df["Session"] = df.groupby((df['Start_Time'] == 0).cumsum()).ngroup() + 1

    # Load patient data from JSON file
    with open(JSON_PATH, "r") as f:
        patient_data = json.load(f)["patient"]

    # Initialize hidden Tkinter root for file dialog
    root = tk.Tk()
    root.withdraw()

    # Open file dialog to specify output path for the full report
    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        initialfile="Full_Report.pdf",
        title="Save Full Report As"
    )

    # Check if the user cancelled the save operation
    if not file_path:
        print("[INFO] Save operation cancelled.")
        return

    # Initialize PDF document
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Add report title
    elements.append(Paragraph(f"<b>Sleep Apnea Detection System</b>", styles["Title"]))
    elements.append(Spacer(1, 20))

    # Add patient information section
    elements.append(Paragraph("Patient Information", styles["Heading2"]))

    patient_info = f"""
    Name: {patient_data.get("name", "N/A")}<br/>
    Age: {patient_data.get("age", "N/A")}<br/>
    Sex: {patient_data.get("sex", "N/A")}<br/>
    Weight (Kg): {patient_data.get("weight_(kg)", "N/A")}<br/>
    Height (cm): {patient_data.get("height_(cm)", "N/A")}<br/>
    BMI: {patient_data.get("bmi", "N/A")}<br/>
    Neck Circumference: {patient_data.get("neck_circumference_(cm)", "N/A")} cm<br/>
    Regular alcohol use: {patient_data.get("regular_alcohol_use", "N/A")}<br/>
    Regular sleep difficulties: {patient_data.get("regular_sleep_difficulties", "N/A")}<br/>
    Familiar apnea history: {patient_data.get("familiar_apnea_history", "N/A")}<br/>
    """
    elements.append(Paragraph(patient_info, styles["Normal"]))
    elements.append(Spacer(1, 20))

    # Define columns to include in the report
    columns_required = ["Start_Time", "End_Time", "Snoring_Intensity", "Snoring",
                        "Nasal_Airflow", "Spectral_Centroid", "Has_Apnea", "Treatment_Required",
                        "Snore_Energy", "Decibel_Level_dB"]

    # Iterate over each session and add session-specific data
    for session_id, session_df in df.groupby("Session"):
        elements.append(Paragraph(f"<b>Session {session_id}</b>", styles["Heading2"]))
        elements.append(Spacer(1, 10))

        for idx, row in session_df.iterrows():
            for col in columns_required:
                value = row[col] if col in row else "N/A"
                elements.append(Paragraph(f"<b>{col}:</b> {value}", styles["Normal"]))
            elements.append(Spacer(1, 10))

        elements.append(Spacer(1, 20))

    # Generate personalized recommendations based on patient profile
    recommendations = generate_recommendations(
        age=patient_data.get("age", 0),
        sex=patient_data.get("sex", "N/A"),
        weight=patient_data.get("weight", 0),
        height=patient_data.get("height", 0),
        bmi=patient_data.get("bmi", 0),
        neck_circumference=patient_data.get("neck_circumference_(cm)", 0),
        alcohol_use=patient_data.get("regular_alcohol_use", False),
        apnea_history=patient_data.get("familiar_apnea_history", False),
        sleep_difficulties=patient_data.get("regular_sleep_difficulties", False)
    )

    # Add recommendations to the report
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Profile based recommendations", styles["Heading2"]))
    for rec in recommendations:
        elements.append(Paragraph(f"- {rec}", styles["Normal"]))

    # Build and save the PDF document
    doc.build(elements)
    print(f"[INFO] Full report saved to: {file_path}")
    
    # Close the hidden Tkinter root
    root.destroy()
