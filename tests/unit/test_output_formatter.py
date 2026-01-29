"""Unit tests for output_formatter module.

Tests validate terminal error formatting with [ERROR]/[FIX]/[THEN] structure,
ANSI color support, and human-readable error messages for various error types.
"""

import pytest


class TestTerminalErrorStructure:
    """Verify terminal error format uses [ERROR]/[FIX]/[THEN] structure."""

    def test_terminal_error_format_uses_error_fix_then_structure(self):
        """Terminal error output must use [ERROR]/[FIX]/[THEN] prefix structure."""
        from scripts.install.output_formatter import TerminalFormatter
        from scripts.install.error_codes import ENV_NO_VENV

        formatter = TerminalFormatter()
        result = formatter.format_terminal_error(
            error_code=ENV_NO_VENV,
            error_message="No virtual environment detected",
            fix_action="Create a virtual environment using pipenv",
            then_action="Run the installer again",
        )

        # Verify the structure contains all three prefixes
        assert "[ERROR]" in result
        assert "[FIX]" in result
        assert "[THEN]" in result

    def test_terminal_error_format_includes_error_message(self):
        """Terminal error output must include the error message after [ERROR]."""
        from scripts.install.output_formatter import TerminalFormatter
        from scripts.install.error_codes import ENV_NO_VENV

        formatter = TerminalFormatter()
        result = formatter.format_terminal_error(
            error_code=ENV_NO_VENV,
            error_message="No virtual environment detected",
            fix_action="Create a virtual environment",
            then_action="Run the installer",
        )

        assert "No virtual environment detected" in result

    def test_terminal_error_format_includes_fix_action(self):
        """Terminal error output must include the fix action after [FIX]."""
        from scripts.install.output_formatter import TerminalFormatter
        from scripts.install.error_codes import ENV_NO_VENV

        formatter = TerminalFormatter()
        result = formatter.format_terminal_error(
            error_code=ENV_NO_VENV,
            error_message="No virtual environment detected",
            fix_action="Create a virtual environment using pipenv",
            then_action="Run the installer",
        )

        assert "Create a virtual environment using pipenv" in result

    def test_terminal_error_format_includes_then_action(self):
        """Terminal error output must include the then action after [THEN]."""
        from scripts.install.output_formatter import TerminalFormatter
        from scripts.install.error_codes import ENV_NO_VENV

        formatter = TerminalFormatter()
        result = formatter.format_terminal_error(
            error_code=ENV_NO_VENV,
            error_message="No virtual environment detected",
            fix_action="Create a virtual environment",
            then_action="Run the installer again",
        )

        assert "Run the installer again" in result


class TestTerminalErrorWithColors:
    """Verify terminal error format supports ANSI colors."""

    def test_format_terminal_error_with_colors_enabled(self):
        """Terminal error output includes ANSI color codes when colors enabled."""
        from scripts.install.output_formatter import TerminalFormatter
        from scripts.install.error_codes import ENV_NO_VENV

        formatter = TerminalFormatter(use_colors=True)
        result = formatter.format_terminal_error(
            error_code=ENV_NO_VENV,
            error_message="No virtual environment detected",
            fix_action="Create a virtual environment",
            then_action="Run the installer",
        )

        # Should contain ANSI escape codes
        assert "\033[" in result

    def test_format_terminal_error_without_colors(self):
        """Terminal error output excludes ANSI color codes when colors disabled."""
        from scripts.install.output_formatter import TerminalFormatter
        from scripts.install.error_codes import ENV_NO_VENV

        formatter = TerminalFormatter(use_colors=False)
        result = formatter.format_terminal_error(
            error_code=ENV_NO_VENV,
            error_message="No virtual environment detected",
            fix_action="Create a virtual environment",
            then_action="Run the installer",
        )

        # Should NOT contain ANSI escape codes
        assert "\033[" not in result


