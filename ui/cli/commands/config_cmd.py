"""Configuration commands for CLI"""

import click
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from pathlib import Path

from core.config.settings import Settings
from core.communication.serial_manager import SerialManager

console = Console()


@click.command()
@click.pass_context
def show_config(ctx):
    """Display current configuration"""
    settings: Settings = ctx.obj["settings"]

    # Create table
    table = Table(title="Current Configuration", show_header=True)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    # Serial settings
    table.add_row("Serial Port", settings.serial.port)
    table.add_row("Baudrate", str(settings.serial.baudrate))

    # Calibration
    table.add_row("", "")  # Spacer
    table.add_row("Pen Up Angle", f"{settings.calibration.pen_up_angle}°")
    table.add_row("Pen Down Angle", f"{settings.calibration.pen_down_angle}°")
    table.add_row("X Direction", str(settings.calibration.x_direction))
    table.add_row("Y Direction", str(settings.calibration.y_direction))
    table.add_row("Steps/mm X", f"{settings.calibration.steps_per_mm_x:.2f}")
    table.add_row("Steps/mm Y", f"{settings.calibration.steps_per_mm_y:.2f}")
    table.add_row("Max X", f"{settings.calibration.max_x} mm")
    table.add_row("Max Y", f"{settings.calibration.max_y} mm")
    table.add_row("Default Speed", f"{settings.calibration.default_speed} mm/min")
    table.add_row("Rapid Speed", f"{settings.calibration.rapid_speed} mm/min")

    console.print(table)


@click.command()
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.pass_context
def export_config(ctx, output):
    """Export configuration to file"""
    settings: Settings = ctx.obj["settings"]

    if not output:
        output = "config/exported_settings.yaml"

    output_path = Path(output)
    settings.save(output_path)

    console.print(f"[green]✓[/green] Configuration exported to: {output_path}")


@click.command()
@click.argument("config_file", type=click.Path(exists=True))
@click.pass_context
def load_config(ctx, config_file):
    """Load configuration from file"""
    try:
        settings = Settings.load(Path(config_file))
        ctx.obj["settings"] = settings
        console.print(f"[green]✓[/green] Configuration loaded from: {config_file}")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to load configuration: {e}")


@click.command()
@click.pass_context
def setup_wizard(ctx):
    """Interactive setup wizard"""
    console.print("[bold cyan]Setup Wizard[/bold cyan]\n")

    settings: Settings = ctx.obj["settings"]

    # Port selection
    console.print("[bold]1. Serial Port Selection[/bold]")
    ports = SerialManager.list_ports()

    if ports:
        console.print("\nAvailable ports:")
        for i, port in enumerate(ports, 1):
            console.print(f"  {i}. {port}")

        choice = Prompt.ask(
            "Select port number",
            default="1",
            choices=[str(i) for i in range(1, len(ports) + 1)],
        )
        settings.serial.port = ports[int(choice) - 1].device
    else:
        port = Prompt.ask("Enter COM port", default=settings.serial.port)
        settings.serial.port = port

    # Work area
    console.print("\n[bold]2. Work Area[/bold]")
    max_x = Prompt.ask("Maximum X (mm)", default=str(settings.calibration.max_x))
    max_y = Prompt.ask("Maximum Y (mm)", default=str(settings.calibration.max_y))
    settings.calibration.max_x = float(max_x)
    settings.calibration.max_y = float(max_y)

    # Servo angles
    console.print("\n[bold]3. Pen Servo[/bold]")
    pen_up = Prompt.ask("Pen up angle", default=str(settings.calibration.pen_up_angle))
    pen_down = Prompt.ask(
        "Pen down angle", default=str(settings.calibration.pen_down_angle)
    )
    settings.calibration.pen_up_angle = int(pen_up)
    settings.calibration.pen_down_angle = int(pen_down)

    # Save
    if Confirm.ask("\nSave configuration?", default=True):
        config_path = Path("config/local_settings.yaml")
        settings.save(config_path)
        console.print(f"[green]✓[/green] Configuration saved to: {config_path}")

    console.print("\n[bold green]Setup complete![/bold green]")
