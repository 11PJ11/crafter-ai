"""
RCVersion value object for release candidate versioning.

Handles creation, parsing, and manipulation of RC version strings.
RC version format: {base}-rc.{branch}.{YYYYMMDD}.{N}

Example:
    >>> rc = RCVersion.create("1.2.3", "main", date(2026, 1, 27), 1)
    >>> str(rc)
    '1.2.3-rc.main.20260127.1'
    >>> RCVersion.parse("1.2.3-rc.feature-new-agent.20260127.2").build_number
    2
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import ClassVar


@dataclass(frozen=True)
class RCVersion:
    """
    Release candidate version representation.

    Parses and creates RC version strings in the format:
    {base}-rc.{branch}.{YYYYMMDD}.{N}

    Attributes:
        base_version: The base semantic version (e.g., "1.2.3")
        branch: The branch name (normalized, "/" replaced with "-")
        build_date: The date of the build
        build_number: The build number for this date

    Raises:
        ValueError: If the RC version string is invalid
    """

    base_version: str
    branch: str
    build_date: date
    build_number: int

    _RC_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^(?P<base>\d+\.\d+\.\d+)-rc\."
        r"(?P<branch>[a-zA-Z0-9\-]+)\."
        r"(?P<date>\d{8})\."
        r"(?P<build>\d+)$"
    )

    @classmethod
    def create(
        cls,
        base_version: str,
        branch: str,
        build_date: date,
        build_number: int,
    ) -> RCVersion:
        """
        Create an RC version from components.

        Branch names with "/" are normalized to "-".

        Args:
            base_version: The base semantic version (e.g., "1.2.3")
            branch: The branch name (slashes will be normalized to hyphens)
            build_date: The date of the build
            build_number: The build number for this date

        Returns:
            A new RCVersion instance
        """
        normalized_branch = cls._normalize_branch_name(branch)
        return cls(
            base_version=base_version,
            branch=normalized_branch,
            build_date=build_date,
            build_number=build_number,
        )

    @classmethod
    def parse(cls, rc_version_string: str) -> RCVersion:
        """
        Parse an RC version string.

        Args:
            rc_version_string: A string in format "1.2.3-rc.branch.YYYYMMDD.N"

        Returns:
            A new RCVersion instance

        Raises:
            ValueError: If the string is not a valid RC version format
        """
        if not rc_version_string:
            raise ValueError(f"Invalid RC version: '{rc_version_string}' - version string cannot be empty")

        match = cls._RC_PATTERN.match(rc_version_string)
        if not match:
            raise ValueError(
                f"Invalid RC version: '{rc_version_string}' - "
                "must be in format base-rc.branch.YYYYMMDD.N"
            )

        base_version = match.group("base")
        branch = match.group("branch")
        date_str = match.group("date")
        build_number = int(match.group("build"))

        build_date = cls._parse_date_string(date_str)

        return cls(
            base_version=base_version,
            branch=branch,
            build_date=build_date,
            build_number=build_number,
        )

    def increment_build_number(self) -> RCVersion:
        """
        Create a new RC version with incremented build number.

        Returns:
            A new RCVersion instance with build_number + 1
        """
        return RCVersion(
            base_version=self.base_version,
            branch=self.branch,
            build_date=self.build_date,
            build_number=self.build_number + 1,
        )

    def __str__(self) -> str:
        """Return the RC version as a formatted string."""
        date_str = self.build_date.strftime("%Y%m%d")
        return f"{self.base_version}-rc.{self.branch}.{date_str}.{self.build_number}"

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""
        return f"RCVersion('{self}')"

    @staticmethod
    def _normalize_branch_name(branch: str) -> str:
        """
        Normalize branch name by replacing slashes with hyphens.

        Args:
            branch: The branch name to normalize

        Returns:
            The normalized branch name with "/" replaced by "-"
        """
        return branch.replace("/", "-")

    @staticmethod
    def _parse_date_string(date_str: str) -> date:
        """
        Parse a date string in YYYYMMDD format.

        Args:
            date_str: A date string in YYYYMMDD format

        Returns:
            A date object

        Raises:
            ValueError: If the date string is invalid
        """
        year = int(date_str[0:4])
        month = int(date_str[4:6])
        day = int(date_str[6:8])
        return date(year, month, day)
