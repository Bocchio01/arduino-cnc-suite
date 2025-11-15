import pytest
from core.gcode.generator import GCodeGenerator


def test_header_generation():
    gen = GCodeGenerator()
    gen.header()
    gcode = gen.get_gcode()

    assert "G21" in gcode  # Units: mm
    assert "G90" in gcode  # Absolute positioning
    assert "G28" in gcode  # Home


def test_pen_control():
    gen = GCodeGenerator(pen_up_cmd="M5", pen_down_cmd="M3 S90")

    gen.pen_up()
    gen.pen_down()
    gen.pen_up()

    gcode = gen.get_gcode()
    assert gcode.count("M5") == 2  # Two pen ups
    assert gcode.count("M3 S90") == 1  # One pen down


def test_line_drawing():
    gen = GCodeGenerator()
    gen.header()
    gen.draw_line(0, 0, 10, 10)
    gen.footer()

    gcode = gen.get_gcode()
    assert "G0 X0.000 Y0.000" in gcode  # Rapid to start
    assert "G1 X10.000 Y10.000" in gcode  # Linear move


def test_rectangle():
    gen = GCodeGenerator()
    gen.draw_rectangle(10, 10, 50, 30)

    gcode = gen.get_gcode()
    assert "X10.000 Y10.000" in gcode
    assert "X60.000" in gcode  # 10 + 50
    assert "Y40.000" in gcode  # 10 + 30


def test_circle_segmentation():
    gen = GCodeGenerator()
    gen.draw_circle(50, 50, 25, segments=36)

    gcode = gen.get_gcode()
    # Should have 37 move commands (36 segments + 1 to close)
    move_commands = [line for line in gcode if line.startswith("G1")]
    assert len(move_commands) == 37


def test_polyline():
    gen = GCodeGenerator()
    points = [(0, 0), (10, 0), (10, 10), (0, 10)]
    gen.draw_polyline(points)

    gcode = gen.get_gcode()
    assert len([l for l in gcode if l.startswith("G1")]) == 3
