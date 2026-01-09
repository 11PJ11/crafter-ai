# AI-Craft Development Guide

## Pre-Commit Hook: Test Quality Gate

### Policy

This repository enforces **100% test passing** before any commit. This is a strict quality gate with no exceptions in automated enforcement.

**Automatic Enforcement**:
- Pre-commit hook runs ALL tests in `tests/` directory before every commit
- Commit is **blocked** if ANY test fails (exit code 1)
- Hook provides clear feedback with failed test details
- No exceptions in automated enforcement

**Rationale**:
- **Prevents broken code from entering git history** - Every commit is a stable checkpoint
- **Ensures continuous integration readiness** - All commits can be safely deployed
- **Maintains team velocity** - No "fix the build" overhead or merge conflicts from broken code
- **Enables safe experimentation** - Hook catches issues before they propagate
- **Quality is paramount** - Software craftsmanship requires 100% passing tests

### Emergency Bypass

**ONLY use `--no-verify` for critical scenarios**:
- Security patch requiring immediate deployment
- Production hotfix with time-critical deadline
- Critical bug fix that must bypass normal workflow temporarily

**Usage**:
```bash
git commit --no-verify -m "emergency: critical security patch"
```

**Requirements after emergency bypass**:
1. **Immediate follow-up commit** to fix tests and restore quality
2. **Document reason for bypass** in commit message (for audit trail)
3. **Notify team** of emergency commit and follow-up plan
4. **All `--no-verify` usage is logged** for audit purposes

### Hook Installation

Hook is automatically installed at `.git/hooks/pre-commit` (local to each clone).

**For new clones**, verify hook is present:
```bash
ls -la .git/hooks/pre-commit
# Should show: -rwxr-xr-x ... .git/hooks/pre-commit
```

**If missing**, copy from repository documentation or recreate using the script below.

### Hook Behavior

**When tests pass**:
```
Running pre-commit test validation...
Running test suite...
✓ All tests passing (16/16) - commit allowed
```

**When tests fail**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✗ COMMIT BLOCKED: Tests failed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Failed tests:
  FAILED tests/test_example.py::test_feature - AssertionError

Test Results: 15/16 passing (1 failed)

Fix failing tests before committing.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EMERGENCY BYPASS (use with extreme caution):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  git commit --no-verify -m "your message"

⚠️  WARNING: --no-verify should ONLY be used for:
  • Critical security patches
  • Emergency production fixes

You MUST create immediate follow-up commit to fix tests.
All --no-verify usage is logged for audit.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Graceful degradation**:
- If `python3` not available → Warning, commit allowed
- If `pytest` not installed → Warning, commit allowed
- If `tests/` directory missing → Skip testing, commit allowed

### Mikado Method Integration

**Mikado graph updates** should happen at **stable states** with passing tests:
- Complete a Mikado goal → tests pass → commit with graph update
- Work-in-progress (WIP) commits are **not allowed** (all tests must pass)
- Use `git stash` or feature branches for experimental work
- Mikado MCP server integration for workflow management

### Testing the Hook

**Test 1: Success Path** (all tests passing)
```bash
touch .test-file
git add .test-file
git commit -m "test: verify hook allows commit"
# Expected: ✓ All tests passing (16/16) - commit allowed
git reset HEAD~1  # Undo test commit
rm .test-file
```

**Test 2: Failure Path** (failing test blocks commit)
```bash
# Create failing test
cat > tests/test_hook_failure.py << 'EOF'
def test_intentional_failure():
    """Test to verify pre-commit hook blocks failing tests"""
    assert False, "Intentional failure to test hook"
EOF

git add tests/test_hook_failure.py
git commit -m "test: should be blocked"
# Expected: ✗ COMMIT BLOCKED: Tests failed

# Cleanup
git restore --staged tests/test_hook_failure.py
rm tests/test_hook_failure.py
```

**Test 3: Emergency Bypass**
```bash
# Create failing test
echo "def test_fail(): assert False" > tests/test_fail.py
git add tests/test_fail.py

# Emergency bypass (use with caution)
git commit --no-verify -m "emergency: demonstrate bypass"
# Expected: Commit succeeds despite failing test

# Immediate follow-up to fix
git restore --staged tests/test_fail.py
rm tests/test_fail.py
git commit -m "fix: remove failing test after emergency bypass"
```

### Pre-Commit Hook Source

The hook is installed at `.git/hooks/pre-commit`. If you need to recreate it:

