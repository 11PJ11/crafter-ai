#!/bin/bash
# Acceptance Tests for AI-Craft Update Script
# Tests the update workflow: build → uninstall → install
# shellcheck disable=SC2317,SC2155  # Test helper functions called indirectly, declare/assign acceptable in tests

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TEST_CLAUDE_CONFIG="/tmp/ai-craft-update-test-$$"

# Color constants
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

log_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((TESTS_PASSED++)) || true
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((TESTS_FAILED++)) || true
}

run_test() {
    local test_name="$1"
    local test_func="$2"

    ((TESTS_RUN++)) || true
    log_test "$test_name"

    if $test_func; then
        log_pass "$test_name"
        return 0
    else
        log_fail "$test_name"
        return 1
    fi
}

# Setup test environment
setup() {
    echo -e "${YELLOW}=== Setting up test environment ===${NC}"

    mkdir -p "$TEST_CLAUDE_CONFIG"
    export CLAUDE_CONFIG_DIR="$TEST_CLAUDE_CONFIG"

    # Install initial version
    "$PROJECT_ROOT/scripts/install-ai-craft.sh" >/dev/null 2>&1

    echo "Test config dir: $TEST_CLAUDE_CONFIG"
}

# Cleanup test environment
cleanup() {
    echo -e "${YELLOW}=== Cleaning up test environment ===${NC}"

    if [[ -d "$TEST_CLAUDE_CONFIG" ]]; then
        rm -rf "$TEST_CLAUDE_CONFIG"
        echo "Removed test directory: $TEST_CLAUDE_CONFIG"
    fi
}

trap cleanup EXIT

#######################################
# UPDATE SCRIPT TESTS
#######################################

test_update_dry_run_no_changes() {
    local before_count=$(find "$TEST_CLAUDE_CONFIG/agents/nw" -name "*.md" 2>/dev/null | wc -l)

    "$PROJECT_ROOT/scripts/update-ai-craft.sh" --dry-run --force >/dev/null 2>&1

    local after_count=$(find "$TEST_CLAUDE_CONFIG/agents/nw" -name "*.md" 2>/dev/null | wc -l)

    [[ $before_count -eq $after_count ]]
}

test_update_preserves_agent_count() {
    local before_count=$(find "$TEST_CLAUDE_CONFIG/agents/nw" -name "*.md" 2>/dev/null | wc -l)

    "$PROJECT_ROOT/scripts/update-ai-craft.sh" --force >/dev/null 2>&1

    local after_count=$(find "$TEST_CLAUDE_CONFIG/agents/nw" -name "*.md" 2>/dev/null | wc -l)

    # Should have same or more agents after update
    [[ $after_count -ge $before_count ]]
}

test_update_creates_backup_when_requested() {
    "$PROJECT_ROOT/scripts/update-ai-craft.sh" --force --backup >/dev/null 2>&1

    # The update process creates backups - check for any ai-craft backup directory
    # (uninstall backup is preserved, update backup may be cleaned)
    local backup_count=$(find "$TEST_CLAUDE_CONFIG/backups" -maxdepth 1 -name "ai-craft-*" -type d 2>/dev/null | wc -l)
    [[ $backup_count -ge 1 ]]
}

test_update_creates_report() {
    [[ -f "$TEST_CLAUDE_CONFIG/ai-craft-update-report.txt" ]]
}

test_update_manifest_updated() {
    [[ -f "$TEST_CLAUDE_CONFIG/ai-craft-manifest.txt" ]]
}

test_update_essential_commands_present() {
    local essential_commands=("discuss.md" "design.md" "distill.md" "develop.md" "deliver.md")
    for cmd in "${essential_commands[@]}"; do
        if [[ ! -f "$TEST_CLAUDE_CONFIG/commands/nw/$cmd" ]]; then
            return 1
        fi
    done
    return 0
}

#######################################
# MAIN TEST RUNNER
#######################################

main() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║     AI-Craft Update Script Acceptance Tests    ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
    echo ""

    setup

    echo ""
    echo -e "${YELLOW}=== Update Script Tests ===${NC}"
    run_test "Update dry-run makes no changes" test_update_dry_run_no_changes
    run_test "Update preserves agent count" test_update_preserves_agent_count
    run_test "Update creates backup when requested" test_update_creates_backup_when_requested
    run_test "Update creates report file" test_update_creates_report
    run_test "Update maintains manifest" test_update_manifest_updated
    run_test "Update preserves essential commands" test_update_essential_commands_present

    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                 TEST SUMMARY                   ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "Tests run:    ${TESTS_RUN}"
    echo -e "Tests passed: ${GREEN}${TESTS_PASSED}${NC}"
    echo -e "Tests failed: ${RED}${TESTS_FAILED}${NC}"
    echo ""

    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}✅ All acceptance tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}❌ Some tests failed${NC}"
        exit 1
    fi
}

main "$@"
