# Version Update Experience - Component Boundaries

**Feature:** Version delivery and update loop for end users
**Wave:** DESIGN
**Status:** Hexagonal architecture specification complete
**Date:** 2026-01-25
**Architect:** Morgan (Solution Architect)

---

## Hexagonal Architecture Overview

The Version Update Experience follows **Hexagonal Architecture (Ports & Adapters)** to ensure:

1. **Core business logic** isolated from external dependencies
2. **Port interfaces** define contracts between layers
3. **Adapter implementations** handle external integrations
4. **Dependency direction** flows inward (adapters depend on ports, not vice versa)

```
┌─────────────────────────────────────────────────────────────┐
│                     ADAPTER LAYER                           │
│  ┌────────────┐  ┌────────────┐  ┌─────────────────┐      │
│  │ CLI        │  │ Console UI │  │ GitHub API      │      │
│  │ Command    │  │ Adapter    │  │ Adapter         │      │
│  │ Adapter    │  │            │  │                 │      │
│  └────────────┘  └────────────┘  └─────────────────┘      │
│         │              │                   │                │
│         ▼              ▼                   ▼                │
│  ┌─────────────────────────────────────────────┐          │
│  │           PORT LAYER (Interfaces)           │          │
│  │  ┌─────────┐  ┌───────────┐  ┌──────────┐ │          │
│  │  │ Command │  │ User      │  │ Version  │ │          │
│  │  │ Port    │  │ Interact  │  │ Source   │ │          │
│  │  └─────────┘  └───────────┘  └──────────┘ │          │
│  └─────────────────────────────────────────────┘          │
│                       │                                     │
│                       ▼                                     │
│  ┌─────────────────────────────────────────────┐          │
│  │            CORE DOMAIN (Business Logic)     │          │
│  │  ┌──────────┐  ┌────────────┐  ┌─────────┐ │          │
│  │  │ Version  │  │ Update     │  │ Backup  │ │          │
│  │  │ Manager  │  │ Orchestr.  │  │ Manager │ │          │
│  │  └──────────┘  └────────────┘  └─────────┘ │          │
│  └─────────────────────────────────────────────┘          │
│         │              │                   │                │
│         ▼              ▼                   ▼                │
│  ┌─────────────────────────────────────────────┐          │
│  │           PORT LAYER (Interfaces)           │          │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐ │          │
│  │  │ File     │  │ Git      │  │ Backup   │ │          │
│  │  │ System   │  │ Config   │  │ Storage  │ │          │
│  │  └──────────┘  └──────────┘  └──────────┘ │          │
│  └─────────────────────────────────────────────┘          │
│         │              │                   │                │
│         ▼              ▼                   ▼                │
│  ┌────────────┐  ┌────────────┐  ┌─────────────────┐      │
│  │ File       │  │ Git Config │  │ Backup          │      │
│  │ System     │  │ Adapter    │  │ Storage Adapter │      │
│  │ Adapter    │  │            │  │                 │      │
│  └────────────┘  └────────────┘  └─────────────────┘      │
│                     ADAPTER LAYER                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Integration with Existing Installation System

### Architecture Principle: Reuse, Don't Duplicate

The version update feature **delegates** to the existing nWave installation system in `scripts/install/` rather than reimplementing installation logic.

**Existing Components REUSED** (from `scripts/install/install_utils.py`):
- `BackupManager` - Backup creation and restoration
- `PathUtils` - Cross-platform path utilities
- `Logger` - Structured logging with file output
- `ManifestWriter` - Installation manifest generation
- `confirm_action()` - User confirmation prompts

**Existing Scripts DELEGATED TO**:
- `install_nwave.py` - Complete installation workflow (backup, build, install, validate)
- `update_nwave.py` - Developer update workflow (build from source → uninstall → install)
- `uninstall_nwave.py` - Clean framework removal

### Component Responsibility Changes

**UpdateOrchestrator → UpdateDownloadOrchestrator** (RENAMED):
- **OLD Responsibility:** Complete update orchestration including backup, installation, validation
- **NEW Responsibility:** Download release from GitHub, extract, delegate to existing installer
- **Rationale:** Avoids duplicating 500+ lines of battle-tested installation code

**BackupManager Component** (REMOVED from new code):
- **Reason:** Already exists in `install_utils.py`
- **Usage:** Import from existing location: `from scripts.install.install_utils import BackupManager`

**FileSystemAdapter** (SIMPLIFIED):
- **Removed Methods:** `backup_directory()`, `restore_directory()` (use BackupManager instead)
- **Kept Methods:** `download_file()`, `extract_archive()`, file I/O operations

---

## Core Domain Boundaries

### 1. Version Manager

**Responsibility:** Version comparison, breaking change detection, pre-release filtering, changelog processing

**Public Interface:**
```python
class VersionManager:
    """Core business logic for version management."""

    def check_for_updates(self) -> VersionCheckResult:
        """
        Check if updates are available.

        Returns:
            VersionCheckResult with:
            - installed_version: Current version
            - available_version: Latest available version (or None if check failed)
            - update_available: Boolean
            - breaking_change: Boolean (major version bump)
            - changelog_highlights: List[str] (2-3 key points)
            - error_message: Optional error if check failed
        """

    def compare_versions(
        self,
        installed: str,
        available: str
    ) -> VersionComparison:
        """
        Compare two semantic versions, filtering pre-release versions.

        Pre-Release Filtering:
        - Skips beta, rc, alpha versions (e.g., "1.6.0-beta.1")
        - Only offers stable versions as updates
        - Power users must manually install pre-release versions

        Returns:
            VersionComparison with:
            - is_newer: Boolean (false if available is pre-release)
            - is_breaking: Boolean (major version bump)
            - version_diff: VersionDiff (major, minor, patch changes)
        """

    def detect_breaking_changes(
        self,
        installed: str,
        available: str
    ) -> bool:
        """
        Detect if update contains breaking changes.

        Breaking change = major version bump (1.x.x → 2.x.x)
        """

    def extract_changelog_highlights(
        self,
        changelog: str
    ) -> List[str]:
        """
        Extract 2-3 key highlights from changelog.

        Prioritizes:
        1. BREAKING CHANGES section (if present)
        2. Features section (feat:)
        3. Bug Fixes section (fix:)
        """