class TestMissingDependencyError:
    """Verify missing dependency error shows module name in terminal."""

    def test_missing_dependency_error_shows_module_name_in_terminal(self):
        """Missing dependency error must include the module name."""
        from scripts.install.output_formatter import TerminalFormatter

        formatter = TerminalFormatter()
        result = formatter.format_dependency_error(
            module_name="yaml",
            package_name="PyYAML",
        )

        # Should include module name and suggest installation
        assert "yaml" in result
        assert "[ERROR]" in result
        assert "[FIX]" in result
        assert "[THEN]" in result

    def test_missing_dependency_error_includes_package_name(self):
        """Missing dependency error must include the pip package name."""
        from scripts.install.output_formatter import TerminalFormatter

        formatter = TerminalFormatter()
        result = formatter.format_dependency_error(
            module_name="yaml",
            package_name="PyYAML",
        )

        assert "PyYAML" in result

    def test_missing_dependency_error_suggests_pip_install(self):
        """Missing dependency error should suggest pip install command."""
        from scripts.install.output_formatter import TerminalFormatter

        formatter = TerminalFormatter()
        result = formatter.format_dependency_error(
            module_name="yaml",
            package_name="PyYAML",
        )

        # Should suggest installation command
        assert "pip install" in result.lower() or "pipenv install" in result.lower()


class TestPermissionError:
    """Verify permission error provides clear terminal guidance."""

    def test_permission_error_provides_clear_terminal_guidance(self):
        """Permission error must provide clear guidance for resolving access issues."""
        from scripts.install.output_formatter import TerminalFormatter

        formatter = TerminalFormatter()
        result = formatter.format_permission_error(
            path="/home/user/.claude",
            operation="write",
        )

        assert "[ERROR]" in result
        assert "[FIX]" in result
        assert "[THEN]" in result
        assert "/home/user/.claude" in result

    def test_permission_error_includes_operation_type(self):
        """Permission error should mention the failed operation type."""
        from scripts.install.output_formatter import TerminalFormatter

        formatter = TerminalFormatter()
        result = formatter.format_permission_error(
            path="/home/user/.claude",
            operation="write",
        )

        assert "write" in result.lower()

    def test_permission_error_suggests_chmod_or_ownership(self):
        """Permission error should suggest chmod or ownership changes."""
        from scripts.install.output_formatter import TerminalFormatter

        formatter = TerminalFormatter()
        result = formatter.format_permission_error(
            path="/home/user/.claude",
            operation="write",
        )

        # Should suggest permission or ownership fix
        assert "chmod" in result.lower() or "permission" in result.lower()


class TestVenvError:
    """Verify virtual environment error formatting."""

    def test_format_venv_error_includes_error_fix_then_structure(self):
        """Venv error must use [ERROR]/[FIX]/[THEN] structure."""
        from scripts.install.output_formatter import TerminalFormatter

        formatter = TerminalFormatter()
        result = formatter.format_venv_error()

        assert "[ERROR]" in result
        assert "[FIX]" in result
        assert "[THEN]" in result

    def test_format_venv_error_suggests_pipenv_shell(self):
        """Venv error should suggest pipenv shell command."""
        from scripts.install.output_formatter import TerminalFormatter

        formatter = TerminalFormatter()
        result = formatter.format_venv_error()

        assert "pipenv" in result.lower()


class TestModuleImportability:
    """Verify the module is importable and well-structured."""

    def test_output_formatter_module_importable(self):
        """The output_formatter module must be importable."""
        try:
            from scripts.install import output_formatter

            assert output_formatter is not None
        except ImportError as e:
            pytest.fail(f"output_formatter module should be importable: {e}")

    def test_terminal_formatter_class_defined(self):
        """TerminalFormatter class must be defined."""
        from scripts.install import output_formatter

        assert hasattr(output_formatter, "TerminalFormatter"), (
            "TerminalFormatter class must be defined"
        )

    def test_terminal_formatter_has_format_terminal_error(self):
        """TerminalFormatter must have format_terminal_error method."""
        from scripts.install.output_formatter import TerminalFormatter

        assert hasattr(TerminalFormatter, "format_terminal_error"), (
            "format_terminal_error method must be defined"
        )

    def test_terminal_formatter_has_format_dependency_error(self):
        """TerminalFormatter must have format_dependency_error method."""
        from scripts.install.output_formatter import TerminalFormatter

        assert hasattr(TerminalFormatter, "format_dependency_error"), (
            "format_dependency_error method must be defined"
        )

    def test_terminal_formatter_has_format_permission_error(self):
        """TerminalFormatter must have format_permission_error method."""
        from scripts.install.output_formatter import TerminalFormatter

        assert hasattr(TerminalFormatter, "format_permission_error"), (
            "format_permission_error method must be defined"
        )

    def test_terminal_formatter_has_format_venv_error(self):
        """TerminalFormatter must have format_venv_error method."""
        from scripts.install.output_formatter import TerminalFormatter

        assert hasattr(TerminalFormatter, "format_venv_error"), (
            "format_venv_error method must be defined"
        )
