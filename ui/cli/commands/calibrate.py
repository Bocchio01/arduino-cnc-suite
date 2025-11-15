"""Calibration commands for CLI"""

import click
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

from core.config.settings import Settings
from core.communication.gcode_sender import GCodeSender
from core.calibration.calibrator import Calibrator

console = Console()


@click.command()
@click.option("--port", help="Serial port")
@click.pass_context
def calibrate(ctx, port):
    """Interactive calibration wizard"""
    settings: Settings = ctx.obj["settings"]

    if not port:
        port = settings.serial.port

    console.print(
        Panel.fit(
            "[bold cyan]Calibration Wizard[/bold cyan]\n"
            "This will guide you through calibrating your plotter",
            border_style="cyan",
        )
    )

    # Connect
    console.print(f"\n[yellow]Connecting to {port}...[/yellow]")
    sender = GCodeSender(port, settings.serial.baudrate)

    if not sender.connect():
        console.print("[bold red]✗[/bold red] Connection failed")
        return

    console.print("[bold green]✓[/bold green] Connected\n")

    calibrator = Calibrator(sender, settings.calibration)

    # Step 1: Servo angles
    if Confirm.ask("Test pen servo angles?", default=True):
        console.print("\n[bold]Step 1: Pen Servo Calibration[/bold]")

        up_angle = Prompt.ask(
            "Pen up angle (degrees)", default=str(settings.calibration.pen_up_angle)
        )
        down_angle = Prompt.ask(
            "Pen down angle (degrees)", default=str(settings.calibration.pen_down_angle)
        )

        def status_callback(msg):
            console.print(f"  {msg}")

        calibrator.test_pen_servo(
            int(up_angle), int(down_angle), callback=status_callback
        )

        if Confirm.ask("Save these angles?", default=True):
            settings.calibration.pen_up_angle = int(up_angle)
            settings.calibration.pen_down_angle = int(down_angle)
            console.print("[green]✓[/green] Saved")

    # Step 2: Movement test
    if Confirm.ask("\nTest axis movement?", default=True):
        console.print("\n[bold]Step 2: Axis Movement Test[/bold]")

        distance = Prompt.ask("Test distance (mm)", default="50")

        def status_callback(msg):
            console.print(f"  {msg}")

        calibrator.test_movement(float(distance), callback=status_callback)

        # Ask about direction
        if not Confirm.ask("Did X axis move in the correct direction?", default=True):
            settings.calibration.x_direction *= -1
            console.print("[yellow]✓[/yellow] X direction reversed")

        if not Confirm.ask("Did Y axis move in the correct direction?", default=True):
            settings.calibration.y_direction *= -1
            console.print("[yellow]✓[/yellow] Y direction reversed")

    # Step 3: Test pattern
    if Confirm.ask("\nDraw test pattern?", default=True):
        console.print("\n[bold]Step 3: Test Pattern[/bold]")

        size = Prompt.ask("Pattern size (mm)", default="50")

        def status_callback(msg):
            console.print(f"  {msg}")

        calibrator.draw_test_pattern(float(size), callback=status_callback)

    # Save settings
    if Confirm.ask("\nSave calibration settings?", default=True):
        from pathlib import Path

        config_path = Path("config/local_settings.yaml")
        settings.save(config_path)
        console.print(f"[green]✓[/green] Settings saved to {config_path}")

    sender.disconnect()
    console.print("\n[bold green]Calibration complete![/bold green]")


@click.command()
@click.option("--port", help="Serial port")
@click.option("--size", type=float, default=50, help="Pattern size in mm")
@click.pass_context
def test_pattern(ctx, port, size):
    """Draw a test pattern"""
    settings: Settings = ctx.obj["settings"]

    if not port:
        port = settings.serial.port

    console.print(f"Drawing test pattern ({size}x{size} mm)...")

    sender = GCodeSender(port, settings.serial.baudrate)

    if not sender.connect():
        console.print("[bold red]✗[/bold red] Connection failed")
        return

    calibrator = Calibrator(sender, settings.calibration)

    def status_callback(msg):
        console.print(f"  {msg}")

    success = calibrator.draw_test_pattern(size, callback=status_callback)

    sender.disconnect()

    if success:
        console.print("[bold green]✓[/bold green] Test complete")
    else:
        console.print("[bold red]✗[/bold red] Test failed")
