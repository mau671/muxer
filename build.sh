#!/bin/bash

# Script para builds locales del proyecto Muxer
# Autor: Mauricio González Prendas
# Uso: ./build.sh [opciones]

set -e  # Salir en caso de error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar ayuda
show_help() {
    echo "Uso: $0 [opciones]"
    echo ""
    echo "Opciones:"
    echo "  -h, --help          Mostrar esta ayuda"
    echo "  -c, --clean         Limpiar builds anteriores"
    echo "  -d, --dev           Build de desarrollo (más rápido, menos optimizado)"
    echo "  -r, --release       Build de release (optimizado, por defecto)"
    echo "  -a, --arch ARCH     Arquitectura específica (amd64, arm64, auto)"
    echo "  -v, --verbose       Output verboso"
    echo ""
    echo "Ejemplos:"
    echo "  $0                  # Build de release para arquitectura actual"
    echo "  $0 --clean --dev    # Limpiar y hacer build de desarrollo"
    echo "  $0 --arch amd64     # Build específico para AMD64"
    echo ""
}

# Valores por defecto
BUILD_TYPE="release"
CLEAN=false
VERBOSE=false
ARCH="auto"

# Parsear argumentos
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
            ARCH="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo -e "${RED}Error: Opción desconocida $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Función para logging
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] ✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] ⚠${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ✗${NC} $1"
}

# Detectar arquitectura actual
detect_arch() {
    local machine=$(uname -m)
    case $machine in
        x86_64)
            echo "amd64"
            ;;
        aarch64|arm64)
            echo "arm64"
            ;;
        *)
            log_error "Arquitectura no soportada: $machine"
            exit 1
            ;;
    esac
}

# Verificar dependencias
check_dependencies() {
    log "Verificando dependencias..."
    
    if ! command -v uv &> /dev/null; then
        log_error "uv no está instalado. Instálalo con: pip install uv"
        exit 1
    fi
    
    if ! command -v git &> /dev/null; then
        log_error "git no está instalado"
        exit 1
    fi
    
    log_success "Todas las dependencias están disponibles"
}

# Limpiar builds anteriores
clean_builds() {
    if [ "$CLEAN" = true ]; then
        log "Limpiando builds anteriores..."
        rm -rf dist/ build/ *.spec .venv/
        log_success "Limpieza completada"
    fi
}

# Configurar entorno
setup_environment() {
    log "Configurando entorno de desarrollo..."
    
    # Sincronizar dependencias
    if [ "$BUILD_TYPE" = "dev" ]; then
        uv sync --group dev
    else
        uv sync --group dev
    fi
    
    log_success "Entorno configurado"
}

# Obtener información de versión
get_version_info() {
    local commit_count=$(git rev-list --count HEAD 2>/dev/null || echo "0")
    local git_hash=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
    local version="1.0.${commit_count}"
    
    echo "Versión: $version"
    echo "Commit: $git_hash"
    echo "Commits: $commit_count"
}

# Hacer el build
build_binary() {
    local target_arch="$1"
    local binary_name="muxer-linux-${target_arch}"
    
    log "Iniciando build para arquitectura: $target_arch"
    log "Tipo de build: $BUILD_TYPE"
    
    # Mostrar información de versión
    get_version_info
    
    # Crear directorio dist si no existe
    mkdir -p dist
    
    # Configurar argumentos de PyInstaller
    local pyinstaller_args=(
        "--onefile"
        "--name" "$binary_name"
        "--hidden-import=app"
        "--add-data" "app:app"
        "run.py"
    )
    
    # Argumentos adicionales según el tipo de build
    if [ "$BUILD_TYPE" = "release" ]; then
        pyinstaller_args+=("--strip" "--noupx")
        log "Build de release: aplicando optimizaciones"
    else
        log "Build de desarrollo: sin optimizaciones"
    fi
    
    # Argumentos de verbose si está habilitado
    if [ "$VERBOSE" = true ]; then
        pyinstaller_args+=("--log-level" "DEBUG")
    fi
    
    # Ejecutar PyInstaller
    log "Ejecutando PyInstaller..."
    if [ "$VERBOSE" = true ]; then
        uv run pyinstaller "${pyinstaller_args[@]}"
    else
        uv run pyinstaller "${pyinstaller_args[@]}" --log-level WARN
    fi
    
    # Verificar que el binario se creó correctamente
    if [ -f "dist/$binary_name" ]; then
        log_success "Build completado exitosamente"
        
        # Mostrar información del binario
        echo ""
        echo "📦 Información del binario:"
        echo "   Archivo: dist/$binary_name"
        echo "   Tamaño: $(du -h "dist/$binary_name" | cut -f1)"
        echo "   Tipo: $(file "dist/$binary_name" | cut -d: -f2- | sed 's/^ *//')"
        
        # Hacer el binario ejecutable
        chmod +x "dist/$binary_name"
        
        # Probar que el binario funciona
        log "Probando el binario..."
        if "./dist/$binary_name" --version &> /dev/null; then
            log_success "El binario funciona correctamente"
        else
            log_warning "No se pudo verificar la funcionalidad del binario"
        fi
        
    else
        log_error "Error: No se pudo crear el binario"
        exit 1
    fi
}

# Función principal
main() {
    echo ""
    echo "🔨 Muxer Local Build Script"
    echo "=========================="
    echo ""
    
    # Determinar arquitectura
    if [ "$ARCH" = "auto" ]; then
        ARCH=$(detect_arch)
        log "Arquitectura detectada automáticamente: $ARCH"
    else
        log "Usando arquitectura especificada: $ARCH"
    fi
    
    # Verificar que estamos en el directorio correcto
    if [ ! -f "pyproject.toml" ]; then
        log_error "Error: No se encontró pyproject.toml. Ejecuta este script desde el directorio raíz del proyecto."
        exit 1
    fi
    
    # Ejecutar pasos del build
    check_dependencies
    clean_builds
    setup_environment
    build_binary "$ARCH"
    
    echo ""
    log_success "🎉 Build completado exitosamente!"
    echo ""
    echo "El binario está disponible en: dist/muxer-linux-$ARCH"
    echo ""
    echo "Para probar el binario:"
    echo "  ./dist/muxer-linux-$ARCH --help"
    echo ""
}

# Ejecutar función principal
main "$@" 