"""
Unit tests for RCVersion value object.

Tests RC version parsing, creation, and manipulation.
RC version format: {base}-rc.{branch}.{YYYYMMDD}.{N}

Acceptance criteria:
- RCVersion.create("1.2.3", "main", date(2026,1,27), 1) == "1.2.3-rc.main.20260127.1"
- RCVersion.parse("1.2.3-rc.feature-new-agent.20260127.2").build_number == 2
- Branch names with "/" are normalized to "-"
"""

from datetime import date

import pytest

from nWave.core.versioning.domain.rc_version import RCVersion


class TestRCVersionCreateWithMainBranch:
    """Tests for creating RC versions with main branch."""

    def test_create_rc_version_with_main_branch(self):
        """Create RC version with main branch produces correct format."""
        rc_version = RCVersion.create("1.2.3", "main", date(2026, 1, 27), 1)

        assert str(rc_version) == "1.2.3-rc.main.20260127.1"

    def test_acceptance_criteria_main_branch_creation(self):
        """Acceptance criteria: RCVersion.create("1.2.3", "main", date(2026,1,27), 1) == "1.2.3-rc.main.20260127.1"."""
        rc_version = RCVersion.create("1.2.3", "main", date(2026, 1, 27), 1)

        assert str(rc_version) == "1.2.3-rc.main.20260127.1"

    def test_create_rc_version_with_different_date(self):
        """Create RC version with different date formats correctly."""
        rc_version = RCVersion.create("2.0.0", "main", date(2025, 12, 1), 5)

        assert str(rc_version) == "2.0.0-rc.main.20251201.5"

    def test_create_rc_version_with_master_branch(self):
        """Create RC version with master branch."""
        rc_version = RCVersion.create("1.0.0", "master", date(2026, 1, 28), 1)

        assert str(rc_version) == "1.0.0-rc.master.20260128.1"


class TestRCVersionCreateWithFeatureBranch:
    """Tests for creating RC versions with feature branches."""

    def test_create_rc_version_with_simple_feature_branch(self):
        """Create RC version with simple feature branch name."""
        rc_version = RCVersion.create("1.2.3", "feature-new-agent", date(2026, 1, 27), 2)

        assert str(rc_version) == "1.2.3-rc.feature-new-agent.20260127.2"

    def test_create_rc_version_with_hyphenated_branch_name(self):
        """Create RC version with hyphenated branch name."""
        rc_version = RCVersion.create("1.5.0", "bugfix-critical-issue", date(2026, 2, 15), 3)

        assert str(rc_version) == "1.5.0-rc.bugfix-critical-issue.20260215.3"

    def test_create_rc_version_with_number_in_branch_name(self):
        """Create RC version with numbers in branch name."""
        rc_version = RCVersion.create("1.2.3", "issue-123-fix", date(2026, 1, 27), 1)

        assert str(rc_version) == "1.2.3-rc.issue-123-fix.20260127.1"


class TestRCVersionParseValidString:
    """Tests for parsing valid RC version strings."""

    def test_parse_rc_version_string(self):
        """Parse valid RC version string."""
        rc_version = RCVersion.parse("1.2.3-rc.main.20260127.1")

        assert rc_version is not None

    def test_parse_extracts_base_version(self):
        """Parse extracts the base version string."""
        rc_version = RCVersion.parse("1.2.3-rc.main.20260127.1")

        assert rc_version.base_version == "1.2.3"

    def test_parse_extracts_branch_name(self):
        """Parse extracts the branch name."""
        rc_version = RCVersion.parse("1.2.3-rc.main.20260127.1")

        assert rc_version.branch == "main"

    def test_parse_rc_version_with_feature_branch(self):
        """Parse RC version with feature branch name."""
        rc_version = RCVersion.parse("1.2.3-rc.feature-new-agent.20260127.2")

        assert rc_version.branch == "feature-new-agent"


