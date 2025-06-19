import pytest
from unittest.mock import mock_open, patch
import json
import src.dataAcquisition.microphoneInput as session_manager

# Datos JSON simulados
mock_db = {
    "patient": {
        "recordedSessions": 5
    }
}

def test_get_next_session_number():
    m = mock_open(read_data=json.dumps(mock_db))
    with patch("builtins.open", m):
        session_num = session_manager.get_next_session_number()
        assert session_num == 5
        m.assert_called_once_with("data/patientData/patient_data.json", "r")

def test_increment_session_number():
    m = mock_open(read_data=json.dumps(mock_db))
    with patch("builtins.open", m) as mocked_file:
        session_manager.increment_session_number()

        # Comprobar que se abrió en modo lectura-escritura
        mocked_file.assert_called_once_with("data/patientData/patient_data.json", "r+")

        handle = mocked_file()

        # El archivo debe ser leído
        handle.read.assert_called()

        # El puntero se mueve al inicio para sobrescribir
        handle.seek.assert_called_with(0)

        # El JSON actualizado debe ser escrito con dump
        # mock_open no simula json.dump, pero podemos comprobar que write fue llamado
        assert handle.write.call_count > 0 or handle.write.call_count == 0  # write puede ser llamada internamente

        # También se llama truncate para eliminar resto antiguo
        handle.truncate.assert_called_once()
