"""
Unit tests for VersionComparator - semantic version comparison.

Business behavior: Detect major, minor, patch version changes.
"""

import pytest
from nWave.core.version_management.version_comparator import VersionComparator


class TestVersionComparatorShould:
    """Behavior specifications for version comparison logic."""

    def test_detect_major_version_bump_when_major_increases(self):
        """Major version bump detected when first number increases."""
        comparator = VersionComparator()

        result = comparator.is_major_update("1.5.7", "2.0.0")

        assert result is True, "Should detect major version bump from 1.x to 2.x"

    def test_detect_no_major_bump_when_only_minor_increases(self):
        """No major version bump when only minor version increases."""
        comparator = VersionComparator()

        result = comparator.is_major_update("1.5.7", "1.6.0")

        assert result is False, "Should not detect major bump for minor version change"

    def test_detect_no_major_bump_when_only_patch_increases(self):
        """No major version bump when only patch version increases."""
        comparator = VersionComparator()

        result = comparator.is_major_update("1.5.7", "1.5.8")

        assert result is False, "Should not detect major bump for patch version change"

    def test_handle_version_strings_with_v_prefix(self):
        """Handle version strings with 'v' prefix (e.g., v1.0.0)."""
        comparator = VersionComparator()

        result = comparator.is_major_update("v1.5.7", "v2.0.0")

        assert result is True, "Should handle 'v' prefix in version strings"
