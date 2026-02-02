# Modern CLI Installer - User Stories

**Epic**: modern_CLI_installer
**Product Owner**: Riley
**Created**: 2026-02-01
**Status**: DISCUSS Wave - Requirements Specification

---

## Epic Summary

The modern_CLI_installer epic delivers a complete developer experience for building, testing, and distributing the nWave framework. It consists of three interconnected journeys:

1. **forge:build-local-candidate** - Build pipx-compatible wheel with semantic versioning
2. **forge:install-local-candidate** - Install and validate local wheel before release
3. **install-nwave** - First-time PyPI installation for end users

The journeys share common infrastructure (pre-flight checks, doctor verification, shared artifacts) and follow a progressive trust-building emotional arc.

---

## Dependency Diagram

```
+------------------------+     +-----------------------------+
|   INFRASTRUCTURE       |     |                             |
|   (US-001 to US-005)   |     |                             |
+------------------------+     |                             |
           |                   |                             |
           v                   |                             |
+------------------------+     |    +--------------------+   |
|  JOURNEY 1: BUILD      |     |    |  JOURNEY 3: PYPI   |   |
|  forge:build-local     |     |    |  install-nwave     |   |
|  (US-010 to US-019)    |     |    |  (US-030 to US-039)|   |
+------------------------+     |    +--------------------+   |
           |                   |             ^               |
           v                   |             |               |
+------------------------+     |     (shares doctor,         |
|  JOURNEY 2: INSTALL    |-----+      pre-flight checks)     |
|  forge:install-local   |                                   |
|  (US-020 to US-029)    |                                   |
+------------------------+                                   |
           |                                                 |
           +------ (shared patterns) -----------------------+
                              |
                              v
               +-----------------------------+
               |  CROSS-CUTTING STORIES      |
               |  US-040: Rollback           |
               |  US-041: Upgrade Detection  |
               |  (applies to all journeys)  |
               +-----------------------------+
```

**Execution Order**:
1. Infrastructure stories (US-001 to US-005) - MUST be first
2. Journey 1 (BUILD) stories (US-010 to US-019) - MUST follow infrastructure
3. Journey 2 (INSTALL) stories (US-020 to US-029) - MUST follow Journey 1
4. Journey 3 (PYPI) stories (US-030 to US-039) - Can run in parallel with Journey 2 after infrastructure
5. Cross-Cutting stories (US-040 to US-041) - Apply across all journeys, implement after US-039

---

## Story List with Priorities

### Infrastructure Stories (Foundation)

| ID | Story | Priority | Dependencies |
|----|-------|----------|--------------|
| US-001 | Shared Pre-flight Check Framework | P0 | None |
| US-002 | Shared Doctor Health Check Framework | P0 | None |
| US-003 | Shared Artifacts Registry | P0 | None |
| US-004 | Installer Configuration System | P0 | US-001 |
| US-005 | URL Configuration Management | P1 | None |

### Journey 1: forge:build-local-candidate

| ID | Story | Priority | Dependencies |
|----|-------|----------|--------------|
| US-010 | Build Pre-flight Validation | P0 | US-001 |
| US-011 | Conventional Commits Version Bumping | P0 | US-010 |
| US-012 | Wheel Build Process | P0 | US-011 |
| US-013 | Wheel Content Validation | P0 | US-012 |
| US-014 | Build Success Summary | P0 | US-013 |
| US-015 | Local Install Prompt | P1 | US-014 |
| US-016 | Force Version Override | P1 | US-011 |
| US-017 | Daily Build Sequence Tracking | P1 | US-011 |
| US-018 | CI Mode Build Support | P1 | US-010 |
| US-019 | Auto-repair Missing Build Dependencies | P1 | US-010 |

### Journey 2: forge:install-local-candidate

| ID | Story | Priority | Dependencies |
|----|-------|----------|--------------|
| US-020 | Install Pre-flight Validation | P0 | US-001, US-014 |
| US-021 | Release Readiness Validation | P0 | US-020 |
| US-022 | Candidate Installation via pipx | P0 | US-021 |
| US-023 | Post-Install Doctor Verification | P0 | US-002, US-022 |
| US-024 | Release Report Generation | P0 | US-023 |
| US-025 | Auto-chain to Build on Missing Wheel | P1 | US-020 |
| US-026 | Multiple Wheel Selection | P1 | US-020 |
| US-027 | CI Mode Install Support | P1 | US-020 |
| US-028 | JSON Output for CI/CD | P1 | US-024 |
| US-029 | Strict Mode for Release Validation | P2 | US-021 |

### Journey 3: install-nwave (PyPI)

| ID | Story | Priority | Dependencies |
|----|-------|----------|--------------|
| US-030 | PyPI Download and Dependencies | P0 | US-001 |
| US-031 | Install Path Resolution | P0 | US-004 |
| US-032 | Framework Installation with Progress | P0 | US-031 |
| US-033 | Doctor Verification for PyPI Install | P0 | US-002 |
| US-034 | Welcome and Celebration Display | P0 | US-033 |
| US-035 | Restart Claude Code Notification | P0 | US-034 |
| US-036 | Verification in Claude Code | P0 | US-035 |
| US-037 | Custom Install Path via Environment | P1 | US-031 |
| US-038 | CI Mode for PyPI Install | P1 | US-030 |
| US-039 | Backup Creation Before Install | P1 | US-032 |

### Cross-Cutting Stories

| ID | Story | Priority | Dependencies |
|----|-------|----------|--------------|
| US-040 | Rollback on Installation Failure | P0 | US-039, US-002 |
| US-041 | Upgrade Detection and Handling | P0 | US-039, US-004, US-001 |

---

## Story Details

---

## Infrastructure Stories

### US-001: Shared Pre-flight Check Framework

**As a** developer running any nWave CLI command
**I want** consistent pre-flight validation across all journeys
**So that** I get a unified experience and actionable error messages

#### Problem Statement
Marco runs forge:build-local-candidate and sees pre-flight checks. Later he runs install-nwave and sees different check formats. This inconsistency confuses users and duplicates code.

#### Domain Examples

**Example 1: Python version check passes**
Marco has Python 3.12.1 installed. When he runs any nWave command, the pre-flight shows "Python version [check] 3.12.1 (3.10+ OK)" in the same format regardless of which journey he's running.

**Example 2: pipx missing with auto-repair**
Maria doesn't have pipx installed. When she runs install-nwave, the pre-flight check fails with "pipx not found" and offers "Install it now? [Y/n]". She types Y and pipx is installed automatically.

**Example 3: Permission denied blocking**
Alex runs install-nwave but ~/.claude is not writable. The check shows "[x] Cannot write to ~/.claude/" with clear instructions: "Check permissions or create manually: mkdir -p ~/.claude/ && chmod u+w ~/.claude/"

#### UAT Scenarios

```gherkin
Scenario: Pre-flight displays consistent format across journeys
  Given Marco has Python 3.12.1 installed
  When Marco runs "forge:build-local-candidate"
  Then the Python version check shows "Python version [check] 3.12.1 (3.10+ OK)"
  And when Marco runs "install-nwave"
  Then the Python version check shows the same format

Scenario: Fixable issue offers auto-repair
  Given Maria does not have pipx installed
  When Maria runs "install-nwave"
  Then the pre-flight check fails for "pipx available"
  And the prompt asks "Install it now? [Y/n]"
  And Maria types "Y"
  Then pipx is installed via "pip install pipx && pipx ensurepath"
  And pre-flight checks resume

Scenario: Blocking issue provides actionable error
  Given Alex cannot write to ~/.claude/
  When Alex runs "install-nwave"
  Then the pre-flight check fails for "Write permissions"
  And the error shows "Cannot write to ~/.claude/"
  And the fix suggestion shows "mkdir -p ~/.claude/ && chmod u+w ~/.claude/"
  And the installation aborts
```

#### Acceptance Criteria
- [ ] Core checks (python_version, pipx_available, claude_dir_writable) available to all journeys
- [ ] Build-specific checks (build_package, pyproject_toml, source_directory, dist_directory) available to build journey
- [ ] Install-specific checks (wheel_exists, pipx_isolation, install_path_resolved) available to install journeys
- [ ] Fixable issues prompt for auto-repair with clear Y/n prompt
- [ ] Blocking issues provide actionable error messages with recovery steps
- [ ] Check results displayed in consistent table format across all journeys

#### Technical Notes
- Schema defined in: `docs/ux/modern-cli-installer/shared/pre-flight-checks.yaml`
- Error handling follows layered approach: pre-flight -> interactive_repair -> clear_failure

---

### US-002: Shared Doctor Health Check Framework

**As a** developer who just installed nWave
**I want** consistent health verification across all install methods
**So that** I know my installation is healthy regardless of how I installed

#### Problem Statement
Elena installs nWave from PyPI and sees doctor output. Later she installs a local candidate and the doctor output is different. This inconsistency makes it hard to compare health between install methods.

#### Domain Examples

**Example 1: Healthy installation**
Elena runs `nw doctor` after PyPI install. She sees a table showing Core, Agents (47), Commands (23), Templates (12), Config (Valid), Permissions (OK), Version (2.1.0). Status shows "HEALTHY" with green indicator.

**Example 2: Degraded installation**
Roberto installed nWave but template files are missing. Doctor shows Agents (47 OK), Commands (23 OK), Templates (0 MISSING - warning). Status shows "DEGRADED" with yellow indicator.

