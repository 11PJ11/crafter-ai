# Acceptance Criteria: Installation Environment Detection

**Feature ID:** APEX-002
**Wave:** DISCUSS
**Created:** 2026-01-29

---

## AC-01: Pre-flight Environment Check Runs First

### Scenario: Environment validation before any installation action

```gherkin
Given a user executes the nWave installer
When the installer starts
Then environment validation runs before any installation action
And the validation checks virtual environment status
And the validation checks pipenv availability
And the validation checks required dependencies
And the validation checks Python version
And all validation results are logged to installation log
```

### Scenario: Pre-flight check completes within performance threshold

```gherkin
Given a user executes the nWave installer
When the pre-flight environment check runs
Then all checks complete within 2 seconds
And the user sees progress indication during checks
```

---

## AC-02: Virtual Environment Hard Block

### Scenario: Installation blocked when not in virtual environment

```gherkin
Given Marco has Python 3.10 installed
And Marco is NOT inside a virtual environment
When Marco runs "python3 scripts/install/install_nwave.py"
Then the installer displays error containing "Virtual environment required"
And the installer displays fix command "pipenv install --dev && pipenv shell"
And the installer does NOT proceed to build phase
And the installer exits with code 1
And the error is logged with timestamp and system state
```

### Scenario: No bypass flag available

```gherkin
Given the installer supports command-line arguments
When a user passes "--skip-checks" or "--force" flag
Then the installer ignores the flag
And the installer still performs all environment checks
And no bypass mechanism is available
```

### Scenario: Installation proceeds when in virtual environment

```gherkin
Given Marco is inside a pipenv virtual environment
And all dependencies are installed
When Marco runs "python scripts/install/install_nwave.py"
Then the virtual environment check passes
And the installer proceeds to dependency verification
```

---

## AC-03: Pipenv-Only Enforcement

### Scenario: Pipenv not installed

```gherkin
Given Marco has Python 3.10 installed
And pipenv is NOT installed on the system
When Marco runs "python3 scripts/install/install_nwave.py"
Then the installer displays error "pipenv is required but not installed"
And the installer displays fix command "pip3 install pipenv"
And the installer does NOT suggest pip, poetry, or conda alternatives
And the installer exits with code 1
```

### Scenario: Error messages reference only pipenv

```gherkin
Given any environment check fails
When the installer displays remediation commands
Then all commands reference pipenv exclusively
And no alternative package managers are mentioned
And no fallback options are provided
```

---

## AC-04: Context-Aware Terminal Errors

### Scenario: Human-friendly error in terminal

```gherkin
Given the installer is running in a terminal (TTY)
And the virtual environment is not active
When the installer performs environment check
Then the installer displays formatted error with "[ERROR]" prefix
And the installer displays fix command with "[FIX]" prefix
And the installer displays next step with "[THEN]" prefix
And the error message uses human-readable language
```

### Scenario: Missing dependency error in terminal

```gherkin
Given Sofia is inside the pipenv shell
And the yaml module is NOT installed
When Sofia runs "python scripts/install/install_nwave.py"
Then the installer displays "[ERROR] Missing required module: yaml"
And the installer displays "[FIX] Run: pipenv install --dev"
And the installer displays "[THEN] Re-run the installer"
And the installer exits with code 1
```

---

## AC-05: Context-Aware Claude Code Errors

### Scenario: Structured JSON error in Claude Code context

```gherkin
Given the installer detects Claude Code execution context
And the virtual environment is not active
When the installer performs environment check
Then the installer outputs JSON to stdout
And the JSON contains "status": "error"
And the JSON contains "error_code": "ENV_NO_VENV"
And the JSON contains "message" with human description
And the JSON contains "remediation" with exact fix command
And the JSON contains "recoverable": true
And the error is logged to installation log
```

### Scenario: Claude Code context detection

```gherkin
Given the installer starts execution
When the installer checks execution context
Then the installer detects Claude Code environment variables
Or the installer detects non-TTY stdout
And the installer sets output mode accordingly
```

### Scenario: Self-healing error codes

```gherkin
Given the installer runs in Claude Code context
When any environment check fails
Then the error includes one of the defined error codes:
  | Error Code     | Condition                    | Recoverable |
  | ENV_NO_VENV    | Not in virtual environment   | true        |
  | ENV_NO_PIPENV  | Pipenv not installed         | true        |
  | DEP_MISSING    | Required module not found    | true        |
  | BUILD_FAILED   | Build phase error            | false       |
  | VERIFY_FAILED  | Verification found issues    | true        |
And Claude Code can parse the error and take action
```

---

## AC-06: Dependency Verification Before Build

### Scenario: All dependencies present

```gherkin
Given Sofia is inside the pipenv shell
And all required modules are installed (yaml, pathlib, etc.)
When Sofia runs "python scripts/install/install_nwave.py"
Then the dependency check passes
And the installer logs "Dependency check: PASSED"
And the installer proceeds to build phase
```

### Scenario: One dependency missing

```gherkin
Given Sofia is inside the pipenv shell
And the yaml module is NOT installed
When Sofia runs "python scripts/install/install_nwave.py"
Then the installer displays error listing "yaml" as missing
And the build phase does NOT start
And the installer exits with code 1
```

### Scenario: Multiple dependencies missing

