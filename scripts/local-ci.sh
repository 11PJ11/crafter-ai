#!/usr/bin/env bash
# ============================================================================
# Local CI/CD Simulation Script
# ============================================================================
# Runs the same validation checks as GitHub Actions CI/CD pipelines locally
# This allows catching issues before pushing to remote
#
# Usage:
#   ./scripts/local-ci.sh [--verbose] [--fast]
#
# Options:
#   --verbose    Show detailed output
#   --fast       Skip slower checks (build validation)
#   --help       Show this help message
# ============================================================================

# Note: Don't use set -e as we want to continue through all checks and report summary

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VERBOSE=false
FAST_MODE=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --fast|-f)
            FAST_MODE=true
            shift
            ;;
        --help|-h)
            head -n 20 "$0" | grep "^#" | sed 's/^# *//'
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

cd "$PROJECT_ROOT"

# Helper functions
print_header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${BLUE}ℹ${NC} $1"
    fi
}

# Track results
TESTS_PASSED=0
TESTS_FAILED=0

run_check() {
    local check_name="$1"
    local check_command="$2"

    print_info "Running: $check_command"

    if [ "$VERBOSE" = true ]; then
        if eval "$check_command"; then
            print_success "$check_name"
            ((TESTS_PASSED++))
            return 0
        else
            print_error "$check_name"
            ((TESTS_FAILED++))
            return 1
        fi
    else
        if eval "$check_command" > /dev/null 2>&1; then
            print_success "$check_name"
            ((TESTS_PASSED++))
            return 0
        else
            print_error "$check_name"
            ((TESTS_FAILED++))
            return 1
        fi
    fi
}

# ============================================================================
# CI/CD Validation Checks (mirrors .github/workflows/)
# ============================================================================

print_header "Local CI/CD Validation"
echo "Simulating GitHub Actions CI/CD pipeline locally"
echo "Project: $PROJECT_ROOT"
echo ""

# 1. YAML Validation (matches CI yaml validation)
print_header "1. YAML File Validation"
if [ -f "scripts/validation/validate_yaml_files.py" ]; then
    run_check "YAML syntax validation" "python3 scripts/validation/validate_yaml_files.py"
else
    print_warning "YAML validator not found, skipping"
fi

# 2. Python Tests (matches CI npm test)
print_header "2. Python Test Suite"
run_check "Python tests (pytest)" "npm test"

# 3. Build Validation (matches CI npm run build)
if [ "$FAST_MODE" = false ]; then
    print_header "3. Build Validation"
    run_check "Build process" "npm run build"
else
    print_info "Skipping build (fast mode)"
fi

# 4. Shell Script Validation (matches quality-gates job)
print_header "4. Shell Script Validation"
if compgen -G "scripts/*.sh" > /dev/null; then
    shell_errors=0
    for script in scripts/*.sh; do
        if bash -n "$script" 2>&1; then
            print_success "Shell syntax: $(basename "$script")"
        else
            print_error "Shell syntax: $(basename "$script")"
            ((shell_errors++))
        fi
    done

    if [ $shell_errors -eq 0 ]; then
        ((TESTS_PASSED++))
    else
        ((TESTS_FAILED++))
    fi
else
    print_info "No shell scripts found in scripts/"
fi

# 5. Security Validation (matches CI security check)
print_header "5. Security Validation"
security_issues=$(grep -rE "(password|secret|token)[[:space:]]*=[[:space:]]*['\"][^'\"]+['\"]" scripts/ --include="*.sh" 2>/dev/null | grep -v "example\|test\|comment\|TODO" || true)

if [ -z "$security_issues" ]; then
    print_success "No hardcoded credentials detected"
    ((TESTS_PASSED++))
else
    print_error "Potential hardcoded credentials detected"
    echo "$security_issues"
    ((TESTS_FAILED++))
fi

# 6. Agent and Command Validation (matches quality-gates)
print_header "6. nWave Framework Validation"
if [ -d "nWave/agents" ]; then
    agent_count=$(find nWave/agents -name "*.md" -type f 2>/dev/null | wc -l)
    if [ "$agent_count" -ge 10 ]; then
        print_success "Agent definitions: $agent_count found"
        ((TESTS_PASSED++))
    else
        print_warning "Agent definitions: only $agent_count found (expected >= 10)"
        ((TESTS_FAILED++))
    fi
else
    print_warning "nWave agents directory not found"
fi

if [ -d "nWave/tasks" ]; then
    command_count=$(find nWave/tasks -name "*.md" -type f 2>/dev/null | wc -l)
    print_success "Command definitions: $command_count found"
    ((TESTS_PASSED++))
else
    print_info "nWave tasks directory not found"
fi

# 7. Documentation Check (matches documentation-check job)
print_header "7. Documentation Validation"
required_docs=("README.md" "docs/installation/INSTALL.md")
doc_errors=0

for doc_file in "${required_docs[@]}"; do
    if [ -f "$doc_file" ]; then
        print_success "Documentation: $doc_file"
    else
        print_warning "Missing documentation: $doc_file"
        ((doc_errors++))
    fi
done

if [ $doc_errors -eq 0 ]; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi

# ============================================================================
# Results Summary
# ============================================================================

print_header "CI/CD Validation Results"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ ALL CHECKS PASSED${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "  Passed: $TESTS_PASSED"
    echo "  Failed: $TESTS_FAILED"
    echo ""
    echo "✓ Your code is ready for CI/CD!"
    echo "✓ Safe to push to remote repository"
    exit 0
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ VALIDATION FAILED${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "  Passed: $TESTS_PASSED"
    echo "  Failed: $TESTS_FAILED"
    echo ""
    echo "⚠ Fix the above issues before pushing"
    echo "⚠ CI/CD pipeline will fail with these errors"
    exit 1
fi