**Example 3: Unhealthy installation**
Carla's install failed midway. Doctor shows Agents (0 FAIL), Commands (0 FAIL). Status shows "UNHEALTHY" with red indicator and suggests "nw install --repair".

#### UAT Scenarios

```gherkin
Scenario: Doctor shows healthy status
  Given Elena has a complete nWave installation
  When Elena runs "nw doctor"
  Then the doctor table displays all components
  And "Agents" shows "${agent_count} OK"
  And "Commands" shows "${command_count} OK"
  And "Templates" shows "${template_count} OK"
  And "Config" shows "Valid"
  And "Permissions" shows "OK"
  And the status shows "HEALTHY"

Scenario: Doctor shows degraded status for warnings
  Given Roberto has nWave installed but templates are missing
  When Roberto runs "nw doctor"
  Then "Templates" shows "0 MISSING"
  And the severity is "warning"
  And the status shows "DEGRADED"
  And Roberto can still use core functionality

Scenario: Doctor shows unhealthy status for critical failures
  Given Carla has a broken nWave installation
  When Carla runs "nw doctor"
  Then "Agents" shows failure status
  And the severity is "critical"
  And the status shows "UNHEALTHY"
  And repair instructions are provided
```

#### Acceptance Criteria
- [ ] Doctor checks: core_installation, agent_files, command_files, template_files, config_valid, permissions, version_match
- [ ] Health status levels: HEALTHY (all critical pass), DEGRADED (warnings only), UNHEALTHY (critical fails)
- [ ] Consistent table format across forge:install-local-candidate and install-nwave
- [ ] Agent/command/template counts validate against expected values from build
- [ ] Version match validates installed version against expected version
- [ ] JSON output format available for CI/CD integration

#### Technical Notes
- Schema defined in: `docs/ux/modern-cli-installer/shared/doctor-health-check.yaml`
- Triggered automatically after pipx install
- Manually available via `/nw:doctor` command

---

### US-003: Shared Artifacts Registry

**As a** developer building and installing nWave
**I want** consistent artifact values across all journey steps
**So that** version/counts displayed at build time match install time

#### Problem Statement
Giuseppe builds a wheel showing "1.3.0-dev-20260201-1" and 47 agents. After install, doctor shows 45 agents. This mismatch breaks trust and indicates a bundling bug.

#### Domain Examples

**Example 1: Version consistency across build and install**
Giuseppe builds wheel version "1.3.0-dev-20260201-1". At build summary, install prompt, release readiness, and doctor verification - all show "1.3.0-dev-20260201-1".

**Example 2: Count consistency across steps**
Lucia's build shows 47 agents bundled. After install, doctor shows 47 agents. The /nw:version command also shows 47 agents.

**Example 3: Wheel path flows to install**
The build creates wheel at "dist/nwave-1.3.0.dev20260201.1-py3-none-any.whl". The install prompt uses this exact path. The install command uses this exact path.

#### UAT Scenarios

```gherkin
Scenario: Candidate version is consistent across journeys
  Given Giuseppe builds with forge:build-local-candidate
  And the candidate version is "1.3.0-dev-20260201-1"
  When the build completes successfully
  Then the version in Step 2 (version bump) is "1.3.0-dev-20260201-1"
  And the version in Step 5 (summary) is "1.3.0-dev-20260201-1"
  And when Giuseppe installs with forge:install-local-candidate
  Then the version in Step 2 (release readiness) is "1.3.0-dev-20260201-1"
  And the version in Step 4 (doctor) is "1.3.0-dev-20260201-1"

Scenario: Component counts are consistent
  Given the build bundles 47 agents, 23 commands, 12 templates
  When validation runs at Step 4 (build wheel validation)
  Then counts show 47, 23, 12
  And when doctor runs after install
  Then counts show 47, 23, 12
  And when user runs /nw:version
  Then counts show 47, 23, 12

Scenario: Wheel path flows correctly to install
  Given build creates "dist/nwave-1.3.0-dev-py3-none-any.whl"
  When the install prompt displays
  Then the command shows "pipx install dist/nwave-1.3.0-dev-py3-none-any.whl --force"
```

#### Acceptance Criteria
- [ ] candidate_version flows through: build steps 2-6, install steps 2-5
- [ ] wheel_path flows through: build step 5, install prompt step 6, install step 1
- [ ] agent_count/command_count/template_count match across build validation, install doctor, /nw:version
- [ ] install_path resolved once and used consistently across install and verify
- [ ] Handoff contracts define required artifacts between journeys
- [ ] Consistency validation rules detect mismatches

#### Technical Notes
- Schema defined in: `docs/ux/modern-cli-installer/shared/shared-artifacts.yaml`
- Handoff contracts: build_to_install, install_to_verify, cicd_to_pypi
- Integration risk ratings: HIGH for version/candidate_version, LOW for counts

---

### US-004: Installer Configuration System

**As a** developer with a custom Claude installation
**I want** to configure where nWave installs
**So that** I can use nWave with non-standard Claude setups

#### Problem Statement
Francesco has Claude installed at ~/custom-claude instead of ~/.claude. Without configuration, nWave installs to wrong location and doesn't work.

#### Domain Examples

**Example 1: Environment variable override**
Francesco sets NWAVE_INSTALL_PATH=~/custom-claude/agents/nw before running pipx install nwave. The install goes to ~/custom-claude/agents/nw and works correctly.

**Example 2: Config file setting**
Giulia edits installer.yaml to set paths.install_dir: ~/my-claude/agents/nw. Without setting env var, install uses this config path.

**Example 3: Default fallback**
Most users don't set anything. Install uses default ~/.claude/agents/nw/ which works with standard Claude.

#### UAT Scenarios

```gherkin
Scenario: Environment variable takes highest priority
  Given NWAVE_INSTALL_PATH is set to "~/env-path/"
  And config/installer.yaml has paths.install_dir = "~/config-path/"
  When the installer resolves the install path
  Then the install path is "~/env-path/"
  And the output shows "NWAVE_INSTALL_PATH=~/env-path/"

Scenario: Config file used when env var not set
  Given NWAVE_INSTALL_PATH is not set
  And config/installer.yaml has paths.install_dir = "~/custom-claude/"
  When the installer resolves the install path
  Then the install path is "~/custom-claude/"

Scenario: Default used as fallback
  Given NWAVE_INSTALL_PATH is not set
  And config/installer.yaml does not specify install_dir
  When the installer resolves the install path
  Then the install path is "~/.claude/agents/nw/"
  And the output shows "Using default: ~/.claude/agents/nw/"
```

#### Acceptance Criteria
- [ ] Resolution order: NWAVE_INSTALL_PATH env var (1) -> config file (2) -> default (3)
- [ ] Default install path: ~/.claude/agents/nw/
- [ ] Backup path configurable: ~/.claude/agents/nw.backup
- [ ] Pre-flight shows resolved path for transparency
- [ ] CI mode detection via CI, GITHUB_ACTIONS, GITLAB_CI, JENKINS_URL env vars
- [ ] Auto-doctor setting defaults to true
- [ ] Update checking configurable (prompt/auto/never)

#### Technical Notes
- Config file: `nWave/data/config/installer.yaml`
- Path expansion for ~ handled correctly
- CI mode disables interactive prompts

---

### US-005: URL Configuration Management

**As a** developer using nWave
**I want** all URLs centrally managed
**So that** documentation links don't break when URLs change

#### Problem Statement
Martina clicks the docs URL shown after install. It returns 404 because the URL changed but wasn't updated in the code.

#### Domain Examples

**Example 1: Docs URL in welcome message**
After install, the welcome message shows "Docs: https://nwave.dev/getting-started". This URL comes from urls.yaml and can be updated in one place.

**Example 2: Bug report URL**
When doctor shows unhealthy status, it suggests reporting at "https://github.com/undeadgrishnackh/crafter-ai/issues/new". This URL is centrally managed.

**Example 3: PyPI package URL**
The /nw:version command can show package URL "https://pypi.org/project/nwave" for reference.

#### UAT Scenarios

```gherkin
Scenario: Documentation URL displayed from config
  Given urls.yaml has docs.getting_started = "https://nwave.dev/getting-started"
  When the welcome message displays after install
  Then the docs URL shows "https://nwave.dev/getting-started"

Scenario: Bug report URL available for errors
  Given urls.yaml has support.bug_report = "https://github.com/undeadgrishnackh/crafter-ai/issues/new"
  When an error occurs and recovery suggests reporting
  Then the bug report URL is correct
```

#### Acceptance Criteria
- [ ] docs.base, docs.getting_started, docs.api, docs.troubleshooting configured
- [ ] repo.github, repo.issues, repo.releases configured
- [ ] package.pypi configured
- [ ] support.community, support.bug_report configured
- [ ] All display URLs read from urls.yaml, not hardcoded

#### Technical Notes
- Config file: `nWave/data/config/urls.yaml`

---

## Journey 1: forge:build-local-candidate

### US-010: Build Pre-flight Validation

**As a** developer running forge:build-local-candidate
**I want** environment validation before build starts
**So that** I catch problems early rather than mid-build

#### Problem Statement
Davide runs forge:build-local-candidate without the build package installed. The build starts, downloads dependencies, then fails at build step. This wastes time. Pre-flight should catch this upfront.

#### Domain Examples

