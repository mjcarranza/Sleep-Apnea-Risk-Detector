
from unittest.mock import patch, mock_open, MagicMock
import pytest
from unittest.mock import patch, MagicMock, call
import pandas as pd
import os
import builtins

from src.ui.data_visualization import DataVisualization

@pytest.fixture
def data_viz():
    # Instancia con parent mock para evitar errores de UI
    return DataVisualization(master=MagicMock())

# --- Test load_patient_info ---

@patch("builtins.open", new_callable=mock_open, read_data='{"patient": {"name": "John", "age": 30}}')
@patch("os.path.exists", return_value=True)
def test_load_patient_info(mock_exists, mock_open, data_viz):
    # Parcheamos creación de labels y buttons para no crear UI real
    with patch.object(data_viz.scrollable_frame, 'pack'), \
         patch('customtkinter.CTkFrame') as mock_frame, \
         patch('customtkinter.CTkLabel') as mock_label, \
         patch('customtkinter.CTkButton') as mock_button:
        data_viz.load_patient_info()

    mock_exists.assert_called_once_with(data_viz.JSON_PATH)

# --- Test load_sleep_sessions ---

@patch("os.path.exists", return_value=True)
@patch("pandas.read_csv")
def test_load_sleep_sessions(mock_read_csv, mock_exists, data_viz):
    # DataFrame simulado con dos sesiones y apnea event
    df = pd.DataFrame({
        "Start_Time": [0, 100, 0, 100],
        "End_Time": [99, 199, 99, 199],
        "Has_Apnea": [True, False, False, False],
        "Snoring": [True, False, False, False],
        "Treatment_Required": [False, False, False, False]
    })

    mock_read_csv.return_value = df

    # Parcheamos métodos que crean UI para no crear UI real
    with patch('customtkinter.CTkFrame'), patch('customtkinter.CTkLabel'), patch('customtkinter.CTkButton'):
        data_viz.load_sleep_sessions()

    mock_exists.assert_called_once_with(data_viz.CSV_PATH)
    mock_read_csv.assert_called_once_with(data_viz.CSV_PATH)

# --- Test toggle_audio ---

@patch('simpleaudio.WaveObject.from_wave_file')
def test_toggle_audio_play_and_stop(mock_wavefile, data_viz):
    mock_play_obj = MagicMock()
    mock_play_obj.is_playing.side_effect = [False, True, False]
    mock_play_obj.play.return_value = mock_play_obj
    mock_wavefile.return_value = mock_play_obj

    mock_button = MagicMock()

    # Audio no está reproduciéndose -> reproduce
    data_viz.current_play_obj = None
    data_viz.toggle_audio("fake_path.wav", mock_button)
    mock_wavefile.assert_called_once_with("fake_path.wav")
    mock_play_obj.play.assert_called_once()
    mock_button.configure.assert_called()

    # Audio está reproduciéndose -> detiene
    data_viz.current_play_obj = mock_play_obj
    data_viz.current_button = mock_button
    mock_play_obj.is_playing.return_value = True

    data_viz.toggle_audio("fake_path.wav", mock_button)
    mock_play_obj.stop.assert_called_once()
    mock_button.configure.assert_called()

# --- Test delete_session ---

@patch('tkinter.messagebox.askyesno', return_value=True)
@patch('tkinter.messagebox.showinfo')
@patch('pandas.read_csv')
@patch('pandas.DataFrame.to_csv')
@patch('shutil.rmtree')
@patch('os.path.exists', return_value=True)
def test_delete_session(mock_exists, mock_rmtree, mock_to_csv, mock_read_csv, mock_showinfo, mock_askyesno, data_viz):
    df = pd.DataFrame({
        "Start_Time": [0, 100, 0, 100],
        "End_Time": [99, 199, 99, 199]
    })
    mock_read_csv.return_value = df

    data_viz.on_show = MagicMock()

    data_viz.delete_session(1)

    mock_askyesno.assert_called_once()
    mock_read_csv.assert_called_once()
    mock_to_csv.assert_called_once()
    mock_rmtree.assert_called_once()
    mock_showinfo.assert_called_once()
    data_viz.on_show.assert_called_once()

# --- Test on_show ---

def test_on_show_clears_and_loads(data_viz):
    child_mock = MagicMock()
    data_viz.scrollable_frame.winfo_children = MagicMock(return_value=[child_mock, child_mock])
    child_mock.destroy = MagicMock()

    with patch.object(data_viz, 'load_patient_info') as mock_load_info, \
         patch.object(data_viz, 'load_sleep_sessions') as mock_load_sessions:
        data_viz.on_show()

    assert child_mock.destroy.call_count == 2
    mock_load_info.assert_called_once()
    mock_load_sessions.assert_called_once()
