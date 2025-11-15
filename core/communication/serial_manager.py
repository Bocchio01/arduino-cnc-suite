"""Low-level serial port management"""

import serial
import serial.tools.list_ports
from typing import List, Optional, Tuple
import logging
import time

logger = logging.getLogger(__name__)


class SerialPortInfo:
    """Information about a serial port"""

    def __init__(self, device: str, description: str, hwid: str):
        self.device = device
        self.description = description
        self.hwid = hwid

    def __str__(self) -> str:
        return f"{self.device} - {self.description}"

    def __repr__(self) -> str:
        return (
            f"SerialPortInfo(device='{self.device}', description='{self.description}')"
        )


class SerialManager:
    """Manages serial port connections and discovery"""

    @staticmethod
    def list_ports() -> List[SerialPortInfo]:
        """List all available serial ports"""
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append(
                SerialPortInfo(
                    device=port.device, description=port.description, hwid=port.hwid
                )
            )
        logger.debug(f"Found {len(ports)} serial ports")
        return ports

    @staticmethod
    def find_arduino_ports() -> List[SerialPortInfo]:
        """Find ports that are likely Arduino devices"""
        arduino_keywords = ["arduino", "ch340", "ch341", "ftdi", "usb serial"]
        ports = SerialManager.list_ports()

        arduino_ports = []
        for port in ports:
            desc_lower = port.description.lower()
            if any(keyword in desc_lower for keyword in arduino_keywords):
                arduino_ports.append(port)

        logger.info(f"Found {len(arduino_ports)} potential Arduino ports")
        return arduino_ports

    @staticmethod
    def test_connection(
        port: str, baudrate: int = 115200, timeout: float = 2.0
    ) -> Tuple[bool, Optional[str]]:
        """
        Test if a port can be opened and responds

        Returns:
            (success, message) tuple
        """
        try:
            ser = serial.Serial(port, baudrate, timeout=timeout)
            time.sleep(2)  # Wait for Arduino reset

            # Try to read startup message
            response = ser.readline().decode("utf-8", errors="ignore").strip()
            ser.close()

            if response:
                logger.info(f"Port {port} responded: {response}")
                return True, response
            else:
                logger.warning(f"Port {port} opened but no response")
                return True, "No response"

        except serial.SerialException as e:
            logger.error(f"Failed to open port {port}: {e}")
            return False, str(e)
        except Exception as e:
            logger.error(f"Unexpected error testing port {port}: {e}")
            return False, str(e)

    @staticmethod
    def auto_detect_plotter(baudrate: int = 115200) -> Optional[str]:
        """
        Automatically detect plotter by testing Arduino ports

        Returns:
            Port name if found, None otherwise
        """
        logger.info("Auto-detecting plotter...")

        arduino_ports = SerialManager.find_arduino_ports()

        for port in arduino_ports:
            logger.debug(f"Testing port: {port.device}")
            success, message = SerialManager.test_connection(port.device, baudrate)

            if success and message and "READY" in message.upper():
                logger.info(f"Found plotter on port: {port.device}")
                return port.device

        logger.warning("No plotter found")
        return None