**Example 1: All checks pass**
Davide has Python 3.12, build package v1.2.1, valid pyproject.toml, nWave/ directory, writable dist/. Pre-flight shows all green checkmarks and "All pre-flight checks passed!".

**Example 2: Missing build package with auto-repair**
Stefania runs forge:build-local-candidate without build package. Pre-flight shows "build package [x] missing" and prompts "Install it now? [Y/n]". She types Y, build is installed, pre-flight resumes.

**Example 3: Invalid pyproject.toml blocking**
Paolo's pyproject.toml has syntax error on line 42. Pre-flight shows "[x] pyproject.toml invalid - Error at line 42: unexpected token". Build aborts with clear fix instructions.

#### UAT Scenarios

```gherkin
Scenario: All pre-flight checks pass
  Given Davide has Python 3.12.1 installed
  And the build package v1.2.1 is installed
  And pyproject.toml is valid with version "1.2.0"
  And nWave/ source directory exists
  And dist/ directory is writable
  When Davide runs "forge:build-local-candidate"
  Then the pre-flight table shows all checkmarks
  And the message shows "All pre-flight checks passed!"

Scenario: Missing build package offers auto-repair
  Given Stefania does not have build package installed
  When Stefania runs "forge:build-local-candidate"
  Then the check "build package" shows failure
  And the prompt asks "Install it now? [Y/n]"
  When Stefania types "Y"
  Then "pip install build" runs
  And pre-flight resumes with build package installed

Scenario: Invalid pyproject.toml blocks build
  Given Paolo's pyproject.toml has syntax error at line 42
  When Paolo runs "forge:build-local-candidate"
  Then the check "pyproject.toml" shows failure
  And the error shows "Error at line 42: ${error_message}"
  And the build aborts
```

#### Acceptance Criteria
- [ ] Validates Python version 3.10+
- [ ] Validates build package installed (fixable with auto-install)
- [ ] Validates pyproject.toml exists and is valid TOML
- [ ] Validates nWave/ source directory exists
- [ ] Validates dist/ directory is writable (fixable with mkdir)
- [ ] Displays consistent table format with check/x/warn icons
- [ ] All checks run and results collected before proceeding

---

### US-011: Conventional Commits Version Bumping

**As a** developer with conventional commit history
**I want** automatic version bumping based on commit types
**So that** I don't manually decide version numbers

#### Problem Statement
Anna has commits: "feat: add new agent", "fix: typo in config". She manually decides "this is minor bump" and types 1.3.0. This is error-prone. Conventional commits should auto-calculate.

#### Domain Examples

**Example 1: Feature commits -> MINOR bump**
Anna's commits since last tag include "feat: add Luna agent". Pyproject shows 1.2.0. Version resolution shows bump type "MINOR" and new version "1.3.0". Candidate becomes "1.3.0-dev-20260201-1".

**Example 2: Breaking change -> MAJOR bump**
Marco has commit "feat!: redesign API". Version resolution shows bump type "MAJOR" and new version "2.0.0".

**Example 3: Fix only -> PATCH bump**
Lucia has only "fix: correct typo" commits. Version resolution shows bump type "PATCH" and new version "1.2.1".

#### UAT Scenarios

```gherkin
Scenario: Feature commits trigger MINOR bump
  Given pyproject.toml version is "1.2.0"
  And commits since last tag include "feat: add Luna agent"
  When version resolution runs
  Then bump type is "MINOR"
  And new version is "1.3.0"
  And candidate version is "1.3.0-dev-${date}-1"

Scenario: Breaking change triggers MAJOR bump
  Given pyproject.toml version is "1.2.0"
  And commits include "BREAKING CHANGE: redesign API"
  When version resolution runs
  Then bump type is "MAJOR"
  And new version is "2.0.0"

Scenario: Fix commits trigger PATCH bump
  Given pyproject.toml version is "1.2.0"
  And only "fix:" commits since last tag
  When version resolution runs
  Then bump type is "PATCH"
  And new version is "1.2.1"
```

#### Acceptance Criteria
- [ ] Analyzes git log since last tag for conventional commits
- [ ] Patterns: BREAKING CHANGE or ! -> MAJOR, ^feat -> MINOR, ^fix -> PATCH
- [ ] Displays current version, branch, last tag in table
- [ ] Shows bump type with explanation
- [ ] Generates candidate version: ${new_version}-dev-YYYYMMDD-sequence
- [ ] Warns if no commits since last tag

---

### US-012: Wheel Build Process

**As a** developer with pre-flight passed
**I want** to see build progress visually
**So that** I know the build is working and how long it takes

#### Problem Statement
Giovanni runs forge:build-local-candidate. The terminal sits there for 30 seconds with no output. He wonders if it's frozen. Progress phases would show activity.

#### Domain Examples

**Example 1: Build shows phased progress**
Giovanni sees: "Cleaning dist/ [check] Removed old", then "Processing source [check] 127 files", then "Running build backend [check] Complete". Duration: "2.3 seconds".

**Example 2: Build cleans old wheels**
There's an old wheel in dist/. Build phase 1 shows "Cleaning dist/ [check] Removed old" and the old wheel is gone.

**Example 3: Build backend failure**
Roberto's pyproject.toml has invalid entry point. Phase 3 shows "Running build backend [x] Failed" with error message and suggested fix.

#### UAT Scenarios

```gherkin
Scenario: Build shows progress phases
  Given pre-flight checks have passed
  When the build process runs
  Then phase "Cleaning dist/" shows progress then checkmark
  And phase "Processing source" shows "${file_count} files"
  And phase "Running build backend" shows progress then checkmark
  And build duration is displayed

Scenario: Build cleans old wheel files
  Given an old wheel exists at "dist/nwave-2.0.0-py3-none-any.whl"
  When the build process runs
  Then the old wheel is removed
  And phase "Cleaning dist/" shows "Removed old"

Scenario: Build fails with backend error
  Given pyproject.toml has invalid entry point
  When the build process runs
  Then phase "Running build backend" shows failure
  And error message from backend is displayed
  And suggested fix is provided
```

#### Acceptance Criteria
- [ ] Three build phases: clean, process, build
- [ ] Each phase shows progress indicator then result
- [ ] File count displayed during processing
- [ ] Duration displayed at completion
- [ ] Backend errors captured and displayed with suggested fixes
- [ ] Wheel created at dist/nwave-${candidate_version}-py3-none-any.whl

---

### US-013: Wheel Content Validation

**As a** developer who just built a wheel
**I want** validation that the wheel is complete and correct
**So that** I catch bundling errors before install

#### Problem Statement
Claudia builds a wheel but agents/ directory wasn't included. She discovers this after install when nw doctor shows 0 agents. Validation should catch this immediately.

#### Domain Examples

**Example 1: All validation passes**
Claudia's wheel shows: Wheel format [check], Metadata present [check], Entry points [check] nw CLI defined, Agents bundled [check] 47, Commands bundled [check] 23, Templates bundled [check] 12, pipx compatible [check].

**Example 2: Missing agents detected**
Build accidentally excluded agents. Validation shows "Agents bundled [x] 0 found" and fails with "Wheel validation failed - agents not bundled".

**Example 3: Entry point missing**
Pyproject.toml entry point misconfigured. Validation shows "Entry points [x] nw CLI not found" with fix suggestion.

#### UAT Scenarios

```gherkin
Scenario: Wheel validation passes with correct content
  Given a wheel has been built
  When wheel validation runs
  Then "Wheel format" passes
  And "Metadata present" shows "pyproject.toml"
  And "Entry points" shows "nw CLI defined"
  And "Agents bundled" shows "${agent_count}"
  And "Commands bundled" shows "${command_count}"
  And "Templates bundled" shows "${template_count}"
  And "pipx compatible" shows "Verified"
  And final status shows "Wheel validation passed!"

Scenario: Validation detects missing agents
  Given wheel was built but agents directory excluded
  When wheel validation runs
  Then "Agents bundled" shows "0 found"
  And validation fails
  And error suggests checking pyproject.toml include patterns

Scenario: Validation detects missing entry point
  Given wheel was built but entry point misconfigured
  When wheel validation runs
  Then "Entry points" shows failure
  And error shows where to fix in pyproject.toml
```

#### Acceptance Criteria
- [ ] Validates wheel file format is correct
- [ ] Validates pyproject.toml metadata is bundled
- [ ] Validates nw CLI entry point is defined
- [ ] Counts and validates agents bundled
- [ ] Counts and validates commands bundled
- [ ] Counts and validates templates bundled
- [ ] Validates pipx compatibility
- [ ] Fails fast on first critical issue

---

### US-014: Build Success Summary

**As a** developer who completed a build
**I want** a clear summary of what was built
**So that** I know the build succeeded and what it contains

#### Problem Statement
Fabio's build finishes but there's no summary. He doesn't know where the wheel is, how big it is, or what it contains. He has to run ls dist/ and unzip the wheel manually.

#### Domain Examples

**Example 1: Complete success summary**
Fabio sees: "FORGE: BUILD COMPLETE" header, "nWave v1.3.0-dev-20260201-1 wheel built successfully!", artifact table with wheel path "dist/nwave-1.3.0.dev20260201.1-py3-none-any.whl", size "2.3 MB", timestamp. Contents table: 47 agents, 23 commands, 12 templates.

**Example 2: Summary matches validation counts**
The summary shows 47 agents. This matches the validation step. Consistency is verified.

