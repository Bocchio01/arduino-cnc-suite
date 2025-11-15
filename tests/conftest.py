import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary config file"""
    config_content = """
printer:
  name: "Test Suite"

serial:
  port: "COM99"
  baudrate: 115200

calibration:
  pen_up_angle: 90
  pen_down_angle: 120
  max_x: 250
  max_y: 250
"""

    config_file = tmp_path / "test_config.yaml"
    config_file.write_text(config_content)
    return config_file
