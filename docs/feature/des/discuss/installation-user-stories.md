# nWave+DES Installation & Uninstallation - User Stories

**Version:** 1.1
**Date:** 2026-01-23
**Status:** DISCUSS Wave - Updated (Virtual Environment Isolation)
**Integration**: These stories extend the DES feature set to include installation/uninstallation workflows
**Update**: Added virtual environment isolation requirements across all installation stories (57 acceptance criteria total)

---

## Personas

### Marcus (Senior Developer)
- **Experience:** 8+ years, TDD practitioner
- **Context:** Wants to add nWave to existing project for workflow automation
- **Pain:** Complex installation procedures waste time; manual configuration is error-prone
- **Goal:** Install nWave+DES with single command and start using immediately

### Priya (Tech Lead)
- **Experience:** 12+ years, team onboarding responsibility
- **Context:** Needs to onboard team to nWave methodology quickly
- **Pain:** Team members struggle with inconsistent setup; troubleshooting installation issues delays productivity
- **Goal:** Reliable, transparent installation that team can verify and trust

### Alex (Junior Developer)
- **Experience:** 1 year, learning TDD methodology
- **Context:** First time using nWave, needs simple setup
- **Pain:** Overwhelmed by complex installation procedures; unclear what was installed and where
- **Goal:** Clear installation process with verification that everything works

---

## User Stories

### US-INSTALL-001: One-Command nWave+DES Installation

**As** Marcus (Senior Developer),
**I want** to install nWave (including DES) with a single command,
**So that** I can start using nWave workflows without manual configuration.

**Story Points:** 5
**Priority:** P0 (Must Have - Blocker for all other stories)

#### Problem (The Pain)

Marcus has an existing Python project and wants to add nWave workflow automation. He doesn't want to:
- Manually copy files to specific directories (~/.claude/nwave/)
- Edit configuration files by hand (hooks, agent configs)
- Set up DES components manually
- Remember complex setup procedures from documentation

When he tried to set up nWave manually in a previous project, he spent 3 hours debugging why hooks weren't working (wrong file permissions) and another hour figuring out where agent templates should go.

#### Who (The User)

- Senior developer with existing Claude Code environment
- Wants to integrate nWave into current project
- Values reliability and time efficiency
- Comfortable with command-line tools (pip, npm, shell scripts)

#### Solution (What We Build)

Single-command installation that:
1. Detects Claude Code environment automatically (~/.claude/ directory)
2. Installs all nWave components (CLI, agents, templates, DES)
3. Configures hooks automatically (SubagentStop for DES validation)
4. Validates installation with health check
5. Provides clear output showing what was installed and where

#### Domain Examples

**Example 1: Fresh Installation on macOS**
```bash
$ pip install nwave
Collecting nwave
  Downloading nwave-1.0.0-py3-none-any.whl (250 kB)
Installing collected packages: nwave
Successfully installed nwave-1.0.0

$ nwave install
nWave Installation v1.0.0
=======================

Detecting environment...
✓ Claude Code detected at: /Users/marcus/.claude/
✓ Python 3.11.5 (compatible)
✓ Git repository detected: /Users/marcus/projects/myapp/

Creating virtual environment...
✓ Virtual environment created at: /Users/marcus/.claude/nwave/venv/
✓ Virtual environment using Python 3.11.5
ℹ Benefits: Isolated from global Python (no dependency conflicts)

Installing components...
✓ nWave CLI installed to venv: /Users/marcus/.claude/nwave/venv/bin/nwave
✓ DES components installed to venv: /Users/marcus/.claude/nwave/venv/lib/python3.11/site-packages/nwave/
✓ Agent definitions synced to: /Users/marcus/.claude/agents/nw/
✓ Templates synced to: /Users/marcus/.claude/templates/nw/
✓ SubagentStop hook configured at: /Users/marcus/.claude/hooks/subagent-stop.py

Running health checks...
✓ Virtual environment operational
✓ CLI accessible: 'nwave --version' → 1.0.0
✓ DES validation library importable
✓ SubagentStop hook callable
✓ Agent files readable (12 agents registered)
✓ Global Python environment unchanged (no packages installed)

Installation complete!

Virtual Environment Details:
  Location: ~/.claude/nwave/venv/
  Python: 3.11.5
  Packages: nwave==1.0.0 (zero external dependencies)
  Activation: Automatic (no manual activation needed for nwave commands)
  Manual activation: source ~/.claude/nwave/venv/bin/activate

Next steps:
  - Run 'nwave --help' to see available commands
  - Try '/nw:execute @researcher "your first task"' in Claude
  - Read quickstart: ~/.claude/nwave/docs/quickstart.md

Installation log: ~/.claude/nwave/install-2026-01-23.log
```

**Example 2: Upgrade Existing Installation**
```bash
$ nwave --version
nWave CLI v0.9.2

$ pip install --upgrade nwave
Upgrading nwave 0.9.2 → 1.0.0...

$ nwave install --upgrade
nWave Installation v1.0.0 (Upgrade Mode)
========================================

Detecting existing installation...
✓ Found nWave v0.9.2 at: /Users/marcus/.claude/nwave/
✓ Backup created at: /Users/marcus/.claude/nwave.backup-2026-01-23/

Preserving user data...
✓ Feature documentation preserved: docs/feature/
✓ Step files preserved: docs/feature/*/steps/
✓ Audit logs preserved: .nwave/audit/
✓ User configuration preserved: ~/.claude/nwave/config.yaml

Upgrading components...
✓ DES data models migrated: v1.3 → v1.4 (1 step file updated)
✓ Hook implementation updated (SubagentStop v2.0)
✓ Agent definitions updated (3 new agents, 2 updated)
✓ Templates refreshed (5 new templates)

Running health checks...
✓ All components operational
✓ Existing step files compatible

Upgrade complete!

Changes:
  - New feature: Installation/Uninstallation workflows (US-INSTALL-001)
  - Breaking change: None
  - Migration notes: ~/.claude/nwave/MIGRATION-0.9-to-1.0.md

Rollback: nwave install --rollback 2026-01-23
```

