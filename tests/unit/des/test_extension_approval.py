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
    assert hasattr(engine, "evaluate"), (
        "ExtensionApprovalEngine must have evaluate() method"
    )
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
    assert result_over_limit.approved is False, (
        "Should deny when over max extensions limit"
    )


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

    assert result_turns.approved is False, (
        "Should deny unreasonably large turn extension"
    )
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

    assert result_minutes.approved is False, (
        "Should deny unreasonably large minute extension"
    )


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
    assert "current_extensions" in params, (
        "evaluate must have 'current_extensions' parameter"
    )
    assert "phase_max_extensions" in params, (
        "evaluate must have 'phase_max_extensions' parameter"
    )


# ============================================================================
# EDGE CASE TESTS - Boundary Conditions and Exceptional Scenarios
# ============================================================================


def test_deny_when_reason_exactly_at_minimum_length():
    """Should deny when reason is exactly 20 characters (boundary)."""
    from des.extension_api import ExtensionRequest
    from des.extension_approval import ExtensionApprovalEngine

    engine = ExtensionApprovalEngine()
    request = ExtensionRequest(
        reason="12345678901234567890",  # Exactly 20 chars
        additional_turns=5,
        additional_minutes=None,
    )

    result = engine.evaluate(request, current_extensions=0, phase_max_extensions=2)

    assert result.approved is False, (
        "Should deny reason exactly at minimum length (20 chars)"
    )
    assert (
        "insufficient justification" in result.reason.lower()
        or "too short" in result.reason.lower()
    ), "Denial reason should mention insufficient justification"


def test_approve_when_reason_just_over_minimum_length():
    """Should approve when reason is just over 20 characters."""
    from des.extension_api import ExtensionRequest
    from des.extension_approval import ExtensionApprovalEngine

    engine = ExtensionApprovalEngine()
    request = ExtensionRequest(
        reason="123456789012345678901",  # 21 chars
        additional_turns=5,
        additional_minutes=None,
    )

    result = engine.evaluate(request, current_extensions=0, phase_max_extensions=2)

    assert result.approved is True, (
        "Should approve reason just over minimum length (21 chars)"
    )


def test_approve_when_extension_exactly_at_200_percent():
    """Should approve when extension is exactly at 200% threshold (boundary)."""
    from des.extension_api import ExtensionRequest
    from des.extension_approval import ExtensionApprovalEngine

    engine = ExtensionApprovalEngine()
    request = ExtensionRequest(
        reason="Need additional time to complete complex refactoring task",
        additional_turns=20,  # Exactly 200% of original 10
        additional_minutes=None,
    )

    result = engine.evaluate(
        request,
        current_extensions=0,
        phase_max_extensions=2,
        original_turns=10,
    )

    assert result.approved is True, (
        "Should approve extension exactly at 200% threshold (inclusive)"
    )


def test_deny_when_extension_just_over_200_percent():
    """Should deny when extension is just over 200% threshold."""
    from des.extension_api import ExtensionRequest
    from des.extension_approval import ExtensionApprovalEngine

    engine = ExtensionApprovalEngine()
    request = ExtensionRequest(
        reason="Need additional time to complete complex refactoring task",
        additional_turns=21,  # 210% of original 10
        additional_minutes=None,
    )

    result = engine.evaluate(
        request,
        current_extensions=0,
        phase_max_extensions=2,
        original_turns=10,
    )

    assert result.approved is False, (
        "Should deny extension just over 200% threshold (210%)"
    )
    assert (
        "too large" in result.reason.lower() or "excessive" in result.reason.lower()
    ), "Denial reason should mention excessive extension"


def test_approve_when_no_budget_provided_for_non_relevant_metric():
    """Should approve when original budget not provided if not checking that metric."""
    from des.extension_api import ExtensionRequest
    from des.extension_approval import ExtensionApprovalEngine

    engine = ExtensionApprovalEngine()

    # Request turn extension without providing original_minutes (shouldn't matter)
    request = ExtensionRequest(
        reason="Need additional time to complete complex refactoring task",
        additional_turns=5,
        additional_minutes=None,
    )

    result = engine.evaluate(
        request,
        current_extensions=0,
        phase_max_extensions=2,
        original_turns=10,
        original_minutes=None,  # Not provided, but shouldn't matter
    )

    assert result.approved is True, (
        "Should approve when non-relevant budget not provided"
    )


def test_approve_when_requesting_turn_extension_without_original_turns():
    """Should approve turn extension when original_turns not provided (no percentage check)."""
    from des.extension_api import ExtensionRequest
    from des.extension_approval import ExtensionApprovalEngine

    engine = ExtensionApprovalEngine()
    request = ExtensionRequest(
        reason="Need additional time to complete complex refactoring task",
        additional_turns=50,  # Large number, but no original to compare
        additional_minutes=None,
    )

    result = engine.evaluate(
        request,
        current_extensions=0,
        phase_max_extensions=2,
        original_turns=None,  # Not provided - skip percentage check
    )

    assert result.approved is True, (
        "Should approve when original budget not provided (no percentage check possible)"
    )


