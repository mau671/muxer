#!/bin/bash
# Script to create a new release using CalVer (vYY.MM.PATCH)

# Get current Year and Month (e.g., 24.10)
CALVER_PREFIX=$(date +'%y.%m')

# Find the latest tag that matches this month
LAST_TAG=$(git tag -l "v$CALVER_PREFIX.*" --sort=-v:refname | head -n 1)

if [ -z "$LAST_TAG" ]; then
    # If there are no tags this month, start at .1
    NEW_PATCH=1
else
    # Extract the patch number and increment it by 1
    LAST_PATCH=${LAST_TAG##*.}
    NEW_PATCH=$((LAST_PATCH + 1))
fi

NEW_TAG="v$CALVER_PREFIX.$NEW_PATCH"

echo "Creating new release: $NEW_TAG"

# Create and push the tag
git tag -a "$NEW_TAG" -m "Release $NEW_TAG"
git push origin "$NEW_TAG"

echo "Tag $NEW_TAG pushed successfully! GitHub Actions will now automatically build and publish the release."