```

**Dependencies (Outbound Ports):**
- `VersionSourcePort` - Fetch installed and available versions
- `ChangelogProcessorPort` - Parse and extract highlights

**Business Rules:**
- Semantic versioning comparison (MAJOR.MINOR.PATCH)
- Breaking change = major version increase
- Highlight extraction: max 3 items, prioritize breaking changes and features
- Graceful degradation on network failure (show local version only)

**No External Dependencies:**
- No HTTP client references
- No file system references
- Pure Python logic with semantic version parsing (`packaging` library)

---

### 2. UpdateDownloadOrchestrator (RENAMED from UpdateOrchestrator)

**Responsibility:** Download release from GitHub, extract, delegate to existing installer

**Public Interface:**
```python
class UpdateDownloadOrchestrator:
    """Download coordinator that delegates to existing installer."""

    def execute_update(
        self,
        force: bool = False
    ) -> UpdateResult:
        """
        Execute update workflow by downloading and delegating to installer.

        Simplified Workflow (delegates most work):
        1. Check for updates via GitHub API
        2. Download release package from GitHub
        3. Extract release package to temporary directory
        4. DELEGATE to existing installer: python3 <extracted>/scripts/install/install_nwave.py
        5. Return result based on installer exit code

        The existing installer (install_nwave.py) handles:
        - Backup creation (via BackupManager from install_utils.py)
        - Framework validation
        - Installation
        - Manifest generation
        - Rollback (via BackupManager)

        Args:
            force: Pass through to installer via --force flag

        Returns:
            UpdateResult with:
            - success: Boolean (installer exit code == 0)
            - installed_version: Version after update
            - installer_log_path: Path to installer log
            - error_message: Optional error if download or delegation failed
        """
```

**Dependencies (Outbound Ports):**
- `VersionSourcePort` - Fetch GitHub release information
- `UserInteractionPort` - Display prompts, get confirmation BEFORE downloading
- `FileSystemPort` - Download and extract release package ONLY

**Dependencies REMOVED (delegated to installer):**
- ❌ `BackupStoragePort` - Installer handles this via BackupManager
- ❌ Validation logic - Installer handles this
- ❌ Installation logic - Installer handles this
- ❌ Rollback logic - Installer handles this

**Business Rules:**
- Check version BEFORE downloading (avoid unnecessary downloads)
- User confirmation required before download (unless force flag)
- Download to temporary directory
- Delegate to installer script (single source of truth)
- Trust installer exit code for success/failure

**State Transitions:**
```
IDLE → CHECKING_UPDATES → UPDATE_AVAILABLE
                        → NO_UPDATE_AVAILABLE (exit)

UPDATE_AVAILABLE → CREATING_BACKUP → BACKUP_CREATED
                                   → BACKUP_FAILED (abort, exit with error)

BACKUP_CREATED → CLEANING_BACKUPS → PROMPTING_USER
                                   → CLEANUP_WARNING (log, continue)

PROMPTING_USER → USER_CONFIRMED → DOWNLOADING
               → USER_CANCELLED → CLEANUP_CANCELLED_BACKUP (exit)

DOWNLOADING → INSTALLING → UPDATE_COMPLETE (success)
            → DOWNLOAD_FAILED → ROLLING_BACK
            → INSTALL_FAILED → ROLLING_BACK

ROLLING_BACK → ROLLBACK_COMPLETE (restored to pre-update state)
             → ROLLBACK_FAILED (critical error, manual intervention required)
```

---

### 3. ChangelogProcessor

**Responsibility:** Extract highlights from GitHub release notes

**Public Interface:**
```python
class ChangelogProcessor:
    """Parse changelog and extract key highlights."""

    def extract_highlights(
        self,
        changelog_markdown: str,
        max_items: int = 3
    ) -> List[str]:
        """
        Extract 2-3 key highlights from changelog.

        Args:
            changelog_markdown: Full changelog in Markdown format
            max_items: Maximum highlights to extract (default: 3)

        Returns:
            List of highlight strings (e.g., ["Add dashboard", "Fix bug"])

        Returns:
            ValidationResult with:
            - valid: Boolean
            - issues: List[str] (if any)
        """

    def restore_from_backup(
        self,
        backup_path: str
    ) -> RestoreResult:
        """
        Restore from backup with comprehensive pre-flight checks.

        Pre-Restore Validation:
        1. Validate backup integrity (checksum)
        2. Check disk space for restore operation
        3. Check permissions
        4. Attempt restore

        Args:
            backup_path: Path to backup directory

        Returns:
            RestoreResult with:
            - success: Boolean
            - restored_version: Version after restore
            - error_message: Optional error if restore failed

        Raises:
            RestoreError: If restore fails catastrophically
        """

    def determine_backup_path(
        self,
        source_path: str
    ) -> str:
        """
        Determine backup destination path with collision handling.

        Format: {source}_bck_YYYYMMDD or {source}_bck_YYYYMMDD_NN
        Example: ~/.claude_bck_20260125 or ~/.claude_bck_20260125_01

        Collision Handling:
        - If base path exists, append sequence number (_01, _02, ...)
        - Maximum 99 backups per day
        - Raises BackupError if >99 backups for single day

        Returns:
            Full path to backup directory (unique)
        """

    def find_eligible_backups_for_cleanup(
        self,
        retention_days: int = 30
    ) -> List[str]:
        """
        Find backups older than retention period.

        Args:
            retention_days: Retention period in days (default: 30)

        Returns:
            List of backup paths eligible for deletion
        """

    def cleanup_old_backups(
        self,
        retention_days: int = 30
    ) -> CleanupResult:
        """
        Delete backups older than retention period.

        Args:
            retention_days: Retention period in days (default: 30)

        Returns:
            CleanupResult with:
            - deleted_count: Number of backups deleted
            - failed_deletes: List[str] (backups that couldn't be deleted)
            - disk_space_freed_mb: Megabytes freed
        """
```

**Dependencies (Outbound Ports):**
- `BackupStoragePort` - Actual backup/restore operations
- `FileSystemPort` - Directory operations, metadata

**Business Rules:**
- Backup naming: `{source}_bck_YYYYMMDD` (ISO date format, no time)
- Retention: 30 days default (configurable via env var)
- Cleanup trigger: After successful backup creation, before update
- Preserve most recent backup regardless of age
- Non-blocking cleanup: Log warnings for locked/permission-denied directories
- Permission preservation: Maintain original file permissions in backup

**Backup Path Resolution:**
```
Source: ~/.claude/
Date: 2026-01-25
Backup: ~/.claude_bck_20260125/
```

**Cleanup Algorithm:**
```python
current_date = date.today()
backup_dirs = glob("~/.claude_bck_*")

for backup_dir in backup_dirs:
    backup_date = parse_date_from_dirname(backup_dir)  # Extract YYYYMMDD
    age_days = (current_date - backup_date).days

    if age_days > retention_days:
        try:
            delete_directory(backup_dir)
        except PermissionError:
            log_warning(f"Could not delete {backup_dir}: permission denied")
            continue  # Non-blocking
