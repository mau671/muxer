# MKV Muxer

An MKV file processor with automatic track naming, language configuration, and beautiful progress visualization, completely rewritten in Go.

## Enhanced Features

- **Ultra Fast**: Built in Go 1.26 for maximum performance.
- **Zero-Dependencies**: Automatically downloads the required `mkvmerge` binaries if they are not installed on your system. You don't need to install MKVToolNix manually anymore!
- **Beautiful Console Interface**: Rich UI with live progress bars powered by Bubbletea and Lipgloss.
- **Detailed Track Processing**: Automatic business rules for Latin American Spanish, Japanese, English, forced tracks, and more.

## Installation

```bash
# Clone the repository
git clone https://github.com/mau671/muxer.git
cd muxer

# Build the binary
go build -o muxer cmd/muxer/main.go
```

## Usage

```bash
# Process a single file
./muxer -i file.mkv -o processed_file.mkv

# The system will automatically download mkvmerge on the first run if you don't have it!
```

### Available options

- `-i, --input`: Input file or directory (required)
- `-o, --output`: Output file or directory (optional)
- `--delete-after`: Delete source files after processing

## Testing

```bash
go test ./...
```
