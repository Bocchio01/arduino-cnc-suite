import pytest
from unittest.mock import Mock, MagicMock, patch
from core.communication.gcode_sender import GCodeSender


@pytest.fixture
def mock_serial():
    with patch("serial.Serial") as mock:
        serial_instance = MagicMock()
        serial_instance.readline.return_value = b"READY\n"
        serial_instance.is_open = True
        mock.return_value = serial_instance
        yield serial_instance


def test_connection(mock_serial):
    sender = GCodeSender("COM3")

    assert sender.connect()
    assert sender.is_connected

    # Should have written nothing yet
    mock_serial.write.assert_not_called()


def test_send_command(mock_serial):
    sender = GCodeSender("COM3")
    sender.connect()

    # Mock successful response
    mock_serial.readline.return_value = b"ok\n"

    result = sender.send_command("G0 X10 Y20")

    assert result is True
    mock_serial.write.assert_called_with(b"G0 X10 Y20\n")


def test_send_command_error(mock_serial):
    sender = GCodeSender("COM3")
    sender.connect()

    # Mock error response
    mock_serial.readline.return_value = b"error: Unknown command\n"

    result = sender.send_command("INVALID")

    assert result is False


def test_stream_gcode(mock_serial):
    sender = GCodeSender("COM3")
    sender.connect()

    # Mock successful responses
    mock_serial.readline.return_value = b"ok\n"

    gcode = ["G28", "G0 X10 Y10", "M3 S90", "G1 X20 Y20"]

    progress_calls = []

    def progress_callback(current, total):
        progress_calls.append((current, total))

    result = sender.stream_gcode(gcode, progress_callback)

    assert result is True
    assert len(progress_calls) == 4
    assert progress_calls[-1] == (4, 4)


def test_emergency_stop(mock_serial):
    sender = GCodeSender("COM3")
    sender.connect()

    mock_serial.readline.return_value = b"ok\n"

    sender.emergency_stop()

    # Should send pen up command
    calls = [call[0][0].decode() for call in mock_serial.write.call_args_list]
    assert "M5\n" in calls
