"""Tests for BuildPort and SubprocessBuildAdapter.

Tests the hexagonal port/adapter pattern for Python wheel building operations.
All subprocess and file system calls are mocked - no actual builds occur.
"""

from pathlib import Path
from typing import Protocol
from unittest.mock import MagicMock, patch

import pytest

from crafter_ai.installer.adapters.build_adapter import SubprocessBuildAdapter
from crafter_ai.installer.ports.build_port import BuildError, BuildPort


class TestBuildPortProtocol:
    """Tests for BuildPort Protocol definition."""

    def test_build_port_is_protocol(self):
        """BuildPort should be a Protocol class."""
        assert issubclass(BuildPort, Protocol)

    def test_build_port_is_runtime_checkable(self):
        """BuildPort should be runtime_checkable for isinstance checks."""
        # runtime_checkable protocols have __protocol_attrs__
        assert hasattr(BuildPort, "__protocol_attrs__") or hasattr(
            BuildPort, "_is_runtime_protocol"
        )


class TestBuildError:
    """Tests for BuildError exception class."""

    def test_build_error_has_message(self):
        """BuildError should have a message property."""
        error = BuildError("Build failed")
        assert error.message == "Build failed"

    def test_build_error_has_return_code(self):
        """BuildError should have a return_code property."""
        error = BuildError("Build failed", return_code=1)
        assert error.return_code == 1

    def test_build_error_return_code_defaults_to_none(self):
        """BuildError return_code should default to None."""
        error = BuildError("Build failed")
        assert error.return_code is None

    def test_build_error_has_output(self):
        """BuildError should have an output property for captured stderr/stdout."""
        error = BuildError("Build failed", output="error: missing setup.py")
        assert error.output == "error: missing setup.py"

    def test_build_error_output_defaults_to_none(self):
        """BuildError output should default to None."""
        error = BuildError("Build failed")
        assert error.output is None

    def test_build_error_is_exception(self):
        """BuildError should be an Exception subclass."""
        error = BuildError("Build failed")
        assert isinstance(error, Exception)

    def test_build_error_str_includes_message(self):
        """BuildError __str__ should include the message."""
        error = BuildError("Build failed")
        assert "Build failed" in str(error)


class TestSubprocessBuildAdapterImplementsProtocol:
    """Tests that SubprocessBuildAdapter implements BuildPort."""

    def test_adapter_implements_build_port(self):
        """SubprocessBuildAdapter should implement BuildPort protocol."""
        adapter = SubprocessBuildAdapter()
        assert isinstance(adapter, BuildPort)

    def test_adapter_has_build_wheel_method(self):
        """SubprocessBuildAdapter should have build_wheel method."""
        adapter = SubprocessBuildAdapter()
        assert hasattr(adapter, "build_wheel")
        assert callable(adapter.build_wheel)

    def test_adapter_has_build_sdist_method(self):
        """SubprocessBuildAdapter should have build_sdist method."""
        adapter = SubprocessBuildAdapter()
        assert hasattr(adapter, "build_sdist")
        assert callable(adapter.build_sdist)

    def test_adapter_has_clean_build_artifacts_method(self):
        """SubprocessBuildAdapter should have clean_build_artifacts method."""
        adapter = SubprocessBuildAdapter()
        assert hasattr(adapter, "clean_build_artifacts")
        assert callable(adapter.clean_build_artifacts)

    def test_adapter_has_get_wheel_path_method(self):
        """SubprocessBuildAdapter should have get_wheel_path method."""
        adapter = SubprocessBuildAdapter()
        assert hasattr(adapter, "get_wheel_path")
        assert callable(adapter.get_wheel_path)