```

---

### 4. Changelog Processor

**Responsibility:** Parse GitHub release notes, extract highlights, format for display

**Public Interface:**
```python
class ChangelogProcessor:
    """Core business logic for changelog processing."""

    def extract_highlights(
        self,
        changelog: str,
        max_items: int = 3
    ) -> List[str]:
        """
        Extract key highlights from changelog with fallback for malformed content.

        Prioritization:
        1. BREAKING CHANGES section (if present)
        2. Features section (lines starting with "feat:")
        3. Bug Fixes section (lines starting with "fix:")
        4. Other sections (perf:, refactor:, etc.)

        Fallback Strategy:
        - Try structured Markdown parsing first
        - If parsing fails, extract first 3 non-empty lines
        - If no content, return ["No changelog provided"]

        Args:
            changelog: Full changelog text (GitHub release body)
            max_items: Maximum number of highlights (default: 3)

        Returns:
            List of highlight strings (2-3 items)
        """

    def parse_breaking_changes(
        self,
        changelog: str
    ) -> Optional[str]:
        """
        Extract breaking changes section from changelog.

        Looks for:
        - "BREAKING CHANGES" heading
        - "BREAKING CHANGE:" footer in conventional commits

        Returns:
            Breaking changes text or None if not present
        """

    def format_for_display(
        self,
        highlights: List[str],
        breaking_changes: Optional[str]
    ) -> str:
        """
        Format changelog for console display.

        Returns:
            Formatted string with:
            - BREAKING CHANGES section (if present, in red/bold)
            - Bulleted highlights (2-3 items)
            - Truncated to fit console width
        """
```

---

### 5. Lock Manager

**Responsibility:** Manage update process locking to prevent concurrent updates

**Public Interface:**
```python
class LockManager:
    """Core business logic for update process locking."""

    def acquire_lock(self) -> LockResult:
        """
        Acquire update lock to prevent concurrent updates.

        Lock File: ~/.claude/.nwave-update.lock
        Format: JSON with PID, timestamp, hostname, versions

        Stale Lock Detection:
        - Threshold: 2 hours (configurable via NWAVE_LOCK_TIMEOUT_HOURS)
        - On stale lock: Log warning and force release

        Returns:
            LockResult with:
            - success: Boolean
            - error_message: Optional error if lock acquisition failed
            - stale_lock_removed: Boolean (true if stale lock was removed)
        """

    def release_lock(self) -> None:
        """
        Release update lock.

        Called in finally block to ensure release even on error.
        """

    def check_stale_lock(self) -> bool:
        """
        Check if existing lock is stale (>2 hours old).

        Returns:
            True if lock exists and is stale
        """

    def force_release_lock(self) -> None:
        """
        Force release lock for emergency recovery.

        Use with caution - only for manual intervention.
        """
```

**Lock File Specification:**

**Location:** `~/.claude/.nwave-update.lock`

**Format:**
```json
{
  "pid": 12345,
  "timestamp": "2026-01-25T21:00:00Z",
  "hostname": "user-laptop",
  "version_from": "1.5.7",
  "version_to": "1.6.0"
}
```

**Stale Lock Detection:**
- **Threshold:** 2 hours (configurable via `NWAVE_LOCK_TIMEOUT_HOURS` environment variable)
- **On Stale Lock:** Log warning and force release
- **Rationale:** Update should not take >2 hours; likely indicates crashed process

**Usage in UpdateOrchestrator:**
```python
def execute_update(self):
    """Execute update with lock protection."""
    lock_result = self.lock_manager.acquire_lock()

    if not lock_result.success:
        raise ConcurrentUpdateError(lock_result.error_message)

    try:
        # ... update logic
    finally:
        self.lock_manager.release_lock()
```

**Dependencies (Outbound Ports):**
- None (pure text processing)

**Business Rules:**
- Maximum 3 highlights (avoid overwhelming user)
- Prioritize breaking changes (always show if present)
- Extract first line of commit message (ignore body)
- Remove conventional commit prefix (feat:, fix:, etc.)
- Truncate long lines to console width
- Preserve markdown links (don't expand URLs)

**Parsing Strategy:**

**Input (GitHub Release Body):**
```markdown
## What's Changed
* feat: add user dashboard by @contributor1
* fix(auth): resolve timeout issue by @contributor2
* docs: update installation guide by @contributor3

## BREAKING CHANGES
* feat!: redesign API endpoints - requires client migration

**Full Changelog**: https://github.com/.../compare/v1.5.7...v1.6.0
```

**Output (Highlights):**
```python
[
    "Redesign API endpoints (BREAKING CHANGE)",
    "Add user dashboard",
    "Resolve timeout issue"
]
```

---

## Port Layer (Interfaces)

### Inbound Ports (Primary - Driving Adapters)

#### 1. CLI Command Port

**Purpose:** Entry point for user commands (`/nw:version`, `/nw:update`)

**Interface:**
```python
from abc import ABC, abstractmethod

class CLICommandPort(ABC):
    """Interface for CLI command execution."""

    @abstractmethod
    def execute_version_check(self) -> int:
        """
        Execute /nw:version command.

        Returns:
            Exit code (0 = success, 1 = error)
        """

    @abstractmethod
    def execute_update(
        self,
        force: bool = False
    ) -> int:
        """
        Execute /nw:update command.

        Args:
            force: Skip confirmation prompt

        Returns:
            Exit code (0 = success, 1 = error, 2 = cancelled)
        """
```

**Implementation:** `CLICommandAdapter` (see Adapter Layer)

---

### Outbound Ports (Secondary - Driven Adapters)

#### 2. Version Source Port

**Purpose:** Fetch version information (local and remote)

**Interface:**
```python
from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass

@dataclass
class VersionInfo:
    version: str  # Semantic version (e.g., "1.5.7")
    source: str   # "local" or "github"

@dataclass
class ReleaseMetadata:
    version: str          # Semantic version (e.g., "1.6.0")
    tag_name: str         # Git tag (e.g., "v1.6.0")
    changelog: str        # Release notes (Markdown)
    published_at: str     # ISO 8601 datetime
    release_url: str      # GitHub release URL

class VersionSourcePort(ABC):
    """Interface for version information retrieval."""

    @abstractmethod
    def get_installed_version(self) -> VersionInfo:
        """
        Get currently installed version.

        Reads from: ~/.claude/nwave-version.txt

        Returns:
            VersionInfo with installed version
        """

    @abstractmethod
    def get_latest_release(self) -> Optional[ReleaseMetadata]:
        """
        Get latest available release from GitHub.

        Fetches from: GET /repos/{owner}/{repo}/releases/latest

        Returns:
            ReleaseMetadata or None if fetch failed
        """