```gherkin
Given Sofia is inside the pipenv shell
And modules yaml and toml are NOT installed
When Sofia runs "python scripts/install/install_nwave.py"
Then the installer displays error listing all missing modules
And the error message shows "Missing required modules: yaml, toml"
And the build phase does NOT start
```

---

## AC-07: Automatic Post-Installation Verification

### Scenario: Verification runs after successful build

```gherkin
Given Kenji is inside the pipenv shell
And all environment checks pass
And the build phase completes successfully
When the build phase finishes
Then automatic verification runs immediately
And Kenji sees agent file count verification
And Kenji sees command file count verification
And Kenji sees manifest file verification
And verification results are logged
```

### Scenario: Verification confirms expected file counts

```gherkin
Given the build phase completed successfully
When automatic verification runs
Then verification checks ~/.claude/agents/nw/ directory
And verification reports "28 agent files found" (or current expected count)
And verification checks ~/.claude/commands/nw/ directory
And verification reports "23 command files found" (or current expected count)
And verification checks ~/.claude/nwave-manifest.txt exists
```

### Scenario: Verification passes

```gherkin
Given all installation files are present
When automatic verification completes
Then Kenji sees "[SUCCESS] Installation verified. All components present."
And the installer exits with code 0
```

### Scenario: Verification detects issues

```gherkin
Given some agent files failed to install
When automatic verification runs
Then verification reports discrepancy in file counts
And verification displays "[WARNING] Expected 28 agent files, found 25"
And verification displays "[FIX] Re-run installer or check installation log"
And the installer exits with code 1
```

---

## AC-08: Standalone Verification Command

### Scenario: Verification command exists and runs

```gherkin
Given nWave is installed
When Kenji runs "pipenv run python scripts/install/verify_nwave.py"
Then the verification script executes
And verification checks all installation components
And verification reports status to stdout
```

### Scenario: Standalone verification passes

```gherkin
Given nWave is fully installed
And all expected files are present
When Kenji runs "pipenv run python scripts/install/verify_nwave.py"
Then verification reports all checks passed
And verification displays file counts for each component
And verification exits with code 0
```

### Scenario: Standalone verification fails

```gherkin
Given nWave is partially installed
And 3 agent files are missing
When Kenji runs "pipenv run python scripts/install/verify_nwave.py"
Then verification reports "[FAIL] Agent files: 25 found, 28 expected"
And verification provides remediation command
And verification exits with code 1
```

### Scenario: Verification without prior installation

```gherkin
Given nWave has never been installed
And ~/.claude/agents/nw/ does not exist
When Kenji runs "pipenv run python scripts/install/verify_nwave.py"
Then verification reports "[FAIL] nWave not installed"
And verification provides installation command
And verification exits with code 1
```

---

## AC-09: Installation Logging

### Scenario: Log file created

```gherkin
Given a user runs the installer
When the installer starts
Then a log file is created at ~/.nwave/install.log
Or the log file is appended if it exists
And the log includes session start timestamp
```

### Scenario: Successful actions logged

```gherkin
Given the installer runs successfully
When each check and action completes
Then the action is logged with timestamp
And the action is logged with outcome (PASS/FAIL)
And the log is human-readable
```

### Scenario: Errors logged with detail

```gherkin
Given an environment check fails
When the error is displayed to user
Then the complete error is also logged
And the log includes error type and message
And the log includes system state (Python version, venv status)
And the log includes remediation command shown to user
```

### Scenario: Log preserved across attempts

```gherkin
Given a previous installation attempt failed
And a log file exists from that attempt
When the user runs the installer again
Then the new session is appended to existing log
And previous session logs are preserved
And sessions are separated by clear markers
```

---

## AC-10: Documentation Accuracy

### Scenario: Prerequisites correctly stated

```gherkin
Given Alex reads docs/installation/installation-guide.md
When Alex views the prerequisites section
Then the documentation states "Python 3.8 or higher"
And the documentation states "pipenv" is required
And the documentation provides "pip3 install pipenv" command
```

### Scenario: Quick start commands work on virgin machine

```gherkin
Given Alex has a virgin machine with Python 3.8+
And Alex follows the quick start section exactly
When Alex executes:
  | Step | Command                                                |
  | 1    | pip3 install pipenv                                    |
  | 2    | cd crafter-ai                                          |
  | 3    | pipenv install --dev                                   |
  | 4    | pipenv run python scripts/install/install_nwave.py    |
  | 5    | pipenv run python scripts/install/verify_nwave.py     |
Then each command succeeds
And nWave is installed successfully
And verification passes
```

### Scenario: No undocumented prerequisites

```gherkin
Given a user follows only the documented prerequisites
When the user attempts installation
Then no additional tools or packages are required
And the installation succeeds without hidden dependencies
```

---

## Summary Matrix

| AC ID | Requirement | Story | Priority |
|-------|-------------|-------|----------|
| AC-01 | FR-01 | US-001 | High |
| AC-02 | FR-02 | US-001 | High |
| AC-03 | FR-03 | US-001 | High |
| AC-04 | FR-04 | US-001, US-002 | High |
| AC-05 | FR-04, NFR-01 | US-004 | Medium |
| AC-06 | FR-05 | US-002 | High |
| AC-07 | FR-06 | US-003 | Medium |
| AC-08 | FR-07 | US-003 | Medium |
| AC-09 | FR-08 | All | Medium |
| AC-10 | DR-01, DR-02 | US-005 | High |
