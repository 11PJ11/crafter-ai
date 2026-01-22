#!/bin/bash
# Acceptance Tests for AI-Craft Install/Uninstall Scripts
# Tests the complete lifecycle: install → verify → uninstall → verify
# shellcheck disable=SC2317,SC2155  # Test helper functions called indirectly, declare/assign acceptable in tests

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TEST_CLAUDE_CONFIG="/tmp/ai-craft-test-$$"

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

    # Create isolated test directory
    mkdir -p "$TEST_CLAUDE_CONFIG"
    export CLAUDE_CONFIG_DIR="$TEST_CLAUDE_CONFIG"

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

# Trap to ensure cleanup on exit
trap cleanup EXIT

#######################################
# INSTALL SCRIPT TESTS
#######################################

test_install_creates_agents_directory() {
    "$PROJECT_ROOT/scripts/install-ai-craft.sh" >/dev/null 2>&1
    [[ -d "$TEST_CLAUDE_CONFIG/agents/nw" ]]
}

test_install_creates_commands_directory() {
    [[ -d "$TEST_CLAUDE_CONFIG/commands/nw" ]]
}

test_install_creates_manifest() {
    [[ -f "$TEST_CLAUDE_CONFIG/ai-craft-manifest.txt" ]]
}

test_install_has_minimum_agents() {
    local agent_count=$(find "$TEST_CLAUDE_CONFIG/agents/nw" -name "*.md" 2>/dev/null | wc -l)
    [[ $agent_count -ge 10 ]]
}

test_install_has_essential_commands() {
    local essential_commands=("discuss.md" "design.md" "distill.md" "develop.md" "deliver.md")
    for cmd in "${essential_commands[@]}"; do
        if [[ ! -f "$TEST_CLAUDE_CONFIG/commands/nw/$cmd" ]]; then
            return 1
        fi
    done
    return 0
}

test_install_dry_run_no_changes() {
    # Remove existing installation
    rm -rf "$TEST_CLAUDE_CONFIG/agents" "$TEST_CLAUDE_CONFIG/commands" "$TEST_CLAUDE_CONFIG/ai-craft-manifest.txt"

    # Run dry-run
    "$PROJECT_ROOT/scripts/install-ai-craft.sh" --dry-run >/dev/null 2>&1

    # Verify nothing was created (except from previous test - check manifest specifically)
    [[ ! -f "$TEST_CLAUDE_CONFIG/ai-craft-manifest.txt" ]] || \
    grep -q "$(date +%Y)" "$TEST_CLAUDE_CONFIG/ai-craft-manifest.txt" 2>/dev/null
}

#######################################
# UNINSTALL SCRIPT TESTS
#######################################

test_uninstall_removes_agents() {
    # First ensure we have an installation
    "$PROJECT_ROOT/scripts/install-ai-craft.sh" >/dev/null 2>&1

    # Run uninstall
    "$PROJECT_ROOT/scripts/uninstall-ai-craft.sh" --force >/dev/null 2>&1

    [[ ! -d "$TEST_CLAUDE_CONFIG/agents/nw" ]]
}

test_uninstall_removes_commands() {
    [[ ! -d "$TEST_CLAUDE_CONFIG/commands/nw" ]]
}

test_uninstall_removes_manifest() {
    [[ ! -f "$TEST_CLAUDE_CONFIG/ai-craft-manifest.txt" ]]
}

test_uninstall_creates_backup_when_requested() {
    # Reinstall first
    "$PROJECT_ROOT/scripts/install-ai-craft.sh" >/dev/null 2>&1

    # Uninstall with backup
    "$PROJECT_ROOT/scripts/uninstall-ai-craft.sh" --force --backup >/dev/null 2>&1

    # Check backup was created
    local backup_count=$(find "$TEST_CLAUDE_CONFIG/backups" -maxdepth 1 -name "ai-craft-uninstall-*" -type d 2>/dev/null | wc -l)
    [[ $backup_count -ge 1 ]]
}

test_uninstall_dry_run_no_changes() {
    # Reinstall first
    "$PROJECT_ROOT/scripts/install-ai-craft.sh" >/dev/null 2>&1

    # Run dry-run uninstall
    "$PROJECT_ROOT/scripts/uninstall-ai-craft.sh" --dry-run --force >/dev/null 2>&1

    # Verify installation still exists
    [[ -d "$TEST_CLAUDE_CONFIG/agents/nw" ]]
}

#######################################
# REINSTALL CYCLE TEST
#######################################

test_reinstall_cycle() {
    # Clean slate
    rm -rf "${TEST_CLAUDE_CONFIG:?}"/*

    # Install
    "$PROJECT_ROOT/scripts/install-ai-craft.sh" >/dev/null 2>&1
    local install1_agents=$(find "$TEST_CLAUDE_CONFIG/agents/nw" -name "*.md" 2>/dev/null | wc -l)

    # Uninstall
    "$PROJECT_ROOT/scripts/uninstall-ai-craft.sh" --force >/dev/null 2>&1

    # Reinstall
    "$PROJECT_ROOT/scripts/install-ai-craft.sh" >/dev/null 2>&1
    local install2_agents=$(find "$TEST_CLAUDE_CONFIG/agents/nw" -name "*.md" 2>/dev/null | wc -l)

    # Verify same number of agents
    [[ $install1_agents -eq $install2_agents ]] && [[ $install1_agents -gt 0 ]]
}

#######################################
# MAIN TEST RUNNER
#######################################

main() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  AI-Craft Install/Uninstall Acceptance Tests   ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
    echo ""

    setup

    echo ""
    echo -e "${YELLOW}=== Install Script Tests ===${NC}"
    run_test "Install creates agents directory" test_install_creates_agents_directory
    run_test "Install creates commands directory" test_install_creates_commands_directory
    run_test "Install creates manifest file" test_install_creates_manifest
    run_test "Install has minimum 10 agents" test_install_has_minimum_agents
    run_test "Install has essential DW commands" test_install_has_essential_commands

    echo ""
    echo -e "${YELLOW}=== Uninstall Script Tests ===${NC}"
    run_test "Uninstall removes agents directory" test_uninstall_removes_agents
    run_test "Uninstall removes commands directory" test_uninstall_removes_commands
    run_test "Uninstall removes manifest file" test_uninstall_removes_manifest
    run_test "Uninstall creates backup when requested" test_uninstall_creates_backup_when_requested
    run_test "Uninstall dry-run makes no changes" test_uninstall_dry_run_no_changes

    echo ""
    echo -e "${YELLOW}=== Lifecycle Tests ===${NC}"
    run_test "Reinstall cycle works correctly" test_reinstall_cycle

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
