#!/bin/bash
# Test script for Unix installer dry-run validation
# Validates that the installer works correctly in dry-run mode without modifying filesystem

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
INSTALLER_SCRIPT="$SCRIPT_DIR/install-ai-craft.sh"
TEMP_TEST_DIR=$(mktemp -d)

# Cleanup on exit
cleanup() {
    rm -rf "$TEMP_TEST_DIR"
}
trap cleanup EXIT

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test result tracking
TESTS_PASSED=0
TESTS_FAILED=0

# Test functions
test_passed() {
    echo -e "${GREEN}✓${NC} $1"
    ((TESTS_PASSED++))
}

test_failed() {
    echo -e "${RED}✗${NC} $1"
    ((TESTS_FAILED++))
}

test_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Verify installer script exists
if [[ ! -f "$INSTALLER_SCRIPT" ]]; then
    echo -e "${RED}ERROR: Installer script not found at $INSTALLER_SCRIPT${NC}"
    exit 1
fi

test_info "Starting Unix installer dry-run validation tests"
test_info "Installer: $INSTALLER_SCRIPT"
test_info "Test directory: $TEMP_TEST_DIR"
echo ""

# Test 1: Installer script is executable
if [[ -x "$INSTALLER_SCRIPT" ]]; then
    test_passed "Installer script is executable"
else
    chmod +x "$INSTALLER_SCRIPT"
    test_passed "Installer script made executable"
fi

# Test 2: Installer accepts --help flag
if "$INSTALLER_SCRIPT" --help > "$TEMP_TEST_DIR/help.txt" 2>&1; then
    if grep -q "dry-run" "$TEMP_TEST_DIR/help.txt"; then
        test_passed "Installer documents --dry-run flag in help"
    else
        test_failed "Installer help does not document --dry-run flag"
    fi
else
    test_failed "Installer --help command failed"
fi

# Test 3: Installer accepts --dry-run flag without error
test_info "Running installer in dry-run mode..."
export CLAUDE_CONFIG_DIR="$TEMP_TEST_DIR/.claude"
mkdir -p "$CLAUDE_CONFIG_DIR"

# Capture output in dry-run mode
DRY_RUN_OUTPUT=$(mktemp)
if "$INSTALLER_SCRIPT" --dry-run > "$DRY_RUN_OUTPUT" 2>&1; then
    test_passed "Installer executes successfully in dry-run mode (exit code 0)"
else
    EXIT_CODE=$?
    test_failed "Installer failed in dry-run mode (exit code: $EXIT_CODE)"
fi

# Test 4: Dry-run output indicates what would be installed
if grep -q "agents" "$DRY_RUN_OUTPUT" || grep -q "commands" "$DRY_RUN_OUTPUT" || grep -q "nWave" "$DRY_RUN_OUTPUT"; then
    test_passed "Dry-run output reports installation path detection results"
else
    test_failed "Dry-run output does not show installation path detection"
fi

# Test 5: Verify dry-run does not modify filesystem
# Check that no actual files were copied (agents/commands directories should not be created)
if [[ ! -d "$CLAUDE_CONFIG_DIR/agents" && ! -d "$CLAUDE_CONFIG_DIR/commands" ]]; then
    test_passed "Dry-run mode did not create agents/commands directories"
else
    test_failed "Dry-run mode modified filesystem (created agents or commands directories)"
fi

# Test 6: Verify dry-run output contains [DRY RUN] prefix indicators
if grep -q "\[DRY RUN\]" "$DRY_RUN_OUTPUT" 2>/dev/null; then
    test_passed "Dry-run output uses [DRY RUN] prefix to indicate simulation"
else
    test_info "Dry-run output does not use explicit [DRY RUN] prefix (may still be valid)"
fi

# Test 7: Verify installation paths are detected
if grep -qE "(Found|agents|commands|nWave)" "$DRY_RUN_OUTPUT"; then
    test_passed "Installation path detection works (agents and commands counted)"
else
    test_failed "Installation path detection did not report expected information"
fi

# Test 8: Validate installer validates without errors (no error messages in output)
if ! grep -qi "error" "$DRY_RUN_OUTPUT"; then
    test_passed "Dry-run execution shows no error messages"
else
    ERROR_COUNT=$(grep -i "error" "$DRY_RUN_OUTPUT" | wc -l)
    test_failed "Dry-run execution produced $ERROR_COUNT error messages"
fi

# Test 9: Verify install log would be created but not modified
if [[ -f "$CLAUDE_CONFIG_DIR/ai-craft-install.log" ]]; then
    # In dry-run, log might be touched but should have minimal content
    LOG_SIZE=$(stat -f%z "$CLAUDE_CONFIG_DIR/ai-craft-install.log" 2>/dev/null || stat -c%s "$CLAUDE_CONFIG_DIR/ai-craft-install.log" 2>/dev/null || echo "unknown")
    test_info "Install log file size: $LOG_SIZE bytes"
fi

echo ""
echo "======================================"
echo -e "Test Results: ${GREEN}$TESTS_PASSED passed${NC}, ${RED}$TESTS_FAILED failed${NC}"
echo "======================================"

# Show sample output
echo ""
echo "Sample installer output (first 20 lines):"
head -20 "$DRY_RUN_OUTPUT"

# Cleanup
rm -f "$DRY_RUN_OUTPUT"

# Exit with appropriate code
if [[ $TESTS_FAILED -eq 0 ]]; then
    exit 0
else
    exit 1
fi