**Example 3: Installation in CI/CD Environment**
```bash
$ pip install nwave

$ nwave install --ci
nWave Installation v1.0.0 (CI Mode)
====================================

Detecting environment...
⚠ Claude Code NOT detected (expected in CI)
✓ Python 3.11.5 (compatible)
✓ Git repository detected

Installing components (CI mode)...
✓ nWave CLI installed to: /home/ci/.local/bin/
✓ DES validation library installed
⚠ Hooks skipped (--ci flag: no Claude Code environment)
⚠ Agents skipped (--ci flag: not needed for validation)
⚠ Templates skipped (--ci flag: not needed for validation)

Running health checks...
✓ CLI accessible
✓ DES validation importable
⚠ Claude integration: N/A (CI mode)

Installation complete (CI mode)!

Available in CI:
  - nwave validate-step <step-file>
  - nwave lint-uat <uat-file>
  - nwave audit-report <audit-log>

Not available in CI:
  - /nw:* commands (require Claude Code)
  - Agent execution
```

**Example 4: Installation Failure - Permissions Issue**
```bash
$ nwave install
nWave Installation v1.0.0
=======================

Detecting environment...
✓ Claude Code detected at: /Users/marcus/.claude/
✓ Python 3.11.5 (compatible)

Installing components...
✗ ERROR: Permission denied writing to /Users/marcus/.claude/hooks/

Diagnosis:
  - File ownership: root (expected: marcus)
  - Permissions: 0755 (expected: writable by user)

Recovery suggestions:
  1. Fix ownership: sudo chown -R marcus:staff ~/.claude/
  2. Fix permissions: chmod -R u+w ~/.claude/hooks/
  3. Re-run: nwave install

Installation failed. No changes were made.
Error details: ~/.claude/nwave/install-error-2026-01-23.log
```

**Example 5: Installation Failure - Virtual Environment Creation Failed**
```bash
$ nwave install
nWave Installation v1.0.0
=======================

Detecting environment...
✓ Claude Code detected at: /Users/marcus/.claude/
✓ Python 3.11.5 (compatible)

Creating virtual environment...
✗ ERROR: Cannot create virtual environment

Diagnosis:
  - Python venv module not available
  - Cause: Python installation incomplete (missing ensurepip or venv module)
  - Common on: Debian/Ubuntu minimal Python installations

Recovery suggestions (Ubuntu/Debian):
  1. Install venv module: sudo apt install python3.11-venv
  2. Re-run: nwave install

Recovery suggestions (macOS):
  1. Reinstall Python from python.org (includes venv by default)
  2. Or use Homebrew: brew reinstall python@3.11

Recovery suggestions (Windows):
  1. Reinstall Python with "pip" option checked in installer
  2. Or use: python -m ensurepip --upgrade

Installation failed. No changes were made.
Error details: ~/.claude/nwave/install-error-2026-01-23.log
```

#### Acceptance Criteria

- [ ] AC-001.1: Single command (`nwave install`) installs all components (CLI, DES, agents, templates, hooks)
- [ ] AC-001.2: Installation detects Claude Code environment automatically (checks for ~/.claude/ directory)
- [ ] AC-001.3: Hooks are configured automatically with correct permissions (executable, correct owner)
- [ ] AC-001.4: Installation is idempotent (safe to run multiple times - detects existing installation)
- [ ] AC-001.5: Installation output shows what was installed and file paths (transparency requirement)
- [ ] AC-001.6: Health check runs post-installation and reports component status
- [ ] AC-001.7: Installation creates log file with detailed trace for troubleshooting
- [ ] AC-001.8: Upgrade mode preserves user data (feature docs, step files, audit logs, config)
- [ ] AC-001.9: CI mode skips Claude-specific components (hooks, agents) and runs minimal installation
- [ ] AC-001.10: Installation failures provide clear error message, diagnosis, and recovery suggestions
- [ ] AC-001.11: Installation completes in < 30 seconds for fresh install, < 60 seconds for upgrade
- [ ] AC-001.12: Virtual environment created at ~/.claude/nwave/venv/ with Python packages isolated from global environment
- [ ] AC-001.13: Installation output explicitly shows virtual environment creation and explains isolation benefit
- [ ] AC-001.14: nWave CLI automatically uses virtual environment (no manual activation required by users)
- [ ] AC-001.15: Global Python environment verification shows no nWave packages installed globally
- [ ] AC-001.16: Virtual environment creation failure provides platform-specific recovery guidance

#### Technical Notes

- **Dependency**: Python 3.11+ (stdlib only, zero external dependencies)
- **Installation scope**: User-scoped (~/.claude/) not system-wide (/usr/local/)
- **Hooks**: SubagentStop hook must be executable and imported by Claude Code
- **Upgrade strategy**: Backup existing installation before modification, rollback capability
- **Safety**: Installation is non-destructive (creates directories, does not delete existing files)

---

### US-INSTALL-002: Clean nWave+DES Uninstallation

**As** Priya (Tech Lead),
**I want** to uninstall nWave completely with a single command,
**So that** I can remove nWave if the team decides not to use it.

**Story Points:** 3
**Priority:** P0 (Must Have - Critical for trial adoption)

#### Problem (The Pain)

