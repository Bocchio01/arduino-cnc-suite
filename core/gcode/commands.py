"""G-code command definitions and utilities"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class CommandType(Enum):
    """G-code command types"""

    # Motion commands
    RAPID_MOVE = "G0"  # Rapid positioning
    LINEAR_MOVE = "G1"  # Linear interpolation
    ARC_CW = "G2"  # Circular interpolation, clockwise
    ARC_CCW = "G3"  # Circular interpolation, counter-clockwise

    # Coordinate system
    ABSOLUTE = "G90"  # Absolute positioning
    RELATIVE = "G91"  # Relative positioning

    # Units
    UNITS_MM = "G21"  # Set units to millimeters
    UNITS_INCH = "G20"  # Set units to inches

    # Machine control
    HOME = "G28"  # Home all axes
    DWELL = "G4"  # Dwell (pause)

    # Pen/Spindle control
    PEN_DOWN = "M3"  # Pen down (spindle on)
    PEN_UP = "M5"  # Pen up (spindle off)

    # Program control
    PROGRAM_END = "M2"  # Program end
    OPTIONAL_STOP = "M1"  # Optional stop


@dataclass
class GCodeCommand:
    """Represents a single G-code command"""

    command_type: CommandType
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None
    feed_rate: Optional[float] = None
    spindle_speed: Optional[int] = None
    dwell_time: Optional[float] = None
    comment: Optional[str] = None

    def to_string(self) -> str:
        """Convert command to G-code string"""
        parts = [self.command_type.value]

        # Add coordinates
        if self.x is not None:
            parts.append(f"X{self.x:.3f}")
        if self.y is not None:
            parts.append(f"Y{self.y:.3f}")
        if self.z is not None:
            parts.append(f"Z{self.z:.3f}")

        # Add feed rate
        if self.feed_rate is not None:
            parts.append(f"F{self.feed_rate:.0f}")

        # Add spindle speed
        if self.spindle_speed is not None:
            parts.append(f"S{self.spindle_speed}")

        # Add dwell time
        if self.dwell_time is not None:
            parts.append(f"P{self.dwell_time:.3f}")

        # Build command string
        cmd_string = " ".join(parts)

        # Add comment if present
        if self.comment:
            cmd_string += f" ; {self.comment}"

        return cmd_string

    def __str__(self) -> str:
        return self.to_string()


class GCodeBuilder:
    """Helper class for building G-code commands"""

    @staticmethod
    def rapid_move(x: float, y: float, comment: Optional[str] = None) -> GCodeCommand:
        """Create a rapid move command"""
        return GCodeCommand(
            command_type=CommandType.RAPID_MOVE, x=x, y=y, comment=comment
        )

    @staticmethod
    def linear_move(
        x: float,
        y: float,
        feed_rate: Optional[float] = None,
        comment: Optional[str] = None,
    ) -> GCodeCommand:
        """Create a linear move command"""
        return GCodeCommand(
            command_type=CommandType.LINEAR_MOVE,
            x=x,
            y=y,
            feed_rate=feed_rate,
            comment=comment,
        )

    @staticmethod
    def pen_up(comment: Optional[str] = None) -> GCodeCommand:
        """Create a pen up command"""
        return GCodeCommand(command_type=CommandType.PEN_UP, comment=comment)

    @staticmethod
    def pen_down(
        spindle_speed: int = 90, comment: Optional[str] = None
    ) -> GCodeCommand:
        """Create a pen down command"""
        return GCodeCommand(
            command_type=CommandType.PEN_DOWN,
            spindle_speed=spindle_speed,
            comment=comment,
        )

    @staticmethod
    def home(comment: Optional[str] = None) -> GCodeCommand:
        """Create a home command"""
        return GCodeCommand(command_type=CommandType.HOME, comment=comment)

    @staticmethod
    def dwell(seconds: float, comment: Optional[str] = None) -> GCodeCommand:
        """Create a dwell (pause) command"""
        return GCodeCommand(
            command_type=CommandType.DWELL, dwell_time=seconds, comment=comment
        )
