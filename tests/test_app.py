import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
import json
from unittest import mock
from main import App
from src.ui.paths import TERMS_PATH
from src.utils.data_utils import is_profile_complete


@pytest.fixture
def app_instance():
    return App()

def test_is_terms_accepted_file_missing(app_instance):
    """Should create file and return False if terms.json does not exist."""
    with mock.patch("os.path.exists", return_value=False), \
         mock.patch("builtins.open", mock.mock_open()) as mocked_file:
        result = app_instance.is_terms_accepted()
        assert result is False
        assert mocked_file().write.call_count >= 1


def test_is_terms_accepted_file_exists_true(app_instance):
    """Should return True if terms.json says 'accepted': True."""
    with mock.patch("os.path.exists", return_value=True), \
         mock.patch("builtins.open", mock.mock_open(read_data=json.dumps({"accepted": True}))):
        result = app_instance.is_terms_accepted()
        assert result is True

def test_is_terms_accepted_file_exists_false(app_instance):
    """Should return False if terms.json says 'accepted': False."""
    with mock.patch("os.path.exists", return_value=True), \
         mock.patch("builtins.open", mock.mock_open(read_data=json.dumps({"accepted": False}))):
        result = app_instance.is_terms_accepted()
        assert result is False

def test_on_terms_accepted_profile_incomplete(app_instance):
    """Should call show_frame with 'ProfileForm' if profile is incomplete."""
    with mock.patch("src.utils.data_utils.is_profile_complete", return_value=False), \
         mock.patch.object(app_instance, 'show_frame') as mock_show_frame:
        app_instance.on_terms_accepted()
        mock_show_frame.assert_called_once_with("StartScreen")

def test_on_terms_accepted_profile_complete(app_instance):
    """Should call show_frame with 'StartScreen' if profile is complete."""
    with mock.patch("src.utils.data_utils.is_profile_complete", return_value=True), \
         mock.patch.object(app_instance, 'show_frame') as mock_show_frame:
        app_instance.on_terms_accepted()
        mock_show_frame.assert_called_once_with("StartScreen")