Priya's team tried nWave for 2 sprints but decided to use a different workflow tool (team preferred Notion for documentation). She needs to:
- Remove all nWave files without breaking Claude Code
- Restore original Claude Code configuration (if any hooks were modified)
- Not leave behind orphaned files or configurations that clutter the system
- Ensure clean state for potential reinstallation later

When she tried to manually remove a previous tool, she accidentally deleted shared Claude configurations and broke other workflows. She wants uninstallation to be as reliable as installation.

#### Who (The User)

- Tech Lead responsible for team tooling decisions
- Needs clean removal for tool evaluation process
- Values safety (no accidental deletions) and completeness (no orphaned files)
- May want to reinstall later after team decision

#### Solution (What We Build)

Single-command uninstallation that:
1. Identifies all nWave components automatically
2. Creates backup before removal (safety net)
3. Removes nWave files selectively (preserves user data by default)
4. Offers option to delete user data (feature docs, step files)
5. Provides clear output showing what was removed

#### Domain Examples

**Example 1: Standard Uninstallation (Preserve User Data)**
```bash
$ nwave uninstall
nWave Uninstallation v1.0.0
===========================

Detecting installation...
✓ nWave v1.0.0 found at: /Users/priya/.claude/nwave/
✓ Components detected:
  - Virtual environment (venv/)
  - CLI (venv/bin/nwave)
  - DES validation library (venv/lib/python3.11/site-packages/nwave/)
  - Agent definitions (12 agents in ~/.claude/agents/nw/)
  - Templates (15 templates in ~/.claude/templates/nw/)
  - SubagentStop hook (~/.claude/hooks/subagent-stop.py)

User data detected:
  - Feature documentation: docs/feature/ (5 features, 127 files)
  - Step files: docs/feature/*/steps/ (23 steps)
  - Audit logs: .nwave/audit/ (15 days of logs)
  - Configuration: ~/.claude/nwave/config.yaml

⚠ This will remove nWave but PRESERVE user data.

What to remove:
  ✓ Virtual environment and all Python packages
  ✓ nWave CLI and libraries
  ✓ Agent definitions and templates
  ✓ SubagentStop hook
  ✗ User data (use --delete-data to remove)

Create backup before uninstalling? [Y/n]: Y

Creating backup...
✓ Backup created at: /Users/priya/.claude/nwave.backup-2026-01-23/
  (Size: 15 MB, includes all nWave files + user data)

Uninstalling components...
✓ Virtual environment removed from: /Users/priya/.claude/nwave/venv/
✓ nWave CLI removed (from venv)
✓ DES components removed (from venv)
✓ SubagentStop hook removed from: /Users/priya/.claude/hooks/
✓ Agent definitions removed from: /Users/priya/.claude/agents/nw/
✓ Templates removed from: /Users/priya/.claude/templates/nw/

Environment verification...
✓ Global Python environment unchanged (no nWave packages found)
✓ No orphaned Python packages remaining

User data preserved:
  ✓ Feature documentation: docs/feature/
  ✓ Step files: docs/feature/*/steps/
  ✓ Audit logs: .nwave/audit/
  ✓ Configuration: ~/.claude/nwave/config.yaml

Uninstallation complete!

Preserved data location: Current working directory
Backup location: /Users/priya/.claude/nwave.backup-2026-01-23/
Restore: nwave install --restore 2026-01-23

Your global Python environment is clean (no nWave packages were installed globally).
To remove user data: nwave uninstall --delete-data
```

**Example 2: Complete Uninstallation (Delete All Data)**
```bash
$ nwave uninstall --delete-data
nWave Uninstallation v1.0.0 (Delete All Data)
==============================================

⚠ WARNING: This will delete ALL nWave data including:
  - Feature documentation (docs/feature/)
  - Step files (docs/feature/*/steps/)
  - Audit logs (.nwave/audit/)
  - Configuration files (~/.claude/nwave/config.yaml)
  - Backup history (~/.claude/nwave.backup-*/)

⚠ This action CANNOT be undone without backups.

Files to be deleted:
  - 5 features with 127 documentation files
  - 23 step files with execution history
  - 15 days of audit logs (3.2 MB)
  - 2 configuration files
  - 3 previous backups (45 MB total)

Create final backup before deletion? [Y/n]: Y

Creating final backup...
✓ Final backup created at: /Users/priya/.claude/nwave.FINAL-backup-2026-01-23/
  (Size: 60 MB, includes ALL nWave data ever created)

Uninstalling components...
✓ nWave CLI removed
✓ DES components removed
✓ SubagentStop hook removed
✓ Agent definitions removed
✓ Templates removed

Deleting user data...
✓ Feature documentation deleted: docs/feature/
✓ Step files deleted: docs/feature/*/steps/
✓ Audit logs deleted: .nwave/audit/
✓ Configuration deleted: ~/.claude/nwave/
✓ Old backups deleted: ~/.claude/nwave.backup-*/

Uninstallation complete (all data removed)!

Final backup location: /Users/priya/.claude/nwave.FINAL-backup-2026-01-23/
Restore: nwave install --restore 2026-01-23

nWave is completely removed from this system.
```

**Example 3: Uninstallation with Rollback**
```bash
$ nwave uninstall
[... uninstallation completes ...]

$ # Oh no, team changed their mind - we need nWave back!

$ nwave install --restore 2026-01-23
nWave Installation v1.0.0 (Restore Mode)
========================================

Detecting backup...
✓ Backup found: /Users/priya/.claude/nwave.backup-2026-01-23/
  (Created: 2026-01-23 14:30:15, Size: 15 MB)

Backup contents:
  - nWave v1.0.0 (all components)
  - User data: 5 features, 23 steps, 15 days audit logs
  - Configuration: config.yaml

Restoring from backup...
✓ nWave components restored
✓ User data restored
✓ Configuration restored
✓ Hooks re-enabled

Running health checks...
✓ All components operational

Restoration complete!

System state: Identical to pre-uninstallation state
Next steps: Continue using nWave as before
```