#### UAT Scenarios

```gherkin
Scenario: Success summary displays complete information
  Given wheel validation has passed
  When the success summary displays
  Then header shows "FORGE: BUILD COMPLETE"
  And celebration shows "nWave v${candidate_version} wheel built successfully!"
  And artifact table shows wheel path, size, timestamp
  And contents table shows agent, command, template counts

Scenario: Summary counts match validation
  Given validation showed 47 agents, 23 commands, 12 templates
  When summary displays
  Then summary shows 47 agents, 23 commands, 12 templates
```

#### Acceptance Criteria
- [ ] Header shows "FORGE: BUILD COMPLETE"
- [ ] Version displayed matches candidate_version
- [ ] Wheel path displayed and file exists
- [ ] Wheel size displayed (human-readable)
- [ ] Build timestamp displayed
- [ ] Agent/command/template counts displayed
- [ ] Counts match validation step

---

### US-015: Local Install Prompt

**As a** developer who just built a wheel
**I want** an option to install locally immediately
**So that** I can test my changes without typing another command

#### Problem Statement
Rita builds a wheel successfully. Now she has to type "pipx install dist/nwave-1.3.0.dev20260201.1-py3-none-any.whl --force" manually. An interactive prompt would be faster.

#### Domain Examples

**Example 1: User accepts install prompt**
Rita sees "Install locally now? [Y/n]" and presses Enter. The install starts with "pipx install ${wheel_path} --force" and forge:install-local-candidate journey continues.

**Example 2: User declines install prompt**
Rita types "n". She sees manual instructions: "pipx install ${wheel_path} --force" and alternative "pip install -e ." for dev mode. Documentation URL shown.

#### UAT Scenarios

```gherkin
Scenario: User accepts install prompt
  Given a successful build has completed
  And prompt shows "Install locally now? [Y/n]"
  When user types "Y" or presses Enter
  Then "pipx install ${wheel_path} --force" runs
  And forge:install-local-candidate journey continues

Scenario: User declines install prompt
  Given prompt shows "Install locally now? [Y/n]"
  When user types "n"
  Then manual install command is displayed
  And dev mode command "pip install -e ." is shown
  And docs URL is displayed
```

#### Acceptance Criteria
- [ ] Prompt appears after successful build summary
- [ ] Default is Y (Enter accepts)
- [ ] Y triggers pipx install with --force flag
- [ ] n shows manual instructions
- [ ] Wheel path in command matches summary
- [ ] Handoff to forge:install-local-candidate is seamless

---

### US-016: Force Version Override

**As a** developer who wants a specific version
**I want** to override automatic version calculation
**So that** I can create a specific version for testing

#### Problem Statement
Alberto needs to test version 3.0.0 migration even though current is 1.2.0. Conventional commits would only bump minor. Force flag lets him override.

#### Domain Examples

**Example 1: Force higher version**
Alberto runs "forge:build-local-candidate --force-version 3.0.0". Despite commit history suggesting minor bump, version becomes "3.0.0-dev-20260201-1".

**Example 2: Force lower version rejected**
Alberto tries "--force-version 1.0.0" but current is 1.2.0. Error: "Force version rejected - must be higher than current version 1.2.0".

#### UAT Scenarios

```gherkin
Scenario: Force version higher than current
  Given current version is "1.2.0"
  When user runs "forge:build-local-candidate --force-version 2.0.0"
  Then new version is "2.0.0"
  And candidate is "2.0.0-dev-${date}-1"

Scenario: Force version lower than current rejected
  Given current version is "1.3.0"
  When user runs "forge:build-local-candidate --force-version 1.2.0"
  Then error shows "Force version rejected"
  And message shows "Force version must be higher than current"
```

#### Acceptance Criteria
- [ ] --force-version flag accepts semver string
- [ ] Force version must be > current version
- [ ] Force version takes priority over conventional commit analysis
- [ ] Clear error when force version is too low

---

### US-017: Daily Build Sequence Tracking

**As a** developer iterating rapidly
**I want** build sequences to track multiple builds per day
**So that** each candidate version is unique

#### Problem Statement
Bianca builds 5 times in one day. Without sequence, all would be "1.3.0-dev-20260201" and overwrite each other.

#### Domain Examples

**Example 1: First build of day**
Bianca's first build is "1.3.0-dev-20260201-1".

**Example 2: Second build same day**
Later same day, she builds again. Version is "1.3.0-dev-20260201-2".

**Example 3: New day resets sequence**
Next day, sequence resets. First build is "1.3.0-dev-20260202-1".

#### UAT Scenarios

```gherkin
Scenario: First build of day gets sequence 1
  Given no builds today
  When user builds
  Then candidate version ends with "-1"

Scenario: Second build increments sequence
  Given a build "1.3.0-dev-20260201-1" was made earlier today
  When user builds again
  Then candidate version is "1.3.0-dev-20260201-2"

Scenario: New day resets sequence
  Given yesterday's last build was "1.3.0-dev-20260131-5"
  When user builds today
  Then candidate version is "1.3.0-dev-20260201-1"
```

#### Acceptance Criteria
- [ ] Sequence counter tracks builds per date
- [ ] First build of day starts at 1
- [ ] Subsequent builds increment
- [ ] New day resets to 1
- [ ] Sequence persisted (survives terminal close)

---

### US-018: CI Mode Build Support

**As a** developer running builds in CI/CD
**I want** non-interactive mode
**So that** builds complete without prompts

#### Problem Statement
The CI pipeline runs forge:build-local-candidate. It hangs waiting for "Install locally now? [Y/n]" which nobody is there to answer.

#### Domain Examples

**Example 1: CI=true skips prompts**
CI=true is set. Build completes without install prompt. Exit code is 0.

**Example 2: --no-prompt flag**
User runs "forge:build-local-candidate --no-prompt". Build completes, wheel path printed for scripting.

**Example 3: --install flag auto-installs**
User runs "forge:build-local-candidate --install". Build completes and install happens automatically without prompt.

#### UAT Scenarios

```gherkin
Scenario: CI mode skips interactive prompts
  Given CI=true is set
  When user runs "forge:build-local-candidate"
  Then no prompts appear
  And build completes silently
  And exit code is 0

Scenario: --no-prompt flag skips install prompt
  When user runs "forge:build-local-candidate --no-prompt"
  Then build completes
  And install prompt is skipped
  And wheel path is printed

Scenario: --install flag auto-installs
  When user runs "forge:build-local-candidate --install"
  Then build completes
  And install proceeds automatically
  And forge:install-local-candidate completes
```

#### Acceptance Criteria
- [ ] Detects CI=true, GITHUB_ACTIONS, GITLAB_CI, JENKINS_URL
- [ ] CI mode disables all prompts
- [ ] --no-prompt flag skips install prompt
- [ ] --install flag triggers auto-install
- [ ] Exit code 0 on success, non-zero on failure

---

### US-019: Auto-repair Missing Build Dependencies

**As a** developer missing the build package
**I want** automatic installation offer
**So that** I don't have to leave the build flow

#### Problem Statement
Sara runs forge:build-local-candidate. She doesn't have the build package. Rather than just failing, it should offer to install.

#### Domain Examples

**Example 1: User accepts auto-install**
Pre-flight shows "build package missing". Prompt: "Install it now? [Y/n]". Sara types Y. Spinner shows "Installing build package...". "build v1.2.1 installed successfully". Pre-flight resumes.

**Example 2: User declines**
Sara types n. Message: "Build cancelled. Install build package manually: pip install build".

#### UAT Scenarios

```gherkin
Scenario: User accepts auto-install of build package
  Given build package is not installed
  When user runs "forge:build-local-candidate"
  Then pre-flight shows "build package missing"
  And prompt asks "Install it now? [Y/n]"
  When user types "Y"
  Then "pip install build" runs
  And message shows "build v${version} installed successfully"
  And pre-flight resumes

Scenario: User declines auto-install
  Given prompt shows "Install it now? [Y/n]"
  When user types "n"
  Then build is cancelled
  And message shows "Install build package manually: pip install build"
```

#### Acceptance Criteria
- [ ] Detects missing build package via "python -m build --version"
- [ ] Offers auto-install with Y/n prompt
- [ ] Runs "pip install build" on acceptance
- [ ] Shows success message with installed version
- [ ] Resumes pre-flight checks after install
- [ ] Shows manual instructions on decline

---

## Journey 2: forge:install-local-candidate

### US-020: Install Pre-flight Validation

**As a** developer running forge:install-local-candidate
**I want** validation that wheel exists and environment is ready
**So that** I catch problems before attempting install

#### Problem Statement
Tommaso runs forge:install-local-candidate but forgot to build first. Install fails midway with confusing error. Pre-flight should catch missing wheel.

#### Domain Examples

**Example 1: All checks pass**
Tommaso has wheel at dist/, pipx installed, ~/.claude writable. All checks green.

**Example 2: Missing wheel with auto-chain**
No wheel in dist/. Pre-flight shows "Wheel [x] No wheel found". Prompt: "Run forge:build-local now? [Y/n]". User accepts, build runs, install resumes.

**Example 3: pipx missing**
pipx not installed. Pre-flight shows "[x] pipx not installed" with install instructions.

#### UAT Scenarios

