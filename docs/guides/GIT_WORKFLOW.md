# Git Workflow and Quality Standards

## Pre-Commit Hook: 100% Test Passing Requirement

### Policy

**STRICT ENFORCEMENT**: All commits MUST have 100% passing tests. NO EXCEPTIONS.

The pre-commit hook automatically runs the entire test suite before allowing any commit. If ANY test fails, the commit is blocked.

### How It Works

**On every `git commit` attempt:**

1. Hook runs all tests: `pytest tests/ -v`
2. Hook evaluates results:
   - **All tests pass** → Commit allowed ✓
   - **Any test fails** → Commit blocked ✗

**Audit Logging:**
- All commit attempts logged to `.git/hooks/pre-commit.log`
- Log format: `timestamp | commit_hash | status | details`
- Includes PASS, FAIL, SKIP, and BYPASS events

### Normal Workflow

```bash
# Make changes
vim src/my_feature.py

# Add changes
git add src/my_feature.py

# Attempt commit (triggers pre-commit hook)
git commit -m "feat: add new feature"

# Hook runs tests automatically
# ✓ All tests passing (16/16) - commit allowed
# [feature-branch abc1234] feat: add new feature
```

### When Tests Fail

```bash
git commit -m "feat: add new feature"

# Hook output:
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ✗ COMMIT BLOCKED: Tests failed
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# Failed tests:
#   FAILED tests/test_feature.py::test_example
#
# Test Results: 15/16 passing (1 failed)
#
# Fix failing tests before committing.
```

**Required Action:**
1. Fix the failing tests
2. Run tests manually to verify: `pytest tests/`
3. Retry commit once tests pass

### Emergency Bypass Protocol

**⚠️ USE WITH EXTREME CAUTION**

The `--no-verify` flag bypasses the pre-commit hook. This should ONLY be used for:

- **Critical security patches** requiring immediate deployment
- **Emergency production fixes** where delayed commit creates higher risk

**Usage:**
```bash
git commit --no-verify -m "security: emergency patch for CVE-2026-XXXXX"
```

**MANDATORY Follow-Up:**
1. **Immediately** fix failing tests
2. Create follow-up commit with passing tests within same work session
3. Document reason for bypass in commit message or audit log
4. All `--no-verify` usage is logged and flagged for audit

**Detection:**
- Post-commit hook detects bypass usage
- Logs entry: `BYPASS | --no-verify used | ⚠️ AUDIT REQUIRED`
- Displays warning message after commit

### Audit Log

**Location**: `.git/hooks/pre-commit.log`

**Example entries:**
```
2026-01-08T15:30:00Z | abc1234 | PASS | 16/16 tests | commit_allowed
2026-01-08T15:45:00Z | def5678 | FAIL | 14/16 tests | commit_blocked | 2 failed
2026-01-08T16:00:00Z | ghi9012 | BYPASS | --no-verify used | ⚠️ AUDIT REQUIRED
2026-01-08T16:05:00Z | jkl3456 | PASS | 16/16 tests | commit_allowed
```

**Review audit log:**
```bash
cat .git/hooks/pre-commit.log
```

**Check for bypasses:**
```bash
grep "BYPASS" .git/hooks/pre-commit.log
```

### Setup in New Clones

The pre-commit hook is installed locally in `.git/hooks/` and is NOT committed to the repository.

**For new clones, the hook must be set up manually:**

1. Clone repository:
   ```bash
   git clone <repository-url>
   cd ai-craft
   ```

2. Hook should already exist at `.git/hooks/pre-commit`
   - If not, contact team lead for hook installation script

3. Verify hook is executable:
   ```bash
   ls -la .git/hooks/pre-commit
   # Should show: -rwxr-xr-x (executable permissions)
   ```

4. Test hook:
   ```bash
   # Make trivial change
   echo "# test" >> README.md
   git add README.md
   git commit -m "test: verify pre-commit hook"
   # Should see: "Running pre-commit test validation..."
   ```

### Troubleshooting

**Hook doesn't run:**
- Verify hook is executable: `chmod +x .git/hooks/pre-commit`
- Check hook exists: `ls -la .git/hooks/pre-commit`

**Hook fails with "pytest not available":**
- Install pytest: `pip install pytest`
- Verify installation: `pytest --version`

**Hook runs but tests not found:**
- Verify tests directory exists: `ls tests/`
- Run tests manually: `pytest tests/`

**Need to skip hook temporarily (NOT RECOMMENDED):**
- Use `--no-verify` (see Emergency Bypass Protocol above)
- MUST fix tests and commit follow-up immediately

### Philosophy

**Why strict enforcement?**

From project quality standards:

> "All tests must RUN. All tests must PASS. Not working tests count as test failures and must be fixed. NO EXCEPTIONS"

> "NEVER EVER COMMIT WITH FAILING TESTS!!! NO EXCEPTIONS!"

> "Anything below 100% passing tests IS NOT PRODUCTION READY - could create catastrophic production failures"

**Quality saves time, money, and lives in the long run.**

The pre-commit hook enforces this standard automatically, preventing broken code from entering the codebase and maintaining a stable foundation for all development.

### Related Documentation

- **Testing Philosophy**: See `CLAUDE.md` → Testing Principles
- **Quality Standards**: See `CLAUDE.md` → Quality Standards
- **CI/CD Pipeline**: See `docs/CI-CD-README.md`
# Test comment
