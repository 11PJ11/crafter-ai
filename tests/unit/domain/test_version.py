"""
Unit tests for Version entity.

Tests semantic version parsing, comparison, and validation.
Acceptance criteria:
- Version("1.3.0") > Version("1.2.3") returns True
- Version("1.2.3-rc.main.20260127.1").is_prerelease returns True
- Invalid version strings raise ValueError
"""

import pytest
from nWave.core.versioning.domain.version import Version


class TestVersionParseValidSemver:
    """Tests for parsing valid semantic version strings."""

    def test_parse_simple_version(self):
        """Parse a simple major.minor.patch version."""
        version = Version("1.2.3")

        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3

    def test_parse_zero_components(self):
        """Parse version with zero components."""
        version = Version("0.0.1")

        assert version.major == 0
        assert version.minor == 0
        assert version.patch == 1

    def test_parse_large_numbers(self):
        """Parse version with large component numbers."""
        version = Version("100.200.300")

        assert version.major == 100
        assert version.minor == 200
        assert version.patch == 300

    def test_string_representation(self):
        """Version string representation matches input."""
        version = Version("1.2.3")

        assert str(version) == "1.2.3"


class TestVersionParseInvalidRaisesValueError:
    """Tests for invalid version string handling."""

    def test_empty_string_raises_value_error(self):
        """Empty string raises ValueError."""
        with pytest.raises(ValueError, match="Invalid version"):
            Version("")

    def test_malformed_string_raises_value_error(self):
        """Malformed string raises ValueError."""
        with pytest.raises(ValueError, match="Invalid version"):
            Version("not-a-version")

    def test_two_components_raises_value_error(self):
        """Version with only two components raises ValueError."""
        with pytest.raises(ValueError, match="Invalid version"):
            Version("1.2")

    def test_four_components_without_prerelease_raises_value_error(self):
        """Version with four numeric components raises ValueError."""
        with pytest.raises(ValueError, match="Invalid version"):
            Version("1.2.3.4")

    def test_negative_numbers_raises_value_error(self):
        """Version with negative numbers raises ValueError."""
        with pytest.raises(ValueError, match="Invalid version"):
            Version("-1.2.3")

    def test_non_numeric_components_raises_value_error(self):
        """Version with non-numeric components raises ValueError."""
        with pytest.raises(ValueError, match="Invalid version"):
            Version("a.b.c")


class TestVersionComparisonGreaterThan:
    """Tests for version greater-than comparison."""

    def test_major_version_greater(self):
        """Higher major version is greater."""
        assert Version("2.0.0") > Version("1.9.9")

    def test_minor_version_greater(self):
        """Higher minor version is greater when major is equal."""
        assert Version("1.3.0") > Version("1.2.3")

    def test_patch_version_greater(self):
        """Higher patch version is greater when major and minor are equal."""
        assert Version("1.2.4") > Version("1.2.3")

    def test_acceptance_criteria_comparison(self):
        """Acceptance criteria: Version("1.3.0") > Version("1.2.3") returns True."""
        assert Version("1.3.0") > Version("1.2.3")


class TestVersionComparisonLessThan:
    """Tests for version less-than comparison."""

    def test_major_version_less(self):
        """Lower major version is less."""
        assert Version("1.9.9") < Version("2.0.0")

    def test_minor_version_less(self):
        """Lower minor version is less when major is equal."""
        assert Version("1.2.3") < Version("1.3.0")

    def test_patch_version_less(self):
        """Lower patch version is less when major and minor are equal."""
        assert Version("1.2.3") < Version("1.2.4")


class TestVersionComparisonEqual:
    """Tests for version equality comparison."""

    def test_equal_versions(self):
        """Identical version strings are equal."""
        assert Version("1.2.3") == Version("1.2.3")

    def test_not_equal_versions(self):
        """Different version strings are not equal."""
        assert Version("1.2.3") != Version("1.2.4")

    def test_equality_reflexive(self):
        """Version equals itself."""
        v = Version("1.2.3")
        assert v == v

    def test_greater_or_equal(self):
        """Greater or equal comparison works."""
        assert Version("1.3.0") >= Version("1.2.3")
        assert Version("1.2.3") >= Version("1.2.3")

    def test_less_or_equal(self):
        """Less or equal comparison works."""
        assert Version("1.2.3") <= Version("1.3.0")
        assert Version("1.2.3") <= Version("1.2.3")


class TestVersionPrereleaseDetection:
    """Tests for pre-release version detection."""

    def test_stable_version_is_not_prerelease(self):
        """Simple version is not a pre-release."""
        version = Version("1.2.3")

        assert version.is_prerelease is False

    def test_rc_version_is_prerelease(self):
        """RC version is a pre-release."""
        version = Version("1.2.3-rc.main.20260127.1")

        assert version.is_prerelease is True

    def test_acceptance_criteria_prerelease_detection(self):
        """Acceptance criteria: Version("1.2.3-rc.main.20260127.1").is_prerelease returns True."""
        version = Version("1.2.3-rc.main.20260127.1")

        assert version.is_prerelease is True

    def test_alpha_version_is_prerelease(self):
        """Alpha version is a pre-release."""
        version = Version("1.2.3-alpha")

        assert version.is_prerelease is True

    def test_beta_version_is_prerelease(self):
        """Beta version is a pre-release."""
        version = Version("1.2.3-beta.1")

        assert version.is_prerelease is True


class TestVersionRcFormatParsing:
    """Tests for RC version format parsing."""

    def test_parse_rc_version_string(self):
        """Parse RC version string extracts base version."""
        version = Version("1.2.3-rc.main.20260127.1")

        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3

    def test_rc_version_prerelease_tag(self):
        """RC version contains prerelease tag."""
        version = Version("1.2.3-rc.main.20260127.1")

        assert version.prerelease == "rc.main.20260127.1"

    def test_rc_version_string_representation(self):
        """RC version string representation includes prerelease."""
        version = Version("1.2.3-rc.main.20260127.1")

        assert str(version) == "1.2.3-rc.main.20260127.1"

    def test_stable_version_compares_greater_than_rc(self):
        """Stable version is greater than same base RC version."""
        stable = Version("1.2.3")
        rc = Version("1.2.3-rc.main.20260127.1")

        assert stable > rc

    def test_rc_version_with_feature_branch(self):
        """RC version with feature branch name parses correctly."""
        version = Version("1.2.3-rc.feature-new-agent.20260127.2")

        assert version.prerelease == "rc.feature-new-agent.20260127.2"
        assert version.is_prerelease is True


class TestVersionHashable:
    """Tests for Version being hashable (usable in sets and as dict keys)."""

    def test_version_is_hashable(self):
        """Version can be hashed."""
        version = Version("1.2.3")
        hash_value = hash(version)

        assert isinstance(hash_value, int)

    def test_equal_versions_have_same_hash(self):
        """Equal versions have the same hash."""
        v1 = Version("1.2.3")
        v2 = Version("1.2.3")

        assert hash(v1) == hash(v2)

    def test_version_usable_in_set(self):
        """Versions can be stored in sets."""
        versions = {Version("1.2.3"), Version("1.2.3"), Version("1.3.0")}

        assert len(versions) == 2

    def test_version_usable_as_dict_key(self):
        """Versions can be used as dictionary keys."""
        version_map = {Version("1.2.3"): "old", Version("1.3.0"): "new"}

        assert version_map[Version("1.2.3")] == "old"
