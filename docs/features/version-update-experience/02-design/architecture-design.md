# Version Update Experience - Architecture Design

**Feature:** Version delivery and update loop for end users
**Wave:** DESIGN
**Status:** Architecture design complete
**Date:** 2026-01-25
**Architect:** Morgan (Solution Architect)

---

## Architecture Overview

### Architecture Style: Hexagonal Architecture (Ports & Adapters)

This feature adopts **Hexagonal Architecture** to ensure clean separation between:
- **Core business logic** (version comparison, update orchestration)
- **External dependencies** (GitHub API, file system, git operations)

This enables:
- Independent testing of business logic without external dependencies
- Easy replacement of adapters (e.g., GitHub API client libraries)
- Clear contracts through port interfaces
- Technology-agnostic domain model

### System Context

The Version Update Experience operates within the nWave framework ecosystem:

**External Dependencies:**
- **GitHub API** - Fetch release information (latest version, changelog)
- **Local File System** - Read/write VERSION file, backup/restore operations
- **Git Configuration** - Resolve repository URL dynamically
- **User (CLI)** - Interactive commands (`/nw:version`, `/nw:update`)

**Design Principles:**
1. **No hardcoded repository URLs** - Dynamic resolution from git config
2. **Fail gracefully** - Network failures show local version with helpful guidance
3. **Safety first** - Backup before any changes, automatic rollback on failure
4. **User confirmation** - Always require explicit approval before updates
5. **Clear feedback** - Attention-grabbing notifications and error messages

---

## Component Architecture (Hexagonal Layers)

### Core Domain (Business Logic)

The innermost hexagon contains pure business logic with no external dependencies:

**1. Version Manager**
- Compare semantic versions (current vs available)
- Detect breaking changes (major version bumps)
- Determine update necessity
- Extract version highlights from changelog

**2. Update Orchestrator**
- Coordinate update workflow: backup → download → install → cleanup
- Manage update state transitions
- Handle rollback logic on failure
- Coordinate backup cleanup (30-day retention)

**3. Changelog Processor**
- Parse GitHub release notes
- Extract 2-3 key highlights
- Identify breaking changes in release notes
- Format changelog for user display

**4. Backup Manager**
- Calculate backup destination paths (`~/.claude_bck_YYYYMMDD/`)
- Determine backups eligible for cleanup (>30 days)
- Manage backup lifecycle (create, validate, restore, cleanup)

### Application Ports (Interfaces)

Ports define contracts between core domain and external systems:

**Inbound Ports (Primary):**
- **CLI Command Port** - Entry point for user commands
  - `execute_version_check()` → VersionCheckResult
  - `execute_update()` → UpdateResult

**Outbound Ports (Secondary):**
- **Version Source Port** - Fetch version information
  - `get_installed_version()` → VersionInfo
  - `get_latest_release()` → ReleaseMetadata

- **File System Port** - Backup and file operations
  - `backup_directory(source, destination)` → BackupResult
  - `restore_directory(backup_path, destination)` → RestoreResult
  - `delete_directory(path)` → DeleteResult
  - `read_version_file(path)` → string
  - `write_version_file(path, version)` → WriteResult

- **Git Config Port** - Repository information
  - `get_remote_origin_url()` → string
  - `parse_repository_info(url)` → RepositoryInfo

- **User Interaction Port** - Confirmation and display
  - `display_version_info(info)` → void
  - `display_update_banner(changelog)` → void
  - `confirm_update()` → boolean
  - `display_error(message)` → void

### Adapter Layer (Infrastructure)

Concrete implementations of port interfaces:

**Inbound Adapters:**
- **CLI Command Adapter** - Implements `/nw:version` and `/nw:update` commands
  - Parses command arguments
  - Routes to appropriate core domain service
  - Formats output for console display

**Outbound Adapters:**
- **GitHub API Adapter** - Implements Version Source Port
  - Uses `requests` library for HTTP calls
  - Endpoint: `GET /repos/{owner}/{repo}/releases/latest`
  - Handles rate limiting, timeouts, network errors
  - Caches repository URL for session duration

- **Local File System Adapter** - Implements File System Port
  - Uses `shutil` for directory operations
  - Uses `pathlib.Path` for cross-platform path handling
  - Preserves file permissions during backup/restore
  - Handles permission errors, disk space errors

- **Git Config Adapter** - Implements Git Config Port
  - Executes `git config --get remote.origin.url`
  - Parses both HTTPS and SSH URL formats
  - Returns RepositoryInfo(owner, repo)
  - Handles missing `.git/config` gracefully

- **Console UI Adapter** - Implements User Interaction Port
  - Uses `rich` library for formatted console output
  - Attention-grabbing banners with color/borders
  - Prompt for Y/N confirmation
  - Error messages with suggested actions

---

## Key Architectural Decisions (ADRs)

### ADR-001: Hexagonal Architecture for Domain Isolation

**Context:**
The Version Update Experience integrates with multiple external systems (GitHub API, file system, git) that may change or need mocking during testing.

**Decision:**
Adopt Hexagonal Architecture with clear port/adapter boundaries.

**Rationale:**
- **Testability:** Core business logic can be unit tested without external dependencies
- **Flexibility:** Easy to swap implementations (e.g., different GitHub API clients)
- **Maintainability:** Clear contracts prevent tight coupling
- **Evolution:** Can add new integrations (e.g., GitLab API) without changing core logic

**Consequences:**
- **Positive:** Clean architecture, excellent testability, technology independence
- **Negative:** Initial complexity, more interfaces/files to maintain
- **Mitigation:** Clear documentation of port contracts, comprehensive interface tests

**Alternatives Considered:**
- **Layered Architecture:** Rejected due to potential for dependency leaks between layers
- **Monolithic Script:** Rejected due to poor testability and tight coupling

---

### ADR-002: Dynamic Repository URL Resolution

**Context:**
The nWave framework may be forked, used in enterprise environments, or developed locally with different remote origins. Hardcoding repository URLs would break these scenarios.

**Decision:**
Dynamically resolve repository URL from `git config --get remote.origin.url` at runtime.

**Rationale:**
- **Flexibility:** Works across open source, enterprise forks, and development environments
- **Correctness:** Always fetches from the correct repository
- **No Configuration:** Zero-configuration required from users
- **Graceful Fallback:** If git config unavailable, show local version only

**Consequences:**
- **Positive:** Universal compatibility, no hardcoded URLs, automatic fork support
- **Negative:** Requires git repository with remote origin configured
- **Mitigation:** Clear error message if resolution fails, with remediation steps

