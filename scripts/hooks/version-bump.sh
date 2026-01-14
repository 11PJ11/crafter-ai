#!/bin/bash
# nWave Version Auto-Increment Hook
# Automatically bumps patch version when nWave files are modified

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

CATALOG_FILE="nWave/framework-catalog.yaml"
VERSION_FILE="nWave/tasks/nw/version.md"

# Check if nWave files are staged (excluding version.md to avoid loops)
NWAVE_STAGED=$(git diff --cached --name-only | grep -E "^(nWave/|tools/)" | grep -v "version.md" || true)

if [ -z "$NWAVE_STAGED" ]; then
    echo -e "${BLUE}No nWave files modified, skipping version bump${NC}"
    exit 0
fi

if [ ! -f "$CATALOG_FILE" ] || [ ! -f "$VERSION_FILE" ]; then
    echo -e "${YELLOW}Warning: Version files not found, skipping version bump${NC}"
    exit 0
fi

# Extract current version from framework-catalog.yaml
CURRENT_VERSION=$(grep -E "^version:" "$CATALOG_FILE" | sed 's/version: *"//' | sed 's/"//')

if [ -z "$CURRENT_VERSION" ]; then
    echo -e "${YELLOW}Warning: Could not parse version from $CATALOG_FILE${NC}"
    exit 0
fi

# Parse version components
MAJOR=$(echo "$CURRENT_VERSION" | cut -d. -f1)
MINOR=$(echo "$CURRENT_VERSION" | cut -d. -f2)
PATCH=$(echo "$CURRENT_VERSION" | cut -d. -f3)

# Increment patch version
NEW_PATCH=$((PATCH + 1))
NEW_VERSION="${MAJOR}.${MINOR}.${NEW_PATCH}"

# Get current timestamp
BUILD_TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Update framework-catalog.yaml
sed -i "s/^version: \"${CURRENT_VERSION}\"/version: \"${NEW_VERSION}\"/" "$CATALOG_FILE"

# Update version.md
sed -i "s/Version: ${CURRENT_VERSION}/Version: ${NEW_VERSION}/" "$VERSION_FILE"
sed -i "s/Build: [0-9T:-]*Z/Build: ${BUILD_TIMESTAMP}/" "$VERSION_FILE"

# Update dependent files (README.md and COMMAND-AGENT-MAPPING.md)
README_FILE="README.md"
MAPPING_FILE="nWave/data/agents_reference/COMMAND-AGENT-MAPPING.md"

if [ -f "$README_FILE" ]; then
    sed -i "s/<!-- version: ${CURRENT_VERSION} -->/<!-- version: ${NEW_VERSION} -->/" "$README_FILE"
    git add "$README_FILE"
fi

if [ -f "$MAPPING_FILE" ]; then
    sed -i "s/<!-- version: ${CURRENT_VERSION} -->/<!-- version: ${NEW_VERSION} -->/" "$MAPPING_FILE"
    git add "$MAPPING_FILE"
fi

# Stage the updated files
git add "$CATALOG_FILE" "$VERSION_FILE"

echo -e "${GREEN}Version bumped: ${CURRENT_VERSION} -> ${NEW_VERSION}${NC}"
echo -e "${GREEN}  (Also updated: README.md, COMMAND-AGENT-MAPPING.md)${NC}"

exit 0
