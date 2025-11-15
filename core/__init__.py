"""
Arduino CNC Suite - Core Module
Professional CNC plotter software with standard G-code support
"""

__version__ = "2.0.0"
__author__ = "Tommaso Bocchietti"

from core.config.settings import Settings
from core.gcode.generator import GCodeGenerator
from core.communication.gcode_sender import GCodeSender

__all__ = [
    "Settings",
    "GCodeGenerator",
    "GCodeSender",
]
