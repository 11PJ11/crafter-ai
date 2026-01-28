"""
Unit tests for BackupPolicy domain service.

Tests rolling retention rules (maximum 3 backups) and backup path generation.

HEXAGONAL ARCHITECTURE:
- BackupPolicy is a DOMAIN SERVICE (pure business logic)
- NO mocking of domain classes allowed
- Tests use real objects exclusively
"""

from datetime import datetime
from pathlib import Path


class TestBackupPolicyRetention:
    """Tests for backup retention rules (maximum 3 backups)."""

    def test_backup_policy_returns_empty_when_exactly_at_limit(self):
        """
        GIVEN: 3 existing backup paths (exactly at max_backups limit)
        WHEN: Determining which backups to delete
        THEN: Returns empty list (no deletion needed when at limit)

        NOTE: This tests the "keep exactly N" behavior. When count == max,
        no deletion needed. Deletion only happens when count > max.
        """
        # ARRANGE
        from nWave.core.versioning.domain.backup_policy import BackupPolicy

        policy = BackupPolicy(max_backups=3)
        existing_backups = [
            Path("~/.claude.backup.20260125120000"),
            Path("~/.claude.backup.20260126120000"),
            Path("~/.claude.backup.20260127120000"),
        ]

        # ACT
        to_delete = policy.get_backups_to_delete(existing_backups)

        # ASSERT - At limit, nothing to delete
        assert len(to_delete) == 0
        assert to_delete == []

    def test_backup_policy_returns_empty_when_less_than_3(self):
        """
        GIVEN: 2 existing backup paths (below retention limit)
        WHEN: Determining which backups to delete
        THEN: Returns empty list (no deletion needed)
        """
        # ARRANGE
        from nWave.core.versioning.domain.backup_policy import BackupPolicy

        policy = BackupPolicy(max_backups=3)
        existing_backups = [
            Path("~/.claude.backup.20260126120000"),
            Path("~/.claude.backup.20260127120000"),
        ]

        # ACT
        to_delete = policy.get_backups_to_delete(existing_backups)

        # ASSERT
        assert to_delete == []

    def test_backup_policy_handles_empty_backup_list(self):
        """
        GIVEN: No existing backups
        WHEN: Determining which backups to delete
        THEN: Returns empty list
        """
        # ARRANGE
        from nWave.core.versioning.domain.backup_policy import BackupPolicy

        policy = BackupPolicy(max_backups=3)
        existing_backups: list[Path] = []

        # ACT
        to_delete = policy.get_backups_to_delete(existing_backups)

        # ASSERT
        assert to_delete == []

    def test_backup_policy_sorts_by_timestamp(self):
        """
        GIVEN: 4 existing backups in unsorted order (1 over limit)
        WHEN: Determining which backups to delete
        THEN: Returns 1 oldest backup for deletion (to keep exactly 3)

        The backups are provided in unsorted order to verify sorting works.
        """
        # ARRANGE
        from nWave.core.versioning.domain.backup_policy import BackupPolicy

        policy = BackupPolicy(max_backups=3)
        existing_backups = [
            Path("~/.claude.backup.20260127120000"),  # newest
            Path("~/.claude.backup.20260124120000"),  # oldest - should be deleted
            Path("~/.claude.backup.20260125120000"),
            Path("~/.claude.backup.20260126120000"),
        ]

        # ACT
        to_delete = policy.get_backups_to_delete(existing_backups)

        # ASSERT
        # With 4 backups and max 3, delete 1 oldest to keep exactly 3
        assert len(to_delete) == 1
        assert to_delete[0] == Path("~/.claude.backup.20260124120000")