def test_approve_when_requesting_minute_extension_without_original_minutes():
    """Should approve minute extension when original_minutes not provided (no percentage check)."""
    from des.extension_api import ExtensionRequest
    from des.extension_approval import ExtensionApprovalEngine

    engine = ExtensionApprovalEngine()
    request = ExtensionRequest(
        reason="Need additional time to complete complex refactoring task",
        additional_turns=None,
        additional_minutes=100,  # Large number, but no original to compare
    )

    result = engine.evaluate(
        request,
        current_extensions=0,
        phase_max_extensions=2,
        original_minutes=None,  # Not provided - skip percentage check
    )

    assert result.approved is True, (
        "Should approve when original budget not provided (no percentage check possible)"
    )


def test_deny_when_current_extensions_equals_phase_max():
    """Should deny when current extensions exactly equals phase max (boundary)."""
    from des.extension_api import ExtensionRequest
    from des.extension_approval import ExtensionApprovalEngine

    engine = ExtensionApprovalEngine()
    request = ExtensionRequest(
        reason="Need additional time to complete complex refactoring task",
        additional_turns=5,
        additional_minutes=None,
    )

    result = engine.evaluate(
        request,
        current_extensions=3,
        phase_max_extensions=3,  # Equal
    )

    assert result.approved is False, (
        "Should deny when current extensions equals phase max"
    )
    assert "maximum" in result.reason.lower() or "limit" in result.reason.lower(), (
        "Denial reason should mention maximum limit"
    )


def test_approve_when_current_extensions_one_below_phase_max():
    """Should approve when current extensions is one below phase max."""
    from des.extension_api import ExtensionRequest
    from des.extension_approval import ExtensionApprovalEngine

    engine = ExtensionApprovalEngine()
    request = ExtensionRequest(
        reason="Need additional time to complete complex refactoring task",
        additional_turns=5,
        additional_minutes=None,
    )

    result = engine.evaluate(
        request,
        current_extensions=2,
        phase_max_extensions=3,  # One below
    )

    assert result.approved is True, (
        "Should approve when current extensions one below phase max"
    )


def test_approve_when_both_turn_and_minute_extensions_within_limits():
    """Should approve when both turn and minute extensions are within 200% limits."""
    from des.extension_api import ExtensionRequest
    from des.extension_approval import ExtensionApprovalEngine

    engine = ExtensionApprovalEngine()
    request = ExtensionRequest(
        reason="Need additional time to complete complex refactoring task",
        additional_turns=10,  # 100% of original 10 turns
        additional_minutes=15,  # 75% of original 20 minutes
    )

    result = engine.evaluate(
        request,
        current_extensions=0,
        phase_max_extensions=2,
        original_turns=10,
        original_minutes=20,
    )

    assert result.approved is True, (
        "Should approve when both turn and minute extensions within limits"
    )


def test_deny_when_only_minute_extension_exceeds_limit():
    """Should deny when only minute extension exceeds 200%, even if turn extension is fine."""
    from des.extension_api import ExtensionRequest
    from des.extension_approval import ExtensionApprovalEngine

    engine = ExtensionApprovalEngine()
    request = ExtensionRequest(
        reason="Need additional time to complete complex refactoring task",
        additional_turns=5,  # 50% of original 10 turns (fine)
        additional_minutes=50,  # 250% of original 20 minutes (exceeds)
    )

    result = engine.evaluate(
        request,
        current_extensions=0,
        phase_max_extensions=2,
        original_turns=10,
        original_minutes=20,
    )

    assert result.approved is False, "Should deny when minute extension exceeds limit"
    assert (
        "too large" in result.reason.lower() or "excessive" in result.reason.lower()
    ), "Denial reason should mention excessive extension"


def test_evaluation_order_checks_max_extensions_first():
    """Should deny for max extensions exceeded before checking other criteria."""
    from des.extension_api import ExtensionRequest
    from des.extension_approval import ExtensionApprovalEngine

    engine = ExtensionApprovalEngine()
    request = ExtensionRequest(
        reason="Short",  # Too short, but max extensions should be checked first
        additional_turns=5,
        additional_minutes=None,
    )

    result = engine.evaluate(
        request,
        current_extensions=2,
        phase_max_extensions=2,  # At limit
    )

    assert result.approved is False, "Should deny when max extensions exceeded"
    assert "maximum" in result.reason.lower() or "limit" in result.reason.lower(), (
        "Should mention max limit, not insufficient reason (checked first)"
    )
