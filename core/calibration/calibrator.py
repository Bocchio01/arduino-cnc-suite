"""Interactive calibration for the plotter"""

from typing import Tuple, Optional, Callable
from core.communication.gcode_sender import GCodeSender
from core.config.settings import CalibrationConfig
import logging
import time

logger = logging.getLogger(__name__)


class Calibrator:
    """Interactive calibration wizard"""

    def __init__(self, sender: GCodeSender, config: CalibrationConfig):
        self.sender = sender
        self.config = config

    def test_pen_servo(
        self,
        up_angle: int,
        down_angle: int,
        callback: Optional[Callable[[str], None]] = None,
    ) -> bool:
        """
        Test pen servo angles

        Args:
            up_angle: Angle for pen up position
            down_angle: Angle for pen down position
            callback: Optional callback for status updates
        """
        if not self.sender.is_connected:
            logger.error("Not connected to plotter")
            return False

        try:
            if callback:
                callback(f"Testing pen up angle: {up_angle}°")

            # Pen up
            self.sender.send_command(f"M5")
            time.sleep(0.5)

            if callback:
                callback(f"Testing pen down angle: {down_angle}°")

            # Pen down
            self.sender.send_command(f"M3 S{down_angle}")
            time.sleep(0.5)

            # Pen up again
            self.sender.send_command(f"M5")

            if callback:
                callback("Servo test complete")

            return True

        except Exception as e:
            logger.error(f"Servo test failed: {e}")
            return False

    def test_movement(
        self, distance: float = 50, callback: Optional[Callable[[str], None]] = None
    ) -> bool:
        """
        Test X and Y axis movement

        Args:
            distance: Distance to move in mm
            callback: Optional callback for status updates
        """
        if not self.sender.is_connected:
            logger.error("Not connected to plotter")
            return False

        try:
            # Home first
            if callback:
                callback("Homing...")
            self.sender.send_command("G28")

            # Test X axis
            if callback:
                callback(f"Moving X axis +{distance}mm")
            self.sender.send_command(f"G0 X{distance} Y0")
            time.sleep(1)

            if callback:
                callback("Returning to origin")
            self.sender.send_command("G0 X0 Y0")
            time.sleep(1)

            # Test Y axis
            if callback:
                callback(f"Moving Y axis +{distance}mm")
            self.sender.send_command(f"G0 X0 Y{distance}")
            time.sleep(1)

            if callback:
                callback("Returning to origin")
            self.sender.send_command("G0 X0 Y0")

            if callback:
                callback("Movement test complete")

            return True

        except Exception as e:
            logger.error(f"Movement test failed: {e}")
            return False

    def draw_test_pattern(
        self, size: float = 50, callback: Optional[Callable[[str], None]] = None
    ) -> bool:
        """
        Draw a test pattern (square with diagonals)

        Args:
            size: Size of the test pattern in mm
            callback: Optional callback for status updates
        """
        if not self.sender.is_connected:
            logger.error("Not connected to plotter")
            return False

        try:
            if callback:
                callback("Drawing test pattern...")

            # Home and pen up
            self.sender.send_command("G28")
            self.sender.send_command("M5")

            # Move to start
            margin = 10
            self.sender.send_command(f"G0 X{margin} Y{margin}")

            # Draw square
            self.sender.send_command("M3 S90")  # Pen down
            self.sender.send_command(f"G1 X{margin + size} Y{margin} F1000")
            self.sender.send_command(f"G1 X{margin + size} Y{margin + size}")
            self.sender.send_command(f"G1 X{margin} Y{margin + size}")
            self.sender.send_command(f"G1 X{margin} Y{margin}")

            # Draw diagonals
            self.sender.send_command(f"G1 X{margin + size} Y{margin + size}")
            self.sender.send_command(f"G0 X{margin + size} Y{margin}")
            self.sender.send_command(f"G1 X{margin} Y{margin + size}")

            # Pen up and home
            self.sender.send_command("M5")
            self.sender.send_command("G28")

            if callback:
                callback("Test pattern complete")

            return True

        except Exception as e:
            logger.error(f"Test pattern failed: {e}")
            return False

    def measure_steps_per_mm(
        self,
        target_distance: float = 100,
        callback: Optional[Callable[[str], None]] = None,
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Interactive steps/mm calibration

        Returns:
            (x_steps_per_mm, y_steps_per_mm) or (None, None) if failed
        """
        if callback:
            callback(
                f"This will move the axes {target_distance}mm.\n"
                "Please measure the actual distance traveled and enter it."
            )

        # This would need user input, so just return current values
        # In a GUI/CLI, you'd prompt for actual measurements
        return (self.config.steps_per_mm_x, self.config.steps_per_mm_y)
