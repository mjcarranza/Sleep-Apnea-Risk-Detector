import tkinter as tk
from tkinter import filedialog
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import pandas as pd
import json
import os

from utils.helpers import load_patient_data  # Asegúrate que esta función esté correctamente implementada
from ui.paths import CSV_PATH, JSON_PATH, REPORT_FOLDER  # Si tienes estas rutas centralizadas

JSON_PATH = "data/patientData/patient_data.json"
CSV_PATH = "data/processed/processed_patient_data.csv"
OUTPUT_DIR = "docs"

def generate_report(session_number):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Cargar datos del paciente
    with open(JSON_PATH, "r") as f:
        patient_data = json.load(f)["patient"]

    # Cargar datos del CSV
    df = pd.read_csv(CSV_PATH)
    df["Session"] = df.groupby((df['Start_Time'] == 0).cumsum()).ngroup() + 1
    session_df = df[df["Session"] == session_number]

    # Filtrar eventos de apnea
    apnea_events = session_df[session_df["Has_Apnea"] == True][["Start_Time", "End_Time", "Snoring", "Treatment_Required"]]

    # Abrir cuadro de diálogo para seleccionar dónde guardar el archivo
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal de Tkinter

    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        initialfile=f"Session{session_number}_report.pdf",
        title="Save Report As"
    )

    if not file_path:  # Si el usuario cancela
        print("[INFO] Save operation cancelled.")
        return

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Información del paciente
    patient_info = f"""
    <b>Patient Report</b><br/>
    Name: {patient_data.get("name", "N/A")}<br/>
    Age: {patient_data.get("age", "N/A")}<br/>
    Sex: {patient_data.get("sex", "N/A")}<br/>
    BMI: {patient_data.get("bmi", "N/A")}<br/>
    Neck Circumference: {patient_data.get("neck_circumference_(cm)", "N/A")} cm<br/>
    Session Number: {session_number}
    """
    elements.append(Paragraph(patient_info, styles["Normal"]))
    elements.append(Spacer(1, 20))

    # Tabla de eventos
    if not apnea_events.empty:
        elements.append(Paragraph("Apnea Events", styles["Heading2"]))
        data = [["Start Time", "End Time", "Snoring", "Treatment Required"]] + apnea_events.values.tolist()
        table = Table(data, colWidths=[100, 100, 100, 130])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 10),
            ('BACKGROUND',(0,1),(-1,-1),colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("No apnea events were detected in this session.", styles["Normal"]))

    doc.build(elements)
    print(f"[INFO] Report saved to: {file_path}")


def generate_full_report():
    if not os.path.exists(CSV_PATH):
        print("[ERROR] No se encontró el archivo CSV.")
        return

    # Cargar datos
    df = pd.read_csv(CSV_PATH)
    df["Session"] = df.groupby((df['Start_Time'] == 0).cumsum()).ngroup() + 1

    # Cargar datos del paciente
    with open(JSON_PATH, "r") as f:
        patient_data = json.load(f)["patient"]

    # Abrir cuadro de diálogo para seleccionar dónde guardar el archivo
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal de Tkinter

    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        initialfile="Full_Report.pdf",
        title="Save Full Report As"
    )

    if not file_path:  # Si el usuario cancela
        print("[INFO] Save operation cancelled.")
        return

    # Estilos y documento
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Título
    elements.append(Paragraph("<b>Sleep Report - All Sessions</b>", styles["Title"]))
    elements.append(Spacer(1, 20))

    # Información del paciente
    patient_info = f"""
    <b>Patient Information</b><br/>
    Name: {patient_data.get("name", "N/A")}<br/>
    Age: {patient_data.get("age", "N/A")}<br/>
    Sex: {patient_data.get("sex", "N/A")}<br/>
    BMI: {patient_data.get("bmi", "N/A")}<br/>
    Neck Circumference: {patient_data.get("neck_circumference_(cm)", "N/A")} cm<br/>
    """
    elements.append(Paragraph(patient_info, styles["Normal"]))
    elements.append(Spacer(1, 20))

    # Iterar por sesiones
    for session_id, session_df in df.groupby("Session"):
        elements.append(Paragraph(f"<b>Session {session_id}</b>", styles["Heading2"]))
        elements.append(Spacer(1, 10))

        apnea_events = session_df[session_df["Has_Apnea"] == True][["Start_Time", "End_Time", "Snoring", "Treatment_Required"]]

        # Siempre crear tabla (incluso si no hay eventos)
        data = [["Start Time", "End Time", "Snoring", "Treatment Required"]]

        if not apnea_events.empty:
            data += apnea_events.values.tolist()
        else:
            # Agregar fila vacía (opcional, o puedes dejar solo los headers)
            data.append(["-", "-", "-", "-"])

        table = Table(data, colWidths=[100, 100, 100, 130])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 10),
            ('BACKGROUND',(0,1),(-1,-1),colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ]))
        elements.append(table)
    elements.append(Spacer(1, 20))

    doc.build(elements)
    print(f"[INFO] Full report saved to: {file_path}")
