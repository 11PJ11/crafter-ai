# User Stories: Installation Environment Detection

**Feature ID:** APEX-002
**Wave:** DISCUSS
**Created:** 2026-01-29

---

## US-001: First-Time Installation on Virgin Machine

### Problem (The Pain)

Marco is a backend developer exploring nWave for his team's AI-assisted development workflow. He has just cloned the repository on his MacBook Pro with only Python 3.10 installed. When he runs `python3 scripts/install/install_nwave.py` as shown in the README, he gets a cryptic `ModuleNotFoundError: No module named 'yaml'` error. He spends 30 minutes searching documentation before realizing he needs pipenv and a virtual environment.

### Who (The User)

- Developer new to nWave, evaluating or adopting the framework
- Fresh machine with Python 3.8+ installed, no pipenv yet
- Comfortable with command line but unfamiliar with project specifics
- Wants to get running quickly without deep diving into project internals

### Solution (What We Build)

Pre-flight environment detection that catches missing prerequisites immediately, provides exact commands to fix the issue, and guides Marco from clone to successful installation in under 5 minutes.

### Domain Examples

#### Example 1: Marco Runs Installer Without Pipenv Installed
Marco on his MacBook Pro, Python 3.10 installed, no pipenv.
He runs `python3 scripts/install/install_nwave.py` from repository root.
Installer detects pipenv not installed, displays:
```
[ERROR] pipenv is required but not installed.
[FIX] Run: pip3 install pipenv
[THEN] Run: pipenv install --dev && pipenv run python scripts/install/install_nwave.py
```

#### Example 2: Marco Runs Installer Outside Virtual Environment
Marco has pipenv installed but runs installer directly without activating environment.
Installer detects no virtual environment active, displays:
```
[ERROR] Virtual environment required. You are running in global Python.
[FIX] Run: pipenv install --dev && pipenv shell
[THEN] Run: python scripts/install/install_nwave.py
```

#### Example 3: Marco Follows the Fix Commands
Marco runs `pipenv install --dev && pipenv shell` as instructed.
Marco runs `python scripts/install/install_nwave.py` inside the shell.
Installation completes successfully, automatic verification confirms 28 agent files and 23 command files installed.

### UAT Scenarios (BDD)

```gherkin
Scenario: Installation blocked when pipenv not installed
  Given Marco has Python 3.10 installed on his MacBook
  And pipenv is not installed
  When Marco runs "python3 scripts/install/install_nwave.py"
  Then the installer displays error "pipenv is required but not installed"
  And the installer displays fix command "pip3 install pipenv"
  And the installer exits with code 1
  And the error is logged to the installation log

Scenario: Installation blocked when not in virtual environment
  Given Marco has pipenv installed
  And Marco is not inside a pipenv virtual environment
  When Marco runs "python3 scripts/install/install_nwave.py"
  Then the installer displays error "Virtual environment required"
  And the installer displays fix command "pipenv install --dev && pipenv shell"
  And the installer exits with code 1
  And the error is logged to the installation log

Scenario: Successful installation in properly configured environment
  Given Marco has pipenv installed
  And Marco has run "pipenv install --dev"
  And Marco is inside the pipenv shell
  When Marco runs "python scripts/install/install_nwave.py"
  Then the installer completes successfully
  And automatic verification confirms agent files installed
  And automatic verification confirms command files installed
  And Marco sees "Installation complete. Verification passed."
```

### Acceptance Criteria

- [ ] Installer detects missing pipenv and provides installation command
- [ ] Installer detects global Python execution and blocks with venv setup command
- [ ] Installer proceeds only when all pre-flight checks pass
- [ ] Successful installation triggers automatic verification
- [ ] All scenarios logged to installation log file

### Technical Notes

- Pre-flight checks must use only Python standard library (sys, os, subprocess)
- Virtual environment detection: `sys.prefix != sys.base_prefix`
- Pipenv detection: `subprocess.run(['pipenv', '--version'])`

---

## US-002: Dependency Verification Before Build

### Problem (The Pain)

Sofia is re-installing nWave after a system update that cleared her Python packages. She activates her existing pipenv shell but hasn't run `pipenv install` to restore dependencies. The installer starts, begins the build phase, and fails mid-way with `ModuleNotFoundError`. She loses time waiting for partial build before seeing the error.

### Who (The User)

- Experienced nWave user returning after environment change
- Virtual environment exists but dependencies incomplete
- Expects quick reinstallation, frustrated by mid-process failures

### Solution (What We Build)

Dependency verification that checks all required modules are importable BEFORE attempting the build phase, failing fast with clear remediation.

### Domain Examples

