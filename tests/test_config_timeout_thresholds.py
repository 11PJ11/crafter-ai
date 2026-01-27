"""
Unit tests for timeout threshold configuration in ConfigManager.

Tests configuration support for:
- duration_minutes field
- threshold percentages at 50%, 75%, 90%
- per-task-type thresholds (quick/standard/complex)
- validation of threshold ordering
"""

import tempfile
from pathlib import Path
import yaml
from tools.utils.config_manager import ConfigManager


class TestTimeoutThresholdConfiguration:
    """Test timeout threshold configuration functionality."""

    def create_config_file(self, config_data):
        """Helper to create temporary config file."""
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
        yaml.dump(config_data, temp_file)
        temp_file.flush()
        return Path(temp_file.name)

    def test_configuration_supports_duration_minutes(self):
        """Configuration should support duration_minutes field."""
        # Given: A configuration with duration_minutes in task_types
        config_data = {"task_types": {"standard": {"duration_minutes": 120}}}
        config_file = self.create_config_file(config_data)

        # When: Loading configuration through ConfigManager
        config_manager = ConfigManager(config_file)
        standard_config = config_manager.get_task_type_config("standard")

        # Then: duration_minutes should be accessible
        assert standard_config is not None
        assert "duration_minutes" in standard_config
        assert standard_config["duration_minutes"] == 120

        # Cleanup
        config_file.unlink()

    def test_configuration_supports_threshold_percentages(self):
        """Configuration should support threshold percentages at 50%, 75%, 90%."""
        # Given: A configuration with threshold percentages
        config_data = {
            "task_types": {
                "standard": {
                    "duration_minutes": 120,
                    "thresholds": {
                        "warning_50": 60,
                        "warning_75": 90,
                        "warning_90": 108,
                    },
                }
            }
        }
        config_file = self.create_config_file(config_data)

        # When: Loading configuration through ConfigManager
        config_manager = ConfigManager(config_file)
        standard_config = config_manager.get_task_type_config("standard")

        # Then: All three thresholds should be accessible
        assert standard_config is not None
        assert "thresholds" in standard_config
        thresholds = standard_config["thresholds"]
        assert thresholds["warning_50"] == 60
        assert thresholds["warning_75"] == 90
        assert thresholds["warning_90"] == 108

        # Cleanup
        config_file.unlink()

    def test_thresholds_configurable_per_task_type_quick(self):
        """Thresholds should be configurable for quick task type."""
        # Given: A configuration with quick task thresholds
        config_data = {
            "task_types": {
                "quick": {
                    "duration_minutes": 30,
                    "thresholds": {
                        "warning_50": 15,
                        "warning_75": 23,
                        "warning_90": 27,
                    },
                }
            }
        }
        config_file = self.create_config_file(config_data)

        # When: Retrieving quick task configuration
        config_manager = ConfigManager(config_file)
        quick_config = config_manager.get_task_type_config("quick")

        # Then: Quick task thresholds should be accessible
        assert quick_config is not None
        assert quick_config["duration_minutes"] == 30
        assert quick_config["thresholds"]["warning_50"] == 15
        assert quick_config["thresholds"]["warning_75"] == 23
        assert quick_config["thresholds"]["warning_90"] == 27

        # Cleanup
        config_file.unlink()

    def test_thresholds_configurable_per_task_type_standard(self):
        """Thresholds should be configurable for standard task type."""
        # Given: A configuration with standard task thresholds
        config_data = {
            "task_types": {
                "standard": {
                    "duration_minutes": 120,
                    "thresholds": {
                        "warning_50": 60,
                        "warning_75": 90,
                        "warning_90": 108,
                    },
                }
            }
        }
        config_file = self.create_config_file(config_data)

        # When: Retrieving standard task configuration
        config_manager = ConfigManager(config_file)
        standard_config = config_manager.get_task_type_config("standard")

        # Then: Standard task thresholds should be accessible
        assert standard_config is not None
        assert standard_config["duration_minutes"] == 120
        assert standard_config["thresholds"]["warning_50"] == 60
        assert standard_config["thresholds"]["warning_75"] == 90
        assert standard_config["thresholds"]["warning_90"] == 108

        # Cleanup
        config_file.unlink()

    def test_thresholds_configurable_per_task_type_complex(self):
        """Thresholds should be configurable for complex task type."""
        # Given: A configuration with complex task thresholds
        config_data = {
            "task_types": {
                "complex": {
                    "duration_minutes": 480,
                    "thresholds": {
                        "warning_50": 240,
                        "warning_75": 360,
                        "warning_90": 432,
                    },
                }
            }
        }
        config_file = self.create_config_file(config_data)

        # When: Retrieving complex task configuration
        config_manager = ConfigManager(config_file)
        complex_config = config_manager.get_task_type_config("complex")

        # Then: Complex task thresholds should be accessible
        assert complex_config is not None
        assert complex_config["duration_minutes"] == 480
        assert complex_config["thresholds"]["warning_50"] == 240
        assert complex_config["thresholds"]["warning_75"] == 360
        assert complex_config["thresholds"]["warning_90"] == 432

        # Cleanup
        config_file.unlink()

    def test_validation_ensures_thresholds_in_ascending_order(self):
        """Validation should ensure threshold percentages are in ascending order."""
        # Given: A configuration with thresholds NOT in ascending order
        config_data = {
            "task_types": {
                "invalid": {
                    "duration_minutes": 120,
                    "thresholds": {
                        "warning_50": 90,  # Wrong: 90 > 75
                        "warning_75": 60,  # Wrong: 60 < 90
                        "warning_90": 108,
                    },
                }
            }
        }
        config_file = self.create_config_file(config_data)

        # When: Validating configuration
        config_manager = ConfigManager(config_file)
        invalid_config = config_manager.get_task_type_config("invalid")
        errors = config_manager.validate_threshold_ordering(
            invalid_config["thresholds"]
        )

        # Then: Validation should detect out-of-order thresholds
        assert len(errors) > 0
        assert any("warning_50" in error and "warning_75" in error for error in errors)

        # Cleanup
        config_file.unlink()

    def test_validation_passes_with_correct_threshold_order(self):
        """Validation should pass when thresholds are in correct ascending order."""
        # Given: A configuration with thresholds in correct ascending order
        config_data = {
            "task_types": {
                "valid": {
                    "duration_minutes": 120,
                    "thresholds": {
                        "warning_50": 60,
                        "warning_75": 90,
                        "warning_90": 108,
                    },
                }
            }
        }
        config_file = self.create_config_file(config_data)

        # When: Validating configuration
        config_manager = ConfigManager(config_file)
        valid_config = config_manager.get_task_type_config("valid")
        errors = config_manager.validate_threshold_ordering(valid_config["thresholds"])

        # Then: Validation should pass (no errors)
        assert len(errors) == 0

        # Cleanup
        config_file.unlink()
