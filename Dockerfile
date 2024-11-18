# Imagen base para Python y UV
FROM ghcr.io/astral-sh/uv:python3.12-alpine AS runtime

# Instalar MKVToolNix y dependencias necesarias
RUN apk add --no-cache \
    mkvtoolnix \
    boost-filesystem \
    boost-regex \
    boost-system \
    libmatroska \
    libogg \
    libvorbis \
    cmark

# Crear directorio para la aplicación
WORKDIR /app

# Copiar el proyecto al contenedor
COPY . /app

# Sincronizar el entorno con UV
RUN uv sync --frozen

# Configurar el PATH para incluir el entorno virtual creado por UV
ENV PATH="/app/.venv/bin:$PATH"

# Usar ENTRYPOINT para manejar correctamente los argumentos
ENTRYPOINT ["uv", "run", "main.py"]
