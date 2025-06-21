# Base image for Python and UV
FROM ghcr.io/astral-sh/uv:python3.12-alpine AS runtime

# Accept version as build argument
ARG VERSION=0.1.0

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
COPY pyproject.toml uv.lock README.md LICENSE ./
COPY app/ ./app/
COPY run.py ./

# Set version environment variable for hatch-vcs
ENV SETUPTOOLS_SCM_PRETEND_VERSION_FOR_MUXER=$VERSION

# Synchronize the environment with UV (without requiring git metadata)
RUN uv sync --frozen --no-dev

# Configure the PATH to include the virtual environment created by UV
ENV PATH="/app/.venv/bin:$PATH"

# Create volume mount points
VOLUME ["/data"]

# Use ENTRYPOINT to properly handle arguments with the new entry point
ENTRYPOINT ["uv", "run", "run.py"]
