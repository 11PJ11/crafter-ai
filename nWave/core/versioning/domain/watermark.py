"""
Watermark entity for update check state tracking.

Tracks when the last version check was performed and what the latest
known version is. Determines if a check is stale (>24 hours old).

Example:
    >>> from datetime import datetime, timezone
    >>> watermark = Watermark(
    ...     last_check=datetime.now(timezone.utc),
    ...     latest_version=Version("1.0.0"),
    ... )
    >>> watermark.is_stale
    False
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from nWave.core.versioning.domain.version import Version


STALENESS_THRESHOLD_HOURS = 24


@dataclass(frozen=True)
class Watermark:
    """
    Update check state tracking entity.

    Stores the timestamp of the last version check and the latest
    known version. Provides staleness detection (>24 hours since last check).

    Attributes:
        last_check: Timestamp of the last version check (UTC)
        latest_version: The latest known version at the time of check

    Note:
        This is an immutable value object. Update methods return new instances.
    """

    last_check: datetime
    latest_version: Version

    @property
    def is_stale(self) -> bool:
        """
        Check if the watermark is stale.

        A watermark is considered stale if more than 24 hours have
        passed since the last check.

        Returns:
            True if last_check was more than 24 hours ago, False otherwise.
        """
        threshold = timedelta(hours=STALENESS_THRESHOLD_HOURS)
        time_since_check = datetime.now(timezone.utc) - self.last_check
        return time_since_check > threshold

    def to_json(self) -> str:
        """
        Serialize the watermark to a JSON string.

        Returns:
            JSON string representation of the watermark.
        """
        data = {
            "last_check": self.last_check.isoformat(),
            "latest_version": str(self.latest_version),
        }
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_str: str) -> Watermark:
        """
        Deserialize a watermark from a JSON string.

        Args:
            json_str: JSON string to parse.

        Returns:
            A new Watermark instance with the deserialized data.

        Raises:
            ValueError: If the JSON is invalid or missing required fields.
            json.JSONDecodeError: If the string is not valid JSON.
        """
        data = json.loads(json_str)
        last_check = datetime.fromisoformat(data["last_check"])
        latest_version = Version(data["latest_version"])
        return cls(last_check=last_check, latest_version=latest_version)

    def with_updated_timestamp(self, new_timestamp: datetime) -> Watermark:
        """
        Create a new watermark with an updated timestamp.

        Args:
            new_timestamp: The new last_check timestamp.

        Returns:
            A new Watermark with the updated timestamp and same version.
        """
        return Watermark(
            last_check=new_timestamp,
            latest_version=self.latest_version,
        )

    def with_updated_version(self, new_version: Version) -> Watermark:
        """
        Create a new watermark with an updated version.

        Args:
            new_version: The new latest_version.

        Returns:
            A new Watermark with the updated version and same timestamp.
        """
        return Watermark(
            last_check=self.last_check,
            latest_version=new_version,
        )

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        date_str = self.last_check.strftime("%Y-%m-%d %H:%M:%S")
        return f"Watermark(version={self.latest_version}, checked={date_str})"

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""
        return f"Watermark(last_check={self.last_check.isoformat()}, latest_version={self.latest_version!r})"