**Example 4: Partial Uninstallation (CLI Only)**
```bash
$ nwave uninstall --keep-agents --keep-templates
nWave Uninstallation v1.0.0 (Partial Mode)
===========================================

Partial uninstallation requested:
  ✓ Remove: CLI, DES library, hooks
  ✗ Keep: Agent definitions, templates

Creating backup...
✓ Backup created

Uninstalling selected components...
✓ nWave CLI removed
✓ DES components removed
✓ SubagentStop hook removed
⚠ Agent definitions KEPT (as requested)
⚠ Templates KEPT (as requested)

Partial uninstallation complete!

Agents and templates remain available for other tools.
To remove agents/templates: nwave uninstall --agents-only
```

#### Acceptance Criteria

- [ ] AC-002.1: Single command (`nwave uninstall`) removes all nWave components
- [ ] AC-002.2: Uninstallation creates backup before removing files (default: yes, can be skipped with --no-backup)
- [ ] AC-002.3: User data is preserved by default (docs/feature/, steps/, audit logs, config)
- [ ] AC-002.4: `--delete-data` flag removes ALL user data with explicit confirmation prompt
- [ ] AC-002.5: Uninstallation output shows what was removed and what was preserved
- [ ] AC-002.6: Backup location is reported with instructions for restoration
- [ ] AC-002.7: Restore capability (`nwave install --restore <date>`) works from any backup
- [ ] AC-002.8: Partial uninstallation supported (--keep-agents, --keep-templates, --keep-hooks)
- [ ] AC-002.9: Uninstallation validates no active executions (warns if IN_PROGRESS steps detected)
- [ ] AC-002.10: Uninstallation log created with detailed trace
- [ ] AC-002.11: Virtual environment completely removed (~/.claude/nwave/venv/ deleted)
- [ ] AC-002.12: Post-uninstallation verification confirms no nWave packages in global Python environment
- [ ] AC-002.13: Uninstallation output explicitly confirms global Python environment is unchanged

#### Technical Notes

- **Safety**: Backup is MANDATORY unless explicitly disabled (--no-backup flag)
- **User data preservation**: Default behavior protects user work product
- **Restoration**: Backups are timestamped and indexed for easy restoration
- **Active execution detection**: Check for IN_PROGRESS steps before uninstalling
- **Partial removal**: Support granular uninstallation for advanced users

---

### US-INSTALL-003: Installation Verification & Health Check

**As** Alex (Junior Developer),
**I want** to verify my nWave installation is working correctly,
**So that** I'm confident everything is set up before starting my first workflow.

**Story Points:** 2
**Priority:** P1 (Should Have - Critical for learning experience)

#### Problem (The Pain)

Alex just ran `nwave install` and it said "Installation complete!" but he's not sure if everything actually works. He doesn't know:
- If the CLI is accessible from his terminal
- If agents can actually be invoked from Claude
- If DES validation will work when he runs `/nw:execute`
- If hooks are properly configured

When he tried another tool, installation claimed success but commands failed with cryptic errors. He spent hours debugging before realizing the installation was incomplete. He wants confidence BEFORE starting real work.

#### Who (The User)

- Junior developer unfamiliar with nWave
- Needs verification that installation was successful
- Wants clear pass/fail status for each component
- Benefits from learning what each component does

#### Solution (What We Build)

Health check command that:
1. Tests each component individually (CLI, DES, agents, hooks, templates)
2. Provides pass/fail status with explanations
3. Suggests fixes for failures
4. Runs automatically post-installation (can also be run manually)

#### Domain Examples

**Example 1: Healthy Installation**
```bash
$ nwave health-check
nWave Health Check v1.0.0
=========================

Running diagnostics...

[1/6] Virtual Environment
  ✓ Virtual environment exists: ~/.claude/nwave/venv/
  ✓ Python version in venv: 3.11.5 (matches system Python)
  ✓ venv activation works: source ~/.claude/nwave/venv/bin/activate
  ✓ nWave packages in venv: nwave==1.0.0
  ✓ No nWave packages in global Python environment (isolation verified)

[2/6] CLI Accessibility
  ✓ nwave command found in PATH
  ✓ Version: 1.0.0
  ✓ All subcommands accessible (install, uninstall, execute, validate, audit)
  ✓ CLI automatically uses venv (no manual activation needed)

[3/6] DES Validation Library
  ✓ DES module importable from venv: import nwave.des
  ✓ Validation functions available: 8/8 validators
  ✓ Data models compatible: StepFile v1.4, TaskState v1.2
  ✓ Hook integration ready: SubagentStop callable

[4/6] Agent Definitions
  ✓ Agent directory found: ~/.claude/agents/nw/
  ✓ Agents registered: 12/12
    - researcher, solution-architect, product-owner, acceptance-designer,
      software-crafter, devop, reviewer, documenter, analyst, designer,
      coordinator, facilitator
  ✓ Agent files readable and valid YAML

[5/6] SubagentStop Hook
  ✓ Hook file exists: ~/.claude/hooks/subagent-stop.py
  ✓ Hook is executable (permissions: 0755)
  ✓ Hook can be imported by Claude Code
  ✓ DES validation reachable from hook

[6/6] Templates
  ✓ Template directory found: ~/.claude/templates/nw/
  ✓ Templates available: 15/15
  ✓ Template syntax valid (YAML parsing successful)

Overall Status: ✓ HEALTHY

All components operational. nWave is ready to use!

Virtual Environment Status:
  Location: ~/.claude/nwave/venv/
  Python: 3.11.5
  Packages: nwave==1.0.0 (isolated from global environment)
  Global environment: Clean (no nWave packages)

Next steps:
  - Try: /nw:execute @researcher "analyze user authentication patterns"
  - Read: ~/.claude/nwave/docs/quickstart.md
  - Examples: ~/.claude/nwave/examples/
```

