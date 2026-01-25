# Version Update Experience - Data Models

**Feature:** Version delivery and update loop for end users
**Wave:** DESIGN
**Status:** Domain models and data structures complete
**Date:** 2026-01-25
**Architect:** Morgan (Solution Architect)

---

## Overview

This document defines all domain models and data structures used in the Version Update Experience feature. Models are designed to be:

1. **Immutable where possible** - Use `@dataclass(frozen=True)` for value objects
2. **Type-safe** - Comprehensive type annotations
3. **Self-documenting** - Clear field names and docstrings
4. **Validation-aware** - Include validation methods where appropriate
5. **Serializable** - Support JSON serialization for logging/debugging

---

## Domain Models (Core Business Objects)

### 1. VersionInfo

**Purpose:** Represents version information (installed or available)

**Definition:**
```python
from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class VersionInfo:
    """
    Version information with source tracking.

    Attributes:
        version: Semantic version string (e.g., "1.5.7")
        source: Where version came from ("local", "github", "cache")
    """
    version: str
    source: Literal["local", "github", "cache"]

    def __post_init__(self):
        """Validate version format."""
        if not self._is_valid_semver(self.version):
            raise ValueError(f"Invalid semantic version: {self.version}")

    @staticmethod
    def _is_valid_semver(version: str) -> bool:
        """Check if version matches semantic versioning format."""
        import re
        pattern = r'^\d+\.\d+\.\d+(?:-[\w.]+)?(?:\+[\w.]+)?$'
        return bool(re.match(pattern, version))

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "version": self.version,
            "source": self.source
        }
```

**Example Usage:**
```python
installed = VersionInfo(version="1.5.7", source="local")
available = VersionInfo(version="1.6.0", source="github")
```

**Validation Rules:**
- Version must match semantic versioning format (MAJOR.MINOR.PATCH)
- Optional pre-release suffix (e.g., "1.6.0-beta.1")
- Optional build metadata (e.g., "1.6.0+20241201")

---

### 2. ReleaseMetadata

**Purpose:** Complete metadata for a GitHub release

**Definition:**
```python
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class ReleaseMetadata:
    """
    GitHub release metadata.

    Attributes:
        version: Semantic version (without 'v' prefix)
        tag_name: Git tag name (e.g., "v1.6.0")
        changelog: Release notes in Markdown format
        published_at: Release publication datetime (ISO 8601)
        release_url: GitHub release page URL
    """
    version: str
    tag_name: str
    changelog: str
    published_at: str  # ISO 8601 datetime string
    release_url: str

    def get_published_datetime(self) -> datetime:
        """Parse published_at as datetime object."""
        return datetime.fromisoformat(self.published_at.replace('Z', '+00:00'))

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "version": self.version,
            "tag_name": self.tag_name,
            "changelog": self.changelog,
            "published_at": self.published_at,
            "release_url": self.release_url
        }
```

**Example Usage:**
```python
release = ReleaseMetadata(
    version="1.6.0",
    tag_name="v1.6.0",
    changelog="## What's Changed\n* feat: add dashboard\n* fix: resolve bug",
    published_at="2026-01-20T14:32:15Z",
    release_url="https://github.com/swcraftsmanshipdojo/nWave/releases/tag/v1.6.0"
)
```

---

### 3. VersionComparison

**Purpose:** Result of comparing two versions

**Definition:**
```python
from dataclasses import dataclass
from typing import Tuple

@dataclass(frozen=True)
class VersionDiff:
    """
    Difference between two versions.

    Attributes:
        major: Change in major version (e.g., 1 → 2 = +1)
        minor: Change in minor version
        patch: Change in patch version
    """
    major: int
    minor: int
    patch: int

    def is_major_bump(self) -> bool:
        """Check if major version increased."""
        return self.major > 0

    def is_minor_bump(self) -> bool:
        """Check if minor version increased (no major bump)."""
        return self.major == 0 and self.minor > 0

    def is_patch_bump(self) -> bool:
        """Check if only patch version increased."""
        return self.major == 0 and self.minor == 0 and self.patch > 0

@dataclass(frozen=True)
class VersionComparison:
    """
    Comparison result for two versions.

    Attributes:
        installed: Installed version string
        available: Available version string
        is_newer: True if available > installed
        is_breaking: True if major version increased (breaking change)
        version_diff: Difference breakdown (major, minor, patch)
    """
    installed: str
    available: str
    is_newer: bool
    is_breaking: bool
    version_diff: VersionDiff

    def summary(self) -> str:
        """Human-readable summary of comparison."""
        if not self.is_newer:
            return f"Already running latest version ({self.installed})"

        if self.is_breaking:
            return f"Breaking change update available: {self.installed} → {self.available}"

        return f"Update available: {self.installed} → {self.available}"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "installed": self.installed,
            "available": self.available,
            "is_newer": self.is_newer,
            "is_breaking": self.is_breaking,
            "version_diff": {
                "major": self.version_diff.major,
                "minor": self.version_diff.minor,
                "patch": self.version_diff.patch
            }
        }
```

