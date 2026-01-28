"""
Version entity for semantic versioning.

Handles parsing, comparison, and validation of semantic version strings.
Supports standard semver (major.minor.patch) and pre-release versions.

Example:
    >>> version = Version("1.2.3")
    >>> version.major
    1
    >>> Version("1.3.0") > Version("1.2.3")
    True
    >>> Version("1.2.3-rc.main.20260127.1").is_prerelease
    True
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import total_ordering
from typing import Optional


@total_ordering
@dataclass(frozen=True)
class Version:
    """
    Semantic version representation.

    Parses and compares semantic version strings in the format:
    major.minor.patch[-prerelease]

    Attributes:
        major: Major version number (breaking changes)
        minor: Minor version number (new features, backward compatible)
        patch: Patch version number (bug fixes)
        prerelease: Optional pre-release identifier (e.g., "rc.main.20260127.1")

    Raises:
        ValueError: If the version string is invalid
    """

    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None

    _SEMVER_PATTERN = re.compile(
        r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
        r"(?:-(?P<prerelease>[\da-zA-Z\-\.]+))?$"
    )

    def __init__(self, version_string: str) -> None:
        """
        Create a Version from a version string.

        Args:
            version_string: A semantic version string (e.g., "1.2.3" or "1.2.3-rc.1")

        Raises:
            ValueError: If the version string is invalid
        """
        if not version_string:
            raise ValueError(f"Invalid version: '{version_string}' - version string cannot be empty")

        match = self._SEMVER_PATTERN.match(version_string)
        if not match:
            raise ValueError(f"Invalid version: '{version_string}' - must be in format major.minor.patch[-prerelease]")

        object.__setattr__(self, "major", int(match.group("major")))
        object.__setattr__(self, "minor", int(match.group("minor")))
        object.__setattr__(self, "patch", int(match.group("patch")))
        object.__setattr__(self, "prerelease", match.group("prerelease"))

    @property
    def is_prerelease(self) -> bool:
        """Check if this is a pre-release version."""
        return self.prerelease is not None

    def __str__(self) -> str:
        """Return the version as a string."""
        base = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            return f"{base}-{self.prerelease}"
        return base

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""
        return f"Version('{self}')"

    def __eq__(self, other: object) -> bool:
        """Check equality with another Version."""
        if not isinstance(other, Version):
            return NotImplemented
        return (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
            and self.prerelease == other.prerelease
        )

    def __lt__(self, other: Version) -> bool:
        """
        Compare versions for ordering.

        Pre-release versions are considered less than stable versions
        with the same base version (e.g., 1.2.3-rc < 1.2.3).
        """
        if not isinstance(other, Version):
            return NotImplemented

        # Compare major.minor.patch first
        self_tuple = (self.major, self.minor, self.patch)
        other_tuple = (other.major, other.minor, other.patch)

        if self_tuple != other_tuple:
            return self_tuple < other_tuple

        # Same base version: compare pre-release status
        # No prerelease (stable) > prerelease
        if self.prerelease is None and other.prerelease is not None:
            return False
        if self.prerelease is not None and other.prerelease is None:
            return True

        # Both have prerelease: compare lexicographically
        if self.prerelease and other.prerelease:
            return self.prerelease < other.prerelease

        return False

    def __hash__(self) -> int:
        """Return hash for use in sets and as dict keys."""
        return hash((self.major, self.minor, self.patch, self.prerelease))
