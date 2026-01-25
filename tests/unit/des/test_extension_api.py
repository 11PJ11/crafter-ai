"""Unit tests for DES extension API contract.

This module validates the extension request API design including:
- ExtensionRequest dataclass structure
- request_extension() method signature
- Type safety and validation
"""

from dataclasses import fields
from typing import Optional


def test_extension_request_dataclass_exists():
    """ExtensionRequest dataclass should be importable."""
    # RED: This will fail until we create the dataclass
    from des.extension_api import ExtensionRequest

    assert ExtensionRequest is not None


def test_extension_request_has_required_fields():
    """ExtensionRequest should have reason, additional_turns, additional_minutes fields."""
    from des.extension_api import ExtensionRequest

    field_names = {f.name for f in fields(ExtensionRequest)}
    assert "reason" in field_names, "ExtensionRequest must have 'reason' field"
    assert (
        "additional_turns" in field_names
    ), "ExtensionRequest must have 'additional_turns' field"
    assert (
        "additional_minutes" in field_names
    ), "ExtensionRequest must have 'additional_minutes' field"


def test_extension_request_field_types():
    """ExtensionRequest fields should have correct types."""
    from des.extension_api import ExtensionRequest

    field_types = {f.name: f.type for f in fields(ExtensionRequest)}

    # reason should be string
    assert field_types["reason"] == str, "reason must be str type"

    # additional_turns should be Optional[int]
    assert (
        field_types["additional_turns"] == Optional[int]
    ), "additional_turns must be Optional[int]"

    # additional_minutes should be Optional[int]
    assert (
        field_types["additional_minutes"] == Optional[int]
    ), "additional_minutes must be Optional[int]"


def test_extension_request_instantiation():
    """ExtensionRequest should be instantiable with valid data."""
    from des.extension_api import ExtensionRequest

    request = ExtensionRequest(
        reason="Need more time to complete research",
        additional_turns=5,
        additional_minutes=10,
    )

    assert request.reason == "Need more time to complete research"
    assert request.additional_turns == 5
    assert request.additional_minutes == 10


def test_extension_request_allows_none_values():
    """ExtensionRequest should allow None for optional fields."""
    from des.extension_api import ExtensionRequest

    # Can specify only turns
    request1 = ExtensionRequest(
        reason="Need more turns", additional_turns=3, additional_minutes=None
    )
    assert request1.additional_turns == 3
    assert request1.additional_minutes is None

    # Can specify only minutes
    request2 = ExtensionRequest(
        reason="Need more time", additional_turns=None, additional_minutes=15
    )
    assert request2.additional_turns is None
    assert request2.additional_minutes == 15


def test_request_extension_function_exists():
    """request_extension() function should be importable."""
    from des.extension_api import request_extension

    assert callable(request_extension), "request_extension must be a callable function"


def test_request_extension_signature():
    """request_extension() should accept reason, additional_turns, additional_minutes parameters."""
    import inspect
    from des.extension_api import request_extension

    sig = inspect.signature(request_extension)
    params = list(sig.parameters.keys())

    assert "reason" in params, "request_extension must have 'reason' parameter"
    assert (
        "additional_turns" in params
    ), "request_extension must have 'additional_turns' parameter"
    assert (
        "additional_minutes" in params
    ), "request_extension must have 'additional_minutes' parameter"


def test_request_extension_parameter_types():
    """request_extension() parameters should have correct type hints."""
    import inspect
    from des.extension_api import request_extension

    sig = inspect.signature(request_extension)

    # Check reason type
    reason_annotation = sig.parameters["reason"].annotation
    assert reason_annotation == str, "reason parameter must be annotated as str"

    # Check additional_turns type
    turns_annotation = sig.parameters["additional_turns"].annotation
    assert (
        turns_annotation == Optional[int]
    ), "additional_turns parameter must be annotated as Optional[int]"

    # Check additional_minutes type
    minutes_annotation = sig.parameters["additional_minutes"].annotation
    assert (
        minutes_annotation == Optional[int]
    ), "additional_minutes parameter must be annotated as Optional[int]"


def test_request_extension_return_type():
    """request_extension() should return ExtensionRequest."""
    import inspect
    from des.extension_api import request_extension, ExtensionRequest

    sig = inspect.signature(request_extension)
    assert (
        sig.return_annotation == ExtensionRequest
    ), "request_extension must return ExtensionRequest"


def test_request_extension_creates_request_object():
    """request_extension() should create and return ExtensionRequest instance."""
    from des.extension_api import request_extension, ExtensionRequest

    result = request_extension(
        reason="Testing extension", additional_turns=2, additional_minutes=5
    )

    assert isinstance(
        result, ExtensionRequest
    ), "request_extension must return ExtensionRequest instance"
    assert result.reason == "Testing extension"
    assert result.additional_turns == 2
    assert result.additional_minutes == 5