```

**Implementations:**
- `LocalVersionSource` - Reads `~/.claude/nwave-version.txt` and caches changelogs
- `GitHubAPIAdapter` - Fetches from GitHub API with rate limit handling

---

#### 3. File System Port

**Purpose:** File operations (backup, restore, delete)

**Interface:**
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class BackupResult:
    success: bool
    backup_path: str
    backup_size_mb: float
    error_message: Optional[str] = None

@dataclass
class RestoreResult:
    success: bool
    restored_version: str
    error_message: Optional[str] = None

@dataclass
class DeleteResult:
    success: bool
    error_message: Optional[str] = None

class FileSystemPort(ABC):
    """Interface for file system operations."""

    @abstractmethod
    def backup_directory(
        self,
        source: str,
        destination: str
    ) -> BackupResult:
        """
        Backup directory recursively.

        Preserves:
        - File permissions
        - Timestamps
        - Directory structure

        Args:
            source: Source directory path
            destination: Destination directory path

        Returns:
            BackupResult with success status and backup path
        """

    @abstractmethod
    def restore_directory(
        self,
        backup_path: str,
        destination: str
    ) -> RestoreResult:
        """
        Restore directory from backup.

        Args:
            backup_path: Backup directory path
            destination: Restore destination path

        Returns:
            RestoreResult with success status
        """

    @abstractmethod
    def delete_directory(
        self,
        path: str
    ) -> DeleteResult:
        """
        Delete directory recursively.

        Args:
            path: Directory path to delete

        Returns:
            DeleteResult with success status
        """

    @abstractmethod
    def check_disk_space(
        self,
        path: str,
        required_mb: float
    ) -> bool:
        """
        Check if sufficient disk space available.

        Args:
            path: Path to check disk space for
            required_mb: Required space in megabytes

        Returns:
            True if sufficient space, False otherwise
        """

    @abstractmethod
    def read_version_file(
        self,
        path: str
    ) -> Optional[str]:
        """
        Read version from file.

        Args:
            path: Path to version file

        Returns:
            Version string or None if file doesn't exist
        """

    @abstractmethod
    def write_version_file(
        self,
        path: str,
        version: str
    ) -> bool:
        """
        Write version to file.

        Args:
            path: Path to version file
            version: Version string

        Returns:
            True if write succeeded, False otherwise
        """
```

**Implementation:** `FileSystemAdapter` (uses `shutil` + `pathlib`)

---

#### 4. Git Config Port

**Purpose:** Resolve repository URL from git configuration

**Interface:**
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class RepositoryInfo:
    owner: str    # GitHub owner (e.g., "swcraftsmanshipdojo")
    repo: str     # Repository name (e.g., "nWave")
    api_url: str  # API URL (e.g., "https://api.github.com/repos/...")
    web_url: str  # Web URL (e.g., "https://github.com/...")

class GitConfigPort(ABC):
    """Interface for git configuration access."""

    @abstractmethod
    def get_remote_origin_url(self) -> Optional[str]:
        """
        Get git remote origin URL.

        Executes: git config --get remote.origin.url

        Returns:
            Remote URL or None if not in git repo
        """

    @abstractmethod
    def parse_repository_info(
        self,
        git_url: str
    ) -> RepositoryInfo:
        """
        Parse GitHub owner/repo from git URL.

        Handles both formats:
        - HTTPS: https://github.com/{owner}/{repo}.git
        - SSH: git@github.com:{owner}/{repo}.git

        Args:
            git_url: Git remote URL

        Returns:
            RepositoryInfo with owner, repo, URLs

        Raises:
            ValueError if URL format not recognized
        """
```

**Implementation:** `GitConfigAdapter` (uses `subprocess` + `git` command)

---

#### 5. User Interaction Port

**Purpose:** Display information and get user input

**Interface:**
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class VersionCheckResult:
    installed_version: str
    available_version: Optional[str]
    update_available: bool
    breaking_change: bool
    changelog_highlights: List[str]
    error_message: Optional[str] = None

@dataclass
class UpdateResult:
    success: bool
    installed_version: str
    backup_path: str
    error_message: Optional[str] = None
    rollback_performed: bool = False

class UserInteractionPort(ABC):
    """Interface for user interaction."""

    @abstractmethod
    def display_version_info(
        self,
        result: VersionCheckResult
    ) -> None:
        """
        Display version check result.

        If update available:
        - Attention-grabbing banner
        - Version diff (current → available)
        - Changelog highlights (2-3 bullets)
        - Breaking change warning (if major version bump)
        - Update command hint

        If no update or error:
        - Simple message
        """

    @abstractmethod
    def display_update_banner(
        self,
        result: VersionCheckResult
    ) -> None:
        """
        Display update information before prompting.

        Shows:
        - Changelog highlights
        - Breaking change warning (if applicable)
        - Backup path
        """

    @abstractmethod
    def confirm_update(self) -> bool:
        """
        Prompt user to confirm update.

        Prompt: "Proceed with update? (Y/N)"

        Returns:
            True if user confirms (Y), False if cancelled (N)
        """

    @abstractmethod
    def display_update_summary(
        self,
        result: UpdateResult
    ) -> None:
        """
        Display update completion summary.

        Shows:
        - Updated version
        - Key changes (2-3 bullets)
        - Full changelog link
        """

    @abstractmethod
    def display_error(
        self,
        message: str,
        suggested_action: Optional[str] = None
    ) -> None:
        """
        Display error message with optional suggested action.

        Args:
            message: Error description
            suggested_action: Optional remediation guidance
        """
```

**Implementation:** `ConsoleUIAdapter` (uses `rich` library)

---

## Adapter Layer (Infrastructure)

### Inbound Adapters (Primary)

#### CLI Command Adapter (Python-Based)

**Purpose:** Implements CLI commands (`/nw:version`, `/nw:update`) as Python scripts

**Files:**
- `nWave/cli/version_cli.py` - Python entry point for `/nw:version`
- `nWave/cli/update_cli.py` - Python entry point for `/nw:update`

**Command File Integration:**
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

**Why Python (Not Bash):**
- **Windows Compatibility:** nWave must work on Windows without WSL
- **Cross-Platform:** Python 3.11+ is framework prerequisite
- **Consistent Environment:** No shell script compatibility issues
- **Error Handling:** Better error handling than bash scripts

**Implementation Pattern:**
```python
#!/usr/bin/env python3
"""Entry point for /nw:version command."""
import sys
from pathlib import Path

# Add nWave to path
sys.path.insert(0, str(Path.home() / ".claude" / "nWave"))

from nWave.core.version_manager import VersionManager
from nWave.adapters.console_ui_adapter import ConsoleUIAdapter
# ... initialize and execute

def main():
    # Dependency injection
    version_manager = VersionManager(...)
    ui_adapter = ConsoleUIAdapter()

    # Execute
    result = version_manager.check_for_updates()
    ui_adapter.display_version_info(result)

    return 0 if result.is_success() else 1

if __name__ == "__main__":
    sys.exit(main())
```

---

#### Original CLI Command Adapter

**Purpose:** Implements CLI commands (`/nw:version`, `/nw:update`)

**File:** `nWave/commands/version.py`, `nWave/commands/update.py`