**Alternatives Considered:**
- **Hardcoded GitHub URL:** Rejected - breaks enterprise/fork scenarios
- **Configuration File:** Rejected - adds user burden, prone to misconfiguration
- **Environment Variable:** Rejected - requires manual setup, not discoverable

---

### ADR-003: GitHub API as Version Source (No Local Cache)

**Context:**
Version information can be sourced from local CHANGELOG.md, cached API responses, or real-time GitHub API calls.

**Decision:**
Use real-time GitHub API calls with no local cache, graceful degradation on failure.

**Rationale:**
- **Accuracy:** Always shows latest release information
- **Simplicity:** No cache invalidation logic required
- **Freshness:** Users always see current state
- **Graceful Degradation:** On network failure, show local version with retry hint

**Consequences:**
- **Positive:** Simple implementation, always accurate, no stale cache issues
- **Negative:** Requires network connectivity, subject to GitHub API rate limits
- **Mitigation:** 10-second timeout, clear error messages, suggest manual check URL

**Alternatives Considered:**
- **Local CHANGELOG.md:** Rejected - may be out of date after local changes
- **Cached API Response:** Rejected - adds complexity, introduces stale data
- **Polling with Cache:** Rejected - over-engineering for infrequent checks

---

### ADR-004: Backup-First with Automatic Rollback

**Context:**
Updates may fail mid-process (network error, corrupted download, permission issues), leaving installation in broken state.

**Decision:**
Always create backup before any changes, automatic rollback on failure.

**Workflow:**
1. Create backup at `~/.claude_bck_YYYYMMDD/`
2. Validate backup creation succeeded
3. Perform update operations
4. On any failure, automatically restore from backup
5. On success, preserve backup for 30 days

**Rationale:**
- **Safety:** Zero data loss even on catastrophic failure
- **User Confidence:** Users trust update process knowing rollback exists
- **Automatic Recovery:** No manual intervention required on failure
- **Audit Trail:** Backup directories serve as rollback points

**Consequences:**
- **Positive:** Safe updates, automatic recovery, user confidence
- **Negative:** Disk space usage, backup operation time (~30 seconds)
- **Mitigation:** 30-day auto-cleanup, clear disk space warnings

**Alternatives Considered:**
- **No Backup:** Rejected - unacceptable risk of data loss
- **Optional Backup:** Rejected - users won't use it, leads to support issues
- **Incremental Backup:** Rejected - adds complexity, slower restore

---

### ADR-005: Semantic Versioning for Breaking Change Detection

**Context:**
Users need clear warning when updates contain breaking changes requiring migration effort.

**Decision:**
Use semantic versioning major version bump (1.x.x → 2.x.x) as breaking change signal.

**Implementation:**
- Compare major version components
- If major version increases, display breaking change warning
- Extract "BREAKING CHANGES" section from GitHub release notes
- Require explicit confirmation before proceeding

**Rationale:**
- **Industry Standard:** Semantic versioning is widely understood
- **Simple Detection:** Major version comparison is straightforward
- **Clear Signal:** Major bumps indicate breaking changes by convention
- **Automated:** Semantic-release enforces this convention

**Consequences:**
- **Positive:** Clear, automated detection; no manual tagging required
- **Negative:** Relies on team following semantic versioning discipline
- **Mitigation:** Conventional commits enforcement via pre-commit hooks

**Alternatives Considered:**
- **Changelog Parsing:** Rejected - fragile, depends on free-text format
- **Manual Tagging:** Rejected - prone to human error, not automated
- **Breaking Change File:** Rejected - additional maintenance burden

---

### ADR-006: 30-Day Backup Retention with Auto-Cleanup

**Context:**
Without cleanup, backup directories accumulate indefinitely, consuming disk space.

**Decision:**
Automatically delete backups older than 30 days during update process.

**Implementation:**
- Trigger cleanup after successful backup creation (before update)
- Scan for directories matching `~/.claude_bck_YYYYMMDD/` pattern
- Delete directories where `(current_date - backup_date) > 30 days`
- Log warnings for locked or permission-denied directories (non-blocking)
- Preserve most recent backup regardless of age

**Rationale:**
- **Disk Space Management:** Prevents unbounded growth
- **Reasonable Retention:** 30 days provides safety buffer for rollback
- **Automated:** No user intervention required
- **Non-Blocking:** Cleanup failures don't prevent updates

**Consequences:**
- **Positive:** Automatic cleanup, no user burden, disk space preservation
- **Negative:** Users cannot configure retention period without env var
- **Mitigation:** Make retention configurable via `NWAVE_BACKUP_RETENTION_DAYS` env var

**Alternatives Considered:**
- **No Cleanup:** Rejected - disk space accumulation is poor UX
- **Manual Cleanup Command:** Rejected - users won't use it
- **Max Count (e.g., keep 5):** Rejected - doesn't account for update frequency

---

### ADR-007: Conventional Commits Enforcement via Git Hooks

**Context:**
Semantic-release depends on structured commit history to determine version bumps and generate changelogs.

**Decision:**
Enforce Conventional Commits format at commit time using git hooks (commit-msg hook).

**Implementation:**
- Use `commitlint` with `@commitlint/config-conventional`
- Hook runs via `pre-commit` framework for cross-platform compatibility
- Reject commits with invalid format and show helpful error message
- Error message includes format explanation, examples, and reference link

**Rationale:**
- **Automation Prerequisite:** Semantic-release requires conventional commits
- **Early Validation:** Catch errors at commit time, not CI/CD
- **Team Discipline:** Prevents non-compliant commits from entering history
- **Learning Tool:** Error messages educate developers on format

**Consequences:**
- **Positive:** Consistent commit history, automated version bumping works reliably
- **Negative:** Learning curve for developers unfamiliar with format
- **Mitigation:** Clear error messages with examples, link to official spec

**Alternatives Considered:**
- **CI/CD Validation:** Rejected - too late, requires force-push to fix
- **Commitizen Interactive Tool:** Rejected - extra step, not enforced
- **No Enforcement:** Rejected - semantic-release fails silently

---

### ADR-008: Pre-Push Validation for Release Configuration

**Context:**
Releases fail if VERSION file or semantic-release configuration is missing, wasting CI/CD time.

**Decision:**
Validate release configuration at pre-push time using git hook.

**Validation Checks:**
1. `nWave/VERSION` file exists with valid semver format (X.Y.Z)
2. `.releaserc` or `release.config.js` exists
3. All checks pass before push proceeds

**Rationale:**
- **Fast Feedback:** Catch configuration issues before pushing
- **CI/CD Efficiency:** Don't waste GitHub Actions minutes on predictable failures
- **Team Productivity:** Fix issues locally, not through failed CI runs
- **Pre-Release Gate:** Ensures releases are properly configured