**Example 2: Partial Failure - Hook Not Executable**
```bash
$ nwave health-check
nWave Health Check v1.0.0
=========================

Running diagnostics...

[1/5] CLI Accessibility
  ✓ PASS

[2/5] DES Validation Library
  ✓ PASS

[3/5] Agent Definitions
  ✓ PASS

[4/5] SubagentStop Hook
  ✓ Hook file exists: ~/.claude/hooks/subagent-stop.py
  ✗ Hook is NOT executable (permissions: 0644, expected: 0755)
  ⚠ This will prevent DES validation from running!

[5/5] Templates
  ✓ PASS

Overall Status: ✗ UNHEALTHY (1 component failed)

Failures:
  - SubagentStop Hook: Not executable

Recovery suggestions:
  1. Fix permissions: chmod +x ~/.claude/hooks/subagent-stop.py
  2. Re-run health check: nwave health-check

If issue persists:
  - Reinstall: nwave install --force
  - Get support: https://nwave.dev/support

Health check log: ~/.claude/nwave/health-check-2026-01-23.log
```

**Example 3: Missing Component - Agents Not Installed**
```bash
$ nwave health-check
nWave Health Check v1.0.0
=========================

Running diagnostics...

[1/5] CLI Accessibility
  ✓ PASS

[2/5] DES Validation Library
  ✓ PASS

[3/5] Agent Definitions
  ✗ Agent directory NOT found: ~/.claude/agents/nw/
  ✗ Expected 12 agents, found 0
  ⚠ This will prevent /nw:* commands from working!

[4/5] SubagentStop Hook
  ✓ PASS

[5/5] Templates
  ✓ PASS

Overall Status: ✗ UNHEALTHY (1 component failed)

Failures:
  - Agent Definitions: Directory missing

Diagnosis:
  This usually indicates incomplete installation or manual file deletion.

Recovery suggestions:
  1. Reinstall agents: nwave install --agents-only
  2. Or full reinstall: nwave install --force

If using custom agent directory:
  - Set: export NWAVE_AGENT_DIR=/path/to/agents
  - Re-run: nwave health-check

Health check log: ~/.claude/nwave/health-check-2026-01-23.log
```

**Example 4: Educational Mode - Explain Each Component**
```bash
$ nwave health-check --explain
nWave Health Check v1.0.0 (Educational Mode)
=============================================

[1/5] CLI Accessibility
  What: Command-line interface for nWave operations
  Why: Allows installation, validation, and workflow management
  Test: Checks if 'nwave' command is in PATH and executable
  ✓ PASS

[2/5] DES Validation Library
  What: Deterministic Execution System validation logic
  Why: Ensures TDD phases are executed correctly and completely
  Test: Verifies Python module can be imported and validators work
  ✓ PASS

[3/5] Agent Definitions
  What: Claude Code agent configuration files (YAML)
  Why: Defines agent personas, commands, and dependencies
  Test: Checks ~/.claude/agents/nw/ for 12 agent definition files
  ✓ PASS

[4/5] SubagentStop Hook
  What: Hook that runs after every sub-agent task completion
  Why: Validates step file state and prevents abandoned work
  Test: Verifies hook file exists, is executable, and imports correctly
  ✓ PASS

[5/5] Templates
  What: Reusable templates for requirements, design, acceptance tests
  Why: Provides starting point for methodology compliance
  Test: Checks template directory and validates YAML syntax
  ✓ PASS

Overall Status: ✓ HEALTHY

You now understand what each component does and why it's needed!
```

#### Acceptance Criteria

- [ ] AC-003.1: Health check tests all 6 components (venv, CLI, DES, agents, hooks, templates)
- [ ] AC-003.2: Each component test shows pass/fail status with clear explanation
- [ ] AC-003.3: Overall status is HEALTHY only if all components pass
- [ ] AC-003.4: Failures provide specific recovery suggestions (commands to run)
- [ ] AC-003.5: Health check runs automatically after installation (can be skipped with --no-health-check)
- [ ] AC-003.6: Manual health check command available: `nwave health-check`
- [ ] AC-003.7: Educational mode (`--explain`) describes what each component does and why
- [ ] AC-003.8: Health check log created with detailed diagnostics for troubleshooting
- [ ] AC-003.9: Health check completes in < 5 seconds
- [ ] AC-003.10: Exit code 0 for healthy, non-zero for unhealthy (supports CI integration)
- [ ] AC-003.11: Virtual environment health validation includes existence check, Python version match, and package isolation verification
- [ ] AC-003.12: Health check explicitly confirms no nWave packages in global Python environment
- [ ] AC-003.13: Virtual environment diagnostics show location, Python version, and installed packages

#### Technical Notes

- **Test strategy**: Non-destructive read-only tests (no side effects)
- **Component tests**: File existence, permissions, syntax validation, import tests
- **Educational value**: Helps users understand nWave architecture
- **CI integration**: Exit codes allow automated verification in pipelines

---

### US-INSTALL-004: Installation Upgrade & Migration

**As** Marcus (Senior Developer),
**I want** to upgrade nWave to latest version with automatic migration,
**So that** I get new features without losing my existing work.

**Story Points:** 5
**Priority:** P1 (Should Have - Critical for production adoption)

#### Problem (The Pain)