```gherkin
Scenario: All pre-flight checks pass
  Given wheel exists at "${wheel_path}"
  And pipx is installed
  And ~/.claude is writable
  When user runs "forge:install-local-candidate"
  Then all checks show green
  And installation proceeds

Scenario: Missing wheel offers build chain
  Given no wheel in dist/
  When user runs "forge:install-local-candidate"
  Then check shows "No wheel found in dist/"
  And prompt asks "Run forge:build-local now? [Y/n]"
  When user types "Y"
  Then forge:build-local runs
  And after success, install resumes

Scenario: pipx missing shows blocking error
  Given pipx is not installed
  When user runs "forge:install-local-candidate"
  Then error shows "pipx not installed"
  And fix shows "pip install pipx && pipx ensurepath"
```

#### Acceptance Criteria
- [ ] Validates Python version 3.10+
- [ ] Validates pipx available (blocking)
- [ ] Validates ~/.claude writable
- [ ] Validates wheel exists in dist/ (fixable via build chain)
- [ ] Validates wheel format is valid .whl
- [ ] Auto-chain to build on missing wheel
- [ ] Handles multiple wheels with selection prompt

---

### US-021: Release Readiness Validation

**As a** developer preparing a release
**I want** to validate wheel meets PyPI requirements
**So that** I catch issues before CI/CD attempts upload

#### Problem Statement
The wheel is built but missing required metadata. CI/CD fails on twine upload. Readiness validation catches this locally first.

#### Domain Examples

**Example 1: All readiness checks pass**
Wheel has valid metadata, entry points, license, README. Status: "READY FOR PYPI".

**Example 2: CHANGELOG missing entry (warning)**
CHANGELOG.md has no entry for version. Warning shown but not blocking. "Continue anyway? [Y/n]".

**Example 3: twine check fails (blocking)**
twine check finds missing description. "[x] twine check failed". Fix instructions provided.

#### UAT Scenarios

```gherkin
Scenario: All release readiness checks pass
  Given wheel has complete metadata
  And CHANGELOG has entry for version
  When release readiness validation runs
  Then "twine check" passes
  And "Metadata complete" passes
  And "Entry points" shows "nw CLI defined"
  And "CHANGELOG exists" passes
  And "License bundled" passes
  And "README bundled" passes
  And status shows "READY FOR PYPI"

Scenario: Missing CHANGELOG shows warning
  Given CHANGELOG has no entry for this version
  When release readiness runs
  Then "CHANGELOG exists" shows warning
  And prompt asks "Continue anyway? [Y/n]"
  When user types "Y"
  Then installation continues

Scenario: twine check fails
  Given wheel has invalid metadata
  When release readiness runs
  Then "twine check" fails
  And error shows what's wrong
  And installation aborts
```

#### Acceptance Criteria
- [ ] Runs twine check on wheel (blocking)
- [ ] Validates metadata completeness: name, version, description, author, license
- [ ] Validates entry points: nw CLI defined
- [ ] Validates CHANGELOG entry exists (warning, not blocking)
- [ ] Validates PEP 440 version format
- [ ] Validates LICENSE bundled
- [ ] Validates README bundled
- [ ] Shows "READY FOR PYPI" or failure status

---

### US-022: Candidate Installation via pipx

**As a** developer with validated wheel
**I want** installation via pipx with progress display
**So that** I can see what's happening

#### Problem Statement
pipx install runs silently for 30 seconds. Developer wonders if it's working.

#### Domain Examples

**Example 1: Install shows phases**
Phases: "Uninstalling previous [check] Removed", "Installing from wheel [check] Complete", "Symlinking nw [check] Available". Duration: "3.2 seconds".

**Example 2: Previous install removed first**
Existing nwave version uninstalled before new version installed.

**Example 3: nw command available after**
"which nw" returns valid path after install.

#### UAT Scenarios

```gherkin
Scenario: Install shows progress phases
  Given release readiness passed
  When install process runs
  Then "Uninstalling previous" shows progress
  And "Installing from wheel" shows progress
  And "Symlinking nw" shows when complete
  And duration is displayed

Scenario: Previous installation removed first
  Given previous nwave version installed
  When install runs
  Then previous version is uninstalled first
  And new version is installed

Scenario: nw command is available after install
  Given install completed
  Then "which nw" returns a valid path
  And nw command is executable
```

#### Acceptance Criteria
- [ ] Uninstalls previous nwave if exists (pipx uninstall nwave --force)
- [ ] Installs from wheel (pipx install ${wheel_path} --force)
- [ ] Verifies nw command available (which nw)
- [ ] Shows phase progress during install
- [ ] Displays total install duration
- [ ] Handles install failures with clear error messages

---

### US-023: Post-Install Doctor Verification

**As a** developer who just installed candidate
**I want** automatic health verification
**So that** I know the install succeeded fully

#### Problem Statement
pipx install succeeded but agents weren't copied to ~/.claude. Without doctor, this isn't caught until user tries to use an agent.

#### Domain Examples

**Example 1: Doctor passes all checks**
Core installation, 47 agents, 23 commands, 12 templates, config valid, permissions OK, version matches. Status: "HEALTHY".

**Example 2: Version mismatch detected**
nw --version shows different version than wheel. "[x] Version mismatch - wheel 1.3.0-dev vs installed 1.2.0".

**Example 3: Agent count mismatch**
Build bundled 47 agents but only 45 installed. Warning shown.

#### UAT Scenarios

```gherkin
Scenario: Doctor shows healthy status
  Given candidate installed successfully
  When doctor verification runs
  Then "Core installation" passes
  And "Agent files" shows "${agent_count} OK"
  And "Command files" shows "${command_count} OK"
  And "Template files" shows "${template_count} OK"
  And "Config valid" passes
  And "Permissions" passes
  And "Version match" shows ${candidate_version}
  And status shows "HEALTHY"

Scenario: Doctor detects version mismatch
  Given wheel version is "1.3.0-dev-20260201-1"
  And installed version shows "1.2.0"
  When doctor runs
  Then "Version match" fails
  And error shows wheel vs installed versions
  And reinstall instructions provided

Scenario: Doctor shows nw version output
  Given candidate installed
  When doctor runs
  Then nw --version output displayed
  And shows "nWave Framework v${candidate_version}"
  And shows "Installed: ${install_path}"
```

#### Acceptance Criteria
- [ ] Runs automatically after successful pipx install
- [ ] Verifies core installation at ${install_path}
- [ ] Counts and validates agent files match wheel bundled count
- [ ] Counts and validates command files
- [ ] Counts and validates template files
- [ ] Validates config (nwave.yaml) parses correctly
- [ ] Validates file permissions are correct
- [ ] Validates nw --version matches candidate_version
- [ ] Shows nw --version output with full details

---

### US-024: Release Report Generation

**As a** developer who completed install
**I want** a comprehensive release report
**So that** I have a checklist for testing and know CI/CD will pass

#### Problem Statement
Install finished but developer doesn't know what to test or if it's ready for CI/CD.

#### Domain Examples

**Example 1: Complete release report**
Report shows: version, branch, build/install timestamps, wheel size. Install manifest: 47 agents, 23 commands, 12 templates, install path. Release readiness: all checks passed. Test checklist: restart Claude, run /nw:version, etc.

**Example 2: Report with warning**
CHANGELOG was missing. Report shows warning in release readiness section but otherwise complete.

#### UAT Scenarios

```gherkin
Scenario: Release report shows complete summary
  Given doctor verification passed
  When release report displays
  Then header shows "FORGE: CANDIDATE INSTALLED"
  And release summary shows version, branch, timestamps, size
  And install manifest shows agent, command, template counts
  And release readiness shows all checks passed
  And test checklist shows verification steps

Scenario: Release report includes test checklist
  Given install completed
  When report displays
  Then checklist includes "Restart Claude Code"
  And includes "Run: /nw:version"
  And includes "Run: /nw:help"
  And includes "Test an agent: /nw:product-owner"
  And includes "Run: nw doctor"
```

#### Acceptance Criteria
- [ ] Shows "FORGE: CANDIDATE INSTALLED" header
- [ ] Release summary: version, branch, build timestamp, install timestamp, size
- [ ] Install manifest: agent count, command count, template count, install path
- [ ] Release readiness: summary of all checks (passed/warning/failed)
- [ ] Test checklist: restart Claude, /nw:version, /nw:help, test agent, nw doctor
- [ ] Next steps guidance for local testing and CI/CD

---

### US-025: Auto-chain to Build on Missing Wheel

**As a** developer who forgot to build
**I want** automatic build chain
**So that** I don't have to remember the build command

#### Problem Statement
Pietro runs forge:install-local-candidate but dist/ is empty. Rather than just failing, offer to run build.

#### Domain Examples

**Example 1: User accepts build chain**
No wheel. Prompt: "Run forge:build-local now? [Y/n]". User types Y. Build runs. After success, install resumes automatically.

**Example 2: Build succeeds and install continues**
After build completes, message shows "Resuming install-local-candidate...". Install continues with newly built wheel.

#### UAT Scenarios

```gherkin
Scenario: Missing wheel triggers build prompt
  Given no wheel in dist/
  When user runs "forge:install-local-candidate"
  Then error shows "No wheel found in dist/"
  And prompt asks "Run forge:build-local now? [Y/n]"

Scenario: User accepts and build runs
  Given user sees build prompt
  When user types "Y"
  Then forge:build-local runs
  And after success, install resumes
  And message shows "Resuming install-local-candidate..."
```

