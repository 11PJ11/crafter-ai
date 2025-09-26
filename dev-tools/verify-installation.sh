#!/bin/bash
# Installation Verification Script
# Verifies that all hooks will work correctly after global installation

set -euo pipefail

echo "🔍 Claude Code Hook Installation Verification"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

# Function to log results
log_result() {
    local status="$1"
    local message="$2"
    case "$status" in
        "PASS")
            echo -e "${GREEN}✅ PASS${NC}: $message"
            ;;
        "FAIL")
            echo -e "${RED}❌ FAIL${NC}: $message"
            ((ERRORS++))
            ;;
        "WARN")
            echo -e "${YELLOW}⚠️  WARN${NC}: $message"
            ((WARNINGS++))
            ;;
    esac
}

# Test 1: Verify installation directory structure
echo -e "\n📁 Testing Installation Structure"
echo "================================="

HOOK_BASE="${HOME}/.claude/hooks"
REQUIRED_DIRS=(
    "workflow"
    "code-quality"
    "lib"
    "lib/tools"
    "lib/formatters"
    "lib/logging"
    "config"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "${HOOK_BASE}/${dir}" ]; then
        log_result "PASS" "Directory exists: ${dir}"
    else
        log_result "FAIL" "Missing directory: ${dir}"
    fi
done

# Test 2: Verify all hook scripts exist and are executable
echo -e "\n🔧 Testing Hook Scripts"
echo "======================="

HOOK_SCRIPTS=(
    "workflow/state-initializer.sh"
    "workflow/context-isolator.py"
    "workflow/input-validator.sh"
    "workflow/output-monitor.py"
    "workflow/stage-transition.sh"
    "code-quality/lint-format.sh"
)

for script in "${HOOK_SCRIPTS[@]}"; do
    script_path="${HOOK_BASE}/${script}"
    if [ -f "$script_path" ]; then
        if [ -x "$script_path" ]; then
            log_result "PASS" "Hook executable: ${script}"
        else
            log_result "FAIL" "Hook not executable: ${script}"
        fi
    else
        log_result "FAIL" "Hook missing: ${script}"
    fi
done

# Test 3: Test hook self-location and dependency resolution
echo -e "\n🔗 Testing Dependency Resolution"
echo "================================="

# Test state initializer
if [ -f "${HOOK_BASE}/workflow/state-initializer.sh" ]; then
    if "${HOOK_BASE}/workflow/state-initializer.sh" >/dev/null 2>&1; then
        log_result "PASS" "State initializer resolves dependencies"
    else
        log_result "FAIL" "State initializer dependency resolution failed"
    fi
else
    log_result "FAIL" "State initializer not found"
fi

# Test lint-format hook
if [ -f "${HOOK_BASE}/code-quality/lint-format.sh" ]; then
    # Create a temporary test to avoid modifying real files
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"
    echo "print('test')" > test.py

    if "${HOOK_BASE}/code-quality/lint-format.sh" >/dev/null 2>&1; then
        log_result "PASS" "Lint-format hook works from different directory"
    else
        log_result "WARN" "Lint-format hook had issues (may be missing formatters)"
    fi

    cd - >/dev/null
    rm -rf "$TEMP_DIR"
else
    log_result "FAIL" "Lint-format hook not found"
fi

# Test 4: Verify configuration matches installation
echo -e "\n⚙️  Testing Configuration Consistency"
echo "===================================="

CONFIG_FILE="${HOOK_BASE}/config/hooks-config.json"
if [ -f "$CONFIG_FILE" ]; then
    log_result "PASS" "Configuration file exists"

    # Check if all configured hooks exist
    while IFS= read -r hook_path; do
        # Extract path from JSON, remove quotes and $HOME prefix
        clean_path=$(echo "$hook_path" | sed 's/.*"\$HOME\/.claude\/hooks\/\([^"]*\)".*/\1/')
        full_path="${HOOK_BASE}/${clean_path}"

        if [ -f "$full_path" ]; then
            log_result "PASS" "Configured hook exists: ${clean_path}"
        else
            log_result "FAIL" "Configured hook missing: ${clean_path}"
        fi
    done < <(grep -o '"command": "[^"]*"' "$CONFIG_FILE")
else
    log_result "FAIL" "Configuration file missing"
fi

# Test 5: Test library components
echo -e "\n📚 Testing Library Components"
echo "============================="

LIB_COMPONENTS=(
    "lib/HookManager.sh"
    "lib/logging/LogManager.sh"
    "lib/tools/LanguageDetector.sh"
    "lib/tools/ToolManager.sh"
    "lib/formatters/FormatterRegistry.sh"
)

for component in "${LIB_COMPONENTS[@]}"; do
    if [ -f "${HOOK_BASE}/${component}" ]; then
        log_result "PASS" "Library component exists: ${component}"
    else
        log_result "FAIL" "Missing library component: ${component}"
    fi
done

# Test 6: Environment requirements
echo -e "\n🌍 Testing Environment Requirements"
echo "==================================="

# Check required executables for formatters
FORMATTERS=(
    "python3:Python formatting"
    "black:Python Black formatter"
    "isort:Python import sorting"
    "ruff:Python linting"
)

for formatter_check in "${FORMATTERS[@]}"; do
    IFS=':' read -r cmd desc <<< "$formatter_check"
    if command -v "$cmd" >/dev/null 2>&1; then
        log_result "PASS" "$desc available"
    else
        log_result "WARN" "$desc not available (some formatting may be skipped)"
    fi
done

# Summary
echo -e "\n📊 Installation Verification Summary"
echo "===================================="

if [ $ERRORS -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}🎉 PERFECT: All tests passed! Installation ready.${NC}"
        exit 0
    else
        echo -e "${YELLOW}✅ GOOD: All critical tests passed. ${WARNINGS} warning(s).${NC}"
        exit 0
    fi
else
    echo -e "${RED}❌ ISSUES FOUND: ${ERRORS} error(s), ${WARNINGS} warning(s).${NC}"
    echo "Please fix errors before installing."
    exit 1
fi