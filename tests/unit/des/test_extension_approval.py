"""Unit tests for ExtensionApprovalEngine.

This module validates the extension approval logic including:
- Approval criteria validation (justified reason)
- Denial for max extensions exceeded
- Denial for unreasonably large extensions
- ApprovalResult structure and decision rationale
"""

from dataclasses import fields


def test_approval_result_dataclass_exists():
    """ApprovalResult dataclass should be importable."""
    from des.extension_approval import ApprovalResult

    assert ApprovalResult is not None


def test_approval_result_has_required_fields():
    """ApprovalResult should have approved, reason fields."""
    from des.extension_approval import ApprovalResult

    field_names = {f.name for f in fields(ApprovalResult)}
    assert "approved" in field_names, "ApprovalResult must have 'approved' field"
    assert "reason" in field_names, "ApprovalResult must have 'reason' field"


def test_approval_result_field_types():
    """ApprovalResult fields should have correct types."""
    from des.extension_approval import ApprovalResult

    field_types = {f.name: f.type for f in fields(ApprovalResult)}

    assert field_types["approved"] == bool, "approved must be bool type"
    assert field_types["reason"] == str, "reason must be str type"


def test_extension_approval_engine_exists():
    """ExtensionApprovalEngine class should be importable."""
    from des.extension_approval import ExtensionApprovalEngine

    assert ExtensionApprovalEngine is not None


def test_extension_approval_engine_has_evaluate_method():
    """ExtensionApprovalEngine should have evaluate() method."""
    from des.extension_approval import ExtensionApprovalEngine

    engine = ExtensionApprovalEngine()
    assert hasattr(
        engine, "evaluate"
    ), "ExtensionApprovalEngine must have evaluate() method"
    assert callable(engine.evaluate), "evaluate must be a callable method"


def test_approve_when_reason_is_justified():
    """Should approve when reason is non-empty and justified (>20 chars)."""
    from des.extension_api import ExtensionRequest
    from des.extension_approval import ExtensionApprovalEngine

    engine = ExtensionApprovalEngine()
    request = ExtensionRequest(
        reason="Need additional time to complete complex refactoring task",
        additional_turns=5,
        additional_minutes=None,
    )

    result = engine.evaluate(request, current_extensions=0, phase_max_extensions=2)

    assert result.approved is True, "Should approve justified extension request"
    assert len(result.reason) > 0, "Approval reason should be provided"


def test_deny_when_reason_too_short():
    """Should deny when reason is not justified (<=20 chars)."""
    from des.extension_api import ExtensionRequest
    from des.extension_approval import ExtensionApprovalEngine

    engine = ExtensionApprovalEngine()
    request = ExtensionRequest(
        reason="Need more time",  # Only 14 chars
        additional_turns=5,
        additional_minutes=None,
    )

    result = engine.evaluate(request, current_extensions=0, phase_max_extensions=2)

    assert result.approved is False, "Should deny unjustified extension request"
    assert (
        "insufficient justification" in result.reason.lower()
        or "too short" in result.reason.lower()
        or "justify" in result.reason.lower()
    ), "Denial reason should mention insufficient justification"


def test_deny_when_max_extensions_exceeded():
    """Should deny when current extensions equals or exceeds phase maximum."""
    from des.extension_api import ExtensionRequest
    from des.extension_approval import ExtensionApprovalEngine

    engine = ExtensionApprovalEngine()
    request = ExtensionRequest(
        reason="Need additional time to complete complex refactoring task",
        additional_turns=3,
        additional_minutes=None,
    )

    # At limit
    result_at_limit = engine.evaluate(
        request, current_extensions=2, phase_max_extensions=2
    )
    assert result_at_limit.approved is False, "Should deny when at max extensions limit"
    assert (
        "maximum" in result_at_limit.reason.lower()
        or "exceeded" in result_at_limit.reason.lower()
        or "limit" in result_at_limit.reason.lower()
    ), "Denial reason should mention maximum exceeded"

    # Beyond limit
    result_over_limit = engine.evaluate(
        request, current_extensions=3, phase_max_extensions=2
    )
    assert (
        result_over_limit.approved is False
    ), "Should deny when over max extensions limit"


def test_deny_when_extension_unreasonably_large():
    """Should deny when requested extension exceeds 200% of original budget."""
    from des.extension_api import ExtensionRequest
    from des.extension_approval import ExtensionApprovalEngine

    engine = ExtensionApprovalEngine()

    # Request 300% extension (exceeds 200% threshold)
    request_turns = ExtensionRequest(
        reason="Need significantly more turns for comprehensive testing",
        additional_turns=30,  # Assuming original ~10, this is 300%
        additional_minutes=None,
    )

    result_turns = engine.evaluate(
        request_turns,
        current_extensions=0,
        phase_max_extensions=2,
        original_turns=10,
    )

    assert (
        result_turns.approved is False
    ), "Should deny unreasonably large turn extension"
    assert (
        "too large" in result_turns.reason.lower()
        or "unreasonable" in result_turns.reason.lower()
        or "excessive" in result_turns.reason.lower()
    ), "Denial reason should mention unreasonably large extension"

    # Request 300% extension for minutes
    request_minutes = ExtensionRequest(
        reason="Need significantly more time for comprehensive testing",
        additional_turns=None,
        additional_minutes=60,  # Assuming original ~20, this is 300%
    )

    result_minutes = engine.evaluate(
        request_minutes,
        current_extensions=0,
        phase_max_extensions=2,
        original_minutes=20,
    )

    assert (
        result_minutes.approved is False
    ), "Should deny unreasonably large minute extension"


def test_approve_when_extension_within_200_percent():
    """Should approve when extension is within 200% threshold."""
    from des.extension_api import ExtensionRequest
    from des.extension_approval import ExtensionApprovalEngine

    engine = ExtensionApprovalEngine()

    # Request 150% extension (within 200% threshold)
    request = ExtensionRequest(
        reason="Need additional time to complete complex refactoring task",
        additional_turns=15,  # 150% of original 10
        additional_minutes=None,
    )

    result = engine.evaluate(
        request,
        current_extensions=0,
        phase_max_extensions=2,
        original_turns=10,
    )

    assert result.approved is True, "Should approve reasonable extension within 200%"


def test_evaluate_signature_has_required_parameters():
    """evaluate() method should have required parameters."""
    import inspect
    from des.extension_approval import ExtensionApprovalEngine

    engine = ExtensionApprovalEngine()
    sig = inspect.signature(engine.evaluate)
    params = list(sig.parameters.keys())

    assert "request" in params, "evaluate must have 'request' parameter"
    assert (
        "current_extensions" in params
    ), "evaluate must have 'current_extensions' parameter"
    assert (
        "phase_max_extensions" in params
    ), "evaluate must have 'phase_max_extensions' parameter"
