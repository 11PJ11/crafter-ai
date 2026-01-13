#!/bin/bash

# Build IDE Bundle Script
# Builds the nWave IDE bundle with agents, commands, and hooks

# Note: Not using 'set -e' here because we want to handle Python script exit codes explicitly

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}  nWave IDE Bundle Builder${NC}"
echo -e "${BLUE}=====================================${NC}"
echo

# Check if Python script exists
BUILD_SCRIPT="$PROJECT_ROOT/tools/build_ide_bundle.py"
if [ ! -f "$BUILD_SCRIPT" ]; then
    echo -e "${RED}Error: Build script not found at $BUILD_SCRIPT${NC}"
    exit 1
fi

# Change to project root directory
cd "$PROJECT_ROOT"

echo -e "${YELLOW}Project root: $PROJECT_ROOT${NC}"
echo -e "${YELLOW}Build script: $BUILD_SCRIPT${NC}"
echo

# Check for dry-run flag
DRY_RUN=""
if [ "$1" = "--dry-run" ] || [ "$1" = "-n" ]; then
    DRY_RUN="--dry-run"
    echo -e "${YELLOW}Running in dry-run mode...${NC}"
    echo
fi

# Clean previous build (remove dist folder)
if [ -z "$DRY_RUN" ]; then
    if [ -d "dist" ]; then
        echo -e "${YELLOW}Cleaning previous build...${NC}"
        rm -rf dist
        echo -e "${YELLOW}Removed existing dist directory${NC}"
        echo
    fi
else
    echo -e "${YELLOW}[DRY RUN] Would remove existing dist directory${NC}"
    echo
fi

# Run the Python build script with correct source and output directories
echo -e "${BLUE}Starting build process...${NC}"
echo
python3 "$BUILD_SCRIPT" --source nWave --output dist/ide $DRY_RUN

# Check if build was successful
if [ $? -eq 0 ]; then
    echo
    echo -e "${GREEN}=====================================${NC}"
    echo -e "${GREEN}  Build completed successfully!${NC}"
    echo -e "${GREEN}=====================================${NC}"

    if [ -z "$DRY_RUN" ]; then
        echo -e "${YELLOW}Distribution available at: dist/ide/${NC}"
        echo -e "${YELLOW}Contents:${NC}"
        if [ -d "dist/ide" ]; then
            ls -la dist/ide/
        fi
    fi
else
    echo
    echo -e "${RED}=====================================${NC}"
    echo -e "${RED}  Build failed!${NC}"
    echo -e "${RED}=====================================${NC}"
    exit 1
fi