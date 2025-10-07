import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from recommendation.recommendation_engine import generate_recommendations
from dataAcquisition.cameraInput import getPhotoDatetime, getFileNames

# Import centralized paths for CSV and JSON data files
from ui.paths import CSV_PATH, JSON_PATH

# Constants for data paths and output directory
JSON_PATH = "data/patientData/patient_data.json"
CSV_PATH = "data/processed/processed_patient_data.csv"
OUTPUT_DIR = "docs"
AUDIO_FOLDER = "data/raw"


def generate_report(session_number):
    """Generates a summarized PDF report for a specific sleep session."""

    # --- Ensure output directory exists ---
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # --- Load patient data ---
    with open(JSON_PATH, "r") as f:
        patient_data = json.load(f)["patient"]

    # --- Load processed data ---
    df = pd.read_csv(CSV_PATH)
    df["Session"] = df.groupby((df['Start_Time'] == 0).cumsum()).ngroup() + 1
    session_df = df[df["Session"] == session_number]

    # --- Analyze the session ---
    result = analyze_sleep_session(session_df)

    # --- Add image predictions as table --- 
    imagesPath = os.path.join(AUDIO_FOLDER, f"Session{session_number}", "Images")
    imagesNameList = getFileNames(imagesPath)

    # --- Save path dialog ---
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
        root.destroy()
        return

    # --- Create PDF ---
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # --- Title ---
    elements.append(Paragraph('<font color="#4A90E2"><b>Sleep Apnea Detection System</b></font>', styles["Title"]))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Patient Report - Sleep Session {session_number}", styles["Heading2"]))
    elements.append(Spacer(1, 20))

    # --- Patient Info Table ---
    patient_info = [
        ["Name", patient_data.get("name", "N/A")],
        ["Age", patient_data.get("age", "N/A")],
        ["Sex", patient_data.get("sex", "N/A")],
        ["BMI", patient_data.get("bmi", "N/A")],
        ["Neck Circumference", f"{patient_data.get('neck_circumference_(cm)', 'N/A')} cm"],
        ["Regular Alcohol Use", patient_data.get("regular_alcohol_use", "N/A")],
        ["Sleep Difficulties", patient_data.get("regular_sleep_difficulties", "N/A")],
        ["Familiar Apnea History", patient_data.get("familiar_apnea_history", "N/A")]
    ]
    patient_table = Table(patient_info, hAlign="LEFT")
    patient_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
    ]))
    elements.append(Paragraph("Patient Information", styles["Heading3"]))
    elements.append(patient_table)
    elements.append(Spacer(1, 20))

    # --- Session Summary Table ---
    session_summary = result["session_summary_row"]
    session_table_data = [["Duration\n(h)", "Total\nApneas", "Mean\nSnoring", "Snoring\nVariability", 
                           "Max\nDecibel", "Apnea\nRate (/h)", "Treatment\nRequired"]]

    for _, row in session_summary.iterrows():
        session_table_data.append([
            row["Duration_h"], row["Total_Apneas"], row["Snoring_Mean"],
            row["Snoring_Variability"], row["Decibel_Max"],
            row["Apnea_Rate_hr"], "Yes" if row["Treatment_Required"] else "No"
        ])

    session_table = Table(session_table_data, hAlign="LEFT")
    session_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4A4A6A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9)
    ]))
    elements.append(Paragraph("Session Summary", styles["Heading3"]))
    elements.append(session_table)
    elements.append(Spacer(1, 20))
    

    # --- Descriptive Statistics ---
    desc = result["descriptive_table"].round(2).reset_index()

    # 1️⃣ Define tus nombres personalizados aquí
    column_mapping = {
        "Snoring_Intensity": "Snoring\nIntensity",
        "Nasal_Airflow": "Nasal\nAirflow",
        "Spectral_Centroid": "Spectral\nCentroid",
        "Decibel_Level_dB": "Decibel\nLevel (dB)"
    }

    # 2️⃣ Renombra las columnas según el diccionario (solo las que existan)
    desc = desc.rename(columns={col: column_mapping.get(col, col) for col in desc.columns})

    # 3️⃣ Construye la tabla con los nuevos nombres
    desc_data = [desc.columns.tolist()] + desc.values.tolist()
    desc_table = Table(desc_data, hAlign="LEFT", colWidths=[80] + [60] * (len(desc.columns) - 1))
    desc_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4A4A6A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8)
    ]))

    elements.append(Paragraph("Descriptive Statistics", styles["Heading3"]))
    elements.append(desc_table)
    elements.append(Spacer(1, 20))


    # --- Información de Imágenes Capturadas ---
    elements.append(Paragraph("Information of Captured Images", styles["Heading3"]))
    elements.append(Spacer(1, 10))

    # Encabezados
    headers = ["Date and Time", "Sleeping Position Detected"]
    data = [headers]

    # Agregar filas desde las imágenes capturadas
    for image_name in imagesNameList:
        image_path = os.path.join(imagesPath, image_name)

        # Obtiene fecha/hora del archivo
        dt = getPhotoDatetime(image_path)
        name_only, _ = os.path.splitext(image_name)

        data.append([dt, name_only])

    # Crear la tabla en ReportLab
    img_table = Table(data, hAlign="LEFT", colWidths=[180, 180])
    img_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4A4A6A")),   # Encabezado oscuro
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F5F5F5"), colors.whitesmoke]),
    ]))

    elements.append(img_table)
    elements.append(Spacer(1, 20))



    # --- Include Graphs ---
    if os.path.exists("apnea_pie_chart.png"):
        elements.append(Paragraph("Apnea Time Distribution", styles["Heading3"]))
        elements.append(Image("apnea_pie_chart.png", width=200, height=200))
        elements.append(Spacer(1, 20))
    
    if os.path.exists("sleep_session_summary.png"):
        elements.append(Paragraph("Signal Evolution Summary", styles["Heading3"]))
        elements.append(Image("sleep_session_summary.png", width=400, height=180))
        elements.append(Spacer(1, 20))

    # --- Recommendations ---
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
    elements.append(Paragraph("Recommendations", styles["Heading3"]))
    for rec in recommendations:
        elements.append(Paragraph(f"- {rec}", styles["Normal"]))

    elements.append(Paragraph("Note", styles["Heading3"]))
    elements.append(Paragraph("Remember that this is an AI detection system for Obstructive Sleeping Apnea (OSA). This report is for informating purposes only and does not replace a professional diagnosis.", styles["Normal"]))
    elements.append(Paragraph("Please check results with a doctor.", styles["Normal"]))


    # --- Build PDF ---
    doc.build(elements)
    print(f"[INFO] Report saved to: {file_path}")
    root.destroy()

    # --- Delete temporary pie chart ---
    if os.path.exists("apnea_pie_chart.png"):
        os.remove("apnea_pie_chart.png")
    if os.path.exists("sleep_session_summary.png"):
        os.remove("sleep_session_summary.png")