**Implementation:**
```python
class VersionCommand:
    """CLI command: /nw:version"""

    def __init__(
        self,
        version_manager: VersionManager,
        ui_adapter: UserInteractionPort
    ):
        self.version_manager = version_manager
        self.ui_adapter = ui_adapter

    def execute(self) -> int:
        """Execute version check command."""
        try:
            result = self.version_manager.check_for_updates()
            self.ui_adapter.display_version_info(result)
            return 0  # Success
        except Exception as e:
            self.ui_adapter.display_error(
                message=f"Version check failed: {e}",
                suggested_action="Try again later or check manually at releases URL"
            )
            return 1  # Error

class UpdateCommand:
    """CLI command: /nw:update"""

    def __init__(
        self,
        update_orchestrator: UpdateOrchestrator,
        ui_adapter: UserInteractionPort
    ):
        self.update_orchestrator = update_orchestrator
        self.ui_adapter = ui_adapter

    def execute(self, force: bool = False) -> int:
        """Execute update command."""
        try:
            result = self.update_orchestrator.execute_update(force)

            if result.success:
                self.ui_adapter.display_update_summary(result)
                return 0  # Success
            else:
                self.ui_adapter.display_error(
                    message=result.error_message,
                    suggested_action="Check logs for details"
                )
                return 1  # Error

        except KeyboardInterrupt:
            self.ui_adapter.display_error("Update cancelled by user")
            return 2  # Cancelled
```

**Integration with nWave Command System:**
- Register commands in command registry
- Hook into existing CLI infrastructure
- Follow nWave command conventions

---

### Outbound Adapters (Secondary)

#### GitHub API Adapter

**Purpose:** Fetch release information from GitHub API

**File:** `nWave/adapters/github_adapter.py`

**Implementation:**
```python
import requests
from typing import Optional
from datetime import datetime
import time

class GitHubAPIAdapter(VersionSourcePort):
    """Adapter for GitHub API integration."""

    def __init__(
        self,
        owner: str,
        repo: str,
        timeout: int = 10
    ):
        self.owner = owner
        self.repo = repo
        self.timeout = timeout
        self.api_base = "https://api.github.com"

    def get_latest_release(self) -> Optional[ReleaseMetadata]:
        """Fetch latest release from GitHub API with rate limit handling."""
        url = f"{self.api_base}/repos/{self.owner}/{self.repo}/releases/latest"

        try:
            response = requests.get(
                url,
                headers={
                    "Accept": "application/vnd.github+json",
                    "User-Agent": "nWave-Version-Checker"
                },
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                return ReleaseMetadata(
                    version=self._extract_version(data["tag_name"]),
                    tag_name=data["tag_name"],
                    changelog=data.get("body", ""),
                    published_at=data["published_at"],
                    release_url=data["html_url"]
                )

            elif response.status_code == 404:
                # No releases found
                return None

            elif response.status_code == 429:
                # Rate limit exceeded - parse X-RateLimit-Reset header
                reset_timestamp = int(response.headers.get("X-RateLimit-Reset", 0))
                wait_seconds = max(0, reset_timestamp - int(time.time()))
                wait_minutes = wait_seconds // 60

                raise RateLimitExceeded(
                    message=f"GitHub API rate limit exceeded. Try again in {wait_minutes} minutes.",
                    reset_at=datetime.fromtimestamp(reset_timestamp),
                    retry_after_seconds=wait_seconds
                )

            else:
                # Other errors
                return None

        except requests.Timeout:
            # Network timeout
            return None

        except requests.RequestException:
            # Network error
            return None

    def _extract_version(self, tag_name: str) -> str:
        """Extract version from tag name (remove 'v' prefix)."""
        return tag_name.lstrip('v')
```

**Error Handling:**
- Network timeout (10 seconds)
- Rate limiting (HTTP 429) with X-RateLimit-Reset header parsing
- Invalid response (non-200 status)
- Connection errors

**Security:**
- HTTPS only (no HTTP fallback)
- SSL certificate validation enabled
- No API token (public repositories)

---

#### Local Version Source (with Changelog Caching)

**Purpose:** Read local version and cache changelogs for offline access

**File:** `nWave/adapters/local_version_source.py`

**Implementation:**
```python
from pathlib import Path
from typing import Optional

class LocalVersionSource:
    """Adapter for local version information and changelog caching."""

    def get_installed_version(self) -> VersionInfo:
        """Read installed version from file."""
        version_file = Path.home() / ".claude" / "nwave-version.txt"

        if version_file.exists():
            version = version_file.read_text().strip()
            return VersionInfo(version=version, source="local")
        else:
            raise VersionFileNotFound("VERSION file not found")

    def cache_changelog(self, version: str, changelog: str) -> None:
        """
        Cache changelog for offline access.

        File: ~/.claude/.nwave-changelog-{version}.txt

        Called after successful GitHub API fetch to enable
        offline graceful degradation.
        """
        cache_file = Path.home() / ".claude" / f".nwave-changelog-{version}.txt"
        cache_file.write_text(changelog)

    def get_cached_changelog(self, version: str) -> Optional[str]:
        """
        Retrieve cached changelog.

        Returns:
            Cached changelog or None if not found
        """
        cache_file = Path.home() / ".claude" / f".nwave-changelog-{version}.txt"

        if cache_file.exists():
            return cache_file.read_text()
        return None
```

**Usage in VersionManager:**
```python
def check_for_updates(self) -> VersionCheckResult:
    """Check for updates with offline changelog fallback."""

    # Try GitHub API
    try:
        release = self.github_adapter.get_latest_release()

        if release:
            # Cache changelog for offline access
            self.local_source.cache_changelog(release.version, release.changelog)
            # ... process release
    except NetworkError:
        # Fallback to cached changelog if available
        cached_changelog = self.local_source.get_cached_changelog(installed_version)
        if cached_changelog:
            # Use cached changelog for display
            # ...
```

**Benefits:**
- **Graceful Degradation:** Show version info even when GitHub API unavailable
- **Offline Capability:** Users can view changelog of current version offline
- **Reduced API Calls:** Can display cached information without API hit
- **Better UX:** Faster response when using cached data

---

#### File System Adapter

**Purpose:** Backup, restore, delete operations

**File:** `nWave/adapters/filesystem_adapter.py`

