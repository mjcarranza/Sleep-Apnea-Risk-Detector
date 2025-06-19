import pytest
import os
import numpy as np
from unittest.mock import patch, MagicMock
from src.ui.recording_screen import RecordingScreen, get_volume_color

# ---- Test for the standalone function get_volume_color ----
@pytest.mark.parametrize("volume,expected_color", [
    (0.0, '#00ff00'),  # Green for zero volume
    (0.5, '#ffff00'),  # Yellow for mid volume
    (1.0, '#ff0000'),  # Red for full volume
])
def test_get_volume_color(volume, expected_color):
    assert get_volume_color(volume) == expected_color

# ---- Tests for the RecordingScreen class (Logic only) ----

@patch('src.ui.recording_screen.sd.query_devices')
def test_get_input_devices(mock_query_devices):
    # Mock input devices
    mock_query_devices.return_value = [
        {'name': 'Mic1', 'max_input_channels': 1},
        {'name': 'Speaker', 'max_input_channels': 0},
        {'name': 'Mic2', 'max_input_channels': 2},
    ]

    screen = RecordingScreen(parent=MagicMock())
    devices = screen.get_input_devices()
    assert 'Mic1' in devices
    assert 'Mic2' in devices
    assert 'Speaker' not in devices  # Should not include output-only devices

@patch('os.listdir')
def test_get_alarm_sounds(mock_listdir):
    # Mock alarm sound directory
    mock_listdir.return_value = ['alarm1.mp3', 'alarm2.mp3', 'readme.txt']
    
    screen = RecordingScreen(parent=MagicMock())
    sounds = screen.get_alarm_sounds()
    assert 'alarm1.mp3' in sounds
    assert 'alarm2.mp3' in sounds
    assert 'readme.txt' not in sounds  # Should filter out non-mp3 files

def test_get_selected_device_index_found():
    screen = RecordingScreen(parent=MagicMock())
    # Mock values
    screen.selected_device.set('Mic1')
    with patch('src.ui.recording_screen.sd.query_devices', return_value=[{'name': 'Mic1', 'max_input_channels': 1}]):
        index = screen.get_selected_device_index()
        assert index == 0  # Mic1 found at index 0

def test_get_selected_device_index_not_found():
    screen = RecordingScreen(parent=MagicMock())
    # Mock values
    screen.selected_device.set('MicX')  # MicX does not exist
    with patch('src.ui.recording_screen.sd.query_devices', return_value=[{'name': 'Mic1', 'max_input_channels': 1}]):
        index = screen.get_selected_device_index()
        assert index is None  # MicX not found

def test_audio_callback_sets_volume_and_appends_data():
    screen = RecordingScreen(parent=MagicMock())
    indata = np.array([[0.1], [0.1], [0.1]])
    screen.audio_callback(indata, None)
    assert len(screen.audio_data) == 1
    assert isinstance(screen.volume_level, float)
    assert screen.volume_level >= 0

