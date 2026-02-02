"""
Unit tests for Watermark entity.

Tests update check state tracking: last_check timestamp, latest_version,
and staleness determination (>24 hours).

Acceptance criteria:
- Watermark with last_check >24h ago is_stale returns True
- Watermark with last_check <24h ago is_stale returns False
- Watermark serializes to/from JSON
"""

import json
from datetime import datetime, timedelta, timezone

from nWave.core.versioning.domain.version import Version
from nWave.core.versioning.domain.watermark import Watermark


class TestWatermarkIsStaleWhenOlderThan24Hours:
    """Tests for staleness detection when check is older than 24 hours."""

    def test_watermark_is_stale_when_25_hours_ago(self):
        """Watermark is stale when last check was 25 hours ago."""
        last_check = datetime.now(timezone.utc) - timedelta(hours=25)
        watermark = Watermark(
            last_check=last_check,
            latest_version=Version("1.0.0"),
        )

        assert watermark.is_stale is True

    def test_watermark_is_stale_when_exactly_24_hours_1_second_ago(self):
        """Watermark is stale when last check was 24 hours and 1 second ago."""
        last_check = datetime.now(timezone.utc) - timedelta(hours=24, seconds=1)
        watermark = Watermark(
            last_check=last_check,
            latest_version=Version("1.0.0"),
        )

        assert watermark.is_stale is True

    def test_watermark_is_stale_when_48_hours_ago(self):
        """Watermark is stale when last check was 48 hours ago."""
        last_check = datetime.now(timezone.utc) - timedelta(hours=48)
        watermark = Watermark(
            last_check=last_check,
            latest_version=Version("1.0.0"),
        )

        assert watermark.is_stale is True

    def test_acceptance_criteria_stale_watermark(self):
        """Acceptance criteria: Watermark with last_check >24h ago is_stale returns True."""
        last_check = datetime.now(timezone.utc) - timedelta(hours=25)
        watermark = Watermark(
            last_check=last_check,
            latest_version=Version("1.2.3"),
        )

        assert watermark.is_stale is True


class TestWatermarkIsFreshWhenWithin24Hours:
    """Tests for freshness when check is within 24 hours."""

    def test_watermark_is_fresh_when_23_hours_ago(self):
        """Watermark is fresh when last check was 23 hours ago."""
        last_check = datetime.now(timezone.utc) - timedelta(hours=23)
        watermark = Watermark(
            last_check=last_check,
            latest_version=Version("1.0.0"),
        )

        assert watermark.is_stale is False

    def test_watermark_is_fresh_when_exactly_24_hours_minus_1_second_ago(self):
        """Watermark is fresh when last check was 24 hours minus 1 second ago (boundary)."""
        # Use 24 hours minus 1 second to avoid timing issues at exact boundary
        last_check = (
            datetime.now(timezone.utc) - timedelta(hours=24) + timedelta(seconds=1)
        )
        watermark = Watermark(
            last_check=last_check,
            latest_version=Version("1.0.0"),
        )

        assert watermark.is_stale is False

    def test_watermark_is_fresh_when_1_hour_ago(self):
        """Watermark is fresh when last check was 1 hour ago."""
        last_check = datetime.now(timezone.utc) - timedelta(hours=1)
        watermark = Watermark(
            last_check=last_check,
            latest_version=Version("1.0.0"),
        )

        assert watermark.is_stale is False

    def test_watermark_is_fresh_when_just_created(self):
        """Watermark is fresh when last check was just now."""
        last_check = datetime.now(timezone.utc)
        watermark = Watermark(
            last_check=last_check,
            latest_version=Version("1.0.0"),
        )

        assert watermark.is_stale is False

    def test_acceptance_criteria_fresh_watermark(self):
        """Acceptance criteria: Watermark with last_check <24h ago is_stale returns False."""
        last_check = datetime.now(timezone.utc) - timedelta(hours=12)
        watermark = Watermark(
            last_check=last_check,
            latest_version=Version("1.2.3"),
        )

        assert watermark.is_stale is False