class TestRCVersionParseInvalidRaisesError:
    """Tests for invalid RC version string handling."""

    def test_parse_empty_string_raises_value_error(self):
        """Empty string raises ValueError."""
        with pytest.raises(ValueError, match="Invalid RC version"):
            RCVersion.parse("")

    def test_parse_non_rc_version_raises_value_error(self):
        """Non-RC version string raises ValueError."""
        with pytest.raises(ValueError, match="Invalid RC version"):
            RCVersion.parse("1.2.3")

    def test_parse_malformed_rc_string_raises_value_error(self):
        """Malformed RC string raises ValueError."""
        with pytest.raises(ValueError, match="Invalid RC version"):
            RCVersion.parse("1.2.3-rc-invalid")

    def test_parse_invalid_date_format_raises_value_error(self):
        """RC version with invalid date format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid RC version"):
            RCVersion.parse("1.2.3-rc.main.2026-01-27.1")

    def test_parse_missing_build_number_raises_value_error(self):
        """RC version without build number raises ValueError."""
        with pytest.raises(ValueError, match="Invalid RC version"):
            RCVersion.parse("1.2.3-rc.main.20260127")


class TestRCVersionBranchNameNormalization:
    """Tests for branch name normalization (/ to -)."""

    def test_slash_in_branch_name_normalized_to_hyphen(self):
        """Branch name with slash is normalized to hyphen."""
        rc_version = RCVersion.create("1.2.3", "feature/new-agent", date(2026, 1, 27), 1)

        assert rc_version.branch == "feature-new-agent"
        assert str(rc_version) == "1.2.3-rc.feature-new-agent.20260127.1"

    def test_acceptance_criteria_branch_normalization(self):
        """Acceptance criteria: Branch names with "/" are normalized to "-"."""
        rc_version = RCVersion.create("1.0.0", "feature/my-feature", date(2026, 1, 28), 1)

        assert "/" not in str(rc_version)
        assert rc_version.branch == "feature-my-feature"

    def test_multiple_slashes_normalized(self):
        """Multiple slashes in branch name are all normalized."""
        rc_version = RCVersion.create("1.2.3", "feature/sub/branch", date(2026, 1, 27), 1)

        assert rc_version.branch == "feature-sub-branch"

    def test_branch_without_slash_unchanged(self):
        """Branch name without slash remains unchanged."""
        rc_version = RCVersion.create("1.2.3", "main", date(2026, 1, 27), 1)

        assert rc_version.branch == "main"


class TestRCVersionBuildNumberExtraction:
    """Tests for extracting build number from RC versions."""

    def test_extract_build_number_one(self):
        """Extract build number 1 from RC version."""
        rc_version = RCVersion.parse("1.2.3-rc.main.20260127.1")

        assert rc_version.build_number == 1

    def test_acceptance_criteria_build_number_extraction(self):
        """Acceptance criteria: RCVersion.parse("1.2.3-rc.feature-new-agent.20260127.2").build_number == 2."""
        rc_version = RCVersion.parse("1.2.3-rc.feature-new-agent.20260127.2")

        assert rc_version.build_number == 2

    def test_extract_large_build_number(self):
        """Extract large build number from RC version."""
        rc_version = RCVersion.parse("1.2.3-rc.main.20260127.99")

        assert rc_version.build_number == 99

    def test_build_number_from_created_version(self):
        """Build number accessible from created RC version."""
        rc_version = RCVersion.create("1.2.3", "main", date(2026, 1, 27), 5)

        assert rc_version.build_number == 5


class TestRCVersionDateExtraction:
    """Tests for extracting date from RC versions."""

    def test_extract_date_from_rc_version(self):
        """Extract date from parsed RC version."""
        rc_version = RCVersion.parse("1.2.3-rc.main.20260127.1")

        assert rc_version.build_date == date(2026, 1, 27)

    def test_extract_date_different_month(self):
        """Extract date with different month."""
        rc_version = RCVersion.parse("1.2.3-rc.main.20251201.1")

        assert rc_version.build_date == date(2025, 12, 1)

    def test_date_from_created_version(self):
        """Date accessible from created RC version."""
        build_date = date(2026, 2, 15)
        rc_version = RCVersion.create("1.2.3", "main", build_date, 1)

        assert rc_version.build_date == build_date

    def test_date_formatted_correctly_in_string(self):
        """Date formatted as YYYYMMDD in string representation."""
        rc_version = RCVersion.create("1.2.3", "main", date(2026, 3, 5), 1)

        assert "20260305" in str(rc_version)


class TestRCVersionIncrementBuildNumber:
    """Tests for incrementing build number."""

    def test_increment_build_number(self):
        """Increment build number creates new RC version with incremented number."""
        rc_version = RCVersion.parse("1.2.3-rc.main.20260127.1")

        incremented = rc_version.increment_build_number()

        assert incremented.build_number == 2

    def test_increment_preserves_base_version(self):
        """Increment build number preserves base version."""
        rc_version = RCVersion.parse("1.2.3-rc.main.20260127.1")

        incremented = rc_version.increment_build_number()

        assert incremented.base_version == "1.2.3"

    def test_increment_preserves_branch(self):
        """Increment build number preserves branch name."""
        rc_version = RCVersion.parse("1.2.3-rc.feature-x.20260127.1")

        incremented = rc_version.increment_build_number()

        assert incremented.branch == "feature-x"

    def test_increment_preserves_date(self):
        """Increment build number preserves build date."""
        rc_version = RCVersion.parse("1.2.3-rc.main.20260127.1")

        incremented = rc_version.increment_build_number()

        assert incremented.build_date == date(2026, 1, 27)

    def test_increment_produces_correct_string(self):
        """Incremented RC version produces correct string."""
        rc_version = RCVersion.parse("1.2.3-rc.main.20260127.1")

        incremented = rc_version.increment_build_number()

        assert str(incremented) == "1.2.3-rc.main.20260127.2"

    def test_increment_returns_new_instance(self):
        """Increment returns a new instance (immutability)."""
        rc_version = RCVersion.parse("1.2.3-rc.main.20260127.1")

        incremented = rc_version.increment_build_number()

        assert rc_version is not incremented
        assert rc_version.build_number == 1


class TestRCVersionEquality:
    """Tests for RCVersion equality comparison."""

    def test_equal_rc_versions(self):
        """Identical RC versions are equal."""
        v1 = RCVersion.parse("1.2.3-rc.main.20260127.1")
        v2 = RCVersion.parse("1.2.3-rc.main.20260127.1")

        assert v1 == v2

    def test_different_build_numbers_not_equal(self):
        """RC versions with different build numbers are not equal."""
        v1 = RCVersion.parse("1.2.3-rc.main.20260127.1")
        v2 = RCVersion.parse("1.2.3-rc.main.20260127.2")

        assert v1 != v2

    def test_different_branches_not_equal(self):
        """RC versions with different branches are not equal."""
        v1 = RCVersion.parse("1.2.3-rc.main.20260127.1")
        v2 = RCVersion.parse("1.2.3-rc.develop.20260127.1")

        assert v1 != v2

    def test_created_equals_parsed(self):
        """Created RC version equals parsed identical string."""
        created = RCVersion.create("1.2.3", "main", date(2026, 1, 27), 1)
        parsed = RCVersion.parse("1.2.3-rc.main.20260127.1")

        assert created == parsed


class TestRCVersionHashable:
    """Tests for RCVersion being hashable."""

    def test_rc_version_is_hashable(self):
        """RCVersion can be hashed."""
        rc_version = RCVersion.parse("1.2.3-rc.main.20260127.1")

        assert isinstance(hash(rc_version), int)

    def test_equal_rc_versions_have_same_hash(self):
        """Equal RC versions have the same hash."""
        v1 = RCVersion.parse("1.2.3-rc.main.20260127.1")
        v2 = RCVersion.parse("1.2.3-rc.main.20260127.1")

        assert hash(v1) == hash(v2)

    def test_rc_version_usable_in_set(self):
        """RC versions can be stored in sets."""
        rc_versions = {
            RCVersion.parse("1.2.3-rc.main.20260127.1"),
            RCVersion.parse("1.2.3-rc.main.20260127.1"),
            RCVersion.parse("1.2.3-rc.main.20260127.2"),
        }

        assert len(rc_versions) == 2