class TestBuildWheel:
    """Tests for build_wheel method."""

    @patch("crafter_ai.installer.adapters.build_adapter.subprocess.run")
    def test_build_wheel_calls_subprocess_with_correct_command(self, mock_run):
        """build_wheel should call 'python -m build --wheel' via subprocess."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        adapter = SubprocessBuildAdapter()
        output_dir = Path("/tmp/dist")

        with patch.object(
            adapter,
            "get_wheel_path",
            return_value=Path("/tmp/dist/pkg-0.1.0-py3-none-any.whl"),
        ):
            adapter.build_wheel(output_dir)

        mock_run.assert_called_once()
        call_args = mock_run.call_args
        cmd = call_args[0][0] if call_args[0] else call_args[1].get("args", [])
        assert "python" in cmd[0] or cmd[0] == "python"
        assert "-m" in cmd
        assert "build" in cmd
        assert "--wheel" in cmd

    @patch("crafter_ai.installer.adapters.build_adapter.subprocess.run")
    def test_build_wheel_passes_output_dir(self, mock_run):
        """build_wheel should pass --outdir to subprocess."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        adapter = SubprocessBuildAdapter()
        output_dir = Path("/custom/dist")

        with patch.object(
            adapter,
            "get_wheel_path",
            return_value=Path("/custom/dist/pkg-0.1.0-py3-none-any.whl"),
        ):
            adapter.build_wheel(output_dir)

        call_args = mock_run.call_args
        cmd = call_args[0][0] if call_args[0] else call_args[1].get("args", [])
        assert "--outdir" in cmd or "-o" in cmd
        # The output dir should be in the command
        assert any(str(output_dir) in str(arg) for arg in cmd)

    @patch("crafter_ai.installer.adapters.build_adapter.subprocess.run")
    def test_build_wheel_returns_wheel_path_on_success(self, mock_run):
        """build_wheel should return the path to the built wheel."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        adapter = SubprocessBuildAdapter()
        output_dir = Path("/tmp/dist")
        expected_wheel = Path("/tmp/dist/pkg-0.1.0-py3-none-any.whl")

        with patch.object(adapter, "get_wheel_path", return_value=expected_wheel):
            result = adapter.build_wheel(output_dir)

        assert result == expected_wheel

    @patch("crafter_ai.installer.adapters.build_adapter.subprocess.run")
    def test_build_wheel_raises_build_error_on_failure(self, mock_run):
        """build_wheel should raise BuildError when subprocess fails."""
        mock_run.return_value = MagicMock(
            returncode=1, stdout="", stderr="error: no pyproject.toml"
        )
        adapter = SubprocessBuildAdapter()
        output_dir = Path("/tmp/dist")

        with pytest.raises(BuildError) as exc_info:
            adapter.build_wheel(output_dir)

        assert exc_info.value.return_code == 1
        assert "no pyproject.toml" in exc_info.value.output


class TestBuildSdist:
    """Tests for build_sdist method."""

    @patch("crafter_ai.installer.adapters.build_adapter.subprocess.run")
    def test_build_sdist_calls_subprocess_with_correct_command(self, mock_run):
        """build_sdist should call 'python -m build --sdist' via subprocess."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        adapter = SubprocessBuildAdapter()
        output_dir = Path("/tmp/dist")

        with patch.object(
            adapter, "_get_sdist_path", return_value=Path("/tmp/dist/pkg-0.1.0.tar.gz")
        ):
            adapter.build_sdist(output_dir)

        mock_run.assert_called_once()
        call_args = mock_run.call_args
        cmd = call_args[0][0] if call_args[0] else call_args[1].get("args", [])
        assert "python" in cmd[0] or cmd[0] == "python"
        assert "-m" in cmd
        assert "build" in cmd
        assert "--sdist" in cmd

    @patch("crafter_ai.installer.adapters.build_adapter.subprocess.run")
    def test_build_sdist_returns_sdist_path_on_success(self, mock_run):
        """build_sdist should return the path to the built sdist."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        adapter = SubprocessBuildAdapter()
        output_dir = Path("/tmp/dist")
        expected_sdist = Path("/tmp/dist/pkg-0.1.0.tar.gz")

        with patch.object(adapter, "_get_sdist_path", return_value=expected_sdist):
            result = adapter.build_sdist(output_dir)

        assert result == expected_sdist

    @patch("crafter_ai.installer.adapters.build_adapter.subprocess.run")
    def test_build_sdist_raises_build_error_on_failure(self, mock_run):
        """build_sdist should raise BuildError when subprocess fails."""
        mock_run.return_value = MagicMock(
            returncode=1, stdout="", stderr="error: missing MANIFEST.in"
        )
        adapter = SubprocessBuildAdapter()
        output_dir = Path("/tmp/dist")

        with pytest.raises(BuildError) as exc_info:
            adapter.build_sdist(output_dir)

        assert exc_info.value.return_code == 1


class TestCleanBuildArtifacts:
    """Tests for clean_build_artifacts method."""

    @patch("crafter_ai.installer.adapters.build_adapter.shutil.rmtree")
    @patch("crafter_ai.installer.adapters.build_adapter.Path.exists")
    @patch("crafter_ai.installer.adapters.build_adapter.Path.glob")
    def test_clean_build_artifacts_removes_build_dir(
        self, mock_glob, mock_exists, mock_rmtree
    ):
        """clean_build_artifacts should remove build/ directory."""
        mock_exists.return_value = True
        mock_glob.return_value = []
        adapter = SubprocessBuildAdapter()

        adapter.clean_build_artifacts()

        # Check that rmtree was called with build directory
        rmtree_calls = [str(c[0][0]) for c in mock_rmtree.call_args_list]
        assert any("build" in call for call in rmtree_calls)

    @patch("crafter_ai.installer.adapters.build_adapter.shutil.rmtree")
    @patch("crafter_ai.installer.adapters.build_adapter.Path.exists")
    @patch("crafter_ai.installer.adapters.build_adapter.Path.glob")
    def test_clean_build_artifacts_removes_dist_dir(
        self, mock_glob, mock_exists, mock_rmtree
    ):
        """clean_build_artifacts should remove dist/ directory."""
        mock_exists.return_value = True
        mock_glob.return_value = []
        adapter = SubprocessBuildAdapter()

        adapter.clean_build_artifacts()

        rmtree_calls = [str(c[0][0]) for c in mock_rmtree.call_args_list]
        assert any("dist" in call for call in rmtree_calls)

    @patch("crafter_ai.installer.adapters.build_adapter.shutil.rmtree")
    @patch("crafter_ai.installer.adapters.build_adapter.Path.exists")
    @patch("crafter_ai.installer.adapters.build_adapter.Path.glob")
    def test_clean_build_artifacts_removes_egg_info_dirs(
        self, mock_glob, mock_exists, mock_rmtree
    ):
        """clean_build_artifacts should remove *.egg-info directories."""
        mock_exists.return_value = True
        mock_egg_info = MagicMock()
        mock_egg_info.__str__ = lambda _: "pkg.egg-info"
        mock_glob.return_value = [mock_egg_info]
        adapter = SubprocessBuildAdapter()

        adapter.clean_build_artifacts()

        # Verify rmtree was called for egg-info directory
        assert mock_rmtree.call_count >= 1

    @patch("crafter_ai.installer.adapters.build_adapter.shutil.rmtree")
    @patch("crafter_ai.installer.adapters.build_adapter.Path.exists")
    @patch("crafter_ai.installer.adapters.build_adapter.Path.glob")
    def test_clean_build_artifacts_handles_missing_dirs(
        self, mock_glob, mock_exists, _mock_rmtree
    ):
        """clean_build_artifacts should not error when directories don't exist."""
        mock_exists.return_value = False
        mock_glob.return_value = []
        adapter = SubprocessBuildAdapter()

        # Should not raise
        adapter.clean_build_artifacts()


