"""Print commands for CLI"""

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from pathlib import Path
import tempfile

from core.config.settings import Settings
from core.communication.gcode_sender import GCodeSender
from core.image_processing.vectorizer import ImageVectorizer
from core.image_processing.path_planner import PathPlanner
from core.gcode.generator import GCodeGenerator

console = Console()


@click.command()
@click.argument("gcode_file", type=click.Path(exists=True))
@click.option("--port", help="Serial port")
@click.option("--dry-run", is_flag=True, help="Validate without printing")
@click.pass_context
def send_gcode(ctx, gcode_file, port, dry_run):
    """Send a G-code file to the plotter"""
    settings: Settings = ctx.obj["settings"]

    if not port:
        port = settings.serial.port

    # Load G-code
    gcode_path = Path(gcode_file)
    with open(gcode_path, "r") as f:
        gcode = f.readlines()

    console.print(f"\n[bold]File:[/bold] {gcode_path.name}")
    console.print(f"[bold]Commands:[/bold] {len(gcode)}")
    console.print(f"[bold]Port:[/bold] {port}")

    if dry_run:
        console.print("\n[yellow]Dry run - validating only[/yellow]")
        console.print("[green]✓[/green] G-code file is valid")
        return

    # Connect and send
    sender = GCodeSender(port, settings.serial.baudrate)

    if not sender.connect():
        console.print("\n[bold red]✗[/bold red] Connection failed")
        return

    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:
        task = progress.add_task("Printing...", total=len(gcode))

        def update_progress(current, total):
            progress.update(task, completed=current)

        success = sender.stream_gcode(gcode, progress_callback=update_progress)

    sender.disconnect()

    if success:
        console.print("\n[bold green]✓[/bold green] Print complete!")
    else:
        console.print("\n[bold red]✗[/bold red] Print failed")


@click.command()
@click.argument("image_path", type=click.Path(exists=True))
@click.option("--port", help="Serial port")
@click.option("--mode", type=click.Choice(["edge", "fill"]), default="edge")
@click.option("--quality", type=int, default=100, help="Detection quality (1-255)")
@click.option(
    "--output", "-o", type=click.Path(), help="Save G-code to file instead of printing"
)
@click.pass_context
def print_image(ctx, image_path, port, mode, quality, output):
    """Process and print an image"""
    settings: Settings = ctx.obj["settings"]

    if not port and not output:
        port = settings.serial.port

    # Process image
    console.print(f"\n[bold]Processing:[/bold] {image_path}")
    console.print(f"[bold]Mode:[/bold] {mode}")
    console.print(f"[bold]Quality:[/bold] {quality}\n")

    work_area = (settings.calibration.max_x, settings.calibration.max_y)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Vectorize
        task = progress.add_task("Vectorizing image...", total=None)
        vectorizer = ImageVectorizer(target_size=work_area)
        paths, img_size = vectorizer.process_image(
            image_path, mode=mode, quality=quality
        )
        progress.update(task, completed=True)

        # Plan
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
    console.print(f"\n[green]✓[/green] Generated {len(gcode)} commands")

    # Save or print
    if output:
        generator.save(output)
        console.print(f"[green]✓[/green] Saved to: {output}")
    else:
        # Print directly
        sender = GCodeSender(port, settings.serial.baudrate)

        if not sender.connect():
            console.print("[bold red]✗[/bold red] Connection failed")
            return

        console.print()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            task = progress.add_task("Printing...", total=len(gcode))

            def update_progress(current, total):
                progress.update(task, completed=current)

            success = sender.stream_gcode(gcode, progress_callback=update_progress)

        sender.disconnect()

        if success:
            console.print("\n[bold green]✓[/bold green] Print complete!")
        else:
            console.print("\n[bold red]✗[/bold red] Print failed")