**Implementation:**
```python
import shutil
from pathlib import Path

class FileSystemAdapter(FileSystemPort):
    """Adapter for file system operations."""

    def backup_directory(
        self,
        source: str,
        destination: str
    ) -> BackupResult:
        """Backup directory using shutil.copytree with comprehensive checks."""
        try:
            source_path = Path(source).expanduser()
            dest_path = Path(destination).expanduser()

            # Check source exists
            if not source_path.exists():
                return BackupResult(
                    success=False,
                    backup_path=destination,
                    backup_size_mb=0.0,
                    error_message=f"Source directory not found: {source}"
                )

            # Check destination doesn't exist
            if dest_path.exists():
                return BackupResult(
                    success=False,
                    backup_path=destination,
                    backup_size_mb=0.0,
                    error_message=f"Backup destination already exists: {destination}"
                )

            # EXPLICIT: Check disk space (2x requirement enforced)
            required_mb = self._calculate_directory_size(source_path)
            available_mb = self._get_available_disk_space(dest_path.parent)

            if available_mb < required_mb:
                return BackupResult(
                    success=False,
                    backup_path=destination,
                    backup_size_mb=0.0,
                    error_message=f"Insufficient disk space. Need {required_mb:.1f} MB, found {available_mb:.1f} MB"
                )

            # Perform backup
            shutil.copytree(
                source_path,
                dest_path,
                copy_function=shutil.copy2,  # Preserve metadata
                ignore_dangling_symlinks=True,
                dirs_exist_ok=False
            )

            # Calculate and create checksum manifest
            backup_size = self._calculate_directory_size(dest_path)
            checksum = self._calculate_directory_checksum(dest_path)

            # Write backup manifest with checksum
            manifest_file = dest_path / ".backup-manifest.json"
            manifest = {
                "source": str(source_path),
                "destination": str(dest_path),
                "created_at": datetime.now().isoformat(),
                "checksum_sha256": checksum,
                "backup_size_mb": backup_size
            }
            manifest_file.write_text(json.dumps(manifest, indent=2))

            return BackupResult(
                success=True,
                backup_path=str(dest_path),
                backup_size_mb=backup_size
            )

        except PermissionError as e:
            return BackupResult(
                success=False,
                backup_path=destination,
                backup_size_mb=0.0,
                error_message=f"Permission denied: {e}"
            )

        except OSError as e:
            return BackupResult(
                success=False,
                backup_path=destination,
                backup_size_mb=0.0,
                error_message=f"File system error: {e}"
            )

    def restore_directory(
        self,
        backup_path: str,
        destination: str
    ) -> RestoreResult:
        """Restore directory from backup with pre-flight validation."""
        try:
            backup = Path(backup_path).expanduser()
            dest = Path(destination).expanduser()

            # 1. Validate backup integrity (checksum)
            manifest_file = backup / ".backup-manifest.json"
            if manifest_file.exists():
                manifest = json.loads(manifest_file.read_text())
                stored_checksum = manifest.get("checksum_sha256")
                actual_checksum = self._calculate_directory_checksum(backup)

                if stored_checksum != actual_checksum:
                    return RestoreResult(
                        success=False,
                        restored_version="unknown",
                        error_message="Backup corrupted: checksum validation failed"
                    )

            # 2. Check disk space for restore
            backup_size_mb = self._calculate_directory_size(backup)
            available_mb = self._get_available_disk_space(dest.parent)

            if available_mb < backup_size_mb:
                return RestoreResult(
                    success=False,
                    restored_version="unknown",
                    error_message=f"Insufficient disk space for restore. Need {backup_size_mb:.1f} MB, found {available_mb:.1f} MB"
                )

            # 3. Check permissions
            if not self._check_write_permissions(dest.parent):
                return RestoreResult(
                    success=False,
                    restored_version="unknown",
                    error_message=f"Insufficient permissions to restore to {dest}"
                )

            # 4. Attempt restore
            # Remove current installation
            if dest.exists():
                shutil.rmtree(dest)

            # Restore from backup
            shutil.copytree(
                backup,
                dest,
                copy_function=shutil.copy2,
                ignore_dangling_symlinks=True
            )

            # Read restored version
            version_file = dest / "nwave-version.txt"
            if version_file.exists():
                restored_version = version_file.read_text().strip()
            else:
                restored_version = "unknown"

            return RestoreResult(
                success=True,
                restored_version=restored_version
            )

        except Exception as e:
            return RestoreResult(
                success=False,
                restored_version="unknown",
                error_message=f"Restore failed: {e}"
            )

    def _get_available_disk_space(self, path: Path) -> float:
        """Get available disk space in megabytes."""
        import shutil as shutil_disk
        stat = shutil_disk.disk_usage(path)
        return stat.free / (1024 * 1024)

    def _calculate_directory_checksum(self, path: Path) -> str:
        """Calculate SHA-256 checksum of directory contents."""
        import hashlib

        hasher = hashlib.sha256()
        for file_path in sorted(path.rglob('*')):
            if file_path.is_file():
                hasher.update(file_path.read_bytes())

        return hasher.hexdigest()

    def _check_write_permissions(self, path: Path) -> bool:
        """Check if we have write permissions to path."""
        import os
        return os.access(path, os.W_OK)

    def _calculate_directory_size(self, path: Path) -> float:
        """Calculate directory size in megabytes."""
        total_size = sum(
            f.stat().st_size
            for f in path.rglob('*')
            if f.is_file()
        )
        return total_size / (1024 * 1024)  # Convert to MB
```

**Cross-Platform Compatibility:**
- Uses `pathlib.Path` for path handling
- `expanduser()` for `~` expansion
- `shutil.copy2` preserves permissions on all platforms

---

#### Git Config Adapter

**Purpose:** Resolve repository URL from git config

**File:** `nWave/adapters/git_config_adapter.py`

**Implementation:**
```python
import subprocess
import re
from typing import Optional

class GitConfigAdapter(GitConfigPort):
    """Adapter for git configuration access."""

    def get_remote_origin_url(self) -> Optional[str]:
        """Execute git config command to get remote URL."""
        try:
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return None

        except FileNotFoundError:
            # Git not installed
            return None

        except subprocess.TimeoutExpired:
            # Git hung (rare)
            return None

    def parse_repository_info(self, git_url: str) -> RepositoryInfo:
        """Parse GitHub owner/repo from git URL."""
        # HTTPS: https://github.com/{owner}/{repo}.git
        https_match = re.match(
            r'https://github\.com/([^/]+)/([^/]+?)(?:\.git)?$',
            git_url
        )
        if https_match:
            owner, repo = https_match.group(1), https_match.group(2)
            return self._create_repo_info(owner, repo)

        # SSH: git@github.com:{owner}/{repo}.git
        ssh_match = re.match(
            r'git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$',
            git_url
        )
        if ssh_match:
            owner, repo = ssh_match.group(1), ssh_match.group(2)
            return self._create_repo_info(owner, repo)

        raise ValueError(f"Unrecognized GitHub URL format: {git_url}")

    def _create_repo_info(self, owner: str, repo: str) -> RepositoryInfo:
        """Create RepositoryInfo with URLs."""
        return RepositoryInfo(
            owner=owner,
            repo=repo,
            api_url=f"https://api.github.com/repos/{owner}/{repo}",
            web_url=f"https://github.com/{owner}/{repo}"
        )
```

