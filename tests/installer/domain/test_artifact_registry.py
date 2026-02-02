"""Tests for ArtifactRegistry - shared artifact value storage.

This module tests the ArtifactRegistry class which stores and shares
artifact values (paths, strings) between journey stages.
"""

from pathlib import Path

import pytest

from crafter_ai.installer.domain.artifact_registry import ArtifactRegistry


class TestArtifactRegistryBasicOperations:
    """Test basic set/get operations."""

    def test_set_and_get_value(self) -> None:
        """Test setting and getting a value."""
        registry = ArtifactRegistry()
        registry.set("test_key", "test_value")
        assert registry.get("test_key") == "test_value"

    def test_get_returns_none_for_unknown_key(self) -> None:
        """Test get returns None for non-existent key."""
        registry = ArtifactRegistry()
        assert registry.get("unknown_key") is None

    def test_can_store_path_objects(self) -> None:
        """Test storing Path objects."""
        registry = ArtifactRegistry()
        path = Path("/tmp/test/wheel.whl")
        registry.set("wheel", path)
        assert registry.get("wheel") == path
        assert isinstance(registry.get("wheel"), Path)

    def test_can_store_string_values(self) -> None:
        """Test storing string values."""
        registry = ArtifactRegistry()
        registry.set("version", "1.0.0")
        result = registry.get("version")
        assert result == "1.0.0"
        assert isinstance(result, str)


class TestArtifactRegistryGetRequired:
    """Test get_required method."""

    def test_get_required_returns_value_for_existing_key(self) -> None:
        """Test get_required returns value when key exists."""
        registry = ArtifactRegistry()
        registry.set("important", "value")
        assert registry.get_required("important") == "value"

    def test_get_required_raises_key_error_for_missing_key(self) -> None:
        """Test get_required raises KeyError when key missing."""
        registry = ArtifactRegistry()
        with pytest.raises(KeyError) as excinfo:
            registry.get_required("missing_key")
        assert "missing_key" in str(excinfo.value)


class TestArtifactRegistryHas:
    """Test has method."""

    def test_has_returns_true_for_existing_key(self) -> None:
        """Test has returns True when key exists."""
        registry = ArtifactRegistry()
        registry.set("exists", "value")
        assert registry.has("exists") is True

    def test_has_returns_false_for_missing_key(self) -> None:
        """Test has returns False when key does not exist."""
        registry = ArtifactRegistry()
        assert registry.has("not_exists") is False


class TestArtifactRegistryKeys:
    """Test keys method."""

    def test_keys_returns_all_registered_keys(self) -> None:
        """Test keys returns list of all registered keys."""
        registry = ArtifactRegistry()
        registry.set("key1", "value1")
        registry.set("key2", "value2")
        registry.set("key3", "value3")
        keys = registry.keys()
        assert set(keys) == {"key1", "key2", "key3"}

    def test_keys_returns_empty_list_for_empty_registry(self) -> None:
        """Test keys returns empty list when no keys registered."""
        registry = ArtifactRegistry()
        assert registry.keys() == []


class TestArtifactRegistryClear:
    """Test clear method."""

    def test_clear_removes_all_values(self) -> None:
        """Test clear removes all registered values."""
        registry = ArtifactRegistry()
        registry.set("key1", "value1")
        registry.set("key2", "value2")
        registry.clear()
        assert registry.count == 0
        assert registry.get("key1") is None
        assert registry.get("key2") is None


class TestArtifactRegistryCount:
    """Test count property."""

    EXPECTED_COUNT_AFTER_TWO_ENTRIES = 2

    def test_count_returns_number_of_entries(self) -> None:
        """Test count property returns correct number."""
        registry = ArtifactRegistry()
        assert registry.count == 0
        registry.set("key1", "value1")
        assert registry.count == 1
        registry.set("key2", "value2")
        assert registry.count == self.EXPECTED_COUNT_AFTER_TWO_ENTRIES

    def test_count_after_overwrite(self) -> None:
        """Test count doesn't increase when overwriting same key."""
        registry = ArtifactRegistry()
        registry.set("key", "value1")
        registry.set("key", "value2")
        assert registry.count == 1


class TestArtifactRegistryPredefinedKeys:
    """Test predefined key constants."""

    def test_wheel_path_constant_exists(self) -> None:
        """Test WHEEL_PATH constant is defined."""
        assert ArtifactRegistry.WHEEL_PATH == "wheel_path"

    def test_backup_path_constant_exists(self) -> None:
        """Test BACKUP_PATH constant is defined."""
        assert ArtifactRegistry.BACKUP_PATH == "backup_path"

    def test_install_path_constant_exists(self) -> None:
        """Test INSTALL_PATH constant is defined."""
        assert ArtifactRegistry.INSTALL_PATH == "install_path"

    def test_version_constant_exists(self) -> None:
        """Test VERSION constant is defined."""
        assert ArtifactRegistry.VERSION == "version"

    def test_source_constant_exists(self) -> None:
        """Test SOURCE constant is defined."""
        assert ArtifactRegistry.SOURCE == "source"

    def test_predefined_keys_can_be_used_for_storage(self) -> None:
        """Test predefined keys work with set/get."""
        registry = ArtifactRegistry()
        wheel_path = Path("/tmp/wheel.whl")
        registry.set(ArtifactRegistry.WHEEL_PATH, wheel_path)
        assert registry.get(ArtifactRegistry.WHEEL_PATH) == wheel_path
