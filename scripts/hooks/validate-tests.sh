#!/bin/bash
# Pytest Test Validation Hook
# Ensures all tests pass before commit

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# CRITICAL: Clear git environment variables that pre-commit sets
# These can interfere with tests that create temporary git repositories
unset GIT_DIR
unset GIT_WORK_TREE
unset GIT_INDEX_FILE
unset GIT_AUTHOR_DATE
unset GIT_AUTHOR_NAME
unset GIT_AUTHOR_EMAIL

echo -e "${BLUE}Running test validation...${NC}"

# Check if pytest is available
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Warning: python3 not available, skipping tests${NC}"
    exit 0
fi

if ! python3 -m pytest --version &> /dev/null 2>&1; then
    echo -e "${YELLOW}Warning: pytest not available, skipping tests${NC}"
    exit 0
fi

# Check if tests directory exists
if [ ! -d "tests" ]; then
    echo -e "${YELLOW}No tests directory found, skipping tests${NC}"
    exit 0
fi

# Run tests and capture output
set +e
TEST_OUTPUT=$(python3 -m pytest tests/ -v --tb=short 2>&1)
TEST_EXIT_CODE=$?
set -e

# Count tests
TOTAL_TESTS=$(echo "$TEST_OUTPUT" | grep -oP '\d+(?= passed)' | head -1 || echo "0")
FAILED_TESTS=$(echo "$TEST_OUTPUT" | grep -oP '\d+(?= failed)' | head -1 || echo "0")

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}All tests passing (${TOTAL_TESTS}/${TOTAL_TESTS})${NC}"
    exit 0
elif [ $TEST_EXIT_CODE -eq 5 ]; then
    # Exit code 5 = no tests collected
    echo -e "${YELLOW}No tests found, skipping test validation${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}COMMIT BLOCKED: Tests failed${NC}"
    echo ""
    echo -e "${RED}Failed tests:${NC}"
    echo "$TEST_OUTPUT" | grep -E "FAILED|ERROR" | sed 's/^/  /'
    echo ""

    if [ "$FAILED_TESTS" != "0" ]; then
        PASSING_TESTS=$((TOTAL_TESTS - FAILED_TESTS))
        echo -e "${RED}Test Results: ${PASSING_TESTS}/${TOTAL_TESTS} passing (${FAILED_TESTS} failed)${NC}"
    fi

    echo ""
    echo -e "${YELLOW}Fix failing tests before committing.${NC}"
    echo -e "${YELLOW}Emergency bypass: git commit --no-verify${NC}"
    exit 1
fi
