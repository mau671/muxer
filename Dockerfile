# Base image for Python and UV
FROM ghcr.io/astral-sh/uv:python3.12-alpine AS runtime

# Install MKVToolNix and necessary dependencies
RUN apk add --no-cache \
    mkvtoolnix \
    boost-filesystem \
    boost-regex \
    boost-system \
    libmatroska \
    libogg \
    libvorbis \
    cmark

# Create directory for the application
WORKDIR /app

# Copy the project to the container
COPY . /app

# Synchronize the environment with UV
RUN uv sync --frozen

# Configure the PATH to include the virtual environment created by UV
ENV PATH="/app/.venv/bin:$PATH"

# Use ENTRYPOINT to properly handle arguments
ENTRYPOINT ["uv", "run", "main.py"]