class TestBackupPolicyRotationAfterUpdate:
    """
    Tests for backup rotation AFTER a new backup has been created.

    Step 04-08 scenario: Backup rotation maintains exactly 3 copies
    - Given 3 existing backups + 1 new backup created = 4 total
    - When rotation runs
    - Then exactly 1 oldest should be deleted
    - And exactly 3 backups remain
    """

    def test_backup_policy_deletes_only_1_when_4_exist_and_max_is_3(self):
        """
        GIVEN: 4 existing backups (3 original + 1 new from current update)
        WHEN: Determining which backups to delete
        THEN: Returns exactly 1 oldest backup for deletion
        AND: Exactly 3 backups will remain after deletion
        """
        # ARRANGE
        from nWave.core.versioning.domain.backup_policy import BackupPolicy

        policy = BackupPolicy(max_backups=3)
        existing_backups = [
            Path("~/.claude.backup.20260124120000"),  # oldest - should be deleted
            Path("~/.claude.backup.20260125120000"),  # should remain
            Path("~/.claude.backup.20260126120000"),  # should remain
            Path("~/.claude.backup.20260127120000"),  # newest - should remain
        ]

        # ACT
        to_delete = policy.get_backups_to_delete(existing_backups)

        # ASSERT
        assert len(to_delete) == 1, (
            f"With 4 backups and max 3, should delete exactly 1 to keep 3. Got {len(to_delete)}"
        )
        assert to_delete[0] == Path("~/.claude.backup.20260124120000"), (
            "Should delete the oldest backup (20260124)"
        )

        # Verify 3 remain after deletion
        remaining = [b for b in existing_backups if b not in to_delete]
        assert len(remaining) == 3, (
            f"Exactly 3 backups should remain, got {len(remaining)}"
        )

    def test_backup_policy_deletes_2_when_5_exist_and_max_is_3(self):
        """
        GIVEN: 5 existing backups (edge case: 2 over limit)
        WHEN: Determining which backups to delete
        THEN: Returns exactly 2 oldest backups for deletion
        AND: Exactly 3 backups will remain after deletion
        """
        # ARRANGE
        from nWave.core.versioning.domain.backup_policy import BackupPolicy

        policy = BackupPolicy(max_backups=3)
        existing_backups = [
            Path("~/.claude.backup.20260123120000"),  # oldest - should be deleted
            Path(
                "~/.claude.backup.20260124120000"
            ),  # second oldest - should be deleted
            Path("~/.claude.backup.20260125120000"),  # should remain
            Path("~/.claude.backup.20260126120000"),  # should remain
            Path("~/.claude.backup.20260127120000"),  # newest - should remain
        ]

        # ACT
        to_delete = policy.get_backups_to_delete(existing_backups)

        # ASSERT
        assert len(to_delete) == 2, (
            f"With 5 backups and max 3, should delete exactly 2 to keep 3. Got {len(to_delete)}"
        )
        assert to_delete[0] == Path("~/.claude.backup.20260123120000")
        assert to_delete[1] == Path("~/.claude.backup.20260124120000")

        # Verify 3 remain after deletion
        remaining = [b for b in existing_backups if b not in to_delete]
        assert len(remaining) == 3, (
            f"Exactly 3 backups should remain, got {len(remaining)}"
        )


class TestBackupPolicyPathGeneration:
    """Tests for backup path generation with timestamps."""

    def test_backup_policy_generates_timestamp_path(self):
        """
        GIVEN: A specific datetime
        WHEN: Generating a backup path
        THEN: Returns path with timestamp in YYYYMMDDHHMMSS format
        """
        # ARRANGE
        from nWave.core.versioning.domain.backup_policy import BackupPolicy

        policy = BackupPolicy(max_backups=3)
        timestamp = datetime(2026, 1, 28, 14, 30, 45)

        # ACT
        backup_path = policy.generate_backup_path(timestamp)

        # ASSERT
        assert backup_path == Path("~/.claude.backup.20260128143045")

    def test_backup_policy_path_format_is_correct(self):
        """
        GIVEN: A datetime with various values
        WHEN: Generating a backup path
        THEN: Path follows ~/.claude.backup.{YYYYMMDDHHMMSS}/ format
        """
        # ARRANGE
        from nWave.core.versioning.domain.backup_policy import BackupPolicy

        policy = BackupPolicy(max_backups=3)
        timestamp = datetime(2026, 12, 31, 23, 59, 59)

        # ACT
        backup_path = policy.generate_backup_path(timestamp)

        # ASSERT
        path_str = str(backup_path)
        assert path_str.startswith("~/.claude.backup.")
        assert path_str.endswith("20261231235959")
        assert len("20261231235959") == 14  # YYYYMMDDHHMMSS

    def test_backup_policy_path_uses_current_time_when_no_timestamp(self):
        """
        GIVEN: No timestamp provided
        WHEN: Generating a backup path
        THEN: Uses current time for path generation
        """
        # ARRANGE
        from nWave.core.versioning.domain.backup_policy import BackupPolicy

        policy = BackupPolicy(max_backups=3)
        before = datetime.now().replace(microsecond=0)

        # ACT
        backup_path = policy.generate_backup_path()

        # ASSERT
        after = datetime.now().replace(microsecond=0)
        path_str = str(backup_path)
        assert path_str.startswith("~/.claude.backup.")

        # Extract timestamp from path and verify it's between before and after
        # Note: Using replace(microsecond=0) because path format has second precision
        timestamp_str = path_str.split(".")[-1]
        path_timestamp = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")
        assert before <= path_timestamp <= after