def generate_full_report():
    """Generates a complete PDF report containing data from all recorded sleep sessions."""

    # --- Ensure CSV exists ---
    if not os.path.exists(CSV_PATH):
        print("[ERROR] CSV file not found.")
        return

    # --- Load data ---
    df = pd.read_csv(CSV_PATH)
    df["Session"] = df.groupby((df['Start_Time'] == 0).cumsum()).ngroup() + 1

    with open(JSON_PATH, "r") as f:
        patient_data = json.load(f)["patient"]

    # --- Ask where to save ---
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

    # --- Setup PDF ---
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # --- Title ---
    elements.append(Paragraph('<font color="#4A90E2"><b>Sleep Apnea Detection System</b></font>', styles["Title"]))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Full Sleep Sessions Report", styles["Heading2"]))
    elements.append(Spacer(1, 20))

    # --- Patient Info Table ---
    patient_info = [
        ["Name", patient_data.get("name", "N/A")],
        ["Age", patient_data.get("age", "N/A")],
        ["Sex", patient_data.get("sex", "N/A")],
        ["BMI", patient_data.get("bmi", "N/A")],
        ["Neck Circumference", f"{patient_data.get('neck_circumference_(cm)', 'N/A')} cm"],
        ["Regular Alcohol Use", patient_data.get("regular_alcohol_use", "N/A")],
        ["Sleep Difficulties", patient_data.get("regular_sleep_difficulties", "N/A")],
        ["Familiar Apnea History", patient_data.get("familiar_apnea_history", "N/A")]
    ]
    patient_table = Table(patient_info, hAlign="LEFT")
    patient_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
    ]))
    elements.append(Paragraph("Patient Information", styles["Heading2"]))
    elements.append(patient_table)
    elements.append(Spacer(1, 20))

    # --- Analyze all sessions ---
    for session_id, session_df in df.groupby("Session"):
        result = analyze_sleep_session(session_df)

        elements.append(Paragraph(f"<b>Sleep Session {session_id}</b>", styles["Heading2"]))
        elements.append(Spacer(1, 10))

        # --- Session Summary Table ---
        summary = result["session_summary_row"]
        summary_data = [["Duration\n(h)", "Total\nApneas", "Mean\nSnoring", "Snoring\nVariability",
                         "Max\nDecibel", "Apnea\nRate (/h)", "Treatment\nRequired"]]
        for _, row in summary.iterrows():
            summary_data.append([
                row["Duration_h"], row["Total_Apneas"], row["Snoring_Mean"],
                row["Snoring_Variability"], row["Decibel_Max"],
                row["Apnea_Rate_hr"], "Yes" if row["Treatment_Required"] else "No"
            ])

        session_table = Table(summary_data, hAlign="LEFT")
        session_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4A4A6A")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 9)
        ]))
        elements.append(Paragraph("Session Summary", styles["Heading3"]))
        elements.append(session_table)
        elements.append(Spacer(1, 15))

        # --- Descriptive Statistics ---
        desc = result["descriptive_table"].round(2).reset_index()
        column_mapping = {
            "Snoring_Intensity": "Snoring\nIntensity",
            "Nasal_Airflow": "Nasal\nAirflow",
            "Spectral_Centroid": "Spectral\nCentroid",
            "Decibel_Level_dB": "Decibel\nLevel (dB)"
        }
        desc = desc.rename(columns={col: column_mapping.get(col, col) for col in desc.columns})

        desc_data = [desc.columns.tolist()] + desc.values.tolist()
        desc_table = Table(desc_data, hAlign="LEFT", colWidths=[80] + [60]*(len(desc.columns)-1))
        desc_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4A4A6A")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 8)
        ]))
        elements.append(Paragraph("Descriptive Statistics", styles["Heading3"]))
        elements.append(desc_table)
        elements.append(Spacer(1, 20))

        if os.path.exists("apnea_pie_chart.png"):
            elements.append(Paragraph("Apnea Time Distribution", styles["Heading3"]))
            elements.append(Image("apnea_pie_chart.png", width=200, height=200))
            elements.append(Spacer(1, 20))

        if os.path.exists("sleep_session_summary.png"):
            elements.append(Paragraph("Signal Evolution Summary", styles["Heading3"]))
            elements.append(Image("sleep_session_summary.png", width=400, height=180))
            elements.append(Spacer(1, 20))

    # --- Recommendations ---
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
    elements.append(Paragraph("Recommendations", styles["Heading3"]))
    for rec in recommendations:
        elements.append(Paragraph(f"- {rec}", styles["Normal"]))

    # --- Note section ---
    elements.append(Paragraph("Note", styles["Heading3"]))
    elements.append(Paragraph("Remember that this is an AI detection system for Obstructive Sleeping Apnea (OSA). This report is for informating purposes only and does not replace a professional diagnosis.", styles["Normal"]))
    elements.append(Paragraph("Please check results with a doctor.", styles["Normal"]))

    # --- Build PDF ---
    doc.build(elements)
    print(f"[INFO] Full report saved to: {file_path}")
    root.destroy()
    # --- Delete temporary pie chart ---
    if os.path.exists("apnea_pie_chart.png"):
        os.remove("apnea_pie_chart.png")
    if os.path.exists("sleep_session_summary.png"):
        os.remove("sleep_session_summary.png")


