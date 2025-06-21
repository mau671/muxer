import os
import sys
from .args import parse_arguments
from .metadata_handler import get_mkv_metadata
from .track_processor import process_tracks
from .muxer import mux_files
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def main():
    """Main entry point for the MKV muxer application."""
    # Show application header
    console.print(Panel(
        Text("MKV Muxer", justify="center", style="bold cyan"),
        subtitle="Automatic track naming and language configuration",
        border_style="cyan"
    ))
    
    args = parse_arguments()
    
    input_path = args.input
    output_path = args.output if args.output else input_path

    if os.path.isdir(input_path):
        files = [f for f in os.listdir(input_path) if f.endswith(".mkv") and not f.endswith("_muxed.mkv")]
        files.sort()
        
        if not files:
            console.print("[yellow]⚠️  No MKV files found in the specified directory.[/yellow]")
            return
        
        console.print(f"[blue]📁 Found {len(files)} file(s) to process[/blue]\n")

        for i, file in enumerate(files, 1):
            console.print(f"[bold]Processing file {i}/{len(files)}[/bold]")
            
            input_file = os.path.join(input_path, file)
            output_file = os.path.join(
                output_path, f"{os.path.splitext(file)[0]}_muxed.mkv"
            )

            metadata = get_mkv_metadata(input_file)
            processed_tracks = process_tracks(metadata)

            mux_files(input_file, output_file, processed_tracks)

            if args.delete_after:
                os.remove(input_file)
                console.print(f"[red]🗑️  Deleted original file: {file}[/red]")
            
            # Add spacing between files
            if i < len(files):
                console.print()
    else:
        metadata = get_mkv_metadata(input_path)
        processed_tracks = process_tracks(metadata)
        
        # If no output specified or equals input, add _muxed suffix
        if output_path == input_path:
            base_name = os.path.splitext(input_path)[0]
            output_path = f"{base_name}_muxed.mkv"

        mux_files(input_path, output_path, processed_tracks)
    
    # Show completion message
    console.print("\n" + "=" * 50)
    console.print("[green]🎉 All processing completed successfully![/green]")


if __name__ == "__main__":
    main() 