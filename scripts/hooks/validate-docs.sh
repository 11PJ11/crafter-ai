#!/bin/bash
# Documentation Version Validation Hook
# Ensures documentation versions are synchronized

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# CRITICAL: Clear git environment variables that pre-commit sets
# These can cause git commands to fail or behave unexpectedly
unset GIT_DIR
unset GIT_WORK_TREE
unset GIT_INDEX_FILE

echo -e "${BLUE}Running documentation version validation...${NC}"

# Check if validation infrastructure exists
if [ ! -f ".dependency-map.yaml" ]; then
    echo -e "${YELLOW}Warning: .dependency-map.yaml not found, skipping version validation${NC}"
    exit 0
fi

if [ ! -f "scripts/validate-documentation-versions.py" ]; then
    echo -e "${YELLOW}Warning: validation script not found, skipping version validation${NC}"
    exit 0
fi

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Warning: python3 not available, skipping validation${NC}"
    exit 0
fi

# Run validation
set +e
python3 scripts/validate-documentation-versions.py
VERSION_EXIT_CODE=$?
set -e

if [ $VERSION_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}Documentation version validation passed${NC}"
    exit 0
elif [ $VERSION_EXIT_CODE -eq 2 ]; then
    echo -e "${RED}Configuration error in version validation${NC}"
    echo -e "${RED}Check .dependency-map.yaml for errors${NC}"
    exit 1
else
    # Error report already printed by Python script
    echo ""
    echo -e "${YELLOW}Emergency bypass: git commit --no-verify${NC}"
    exit 1
fi
