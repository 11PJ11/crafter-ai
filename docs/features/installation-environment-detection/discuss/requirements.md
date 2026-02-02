# Requirements Specification: Installation Environment Detection

**Feature ID:** APEX-002
**Wave:** DISCUSS
**Status:** Draft
**Created:** 2026-01-29
**Stakeholder:** Mike (Project Owner)

---

## 1. Business Context

### 1.1 Problem Statement

Marco, a developer new to nWave, clones the repository on a fresh machine with only Python 3 installed. When he runs the installation script directly, he encounters a cryptic `ModuleNotFoundError: No module named 'yaml'` with no guidance on how to fix it. He spends 30 minutes searching documentation and forums before discovering he needs pipenv and a virtual environment.

### 1.2 Business Objective

New users approaching nWave must find clear documentation easy to consume that tells them how to install nWave on a virgin machine. The installation experience should be foolproof with proactive detection of environment issues and actionable guidance.

### 1.3 Success Criteria

- Zero users should encounter raw Python tracebacks during installation
- Installation failures provide immediate, actionable fix commands
- Time from clone to successful installation under 5 minutes for prepared environments
- 100% of environment issues detected before build attempt

---

## 2. Functional Requirements

### FR-01: Pre-flight Environment Validation

**Description:** The installer shall validate the Python environment before attempting any installation steps.

**Details:**
- Detect if running inside a virtual environment (pipenv)
- Verify all required Python modules are importable
- Check Python version compatibility (3.8+)
- Validate Pipfile exists in expected location

**Behavior:**
- All checks run before any installation action
- Failures block installation with actionable messages
- All check results logged to installation log

### FR-02: Virtual Environment Enforcement (Hard Block)

**Description:** The installer shall refuse to proceed if not running inside a virtual environment.

**Details:**
- Detect virtual environment via `sys.prefix != sys.base_prefix`
- No bypass flag or override option
- Error message provides exact pipenv commands to create/activate environment

**Rationale:** Enforces best practice, prevents global Python pollution, ensures reproducible installations.

### FR-03: Pipenv-Only Package Management

**Description:** The installer shall support only pipenv as the package manager.

**Details:**
- No fallback to pip, poetry, conda, or other tools
- Error messages reference pipenv commands exclusively
- Validate pipenv is installed and accessible

**Rationale:** Ensures consistent, reproducible installations across all users.

### FR-04: Context-Aware Error Messages

**Description:** Error messages shall adapt based on execution context.

**Details:**

**Terminal Execution:**
- Provide concise, actionable error message
- Include exact command to fix the issue
- Example: `Virtual environment required. Run: pipenv install --dev && pipenv shell`

**Claude Code Execution:**
- Return structured error that enables self-healing orchestration
- Include error code, description, and remediation command
- Enable automated retry after fix

**Both Contexts:**
- Log complete error details to installation log file
- Include timestamp, error type, and system state

### FR-05: Dependency Verification

**Description:** The installer shall verify all required dependencies before build.

**Details:**
- Check for required modules: yaml, pathlib, subprocess, sys
- Identify missing modules by name
- Provide pipenv install command for resolution

### FR-06: Automatic Post-Installation Verification

**Description:** The installer shall automatically verify successful installation.

**Details:**
- Check agent files exist in `~/.claude/agents/nw/` (expect 28+ files)
- Check command files exist in `~/.claude/commands/nw/` (expect 23 files)
- Verify manifest file exists and is readable
- Report verification results to user
- Log verification details to installation log

### FR-07: Standalone Verification Command

**Description:** A separate verification command shall be available for post-installation checks.

**Details:**
- Command: `pipenv run python scripts/install/verify_nwave.py` or similar
- Performs same checks as automatic verification
- Can be run independently at any time
- Returns clear pass/fail status with details

### FR-08: Installation Logging

**Description:** All installation activities shall be logged for debugging and improvement.

