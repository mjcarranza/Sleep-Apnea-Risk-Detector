import os
import json
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from recommendation.recommendation_engine import generate_recommendations

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

    # Assign session numbers to data based on 'Start_Time' being zero
    df["Session"] = df.groupby((df['Start_Time'] == 0).cumsum()).ngroup() + 1

    # Filter the data for the specified session
    session_df = df[df["Session"] == session_number]

    # Define columns to include in the report
    columns_required = [
        "Start_Time", "End_Time", "Snoring_Intensity", "Snoring",
        "Nasal_Airflow", "Spectral_Centroid", "Has_Apnea", "Treatment_Required",
        "Snore_Energy", "Decibel_Level_dB"
    ]

    # Init hidden Tkinter root
    root = tk.Tk()
    root.withdraw()

    # Ask user save path
    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        initialfile=f"Session{session_number}_report.pdf",
        title="Save Report As"
    )

    if not file_path:
        print("[INFO] Save operation cancelled.")
        return

    # Init PDF
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph("<b>Sleep Apnea Detection System</b>", styles["Title"]))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Patient Report For Sleep Session {session_number}", styles["Heading2"]))
    elements.append(Spacer(1, 20))

    # Tabla de información del paciente
    patient_info = [
        ["Name", patient_data.get("name", "N/A")],
        ["Age", patient_data.get("age", "N/A")],
        ["Sex", patient_data.get("sex", "N/A")],
        ["Weight (Kg)", patient_data.get("weight_(kg)", "N/A")],
        ["Height (cm)", patient_data.get("height_(cm)", "N/A")],
        ["BMI", patient_data.get("bmi", "N/A")],
        ["Neck Circumference", f"{patient_data.get('neck_circumference_(cm)', 'N/A')} cm"],
        ["Regular alcohol use", patient_data.get("regular_alcohol_use", "N/A")],
        ["Regular sleep difficulties", patient_data.get("regular_sleep_difficulties", "N/A")],
        ["Familiar apnea history", patient_data.get("familiar_apnea_history", "N/A")]
    ]

    patient_table = Table(patient_info, hAlign="LEFT")
    patient_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
    ]))
    elements.append(patient_table)
    elements.append(Spacer(1, 20))

    # Session Data table
    elements.append(Paragraph("Session Data", styles["Heading2"]))

    # --- Diccionario para nombres más legibles ---
    column_headers = {
        "Start_Time": "Start\nTime (s)",
        "End_Time": "End\nTime (s)",
        "Snoring_Intensity": "Snoring\nIntensity",
        "Snoring": "Snoring\nDetected",
        "Nasal_Airflow": "Nasal\nAirflow",
        "Spectral_Centroid": "Spectral\nCentroid",
        "Has_Apnea": "Has\nApnea",
        "Treatment_Required": "Treatment\nRequired",
        "Snore_Energy": "Snore\nEnergy",
        "Decibel_Level_dB": "Decibel\nLevel (dB)"
    }

    # --- Encabezados limpios ---
    session_data = [[column_headers[col] for col in columns_required]]

    numeric_cols = ["Snoring_Intensity", "Nasal_Airflow", "Spectral_Centroid", 
                    "Snore_Energy", "Decibel_Level_dB"]

    # --- Filas con valores ---
    for _, row in session_df.iterrows():
        formatted_row = []
        for col in columns_required:
            value = row.get(col, "N/A")
            if col in numeric_cols and isinstance(value, (int, float)):
                formatted_row.append(f"{value:.3f}")  # limitar a 3 decimales
            else:
                formatted_row.append(str(value))
        session_data.append(formatted_row)

    # Crear tabla
    session_table = Table(session_data, colWidths=[55]*len(columns_required))

    # Estilo base
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4A4A6A")),  # encabezado
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
    ])

    # --- Resaltar en rojo valores True ---
    highlight_cols = ["Snoring", "Has_Apnea", "Treatment_Required"]
    for row_idx, row in enumerate(session_data[1:], start=1):  # ignorar encabezado
        for col_idx, col in enumerate(columns_required):
            if col in highlight_cols and row[col_idx] == "True":
                style.add('TEXTCOLOR', (col_idx, row_idx), (col_idx, row_idx), colors.red)

    session_table.setStyle(style)
    elements.append(session_table)


    # Recommendations
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
    root.destroy()


"""
Generates a PDF report containing data from all recorded sleep sessions.
"""
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

    elements.append(Paragraph("<b>Sleep Apnea Detection System</b>", styles["Title"]))
    elements.append(Spacer(1, 20))

    # Patient Info table
    patient_info_data = [
        ["Name", patient_data.get("name", "N/A")],
        ["Age", patient_data.get("age", "N/A")],
        ["Sex", patient_data.get("sex", "N/A")],
        ["Weight (Kg)", patient_data.get("weight_(kg)", "N/A")],
        ["Height (cm)", patient_data.get("height_(cm)", "N/A")],
        ["BMI", patient_data.get("bmi", "N/A")],
        ["Neck Circumference (cm)", patient_data.get("neck_circumference_(cm)", "N/A")],
        ["Regular alcohol use", patient_data.get("regular_alcohol_use", "N/A")],
        ["Regular sleep difficulties", patient_data.get("regular_sleep_difficulties", "N/A")],
        ["Familiar apnea history", patient_data.get("familiar_apnea_history", "N/A")],
    ]
    table = Table(patient_info_data, colWidths=[150, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4A4A6A")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
    ]))
    elements.append(Paragraph("Patient Information", styles["Heading2"]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    # Columns for session data
    columns_required = [
        "Start_Time", "End_Time", "Snoring_Intensity", "Snoring",
        "Nasal_Airflow", "Spectral_Centroid", "Has_Apnea", "Treatment_Required",
        "Snore_Energy", "Decibel_Level_dB"
    ]

    # Add each session
    for session_id, session_df in df.groupby("Session"):
        elements.append(Paragraph(f"Session {session_id}", styles["Heading2"]))
        session_data = [columns_required]
        for _, row in session_df.iterrows():
            session_data.append([row.get(col, "N/A") for col in columns_required])

        session_table = Table(session_data, colWidths=[55]*len(columns_required))
        session_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4A4A6A")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ]))
        elements.append(session_table)
        elements.append(Spacer(1, 20))

    # Recommendations
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
    elements.append(Paragraph("Profile based Recommendations", styles["Heading2"]))
    for rec in recommendations:
        elements.append(Paragraph(f"- {rec}", styles["Normal"]))

    doc.build(elements)
    print(f"[INFO] Full report saved to: {file_path}")
    root.destroy()