#### Acceptance Criteria
- [ ] Detects empty dist/ or no .whl files
- [ ] Offers Y/n prompt to run build
- [ ] On acceptance, runs forge:build-local flow
- [ ] After successful build, automatically resumes install
- [ ] On decline, shows manual build command

---

### US-026: Multiple Wheel Selection

**As a** developer with multiple wheels in dist/
**I want** to select which wheel to install
**So that** I can choose the right version

#### Problem Statement
Pietro has 3 wheels from different builds. Install picks one arbitrarily.

#### Domain Examples

**Example 1: Selection prompt shown**
dist/ has: nwave-1.2.0.whl, nwave-1.3.0-dev-1.whl, nwave-1.3.0-dev-2.whl. Prompt shows numbered list. User types "3" to select latest.

**Example 2: User cancels selection**
User types "c" to cancel. Install aborts with "Selection cancelled".

#### UAT Scenarios

```gherkin
Scenario: Multiple wheels prompts selection
  Given multiple wheels in dist/
  When user runs "forge:install-local-candidate"
  Then warning shows "Multiple wheels found"
  And numbered list of wheels displayed
  And prompt asks "Select wheel [1-N, or 'c' to cancel]:"

Scenario: User selects wheel
  Given selection prompt shown
  When user types "2"
  Then second wheel is selected
  And installation proceeds with that wheel

Scenario: User cancels selection
  Given selection prompt shown
  When user types "c"
  Then installation is cancelled
```

#### Acceptance Criteria
- [ ] Detects multiple .whl files in dist/
- [ ] Shows numbered list sorted by modification time (newest first)
- [ ] Accepts number input to select
- [ ] Accepts 'c' to cancel
- [ ] Proceeds with selected wheel

---

### US-027: CI Mode Install Support

**As a** developer running install in CI/CD
**I want** non-interactive mode
**So that** install completes without prompts

#### Problem Statement
CI pipeline runs forge:install-local-candidate. It hangs waiting for prompts.

#### Domain Examples

**Example 1: CI=true auto-selects newest wheel**
Multiple wheels exist. CI=true is set. Newest wheel auto-selected, no prompt.

**Example 2: Exit code reflects status**
On success: exit 0. On failure: exit non-zero.

#### UAT Scenarios

```gherkin
Scenario: CI mode auto-selects newest wheel
  Given CI=true is set
  And multiple wheels exist
  When user runs "forge:install-local-candidate"
  Then newest wheel is selected automatically
  And no prompt appears

Scenario: Exit code is 0 on success
  Given CI=true is set
  And install succeeds
  Then exit code is 0

Scenario: Exit code is non-zero on failure
  Given CI=true is set
  And doctor fails
  Then exit code is non-zero
```

#### Acceptance Criteria
- [ ] Detects CI environment
- [ ] Auto-selects newest wheel on multiple
- [ ] Skips all interactive prompts
- [ ] Returns exit code 0 on success
- [ ] Returns non-zero exit code on any failure

---

### US-028: JSON Output for CI/CD

**As a** CI/CD pipeline consuming install results
**I want** JSON output
**So that** I can parse results programmatically

#### Problem Statement
CI/CD needs to parse install results to decide next steps. Human-readable output is hard to parse.

#### Domain Examples

**Example 1: JSON includes all sections**
JSON has release_summary, install_manifest, release_readiness, doctor_status.

**Example 2: CI can archive report**
"--output release-report.md" writes report to file for artifact archiving.

#### UAT Scenarios

```gherkin
Scenario: JSON output is valid and complete
  Given user runs "forge:install-local-candidate --json"
  Then output is valid JSON
  And includes release_summary with version, branch, timestamps
  And includes install_manifest with counts
  And includes release_readiness with check results

Scenario: Report written to file
  Given user runs "forge:install-local-candidate --output release-report.md"
  Then release report written to file
  And file can be archived as CI artifact
```

#### Acceptance Criteria
- [ ] --json flag outputs JSON instead of TUI
- [ ] JSON schema: status, version, install_path, checks array, counts
- [ ] --output flag writes report to specified file
- [ ] File suitable for CI artifact archiving

---

### US-029: Strict Mode for Release Validation

**As a** developer preparing official release
**I want** strict mode that fails on any warning
**So that** I catch all issues before PyPI upload

#### Problem Statement
CHANGELOG warning is non-blocking normally. For release, it should be blocking.

#### Domain Examples

**Example 1: Strict mode fails on warning**
--strict flag set. CHANGELOG missing entry. Normal mode would warn and continue. Strict mode fails.

**Example 2: Exit code reflects strict failure**
Strict failure returns non-zero exit code.

#### UAT Scenarios

```gherkin
Scenario: Strict mode fails on warnings
  Given CHANGELOG has no entry for version
  When user runs "forge:install-local-candidate --strict"
  Then CHANGELOG warning becomes error
  And installation aborts
  And exit code is non-zero

Scenario: Strict mode passes when all clean
  Given all checks pass with no warnings
  When user runs "forge:install-local-candidate --strict"
  Then installation completes successfully
```

#### Acceptance Criteria
- [ ] --strict flag elevates warnings to errors
- [ ] Any warning causes install abort in strict mode
- [ ] Non-zero exit code on strict failure
- [ ] Useful for CI release gates

---

## Journey 3: install-nwave (PyPI)

### US-030: PyPI Download and Dependencies

**As a** developer installing nWave for first time
**I want** pipx install nwave to download and install
**So that** I get a working nWave installation

#### Problem Statement
First-time user runs pipx install nwave. It should download, install dependencies, and proceed to verification.

#### Domain Examples

**Example 1: Download shows progress**
"Downloading nWave..." with progress bar. "nwave-2.1.0.tar.gz (2.3 MB)". Dependencies shown: rich, click, pyyaml.

**Example 2: pipx not found**
User doesn't have pipx. Error: "pipx not found" with install instructions.

#### UAT Scenarios

```gherkin
Scenario: Successful download from PyPI
  Given user has pipx installed
  When user runs "pipx install nwave"
  Then download progress bar appears
  And version "${version}" is displayed
  And dependencies are installed
  And installation proceeds

Scenario: pipx not found shows error
  Given user does not have pipx
  When user runs "pipx install nwave"
  Then error shows "pipx not found"
  And instructions show how to install pipx
```

#### Acceptance Criteria
- [ ] Downloads from PyPI on pipx install nwave
- [ ] Shows download progress with version
- [ ] Lists dependencies being installed
- [ ] Handles pipx not found with clear instructions
- [ ] Handles network errors gracefully

---

### US-031: Install Path Resolution

**As a** developer with custom Claude setup
**I want** configurable install path
**So that** nWave works with my setup

#### Problem Statement
Developer has Claude at ~/my-claude not ~/.claude. Default path won't work.

#### Domain Examples

**Example 1: Default path used**
No override set. Install uses ~/.claude/agents/nw/.

**Example 2: Environment variable override**
NWAVE_INSTALL_PATH=~/my-claude/agents/nw. Install uses custom path.

**Example 3: Pre-flight shows resolved path**
Output shows "Using: ~/.claude/agents/nw/" so user sees where files go.

#### UAT Scenarios

```gherkin
Scenario: Default path when no override
  Given NWAVE_INSTALL_PATH not set
  And installer.yaml has no custom path
  When install path is resolved
  Then path is "~/.claude/agents/nw/"
  And output shows "Using default: ~/.claude/agents/nw/"

Scenario: Environment variable override
  Given NWAVE_INSTALL_PATH=~/custom-claude/agents/nw/
  When install path is resolved
  Then path is "~/custom-claude/agents/nw/"
  And output shows "NWAVE_INSTALL_PATH=~/custom-claude/agents/nw/"
```

#### Acceptance Criteria
- [ ] Resolves in order: env var -> config file -> default
- [ ] Default is ~/.claude/agents/nw/
- [ ] Expands ~ correctly
- [ ] Shows resolved path in pre-flight output
- [ ] Creates path if doesn't exist

---

### US-032: Framework Installation with Progress

**As a** developer installing nWave
**I want** to see installation progress
**So that** I know it's working

#### Problem Statement
Install takes 30 seconds with no output. User wonders if frozen.

#### Domain Examples

**Example 1: Progress phases displayed**
"Preparing installation...", "Building distribution..." with progress bar, "Installing components to ${install_path}" with per-component progress: Agents 47, Commands 23, Templates 12.

**Example 2: Validation at end**
After install, validation table shows counts and "Validation: PASSED".

#### UAT Scenarios

```gherkin
Scenario: Installation shows progress phases
  Given pre-flight checks passed
  When framework installation runs
  Then "Checking source files" spinner appears
  And "Building distribution" progress bar appears
  And "Installing components" shows per-component progress
  And each component shows count and checkmark when complete

Scenario: Installation validation displays
  Given all components installed
  When validation runs
  Then table shows Agents ${agent_count}, Commands ${command_count}, Templates ${template_count}
  And "Manifest Created" shown
  And final status "Validation: PASSED"
```

#### Acceptance Criteria
- [ ] Shows preparation phase
- [ ] Shows build distribution with progress bar
- [ ] Shows backup creation if existing install
- [ ] Shows per-component installation with counts
- [ ] Shows validation table at end
- [ ] Consistent emoji and formatting with design spec

---

### US-033: Doctor Verification for PyPI Install

