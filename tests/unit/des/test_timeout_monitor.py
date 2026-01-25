"""Unit tests for TimeoutMonitor component.

Tests the timeout monitoring logic that tracks elapsed time from phase start
and detects when duration thresholds are crossed.
"""

from datetime import datetime, timezone, timedelta
import pytest
from des.timeout_monitor import TimeoutMonitor


class TestTimeoutMonitorCalculatesElapsedTime:
    """Test that TimeoutMonitor correctly calculates elapsed time."""

    def test_calculates_elapsed_time_from_phase_start(self):
        """TimeoutMonitor calculates elapsed seconds from phase started_at timestamp."""
        # Given: A phase started 5 minutes ago
        started_at = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
        monitor = TimeoutMonitor(started_at=started_at)

        # When: Getting elapsed seconds
        elapsed = monitor.get_elapsed_seconds()

        # Then: Should be approximately 300 seconds (5 minutes)
        assert 295 <= elapsed <= 305, f"Expected ~300 seconds, got {elapsed}"

    def test_handles_recent_phase_start(self):
        """TimeoutMonitor handles phases that just started (< 1 second ago)."""
        # Given: A phase that just started
        started_at = datetime.now(timezone.utc).isoformat()
        monitor = TimeoutMonitor(started_at=started_at)

        # When: Getting elapsed seconds
        elapsed = monitor.get_elapsed_seconds()

        # Then: Should be less than 2 seconds
        assert 0 <= elapsed <= 2, f"Expected ~0 seconds, got {elapsed}"

    def test_handles_timezone_aware_timestamps(self):
        """TimeoutMonitor correctly parses timezone-aware ISO timestamps."""
        # Given: A timezone-aware timestamp from 10 minutes ago
        started_at = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
        monitor = TimeoutMonitor(started_at=started_at)

        # When: Getting elapsed seconds
        elapsed = monitor.get_elapsed_seconds()

        # Then: Should be approximately 600 seconds
        assert 595 <= elapsed <= 605, f"Expected ~600 seconds, got {elapsed}"


class TestTimeoutMonitorThresholdDetection:
    """Test that TimeoutMonitor detects crossed thresholds."""

    def test_returns_empty_list_when_no_thresholds_crossed(self):
        """check_thresholds returns empty list when elapsed time is under all thresholds."""
        # Given: A phase started 2 minutes ago
        started_at = (datetime.now(timezone.utc) - timedelta(minutes=2)).isoformat()
        monitor = TimeoutMonitor(started_at=started_at)

        # When: Checking thresholds [5, 10, 15] minutes
        crossed = monitor.check_thresholds(duration_minutes=[5, 10, 15])

        # Then: Should return empty list
        assert crossed == []

    def test_returns_single_crossed_threshold(self):
        """check_thresholds returns list with single crossed threshold."""
        # Given: A phase started 7 minutes ago
        started_at = (datetime.now(timezone.utc) - timedelta(minutes=7)).isoformat()
        monitor = TimeoutMonitor(started_at=started_at)

        # When: Checking thresholds [5, 10, 15] minutes
        crossed = monitor.check_thresholds(duration_minutes=[5, 10, 15])

        # Then: Should return [5] (only first threshold crossed)
        assert crossed == [5]

    def test_returns_multiple_crossed_thresholds(self):
        """check_thresholds returns all thresholds that have been crossed."""
        # Given: A phase started 12 minutes ago
        started_at = (datetime.now(timezone.utc) - timedelta(minutes=12)).isoformat()
        monitor = TimeoutMonitor(started_at=started_at)

        # When: Checking thresholds [5, 10, 15] minutes
        crossed = monitor.check_thresholds(duration_minutes=[5, 10, 15])

        # Then: Should return [5, 10] (first two thresholds crossed)
        assert crossed == [5, 10]

    def test_returns_all_crossed_thresholds(self):
        """check_thresholds returns all thresholds when all are crossed."""
        # Given: A phase started 20 minutes ago
        started_at = (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat()
        monitor = TimeoutMonitor(started_at=started_at)

        # When: Checking thresholds [5, 10, 15] minutes
        crossed = monitor.check_thresholds(duration_minutes=[5, 10, 15])

        # Then: Should return [5, 10, 15] (all thresholds crossed)
        assert crossed == [5, 10, 15]

    def test_handles_empty_threshold_list(self):
        """check_thresholds handles empty threshold list correctly."""
        # Given: A phase started 10 minutes ago
        started_at = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
        monitor = TimeoutMonitor(started_at=started_at)

        # When: Checking empty threshold list
        crossed = monitor.check_thresholds(duration_minutes=[])

        # Then: Should return empty list
        assert crossed == []

    def test_handles_unsorted_threshold_list(self):
        """check_thresholds works correctly even with unsorted threshold list."""
        # Given: A phase started 12 minutes ago
        started_at = (datetime.now(timezone.utc) - timedelta(minutes=12)).isoformat()
        monitor = TimeoutMonitor(started_at=started_at)

        # When: Checking unsorted thresholds [15, 5, 10] minutes
        crossed = monitor.check_thresholds(duration_minutes=[15, 5, 10])

        # Then: Should return crossed thresholds in order [5, 10]
        assert crossed == [5, 10]


class TestTimeoutMonitorEdgeCases:
    """Test edge cases and error handling."""

    def test_handles_future_started_at_timestamp(self):
        """TimeoutMonitor handles future timestamps gracefully (returns 0 or negative)."""
        # Given: A timestamp in the future
        started_at = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
        monitor = TimeoutMonitor(started_at=started_at)

        # When: Getting elapsed seconds
        elapsed = monitor.get_elapsed_seconds()

        # Then: Should return 0 or negative value
        assert elapsed <= 0, f"Expected <=0 seconds for future timestamp, got {elapsed}"

    def test_raises_error_for_invalid_timestamp_format(self):
        """TimeoutMonitor raises ValueError for invalid timestamp format."""
        # Given: An invalid timestamp format
        invalid_timestamp = "not-a-valid-timestamp"

        # When/Then: Creating TimeoutMonitor should raise ValueError
        with pytest.raises(ValueError):
            TimeoutMonitor(started_at=invalid_timestamp)

    def test_handles_none_started_at(self):
        """TimeoutMonitor raises ValueError for None started_at."""
        # When/Then: Creating TimeoutMonitor with None should raise ValueError
        with pytest.raises(ValueError):
            TimeoutMonitor(started_at=None)
