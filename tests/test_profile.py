import pytest
from unittest.mock import patch, MagicMock, call
from src.ui.profile_form import ProfileForm

@pytest.fixture
def profile_form():
    # Creamos una instancia sin un parent real, mockeamos para evitar UI
    return ProfileForm(parent=MagicMock())

# --- Test update_bmi ---

def test_update_bmi_valid(profile_form):
    profile_form.fields["weight_(kg)"].get = MagicMock(return_value="70")
    profile_form.fields["height_(cm)"].get = MagicMock(return_value="175")

    # Mock de métodos de entry BMI para verificar llamada
    bmi_field = profile_form.fields["BMI"]
    bmi_field.configure = MagicMock()
    bmi_field.delete = MagicMock()
    bmi_field.insert = MagicMock()

    profile_form.update_bmi()

    bmi_field.configure.assert_any_call(state="normal")
    bmi_field.delete.assert_called_once_with(0, "end")
    bmi_field.insert.assert_called_once_with(0, "22.86")
    bmi_field.configure.assert_any_call(state="disabled")

def test_update_bmi_invalid(profile_form):
    profile_form.fields["weight_(kg)"].get = MagicMock(return_value="abc")
    profile_form.fields["height_(cm)"].get = MagicMock(return_value="175")

    bmi_field = profile_form.fields["BMI"]
    bmi_field.configure = MagicMock()
    bmi_field.delete = MagicMock()
    bmi_field.insert = MagicMock()

    profile_form.update_bmi()

    bmi_field.configure.assert_any_call(state="normal")
    bmi_field.delete.assert_called_once_with(0, "end")
    bmi_field.insert.assert_called_once_with(0, "")
    bmi_field.configure.assert_any_call(state="disabled")

# --- Test load_data_into_form ---

@patch('src.ui.profile_form.load_patient_data')
def test_load_data_into_form(mock_load_data, profile_form):
    mock_load_data.return_value = {
        "name": "John Doe",
        "age": "30",
        "sex": "Male",
        "weight_(kg)": "70",
        "height_(cm)": "175",
        "bmi": "22.86",
        "neck_circumference_(cm)": "40",
        "regular_alcohol_use": "True",
        "regular_sleep_difficulties": "False",
        "familiar_apnea_history": "False"
    }

    # Mock setters for OptionMenu widgets
    for label in profile_form.field_keys.keys():
        widget = profile_form.fields[label]
        if hasattr(widget, "set"):
            widget.set = MagicMock()
        else:
            widget.delete = MagicMock()
            widget.insert = MagicMock()

    profile_form.load_data_into_form()

    for label in profile_form.field_keys.keys():
        widget = profile_form.fields[label]
        key = profile_form.field_keys[label]
        expected_value = mock_load_data.return_value.get(key, "")
        if hasattr(widget, "set"):
            widget.set.assert_called_with(expected_value)
        else:
            widget.delete.assert_called()
            widget.insert.assert_called_with(0, expected_value)

@patch('src.ui.profile_form.load_patient_data')
def test_update_profile_label(mock_load_data, profile_form):
    mock_load_data.return_value = {"name": "Jane Smith"}

    profile_form.profile_icon_label.configure = MagicMock()
    profile_form.update_profile_label()
    profile_form.profile_icon_label.configure.assert_called_once_with(text=" Jane Smith")

# --- Test toggle_edit_save ---

@patch('src.ui.profile_form.save_patient_data')
@patch('src.ui.profile_form.load_patient_data')
@patch('src.ui.profile_form.CustomMessageBox')
def test_toggle_edit_save_save_data_success(mock_msgbox, mock_load, mock_save, profile_form):
    # Prepara profile_form para estar en modo edición
    profile_form.is_editing = True

    # Mock widgets to return valid inputs
    for label, key in profile_form.field_keys.items():
        widget = profile_form.fields[label]
        if hasattr(widget, "get"):
            if key in ["regular_alcohol_use", "regular_sleep_difficulties", "familiar_apnea_history", "sex"]:
                widget.get = MagicMock(return_value="True" if key.startswith("regular") else "Male")
            else:
                widget.get = MagicMock(return_value="10" if key != "name" else "John")

    mock_load.return_value = {"recordedSessions": 3}

    # Mock UI update methods
    profile_form.load_data_into_form = MagicMock()
    profile_form.set_fields_state = MagicMock()
    profile_form.edit_save_button = MagicMock()
    profile_form.cancel_back_button = MagicMock()

    profile_form.toggle_edit_save()

    mock_save.assert_called_once()
    mock_msgbox.assert_called_once()
    profile_form.load_data_into_form.assert_called_once()
    profile_form.set_fields_state.assert_called_with(disabled=True)

def test_toggle_edit_save_switch_to_edit(profile_form):
    profile_form.is_editing = False
    profile_form.set_fields_state = MagicMock()
    profile_form.edit_save_button = MagicMock()
    profile_form.cancel_back_button = MagicMock()

    profile_form.toggle_edit_save()

    profile_form.set_fields_state.assert_called_with(disabled=False)
    profile_form.edit_save_button.configure.assert_called_with(text="Save Data")
    profile_form.cancel_back_button.configure.assert_called_with(text="Cancel")
    assert profile_form.is_editing == True

# --- Test cancel_or_back ---

def test_cancel_or_back_when_editing(profile_form):
    profile_form.is_editing = True
    profile_form.load_data_into_form = MagicMock()
    profile_form.set_fields_state = MagicMock()
    profile_form.edit_save_button = MagicMock()
    profile_form.cancel_back_button = MagicMock()

    profile_form.cancel_or_back()

    profile_form.load_data_into_form.assert_called_once()
    profile_form.set_fields_state.assert_called_with(disabled=True)
    profile_form.edit_save_button.configure.assert_called_with(text="Edit")
    profile_form.cancel_back_button.configure.assert_called_with(text="Back to Main Menu")
    assert profile_form.is_editing == False

def test_cancel_or_back_when_not_editing(profile_form):
    profile_form.is_editing = False
    profile_form.parent.show_frame = MagicMock()

    profile_form.cancel_or_back()

    profile_form.parent.show_frame.assert_called_once_with("StartScreen")

# --- Test set_fields_state ---

def test_set_fields_state(profile_form):
    profile_form.fields["Name"].configure = MagicMock()
    profile_form.fields["Age"].configure = MagicMock()

    profile_form.set_fields_state(disabled=True)
    profile_form.fields["Name"].configure.assert_called_with(state="disabled")
    profile_form.fields["Age"].configure.assert_called_with(state="disabled")

    profile_form.set_fields_state(disabled=False)
    profile_form.fields["Name"].configure.assert_called_with(state="normal")
    profile_form.fields["Age"].configure.assert_called_with(state="normal")