**As a** developer who installed from PyPI
**I want** automatic health verification
**So that** I know installation is complete

#### Problem Statement
pipx install succeeds but files may not be in right place. Doctor catches this.

#### Domain Examples

**Example 1: Doctor runs automatically**
After pipx install, doctor runs and shows "HEALTHY".

**Example 2: Doctor matches install counts**
Doctor shows same agent/command/template counts as installation step.

#### UAT Scenarios

```gherkin
Scenario: Doctor runs after successful install
  Given installation completed
  Then doctor verification runs automatically
  And shows health check table
  And status shows "HEALTHY"

Scenario: Doctor counts match installation
  Given installation showed 47 agents
  When doctor runs
  Then doctor shows 47 agents
```

#### Acceptance Criteria
- [ ] Doctor runs automatically after pipx install
- [ ] Shows same table format as forge:install-local-candidate
- [ ] Counts match installation step
- [ ] HEALTHY/DEGRADED/UNHEALTHY status displayed

---

### US-034: Welcome and Celebration Display

**As a** new nWave user
**I want** a celebration after successful install
**So that** I feel accomplished and welcomed

#### Problem Statement
Install finishes with just "Done". No celebration, no guidance.

#### Domain Examples

**Example 1: ASCII logo and celebration**
nWave ASCII art displayed. "nWave v2.1.0 installed successfully!" Next steps shown.

**Example 2: Restart instruction prominent**
"IMPORTANT: Restart Claude Code to activate" in highlighted box.

#### UAT Scenarios

```gherkin
Scenario: Welcome message displays celebration
  Given doctor shows HEALTHY
  Then ASCII logo is displayed
  And message shows "nWave v${version} installed successfully!"
  And "Your Claude is now powered by nWave" displayed

Scenario: Restart instruction is prominent
  Given welcome message displays
  Then restart instruction is in highlighted box
  And shows "Restart Claude Code (Cmd+Q then reopen)"
```

#### Acceptance Criteria
- [ ] nWave ASCII art logo displayed
- [ ] Version shown in celebration message
- [ ] Restart instruction highlighted
- [ ] Next steps listed: restart, /nw:version, /nw:help
- [ ] Documentation URL shown

---

### US-035: Restart Claude Code Notification

**As a** new nWave user
**I want** clear restart instructions
**So that** I don't wonder why commands don't work

#### Problem Statement
User installs nWave, opens Claude Code, types /nw:version. Nothing happens because Claude wasn't restarted.

#### Domain Examples

**Example 1: Prominent restart message**
Highlighted box: "IMPORTANT: Restart Claude Code to activate".

**Example 2: Next steps guide restart**
"1. Restart Claude Code (Cmd+Q then reopen)"

#### UAT Scenarios

```gherkin
Scenario: Restart instruction is clear
  Given welcome message displays
  Then restart is step 1 of next steps
  And keyboard shortcut Cmd+Q is mentioned

Scenario: User understands restart is required
  Given user sees "IMPORTANT: Restart Claude Code to activate"
  Then user knows to restart before trying commands
```

#### Acceptance Criteria
- [ ] Restart instruction in highlighted/warning box
- [ ] First item in next steps list
- [ ] Keyboard shortcut mentioned (Cmd+Q for Mac)
- [ ] Explains why restart is needed

---

### US-036: Verification in Claude Code

**As a** user who restarted Claude Code
**I want** /nw:version to confirm installation
**So that** I know nWave is working

#### Problem Statement
User restarts Claude, types /nw:version. It should show version, path, and counts.

#### Domain Examples

**Example 1: Version command output**
"/nw:version" shows: "nWave Framework v2.1.0", "Installed: ~/.claude/agents/nw/", "Agents: 47 | Commands: 23 | Templates: 12", "All systems operational".

**Example 2: Counts match doctor**
Counts shown by /nw:version match doctor output.

#### UAT Scenarios

```gherkin
Scenario: /nw:version works after restart
  Given user restarted Claude Code
  When user types "/nw:version"
  Then version matches installation
  And install path shown
  And agent/command/template counts shown
  And "All systems operational" displayed

Scenario: Counts consistent with doctor
  Given doctor showed 47 agents
  When user runs /nw:version
  Then shows 47 agents
```

#### Acceptance Criteria
- [ ] /nw:version command works in Claude Code
- [ ] Shows nWave Framework v${version}
- [ ] Shows install path
- [ ] Shows agent/command/template counts
- [ ] Shows "All systems operational" if healthy

---

### US-037: Custom Install Path via Environment

**As a** developer with non-standard Claude location
**I want** NWAVE_INSTALL_PATH to work with pipx
**So that** I can use nWave with custom setup

#### Problem Statement
Developer has Claude at ~/work/claude. They set NWAVE_INSTALL_PATH before running pipx install.

#### Domain Examples

**Example 1: Env var used during install**
NWAVE_INSTALL_PATH=~/work/claude/agents/nw pipx install nwave. Install goes to custom path.

**Example 2: All paths use env var**
Pre-flight, install, doctor, /nw:version all use the custom path.

#### UAT Scenarios

```gherkin
Scenario: Install respects NWAVE_INSTALL_PATH
  Given NWAVE_INSTALL_PATH=~/work/claude/agents/nw
  When user runs "pipx install nwave"
  Then files installed to ~/work/claude/agents/nw
  And doctor shows this path
  And /nw:version shows this path
```

#### Acceptance Criteria
- [ ] NWAVE_INSTALL_PATH respected during install
- [ ] Path propagated to all steps
- [ ] Path shown in pre-flight for transparency
- [ ] Path shown in /nw:version

---

### US-038: CI Mode for PyPI Install

**As a** developer installing in CI/CD
**I want** non-interactive mode
**So that** install completes without prompts

#### Problem Statement
CI installs nWave as dependency. Should complete silently.

#### Domain Examples

**Example 1: CI=true silent install**
CI=true set. No logo, no prompts. Exit 0 on success.

**Example 2: JSON output available**
--format json provides machine-readable output.

#### UAT Scenarios

```gherkin
Scenario: CI mode completes silently
  Given CI=true is set
  When user runs "pipx install nwave"
  Then no interactive prompts
  And no ASCII logo
  And exit code 0 on success

Scenario: JSON output in CI mode
  Given CI=true and --format json
  When install completes
  Then output is valid JSON
  And includes success: true, version, counts
```

#### Acceptance Criteria
- [ ] Detects CI environment variables
- [ ] Disables ASCII logo in CI
- [ ] Disables interactive prompts
- [ ] Exit code 0 on success
- [ ] --format json for machine-readable output

---

### US-039: Backup Creation Before Install

**As a** developer reinstalling/upgrading nWave
**I want** automatic backup
**So that** I can rollback if needed

#### Problem Statement
User upgrades nWave. Something breaks. They want to rollback but old files are gone.

#### Domain Examples

**Example 1: Backup created before install**
Existing nWave at ~/.claude/agents/nw. Backup created at ~/.claude/backups/nwave-20260201-143025 before new install.

**Example 2: Backup path shown**
"Backup created at ${backup_path}" displayed during install.

#### UAT Scenarios

```gherkin
Scenario: Backup created for existing install
  Given nWave already installed
  When user runs "pipx install nwave"
  Then existing files backed up
  And backup path shown with timestamp
  And new version installed

Scenario: Backup not created for fresh install
  Given no existing nWave installation
  When user runs "pipx install nwave"
  Then no backup created
  And installation proceeds
```

#### Acceptance Criteria
- [ ] Detects existing installation
- [ ] Creates timestamped backup before install
- [ ] Backup path configurable via installer.yaml
- [ ] Shows backup path during install
- [ ] Skips backup if no existing installation

---

## Implementation Notes

### Shared Infrastructure Requirements

All stories depend on the shared infrastructure (US-001 to US-005). The infrastructure provides:

1. **Pre-flight check framework** - Reusable validation with auto-repair
2. **Doctor health check framework** - Consistent verification across journeys
3. **Shared artifacts registry** - Ensures consistency of version, counts, paths
4. **Installer configuration** - Flexible path resolution
5. **URL configuration** - Central URL management

### Journey Dependencies

```
Infrastructure (US-001 to US-005)
    |
    +---> Journey 1: Build (US-010 to US-019)
    |         |
    |         +---> Journey 2: Install Local (US-020 to US-029)
    |
    +---> Journey 3: PyPI Install (US-030 to US-039)
              (can run in parallel after infrastructure)
```

### Testing Strategy

Each story includes UAT scenarios in Gherkin format. These scenarios should be:

1. Automated in the acceptance test suite
2. Used to drive TDD implementation
3. Validated with actual CLI behavior
4. Run in CI/CD pipeline

### Emotional Arc Validation

The journeys follow emotional arcs defined in the design:

- **Build**: Focused -> Confident -> Accomplished
- **Install Local**: Focused -> Trust -> Celebratory
- **PyPI Install**: Excited -> Confident -> Delighted

Test scenarios should validate the user experience matches these emotional states.

---

## Definition of Ready Checklist

- [x] Problem statement clear and in domain language
- [x] User/persona identified with real names and characteristics
- [x] At least 3 domain examples with real data per story
- [x] UAT scenarios in Given/When/Then format (3-7 per story)
- [x] Acceptance criteria derived from UAT
- [x] Stories right-sized (1-3 days estimated)
- [x] Technical notes identify constraints
- [x] Dependencies documented

