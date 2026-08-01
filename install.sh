#!/bin/sh
set -e

# Muxer Installation Script for Linux & macOS
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/mau671/muxer/main/install.sh | bash
#
# Options (via environment variables):
#   MUXER_SYSTEM=1   Install to /usr/local/bin instead of ~/.local/bin (requires root or sudo/doas)
#   MUXER_DIR=/path  Install to a custom directory

REPO="mau671/muxer"
BIN_NAME="muxer"

echo "Detecting OS and Architecture..."
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

# Map architecture to standard Go release names
case "$ARCH" in
    x86_64)          ARCH="amd64" ;;
    aarch64|arm64)   ARCH="arm64" ;;
    *) echo "Unsupported architecture: $ARCH"; exit 1 ;;
esac

# Fetch latest release data from GitHub API
echo "Fetching latest release information..."
LATEST_RELEASE=$(curl -s "https://api.github.com/repos/$REPO/releases/latest")
VERSION=$(echo "$LATEST_RELEASE" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/' | tr -d 'v')

if [ -z "$VERSION" ]; then
    echo "Failed to fetch latest version. Please check your internet connection or GitHub API limits."
    exit 1
fi

echo "Latest version found: $VERSION"

# ── Privilege helper ───────────────────────────────────────────────────────────

# Try to run a command with elevated privileges (sudo, doas, or direct if root).
# Returns 0 on success, 1 if no privilege escalation tool is available.
_run_privileged() {
    if [ "$(id -u)" -eq 0 ]; then
        "$@"
    elif command -v sudo >/dev/null 2>&1; then
        sudo "$@"
    elif command -v doas >/dev/null 2>&1; then
        doas "$@"
    else
        return 1
    fi
}

# ── Determine install directory ────────────────────────────────────────────────

if [ -n "$MUXER_DIR" ]; then
    # Explicit custom directory
    INSTALL_DIR="$MUXER_DIR"
    NEED_PRIV=0
elif [ "${MUXER_SYSTEM:-0}" = "1" ] || [ "$(id -u)" -eq 0 ]; then
    # System-wide install: either requested explicitly or we are already root
    INSTALL_DIR="/usr/local/bin"
    NEED_PRIV=1
else
    # Default: user-local install (no sudo required)
    INSTALL_DIR="${HOME}/.local/bin"
    NEED_PRIV=0
fi

# ── Download ───────────────────────────────────────────────────────────────────

# Format matches the GoReleaser naming convention: muxer_VERSION_os_arch.tar.gz
ASSET_NAME="${BIN_NAME}_${VERSION}_${OS}_${ARCH}.tar.gz"
DOWNLOAD_URL="https://github.com/$REPO/releases/download/v${VERSION}/${ASSET_NAME}"

TMP_DIR=$(mktemp -d)
# Ensure cleanup on exit
trap 'rm -rf "$TMP_DIR"' EXIT

echo "Downloading $ASSET_NAME..."
curl -L --fail -o "$TMP_DIR/release.tar.gz" "$DOWNLOAD_URL"

echo "Extracting binary..."
tar -xzf "$TMP_DIR/release.tar.gz" -C "$TMP_DIR" "$BIN_NAME"

# ── Install ────────────────────────────────────────────────────────────────────

if [ "$NEED_PRIV" -eq 0 ]; then
    mkdir -p "$INSTALL_DIR"
    mv "$TMP_DIR/$BIN_NAME" "$INSTALL_DIR/$BIN_NAME"
    chmod +x "$INSTALL_DIR/$BIN_NAME"
else
    if ! _run_privileged mkdir -p "$INSTALL_DIR" || \
       ! _run_privileged mv "$TMP_DIR/$BIN_NAME" "$INSTALL_DIR/$BIN_NAME" || \
       ! _run_privileged chmod +x "$INSTALL_DIR/$BIN_NAME"; then
        echo ""
        echo "Error: root privileges required but neither sudo nor doas is available."
        echo "Re-run as root, or omit MUXER_SYSTEM=1 to install to ~/.local/bin instead."
        exit 1
    fi
fi

echo ""
echo "✅ Successfully installed Muxer v$VERSION to $INSTALL_DIR/$BIN_NAME"

# ── PATH warning ───────────────────────────────────────────────────────────────

case ":${PATH}:" in
    *":${INSTALL_DIR}:"*)
        # Already in PATH, nothing to do
        ;;
    *)
        echo ""
        echo "⚠️  '$INSTALL_DIR' is not in your PATH."
        echo "   Add this line to your shell profile (~/.bashrc, ~/.zshrc, ~/.profile, etc.):"
        echo ""
        echo "     export PATH=\"\$PATH:$INSTALL_DIR\""
        echo ""
        ;;
esac

echo "Run 'muxer --help' to get started."
