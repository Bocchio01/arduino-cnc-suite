from pathlib import Path
from typing import Optional
import yaml
from pydantic import BaseModel, Field


class SerialConfig(BaseModel):
    port: str = "COM3"
    baudrate: int = 115200
    timeout: int = 10


class CalibrationConfig(BaseModel):
    pen_up_angle: int = 90
    pen_down_angle: int = 120
    pen_servo_pin: int = 9
    pen_lift_delay: int = 300

    x_direction: int = 1
    y_direction: int = 1

    steps_per_mm_x: float = 80.0
    steps_per_mm_y: float = 80.0

    max_x: float = 250.0
    max_y: float = 250.0

    default_speed: int = 1000
    rapid_speed: int = 3000


class ImageProcessingConfig(BaseModel):
    default_quality: int = 100
    canvas_size: int = 500


class GCodeConfig(BaseModel):
    use_relative_coordinates: bool = False
    add_comments: bool = True
    line_ending: str = "\n"


class Settings(BaseModel):
    serial: SerialConfig = Field(default_factory=SerialConfig)
    calibration: CalibrationConfig = Field(default_factory=CalibrationConfig)
    image_processing: ImageProcessingConfig = Field(
        default_factory=ImageProcessingConfig
    )
    gcode: GCodeConfig = Field(default_factory=GCodeConfig)

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "Settings":
        """Load settings from YAML file"""
        if config_path is None:
            config_path = Path("config/default_settings.yaml")

        if not config_path.exists():
            return cls()

        with open(config_path, "r") as f:
            data = yaml.safe_load(f)

        return cls(**data)

    def save(self, config_path: Path):
        """Save settings to YAML file"""
        with open(config_path, "w") as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False)