**Details:**
- Log file location: configurable, default to `~/.nwave/install.log`
- Log levels: INFO for normal flow, WARNING for recoverable issues, ERROR for failures
- Include timestamps, action descriptions, and outcomes
- Preserve logs across installation attempts for troubleshooting

---

## 3. Non-Functional Requirements

### NFR-01: Self-Healing Capability

**Description:** When executed within Claude Code, the installer shall return structured errors that enable automated remediation.

**Details:**
- Error responses include machine-readable error codes
- Remediation commands provided as executable strings
- Status codes distinguish recoverable vs fatal errors

### NFR-02: No Additional Runtime Dependencies

**Description:** The environment detection logic shall rely only on Python 3 standard library.

**Details:**
- Pre-flight checks cannot import yaml, toml, or other non-standard modules
- Detection logic uses only: sys, os, subprocess, pathlib
- Once environment validated, full dependencies available

### NFR-03: Performance

**Description:** Pre-flight checks shall complete within 2 seconds on standard hardware.

### NFR-04: Cross-Platform Compatibility

**Description:** Environment detection shall work on macOS, Linux, and Windows.

**Details:**
- Path handling uses pathlib for cross-platform compatibility
- Virtual environment detection works across all platforms
- Error messages use platform-appropriate path separators

---

## 4. Documentation Requirements

### DR-01: Installation Guide Update

**Description:** The installation guide shall be updated with correct prerequisites and commands.

**File:** `docs/installation/installation-guide.md`

**Changes Required:**
- Update prerequisites to include pipenv requirement
- Correct Python version to 3.8+ (not 3.11+)
- Add virtual environment setup section
- Update quick start with pipenv commands

### DR-02: Quick Start Section

**Description:** Quick start shall provide copy-paste commands that work on a virgin machine.

**Required Content:**
```bash
# Prerequisites (one-time)
pip3 install pipenv

# Setup and install
cd crafter-ai
pipenv install --dev
pipenv run python scripts/install/install_nwave.py

# Verify installation
pipenv run python scripts/install/verify_nwave.py
```

---

## 5. Constraints

### C-01: Python 3 Only
Installation must rely only on Python 3. No other runtime dependencies (Node.js, Ruby, etc.).

### C-02: Local Environment
Python environment must be LOCAL using pipenv. No global Python installation pollution.

### C-03: Dependencies First
Pipfile dependencies must be installed BEFORE running the installer. Script detects and blocks if violated.

### C-04: No Skip Flag
No `--skip-checks` or similar bypass. Environment validation is mandatory.

---

## 6. Assumptions

1. User has Python 3.8+ installed and accessible via `python3` command
2. User has network access to install pipenv via pip
3. User has write access to home directory (`~/.claude/`, `~/.nwave/`)
4. Repository is cloned with Pipfile present at root

---

## 7. Out of Scope

1. Support for package managers other than pipenv
2. Docker-based installation
3. System-wide installation (non-user directory)
4. Multilingual error messages (English only)
5. GUI installer

---

## 8. Glossary

| Term | Definition |
|------|------------|
| Pre-flight check | Validation performed before main installation begins |
| Virtual environment | Isolated Python environment created by pipenv |
| Self-healing | Ability for Claude Code to automatically remediate errors |
| Hard block | Installation refuses to proceed, no bypass available |

---

## 9. Traceability

| Requirement | Business Objective | Acceptance Criteria |
|-------------|-------------------|---------------------|
| FR-01 | Proactive issue detection | AC-01 |
| FR-02 | Enforce best practices | AC-02 |
| FR-03 | Consistent installations | AC-03 |
| FR-04 | Actionable guidance | AC-04, AC-05 |
| FR-05 | Proactive issue detection | AC-06 |
| FR-06 | Verification | AC-07 |
| FR-07 | Verification | AC-08 |
| FR-08 | Continuous improvement | AC-09 |
| DR-01, DR-02 | Clear documentation | AC-10 |
