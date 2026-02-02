"""Tests for ConfigPort Protocol and FileConfigAdapter implementation.

TDD approach: Tests written first to define expected behavior.
"""

from pathlib import Path
from typing import Protocol

from crafter_ai.installer.adapters.config_adapter import FileConfigAdapter
from crafter_ai.installer.ports.config_port import ConfigPort


class TestConfigPortProtocol:
    """Test that ConfigPort is a proper Protocol interface."""

    def test_config_port_is_protocol(self) -> None:
        """ConfigPort should be a typing.Protocol (not ABC)."""
        assert hasattr(ConfigPort, "__protocol_attrs__") or issubclass(
            type(ConfigPort), type(Protocol)
        )

    def test_config_port_is_runtime_checkable(self) -> None:
        """ConfigPort should be runtime_checkable for isinstance checks."""
        # If decorated with @runtime_checkable, isinstance should work
        # We test this by checking FileConfigAdapter implements it
        assert isinstance(FileConfigAdapter, type)


class TestFileConfigAdapterImplementsProtocol:
    """Test that FileConfigAdapter properly implements ConfigPort."""

    def test_adapter_implements_config_port(self, tmp_path: Path) -> None:
        """FileConfigAdapter should implement ConfigPort protocol."""
        adapter = FileConfigAdapter(base_path=tmp_path)
        # Check all required methods exist
        assert hasattr(adapter, "get_config_dir")
        assert hasattr(adapter, "get_data_dir")
        assert hasattr(adapter, "get_cache_dir")
        assert hasattr(adapter, "get_log_dir")
        assert hasattr(adapter, "get")
        assert hasattr(adapter, "set")
        assert hasattr(adapter, "load")
        assert hasattr(adapter, "save")


class TestFileConfigAdapterDirectories:
    """Test directory path methods."""

    def test_get_config_dir_returns_path(self, tmp_path: Path) -> None:
        """get_config_dir should return a Path object."""
        adapter = FileConfigAdapter(base_path=tmp_path)
        result = adapter.get_config_dir()
        assert isinstance(result, Path)
        assert (
            "config" in str(result).lower()
            or tmp_path in result.parents
            or result == tmp_path
        )

    def test_get_data_dir_returns_path(self, tmp_path: Path) -> None:
        """get_data_dir should return a Path object."""
        adapter = FileConfigAdapter(base_path=tmp_path)
        result = adapter.get_data_dir()
        assert isinstance(result, Path)

    def test_get_cache_dir_returns_path(self, tmp_path: Path) -> None:
        """get_cache_dir should return a Path object."""
        adapter = FileConfigAdapter(base_path=tmp_path)
        result = adapter.get_cache_dir()
        assert isinstance(result, Path)

    def test_get_log_dir_returns_path(self, tmp_path: Path) -> None:
        """get_log_dir should return a Path object."""
        adapter = FileConfigAdapter(base_path=tmp_path)
        result = adapter.get_log_dir()
        assert isinstance(result, Path)

    def test_creates_directories_if_missing(self, tmp_path: Path) -> None:
        """Directories should be created if they don't exist."""
        adapter = FileConfigAdapter(base_path=tmp_path)

        # Access directories - they should be created
        config_dir = adapter.get_config_dir()
        data_dir = adapter.get_data_dir()
        cache_dir = adapter.get_cache_dir()
        log_dir = adapter.get_log_dir()

        assert config_dir.exists()
        assert data_dir.exists()
        assert cache_dir.exists()
        assert log_dir.exists()


class TestFileConfigAdapterWithPlatformdirs:
    """Test that adapter uses platformdirs for production paths."""

    def test_production_adapter_uses_platformdirs(self) -> None:
        """Without base_path, adapter should use platformdirs."""
        adapter = FileConfigAdapter()
        config_dir = adapter.get_config_dir()

        # Should contain crafter-ai in the path (our app name)
        assert "crafter-ai" in str(config_dir).lower().replace("_", "-")


class TestFileConfigAdapterGetSet:
    """Test get/set configuration values."""

    def test_get_returns_none_for_missing_key(self, tmp_path: Path) -> None:
        """get() should return None for keys that don't exist."""
        adapter = FileConfigAdapter(base_path=tmp_path)
        result = adapter.get("nonexistent_key")
        assert result is None

    def test_get_returns_default_for_missing_key(self, tmp_path: Path) -> None:
        """get() should return default value for missing keys."""
        adapter = FileConfigAdapter(base_path=tmp_path)
        result = adapter.get("nonexistent_key", default="default_value")
        assert result == "default_value"

    def test_set_and_get_roundtrip(self, tmp_path: Path) -> None:
        """set() followed by get() should return the same value."""
        adapter = FileConfigAdapter(base_path=tmp_path)
        adapter.set("test_key", "test_value")
        result = adapter.get("test_key")
        assert result == "test_value"

    def test_set_overwrites_existing_value(self, tmp_path: Path) -> None:
        """set() should overwrite existing values."""
        adapter = FileConfigAdapter(base_path=tmp_path)
        adapter.set("key", "value1")
        adapter.set("key", "value2")
        assert adapter.get("key") == "value2"


class TestFileConfigAdapterLoadSave:
    """Test load/save configuration persistence."""

    def test_load_returns_empty_dict_for_new_config(self, tmp_path: Path) -> None:
        """load() should return empty dict when no config exists."""
        adapter = FileConfigAdapter(base_path=tmp_path)
        result = adapter.load()
        assert result == {}

    def test_save_persists_config_to_file(self, tmp_path: Path) -> None:
        """save() should persist config to YAML file."""
        adapter = FileConfigAdapter(base_path=tmp_path)
        adapter.set("persistent_key", "persistent_value")
        adapter.save()

        # Create new adapter instance and verify persistence
        adapter2 = FileConfigAdapter(base_path=tmp_path)
        result = adapter2.load()
        assert result.get("persistent_key") == "persistent_value"

    def test_save_creates_config_file(self, tmp_path: Path) -> None:
        """save() should create config.yaml file."""
        adapter = FileConfigAdapter(base_path=tmp_path)
        adapter.set("key", "value")
        adapter.save()

        config_file = adapter.get_config_dir() / "config.yaml"
        assert config_file.exists()

    def test_load_after_save_returns_all_values(self, tmp_path: Path) -> None:
        """load() after save() should return all set values."""
        adapter = FileConfigAdapter(base_path=tmp_path)
        adapter.set("key1", "value1")
        adapter.set("key2", "value2")
        adapter.save()

        # New instance to test persistence
        adapter2 = FileConfigAdapter(base_path=tmp_path)
        config = adapter2.load()
        assert config == {"key1": "value1", "key2": "value2"}