Marcus has been using nWave v0.9 for 3 months. His project has:
- 8 features with full documentation (docs/feature/)
- 45 step files with execution history
- 3 months of audit logs
- Custom configuration in config.yaml

He wants to upgrade to v1.0 for new features (installation workflows, improved DES validation) but he's afraid:
- Upgrade will break existing step files (format incompatibility)
- Configuration changes will lose his custom settings
- Audit logs will be inaccessible in new version
- Rollback will be complicated if upgrade fails

When he upgraded a different tool last year, the migration corrupted his data and he lost 2 weeks of work. He wants confidence that upgrade is safe.

#### Who (The User)

- Senior developer with production nWave usage
- Has significant investment in existing nWave data
- Needs backward compatibility and safe migration
- Values rollback capability as safety net

#### Solution (What We Build)

Upgrade workflow that:
1. Detects version differences and required migrations
2. Creates comprehensive backup before upgrade
3. Migrates data formats automatically (step files, config, audit logs)
4. Validates migrated data for integrity
5. Provides rollback mechanism if upgrade fails
6. Reports migration changes and compatibility status

#### Domain Examples

**Example 1: Smooth Upgrade with Data Migration**
```bash
$ nwave --version
nWave CLI v0.9.2

$ pip install --upgrade nwave
Successfully installed nwave-1.0.0

$ nwave install --upgrade
nWave Upgrade v0.9.2 → v1.0.0
==============================

Detecting existing installation...
✓ nWave v0.9.2 found at: ~/.claude/nwave/
✓ Virtual environment detected: ~/.claude/nwave/venv/ (Python 3.11.5)
✓ User data detected:
  - Features: 8 (237 files)
  - Step files: 45 (12 IN_PROGRESS, 30 DONE, 3 FAILED)
  - Audit logs: 90 days (125 MB)
  - Configuration: config.yaml (3 custom settings)

Analyzing migration requirements...
✓ Virtual environment: Preserved (Python 3.11.5 remains unchanged)
  - Strategy: Upgrade packages in existing venv (no venv recreation)

✓ Step file schema: v1.3 → v1.4 (migration required)
  - Changes: Added 'educational_notes' field to phases
  - Impact: 45 files will be updated
  - Backward compatibility: v0.9 can read v1.4 files

✓ Configuration: v1.0 → v1.1 (migration required)
  - Changes: New setting 'stale_threshold_minutes' (default: 30)
  - Impact: config.yaml will be updated
  - Custom settings preserved: 3/3

✓ Audit logs: v1.0 → v1.0 (no migration needed)
  - Format unchanged
  - Logs remain readable

Creating backup...
✓ Backup created: ~/.claude/nwave.backup-2026-01-23-pre-upgrade/
  (Size: 140 MB, includes all components + data + venv state)
✓ Backup verified: All files readable

Upgrading components...
✓ Virtual environment preserved (no recreation)
✓ nWave packages upgraded in venv (v0.9.2 → v1.0.0)
✓ DES library upgraded in venv (v1.3 → v1.4)
✓ SubagentStop hook upgraded (v1.0 → v2.0)
✓ Agents upgraded (12 updated, 3 new agents added)
✓ Templates refreshed (15 updated, 5 new templates added)

Migrating user data...
✓ Step files migrated: 45/45 successful
  - Schema v1.3 → v1.4
  - Educational notes initialized (empty for existing phases)
  - Validation: All files parse correctly in new format

✓ Configuration migrated: config.yaml
  - New setting added: stale_threshold_minutes = 30
  - Custom settings preserved:
    * audit_retention_days: 90 (custom, default was 30)
    * max_turn_budget: 60 (custom, default was 50)
    * enable_learning_mode: true (custom, default was false)

✓ Audit logs validated: 90 days readable in v1.0

Running post-upgrade health check...
✓ Virtual environment operational (Python 3.11.5)
✓ All components operational
✓ Migrated data integrity verified
✓ Backward compatibility confirmed (can rollback safely)
✓ Global Python environment still clean (no packages installed)

Upgrade complete!

Summary of changes:
  - 3 new agents: installation-coordinator, migration-validator, health-checker
  - 5 new templates: installation.yaml, upgrade.yaml, health-check.yaml, etc.
  - New features: Installation workflows (US-INSTALL-001 through 004)
  - Breaking changes: None
  - Deprecated features: None

Virtual Environment Status:
  Location: ~/.claude/nwave/venv/ (preserved)
  Python: 3.11.5 (unchanged)
  Packages: nwave==1.0.0 (upgraded from 0.9.2)

Migration notes: ~/.claude/nwave/MIGRATION-0.9-to-1.0.md
Rollback: nwave install --rollback 2026-01-23-pre-upgrade
Changelog: ~/.claude/nwave/CHANGELOG.md

Next steps:
  - Review migration notes for new features
  - Try new installation commands: nwave health-check
  - Continue using nWave as before (all existing workflows compatible)
```

**Example 2: Upgrade Failure with Automatic Rollback**
```bash
$ nwave install --upgrade
nWave Upgrade v0.9.2 → v1.0.0
==============================

[... backup created ...]
[... components upgraded ...]

Migrating user data...
✓ Step files: 40/45 migrated
✗ Step files: 5/45 FAILED (step-03-02.json: invalid JSON syntax)

⚠ Migration error detected!

Error details:
  File: docs/feature/auth-upgrade/steps/03-02.json
  Error: JSONDecodeError at line 47: Expecting ',' delimiter
  Cause: File corrupted (likely manual edit)

Performing automatic rollback...
✓ Rolling back to v0.9.2 from backup
✓ Virtual environment restored (Python 3.11.5, nwave==0.9.2)
✓ All components restored
✓ User data restored (no changes applied)
✓ System state: Identical to pre-upgrade

Upgrade FAILED and rolled back automatically.

Recovery suggestions:
  1. Fix corrupted file: docs/feature/auth-upgrade/steps/03-02.json
     (Use 'nwave validate-step' to check syntax)
  2. Re-run upgrade: nwave install --upgrade

If corruption is severe:
  - Restore from older backup: nwave install --restore <date>
  - Remove corrupted feature: mv docs/feature/auth-upgrade ~/backup/

Error log: ~/.claude/nwave/upgrade-error-2026-01-23.log
```

