"""Tests for CandidateVersion domain object.

Tests the BumpType enum, CandidateVersion dataclass, and factory functions
for semantic versioning operations.
"""

from dataclasses import FrozenInstanceError

import pytest

from crafter_ai.installer.domain.candidate_version import (
    BumpType,
    CandidateVersion,
    calculate_next_version,
    create_candidate,
    parse_version,
)


class TestBumpType:
    """Tests for BumpType enum."""

    def test_bump_type_has_major_value(self) -> None:
        """BumpType should have MAJOR value for breaking changes."""
        assert BumpType.MAJOR.value == "major"

    def test_bump_type_has_minor_value(self) -> None:
        """BumpType should have MINOR value for new features."""
        assert BumpType.MINOR.value == "minor"

    def test_bump_type_has_patch_value(self) -> None:
        """BumpType should have PATCH value for fixes."""
        assert BumpType.PATCH.value == "patch"

    def test_bump_type_has_none_value(self) -> None:
        """BumpType should have NONE value for no version bump."""
        assert BumpType.NONE.value == "none"

    def test_bump_type_has_exactly_four_values(self) -> None:
        """BumpType should have exactly four values."""
        expected_count = 4  # MAJOR, MINOR, PATCH, NONE
        assert len(BumpType) == expected_count


class TestParseVersion:
    """Tests for parse_version factory function."""

    def test_parse_version_simple(self) -> None:
        """parse_version should handle simple semver strings."""
        result = parse_version("1.2.3")
        assert result == (1, 2, 3)

    def test_parse_version_zero_patch(self) -> None:
        """parse_version should handle zero patch version."""
        result = parse_version("1.2.0")
        assert result == (1, 2, 0)

    def test_parse_version_zero_minor(self) -> None:
        """parse_version should handle zero minor version."""
        result = parse_version("1.0.0")
        assert result == (1, 0, 0)

    def test_parse_version_initial(self) -> None:
        """parse_version should handle initial 0.x.x versions."""
        result = parse_version("0.1.0")
        assert result == (0, 1, 0)

    def test_parse_version_with_prerelease_suffix(self) -> None:
        """parse_version should strip prerelease suffixes."""
        result = parse_version("1.2.3.dev1")
        assert result == (1, 2, 3)

    def test_parse_version_with_rc_suffix(self) -> None:
        """parse_version should strip rc suffixes."""
        result = parse_version("1.2.3rc1")
        assert result == (1, 2, 3)


class TestCalculateNextVersion:
    """Tests for calculate_next_version factory function."""

    def test_calculate_next_version_major_bump(self) -> None:
        """MAJOR bump should increment major and reset minor/patch."""
        result = calculate_next_version("1.2.3", BumpType.MAJOR)
        assert result == "2.0.0"

    def test_calculate_next_version_minor_bump(self) -> None:
        """MINOR bump should increment minor and reset patch."""
        result = calculate_next_version("1.2.3", BumpType.MINOR)
        assert result == "1.3.0"

    def test_calculate_next_version_patch_bump(self) -> None:
        """PATCH bump should increment patch only."""
        result = calculate_next_version("1.2.3", BumpType.PATCH)
        assert result == "1.2.4"

    def test_calculate_next_version_none_bump(self) -> None:
        """NONE bump should return unchanged version."""
        result = calculate_next_version("1.2.3", BumpType.NONE)
        assert result == "1.2.3"

    def test_calculate_next_version_from_zero(self) -> None:
        """Should handle initial 0.x.x versions correctly."""
        result = calculate_next_version("0.1.0", BumpType.MINOR)
        assert result == "0.2.0"

    def test_calculate_next_version_major_from_zero(self) -> None:
        """MAJOR bump from 0.x.x should go to 1.0.0."""
        result = calculate_next_version("0.9.9", BumpType.MAJOR)
        assert result == "1.0.0"


class TestCandidateVersion:
    """Tests for CandidateVersion dataclass."""

    def test_candidate_version_creation(self) -> None:
        """CandidateVersion should be creatable with all properties."""
        candidate = CandidateVersion(
            current_version="1.2.3",
            bump_type=BumpType.MINOR,
            next_version="1.3.0",
            commit_messages=["feat: add new feature"],
            is_prerelease=False,
            prerelease_suffix=None,
        )

        assert candidate.current_version == "1.2.3"
        assert candidate.bump_type == BumpType.MINOR
        assert candidate.next_version == "1.3.0"
        assert candidate.commit_messages == ["feat: add new feature"]
        assert candidate.is_prerelease is False
        assert candidate.prerelease_suffix is None

    def test_candidate_version_is_frozen(self) -> None:
        """CandidateVersion should be immutable."""
        candidate = CandidateVersion(
            current_version="1.2.3",
            bump_type=BumpType.PATCH,
            next_version="1.2.4",
            commit_messages=["fix: bug fix"],
            is_prerelease=False,
            prerelease_suffix=None,
        )

        with pytest.raises(FrozenInstanceError):
            candidate.current_version = "2.0.0"  # type: ignore[misc]

    def test_candidate_version_prerelease(self) -> None:
        """CandidateVersion should handle prerelease versions."""
        candidate = CandidateVersion(
            current_version="0.1.0",
            bump_type=BumpType.PATCH,
            next_version="0.1.1.dev1",
            commit_messages=["fix: dev fix"],
            is_prerelease=True,
            prerelease_suffix="dev1",
        )

        assert candidate.is_prerelease is True
        assert candidate.prerelease_suffix == "dev1"
        assert candidate.next_version == "0.1.1.dev1"


class TestCreateCandidate:
    """Tests for create_candidate factory function."""

    def test_create_candidate_without_prerelease(self) -> None:
        """create_candidate should create a release version by default."""
        candidate = create_candidate(
            current="1.2.3",
            bump_type=BumpType.MINOR,
            commits=["feat: new feature"],
        )

        assert candidate.current_version == "1.2.3"
        assert candidate.bump_type == BumpType.MINOR
        assert candidate.next_version == "1.3.0"
        assert candidate.commit_messages == ["feat: new feature"]
        assert candidate.is_prerelease is False
        assert candidate.prerelease_suffix is None

    def test_create_candidate_with_prerelease(self) -> None:
        """create_candidate should handle prerelease suffix."""
        candidate = create_candidate(
            current="1.2.3",
            bump_type=BumpType.PATCH,
            commits=["fix: bugfix"],
            prerelease="dev1",
        )

        assert candidate.current_version == "1.2.3"
        assert candidate.bump_type == BumpType.PATCH
        assert candidate.next_version == "1.2.4.dev1"
        assert candidate.is_prerelease is True
        assert candidate.prerelease_suffix == "dev1"

    def test_create_candidate_with_multiple_commits(self) -> None:
        """create_candidate should handle multiple commit messages."""
        commits = [
            "feat!: breaking change",
            "feat: new feature",
            "fix: bug fix",
        ]
        candidate = create_candidate(
            current="1.0.0",
            bump_type=BumpType.MAJOR,
            commits=commits,
        )

        assert candidate.commit_messages == commits
        expected_commits = 3  # breaking, feature, fix
        assert len(candidate.commit_messages) == expected_commits

    def test_create_candidate_with_rc_suffix(self) -> None:
        """create_candidate should handle rc prerelease suffix."""
        candidate = create_candidate(
            current="1.2.3",
            bump_type=BumpType.MINOR,
            commits=["feat: release candidate"],
            prerelease="rc1",
        )

        assert candidate.next_version == "1.3.0rc1"
        assert candidate.is_prerelease is True
        assert candidate.prerelease_suffix == "rc1"
