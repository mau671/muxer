# Muxer

Muxer is a lightning-fast, zero-configuration CLI tool designed to automate and standardize Matroska (MKV) metadata and tracks. It intelligently parses your MKV files, applies predefined rules for audio and subtitles, renaming tracks and setting correct disposition flags (like Default and Forced) instantly.

Stop spending hours manually tagging and reordering tracks in MKVToolNix GUI. **Muxer** does it all automatically.

## ✨ Core Features

* **Intelligent Track Prioritization**: Automatically prioritizes **Spanish (Latin America)** audio as the default track. If not found, it falls back to Spanish (Spain), Japanese, or English.
* **Smart Subtitle Tagging**: Detects forced subtitles and automatically appends tags like `[Forced]`, `[SDH]`, `[CC]`, `[AO]`, and `[Dubtitle]` based on internal metadata.
* **Automatic MKVToolNix Management**: Muxer requires `mkvmerge` to do the heavy lifting. Don't have it installed? No problem. Muxer **automatically downloads and caches** the official portable `mkvmerge` binaries for your OS on the first run.
* **Beautiful TUI**: Enjoy a rich Terminal User Interface (powered by Bubbletea) with live progress bars, spinners, and colorful track summaries while your files are processed.
* **Clean Metadata**: Automatically strips out unnecessary junk metadata, like default video track titles, keeping your library perfectly clean for media servers like Plex, Jellyfin, and Emby.

## 🚀 Installation

### Option 1: Download the standalone binary (Recommended)

You can grab the latest pre-compiled binary for your system (Windows, macOS, or Linux) from our [Releases page](../../releases). 
No dependencies required! Just download and run.

### Option 2: Using Docker

```bash
docker pull ghcr.io/mau671/muxer:latest

# Process files in your local /data directory
docker run --rm -v $(pwd)/data:/data ghcr.io/mau671/muxer:latest -i /data/movie.mkv
```

### Option 3: Compile from source

If you have Go 1.26+ installed:

```bash
git clone https://github.com/mau671/muxer.git
cd muxer
./build.sh
```
Your binary will be ready inside the `bin/` directory.

## 💻 Usage

```bash
# Process a single file
./muxer -i my_movie.mkv

# Process a single file and specify the output name
./muxer -i my_movie.mkv -o output_clean.mkv

# Process and delete the original source file
./muxer -i episode01.mkv --delete-after
```

### Available Flags

* `-i, --input`: Input MKV file (required).
* `-o, --output`: Output MKV file path (optional, defaults to `<filename>_processed.mkv`).
* `--delete-after`: Automatically deletes the original source file after the muxing is successfully completed.

## 🧠 How the Rules Work

Muxer was built to satisfy specific media library standards:

1. **Audio**: Searches for `es-419`, `spa`, or `lat` tags. Renames the track to `Spanish (Latin America)` and sets it as the default audio track.
2. **Subtitles**: Any subtitle marked as forced or containing "signs" or "forzad" in its original title will be tagged as `[Forced]` and marked as the default subtitle track if Latin American audio is present.
3. **Video**: Strips the video track title (making it blank) to ensure Plex/Jellyfin players do not display generic or scene group names.

## 🤝 Contributing

Contributions are welcome! Check out the `CONTRIBUTING.md` file for details on how to set up the development environment, run the test suite, and submit pull requests.
