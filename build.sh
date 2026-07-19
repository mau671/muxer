#!/bin/bash
# Local build script for Muxer (Go)
# Usage: ./build.sh [options]

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

show_help() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  -c, --clean         Clean previous builds"
    echo "  -d, --dev           Development build (faster, less optimized)"
    echo "  -r, --release       Release build (optimized, default)"
    echo "  -a, --arch ARCH     Specific architecture (amd64, arm64, all)"
    echo "  -o, --os OS         Specific OS (linux, windows, darwin, all)"
    echo "  -v, --verbose       Verbose output"
    echo ""
    echo "Examples:"
    echo "  $0                  # Release build for current OS and Architecture"
    echo "  $0 --clean --dev    # Clean and perform a dev build"
    echo "  $0 --os linux --arch amd64 # Build specifically for Linux AMD64"
    echo "  $0 --os all --arch all     # Build for all supported platforms"
    echo ""
}

BUILD_TYPE="release"
CLEAN=false
VERBOSE=false
TARGET_ARCH="auto"
TARGET_OS="auto"

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -c|--clean)
            CLEAN=true
            shift
            ;;
        -d|--dev)
            BUILD_TYPE="dev"
            shift
            ;;
        -r|--release)
            BUILD_TYPE="release"
            shift
            ;;
        -a|--arch)
            TARGET_ARCH="$2"
            shift 2
            ;;
        -o|--os)
            TARGET_OS="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo -e "${RED}Error: Unknown option $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

log() { echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"; }
log_success() { echo -e "${GREEN}[$(date +'%H:%M:%S')] ✓${NC} $1"; }
log_warning() { echo -e "${YELLOW}[$(date +'%H:%M:%S')] ⚠${NC} $1"; }
log_error() { echo -e "${RED}[$(date +'%H:%M:%S')] ✗${NC} $1"; }

get_current_arch() {
    case $(uname -m) in
        x86_64) echo "amd64" ;;
        aarch64|arm64) echo "arm64" ;;
        *) echo "amd64" ;;
    esac
}

get_current_os() {
    case $(uname -s) in
        Linux*) echo "linux" ;;
        Darwin*) echo "darwin" ;;
        CYGWIN*|MINGW32*|MSYS*|MINGW*) echo "windows" ;;
        *) echo "linux" ;;
    esac
}

if [ "$TARGET_ARCH" = "auto" ]; then
    TARGET_ARCH=$(get_current_arch)
fi

if [ "$TARGET_OS" = "auto" ]; then
    TARGET_OS=$(get_current_os)
fi

build_binary() {
    local os=$1
    local arch=$2
    
    local output_name="bin/muxer-${os}-${arch}"
    if [ "$os" = "windows" ]; then
        output_name="${output_name}.exe"
    fi

    log "Building for $os/$arch..."
    
    local ldflags="-X github.com/mau671/muxer/internal/cli.Version=dev"
    if [ "$BUILD_TYPE" = "release" ]; then
        ldflags="-s -w $ldflags"
    fi

    export GOOS=$os
    export GOARCH=$arch
    export CGO_ENABLED=0

    if [ "$VERBOSE" = true ]; then
        go build -v -ldflags="$ldflags" -o "$output_name" cmd/muxer/main.go
    else
        go build -ldflags="$ldflags" -o "$output_name" cmd/muxer/main.go
    fi

    log_success "Binary created at $output_name"
}

if [ "$CLEAN" = true ]; then
    log "Cleaning build directory..."
    rm -rf bin/
    log_success "Cleaned."
fi

mkdir -p bin

log "Starting $BUILD_TYPE build process..."

if [ "$TARGET_OS" = "all" ] && [ "$TARGET_ARCH" = "all" ]; then
    build_binary "linux" "amd64"
    build_binary "linux" "arm64"
    build_binary "windows" "amd64"
    build_binary "darwin" "amd64"
    build_binary "darwin" "arm64"
elif [ "$TARGET_OS" = "all" ]; then
    build_binary "linux" "$TARGET_ARCH"
    build_binary "windows" "$TARGET_ARCH"
    build_binary "darwin" "$TARGET_ARCH"
elif [ "$TARGET_ARCH" = "all" ]; then
    build_binary "$TARGET_OS" "amd64"
    build_binary "$TARGET_OS" "arm64"
else
    build_binary "$TARGET_OS" "$TARGET_ARCH"
fi

log_success "Build process completed!"