**URL Format Support:**
- HTTPS: `https://github.com/swcraftsmanshipdojo/nWave.git`
- SSH: `git@github.com:swcraftsmanshipdojo/nWave.git`
- With or without `.git` suffix

---

#### Console UI Adapter

**Purpose:** Format output for terminal using `rich` library

**File:** `nWave/adapters/console_ui_adapter.py`

**Implementation:**
```python
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Confirm

class ConsoleUIAdapter(UserInteractionPort):
    """Adapter for console UI using rich library."""

    def __init__(self):
        self.console = Console()

    def display_version_info(self, result: VersionCheckResult) -> None:
        """Display version check result."""
        if result.error_message:
            # Network failure - show local version only
            self.console.print(f"nWave v{result.installed_version} (installed)")
            self.console.print(
                f"[yellow]⚠️  {result.error_message}[/yellow]"
            )
            return

        if not result.update_available:
            # Up to date
            self.console.print(
                f"[green]✓[/green] nWave v{result.installed_version} (up to date)"
            )
            return

        # Update available - attention-grabbing banner
        table = Table(
            title="Update Available",
            show_header=True,
            header_style="bold magenta"
        )
        table.add_column("Attribute", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Current version", result.installed_version)
        table.add_row("Available update", result.available_version)

        # Breaking change warning
        if result.breaking_change:
            table.add_row(
                "[bold red]⚠️  BREAKING CHANGES[/bold red]",
                "[bold red]This is a major version update[/bold red]"
            )

        # Changelog highlights
        highlights_text = "\n".join(
            f"• {item}" for item in result.changelog_highlights
        )
        table.add_row("Changelog highlights", highlights_text)

        # Update command
        table.add_row("Update command", "[bold]/nw:update[/bold]")

        panel = Panel(table, border_style="bold red", title="nWave Update")
        self.console.print(panel)

    def confirm_update(self) -> bool:
        """Prompt user to confirm update."""
        return Confirm.ask("Proceed with update?", default=False)

    def display_error(
        self,
        message: str,
        suggested_action: Optional[str] = None
    ) -> None:
        """Display error message."""
        self.console.print(f"[bold red]Error:[/bold red] {message}")
        if suggested_action:
            self.console.print(f"[yellow]→[/yellow] {suggested_action}")
```

**Visual Design:**
- **Attention-grabbing banners:** Colored borders, bold text
- **Breaking change warnings:** Red/bold "⚠️  BREAKING CHANGES"
- **Clear hierarchy:** Tables for structured information
- **Color coding:** Green (success), Yellow (warning), Red (error)

---

## Dependency Flow Rules

**Hexagonal Architecture Principle:** Dependencies point inward

```
Adapters → Ports → Core Domain
(depend on)  (implement/use)  (pure business logic)
```

**Forbidden Dependencies:**
- ❌ Core Domain → Adapters (business logic cannot reference infrastructure)
- ❌ Core Domain → External Libraries (except pure utilities like `packaging`)
- ❌ Ports → Adapters (interfaces cannot reference implementations)

**Allowed Dependencies:**
- ✅ Adapters → Ports (implementations depend on interfaces)
- ✅ Core Domain → Ports (business logic uses port interfaces)
- ✅ Adapters → External Libraries (`requests`, `shutil`, `subprocess`)

**Dependency Injection:**
```python
# Composition root (dependency injection)
def create_version_command():
    # Adapters
    git_config_adapter = GitConfigAdapter()
    repo_info = git_config_adapter.parse_repository_info(
        git_config_adapter.get_remote_origin_url()
    )
    github_adapter = GitHubAPIAdapter(repo_info.owner, repo_info.repo)
    local_version_source = LocalVersionSource()
    console_ui_adapter = ConsoleUIAdapter()

    # Core domain
    changelog_processor = ChangelogProcessor()
    version_manager = VersionManager(
        installed_version_source=local_version_source,
        remote_version_source=github_adapter,
        changelog_processor=changelog_processor
    )

    # Command
    return VersionCommand(version_manager, console_ui_adapter)
```

---

## Component Interaction Protocols

See `architecture-design.md` for detailed sequence diagrams of:
- Version check flow
- Update flow
- Rollback flow

---

## Testing Strategy

### Unit Testing (Core Domain)

**No External Dependencies:**
```python
def test_version_manager_detect_breaking_changes():
    version_manager = VersionManager(
        installed_version_source=MockVersionSource("1.5.7"),
        remote_version_source=MockVersionSource("2.0.0"),
        changelog_processor=MockChangelogProcessor()
    )

    is_breaking = version_manager.detect_breaking_changes("1.5.7", "2.0.0")

    assert is_breaking is True
```

### Integration Testing (Adapters)

**Test with Real Dependencies:**
```python
def test_github_adapter_integration():
    """Test against actual GitHub API."""
    adapter = GitHubAPIAdapter("swcraftsmanshipdojo", "nWave")
    release = adapter.get_latest_release()

    assert release is not None
    assert release.version matches semver pattern
```

### End-to-End Testing

**Full Command Execution:**
```python
def test_version_command_e2e():
    """Test complete version check command."""
    command = create_version_command()  # Full dependency injection
    exit_code = command.execute()

    assert exit_code == 0  # Success
```

---

## Enhanced Implementation Details

### Update Orchestrator Implementation

