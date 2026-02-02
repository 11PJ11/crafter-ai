"""CandidateVersion domain object and BumpType enum.

This module defines the core domain objects for semantic versioning operations.
These are pure domain objects with no external dependencies.
"""

from dataclasses import dataclass
from enum import Enum


class BumpType(Enum):
    """Type of version bump to apply.

    MAJOR: Breaking changes (feat! or BREAKING CHANGE in commit).
    MINOR: New features (feat commit).
    PATCH: Bug fixes (fix commit).
    NONE: No version bump needed.
    """

    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    NONE = "none"


@dataclass(frozen=True)
class CandidateVersion:
    """Immutable representation of a version candidate.

    Attributes:
        current_version: Current version from pyproject.toml.
        bump_type: Determined bump type based on commits.
        next_version: Calculated next version string.
        commit_messages: List of commits driving the bump.
        is_prerelease: Whether this is a dev/rc version.
        prerelease_suffix: Prerelease suffix (e.g., 'dev1', 'rc1').
    """

    current_version: str
    bump_type: BumpType
    next_version: str
    commit_messages: list[str]
    is_prerelease: bool
    prerelease_suffix: str | None


def parse_version(version_str: str) -> tuple[int, int, int]:
    """Parse a semver string into major, minor, patch tuple.

    Strips prerelease suffixes (e.g., '.dev1', 'rc1') before parsing.

    Args:
        version_str: Version string like '1.2.3' or '1.2.3.dev1'.

    Returns:
        Tuple of (major, minor, patch) integers.
    """
    # Strip common prerelease suffixes
    base_version = version_str
    for suffix in (".dev", "dev", ".rc", "rc", ".a", "a", ".b", "b"):
        if suffix in base_version:
            base_version = base_version.split(suffix)[0]
            break

    # Remove trailing dot if present
    base_version = base_version.rstrip(".")

    parts = base_version.split(".")
    return (int(parts[0]), int(parts[1]), int(parts[2]))


def calculate_next_version(current: str, bump_type: BumpType) -> str:
    """Calculate the next version based on bump type.

    Follows semantic versioning conventions:
    - MAJOR: Increment major, reset minor and patch to 0.
    - MINOR: Increment minor, reset patch to 0.
    - PATCH: Increment patch only.
    - NONE: Return current version unchanged.

    Args:
        current: Current version string (e.g., '1.2.3').
        bump_type: Type of bump to apply.

    Returns:
        Next version string (e.g., '1.3.0').
    """
    if bump_type == BumpType.NONE:
        return current

    major, minor, patch = parse_version(current)

    if bump_type == BumpType.MAJOR:
        return f"{major + 1}.0.0"
    elif bump_type == BumpType.MINOR:
        return f"{major}.{minor + 1}.0"
    else:  # PATCH
        return f"{major}.{minor}.{patch + 1}"


def create_candidate(
    current: str,
    bump_type: BumpType,
    commits: list[str],
    prerelease: str | None = None,
) -> CandidateVersion:
    """Factory function to create a CandidateVersion.

    Calculates the next version and handles prerelease suffix formatting.

    Args:
        current: Current version string.
        bump_type: Type of bump to apply.
        commits: List of commit messages driving the bump.
        prerelease: Optional prerelease suffix (e.g., 'dev1', 'rc1').

    Returns:
        CandidateVersion instance with calculated next version.
    """
    base_next = calculate_next_version(current, bump_type)

    if prerelease:
        # PEP 440 format: use dot for dev, no dot for rc/a/b
        if prerelease.startswith("dev"):
            next_version = f"{base_next}.{prerelease}"
        else:
            next_version = f"{base_next}{prerelease}"
        is_prerelease = True
    else:
        next_version = base_next
        is_prerelease = False

    return CandidateVersion(
        current_version=current,
        bump_type=bump_type,
        next_version=next_version,
        commit_messages=commits,
        is_prerelease=is_prerelease,
        prerelease_suffix=prerelease,
    )