**Example Usage:**
```python
comparison = VersionComparison(
    installed="1.5.7",
    available="2.0.0",
    is_newer=True,
    is_breaking=True,
    version_diff=VersionDiff(major=1, minor=-5, patch=-7)
)

print(comparison.summary())
# Output: "Breaking change update available: 1.5.7 → 2.0.0"
```

---

### 4. RepositoryInfo

**Purpose:** GitHub repository information resolved from git config

**Definition:**
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class RepositoryInfo:
    """
    GitHub repository information.

    Attributes:
        owner: GitHub owner/organization (e.g., "swcraftsmanshipdojo")
        repo: Repository name (e.g., "nWave")
        api_url: GitHub API URL for releases
        web_url: GitHub web URL for releases page
    """
    owner: str
    repo: str
    api_url: str
    web_url: str

    @classmethod
    def from_git_url(cls, git_url: str) -> 'RepositoryInfo':
        """
        Parse GitHub URL to extract owner/repo.

        Supports:
        - HTTPS: https://github.com/{owner}/{repo}.git
        - SSH: git@github.com:{owner}/{repo}.git

        Args:
            git_url: Git remote URL

        Returns:
            RepositoryInfo with parsed owner and repo

        Raises:
            ValueError: If URL format not recognized
        """
        import re

        # HTTPS format
        https_match = re.match(
            r'https://github\.com/([^/]+)/([^/]+?)(?:\.git)?$',
            git_url
        )
        if https_match:
            owner, repo = https_match.group(1), https_match.group(2)
            return cls._create(owner, repo)

        # SSH format
        ssh_match = re.match(
            r'git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$',
            git_url
        )
        if ssh_match:
            owner, repo = ssh_match.group(1), ssh_match.group(2)
            return cls._create(owner, repo)

        raise ValueError(f"Unrecognized GitHub URL format: {git_url}")

    @classmethod
    def _create(cls, owner: str, repo: str) -> 'RepositoryInfo':
        """Create RepositoryInfo with computed URLs."""
        return cls(
            owner=owner,
            repo=repo,
            api_url=f"https://api.github.com/repos/{owner}/{repo}",
            web_url=f"https://github.com/{owner}/{repo}"
        )

    def releases_url(self) -> str:
        """Get URL for releases page."""
        return f"{self.web_url}/releases"

    def latest_release_api_url(self) -> str:
        """Get GitHub API URL for latest release."""
        return f"{self.api_url}/releases/latest"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "owner": self.owner,
            "repo": self.repo,
            "api_url": self.api_url,
            "web_url": self.web_url
        }
```

**Example Usage:**
```python
# From HTTPS URL
repo_info = RepositoryInfo.from_git_url(
    "https://github.com/swcraftsmanshipdojo/nWave.git"
)

# From SSH URL
repo_info = RepositoryInfo.from_git_url(
    "git@github.com:swcraftsmanshipdojo/nWave.git"
)

print(repo_info.latest_release_api_url())
# Output: "https://api.github.com/repos/swcraftsmanshipdojo/nWave/releases/latest"
```

---

## Result Objects (Operation Outcomes)

### 5. VersionCheckResult

**Purpose:** Result of version check operation

**Definition:**
```python
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class VersionCheckResult:
    """
    Result of version check operation.

    Attributes:
        installed_version: Currently installed version
        available_version: Latest available version (None if check failed)
        update_available: True if newer version available
        breaking_change: True if major version bump detected
        changelog_highlights: Key changes (2-3 items)
        error_message: Optional error if check failed
    """
    installed_version: str
    available_version: Optional[str]
    update_available: bool
    breaking_change: bool
    changelog_highlights: List[str]
    error_message: Optional[str] = None

    def is_success(self) -> bool:
        """Check if version check succeeded."""
        return self.error_message is None

    def has_update(self) -> bool:
        """Check if update is available."""
        return self.update_available and self.available_version is not None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "installed_version": self.installed_version,
            "available_version": self.available_version,
            "update_available": self.update_available,
            "breaking_change": self.breaking_change,
            "changelog_highlights": self.changelog_highlights,
            "error_message": self.error_message
        }