class TestWatermarkSerializeToJson:
    """Tests for JSON serialization."""

    def test_serialize_to_json_contains_last_check(self):
        """Serialized JSON contains last_check timestamp."""
        last_check = datetime(2026, 1, 28, 12, 0, 0, tzinfo=timezone.utc)
        watermark = Watermark(
            last_check=last_check,
            latest_version=Version("1.2.3"),
        )

        json_str = watermark.to_json()
        data = json.loads(json_str)

        assert "last_check" in data
        assert data["last_check"] == "2026-01-28T12:00:00+00:00"

    def test_serialize_to_json_contains_latest_version(self):
        """Serialized JSON contains latest_version string."""
        last_check = datetime(2026, 1, 28, 12, 0, 0, tzinfo=timezone.utc)
        watermark = Watermark(
            last_check=last_check,
            latest_version=Version("1.2.3"),
        )

        json_str = watermark.to_json()
        data = json.loads(json_str)

        assert "latest_version" in data
        assert data["latest_version"] == "1.2.3"

    def test_serialize_to_json_is_valid_json(self):
        """Serialized output is valid JSON."""
        last_check = datetime(2026, 1, 28, 12, 0, 0, tzinfo=timezone.utc)
        watermark = Watermark(
            last_check=last_check,
            latest_version=Version("1.2.3"),
        )

        json_str = watermark.to_json()

        # Should not raise
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)

    def test_acceptance_criteria_serialize_to_json(self):
        """Acceptance criteria: Watermark serializes to JSON."""
        last_check = datetime(2026, 1, 28, 10, 30, 0, tzinfo=timezone.utc)
        watermark = Watermark(
            last_check=last_check,
            latest_version=Version("2.0.0-rc.main.20260128.1"),
        )

        json_str = watermark.to_json()
        data = json.loads(json_str)

        assert data["last_check"] == "2026-01-28T10:30:00+00:00"
        assert data["latest_version"] == "2.0.0-rc.main.20260128.1"


class TestWatermarkDeserializeFromJson:
    """Tests for JSON deserialization."""

    def test_deserialize_from_json_restores_last_check(self):
        """Deserialize restores last_check timestamp."""
        json_str = (
            '{"last_check": "2026-01-28T12:00:00+00:00", "latest_version": "1.2.3"}'
        )

        watermark = Watermark.from_json(json_str)

        expected = datetime(2026, 1, 28, 12, 0, 0, tzinfo=timezone.utc)
        assert watermark.last_check == expected

    def test_deserialize_from_json_restores_latest_version(self):
        """Deserialize restores latest_version as Version object."""
        json_str = (
            '{"last_check": "2026-01-28T12:00:00+00:00", "latest_version": "1.2.3"}'
        )

        watermark = Watermark.from_json(json_str)

        assert watermark.latest_version == Version("1.2.3")
        assert isinstance(watermark.latest_version, Version)

    def test_deserialize_from_json_with_prerelease_version(self):
        """Deserialize handles pre-release version strings."""
        json_str = '{"last_check": "2026-01-28T12:00:00+00:00", "latest_version": "2.0.0-rc.main.20260128.1"}'

        watermark = Watermark.from_json(json_str)

        assert watermark.latest_version == Version("2.0.0-rc.main.20260128.1")
        assert watermark.latest_version.is_prerelease is True

    def test_acceptance_criteria_deserialize_from_json(self):
        """Acceptance criteria: Watermark deserializes from JSON."""
        json_str = (
            '{"last_check": "2026-01-28T10:30:00+00:00", "latest_version": "2.0.0"}'
        )

        watermark = Watermark.from_json(json_str)

        expected_time = datetime(2026, 1, 28, 10, 30, 0, tzinfo=timezone.utc)
        assert watermark.last_check == expected_time
        assert watermark.latest_version == Version("2.0.0")


class TestWatermarkRoundTripSerialization:
    """Tests for JSON round-trip (serialize then deserialize)."""

    def test_round_trip_preserves_data(self):
        """Serialize then deserialize preserves all data."""
        last_check = datetime(2026, 1, 28, 15, 45, 30, tzinfo=timezone.utc)
        original = Watermark(
            last_check=last_check,
            latest_version=Version("3.1.4"),
        )

        json_str = original.to_json()
        restored = Watermark.from_json(json_str)

        assert restored.last_check == original.last_check
        assert restored.latest_version == original.latest_version

    def test_round_trip_with_prerelease_version(self):
        """Round-trip preserves pre-release version data."""
        last_check = datetime(2026, 1, 28, 15, 45, 30, tzinfo=timezone.utc)
        original = Watermark(
            last_check=last_check,
            latest_version=Version("1.0.0-rc.feature.20260128.5"),
        )

        json_str = original.to_json()
        restored = Watermark.from_json(json_str)

        assert restored.latest_version == original.latest_version
        assert restored.latest_version.is_prerelease is True


