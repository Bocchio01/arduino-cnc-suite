import click
import logging
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from core.config.settings import Settings
from core.communication.gcode_sender import GCodeSender
from core.image_processing.vectorizer import ImageVectorizer
from core.image_processing.path_planner import PathPlanner
from core.gcode.generator import GCodeGenerator

console = Console()
logger = logging.getLogger(__name__)


@click.group()
@click.option("--config", type=click.Path(), help="Path to config file")
@click.option("--verbose", is_flag=True, help="Enable verbose logging")
@click.pass_context
def cli(ctx, config, verbose):
    """Arduino CNC Suite - Command Line Interface"""

    # Setup logging
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Load settings
    if config:
        settings = Settings.load(Path(config))
    else:
        settings = Settings.load()

    ctx.obj = {"settings": settings}
    console.print("[bold green]Arduino CNC Suite CLI[/bold green]")


@cli.command()
@click.pass_context
def list_ports(ctx):
    """List available serial ports"""
    import serial.tools.list_ports

    ports = serial.tools.list_ports.comports()

    if not ports:
        console.print("[yellow]No serial ports found[/yellow]")
        return

    console.print("\n[bold]Available Serial Ports:[/bold]")
    for port in ports:
        console.print(f"  • {port.device} - {port.description}")


@cli.command()
@click.option("--port", help="Serial port (e.g., COM3 or /dev/ttyUSB0)")
@click.pass_context
def connect(ctx, port):
    """Test connection to the plotter"""
    settings = ctx.obj["settings"]

    if not port:
        port = settings.serial.port

    console.print(f"Connecting to [cyan]{port}[/cyan]...")

    sender = GCodeSender(port, settings.serial.baudrate)

    if sender.connect():
        console.print("[bold green]✓[/bold green] Connected successfully!")
        sender.disconnect()
    else:
        console.print("[bold red]✗[/bold red] Connection failed")


@cli.command()
@click.argument("image_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output G-code file")
@click.option("--mode", type=click.Choice(["edge", "fill"]), default="edge")
@click.option("--quality", type=int, default=100, help="Detection quality (1-255)")
@click.option("--width", type=float, help="Target width in mm")
@click.option("--height", type=float, help="Target height in mm")
@click.pass_context
def image_to_gcode(ctx, image_path, output, mode, quality, width, height):
    """Convert an image to G-code"""
    settings = ctx.obj["settings"]

    # Set work area
    if width and height:
        work_area = (width, height)
    else:
        work_area = (settings.calibration.max_x, settings.calibration.max_y)

    console.print(f"\n[bold]Processing image:[/bold] {image_path}")
    console.print(f"Mode: {mode}, Quality: {quality}")
    console.print(f"Target size: {work_area[0]}x{work_area[1]} mm\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Vectorize image
        task = progress.add_task("Vectorizing image...", total=None)
        vectorizer = ImageVectorizer(target_size=work_area)
        paths, img_size = vectorizer.process_image(
            image_path, mode=mode, quality=quality
        )
        progress.update(task, completed=True)

        # Plan paths
        task = progress.add_task("Planning paths...", total=None)
        planner = PathPlanner()
        optimized_paths = planner.plan_from_image(paths, img_size, work_area)
        progress.update(task, completed=True)

        # Generate G-code
        task = progress.add_task("Generating G-code...", total=None)
        generator = GCodeGenerator(
            feed_rate=settings.calibration.default_speed,
            rapid_rate=settings.calibration.rapid_speed,
        )
        generator.header()

        for path in optimized_paths:
            generator.draw_polyline(path)

        generator.footer()
        progress.update(task, completed=True)

    gcode = generator.get_gcode()

    # Save or print
    if output:
        generator.save(output)
        console.print(f"\n[green]✓[/green] G-code saved to: {output}")
    else:
        console.print("\n[bold]Generated G-code:[/bold]")
        for line in gcode[:20]:  # Show first 20 lines
            console.print(f"  {line}")
        if len(gcode) > 20:
            console.print(f"  ... ({len(gcode) - 20} more lines)")

    console.print(f"\nTotal commands: {len(gcode)}")


@cli.command()
@click.argument("gcode_file", type=click.Path(exists=True))
@click.option("--port", help="Serial port")
@click.pass_context
def print_gcode(ctx, gcode_file, port):
    """Send G-code file to the plotter"""
    settings = ctx.obj["settings"]

    if not port:
        port = settings.serial.port

    # Load G-code
    with open(gcode_file, "r") as f:
        gcode = f.readlines()

    console.print(f"\n[bold]Printing:[/bold] {gcode_file}")
    console.print(f"Commands: {len(gcode)}")
    console.print(f"Port: {port}\n")

    # Connect
    sender = GCodeSender(port, settings.serial.baudrate)
    if not sender.connect():
        console.print("[bold red]✗[/bold red] Connection failed")
        return

    # Stream with progress
    with Progress(console=console) as progress:
        task = progress.add_task("Printing...", total=len(gcode))

        def update_progress(current, total):
            progress.update(task, completed=current)

        success = sender.stream_gcode(gcode, progress_callback=update_progress)

    sender.disconnect()

    if success:
        console.print("\n[bold green]✓[/bold green] Print complete!")
    else:
        console.print("\n[bold red]✗[/bold red] Print failed")


@cli.command()
@click.argument("image_path", type=click.Path(exists=True))
@click.option("--port", help="Serial port")
@click.option("--mode", type=click.Choice(["edge", "fill"]), default="edge")
@click.option("--quality", type=int, default=100)
@click.pass_context
def print_image(ctx, image_path, port, mode, quality):
    """Process and print an image directly"""
    import tempfile

    # Generate G-code to temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".gcode", delete=False) as f:
        temp_gcode = f.name

    ctx.invoke(
        image_to_gcode,
        image_path=image_path,
        output=temp_gcode,
        mode=mode,
        quality=quality,
    )

    # Print the G-code
    ctx.invoke(print_gcode, gcode_file=temp_gcode, port=port)

    # Cleanup
    Path(temp_gcode).unlink()


if __name__ == "__main__":
    cli()
