"""Printer profile management for different hardware configurations"""

from pathlib import Path
from typing import Optional, Dict, Any
import yaml
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class HardwareConfig(BaseModel):
    """Hardware specification"""

    controller: str = "Arduino Uno"
    shield: str = "Adafruit Motor Shield v2"
    stepper_motor_1: str = "NEMA 17"
    stepper_motor_2: str = "NEMA 17"
    servo: str = "SG90"


class PinConfig(BaseModel):
    """Pin assignments"""

    stepper_x_port: int = 1
    stepper_y_port: int = 2
    servo_pin: int = 9


class MechanicsConfig(BaseModel):
    """Mechanical configuration"""

    steps_per_revolution: int = 200
    microsteps: int = 8
    belt_pitch: float = 2.0  # mm
    pulley_teeth: int = 20


class StepsPerMM(BaseModel):
    """Steps per millimeter for each axis"""

    x: float = 40.0
    y: float = 40.0


class PrinterProfile(BaseModel):
    """Complete printer profile"""

    name: str
    description: str = ""
    hardware: HardwareConfig = Field(default_factory=HardwareConfig)
    pins: PinConfig = Field(default_factory=PinConfig)
    mechanics: MechanicsConfig = Field(default_factory=MechanicsConfig)
    steps_per_mm: StepsPerMM = Field(default_factory=StepsPerMM)

    @classmethod
    def load(cls, profile_path: Path) -> "PrinterProfile":
        """Load printer profile from YAML file"""
        if not profile_path.exists():
            raise FileNotFoundError(f"Profile not found: {profile_path}")

        with open(profile_path, "r") as f:
            data = yaml.safe_load(f)

        logger.info(f"Loaded printer profile: {data.get('name', 'Unknown')}")
        return cls(**data)

    def save(self, profile_path: Path):
        """Save printer profile to YAML file"""
        profile_path.parent.mkdir(parents=True, exist_ok=True)

        with open(profile_path, "w") as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False)

        logger.info(f"Saved printer profile to: {profile_path}")

    def calculate_steps_per_mm(self) -> StepsPerMM:
        """Calculate steps per mm from mechanical parameters"""
        steps_per_mm = (
            self.mechanics.steps_per_revolution * self.mechanics.microsteps
        ) / (self.mechanics.belt_pitch * self.mechanics.pulley_teeth)

        return StepsPerMM(x=steps_per_mm, y=steps_per_mm)