---

---

## Cross-Cutting Stories

### US-040: Rollback on Installation Failure

**As a** developer whose installation failed mid-process
**I want** automatic rollback to restore my previous working installation
**So that** I'm never left with a broken nWave setup

#### Problem Statement
Roberto's nWave installation fails during agent file copy (Step 4). His previous working version is gone, the new version is incomplete. He's stuck with no working nWave until he manually fixes the situation. Automatic rollback should restore his previous working installation.

#### Domain Examples

**Example 1: Automatic rollback on install failure**
Roberto has nWave 2.0.0 working. He runs upgrade to 2.1.0. During agent installation, a file copy fails. Rollback automatically triggers, restores 2.0.0 from backup at ~/.claude/backups/nwave-20260201-143025. Roberto sees "Installation failed, restored previous version 2.0.0".

**Example 2: Manual rollback trigger**
Maria installed 2.1.0 but it has a bug affecting her workflow. She runs "nw rollback" to restore her previous version from the latest backup. She sees backup list with timestamps and selects the one she wants.

**Example 3: Rollback verification via doctor**
After automatic rollback, Roberto runs "nw doctor". Doctor shows "HEALTHY" with his previous version 2.0.0, confirming rollback succeeded.

**Example 4: No backup available (fresh install failure)**
First-time user Lucia's install fails. There's no backup to restore. Message shows "No previous installation to restore. Please retry: pipx install nwave".

#### UAT Scenarios

```gherkin
Scenario: Automatic rollback on installation failure
  Given Roberto has nWave 2.0.0 installed at ~/.claude/agents/nw/
  And backup exists at ~/.claude/backups/nwave-20260201-143025/
  When installation of 2.1.0 fails during agent file copy
  Then rollback triggers automatically
  And files are restored from ~/.claude/backups/nwave-20260201-143025/
  And message shows "Installation failed. Previous version restored."
  And nw doctor shows version 2.0.0
  And status shows "HEALTHY"

Scenario: Manual rollback command
  Given Maria has nWave 2.1.0 installed
  And backup of 2.0.0 exists at ~/.claude/backups/nwave-20260201-143025/
  When Maria runs "nw rollback"
  Then available backups are listed with timestamps
  And Maria selects backup "nwave-20260201-143025"
  Then files are restored from selected backup
  And message shows "Rolled back to backup from 2026-02-01 14:30:25"
  And nw doctor shows restored version

Scenario: Rollback verification via doctor
  Given automatic rollback just completed
  When Roberto runs "nw doctor"
  Then doctor shows previous version
  And all component counts are correct
  And status shows "HEALTHY"

Scenario: Fresh install failure with no backup
  Given Lucia has no previous nWave installation
  When her first installation fails
  Then message shows "Installation failed. No previous version to restore."
  And message shows "Please retry: pipx install nwave"
  And partial files are cleaned up

Scenario: Rollback with no available backups
  Given Marco has nWave installed but no backups exist
  When Marco runs "nw rollback"
  Then error shows "No backups available"
  And message shows "Reinstall with: pipx install nwave --force"
```

#### Acceptance Criteria
- [ ] Automatic rollback triggers when installation fails at any step after backup creation
- [ ] Rollback restores files from most recent backup at ~/.claude/backups/
- [ ] "nw rollback" command lists available backups with timestamps and versions
- [ ] User can select specific backup to restore
- [ ] Rollback runs nw doctor automatically to verify restoration
- [ ] Clean error message when no backups available
- [ ] Partial installation files cleaned up on failure before rollback
- [ ] Rollback status displayed clearly: "Previous version restored" or "No backup available"

#### Technical Notes
- Backup path: ~/.claude/backups/nwave-YYYYMMDD-HHMMSS/
- Rollback must be atomic: either fully restore or report failure
- Partial files from failed install must be cleaned before rollback
- Doctor verification required after rollback to confirm health
- References journey steps: forge:install-local-candidate Step 3 (Install Candidate), install-nwave Step 4 (Framework Installation)

#### Dependencies
- US-039: Backup Creation Before Install (backup must exist for rollback to work)
- US-002: Shared Doctor Health Check Framework (verification after rollback)

---

### US-041: Upgrade Detection and Handling

**As a** developer running pipx install nwave
**I want** the installer to detect if I'm upgrading or doing a fresh install
**So that** I get appropriate behavior: backup on upgrade, clean install otherwise

#### Problem Statement
Carla runs "pipx install nwave" but already has nWave installed. Without upgrade detection, the installer might overwrite her existing installation without backup, or treat an upgrade like a fresh install and miss important migration steps.

#### Domain Examples

**Example 1: Upgrade detected with backup**
Carla has nWave 2.0.0 installed. She runs "pipx install nwave" to get 2.1.0. Installer detects existing installation, creates backup at ~/.claude/backups/nwave-20260201-143025, then proceeds with upgrade. She sees "Upgrading from 2.0.0 to 2.1.0".

**Example 2: Fresh install detected**
First-time user Paolo runs "pipx install nwave". No existing installation detected. Installer proceeds with fresh install path, no backup created. He sees "Installing nWave 2.1.0 (fresh install)".

**Example 3: Same version reinstall**
Marco has 2.1.0 installed, runs "pipx install nwave" again. Installer detects same version, asks "nWave 2.1.0 already installed. Reinstall? [Y/n]". He types Y to force reinstall.

**Example 4: Downgrade attempt blocked**
Sofia has 2.1.0 but tries to install older 2.0.0 via local wheel. Installer warns "Downgrade detected: 2.1.0 -> 2.0.0. This may cause issues. Continue? [Y/n]".

#### UAT Scenarios

```gherkin
Scenario: Upgrade from older version
  Given Carla has nWave 2.0.0 installed at ~/.claude/agents/nw/
  When Carla runs "pipx install nwave" for version 2.1.0
  Then installer detects existing version 2.0.0
  And message shows "Upgrading from 2.0.0 to 2.1.0"
  And backup is created at ~/.claude/backups/nwave-20260201-${timestamp}/
  And message shows "Backup created: ~/.claude/backups/nwave-20260201-${timestamp}/"
  And installation proceeds with upgrade path
  And doctor shows version 2.1.0 after completion

Scenario: Fresh install on clean system
  Given Paolo has no nWave installation
  When Paolo runs "pipx install nwave"
  Then installer detects no existing installation
  And message shows "Installing nWave ${version} (fresh install)"
  And no backup is created
  And installation proceeds with fresh install path
  And welcome celebration displays

Scenario: Reinstall same version
  Given Marco has nWave 2.1.0 installed
  When Marco runs "pipx install nwave" for version 2.1.0
  Then installer detects same version
  And prompt asks "nWave 2.1.0 already installed. Reinstall? [Y/n]"
  When Marco types "Y"
  Then backup is created
  And reinstallation proceeds

Scenario: Same version reinstall declined
  Given prompt asks "nWave 2.1.0 already installed. Reinstall? [Y/n]"
  When Marco types "n"
  Then message shows "Installation cancelled. Existing installation unchanged."
  And no changes are made

Scenario: Downgrade warning
  Given Sofia has nWave 2.1.0 installed
  When Sofia runs "forge:install-local-candidate" with wheel version 2.0.0
  Then installer detects downgrade
  And warning shows "Downgrade detected: 2.1.0 -> 2.0.0"
  And prompt asks "This may cause issues. Continue? [Y/n]"
  When Sofia types "Y"
  Then backup is created
  And installation proceeds with warning logged

Scenario: CI mode auto-upgrade
  Given CI=true is set
  And existing nWave 2.0.0 is installed
  When CI runs "pipx install nwave" for 2.1.0
  Then upgrade proceeds automatically
  And backup is created
  And no prompts appear
  And exit code is 0 on success
```

#### Acceptance Criteria
- [ ] Installer detects existing nWave installation by checking ~/.claude/agents/nw/ or NWAVE_INSTALL_PATH
- [ ] Version comparison: reads installed version from nwave.yaml or manifest
- [ ] Upgrade path (new > old): creates backup, shows "Upgrading from X to Y", proceeds
- [ ] Fresh install path (no existing): shows "Fresh install", skips backup, proceeds
- [ ] Same version path: prompts for reinstall confirmation (skipped in CI mode)
- [ ] Downgrade path (new < old): shows warning, requires confirmation (skipped in CI mode with warning logged)
- [ ] CI mode: auto-proceeds with upgrade, creates backup, no prompts
- [ ] Pre-flight output clearly shows: detected version, action (upgrade/fresh/reinstall), backup status

#### Technical Notes
- Version detection: Read from ~/.claude/agents/nw/manifest.yaml or nwave.yaml
- Version comparison: Use semantic versioning comparison
- Backup triggered for: upgrades, reinstalls, downgrades (not fresh installs)
- References journey steps: install-nwave Step 3 (Pre-flight Checks), Step 4 (Framework Installation backup creation)
- References journey steps: forge:install-local-candidate Step 1 (Pre-flight), Step 3 (Install Candidate uninstall previous)

#### Dependencies
- US-039: Backup Creation Before Install (triggered by upgrade detection)
- US-004: Installer Configuration System (NWAVE_INSTALL_PATH support)
- US-001: Shared Pre-flight Check Framework (version detection as pre-flight check)

---

**Document Version**: 1.1
**Ready for DESIGN Wave**: Yes