**Example 5: Virtual Environment Corruption During Upgrade**
```bash
$ nwave install --upgrade
nWave Upgrade v0.9.2 → v1.0.0
==============================

Detecting existing installation...
✓ nWave v0.9.2 found
✓ Virtual environment detected: ~/.claude/nwave/venv/
⚠ Virtual environment health check...
✗ ERROR: Virtual environment is corrupted

Diagnosis:
  - venv Python executable missing or broken
  - Possible causes:
    * External modification of venv directory
    * Python version removed from system
    * Disk corruption or filesystem issues
  - Impact: Cannot upgrade in-place

Recovery options:

Option 1: Recreate virtual environment (RECOMMENDED)
  $ nwave install --upgrade --recreate-venv
  - Creates fresh venv with Python 3.11.5
  - Preserves all user data
  - Migrates step files and configuration

Option 2: Manual venv recreation
  $ rm -rf ~/.claude/nwave/venv/
  $ nwave install --upgrade
  - Same result as option 1

Option 3: Complete reinstallation
  $ nwave uninstall --no-backup
  $ nwave install
  - Fresh installation (loses custom config unless backed up manually)

Backup created at: ~/.claude/nwave.backup-2026-01-23/
User data is safe. Virtual environment will be recreated.

Proceeding with Option 1...

Creating fresh virtual environment...
✓ Old venv removed
✓ New venv created (Python 3.11.5)
✓ nWave packages installed in new venv

[... migration continues normally ...]

Upgrade complete with venv recreation!
```

**Example 3: Dry-Run Upgrade (Preview Changes)**
```bash
$ nwave install --upgrade --dry-run
nWave Upgrade Preview v0.9.2 → v1.0.0
=====================================

This is a DRY RUN - no changes will be made.

Analyzing upgrade impact...

Components to be upgraded:
  - CLI: v0.9.2 → v1.0.0
  - DES: v1.3 → v1.4
  - SubagentStop: v1.0 → v2.0
  - Agents: 12 updated, 3 new
  - Templates: 15 updated, 5 new

Data migrations required:
  ✓ Step files: 45 files (v1.3 → v1.4 schema)
    - Changes: Add 'educational_notes' field
    - Estimated time: ~10 seconds
    - Risk: Low (backward compatible)

  ✓ Configuration: config.yaml (v1.0 → v1.1)
    - Changes: Add 'stale_threshold_minutes' setting
    - Custom settings: 3 preserved
    - Risk: Low (non-destructive)

  ✓ Audit logs: No migration needed
    - Format unchanged
    - Risk: None

New features in v1.0.0:
  - Installation workflows (US-INSTALL-001 through 004)
  - Health check command (nwave health-check)
  - Upgrade/rollback capability (this feature!)
  - Educational mode for phase execution

Breaking changes:
  - None

Deprecated features:
  - None (all v0.9 features remain available)

Estimated upgrade time: ~2 minutes
Disk space required: ~150 MB (backup)
Rollback capability: Yes (automatic on failure)

Dry run complete. No changes were made.

To proceed with upgrade: nwave install --upgrade
To view detailed changelog: cat ~/.claude/nwave/CHANGELOG.md
```

**Example 4: Rollback After Upgrade**
```bash
$ nwave install --rollback 2026-01-23-pre-upgrade
nWave Rollback to v0.9.2
========================

Detecting backup...
✓ Backup found: ~/.claude/nwave.backup-2026-01-23-pre-upgrade/
  (Created: 2026-01-23 09:15:30, Size: 140 MB)
  (Original version: v0.9.2)

⚠ This will REPLACE current installation (v1.0.0) with backup (v0.9.2)

Current state will be lost:
  - Any work done after upgrade
  - New step files created in v1.0.0
  - Configuration changes made post-upgrade

Create snapshot of current state before rollback? [Y/n]: Y

Creating pre-rollback snapshot...
✓ Snapshot: ~/.claude/nwave.snapshot-2026-01-23-pre-rollback/

Rolling back to v0.9.2...
✓ nWave components restored from backup
✓ User data restored (state at time of backup)
✓ Configuration restored

Running health check...
✓ All components operational (v0.9.2)

Rollback complete!

System restored to: 2026-01-23 09:15:30 (pre-upgrade state)
Current version: v0.9.2
Snapshot of v1.0.0 state: ~/.claude/nwave.snapshot-2026-01-23-pre-rollback/

If you want to retry upgrade: nwave install --upgrade
```

#### Acceptance Criteria

- [ ] AC-004.1: Upgrade detects version differences and lists required migrations
- [ ] AC-004.2: Backup is MANDATORY before upgrade (cannot be skipped)
- [ ] AC-004.3: Data migration is automatic for step files, configuration, and audit logs
- [ ] AC-004.4: Custom configuration settings are preserved during migration
- [ ] AC-004.5: Migration validates data integrity post-migration (all files parseable)
- [ ] AC-004.6: Automatic rollback occurs if migration fails (no partial state)
- [ ] AC-004.7: Dry-run mode (`--dry-run`) previews changes without applying them
- [ ] AC-004.8: Manual rollback command available: `nwave install --rollback <backup-id>`
- [ ] AC-004.9: Migration notes document breaking changes and new features
- [ ] AC-004.10: Post-upgrade health check verifies all components operational
- [ ] AC-004.11: Backward compatibility preserved (v0.9 can read v1.0 step files)
- [ ] AC-004.12: Virtual environment is preserved during upgrade (not recreated) to maintain Python version consistency
- [ ] AC-004.13: Only nWave packages are upgraded in existing venv (Python interpreter remains unchanged)
- [ ] AC-004.14: Virtual environment corruption detection triggers automatic recreation with user data preservation
- [ ] AC-004.15: Rollback restores virtual environment to pre-upgrade state (packages downgraded to original versions)

