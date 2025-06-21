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

# Copy project files to container
COPY pyproject.toml uv.lock ./
COPY app/ ./app/
COPY run.py ./

# Synchronize the environment with UV
RUN uv sync --frozen

# Configure the PATH to include the virtual environment created by UV
ENV PATH="/app/.venv/bin:$PATH"

# Create volume mount points
VOLUME ["/data"]

# Use ENTRYPOINT to properly handle arguments with the new entry point
ENTRYPOINT ["uv", "run", "run.py"]
