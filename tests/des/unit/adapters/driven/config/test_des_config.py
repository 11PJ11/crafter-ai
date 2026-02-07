"""
Unit tests for DESConfig configuration loader.

Tests DESConfig behavior from driving port perspective (public interface):
- Configuration loading from YAML file
- Default value fallback when file missing/invalid
- audit_logging_enabled setting access
"""

import yaml


class TestDESConfigLoadsValidConfiguration:
    """Test DESConfig loads configuration from valid YAML file."""

    def test_loads_audit_logging_enabled_true_from_config(self, tmp_path):
        """DESConfig loads audit_logging_enabled=true from valid config file."""
        # Arrange: Create config file with audit_logging_enabled: true
        config_file = tmp_path / ".claude" / "des" / "config.yaml"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        config_content = """# DES Configuration
audit_logging_enabled: true
"""
        config_file.write_text(config_content)

        # Act: Load DESConfig with explicit config path (cross-platform)
        from des.adapters.driven.config.des_config import DESConfig

        config = DESConfig(config_path=config_file)

        # Assert: audit_logging_enabled is True
        assert config.audit_logging_enabled is True

    def test_loads_audit_logging_enabled_false_from_config(self, tmp_path):
        """DESConfig loads audit_logging_enabled=false from valid config file."""
        # Arrange: Create config file with audit_logging_enabled: false
        config_file = tmp_path / ".claude" / "des" / "config.yaml"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        config_content = """# DES Configuration
audit_logging_enabled: false
"""
        config_file.write_text(config_content)

        # Act: Load DESConfig with explicit config path (cross-platform)
        from des.adapters.driven.config.des_config import DESConfig

        config = DESConfig(config_path=config_file)

        # Assert: audit_logging_enabled is False
        assert config.audit_logging_enabled is False


class TestDESConfigFallsBackToSafeDefaults:
    """Test DESConfig falls back to safe defaults when config file missing/invalid."""

    def test_uses_default_true_when_config_file_missing(self, tmp_path):
        """DESConfig defaults to audit_logging_enabled=true when config file missing."""
        # Arrange: Point to a non-existent config file
        config_file = tmp_path / ".claude" / "des" / "config.yaml"

        # Act: Load DESConfig with explicit path (cross-platform)
        from des.adapters.driven.config.des_config import DESConfig

        config = DESConfig(config_path=config_file)

        # Assert: audit_logging_enabled defaults to True (safe default)
        assert config.audit_logging_enabled is True

    def test_uses_default_true_when_yaml_invalid(self, tmp_path):
        """DESConfig defaults to audit_logging_enabled=true when YAML invalid."""
        # Arrange: Create config file with invalid YAML
        config_file = tmp_path / ".claude" / "des" / "config.yaml"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        invalid_yaml = "invalid: yaml: [unclosed"
        config_file.write_text(invalid_yaml)

        # Act: Load DESConfig with explicit path (cross-platform)
        from des.adapters.driven.config.des_config import DESConfig

        config = DESConfig(config_path=config_file)

        # Assert: audit_logging_enabled defaults to True despite invalid YAML
        assert config.audit_logging_enabled is True

    def test_uses_default_true_when_audit_key_missing(self, tmp_path):
        """DESConfig defaults to audit_logging_enabled=true when key missing in config."""
        # Arrange: Create valid YAML but without audit_logging_enabled key
        config_file = tmp_path / ".claude" / "des" / "config.yaml"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        config_content = """# DES Configuration
some_other_setting: value
"""
        config_file.write_text(config_content)

        # Act: Load DESConfig with explicit path (cross-platform)
        from des.adapters.driven.config.des_config import DESConfig

        config = DESConfig(config_path=config_file)

        # Assert: audit_logging_enabled defaults to True when key missing
        assert config.audit_logging_enabled is True


class TestDESConfigCreatesDefaultConfigFile:
    """Test DESConfig creates default config file with comments when missing."""

    def test_creates_config_file_when_missing(self, tmp_path):
        """DESConfig creates config file at ~/.claude/des/config.yaml when missing."""
        # Arrange: Point to a non-existent config file
        config_file = tmp_path / ".claude" / "des" / "config.yaml"

        # Act: Load DESConfig with explicit path (cross-platform)
        from des.adapters.driven.config.des_config import DESConfig

        _ = DESConfig(config_path=config_file)

        # Assert: Config file was created
        assert config_file.exists()

    def test_created_config_includes_comments(self, tmp_path):
        """DESConfig creates config file with explanatory comments."""
        # Arrange: Point to a non-existent config file
        config_file = tmp_path / ".claude" / "des" / "config.yaml"

        # Act: Load DESConfig with explicit path (cross-platform)
        from des.adapters.driven.config.des_config import DESConfig

        _ = DESConfig(config_path=config_file)

        # Assert: Config file contains comments (lines starting with #)
        content = config_file.read_text()
        assert "#" in content
        assert "DES" in content or "Deterministic Execution System" in content

    def test_created_config_has_audit_enabled_true(self, tmp_path):
        """DESConfig creates config file with audit_logging_enabled: true default."""
        # Arrange: Point to a non-existent config file
        config_file = tmp_path / ".claude" / "des" / "config.yaml"

        # Act: Load DESConfig with explicit path (cross-platform)
        from des.adapters.driven.config.des_config import DESConfig

        _ = DESConfig(config_path=config_file)

        # Assert: Created config contains audit_logging_enabled: true
        content = config_file.read_text()
        config_data = yaml.safe_load(content)
        assert config_data.get("audit_logging_enabled") is True
