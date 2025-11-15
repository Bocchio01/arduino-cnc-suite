import serial
import time
from typing import List, Callable, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class GCodeSender:
    """Handles G-code streaming to Arduino with acknowledgment protocol"""

    def __init__(self, port: str, baudrate: int = 115200, timeout: int = 10):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial: Optional[serial.Serial] = None
        self._is_connected = False

    def connect(self) -> bool:
        """Establish serial connection"""
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            time.sleep(2)  # Wait for Arduino reset

            # Read startup message
            startup = self.serial.readline().decode("utf-8").strip()
            logger.info(f"Arduino startup: {startup}")

            if "READY" in startup:
                self._is_connected = True
                logger.info(f"Connected to printer on {self.port}")
                return True
            else:
                logger.warning(f"Unexpected startup message: {startup}")
                return False

        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    def disconnect(self):
        """Close serial connection"""
        if self.serial and self.serial.is_open:
            self.serial.close()
            self._is_connected = False
            logger.info("Disconnected from printer")

    @property
    def is_connected(self) -> bool:
        return self._is_connected and self.serial and self.serial.is_open

    def send_command(self, command: str) -> bool:
        """
        Send a single G-code command and wait for acknowledgment

        Returns:
            True if command executed successfully, False otherwise
        """
        if not self.is_connected:
            logger.error("Not connected to printer")
            return False

        command = command.strip()

        # Skip empty lines and comments
        if not command or command.startswith(";"):
            return True

        try:
            # Send command
            self.serial.write((command + "\n").encode("utf-8"))
            logger.debug(f"Sent: {command}")

            # Wait for 'ok' response
            while True:
                response = self.serial.readline().decode("utf-8").strip()

                if response == "ok":
                    logger.debug(f"Command completed: {command}")
                    return True
                elif response.startswith("error"):
                    logger.error(f"Error: {command} -> {response}")
                    return False
                elif not response:
                    logger.error(f"Timeout: {command}")
                    raise TimeoutError(f"No response for: {command}")
                else:
                    # Debug/status messages from Arduino
                    logger.info(f"Arduino: {response}")

        except Exception as e:
            logger.error(f"Communication error: {e}")
            return False

    def stream_gcode(
        self,
        gcode: List[str],
        progress_callback: Optional[Callable[[int, int], None]] = None,
        stop_flag: Optional[Callable[[], bool]] = None,
    ) -> bool:
        """
        Stream a list of G-code commands

        Args:
            gcode: List of G-code commands
            progress_callback: Optional callback(current, total)
            stop_flag: Optional function returning True to stop

        Returns:
            True if all commands executed successfully
        """
        if not self.is_connected:
            logger.error("Not connected to printer")
            return False

        total = len(gcode)
        successful = 0

        for i, line in enumerate(gcode):
            # Check stop flag
            if stop_flag and stop_flag():
                logger.info("Print stopped by user")
                # Send pen up command
                self.send_command("M5")
                return False

            if self.send_command(line):
                successful += 1
            else:
                logger.error(f"Failed at line {i}: {line}")
                return False

            if progress_callback:
                progress_callback(i + 1, total)

        logger.info(f"Stream complete: {successful}/{total} commands")
        return successful == total

    def stream_file(
        self,
        filepath: Path,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> bool:
        """Stream G-code from a file"""
        try:
            with open(filepath, "r") as f:
                gcode = f.readlines()
            return self.stream_gcode(gcode, progress_callback)
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return False

    def emergency_stop(self):
        """Emergency stop - pen up and clear buffer"""
        if self.is_connected:
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()
            self.send_command("M5")  # Pen up
            logger.warning("Emergency stop executed")