**Consequences:**
- **Positive:** Fast feedback, reduced CI failures, better productivity
- **Negative:** Additional local validation step
- **Mitigation:** Fast validation (<1 second), clear error messages

**Alternatives Considered:**
- **CI/CD Only:** Rejected - slow feedback loop, wastes resources
- **Manual Checklist:** Rejected - error-prone, not enforced
- **No Validation:** Rejected - releases fail silently

---

## Quality Attribute Scenarios

### Performance

**Scenario 1: Version Check Response Time**
- **Stimulus:** User runs `/nw:version` command
- **Response:** System fetches latest release from GitHub API
- **Measure:** Total response time < 3 seconds (including network latency)
- **Architectural Support:**
  - Minimal parsing logic in adapter layer
  - Direct API call without retries on success
  - Session-based caching of repository URL (avoid repeated git config calls)

**Scenario 2: Backup Creation Time**
- **Stimulus:** User confirms update, system creates backup
- **Response:** Directory copy operation for typical `~/.claude/` size (10-50 MB)
- **Measure:** Backup creation < 30 seconds
- **Architectural Support:**
  - Use `shutil.copytree` with optimized settings
  - No compression (trade space for speed)
  - Parallel file operations where possible

**Scenario 3: Update Installation Time**
- **Stimulus:** User confirms update after backup
- **Response:** Download and install new version
- **Measure:** Total update time < 60 seconds
- **Architectural Support:**
  - Streaming download (don't load entire package into memory)
  - Minimal validation (checksum only)
  - Reuse existing installer logic

### Reliability

**Scenario 4: Network Failure During Version Check**
- **Stimulus:** GitHub API unreachable or timeout during `/nw:version`
- **Response:** Display local version with helpful error message
- **Measure:** No exception thrown, clear guidance provided
- **Architectural Support:**
  - Try/except around GitHub API adapter
  - Timeout set to 10 seconds
  - Fallback to local version display with manual check URL

**Scenario 5: Partial Update Failure**
- **Stimulus:** Update fails mid-process (network error, corrupted file, permission error)
- **Response:** Automatic rollback from backup, clear error message
- **Measure:** System restored to pre-update state, no data loss
- **Architectural Support:**
  - Backup validation before proceeding
  - Transactional update pattern (all-or-nothing)
  - Automatic restore from backup on any exception
  - Clear error message with failure reason

**Scenario 6: Disk Full During Backup**
- **Stimulus:** Insufficient disk space when creating backup
- **Response:** Fail before update, preserve original installation
- **Measure:** No partial backup created, original installation unchanged
- **Architectural Support:**
  - Check available disk space before backup
  - Fail fast if insufficient space
  - Clear error message with disk space requirements

### Security

**Scenario 7: GitHub API Rate Limiting**
- **Stimulus:** Frequent version checks exceed GitHub API rate limit (60/hour unauthenticated)
- **Response:** Graceful error message suggesting retry later
- **Measure:** No crash, clear retry guidance
- **Architectural Support:**
  - Detect HTTP 429 (Rate Limit Exceeded) response
  - Display rate limit error with reset time if available
  - No retry loop (user initiates retry)

**Scenario 8: HTTPS Only for GitHub API**
- **Stimulus:** All GitHub API calls
- **Response:** Enforce HTTPS, reject insecure connections
- **Measure:** Zero HTTP (unencrypted) requests
- **Architectural Support:**
  - GitHub API adapter uses `https://` URLs only
  - `requests` library validates SSL certificates by default
  - No option to disable SSL verification

**Scenario 9: Backup Permission Preservation**
- **Stimulus:** Backup of `~/.claude/` directory
- **Response:** Restored backup maintains original file permissions
- **Measure:** File permissions identical after restore
- **Architectural Support:**
  - `shutil.copytree` with `copy_function=shutil.copy2` (preserves metadata)
  - Backup manager validates permissions after restore

### Usability

**Scenario 10: Attention-Grabbing Update Notification**
- **Stimulus:** Update available when running `/nw:version`
- **Response:** Banner with clear visual differentiation from normal output
- **Measure:** User recognizes update is available within 2 seconds of seeing output
- **Architectural Support:**
  - `rich` library for colored borders and formatting
  - Banner includes: version diff, 2-3 changelog highlights, update command
  - Breaking change warning in red/bold if major version bump

**Scenario 11: Breaking Change Warning Prominence**
- **Stimulus:** Major version update available (1.x.x → 2.x.x)
- **Response:** Breaking change warning clearly visible
- **Measure:** User understands migration may be required
- **Architectural Support:**
  - Separate breaking change section in banner
  - Red/bold "BREAKING CHANGES" heading
  - Extract breaking change notes from GitHub release
  - Require explicit confirmation with warning text

**Scenario 12: Clear Error Guidance**
- **Stimulus:** Any error condition (network, permissions, disk space)
- **Response:** Error message includes what went wrong and suggested action
- **Measure:** User can resolve issue without external documentation
- **Architectural Support:**
  - Error messages follow pattern: "[Problem] → [Suggested Action]"
  - Include relevant context (file paths, URLs, commands)
  - No generic "update failed" messages

---

## Cross-Cutting Concerns

### Error Handling

**Strategy:** Fail fast with clear error messages, automatic recovery where possible

**Error Categories:**

1. **Network Errors** (GitHub API)
   - Timeout (10 seconds) → "Could not check for updates. Try again later or check manually at {url}"
   - Rate limit → "GitHub API rate limit exceeded. Try again in {X} minutes"
   - Invalid response → "Could not fetch release information. GitHub API may be unavailable"

2. **File System Errors**
   - Permission denied → "Permission denied: Cannot write to {path}. Check file permissions"
   - Disk full → "Insufficient disk space for backup. Need {X} MB free, found {Y} MB"
   - Directory locked → "Directory in use: {path}. Close applications and try again"

3. **Git Configuration Errors**
   - No remote origin → "Could not determine remote repository. Run from a git repository with configured origin"
   - Invalid URL format → "Git remote URL format not recognized: {url}"

4. **Update Errors**
   - Backup creation failed → Abort update, no changes made
   - Download failed → Restore from backup, report error
   - Install failed → Restore from backup, report error
   - Rollback failed → Critical error, manual intervention required (rare)

**Error Handling Flow:**
```
Try:
    Create backup
    Validate backup
    Download new version
    Install new version
    Cleanup old backups
Except Exception as e:
    Restore from backup
    Report error with context
    Suggest remediation action
```

### Logging

**Log Levels:**
- **INFO:** Version checks, update operations, backup cleanup
- **WARN:** Non-blocking failures (cleanup failures, locked directories)
- **ERROR:** Blocking failures (network timeout, permission denied, disk full)

**Log Location:** `~/.claude/nwave-update.log`

**Log Format:**
```
[TIMESTAMP] [LEVEL] [COMPONENT] Message
2026-01-25 14:32:15 INFO  [GitHubAdapter] Fetching latest release for swcraftsmanshipdojo/nWave
2026-01-25 14:32:17 INFO  [VersionManager] Version check: 1.5.7 → 1.6.0 available
2026-01-25 14:35:42 INFO  [BackupManager] Backup created: ~/.claude_bck_20260125/
2026-01-25 14:36:08 INFO  [UpdateOrchestrator] Update completed: 1.5.7 → 1.6.0
2026-01-25 14:36:10 WARN  [BackupManager] Could not delete old backup: ~/.claude_bck_20241201/ (permission denied)
```

**Structured Logging:**
- Use JSON format for machine parsing if needed
- Include component name for debugging
- Include operation context (version numbers, file paths)

### Security

**GitHub API Security:**
- HTTPS only, SSL certificate validation
- No API token required for public repositories (unauthenticated access)
- Rate limiting handled gracefully (60 requests/hour)
- No caching of API responses (avoid stale data)

**File System Security:**
- Preserve file permissions during backup/restore
- No privilege escalation (run as current user)
- Validate paths to prevent directory traversal
- No execution of arbitrary code from remote sources

**Update Verification:**
- Download from official GitHub releases only
- Dynamic repository URL prevents hardcoded URLs
- User confirmation required before any changes
- Backup before changes (rollback on failure)

### Configuration

**Environment Variables:**
- `NWAVE_BACKUP_RETENTION_DAYS` - Backup retention period (default: 30)
- `NWAVE_GITHUB_API_TIMEOUT` - GitHub API timeout in seconds (default: 10)
- `NWAVE_UPDATE_LOG_LEVEL` - Logging level (default: INFO)

**No User Configuration Required:**
- Repository URL resolved dynamically from git config
- Backup location derived from Claude config directory
- VERSION file location standard (`~/.claude/nwave-version.txt`)

---

## Component Interaction Protocols

### Version Check Flow

```
1. User executes /nw:version command
   ↓
2. CLI Command Adapter receives command
   ↓
3. CLI Adapter calls VersionManager.check_for_updates()
   ↓
4. VersionManager requests:
   - LocalVersionSource.get_installed_version() → "1.5.7"
   - GitHubAdapter.get_latest_release() → ReleaseMetadata(version="1.6.0", ...)
   ↓
5. VersionManager compares versions:
   - current: 1.5.7
   - available: 1.6.0
   - breaking_change: false (minor version bump)
   ↓
6. VersionManager calls ChangelogProcessor.extract_highlights()
   ↓
7. VersionManager returns VersionCheckResult to CLI Adapter
   ↓
8. CLI Adapter calls ConsoleUIAdapter.display_version_info()
   ↓
9. ConsoleUIAdapter renders attention-grabbing banner
```

### Update Flow

```
1. User executes /nw:update command
   ↓
2. CLI Command Adapter receives command
   ↓
3. CLI Adapter calls UpdateOrchestrator.execute_update()
   ↓
4. UpdateOrchestrator checks for updates (reuses version check flow)
   ↓
5. If no update available → Display "Already up to date" and exit
   ↓
6. UpdateOrchestrator calls BackupManager.create_backup()
   - BackupManager determines destination: ~/.claude_bck_20260125/
   - FileSystemAdapter.backup_directory(~/.claude/, ~/.claude_bck_20260125/)
   ↓
7. BackupManager validates backup creation succeeded
   ↓
8. UpdateOrchestrator calls BackupManager.cleanup_old_backups()
   - Scan for backups older than 30 days
   - FileSystemAdapter.delete_directory() for each eligible backup
   ↓
9. UpdateOrchestrator displays changelog and prompts user
   - ConsoleUIAdapter.display_update_banner()
   - ConsoleUIAdapter.confirm_update() → boolean
   ↓
10. If user cancels → Delete new backup, display "Update cancelled", exit
    ↓
11. UpdateOrchestrator downloads and installs new version
    - GitHubAdapter.download_release()
    - FileSystemAdapter.install_files()
    ↓
12. On any exception during install:
    - BackupManager.restore_backup()
    - Display error with rollback confirmation
    - Exit with error code
    ↓
13. UpdateOrchestrator returns UpdateResult(success=True)
    ↓
14. ConsoleUIAdapter.display_update_summary()
    - Show updated version
    - Show 2-3 key changes
    - Show full changelog link
```

---

## Technology Stack Rationale

This section provides detailed technology selections with decision matrices. See `technology-stack.md` for implementation details.

**Core Programming Language:** Python 3.7+
- Already used in nWave framework
- Excellent library ecosystem for CLI, HTTP, file operations
- Cross-platform compatibility

**Key Libraries:**
- **GitHub API:** `requests` (HTTP client) - Simple, reliable, well-documented
- **Semantic Version Parsing:** `packaging` - Standard library for Python packaging
- **CLI UI:** `rich` - Modern terminal formatting, colored output, progress bars
- **File Operations:** `shutil` + `pathlib` - Standard library, cross-platform
- **Git Operations:** `subprocess` + `git` command - Direct git config access

**Why Not:**
- **github.py SDK:** Over-engineered for simple API calls, adds dependency
- **httpx:** Unnecessary async complexity for synchronous operations
- **semver library:** `packaging` is more standard in Python ecosystem
- **click/typer:** nWave already has command infrastructure

---

## Installation System Integration

### Existing Installation Infrastructure

nWave has a mature installation system in `scripts/install/`:

**Components:**
- `install_nwave.py` - Framework installer (backup, build, install, validate)
- `update_nwave.py` - Developer update workflow (build → uninstall → install)
- `uninstall_nwave.py` - Clean framework removal
- `install_utils.py` - Shared utilities (BackupManager, PathUtils, Logger, ManifestWriter)

**Key Principle:** REUSE existing infrastructure, don't duplicate.

### Two Update Workflows

#### Developer Workflow (Source Repository Update)
**Scenario:** Developer has nWave repository cloned locally
**Command:** `python3 scripts/install/update_nwave.py --backup --force`
**Process:** Build from source → Uninstall → Install
**Use Case:** Framework development, testing unreleased changes

#### End User Workflow (GitHub Release Update)
**Scenario:** User installed nWave via installer, no local repository
**Command:** `/nw:update`
**Process:** Download release → Extract → Call existing installer
**Use Case:** Production users updating to stable releases

### /nw:update Implementation Strategy

The `/nw:update` command acts as a **download orchestrator** that delegates to existing installation scripts:

```python
# nWave/cli/update_cli.py

def execute_update():
    # 1. Check for updates via GitHub API
    version_info = check_version()
    if not version_info.is_newer:
        print("Already up to date")
        return

    # 2. Download release package from GitHub
    release_url = get_release_download_url(version_info.available_version)
    download_path = download_release(release_url, "/tmp/nwave-update/")

    # 3. Extract release package
    extracted_path = extract_release(download_path)

    # 4. DELEGATE to existing installer
    installer_script = extracted_path / "scripts/install/install_nwave.py"

    # The existing installer handles:
    # - Backup creation (via BackupManager)
    # - Framework validation
    # - Installation
    # - Manifest generation

    result = subprocess.run([sys.executable, str(installer_script)])

    if result.returncode == 0:
        print(f"Updated to version {version_info.available_version}")
    else:
        print("Update failed. Run manual recovery if needed.")
```

**Advantages:**
- ✅ Reuses battle-tested installation logic
- ✅ Single source of truth for installation/backup
- ✅ Existing BackupManager already handles backup/restore
- ✅ Existing validation already in place
- ✅ Consistency: same installation path for all users
- ✅ Developer workflow (update_nwave.py) still works independently

### Deployment and Integration

**Files Added:**
- `nWave/core/version_manager.py` - Core domain logic (version comparison, breaking change detection)
- `nWave/core/update_download_orchestrator.py` - Download coordination ONLY (delegates to installer)
- `nWave/adapters/github_adapter.py` - GitHub API integration (version check + release download)
- `nWave/adapters/git_config_adapter.py` - Repository URL resolution
- `nWave/commands/version.py` - `/nw:version` command implementation
- `nWave/commands/update.py` - `/nw:update` command implementation

**Files REUSED from scripts/install/**:
- `install_utils.py::BackupManager` - Backup creation and restoration
- `install_utils.py::PathUtils` - Cross-platform path utilities
- `install_utils.py::Logger` - Structured logging with file output
- `install_utils.py::ManifestWriter` - Installation manifest generation
- `install_nwave.py` - Complete installation logic (DELEGATED to, not reimplemented)

**Configuration Files Modified:**
- `.pre-commit-config.yaml` - Add commitlint hook
- `commitlint.config.js` - Conventional commits configuration
- `.releaserc` - Semantic-release configuration
- `nWave/VERSION` - Source version file

**Files Created:**
- `~/.claude/nwave-version.txt` - Installed version (created by installer)
- `~/.claude/nwave-update.log` - Update operation log
- `~/.claude_bck_YYYYMMDD/` - Backup directories (transient)

### CI/CD Integration

**GitHub Actions Workflow:**
- Trigger: Push to `main` or `master` branch
- Steps:
  1. Run tests (ensure commits are valid)
  2. Run semantic-release
     - Analyze commits since last tag
     - Determine version bump
     - Generate CHANGELOG.md
     - Update nWave/VERSION
     - Commit changes
     - Create git tag
     - Create GitHub Release with release notes
  3. Publish release artifacts (if applicable)

**semantic-release Configuration:**
See `.releaserc` in Artifacts section of requirements document.

---

## Risks and Mitigation

### Risk 1: GitHub API Rate Limiting

**Probability:** Low (60 requests/hour for unauthenticated, sufficient for typical usage)
**Impact:** Medium (users can't check for updates)

**Mitigation:**
- No caching (avoid wasting rate limit on stale checks)
- Clear error message with rate limit reset time
- Suggest manual check at releases URL
- Consider GitHub token for authenticated requests (5000 requests/hour) in future

### Risk 2: Backup Disk Space

**Probability:** Medium (depends on user disk space)
**Impact:** Low (30-day auto-cleanup prevents accumulation)

**Mitigation:**
- Check available disk space before backup
- 30-day auto-cleanup (configurable via env var)
- Clear error message if insufficient space
- Suggest disk space requirements in error

### Risk 3: Update Failure Mid-Process

**Probability:** Low (network is primary risk)
**Impact:** High (broken installation if not handled)

**Mitigation:**
- Backup-first architecture (rollback always available)
- Automatic rollback on any failure
- Transactional pattern (all-or-nothing)
- Clear error messages with rollback confirmation

### Risk 4: Concurrent Update Attempts

**Probability:** Low (user would need to run `/nw:update` multiple times)
**Impact:** High (backup conflicts, race conditions)

**Mitigation:**
- Lock file mechanism (`.nwave-update.lock` during update)
- Check lock file before starting update
- Clear error if another update is in progress
- Remove lock file on completion or failure

### Risk 5: Corrupted Download

**Probability:** Low (GitHub CDN is reliable)
**Impact:** High (broken installation if not detected)

**Mitigation:**
- Validate download completeness (file size check)
- Checksum validation if GitHub provides checksums
- Automatic rollback from backup on validation failure
- Clear error message with retry suggestion

### Risk 6: Breaking Change Not Detected

**Probability:** Low (relies on semantic versioning discipline)
**Impact:** Medium (users update without preparation)

**Mitigation:**
- Enforce conventional commits via pre-commit hooks
- Pre-push validation ensures VERSION file exists
- semantic-release automated version bumping
- Team education on semantic versioning

---

## Future Enhancements (Out of MVP Scope)

1. **Configurable Backup Retention** - Environment variable for retention period (already planned)
2. **Dry Run Mode** - `--dry-run` flag to preview update without executing
3. **Rollback Command** - `/nw:rollback` to restore from specific backup
4. **Passive Update Notifications** - Show update banner in other nWave commands
5. **Offline Changelog Cache** - Cache last fetched changelog for offline viewing
6. **Update History** - Log of all updates with versions and timestamps
7. **Pre/Post Update Hooks** - Allow custom scripts before/after updates
8. **Multi-Repository Support** - Manage updates for nWave extensions
9. **Delta Updates** - Download only changed files (not full installation)
10. **Automatic Updates** - Optional opt-in for automatic updates (with backup)

---

## Architecture Validation Against Requirements

### User Story Coverage

| User Story | Architectural Support |
|------------|----------------------|
| US-001: Check Installed Version | VersionManager + GitHubAdapter + ConsoleUIAdapter |
| US-002: Update nWave Safely | UpdateOrchestrator + BackupManager + FileSystemAdapter |
| US-003: Breaking Change Warning | VersionManager.detect_breaking_changes() + ConsoleUIAdapter |
| US-004: Automatic Backup Cleanup | BackupManager.cleanup_old_backups() |
| US-005: Conventional Commit Enforcement | commitlint via pre-commit hooks (external) |
| US-006: Pre-push Validation | Pre-push hook (external) |
| US-007: Automated Changelog Generation | semantic-release (external) + GitHub Actions |

### Technical Requirements Coverage

| Requirement | Architectural Support |
|-------------|----------------------|
| TR-001: Version Source of Truth | LocalVersionSource + GitHubAdapter |
| TR-002: GitHub API Integration | GitHubAdapter with requests library |
| TR-003: Backup Specification | BackupManager + FileSystemAdapter |
| TR-004: Semantic Versioning Detection | VersionManager.compare_versions() |
| TR-005: Conventional Commit Enforcement | commitlint (external) |
| TR-006: Pre-push Validation | Pre-push hook (external) |
| TR-007: Repository URL Dynamic Resolution | GitConfigAdapter.resolve_repository_url() |

### Non-Functional Requirements Coverage

| NFR | Architectural Support |
|-----|----------------------|
| NFR-001: Performance | Direct API calls, minimal parsing, session caching |
| NFR-002: Reliability | Backup-first, automatic rollback, graceful degradation |
| NFR-003: Security | HTTPS only, permission preservation, no privilege escalation |

---

## Appendix: Open Questions Resolution

### Q1: VERSION File Format

**Decision:** Plain text with single line containing semantic version (e.g., "1.5.7")

**Rationale:**
- **Simplicity:** Easy to read and write programmatically
- **Parsability:** `version = open('VERSION').read().strip()`
- **No Dependencies:** No JSON/YAML parser required
- **Extensibility:** Can migrate to structured format in future if needed

**Example:**
```
1.5.7
```

### Q2: Changelog Source

**Decision:** GitHub release body API (auto-generated by semantic-release)

**Rationale:**
- **Consistency:** Single source of truth (GitHub releases)
- **Automation:** semantic-release generates from conventional commits
- **No Duplication:** Don't maintain both CHANGELOG.md and GitHub release notes
- **Offline Capability:** Future enhancement can cache last fetched changelog

**Implementation:**
- Fetch from `GET /repos/{owner}/{repo}/releases/latest` response `body` field
- semantic-release populates this from commit history

### Q3: Hook Tooling Choice

**Decision:** commitlint with pre-commit framework

**Rationale:**
- **Industry Standard:** commitlint is de facto standard for conventional commits
- **Configuration:** Simple config via `@commitlint/config-conventional`
- **Integration:** Works seamlessly with pre-commit framework (cross-platform)
- **Error Messages:** Excellent built-in error messages
- **No Interactive Prompts:** Validation only (commitizen adds interactive prompts we don't need)

**Alternatives Considered:**
- **commitizen:** Rejected - adds interactive prompt overhead
- **Custom script:** Rejected - reinventing the wheel

### Q4: Backup Atomicity

**Decision:** Direct copy with validation

**Rationale:**
- **Simplicity:** `shutil.copytree` is atomic at OS level
- **Performance:** No temp directory overhead
- **Failure Safety:** Backup validation before proceeding with update
- **Disk Space:** No double space requirement (temp + final)

**Implementation:**
```python
shutil.copytree(
    source="~/.claude/",
    destination="~/.claude_bck_20260125/",
    copy_function=shutil.copy2,  # Preserve metadata
    ignore_dangling_symlinks=True
)
```

**If copy fails:** Exception thrown, update aborted, no partial backup created.

### Q5: CI/CD Pipeline Design

**Decision:** GitHub Actions with semantic-release, triggered on push to main

**Workflow:**
```yaml
name: Release
on:
  push:
    branches: [main, master]

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Full history for semantic-release
          persist-credentials: false

      - uses: actions/setup-node@v3
        with:
          node-version: 18

      - name: Install semantic-release
        run: npm install -D semantic-release @semantic-release/changelog @semantic-release/git @semantic-release/github @semantic-release/exec

      - name: Run semantic-release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: npx semantic-release
```

**Secrets Required:**
- `GITHUB_TOKEN` - Provided automatically by GitHub Actions

**Trigger Conditions:**
- Push to main/master branch
- semantic-release analyzes commits since last tag
- Only creates release if version bump determined (feat/fix commits present)

---

---

## CLI Integration Specification (Python-Based)

### Platform Constraint

**CRITICAL:** nWave avoids bash/shell scripts for Windows compatibility. The framework accepts Python 3.11+ as a prerequisite. All CLI integration and scripts **MUST** be Python-based, NOT bash-based.

### Command Implementation Architecture

**Entry Points:**
```
nWave/cli/version_cli.py    # Python entry point for /nw:version
nWave/cli/update_cli.py     # Python entry point for /nw:update
```

**Command File Registration:**
```
Source:    nWave/tasks/nw/version.md, nWave/tasks/nw/update.md
Installed: ~/.claude/commands/nw/version.md, ~/.claude/commands/nw/update.md
```

**Command File Pattern:**
```markdown
# ~/.claude/commands/nw/version.md

When invoked, execute:
python3 ~/.claude/nWave/cli/version_cli.py

The script will:
1. Read local version from ~/.claude/nwave-version.txt
2. Check GitHub API for latest release
3. Compare versions and detect breaking changes
4. Display formatted output
```

**Python CLI Implementation:**
```python
# nWave/cli/version_cli.py
#!/usr/bin/env python3
"""
Entry point for /nw:version command.
Invoked by Claude Code when user types /nw:version.
"""
import sys
from pathlib import Path

# Add nWave to path for imports
sys.path.insert(0, str(Path.home() / ".claude" / "nWave"))

from nWave.core.version_manager import VersionManager
from nWave.adapters.github_adapter import GitHubAPIAdapter
from nWave.adapters.console_ui_adapter import ConsoleUIAdapter
# ... dependency injection setup

def main():
    # Initialize adapters and core components
    version_manager = VersionManager(...)
    ui_adapter = ConsoleUIAdapter()

    # Execute version check
    result = version_manager.check_for_updates()
    ui_adapter.display_version_info(result)

    return 0 if result.is_success() else 1

if __name__ == "__main__":
    sys.exit(main())
```

**Integration Flow:**
```
User types "/nw:version" in Claude Code
  ↓
Claude Code reads ~/.claude/commands/nw/version.md
  ↓
Claude Code executes: python3 ~/.claude/nWave/cli/version_cli.py
  ↓
Python script initializes adapters and core components
  ↓
Script calls VersionManager.check_for_updates()
  ↓
Script calls ConsoleUIAdapter.display_version_info()
  ↓
Script exits with code 0 (success) or 1 (error)
```

**Acceptance Test:**
```gherkin
Scenario: User invokes /nw:version through Claude Code
  Given nWave is installed at ~/.claude/nWave/
  And version_cli.py exists at ~/.claude/nWave/cli/version_cli.py
  And command file exists at ~/.claude/commands/nw/version.md
  When user types "/nw:version" in Claude Code
  Then Claude Code executes python3 ~/.claude/nWave/cli/version_cli.py
  And the script reads ~/.claude/nwave-version.txt
  And the script calls GitHub API
  And the output shows current and latest versions
```

---

## Disaster Recovery Specification

### Catastrophic Rollback Failure Recovery

**Problem:** Automatic rollback may fail due to permission errors, disk corruption, or system state issues.

**Solution:** Pre-rollback validation + emergency restore script + comprehensive user guidance.

#### Pre-Rollback Validation

**In BackupManager.restore_from_backup():**
```python
def restore_from_backup(self, backup_path: Path) -> RestoreResult:
    """Restore from backup with comprehensive pre-flight checks."""

    # 1. Validate backup integrity
    if not self._validate_backup_checksum(backup_path):
        return RestoreResult(
            success=False,
            restored_version="unknown",
            error_message="Backup corrupted: checksum validation failed"
        )

    # 2. Check disk space for restore
    backup_size = self._calculate_directory_size(backup_path)
    if not self._check_disk_space_for_restore(backup_path.parent, backup_size):
        return RestoreResult(
            success=False,
            restored_version="unknown",
            error_message=f"Insufficient disk space for restore. Need {backup_size:.1f} MB"
        )

    # 3. Check permissions
    if not self._check_restore_permissions():
        return RestoreResult(
            success=False,
            restored_version="unknown",
            error_message="Insufficient permissions to restore installation"
        )

    # 4. Attempt restore
    try:
        # ... restore logic
    except Exception as e:
        return RestoreResult(
            success=False,
            restored_version="unknown",
            error_message=f"Restore failed: {e}"
        )
```

#### Emergency Restore Script

**Location:** `scripts/emergency_restore.py`

**Purpose:** Manually restore from backup when automatic rollback fails.

**Implementation:**
```python
#!/usr/bin/env python3
"""
Emergency restore script for catastrophic rollback failures.

Usage: python3 ~/.claude/nWave/scripts/emergency_restore.py --backup ~/.claude_bck_20260125/
"""
import argparse
import shutil
from pathlib import Path

def emergency_restore(backup_path: str) -> int:
    """
    Emergency restore from backup.

    Returns:
        0 if successful, 1 if failed
    """
    backup = Path(backup_path).expanduser()
    installation = Path.home() / ".claude"

    print(f"Emergency Restore Tool")
    print(f"======================")
    print(f"Backup: {backup}")
    print(f"Target: {installation}")
    print()

    # Validate backup exists
    if not backup.exists():
        print(f"ERROR: Backup not found at {backup}")
        return 1

    # Validate backup checksum
    manifest = backup / ".backup-manifest.json"
    if manifest.exists():
        # Validate checksum
        # ...
        pass

    # Confirm with user
    response = input("Proceed with emergency restore? This will replace your current installation. (yes/no): ")
    if response.lower() != 'yes':
        print("Restore cancelled.")
        return 0

    try:
        # Remove current installation
        if installation.exists():
            print(f"Removing current installation...")
            shutil.rmtree(installation)

        # Restore from backup
        print(f"Restoring from backup...")
        shutil.copytree(backup, installation, copy_function=shutil.copy2)

        # Verify restored version
        version_file = installation / "nwave-version.txt"
        if version_file.exists():
            restored_version = version_file.read_text().strip()
            print(f"✓ Restore successful! Version: {restored_version}")
            return 0
        else:
            print("⚠ Restore completed but VERSION file not found")
            return 1

    except Exception as e:
        print(f"ERROR: Emergency restore failed: {e}")
        return 1

def main():
    parser = argparse.ArgumentParser(description="Emergency restore from backup")
    parser.add_argument("--backup", required=True, help="Backup directory path")
    args = parser.parse_args()

    return emergency_restore(args.backup)

if __name__ == "__main__":
    exit(main())
```

#### Error Message Template

**On Rollback Failure:**
```
═══════════════════════════════════════════════════════════════
                    CRITICAL ERROR
═══════════════════════════════════════════════════════════════

Automatic rollback failed. Your nWave installation may be in an
inconsistent state.

DO NOT attempt another update until this is resolved.

RECOVERY STEPS:

Step 1: Run emergency restore script
────────────────────────────────────
python3 ~/.claude/nWave/scripts/emergency_restore.py \
  --backup {backup_path}

Step 2: If emergency restore fails, manual recovery required
─────────────────────────────────────────────────────────────
1. Backup current state:
   mv ~/.claude ~/.claude_broken

2. Restore from backup:
   mv {backup_path} ~/.claude

3. Verify installation:
   python3 -c "from pathlib import Path; \
   print(Path('~/.claude/nwave-version.txt').expanduser().read_text())"

Step 3: Report issue
────────────────────
https://github.com/swcraftsmanshipdojo/nWave/issues

Include:
- Error details: {error_message}
- Backup location: {backup_path}
- Log file: ~/.claude/nwave-update.log

═══════════════════════════════════════════════════════════════
```

---

## ADR-009: Pre-Release Version Policy

**Context:** GitHub releases may include beta, rc, or other pre-release versions. Users expect stable versions by default.

**Decision:** Only offer stable versions as updates. Filter out pre-release versions from update checks.

**Implementation:**
```python
# In VersionManager.compare_versions()
from packaging import version

def compare_versions(self, current: str, available: str) -> VersionComparison:
    """Compare versions, filtering pre-release versions."""

    available_parsed = version.parse(available)

    # Filter out pre-release versions
    if isinstance(available_parsed, version.Version) and available_parsed.is_prerelease:
        logger.info(f"Skipping pre-release version: {available}")
        return VersionComparison(
            installed=current,
            available=current,  # Treat as no update available
            is_newer=False,
            is_breaking=False,
            version_diff=VersionDiff(0, 0, 0)
        )

    # Compare stable versions only
    # ... existing comparison logic
```

**Rationale:**
- **User Expectation:** Users expect production-ready stable versions
- **Safety:** Pre-release versions may contain bugs or breaking changes
- **Opt-In:** Users must manually install pre-release versions if desired
- **Consistency:** Aligns with semantic versioning best practices

**Consequences:**
- **Positive:** Safe default behavior, production-ready updates only
- **Negative:** Power users cannot opt-in to pre-release via `/nw:update`
- **Mitigation:** Document how to manually install pre-release versions

**Alternatives Considered:**
- **Flag-based opt-in:** `--pre-release` flag - Rejected as too complex for MVP
- **Configuration option:** Rejected to avoid configuration burden
- **Show warning:** Rejected as still risky for average users

---

## NFR-001 Enhancement: Disk Space Requirements

### Update Operation Disk Space

**Requirement:** Update requires 2x current installation size

**Reason:** Full backup created before update (no compression)

**Typical Sizing:**
- nWave installation: ~100 MB
- Backup during update: ~100 MB
- **Total required:** ~200 MB available disk space

**After Update:** Backup cleanup frees space (30-day retention)

### Pre-Flight Check

**Implementation:** System validates available disk space before starting update

**Error Message on Insufficient Space:**
```
ERROR: Insufficient disk space for update

Required: 200 MB (2x installation size for safety backup)
Available: 85 MB
Shortfall: 115 MB

Update requires 2x installation size because:
1. Full backup created before any changes
2. New version downloaded and installed
3. Backup retained for 30 days (automatic cleanup)

Free up disk space and try again:
- Remove old files/downloads
- Empty trash/recycle bin
- Cleanup old backups manually: ~/.claude_bck_*
```

**Implementation in UpdateOrchestrator:**
```python
def validate_update_prerequisites(self) -> PrerequisiteCheckResult:
    """Validate prerequisites including disk space (2x requirement)."""

    failed_checks = []

    # Calculate required space (2x current installation)
    installation_path = Path.home() / ".claude"
    installation_size_mb = self._calculate_directory_size(installation_path)
    required_space_mb = installation_size_mb * 2

    # Check available space
    available_space_mb = self._get_available_disk_space(installation_path)

    if available_space_mb < required_space_mb:
        failed_checks.append(
            f"Insufficient disk space. Need {required_space_mb:.1f} MB, "
            f"found {available_space_mb:.1f} MB "
            f"(update requires 2x space for safety)"
        )

    # ... other prerequisite checks

    return PrerequisiteCheckResult(
        all_checks_passed=len(failed_checks) == 0,
        failed_checks=failed_checks
    )
```

---

## Summary

This architecture design provides a robust, maintainable, and user-friendly foundation for the Version Update Experience feature. Key strengths:

✅ **Hexagonal architecture** - Clean separation of concerns, excellent testability
✅ **Python-based CLI** - Windows-compatible, no bash scripts
✅ **Safety first** - Backup-before-change with automatic rollback + emergency recovery
✅ **Dynamic configuration** - No hardcoded URLs, works across environments
✅ **Graceful degradation** - Network failures don't crash the system
✅ **Clear user feedback** - Attention-grabbing notifications and error messages
✅ **Automated workflow** - Conventional commits → semantic-release → GitHub releases
✅ **Comprehensive error handling** - Clear guidance for all failure scenarios including catastrophic failures
✅ **Disk space transparency** - Clear 2x requirement documented and enforced

The architecture supports all 7 user stories (4 for users, 3 for creators) and meets all performance, reliability, and security requirements.

### ADR-010: Reuse Existing Installation System

**Context:**
- nWave has mature installation scripts (`install_nwave.py`, `update_nwave.py`, `install_utils.py`)
- These scripts handle backup, validation, manifest generation (500+ lines)
- Risk of duplicating battle-tested code and creating inconsistencies
- Need consistency between developer and end-user workflows

**Decision:**
- `/nw:update` acts as download orchestrator, delegates to existing installer
- Reuse `BackupManager` from `install_utils.py` (don't reimplement)
- Reuse installation validation from existing scripts
- Reuse `Logger`, `PathUtils`, `ManifestWriter` utilities
- Two workflows: Developer (update_nwave.py) vs End User (/nw:update)

**Consequences:**
- ✅ Single source of truth for installation logic
- ✅ Reduced code duplication (~500 lines saved)
- ✅ Consistency: same backup/restore behavior
- ✅ Existing installer continues working for developers
- ✅ Easier maintenance (one installation path to debug)
- ⚠️ /nw:update depends on GitHub release packaging (must include installer scripts)
- ⚠️ Download orchestrator must handle extraction and delegation correctly
- ⚠️ **CRITICAL REQUIREMENT**: GitHub release pipeline MUST package `scripts/install/` directory in releases
  - Release package structure: `nwave-{version}.tar.gz` must contain `scripts/install/install_nwave.py`
  - Verify via semantic-release configuration or manual release checklist
  - Without installer scripts, /nw:update cannot delegate installation

**Alternatives Considered:**
- **Reimplement everything:** High risk of bugs, inconsistency, maintenance burden
- **Python API for installer:** Complex refactoring, breaks existing scripts
- **Unified installer:** Doesn't address download from GitHub issue

**Trade-offs:**
- 🎯 **Simplicity:** Leveraging existing code is simpler than reimplementing
- 🎯 **Reliability:** Existing scripts are battle-tested
- ⚠️ **Release Packaging:** Requires packaging installer scripts in GitHub releases

---

**BLOCKER Fixes Applied:**
1. ✅ CLI Integration - Python-based entry points specified
2. ✅ Lock File Mechanism - Specified in component-boundaries.md (LockManager component)
3. ✅ Catastrophic Rollback Recovery - Pre-validation + emergency restore script + comprehensive guidance
4. ✅ Installation System Integration - ADR-010 added, existing installation system properly integrated

**MAJOR Fixes Applied:**
1. ✅ Disk Space Pre-Flight - Explicitly called in validate_update_prerequisites()
2. ✅ VERSION File Write - Specified in component-boundaries.md
3. ✅ Backup Directory Collision - Specified in component-boundaries.md
4. ✅ GitHub API Rate Limit - X-RateLimit-Reset parsing specified in component-boundaries.md
5. ✅ Changelog Parsing Fallback - Specified in component-boundaries.md
6. ✅ Offline Changelog Cache - Specified in component-boundaries.md
7. ✅ Pre-Release Handling - ADR-009 added
8. ✅ Disk Space Documentation - NFR-001 enhanced

**Next Wave:** DISTILL - Create acceptance tests based on this architecture
**Handoff to:** acceptance-designer (test scenarios for US-001 through US-007)

---

**Architecture Review:** Approved ✅ (Adversarial Review BLOCKERS Resolved)
**Date:** 2026-01-25
**Architect:** Morgan (Solution Architect)