**Comprehensive Update Workflow:**
```python
def execute_update(self, force: bool = False) -> UpdateResult:
    """Execute update with full safety and validation."""

    previous_version = self.version_source.get_installed_version().version

    # Step 1: Acquire lock
    lock_result = self.lock_manager.acquire_lock()
    if not lock_result.success:
        raise ConcurrentUpdateError(lock_result.error_message)

    try:
        # Step 2: Check for updates
        check_result = self.version_manager.check_for_updates()
        if not check_result.update_available:
            return UpdateResult(
                success=True,
                installed_version=previous_version,
                previous_version=previous_version,
                backup_path="",
                error_message="Already up to date"
            )

        new_version = check_result.available_version

        # Step 3: Validate prerequisites (EXPLICIT DISK SPACE CHECK)
        prereq_result = self.validate_update_prerequisites()
        if not prereq_result.all_checks_passed:
            raise UpdatePrerequisiteError(prereq_result.summary())

        # Step 4: Create backup
        backup_result = self.backup_manager.create_backup(
            source_path=str(Path.home() / ".claude")
        )
        if not backup_result.success:
            raise BackupError(backup_result.error_message)

        backup_path = backup_result.backup_path

        # Step 5: Cleanup old backups (non-blocking)
        self.backup_manager.cleanup_old_backups(retention_days=30)

        # Step 6: Prompt user (unless force=True)
        if not force:
            confirmed = self.ui_adapter.confirm_update()
            if not confirmed:
                # Delete backup if user cancels
                self.file_system.delete_directory(backup_path)
                return UpdateResult(
                    success=False,
                    installed_version=previous_version,
                    previous_version=previous_version,
                    backup_path=backup_path,
                    error_message="Update cancelled by user"
                )

        # Step 7: Download and install new version
        try:
            self._download_and_install(new_version)

            # Step 8: EXPLICIT VERSION FILE UPDATE
            version_file = Path.home() / ".claude" / "nwave-version.txt"
            try:
                version_file.write_text(new_version)
            except Exception as e:
                # VERSION file write is CRITICAL - rollback if it fails
                logger.error(f"Failed to write VERSION file: {e}")
                self.backup_manager.restore_from_backup(backup_path)
                raise VersionFileUpdateError(
                    f"Update failed: Could not update VERSION file. Restored from backup."
                )

            # Success
            return UpdateResult(
                success=True,
                installed_version=new_version,
                previous_version=previous_version,
                backup_path=backup_path
            )

        except Exception as e:
            # Automatic rollback on any failure
            logger.error(f"Update failed: {e}. Rolling back...")
            restore_result = self.backup_manager.restore_from_backup(backup_path)

            if not restore_result.success:
                # CATASTROPHIC: Rollback failed
                raise RollbackFailureError(
                    f"Update failed AND rollback failed: {restore_result.error_message}\n"
                    f"Backup location: {backup_path}\n"
                    f"See emergency recovery instructions."
                )

            return UpdateResult(
                success=False,
                installed_version=previous_version,
                previous_version=previous_version,
                backup_path=backup_path,
                error_message=str(e),
                rollback_performed=True
            )

    finally:
        # Always release lock
        self.lock_manager.release_lock()

def validate_update_prerequisites(self) -> PrerequisiteCheckResult:
    """Validate prerequisites with EXPLICIT 2x disk space check."""

    failed_checks = []

    # EXPLICIT: Check disk space (2x current installation)
    installation_path = Path.home() / ".claude"
    installation_size_mb = self.file_system.get_directory_size(installation_path)
    required_space_mb = installation_size_mb * 2

    available_space_mb = self.file_system.check_disk_space(installation_path)

    if available_space_mb < required_space_mb:
        failed_checks.append(
            f"Insufficient disk space. Need {required_space_mb:.1f} MB, "
            f"found {available_space_mb:.1f} MB (update requires 2x space for safety)"
        )

    # Check write permissions
    if not self.file_system.check_write_permissions(installation_path):
        failed_checks.append(f"Write permission denied for {installation_path}")

    # Check lock file
    if self.lock_manager.check_existing_lock():
        failed_checks.append("Another update is in progress")

    return PrerequisiteCheckResult(
        all_checks_passed=len(failed_checks) == 0,
        failed_checks=failed_checks
    )
```

### Backup Manager Implementation - Collision Handling

**Backup Path Determination with Collision Handling:**
```python
def determine_backup_path(self, source_path: str) -> str:
    """Determine backup path with collision handling."""

    base_date = datetime.now().strftime("%Y%m%d")
    base_path = Path(f"~/.claude_bck_{base_date}").expanduser()

    # Handle collision: append sequence number
    if base_path.exists():
        sequence = 1
        while True:
            candidate = Path(f"~/.claude_bck_{base_date}_{sequence:02d}").expanduser()
            if not candidate.exists():
                return str(candidate)
            sequence += 1
            if sequence > 99:
                raise BackupError(
                    "Too many backups for today (>99). "
                    "Cleanup old backups manually: ~/.claude_bck_*"
                )

    return str(base_path)
```

**Backup Manifest Parsing (both formats):**
```python
@staticmethod
def from_backup_path(backup_path: str, version: str) -> BackupManifest:
    """Create manifest from backup path, handling both formats."""
    import re

    # Parse: ~/.claude_bck_20260125 or ~/.claude_bck_20260125_01
    match = re.match(r".*_bck_(\d{8})(?:_(\d{2}))?", backup_path)

    if match:
        date_str = match.group(1)
        sequence = match.group(2) or "00"
        created_at = datetime.strptime(date_str, "%Y%m%d")

        # Calculate metrics
        path = Path(backup_path).expanduser()
        # ... rest of implementation
```

---

## Summary

This component boundaries specification provides:

✅ **Clear Separation:** Core domain, ports, adapters
✅ **Hexagonal Architecture:** Dependencies point inward
✅ **Port Interfaces:** Well-defined contracts between layers
✅ **Adapter Implementations:** Concrete integrations with external systems
✅ **Python-Based CLI:** Windows-compatible entry points (no bash)
✅ **Dependency Injection:** Composition at application root
✅ **Testability:** Core domain testable without external dependencies
✅ **Flexibility:** Easy to swap adapter implementations
✅ **Safety Features:** Lock management, pre-flight checks, explicit VERSION file updates
✅ **Collision Handling:** Backup directory naming with sequence numbers
✅ **Integrity Checks:** Checksums for backup validation
✅ **Graceful Degradation:** Offline changelog caching
✅ **Comprehensive Error Handling:** Pre-validation for catastrophic rollback prevention

**Component Count:**
- **Core Domain:** 3 components (Version Manager, UpdateDownloadOrchestrator [renamed], Changelog Processor)
  - ❌ BackupManager REMOVED - Use existing from scripts/install/install_utils.py
  - ✅ LockManager ADDED - For concurrency control (prevents simultaneous updates)
- **Ports:** 3 interfaces (CLI Command, Version Source, User Interaction)
  - ❌ File System, Git Config, Backup Storage REMOVED - Handled by existing installer
- **Adapters:** 4 implementations (Python CLI, GitHub API, Local Version Source, Console UI)
  - ❌ File System Adapter backup methods REMOVED - Use existing BackupManager
  - ❌ Git Config Adapter KEPT - Still needed for repository URL resolution

**BLOCKER Fixes Applied:**
1. ✅ CLI Integration - Python-based entry points specified
2. ✅ Lock File Mechanism - LockManager component with JSON-based lock files and stale detection
3. ✅ Catastrophic Rollback Recovery - Delegated to existing installer's backup/restore
4. ✅ Installation System Integration - UpdateDownloadOrchestrator delegates to install_nwave.py

**MAJOR Fixes Applied:**
1. ✅ Simplified Component Boundaries - Removed duplicate backup/restore/validation components
2. ✅ Single Source of Truth - Installation logic in existing scripts only
3. ✅ Delegation Model - Download orchestrator calls existing installer
4. ✅ Reduced Code Duplication - ~500 lines of installation code NOT reimplemented

**Next Wave:** DISTILL - Create acceptance tests targeting port interfaces

---

**Component Boundaries:** Approved ✅ (Adversarial Review BLOCKERS Resolved)
**Date:** 2026-01-25
**Architect:** Morgan (Solution Architect)