class TestWatermarkUpdateTimestamp:
    """Tests for updating the last_check timestamp."""

    def test_update_timestamp_creates_new_watermark(self):
        """Update timestamp returns a new Watermark (immutability)."""
        original_time = datetime(2026, 1, 27, 12, 0, 0, tzinfo=timezone.utc)
        original = Watermark(
            last_check=original_time,
            latest_version=Version("1.0.0"),
        )

        new_time = datetime(2026, 1, 28, 12, 0, 0, tzinfo=timezone.utc)
        updated = original.with_updated_timestamp(new_time)

        assert updated is not original
        assert updated.last_check == new_time
        assert original.last_check == original_time  # Original unchanged

    def test_update_timestamp_preserves_version(self):
        """Update timestamp preserves the latest_version."""
        original_time = datetime(2026, 1, 27, 12, 0, 0, tzinfo=timezone.utc)
        version = Version("2.5.0")
        original = Watermark(
            last_check=original_time,
            latest_version=version,
        )

        new_time = datetime(2026, 1, 28, 12, 0, 0, tzinfo=timezone.utc)
        updated = original.with_updated_timestamp(new_time)

        assert updated.latest_version == version

    def test_update_timestamp_makes_stale_watermark_fresh(self):
        """Updating timestamp can make a stale watermark fresh."""
        old_time = datetime.now(timezone.utc) - timedelta(hours=48)
        original = Watermark(
            last_check=old_time,
            latest_version=Version("1.0.0"),
        )
        assert original.is_stale is True

        new_time = datetime.now(timezone.utc)
        updated = original.with_updated_timestamp(new_time)

        assert updated.is_stale is False


class TestWatermarkUpdateLatestVersion:
    """Tests for updating the latest_version."""

    def test_update_version_creates_new_watermark(self):
        """Update version returns a new Watermark (immutability)."""
        last_check = datetime(2026, 1, 28, 12, 0, 0, tzinfo=timezone.utc)
        original = Watermark(
            last_check=last_check,
            latest_version=Version("1.0.0"),
        )

        updated = original.with_updated_version(Version("2.0.0"))

        assert updated is not original
        assert updated.latest_version == Version("2.0.0")
        assert original.latest_version == Version("1.0.0")  # Original unchanged

    def test_update_version_preserves_timestamp(self):
        """Update version preserves the last_check timestamp."""
        last_check = datetime(2026, 1, 28, 12, 0, 0, tzinfo=timezone.utc)
        original = Watermark(
            last_check=last_check,
            latest_version=Version("1.0.0"),
        )

        updated = original.with_updated_version(Version("2.0.0"))

        assert updated.last_check == last_check

    def test_update_to_prerelease_version(self):
        """Can update to a pre-release version."""
        last_check = datetime(2026, 1, 28, 12, 0, 0, tzinfo=timezone.utc)
        original = Watermark(
            last_check=last_check,
            latest_version=Version("1.0.0"),
        )

        updated = original.with_updated_version(Version("2.0.0-rc.main.20260128.1"))

        assert updated.latest_version == Version("2.0.0-rc.main.20260128.1")
        assert updated.latest_version.is_prerelease is True


class TestWatermarkEquality:
    """Tests for Watermark equality comparison."""

    def test_equal_watermarks(self):
        """Watermarks with same data are equal."""
        last_check = datetime(2026, 1, 28, 12, 0, 0, tzinfo=timezone.utc)
        w1 = Watermark(last_check=last_check, latest_version=Version("1.0.0"))
        w2 = Watermark(last_check=last_check, latest_version=Version("1.0.0"))

        assert w1 == w2

    def test_not_equal_different_timestamp(self):
        """Watermarks with different timestamps are not equal."""
        time1 = datetime(2026, 1, 28, 12, 0, 0, tzinfo=timezone.utc)
        time2 = datetime(2026, 1, 28, 13, 0, 0, tzinfo=timezone.utc)
        w1 = Watermark(last_check=time1, latest_version=Version("1.0.0"))
        w2 = Watermark(last_check=time2, latest_version=Version("1.0.0"))

        assert w1 != w2

    def test_not_equal_different_version(self):
        """Watermarks with different versions are not equal."""
        last_check = datetime(2026, 1, 28, 12, 0, 0, tzinfo=timezone.utc)
        w1 = Watermark(last_check=last_check, latest_version=Version("1.0.0"))
        w2 = Watermark(last_check=last_check, latest_version=Version("2.0.0"))

        assert w1 != w2


class TestWatermarkStringRepresentation:
    """Tests for Watermark string representation."""

    def test_str_representation(self):
        """String representation shows key information."""
        last_check = datetime(2026, 1, 28, 12, 0, 0, tzinfo=timezone.utc)
        watermark = Watermark(
            last_check=last_check,
            latest_version=Version("1.2.3"),
        )

        str_repr = str(watermark)

        assert "1.2.3" in str_repr
        assert "2026-01-28" in str_repr

    def test_repr_representation(self):
        """Repr shows developer-friendly information."""
        last_check = datetime(2026, 1, 28, 12, 0, 0, tzinfo=timezone.utc)
        watermark = Watermark(
            last_check=last_check,
            latest_version=Version("1.2.3"),
        )

        repr_str = repr(watermark)

        assert "Watermark" in repr_str
        assert "1.2.3" in repr_str
