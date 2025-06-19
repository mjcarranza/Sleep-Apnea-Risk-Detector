import pytest
from unittest.mock import patch, MagicMock, mock_open
import builtins
import pandas as pd

import src.reportGeneration.reportGenerator as reportGen

@pytest.fixture
def dummy_patient_data():
    return {
        "patient": {
            "name": "John Doe",
            "age": 45,
            "sex": "M",
            "weight_(kg)": 80,
            "height_(cm)": 175,
            "bmi": 26.1,
            "neck_circumference_(cm)": 40,
            "regular_alcohol_use": True,
            "regular_sleep_difficulties": False,
            "familiar_apnea_history": True
        }
    }

@pytest.fixture
def dummy_df():
    return pd.DataFrame({
        "Start_Time": [0, 100],
        "End_Time": [99, 199],
        "Snoring_Intensity": [0.5, 0.3],
        "Snoring": [True, False],
        "Nasal_Airflow": [0.7, 0.6],
        "Spectral_Centroid": [3000, 3500],
        "Has_Apnea": [True, False],
        "Treatment_Required": [False, False],
        "Snore_Energy": [0.8, 0.2],
        "Decibel_Level_dB": [60, 50]
    })

@patch("src.reportGeneration.reportGenerator.generate_recommendations", return_value=["Rec 1", "Rec 2"])
@patch("builtins.open", new_callable=mock_open, read_data='{"patient": {"name": "John Doe"}}')
@patch("os.path.exists", return_value=True)
@patch("pandas.read_csv")
@patch("tkinter.filedialog.asksaveasfilename", return_value="/fake/path/report.pdf")
@patch("reportlab.platypus.SimpleDocTemplate.build")
def test_generate_report(mock_build, mock_dialog, mock_read_csv, mock_exists, mock_open_file, mock_recommendations, dummy_df, dummy_patient_data):
    mock_read_csv.return_value = dummy_df
    mock_open_file.return_value.__enter__.return_value.read.return_value = '{"patient": {"name": "John Doe"}}'
    with patch("json.load", return_value=dummy_patient_data):
        reportGen.generate_report(1)

    mock_dialog.assert_called_once()
    mock_build.assert_called_once()
    mock_recommendations.assert_called_once()

@patch("src.reportGeneration.reportGenerator.generate_recommendations", return_value=["Rec A", "Rec B"])
@patch("builtins.open", new_callable=mock_open, read_data='{"patient": {"name": "John Doe"}}')
@patch("os.path.exists", return_value=True)
@patch("pandas.read_csv")
@patch("tkinter.filedialog.asksaveasfilename", return_value="/fake/path/full_report.pdf")
@patch("reportlab.platypus.SimpleDocTemplate.build")
def test_generate_full_report(mock_build, mock_dialog, mock_read_csv, mock_exists, mock_open_file, mock_recommendations, dummy_df, dummy_patient_data):
    mock_read_csv.return_value = dummy_df
    mock_open_file.return_value.__enter__.return_value.read.return_value = '{"patient": {"name": "John Doe"}}'
    with patch("json.load", return_value=dummy_patient_data):
        reportGen.generate_full_report()

    mock_dialog.assert_called_once()
    mock_build.assert_called_once()
    mock_recommendations.assert_called_once()
