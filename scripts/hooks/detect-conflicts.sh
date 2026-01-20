#!/bin/bash
# Conflict Detection Hook
# Detects when related files (agent + catalog) change together
# Suggests manual review before commit

set -e

# Color codes
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Checking for file conflicts...${NC}"

# Define related file pairs that should not change together
# Format: file1:file2 (colon-separated)
CONFLICT_PAIRS=(
  "nWave/agents/:nWave/commands/"
  "nWave/templates/:nWave/agents/"
)

# Get list of staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null || echo "")

if [ -z "$STAGED_FILES" ]; then
    echo -e "${BLUE}No staged files to check${NC}"
    exit 0
fi

# Track if conflicts found
CONFLICTS_FOUND=0

# Check for conflict pairs
for PAIR in "${CONFLICT_PAIRS[@]}"; do
    IFS=':' read -r FILE1_PATTERN FILE2_PATTERN <<< "$PAIR"

    FILE1_MODIFIED=false
    FILE2_MODIFIED=false

    # Check if any files matching pattern 1 are staged
    if echo "$STAGED_FILES" | grep -q "^$FILE1_PATTERN"; then
        FILE1_MODIFIED=true
    fi

    # Check if any files matching pattern 2 are staged
    if echo "$STAGED_FILES" | grep -q "^$FILE2_PATTERN"; then
        FILE2_MODIFIED=true
    fi

    # If both patterns have changes, flag as conflict
    if [ "$FILE1_MODIFIED" = true ] && [ "$FILE2_MODIFIED" = true ]; then
        CONFLICTS_FOUND=1

        echo ""
        echo -e "${YELLOW}CONFLICT DETECTED: Related files changed together${NC}"
        echo -e "${YELLOW}Files affected:${NC}"
        echo "$STAGED_FILES" | grep "^$FILE1_PATTERN" | sed 's/^/  [1] /'
        echo "$STAGED_FILES" | grep "^$FILE2_PATTERN" | sed 's/^/  [2] /'
        echo ""
        echo -e "${YELLOW}Discrepancy Details:${NC}"
        echo "  - Files from pattern '$FILE1_PATTERN' and '$FILE2_PATTERN' modified in same commit"
        echo "  - This may indicate incomplete refactoring or coupling between agent/catalog"
        echo ""
        echo -e "${YELLOW}Recommendation:${NC}"
        echo "  - Review changes manually to ensure consistency"
        echo "  - Verify agent behavior matches catalog documentation"
        echo "  - Consider splitting into separate commits if logically independent"
        echo ""
    fi
done

if [ $CONFLICTS_FOUND -eq 1 ]; then
    echo -e "${YELLOW}Review suggested before committing${NC}"
    echo -e "${YELLOW}Bypass with: git commit --no-verify${NC}"
    exit 0  # Warning only, non-blocking
else
    echo -e "${BLUE}No file conflicts detected${NC}"
    exit 0
fi