def analyze_sleep_session(session_df, interval_seconds=60, sample_window=5):
    """Analyzes and summarizes a complete sleep session with statistics and plots."""

    rows_per_interval = int(interval_seconds / sample_window)
    session_df = session_df.copy()
    session_df["Interval"] = (session_df.index // rows_per_interval)

    interval_summary = session_df.groupby("Interval").agg({
        "Snoring_Intensity": "mean",
        "Nasal_Airflow": "mean",
        "Spectral_Centroid": "mean",
        "Snore_Energy": "mean",
        "Decibel_Level_dB": "mean",
        "Has_Apnea": "sum",
        "Treatment_Required": "max"
    }).reset_index()

    # General stats
    stats = {}
    stats["duration_hours"] = len(session_df) * sample_window / 3600
    stats["total_apneas"] = session_df["Has_Apnea"].sum()
    stats["total_snoring_events"] = (session_df["Snoring_Intensity"] > 0.3).sum()
    stats["mean_snoring"] = session_df["Snoring_Intensity"].mean()
    stats["max_decibel"] = session_df["Decibel_Level_dB"].max()
    stats["snoring_variability"] = session_df["Snoring_Intensity"].std() / (stats["mean_snoring"] + 1e-6)
    stats["apnea_rate_hr"] = stats["total_apneas"] / stats["duration_hours"]

    # Descriptive stats
    desc = session_df[["Snoring_Intensity", "Nasal_Airflow", "Spectral_Centroid", "Decibel_Level_dB"]].describe()
    desc.loc["cv"] = desc.loc["std"] / (desc.loc["mean"] + 1e-6)

    # Sumarized graphs
    plt.figure(figsize=(10, 4))
    plt.plot(interval_summary["Interval"], interval_summary["Snoring_Intensity"], label="Snoring Intensity (avg)")
    plt.plot(interval_summary["Interval"], interval_summary["Nasal_Airflow"], label="Nasal Airflow (avg)")
    plt.plot(interval_summary["Interval"], interval_summary["Decibel_Level_dB"], label="Decibel Level (avg)")
    plt.xlabel("Intervalo (minutos)")
    plt.ylabel("Promedio")
    plt.title("Evolución de señales por minuto")
    plt.legend()
    plt.tight_layout()
    plt.savefig("sleep_session_summary.png")
    plt.close()

    # Pie chart

    apnea_ratio = [
        session_df["Has_Apnea"].sum(),
        len(session_df) - session_df["Has_Apnea"].sum()
    ]
    labels = ["Time with AOS", "Without Apnea"]
    plt.figure(figsize=(5, 5))
    plt.pie(apnea_ratio, labels=labels, autopct='%1.1f%%', colors=["#ff9999", "#99ff99"], startangle=90)
    plt.title("Apnea time pie chart")
    plt.tight_layout()
    plt.savefig("apnea_pie_chart.png")
    plt.close()

    resumen_sesion = pd.DataFrame([{
        "Sleep_Session": 1,
        "Duration_h": round(stats["duration_hours"], 2),
        "Total_Apneas": int(stats["total_apneas"]),
        "Snoring_Mean": round(stats["mean_snoring"], 3),
        "Snoring_Variability": round(stats["snoring_variability"], 3),
        "Decibel_Max": round(stats["max_decibel"], 2),
        "Apnea_Rate_hr": round(stats["apnea_rate_hr"], 2),
        "Treatment_Required": int(session_df["Treatment_Required"].max())
    }])

    return {
        "interval_summary": interval_summary,
        "session_stats": stats,
        "descriptive_table": desc,
        "session_summary_row": resumen_sesion
    }