#### Example 1: Sofia Has Stale Virtual Environment
Sofia on her workstation, pipenv shell active, but yaml module missing after system update.
She runs `python scripts/install/install_nwave.py`.
Installer checks dependencies, detects yaml missing, displays:
```
[ERROR] Missing required module: yaml
[FIX] Run: pipenv install --dev
[THEN] Re-run the installer
```
Build phase never starts. Time saved.

#### Example 2: Sofia Fixes Dependencies and Retries
Sofia runs `pipenv install --dev` as instructed.
Sofia re-runs `python scripts/install/install_nwave.py`.
All dependency checks pass, build proceeds and completes successfully.

### UAT Scenarios (BDD)

```gherkin
Scenario: Build blocked when dependencies missing
  Given Sofia is inside the pipenv shell
  And the yaml module is not installed
  When Sofia runs "python scripts/install/install_nwave.py"
  Then the installer displays error "Missing required module: yaml"
  And the installer displays fix command "pipenv install --dev"
  And the installer exits before build phase starts
  And the error is logged with module name

Scenario: Dependencies restored and installation proceeds
  Given Sofia is inside the pipenv shell
  And Sofia has run "pipenv install --dev"
  And all required modules are importable
  When Sofia runs "python scripts/install/install_nwave.py"
  Then the dependency check passes
  And the build phase starts
  And installation completes successfully
```

### Acceptance Criteria

- [ ] Installer checks all required modules before build phase
- [ ] Missing modules listed by name in error message
- [ ] Build phase does not start if dependencies missing
- [ ] Pipenv install command provided as remediation

### Technical Notes

- Required modules to check: yaml, pathlib (verify actual list in implementation)
- Use try/except import pattern for standard library check
- Log which modules passed/failed for debugging

---

## US-003: Post-Installation Verification

### Problem (The Pain)

Kenji completed the installation and saw "Build completed successfully" but isn't sure if everything installed correctly. He wants to verify the installation worked before he starts using nWave. Later, after a system update, he wants to check if his installation is still intact without reinstalling.

### Who (The User)

- User who just completed installation, wants confirmation
- User returning after system changes, wants health check
- Methodical personality, appreciates verification steps

### Solution (What We Build)

Automatic verification at end of installation plus standalone verification command for on-demand checks.

### Domain Examples

#### Example 1: Automatic Verification After Installation
Kenji completes installation inside pipenv shell.
Installer automatically runs verification, displays:
```
[VERIFY] Checking agent files... 28 files found in ~/.claude/agents/nw/
[VERIFY] Checking command files... 23 files found in ~/.claude/commands/nw/
[VERIFY] Checking manifest... ~/.claude/nwave-manifest.txt exists
[SUCCESS] Installation verified. All components present.
```

#### Example 2: Standalone Verification After System Update
Kenji returns one week later after macOS update.
He runs `pipenv run python scripts/install/verify_nwave.py`.
Verification checks all components, reports all present.
Kenji is confident his installation is intact.

#### Example 3: Verification Detects Missing Files
Kenji accidentally deleted some agent files.
He runs verification command.
Verification reports:
```
[VERIFY] Checking agent files... 25 files found (expected 28)
[WARNING] Missing agent files detected
[FIX] Re-run: pipenv run python scripts/install/install_nwave.py
```

### UAT Scenarios (BDD)

```gherkin
Scenario: Automatic verification after successful installation
  Given Kenji has completed the installation in pipenv shell
  When the build phase completes successfully
  Then the installer automatically runs verification
  And Kenji sees agent file count (28 expected)
  And Kenji sees command file count (23 expected)
  And Kenji sees manifest file confirmation
  And Kenji sees "Installation verified" message

Scenario: Standalone verification passes
  Given Kenji has nWave installed
  And all installation files are present
  When Kenji runs "pipenv run python scripts/install/verify_nwave.py"
  Then verification reports all checks passed
  And verification exits with code 0

Scenario: Standalone verification detects missing files
  Given Kenji has nWave partially installed
  And some agent files are missing
  When Kenji runs "pipenv run python scripts/install/verify_nwave.py"
  Then verification reports missing files
  And verification provides re-installation command
  And verification exits with code 1
```

### Acceptance Criteria

- [ ] Automatic verification runs at end of successful installation
- [ ] Standalone verification command available
- [ ] Verification checks agent files, command files, and manifest
- [ ] Missing file count reported with expected count
- [ ] Remediation command provided when issues detected

### Technical Notes

- Agent files location: `~/.claude/agents/nw/`
- Command files location: `~/.claude/commands/nw/`
- Manifest location: `~/.claude/nwave-manifest.txt`
- Expected counts may vary by version; read from manifest or config

---

## US-004: Claude Code Self-Healing Installation

### Problem (The Pain)