```

**Example Usage:**
```python
# Successful check with update available
result = VersionCheckResult(
    installed_version="1.5.7",
    available_version="1.6.0",
    update_available=True,
    breaking_change=False,
    changelog_highlights=[
        "Add user dashboard",
        "Fix authentication timeout",
        "Improve performance by 40%"
    ]
)

# Network failure
result = VersionCheckResult(
    installed_version="1.5.7",
    available_version=None,
    update_available=False,
    breaking_change=False,
    changelog_highlights=[],
    error_message="Could not check for updates. Try again later."
)
```

---

### 6. UpdateResult (SIMPLIFIED - delegates to installer)

**Purpose:** Result of update operation (simplified for delegation model)

**Definition:**
```python
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

@dataclass
class UpdateResult:
    """
    Result of update operation (delegated to installer).

    Attributes:
        success: True if installer completed successfully (exit code 0)
        version: Version after update (None if failed)
        error_message: Optional error if update failed
        installer_log_path: Path to installer log file
    """
    success: bool
    version: Optional[str] = None
    error_message: Optional[str] = None
    installer_log_path: Optional[Path] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "success": self.success,
            "version": self.version,
            "error_message": self.error_message,
            "installer_log_path": str(self.installer_log_path) if self.installer_log_path else None
        }
```

**Note:** Backup, restore, and cleanup results are handled by the existing installer's BackupManager, not exposed here.

---

### 7. PrerequisiteCheckResult

**Purpose:** Result of update prerequisite validation

**Definition:**
```python
from dataclasses import dataclass
from typing import List

@dataclass
class PrerequisiteCheckResult:
    """
    Result of prerequisite validation.

    Attributes:
        all_checks_passed: True if all prerequisites met
        failed_checks: List of failed check descriptions
    """
    all_checks_passed: bool
    failed_checks: List[str]

    def is_ready_for_update(self) -> bool:
        """Check if ready to proceed with update."""
        return self.all_checks_passed

    def summary(self) -> str:
        """Human-readable summary of prerequisite checks."""
        if self.all_checks_passed:
            return "All prerequisites met. Ready to update."

        return f"Prerequisites not met: {', '.join(self.failed_checks)}"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "all_checks_passed": self.all_checks_passed,
            "failed_checks": self.failed_checks
        }
```

**Example Usage:**
```python
# All checks passed
result = PrerequisiteCheckResult(
    all_checks_passed=True,
    failed_checks=[]
)

# Failed checks
result = PrerequisiteCheckResult(
    all_checks_passed=False,
    failed_checks=[
        "Insufficient disk space (need 50 MB, found 10 MB)",
        "Write permission denied for ~/.claude/"
    ]
)
```

---

## Configuration Objects

### 12. UpdateConfig

**Purpose:** Configuration for update operations

**Definition:**
```python
from dataclasses import dataclass
import os

@dataclass
class UpdateConfig:
    """
    Configuration for update operations.

    Attributes:
        backup_retention_days: Days to keep backups before cleanup
        github_api_timeout: GitHub API request timeout in seconds
        log_level: Logging level (INFO, DEBUG, WARN, ERROR)
        force_update: Skip confirmation prompts
    """
    backup_retention_days: int = 30
    github_api_timeout: int = 10
    log_level: str = "INFO"
    force_update: bool = False

    @classmethod
    def from_environment(cls) -> 'UpdateConfig':
        """
        Load configuration from environment variables.

        Environment variables:
        - NWAVE_BACKUP_RETENTION_DAYS: Backup retention period (default: 30)
        - NWAVE_GITHUB_API_TIMEOUT: GitHub API timeout (default: 10)
        - NWAVE_UPDATE_LOG_LEVEL: Logging level (default: INFO)
        """
        return cls(
            backup_retention_days=int(
                os.getenv('NWAVE_BACKUP_RETENTION_DAYS', '30')
            ),
            github_api_timeout=int(
                os.getenv('NWAVE_GITHUB_API_TIMEOUT', '10')
            ),
            log_level=os.getenv('NWAVE_UPDATE_LOG_LEVEL', 'INFO').upper()
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "backup_retention_days": self.backup_retention_days,
            "github_api_timeout": self.github_api_timeout,
            "log_level": self.log_level,
            "force_update": self.force_update
        }
```

**Example Usage:**
```python
# Load from environment variables
config = UpdateConfig.from_environment()

