# Contributing to MKV Muxer

Thank you for your interest in contributing to MKV Muxer! This document provides guidelines for development and contributions.

## Development Setup

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- MKVToolNix installed on your system
- Docker (optional, for container testing)

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mau671/muxer.git
   cd muxer
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Run the application:**
   ```bash
   uv run run.py --help
   ```

### Testing

Test the application with sample MKV files:

```bash
# Test with a single file
uv run run.py -i /path/to/test.mkv

# Test with a directory
uv run run.py -i /path/to/test/directory/
```

### Docker Development

Build and test the Docker image locally:

```bash
# Build the image
docker build -t muxer:dev .

# Test the image
docker run --rm -v $(pwd)/data:/data muxer:dev -i /data --help
```

## Code Style

- Follow PEP 8 python style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and small

## Project Structure

```
muxer/
├── app/                    # Main application code
│   ├── __init__.py        # Package initialization
│   ├── main.py            # Main entry point
│   ├── args.py            # Command line argument parsing
│   ├── config.py          # Configuration constants
│   ├── metadata_handler.py # MKV metadata operations
│   ├── track_processor.py  # Track processing logic
│   └── muxer.py           # Muxing operations with UI
├── run.py                 # Application entry point
├── data/                  # Test data directory (not in repo)
├── .github/workflows/     # CI/CD workflows
├── Dockerfile            # Container image definition
└── docker-compose.yaml  # Docker compose configuration
```

## Submitting Changes

1. **Fork the repository**
2. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
4. **Test your changes thoroughly**
5. **Commit with descriptive messages:**
   ```bash
   git commit -m "Add: description of your changes"
   ```

6. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**

## Pull Request Guidelines

- Provide a clear description of the changes
- Include test cases for new functionality
- Ensure all existing tests pass
- Update documentation if necessary
- Follow the existing code style

## Release Process

Releases are automated via GitHub Actions:

1. **Every push to `main`** triggers:
   - Automated testing
   - Binary compilation
   - Docker image build
   - Automatic release creation

2. **Version naming:** `YYYY.MM.DD-{git-hash}`
   - Example: `2024.03.15-a1b2c3d`

3. **Artifacts included:**
   - Linux x64 binary
   - Docker images (latest + versioned)
   - Automatic changelog generation

## Issues and Bug Reports

When reporting bugs:

1. Include your operating system and Python version
2. Provide the exact command you ran
3. Include any error messages
4. Attach sample files if possible (small test cases)

## Feature Requests

We welcome feature requests! Please:

1. Check existing issues first
2. Provide a clear use case
3. Explain the expected behavior
4. Consider if it fits the project scope

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain a welcoming environment

## Need Help?

- Open an issue for bugs or feature requests
- Check existing documentation
- Look at the test files for examples