#### Technical Notes

- **Migration strategy**: Schema versioning with automated migration scripts
- **Backward compatibility**: New versions can read old formats (forward compatibility not guaranteed)
- **Rollback safety**: Automatic rollback on ANY migration failure
- **Dry-run capability**: Preview upgrade impact without commitment
- **Snapshot preservation**: Current state saved before rollback for recovery

---

## Installation Failure Scenarios

### Scenario Matrix

| Failure Type | Detection Method | Error Message | Recovery Suggestion |
|--------------|------------------|---------------|---------------------|
| **Claude Code Not Found** | Check for ~/.claude/ directory | "Claude Code environment not detected. nWave requires Claude Code." | Install Claude Code first OR use --ci flag for CI environments |
| **Python Version Incompatible** | Check `sys.version_info` | "Python 3.11+ required. Found: 3.9.7" | Upgrade Python: pyenv install 3.11 |
| **venv Module Missing** | Import venv module | "Cannot create virtual environment (venv module unavailable)" | Ubuntu/Debian: sudo apt install python3-venv; macOS/Windows: Reinstall Python |
| **Permission Denied** | Check write access to ~/.claude/ | "Permission denied writing to ~/.claude/hooks/" | Fix ownership: sudo chown -R $USER ~/.claude/ |
| **Disk Space Insufficient** | Check available space vs. required | "Insufficient disk space. Required: 50MB, Available: 20MB" | Free up disk space or install to different location |
| **Corrupted Download** | Verify package checksum | "Package integrity check failed (checksum mismatch)" | Clear pip cache: pip cache purge, then reinstall |
| **Conflicting Hook Exists** | Check if ~/.claude/hooks/subagent-stop.py exists from other source | "Existing SubagentStop hook detected (non-nWave source)" | Backup existing hook, then retry with --force |
| **Git Not Found** (optional) | Check if `git` command available | "Git not detected (optional for basic usage)" | Install Git OR ignore warning (reduces functionality) |
| **Network Timeout** | Timeout during pip install | "Network timeout downloading nwave package" | Check internet connection, retry, or use offline install |

### Safety Guarantees

1. **Atomic Installation**: All components installed successfully OR nothing installed (rollback on failure)
2. **No Data Loss**: User data never deleted during installation (only during explicit uninstall --delete-data)
3. **Backup Before Modification**: Upgrade and uninstall always create backups first
4. **Validation Before Commitment**: Health checks run before declaring success
5. **Clear Error Messages**: Every failure includes diagnosis and recovery steps

---

## Integration with Existing DES Stories

### Dependency Relationships

```
US-INSTALL-001 (Installation) ──┐
                                ├──► US-001 (Command Filtering)
US-INSTALL-003 (Health Check) ──┘      │
        │                               ▼
        │                         US-002 (Pre-Invocation)
        │                               │
        ▼                               ▼
US-INSTALL-004 (Upgrade) ────────► US-003 (Post-Execution)
                                        │
                                        ▼
                                   [All other DES stories]
```

**Prerequisites**:
- All DES execution stories (US-001 through US-009, US-INF-001 through US-INF-003) **require** successful installation (US-INSTALL-001)
- Health check (US-INSTALL-003) validates DES components are operational
- Upgrade (US-INSTALL-004) ensures DES data compatibility across versions

**Installation First Principle**:
> "No nWave command can execute without successful installation verification."

---

## Implementation Priority

### Sprint 0: Installation Foundation (P0 - Blockers)
- US-INSTALL-001: One-Command Installation
- US-INSTALL-003: Health Check

### Sprint 1: DES Foundation (P0)
- US-001: Command-Origin Task Filtering
- US-002: Pre-Invocation Template Validation
- US-006: Turn Discipline

### Sprint 2: DES Validation (P0)
- US-003: Post-Execution State Validation
- US-004: Audit Trail

### Sprint 3: Lifecycle Management (P1)
- US-INSTALL-002: Uninstallation
- US-INSTALL-004: Upgrade & Migration
- US-005: Failure Recovery Guidance
- US-007: Boundary Rules

---

## Success Metrics

### Installation Success Metrics
- **Installation success rate**: > 95% (measured via telemetry opt-in)
- **Time to first workflow**: < 5 minutes from installation to first `/nw:execute`
- **Health check pass rate**: > 98% post-installation
- **Upgrade success rate**: > 99% (automatic rollback prevents data loss)

### User Experience Metrics
- **Marcus (Senior Dev)**: Installation takes < 2 minutes, no manual configuration
- **Priya (Tech Lead)**: Team onboarding takes < 15 minutes per developer
- **Alex (Junior Dev)**: Understands what was installed and why (educational mode)

### Safety Metrics
- **Zero data loss incidents**: No user data lost during installation/upgrade/uninstall
- **Rollback success rate**: 100% (backup mechanism always works)
- **Recovery time**: < 5 minutes from failure to working state

---

*Installation user stories created by Riley (product-owner) during DISCUSS wave integration.*
*Integration with DES feature set (docs/feature/des/discuss/user-stories.md)*
