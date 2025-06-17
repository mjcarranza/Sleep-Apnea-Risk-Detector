import tkinter as tk
from tkinter import filedialog
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from recommendation.recommendation_engine import generate_recommendations
import pandas as pd
import json
import os

#from utils.helpers import load_patient_data  # Asegúrate que esta función esté correctamente implementada
from ui.paths import CSV_PATH, JSON_PATH # Si tienes estas rutas centralizadas

JSON_PATH = "data/patientData/patient_data.json"
CSV_PATH = "data/processed/processed_patient_data.csv"
OUTPUT_DIR = "docs"

def generate_report(session_number):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    with open(JSON_PATH, "r") as f:
        patient_data = json.load(f)["patient"]

    df = pd.read_csv(CSV_PATH)
    df["Session"] = df.groupby((df['Start_Time'] == 0).cumsum()).ngroup() + 1
    session_df = df[df["Session"] == session_number]

    columns_required = ["Start_Time", "End_Time", "Snoring_Intensity", "Snoring",
                        "Nasal_Airflow", "Spectral_Centroid", "Has_Apnea", "Treatment_Required",
                        "Snore_Energy", "Decibel_Level_dB"]

    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        initialfile=f"Session{session_number}_report.pdf",
        title="Save Report As"
    )

    if not file_path:
        print("[INFO] Save operation cancelled.")
        return

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph(f"<b>Sleep Apnea Detection System</b>", styles["Title"]))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(f"Patient Report For Sleep Session Number {session_number}", styles["Heading2"]))

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

    elements.append(Paragraph("Session Data", styles["Heading2"]))

    for idx, row in session_df.iterrows():
        for col in columns_required:
            value = row[col] if col in row else "N/A"
            elements.append(Paragraph(f"<b>{col}:</b> {value}", styles["Normal"]))
        elements.append(Spacer(1, 10))

    # Generate and add recommendations
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

    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Recommendations", styles["Heading2"]))
    for rec in recommendations:
        elements.append(Paragraph(f"- {rec}", styles["Normal"]))

    doc.build(elements)
    print(f"[INFO] Report saved to: {file_path}")

    # cerror el root
    root.destroy()

def generate_full_report():
    if not os.path.exists(CSV_PATH):
        print("[ERROR] CSV file not found.")
        return

    df = pd.read_csv(CSV_PATH)
    df["Session"] = df.groupby((df['Start_Time'] == 0).cumsum()).ngroup() + 1

    with open(JSON_PATH, "r") as f:
        patient_data = json.load(f)["patient"]

    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        initialfile="Full_Report.pdf",
        title="Save Full Report As"
    )

    if not file_path:
        print("[INFO] Save operation cancelled.")
        return

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph(f"<b>Sleep Apnea Detection System</b>", styles["Title"]))
    elements.append(Spacer(1, 20))

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

    columns_required = ["Start_Time", "End_Time", "Snoring_Intensity", "Snoring",
                        "Nasal_Airflow", "Spectral_Centroid", "Has_Apnea", "Treatment_Required",
                        "Snore_Energy", "Decibel_Level_dB"]

    for session_id, session_df in df.groupby("Session"):
        elements.append(Paragraph(f"<b>Session {session_id}</b>", styles["Heading2"]))
        elements.append(Spacer(1, 10))

        for idx, row in session_df.iterrows():
            for col in columns_required:
                value = row[col] if col in row else "N/A"
                elements.append(Paragraph(f"<b>{col}:</b> {value}", styles["Normal"]))
            elements.append(Spacer(1, 10))

        elements.append(Spacer(1, 20))

    # Generate and add recommendations
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

    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Profile based recommendations", styles["Heading2"]))
    for rec in recommendations:
        elements.append(Paragraph(f"- {rec}", styles["Normal"]))

    doc.build(elements)
    print(f"[INFO] Full report saved to: {file_path}")
    
    # destruye el root
    root.destroy()
