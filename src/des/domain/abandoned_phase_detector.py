"""
AbandonedPhaseDetector: Domain service for detecting abandoned phase executions.

Identifies phases left in IN_PROGRESS or NOT_EXECUTED states after extended
time periods, indicating agent crash or timeout. Provides recovery guidance.

DOMAIN LANGUAGE:
- Abandoned Phase: Phase in IN_PROGRESS/NOT_EXECUTED beyond timeout threshold
- Stalled Progress: Phase with no turn count change over extended time
- Recovery Suggestion: Actionable guidance (WHY/HOW/ACTION) for junior developers
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class PhaseAbandonmentCheck:
    """Result of checking if a phase is abandoned."""

    is_abandoned: bool
    reason: str  # "timeout", "stalled_turns", "in_progress_no_start", etc.
    time_since_start_minutes: Optional[float]
    message: str


class AbandonedPhaseDetector:
    """
    Detects and reports abandoned phase executions.

    An abandoned phase is one that:
    1. Has been IN_PROGRESS for > 30 minutes without completion
    2. Has been NOT_EXECUTED for > 30 minutes after being started
    3. Has stalled turn count (no progress) for > 20 minutes

    Provides recovery suggestions following WHY/HOW/ACTION pattern.
    """

    DEFAULT_TIMEOUT_MINUTES = 30
    DEFAULT_STALLED_THRESHOLD_MINUTES = 20

    def __init__(self):
        """Initialize detector with default timeout thresholds."""
        pass

    def is_abandoned(
        self,
        phase: Dict[str, Any],
        timeout_minutes: int = DEFAULT_TIMEOUT_MINUTES,
        current_time: Optional[datetime] = None,
    ) -> bool:
        """
        Check if a phase is abandoned due to timeout.

        A phase is abandoned if:
        - Status is IN_PROGRESS or NOT_EXECUTED
        - Started more than timeout_minutes ago
        - Has not completed (ended_at is None)

        Args:
            phase: Phase record with status, started_at, ended_at, turn_count
            timeout_minutes: Threshold for considering phase abandoned (default: 30)
            current_time: Current time for calculation (default: now UTC)

        Returns:
            True if phase is abandoned, False otherwise
        """
        if current_time is None:
            current_time = datetime.now(timezone.utc)

        started_at = self._parse_timestamp(phase.get("started_at"))
        if not started_at:
            return False

        elapsed_minutes = self._calculate_elapsed_minutes_for_timestamp(started_at, current_time)
        if elapsed_minutes is None or elapsed_minutes <= timeout_minutes:
            return False

        status = phase.get("status", "")
        return status in ("IN_PROGRESS", "NOT_EXECUTED")

    def is_abandoned_by_stalled_turn_count(
        self,
        phase: Dict[str, Any],
        stalled_threshold_minutes: int = DEFAULT_STALLED_THRESHOLD_MINUTES,
        current_time: Optional[datetime] = None,
    ) -> bool:
        """
        Check if a phase is abandoned due to stalled turn count.

        A phase has stalled progress if:
        - Status is IN_PROGRESS
        - turn_count is 0 or unchanged from initial state
        - Started more than stalled_threshold_minutes ago

        Args:
            phase: Phase record with status, started_at, turn_count
            stalled_threshold_minutes: Threshold for stalled progress (default: 20)
            current_time: Current time for calculation (default: now UTC)

        Returns:
            True if phase has stalled progress, False otherwise
        """
        if current_time is None:
            current_time = datetime.now(timezone.utc)

        if not self._has_stalled_progress_indicators(phase):
            return False

        started_at = self._parse_timestamp(phase.get("started_at"))
        if not started_at:
            return False

        elapsed_minutes = self._calculate_elapsed_minutes_for_timestamp(started_at, current_time)
        return elapsed_minutes is not None and elapsed_minutes > stalled_threshold_minutes

    def detect_abandoned_phases(
        self,
        phase_execution_log: list,
        timeout_minutes: int = DEFAULT_TIMEOUT_MINUTES,
        current_time: Optional[datetime] = None,
    ) -> list:
        """
        Scan phase execution log and identify all abandoned phases.

        Args:
            phase_execution_log: List of phase records from step file
            timeout_minutes: Threshold for abandonment
            current_time: Current time for calculation

        Returns:
            List of tuples (phase_name, reason, elapsed_minutes) for abandoned phases
        """
        abandoned_phases = []

        for phase in phase_execution_log:
            if self.is_abandoned(phase, timeout_minutes, current_time):
                phase_name = phase.get("phase_name", "UNKNOWN")
                started_at_str = phase.get("started_at")
                elapsed_minutes = self._calculate_elapsed_minutes(started_at_str, current_time)

                abandoned_phases.append(
                    (phase_name, "timeout", elapsed_minutes)
                )
            elif self.is_abandoned_by_stalled_turn_count(phase, timeout_minutes, current_time):
                phase_name = phase.get("phase_name", "UNKNOWN")
                started_at_str = phase.get("started_at")
                elapsed_minutes = self._calculate_elapsed_minutes(started_at_str, current_time)

                abandoned_phases.append(
                    (phase_name, "stalled_turns", elapsed_minutes)
                )

        return abandoned_phases

    def generate_recovery_message(
        self,
        phase: Dict[str, Any],
        reason: str = "timeout",
        step_file_path: str = "steps/unknown.json",
    ) -> str:
        """
        Generate a recovery message for an abandoned phase.

        Follows WHY/HOW/ACTION pattern for junior developer understanding.

        Args:
            phase: Abandoned phase record
            reason: Why abandoned ("timeout", "stalled_turns", etc.)
            step_file_path: Path to step file (for action)

        Returns:
            Recovery message with WHY/HOW/ACTION structure
        """
        phase_name = phase.get("phase_name", "UNKNOWN_PHASE")

        if reason == "timeout":
            why = f"Your {phase_name} phase is stuck IN_PROGRESS. The agent either crashed or timed out, leaving the phase incomplete."
            how = "Resetting the phase status to NOT_EXECUTED lets the system know it can try again from the beginning, ensuring a clean state."
            action = f"Reset {phase_name} status to 'NOT_EXECUTED' in your step file ({step_file_path}), then run `/nw:execute` to retry."

        elif reason == "stalled_turns":
            why = f"Your {phase_name} phase started but never made any progress (turn count stayed at 0), suggesting the agent encountered an immediate error."
            how = "Checking the agent transcript will show you exactly what error happened, so you can fix the root cause before retrying."
            action = f"Review the agent transcript for errors in {phase_name}, fix the issue, reset the phase to NOT_EXECUTED, and retry."

        else:
            why = f"Your {phase_name} phase appears abandoned or stalled."
            how = "Check the agent transcript to understand what happened, then reset the phase to NOT_EXECUTED."
            action = f"Review your step file at {step_file_path} and agent transcript, then retry with `/nw:execute`."

        return f"WHY: {why}\n\nHOW: {how}\n\nACTION: {action}"

    def _has_stalled_progress_indicators(self, phase: Dict[str, Any]) -> bool:
        """Check if phase has indicators of stalled progress."""
        status = phase.get("status", "")
        turn_count = phase.get("turn_count", 0)

        # Stalled if IN_PROGRESS with no progress
        return status == "IN_PROGRESS" and turn_count == 0

    def _parse_timestamp(self, timestamp_str: Optional[str]) -> Optional[datetime]:
        """
        Parse ISO format timestamp string to datetime.

        Args:
            timestamp_str: ISO format timestamp or None

        Returns:
            Parsed datetime or None if invalid
        """
        if not timestamp_str:
            return None

        try:
            if isinstance(timestamp_str, str):
                return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            return timestamp_str
        except (ValueError, AttributeError):
            return None

    def _calculate_elapsed_minutes_for_timestamp(
        self,
        started_at: datetime,
        current_time: datetime,
    ) -> Optional[float]:
        """
        Calculate minutes elapsed since started_at timestamp.

        Args:
            started_at: Start datetime
            current_time: Current time

        Returns:
            Elapsed minutes or None if calculation fails
        """
        try:
            elapsed = current_time - started_at
            return elapsed.total_seconds() / 60
        except (TypeError, AttributeError):
            return None

    def _calculate_elapsed_minutes(
        self,
        started_at_str: Optional[str],
        current_time: Optional[datetime] = None,
    ) -> Optional[float]:
        """
        Calculate minutes elapsed since started_at timestamp (legacy method).

        Args:
            started_at_str: ISO format timestamp string
            current_time: Current time (default: now UTC)

        Returns:
            Elapsed minutes or None if timestamp invalid
        """
        if current_time is None:
            current_time = datetime.now(timezone.utc)

        started_at = self._parse_timestamp(started_at_str)
        if not started_at:
            return None

        return self._calculate_elapsed_minutes_for_timestamp(started_at, current_time)