# Override specific settings
config = UpdateConfig(
    backup_retention_days=60,  # Keep backups for 60 days
    force_update=True  # Skip confirmation
)
```

---

## Exception Types

### 13. LockInfo and LockResult

**Purpose:** Lock file information and acquisition results

**Definition:**
```python
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class LockInfo:
    """
    Lock file information.

    Attributes:
        pid: Process ID that acquired lock
        timestamp: ISO 8601 timestamp when lock was acquired
        hostname: Hostname of machine that acquired lock
        version_from: Version being upgraded from
        version_to: Version being upgraded to
    """
    pid: int
    timestamp: str  # ISO 8601
    hostname: str
    version_from: str
    version_to: str

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "pid": self.pid,
            "timestamp": self.timestamp,
            "hostname": self.hostname,
            "version_from": self.version_from,
            "version_to": self.version_to
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'LockInfo':
        """Create from dictionary (JSON deserialization)."""
        return cls(
            pid=data["pid"],
            timestamp=data["timestamp"],
            hostname=data["hostname"],
            version_from=data["version_from"],
            version_to=data["version_to"]
        )

@dataclass(frozen=True)
class LockResult:
    """
    Result of lock acquisition attempt.

    Attributes:
        success: Boolean indicating if lock was acquired
        error_message: Optional error if acquisition failed
        stale_lock_removed: True if a stale lock was removed before acquisition
    """
    success: bool
    error_message: Optional[str] = None
    stale_lock_removed: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "success": self.success,
            "error_message": self.error_message,
            "stale_lock_removed": self.stale_lock_removed
        }
```

**Example Usage:**
```python
lock_manager = LockManager()
lock_result = lock_manager.acquire_lock()

if not lock_result.success:
    raise ConcurrentUpdateError(lock_result.error_message)

if lock_result.stale_lock_removed:
    logger.warning("Removed stale lock from previous update")

try:
    # ... perform update
finally:
    lock_manager.release_lock()
```

---

### 14. RateLimitExceeded Enhancement

**Purpose:** Enhanced rate limit exception with reset time information

**Definition:**
```python
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class RateLimitExceeded(Exception):
    """
    Raised when GitHub API rate limit exceeded.

    Attributes:
        message: Human-readable error message
        reset_at: Datetime when rate limit resets
        retry_after_seconds: Seconds to wait before retrying
    """
    message: str
    reset_at: datetime
    retry_after_seconds: int

    def __str__(self) -> str:
        """String representation for exception handling."""
        return self.message
```

---

### 15. Custom Exceptions

**Definition:**
```python
class VersionCheckError(Exception):
    """Raised when version check fails."""
    pass

class UpdateError(Exception):
    """Raised when update operation fails."""
    pass

class BackupError(Exception):
    """Raised when backup operation fails."""
    pass

class RestoreError(Exception):
    """Raised when restore operation fails."""
    pass

class InsufficientDiskSpace(Exception):
    """Raised when insufficient disk space for backup."""
    pass

class ConcurrentUpdateError(Exception):
    """Raised when another update is already in progress."""
    pass

class VersionFileUpdateError(UpdateError):
    """Raised when VERSION file cannot be updated after installation."""
    pass

class RollbackFailureError(UpdateError):
    """Raised when automatic rollback fails (catastrophic scenario)."""
    pass

class UpdatePrerequisiteError(UpdateError):
    """Raised when update prerequisites are not met."""
    pass
```

**Example Usage:**
```python
try:
    result = update_orchestrator.execute_update()
except InsufficientDiskSpace as e:
    print(f"Cannot proceed: {e}")
    print("Free up disk space and try again")
except ConcurrentUpdateError:
    print("Another update is already in progress. Wait for it to complete.")
except VersionFileUpdateError as e:
    print(f"Update failed during VERSION file write: {e}")
    print("System has been restored from backup.")
except RollbackFailureError as e:
    print("CRITICAL: Update failed AND automatic rollback failed")
    print(e)  # Contains emergency recovery instructions
```

---

## JSON Serialization

All data models include `to_dict()` methods for JSON serialization:

**Example:**
```python
import json

result = VersionCheckResult(
    installed_version="1.5.7",
    available_version="1.6.0",
    update_available=True,
    breaking_change=False,
    changelog_highlights=["Feature A", "Bug fix B"]
)

# Serialize to JSON
json_str = json.dumps(result.to_dict(), indent=2)

