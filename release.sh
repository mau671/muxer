#!/bin/bash
# Script para crear un nuevo release usando CalVer (vYY.MM.PATCH)

# Obtener Año y Mes actuales (ej. 24.10)
CALVER_PREFIX=$(date +'%y.%m')

# Buscar el último tag que coincida con este mes
LAST_TAG=$(git tag -l "v$CALVER_PREFIX.*" --sort=-v:refname | head -n 1)

if [ -z "$LAST_TAG" ]; then
    # Si no hay tags este mes, empezamos en .1
    NEW_PATCH=1
else
    # Extraer el número de patch y sumarle 1
    LAST_PATCH=${LAST_TAG##*.}
    NEW_PATCH=$((LAST_PATCH + 1))
fi

NEW_TAG="v$CALVER_PREFIX.$NEW_PATCH"

echo "Creando nuevo release: $NEW_TAG"

# Crear y empujar el tag
git tag -a "$NEW_TAG" -m "Release $NEW_TAG"
git push origin "$NEW_TAG"

echo "¡Tag $NEW_TAG empujado! Github Actions comenzará a construir y publicar el release automáticamente."
