"""
Contract tests for ChecksumPort interface.

These tests verify the port interface contract:
- Abstract class with abstract methods
- calculate_sha256(file_path) method defined
- verify(file_path, expected_checksum) method defined
- ChecksumMismatchError exception type defined
"""

import pytest
from abc import ABC
import inspect
from pathlib import Path


class TestChecksumPortIsAbstract:
    """Test that ChecksumPort is properly defined as an abstract class."""

    def test_checksum_port_is_abstract_base_class(self):
        """ChecksumPort must be an abstract base class."""
        from nWave.core.versioning.ports.checksum_port import ChecksumPort

        assert issubclass(ChecksumPort, ABC), "ChecksumPort must inherit from ABC"

    def test_checksum_port_cannot_be_instantiated(self):
        """Abstract classes cannot be directly instantiated."""
        from nWave.core.versioning.ports.checksum_port import ChecksumPort

        with pytest.raises(TypeError):
            ChecksumPort()


class TestCalculateSha256MethodDefined:
    """Test that calculate_sha256 method is properly defined."""

    def test_calculate_sha256_method_exists(self):
        """ChecksumPort must define calculate_sha256 method."""
        from nWave.core.versioning.ports.checksum_port import ChecksumPort

        assert hasattr(ChecksumPort, "calculate_sha256")

    def test_calculate_sha256_is_abstract_method(self):
        """calculate_sha256 must be an abstract method."""
        from nWave.core.versioning.ports.checksum_port import ChecksumPort

        method = getattr(ChecksumPort, "calculate_sha256", None)
        assert method is not None
        assert getattr(method, "__isabstractmethod__", False), \
            "calculate_sha256 must be decorated with @abstractmethod"

    def test_calculate_sha256_accepts_file_path_parameter(self):
        """calculate_sha256 must accept file_path parameter."""
        from nWave.core.versioning.ports.checksum_port import ChecksumPort

        sig = inspect.signature(ChecksumPort.calculate_sha256)
        params = list(sig.parameters.keys())

        # Should have self, file_path
        assert "file_path" in params, "Method must have 'file_path' parameter"

    def test_calculate_sha256_file_path_typed_as_path(self):
        """calculate_sha256 file_path parameter must be typed as Path."""
        from nWave.core.versioning.ports.checksum_port import ChecksumPort
        from typing import get_type_hints

        hints = get_type_hints(ChecksumPort.calculate_sha256)
        assert hints.get("file_path") == Path, \
            "calculate_sha256 file_path must be typed as Path"

    def test_calculate_sha256_returns_string(self):
        """calculate_sha256 must return a string (hex digest)."""
        from nWave.core.versioning.ports.checksum_port import ChecksumPort
        from typing import get_type_hints

        hints = get_type_hints(ChecksumPort.calculate_sha256)
        assert hints.get("return") == str, \
            "calculate_sha256 must return str (SHA256 hex digest)"


class TestVerifyMethodDefined:
    """Test that verify method is properly defined."""

    def test_verify_method_exists(self):
        """ChecksumPort must define verify method."""
        from nWave.core.versioning.ports.checksum_port import ChecksumPort

        assert hasattr(ChecksumPort, "verify")

    def test_verify_is_abstract_method(self):
        """verify must be an abstract method."""
        from nWave.core.versioning.ports.checksum_port import ChecksumPort

        method = getattr(ChecksumPort, "verify", None)
        assert method is not None
        assert getattr(method, "__isabstractmethod__", False), \
            "verify must be decorated with @abstractmethod"

    def test_verify_accepts_file_path_parameter(self):
        """verify must accept file_path parameter."""
        from nWave.core.versioning.ports.checksum_port import ChecksumPort

        sig = inspect.signature(ChecksumPort.verify)
        params = list(sig.parameters.keys())

        assert "file_path" in params, "Method must have 'file_path' parameter"

    def test_verify_accepts_expected_checksum_parameter(self):
        """verify must accept expected_checksum parameter."""
        from nWave.core.versioning.ports.checksum_port import ChecksumPort

        sig = inspect.signature(ChecksumPort.verify)
        params = list(sig.parameters.keys())

        assert "expected_checksum" in params, \
            "Method must have 'expected_checksum' parameter"

    def test_verify_file_path_typed_as_path(self):
        """verify file_path parameter must be typed as Path."""
        from nWave.core.versioning.ports.checksum_port import ChecksumPort
        from typing import get_type_hints

        hints = get_type_hints(ChecksumPort.verify)
        assert hints.get("file_path") == Path, \
            "verify file_path must be typed as Path"

    def test_verify_expected_checksum_typed_as_string(self):
        """verify expected_checksum parameter must be typed as str."""
        from nWave.core.versioning.ports.checksum_port import ChecksumPort
        from typing import get_type_hints

        hints = get_type_hints(ChecksumPort.verify)
        assert hints.get("expected_checksum") == str, \
            "verify expected_checksum must be typed as str"

    def test_verify_returns_bool(self):
        """verify must return a boolean indicating match status."""
        from nWave.core.versioning.ports.checksum_port import ChecksumPort
        from typing import get_type_hints

        hints = get_type_hints(ChecksumPort.verify)
        assert hints.get("return") == bool, \
            "verify must return bool (checksum match status)"


class TestChecksumMismatchErrorDefined:
    """Test that ChecksumMismatchError exception is properly defined."""

    def test_checksum_mismatch_error_class_exists(self):
        """ChecksumMismatchError exception class must be defined."""
        from nWave.core.versioning.ports.checksum_port import ChecksumMismatchError

        assert ChecksumMismatchError is not None

    def test_checksum_mismatch_error_is_exception(self):
        """ChecksumMismatchError must be a subclass of Exception."""
        from nWave.core.versioning.ports.checksum_port import ChecksumMismatchError

        assert issubclass(ChecksumMismatchError, Exception), \
            "ChecksumMismatchError must inherit from Exception"

    def test_checksum_mismatch_error_can_be_raised(self):
        """ChecksumMismatchError must be raisable with a message."""
        from nWave.core.versioning.ports.checksum_port import ChecksumMismatchError

        with pytest.raises(ChecksumMismatchError) as exc_info:
            raise ChecksumMismatchError("Checksum does not match")

        assert "Checksum" in str(exc_info.value)

    def test_checksum_mismatch_error_has_expected_checksum_attribute(self):
        """ChecksumMismatchError should have expected_checksum attribute."""
        from nWave.core.versioning.ports.checksum_port import ChecksumMismatchError

        error = ChecksumMismatchError(
            "Checksum mismatch",
            expected_checksum="abc123",
            actual_checksum="def456"
        )
        assert hasattr(error, "expected_checksum")
        assert error.expected_checksum == "abc123"

    def test_checksum_mismatch_error_has_actual_checksum_attribute(self):
        """ChecksumMismatchError should have actual_checksum attribute."""
        from nWave.core.versioning.ports.checksum_port import ChecksumMismatchError

        error = ChecksumMismatchError(
            "Checksum mismatch",
            expected_checksum="abc123",
            actual_checksum="def456"
        )
        assert hasattr(error, "actual_checksum")
        assert error.actual_checksum == "def456"
