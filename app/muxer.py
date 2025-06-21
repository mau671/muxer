import re
import subprocess
import sys
import time
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

console = Console()


def _extract_filename(path: str) -> str:
    """Extract filename from full path for display."""
    return path.split("/")[-1] if "/" in path else path


def _show_file_info(input_file: str, output_file: str) -> None:
    """Display file processing information."""
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Input File", style="cyan")
    table.add_column("Output File", style="green")

    input_display = _extract_filename(input_file)
    output_display = _extract_filename(output_file)

    table.add_row(input_display, output_display)

    console.print(Panel(table, title="[bold]File Processing", border_style="blue"))


def _show_track_summary(tracks: list[dict[str, Any]]) -> None:
    """Display a summary of tracks to be processed."""
    video_tracks = [t for t in tracks if t["type"] == "video"]
    audio_tracks = [t for t in tracks if t["type"] == "audio"]
    subtitle_tracks = [t for t in tracks if t["type"] == "subtitles"]

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Track Type", style="cyan")
    table.add_column("Count", justify="center", style="yellow")
    table.add_column("Details", style="white")

    table.add_row("Video", str(len(video_tracks)), "H.264/AVC streams")

    # Audio track details
    audio_details = []
    for track in audio_tracks:
        name = track["properties"].get("track_name", "Unknown")
        default = (
            " (default)" if track["properties"].get("default_track", False) else ""
        )
        audio_details.append(f"{name}{default}")

    table.add_row("Audio", str(len(audio_tracks)), ", ".join(audio_details))

    # Subtitle track details
    subtitle_details = []
    for track in subtitle_tracks:
        name = track["properties"].get("track_name", "Unknown")
        default = (
            " (default)" if track["properties"].get("default_track", False) else ""
        )
        forced = " [FORCED]" if track["properties"].get("forced_track", False) else ""
        subtitle_details.append(f"{name}{default}{forced}")

    table.add_row("Subtitles", str(len(subtitle_tracks)), ", ".join(subtitle_details))

    console.print(Panel(table, title="[bold]Track Summary", border_style="green"))


def mux_files(input_file: str, output_file: str, tracks: list[dict[str, Any]]) -> None:
    """
    Combines and processes multimedia tracks using mkvmerge with progress bar.

    Args:
        input_file (str): Path to the input MKV file.
        output_file (str): Path to save the output MKV file.
        tracks (List[Dict[str, Any]]): List of track metadata to process.

    Raises:
        SystemExit: If mkvmerge fails to execute.
    """

    # Show file and track information
    _show_file_info(input_file, output_file)
    _show_track_summary(tracks)

    # Build mkvmerge command
    command = [
        "mkvmerge",
        "--ui-language",
        "en_US",
        "-v",
        "-o",
        output_file,
    ]  # Added --ui-language for English output
    track_order = []
    subtitle_tracks = []
    audio_tracks = []

    for track in tracks:
        track_id = track["id"]
        lang = track["properties"].get(
            "language_ietf", track["properties"].get("language", "und")
        )
        title = track["properties"].get("track_name", "")
        default = "yes" if track["properties"].get("default_track", False) else "no"

        if track["type"] == "subtitles":
            subtitle_tracks.append(str(track_id))

        if track["type"] == "audio":
            audio_tracks.append(str(track_id))

        command.extend(["--language", f"{track_id}:{lang}"])
        command.extend(["--default-track", f"{track_id}:{default}"])

        if title:
            command.extend(["--track-name", f"{track_id}:{title}"])

        track_order.append(f"0:{track_id}")

    if audio_tracks:
        command.extend(["--audio-tracks", ",".join(audio_tracks)])

    if subtitle_tracks:
        command.extend(["--subtitle-tracks", ",".join(subtitle_tracks)])

    command.extend(["--title", ""])
    command.extend(["--track-order", ",".join(track_order)])
    command.append(input_file)

    # Execute mkvmerge with progress tracking
    _execute_with_progress(command, output_file)


def _execute_with_progress(command: list[str], output_file: str) -> None:
    """Execute mkvmerge command with real-time progress tracking."""

    progress_pattern = re.compile(r"Progress:\s*(\d+)%")
    track_pattern = re.compile(r"track \d+:")

    start_time = time.time()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Processing MKV file...", total=100)

        # Start mkvmerge process
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
        )

        track_info_shown = False

        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break

            if output:
                line = output.strip()

                # Check for progress updates
                progress_match = progress_pattern.search(line)
                if progress_match:
                    percentage = int(progress_match.group(1))
                    progress.update(task, completed=percentage)
                    continue

                # Show track information (only once)
                if track_pattern.search(line) and not track_info_shown:
                    console.print(f"[dim]ℹ️  {line}[/dim]")
                    track_info_shown = True

                # Show other important information
                elif "has been opened for writing" in line:
                    console.print("[green]✓[/green] Output file opened for writing")
                elif "The cue entries" in line:
                    console.print("[blue]📝[/blue] Writing cue records (index)...")
                elif "Multiplexing took" in line:
                    console.print(f"[green]✓[/green] {line}")

        # Ensure progress shows 100% completion
        progress.update(task, completed=100)

        return_code = process.poll()
        total_time = time.time() - start_time

        if return_code != 0:
            console.print(
                f"[red]❌ Error executing mkvmerge with return code {return_code}[/red]"
            )
            sys.exit(1)

        # Success message
        output_display = _extract_filename(output_file)
        console.print(
            Panel(
                f"[green]✅ Successfully processed file in {total_time:.2f} seconds[/green]\n"
                f"[cyan]📁 Output: {output_display}[/cyan]",
                title="[bold green]Success",
                border_style="green",
            )
        )
