#!/bin/sh
set -e

# Muxer Installation Script for Linux & macOS

REPO="mau671/muxer"
BIN_NAME="muxer"

echo "Detecting OS and Architecture..."
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

# Map architecture to standard Go release names
case "$ARCH" in
    x86_64) ARCH="amd64" ;;
    aarch64|arm64) ARCH="arm64" ;;
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

# Format matches the new GoReleaser naming convention: muxer_VERSION_os_arch.tar.gz
ASSET_NAME="${BIN_NAME}_${VERSION}_${OS}_${ARCH}.tar.gz"
DOWNLOAD_URL="https://github.com/$REPO/releases/download/v${VERSION}/${ASSET_NAME}"

# Temporary directory for download
TMP_DIR=$(mktemp -d)
cd "$TMP_DIR"

echo "Downloading $ASSET_NAME..."
curl -L -o release.tar.gz "$DOWNLOAD_URL"

echo "Extracting binary..."
tar -xzf release.tar.gz "$BIN_NAME"

echo "Installing to /usr/local/bin (may require sudo)..."
sudo mv "$BIN_NAME" /usr/local/bin/
sudo chmod +x /usr/local/bin/"$BIN_NAME"

# Clean up
cd - > /dev/null
rm -rf "$TMP_DIR"

echo "✅ Successfully installed Muxer v$VERSION to /usr/local/bin/$BIN_NAME"
echo "Run 'muxer --help' to get started."