class TestGetWheelPath:
    """Tests for get_wheel_path method."""

    @patch("crafter_ai.installer.adapters.build_adapter.Path.glob")
    def test_get_wheel_path_finds_whl_file(self, mock_glob):
        """get_wheel_path should find .whl file in directory."""
        wheel_path = Path("/tmp/dist/pkg-0.1.0-py3-none-any.whl")
        mock_glob.return_value = [wheel_path]
        adapter = SubprocessBuildAdapter()

        result = adapter.get_wheel_path(Path("/tmp/dist"))

        assert result == wheel_path

    @patch("crafter_ai.installer.adapters.build_adapter.Path.glob")
    def test_get_wheel_path_returns_none_when_no_wheel(self, mock_glob):
        """get_wheel_path should return None when no .whl file exists."""
        mock_glob.return_value = []
        adapter = SubprocessBuildAdapter()

        result = adapter.get_wheel_path(Path("/tmp/dist"))

        assert result is None

    @patch("crafter_ai.installer.adapters.build_adapter.Path.glob")
    def test_get_wheel_path_returns_first_wheel_if_multiple(self, mock_glob):
        """get_wheel_path should return first wheel if multiple exist."""
        wheel1 = Path("/tmp/dist/pkg-0.1.0-py3-none-any.whl")
        wheel2 = Path("/tmp/dist/pkg-0.2.0-py3-none-any.whl")
        mock_glob.return_value = [wheel1, wheel2]
        adapter = SubprocessBuildAdapter()

        result = adapter.get_wheel_path(Path("/tmp/dist"))

        assert result == wheel1