Vera, the nWave orchestrator running in Claude Code, attempts to guide a new user through installation. The installation fails due to environment issues. Vera receives a raw error message that isn't machine-parseable, making automated remediation difficult.

### Who (The User)

- Claude Code agent (Vera) orchestrating installation
- Needs structured error responses for automated handling
- Expects self-healing capability for common issues

### Solution (What We Build)

Context-aware error responses that return structured, machine-readable errors when running in Claude Code context, enabling automated remediation and retry.

### Domain Examples

#### Example 1: Claude Code Receives Structured Error
Vera invokes installer, no virtual environment active.
Installer detects Claude Code context, returns:
```json
{
  "status": "error",
  "error_code": "ENV_NO_VENV",
  "message": "Virtual environment required",
  "remediation": "pipenv install --dev && pipenv shell",
  "recoverable": true
}
```
Vera executes remediation command and retries.

#### Example 2: Terminal User Receives Human-Friendly Error
Marco runs installer from terminal.
Installer detects terminal context, displays:
```
[ERROR] Virtual environment required. You are running in global Python.
[FIX] Run: pipenv install --dev && pipenv shell
[THEN] Run: python scripts/install/install_nwave.py
```

### UAT Scenarios (BDD)

```gherkin
Scenario: Structured error returned in Claude Code context
  Given the installer is running in Claude Code context
  And the virtual environment is not active
  When the installer performs environment check
  Then the installer returns JSON with error_code "ENV_NO_VENV"
  And the installer returns remediation command
  And the installer indicates error is recoverable
  And the error is logged to installation log

Scenario: Human-friendly error shown in terminal context
  Given the installer is running in terminal context
  And the virtual environment is not active
  When the installer performs environment check
  Then the installer displays formatted error message
  And the installer displays fix command with human-friendly labels
  And the error is logged to installation log
```

### Acceptance Criteria

- [ ] Installer detects execution context (Claude Code vs terminal)
- [ ] Claude Code context receives JSON-structured errors
- [ ] Terminal context receives human-formatted messages
- [ ] Both contexts log complete error details
- [ ] Recoverable errors marked as such for retry logic

### Technical Notes

- Context detection: Check for Claude Code environment variables or invocation pattern
- Error codes: ENV_NO_VENV, ENV_NO_PIPENV, DEP_MISSING, BUILD_FAILED
- JSON output when stdout is not a TTY may be one approach

---

## US-005: Installation Documentation Clarity

### Problem (The Pain)

Alex reads the installation guide and follows the quick start section exactly. The guide says `python3 scripts/install/install_nwave.py` without mentioning pipenv or virtual environment setup. Alex gets the yaml error and feels the documentation failed them.

### Who (The User)

- New user relying on documentation
- Follows instructions literally
- Expects documentation to provide complete, working commands

### Solution (What We Build)

Updated installation documentation with accurate prerequisites, correct Python version, and complete pipenv-based installation commands.

### Domain Examples

#### Example 1: Alex Follows Updated Quick Start
Alex reads updated installation guide quick start:
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
Alex follows commands exactly, installation succeeds first try.

#### Example 2: Alex Checks Prerequisites
Alex reads prerequisites section:
```
Prerequisites:
- Python 3.8 or higher
- pipenv (pip3 install pipenv)
```
Alex verifies Python version, installs pipenv, proceeds with confidence.

### UAT Scenarios (BDD)

```gherkin
Scenario: Documentation provides working quick start
  Given Alex has Python 3.8+ installed
  And Alex follows the quick start commands exactly
  When Alex executes each command in sequence
  Then pipenv is installed successfully
  And dependencies are installed successfully
  And nWave installer completes successfully
  And verification passes

Scenario: Documentation states correct prerequisites
  Given Alex reads the prerequisites section
  When Alex checks the Python version requirement
  Then the documentation states "Python 3.8 or higher"
  And the documentation states pipenv is required
  And the documentation provides pipenv installation command
```

### Acceptance Criteria

- [ ] Quick start provides complete, copy-paste commands
- [ ] Prerequisites list includes pipenv with installation command
- [ ] Python version correctly stated as 3.8+
- [ ] Verification command included in quick start
- [ ] No user action required beyond what documentation specifies

### Technical Notes

- File to update: `docs/installation/installation-guide.md`
- Ensure examples work on macOS, Linux, and Windows
- Test documentation on virgin machine to validate

---

## Story Map Summary

| Story ID | User | Need | Priority |
|----------|------|------|----------|
| US-001 | Marco (new user) | First-time installation guidance | High |
| US-002 | Sofia (returning user) | Dependency verification | High |
| US-003 | Kenji (methodical user) | Installation verification | Medium |
| US-004 | Vera (Claude Code) | Self-healing errors | Medium |
| US-005 | Alex (documentation follower) | Clear documentation | High |
