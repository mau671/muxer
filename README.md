# MKV Muxer

An MKV file processor with automatic track naming, language configuration, and beautiful progress visualization.

## Project Structure

```
muxer/
├── app/                      # Main application code
│   ├── __init__.py          # Python package
│   ├── main.py              # Main entry point with enhanced UI
│   ├── args.py              # Argument handling
│   ├── config.py            # Configuration and constants
│   ├── metadata_handler.py  # MKV metadata handling
│   ├── track_processor.py   # Track processing logic
│   └── muxer.py            # Muxing operations with progress bar
├── run.py                   # Entry point for uv run
├── pyproject.toml          # Project configuration
└── README.md              # This file
```

## ✨ Enhanced Features

- **🎨 Beautiful Console Interface**: Rich UI with tables, panels, and colors
- **📊 Real-time Progress Bar**: Live progress tracking during processing
- **📋 Detailed Track Information**: Summary of video, audio, and subtitle tracks
- **🔍 Processing Status**: Step-by-step status updates with icons
- **🎯 Multi-file Support**: Enhanced batch processing with file counters

## Installation

### Option 1: Download Binary (Recommended)

Download the latest binary from [GitHub Releases](https://github.com/mau671/muxer/releases):

```bash
# Download and make executable
curl -L https://github.com/mau671/muxer/releases/latest/download/muxer -o muxer
chmod +x muxer
```

### Option 2: Docker

```bash
# Pull the latest image
docker pull ghcr.io/mau671/muxer:latest

# Or use docker-compose
git clone https://github.com/mau671/muxer.git
cd muxer
docker-compose up muxer
```

### Option 3: From Source

The project uses `uv` for dependency management:

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the project
git clone https://github.com/mau671/muxer.git
cd muxer
```

## Usage

### Using Binary

```bash
# Process a single file
./muxer -i file.mkv -o processed_file.mkv

# Process a directory
./muxer -i /path/to/directory -o /output/path --delete-after
```

### Using Docker

```bash
# Process files in ./data directory
docker run --rm -v $(pwd)/data:/data ghcr.io/mau671/muxer:latest -i /data

# Or with docker-compose
docker-compose run muxer-single -i /data/yourfile.mkv
```

### Using From Source

```bash
# Process a single file
uv run run.py -i file.mkv -o processed_file.mkv

# Process a directory
uv run run.py -i /path/to/directory -o /output/path --delete-after
```

### Available options

- `-i, --input`: Input file or directory (required)
- `-o, --output`: Output file or directory (optional)
- `--delete-after`: Delete source files after processing

## Functionality

### Audio Processing
- Prioritizes Spanish (Latin America) as default track
- Handles Spanish (Spain) as alternative
- Processes Japanese, Chinese, Korean, and English
- Automatically configures default tracks

### Subtitle Processing  
- Prioritizes forced subtitles in Spanish (Latin America)
- Automatically handles tags [Forced], [SDH], [CC], [Dubtitle], [AO]
- Configures default tracks based on Spanish audio presence

## Development

### Add dependencies

```bash
uv add dependency_name
```

### Run tests (when available)

```bash
uv run pytest
```

## System Requirements

- Python 3.12 or higher
- `mkvmerge` (MKVToolNix) installed on the system
- Dependencies: `rich` for enhanced console output