# Output:
# {
#   "installed_version": "1.5.7",
#   "available_version": "1.6.0",
#   "update_available": true,
#   "breaking_change": false,
#   "changelog_highlights": ["Feature A", "Bug fix B"],
#   "error_message": null
# }
```

**Use Cases:**
- Logging (structured JSON logs)
- API responses (if exposing update functionality via API)
- Testing (assert on serialized output)
- Debugging (inspect object state)

---

## Validation Strategies

### Semantic Version Validation

```python
from packaging import version

def validate_semver(version_str: str) -> bool:
    """
    Validate semantic version string.

    Args:
        version_str: Version string to validate

    Returns:
        True if valid semantic version

    Examples:
        validate_semver("1.5.7") → True
        validate_semver("1.5.7-beta.1") → True
        validate_semver("1.5") → False
    """
    try:
        version.parse(version_str)
        return True
    except version.InvalidVersion:
        return False
```

### Path Validation

```python
from pathlib import Path

def validate_backup_path(backup_path: str) -> bool:
    """
    Validate backup directory path.

    Checks:
    - Path matches expected pattern (~/.claude_bck_YYYYMMDD)
    - Directory exists
    - Directory is readable

    Args:
        backup_path: Backup directory path

    Returns:
        True if valid backup path
    """
    import re

    path = Path(backup_path).expanduser()

    # Check pattern
    pattern = r'\.claude_bck_\d{8}$'
    if not re.search(pattern, path.name):
        return False

    # Check exists and readable
    return path.exists() and path.is_dir() and os.access(path, os.R_OK)
```

---

## Type Aliases

**Definition:**
```python
from typing import TypeAlias

# Semantic version string (e.g., "1.5.7")
SemanticVersion: TypeAlias = str

# ISO 8601 datetime string (e.g., "2026-01-25T14:32:15Z")
ISO8601DateTime: TypeAlias = str

# File path (absolute or relative with ~)
FilePath: TypeAlias = str

# GitHub repository identifier (owner/repo)
RepoIdentifier: TypeAlias = str
```

**Usage:**
```python
def get_version_from_file(path: FilePath) -> SemanticVersion:
    """Read version from file."""
    return Path(path).read_text().strip()
```

---

## Summary

This data models specification provides:

✅ **Domain Models** - Core business objects with validation
✅ **Result Objects** - Operation outcome representations (simplified for delegation)
✅ **Lock Management Objects** - LockInfo and LockResult for concurrency control
✅ **Configuration Object** - Environment-driven configuration
✅ **Custom Exceptions** - Clear error handling including catastrophic scenarios
✅ **Type Safety** - Comprehensive type annotations
✅ **Immutability** - Frozen dataclasses where appropriate
✅ **Serialization** - JSON conversion for all models
✅ **Validation** - Built-in validation methods
✅ **Documentation** - Clear docstrings and examples
✅ **Integration with Existing System** - BackupManifest removed (use existing BackupManager)

**Model Count by Category:**
- **Domain Models:** 4 (VersionInfo, ReleaseMetadata, VersionComparison, RepositoryInfo)
  - ❌ BackupManifest REMOVED - Use existing from scripts/install/install_utils.py
- **Result Objects:** 3 (VersionCheckResult, UpdateResult simplified, PrerequisiteCheckResult)
  - ❌ BackupResult REMOVED - Handled by existing BackupManager
  - ❌ RestoreResult REMOVED - Handled by existing BackupManager
  - ❌ CleanupResult REMOVED - Handled by existing BackupManager
- **Lock Management:** 2 (LockInfo, LockResult)
- **Configuration:** 1 (UpdateConfig)
- **Exceptions:** 10 custom exception types (including RateLimitExceeded enhancement, VersionFileUpdateError, RollbackFailureError, UpdatePrerequisiteError)

**BLOCKER Fixes Applied:**
1. ✅ Lock File Data Models - LockInfo and LockResult added
2. ✅ Installation System Integration - BackupManifest, BackupResult, RestoreResult, CleanupResult removed (use existing)
3. ✅ Catastrophic Recovery - RollbackFailureError exception added

**MAJOR Fixes Applied:**
1. ✅ Simplified UpdateResult - Delegates to installer, no longer tracks backup/rollback details
2. ✅ Rate Limit Enhancement - RateLimitExceeded includes reset_at and retry_after_seconds
3. ✅ VERSION File Error - VersionFileUpdateError exception added

**Next Wave:** DISTILL - Create acceptance tests using these data models

---

**Data Models:** Approved ✅ (Adversarial Review BLOCKERS Resolved)
**Date:** 2026-01-25
**Architect:** Morgan (Solution Architect)