```bash
#!/bin/bash
# Pre-commit hook: Enforce 100% test passing requirement
# Policy: NO EXCEPTIONS - All tests must pass before commit
# Emergency bypass: git commit --no-verify (EMERGENCY ONLY)

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test result flag file (for post-commit hook)
TEST_RESULT_FLAG=".git/hooks/last-test-result"

echo -e "${BLUE}Running pre-commit test validation...${NC}"

# Check if pytest is available
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Warning: python3 not available, skipping tests${NC}"
    echo "SKIP:python3_not_available" > "${TEST_RESULT_FLAG}"
    exit 0
fi

if ! python3 -m pytest --version &> /dev/null 2>&1; then
    echo -e "${YELLOW}Warning: pytest not available, skipping tests${NC}"
    echo "SKIP:pytest_not_available" > "${TEST_RESULT_FLAG}"
    exit 0
fi

# Check if tests directory exists
if [ ! -d "tests" ]; then
    echo -e "${YELLOW}No tests directory found, skipping tests${NC}"
    echo "SKIP:no_tests_directory" > "${TEST_RESULT_FLAG}"
    exit 0
fi

# Run tests and capture output
echo -e "${BLUE}Running test suite...${NC}"
TEST_OUTPUT=$(python3 -m pytest tests/ -v --tb=short 2>&1)
TEST_EXIT_CODE=$?

# Count tests (extract from pytest output)
TOTAL_TESTS=$(echo "$TEST_OUTPUT" | grep -oP '\d+(?= passed)' | head -1 || echo "0")
FAILED_TESTS=$(echo "$TEST_OUTPUT" | grep -oP '\d+(?= failed)' | head -1 || echo "0")

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passing (${TOTAL_TESTS}/${TOTAL_TESTS}) - commit allowed${NC}"
    echo "PASS:${TOTAL_TESTS}/${TOTAL_TESTS} tests | commit_allowed" > "${TEST_RESULT_FLAG}"
    exit 0
else
    echo ""
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}✗ COMMIT BLOCKED: Tests failed${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    # Show failed tests
    echo -e "${RED}Failed tests:${NC}"
    echo "$TEST_OUTPUT" | grep -E "FAILED|ERROR" | sed 's/^/  /'
    echo ""

    # Show test summary
    if [ "$FAILED_TESTS" != "0" ]; then
        PASSING_TESTS=$((TOTAL_TESTS - FAILED_TESTS))
        echo -e "${RED}Test Results: ${PASSING_TESTS}/${TOTAL_TESTS} passing (${FAILED_TESTS} failed)${NC}"
    fi

    echo ""
    echo -e "${YELLOW}Fix failing tests before committing.${NC}"
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}EMERGENCY BYPASS (use with extreme caution):${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "  ${BLUE}git commit --no-verify -m \"your message\"${NC}"
    echo ""
    echo -e "${RED}⚠️  WARNING: --no-verify should ONLY be used for:${NC}"
    echo -e "  • Critical security patches"
    echo -e "  • Emergency production fixes"
    echo ""
    echo -e "${RED}You MUST create immediate follow-up commit to fix tests.${NC}"
    echo -e "${RED}All --no-verify usage is logged for audit.${NC}"
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    # Write failure to flag file
    PASSING_TESTS=$((TOTAL_TESTS - FAILED_TESTS))
    echo "FAIL:${PASSING_TESTS}/${TOTAL_TESTS} tests | commit_blocked | ${FAILED_TESTS} failed" > "${TEST_RESULT_FLAG}"

    exit 1
fi
```

After creating the hook file:
```bash
chmod +x .git/hooks/pre-commit
```

## Development Workflow

### Standard Development Flow

1. **Create feature branch** (optional, but recommended for complex features)
2. **Write failing tests** (TDD approach)
3. **Implement feature** to make tests pass
4. **Run tests manually**: `python3 -m pytest tests/ -v`
5. **Commit** - Pre-commit hook runs automatically
6. **If tests fail** - Fix and retry commit
7. **If tests pass** - Commit succeeds

### Working with Failing Tests

**During development**, tests will fail. This is expected and part of TDD:
- Use `git stash` to save work-in-progress without committing
- Use feature branches for experimental work
- Fix tests before committing to main branch

**Never use `--no-verify` during normal development** - It bypasses the quality gate and should only be used in genuine emergencies.

## Testing Standards

### Test Requirements

- **All tests must RUN** - Non-executable tests count as failures
- **All tests must PASS** - 100% passing rate required
- **Tests must be isolated** - No shared mutable state between tests
- **Clean environment** - Each test creates and cleans up its own fixtures

### Test Organization

```
tests/
├── unit/                  # Fast, isolated unit tests
├── integration/           # Component integration tests
└── end_to_end/           # Full workflow tests
```

### Running Tests

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific test file
python3 -m pytest tests/test_example.py -v

# Run with coverage
python3 -m pytest tests/ --cov=src --cov-report=term-missing

# Run with parallel execution (if pytest-xdist installed)
python3 -m pytest tests/ -n auto
```

## Git Workflow

### Branch Strategy

- **Main branch** (`main` or `master`) - Always stable, all tests passing
- **Feature branches** - For complex features or experiments
- **Trunk-based development** - Favor working directly on main for small changes

### Commit Message Guidelines

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `test`: Adding or updating tests
- `refactor`: Code refactoring without behavior change
- `chore`: Maintenance tasks

**Examples**:
```
feat(auth): add JWT token validation

test(compiler): verify TOON parsing handles empty files

fix(hook): correct test count extraction in pre-commit hook
```

### Emergency Commit Protocol

**Only when absolutely necessary**:

1. **Assess** - Is this truly an emergency? (security patch, critical production fix)
2. **Document** - Clear commit message explaining bypass reason
3. **Bypass** - `git commit --no-verify -m "emergency: <reason>"`
4. **Follow-up** - Immediate commit to fix tests
5. **Notify** - Alert team of emergency bypass and follow-up

## CI/CD Integration

See [CI-CD-README.md](CI-CD-README.md) for continuous integration setup.

## Quality Standards

- **Software craftsmanship** - Quality is paramount
- **Fix all problems as they arise** - Don't defer quality
- **No shortcuts** - Quality saves time and prevents catastrophic failures
- **100% passing tests** - Non-negotiable production readiness requirement

---

**Remember**: The pre-commit hook is your safety net. It prevents broken code from entering git history and maintains the quality standards that make AI-Craft reliable.
