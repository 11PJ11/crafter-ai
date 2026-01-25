"""DES Extension Request API.

This module defines the API for requesting extensions to the Dynamic Extension System.
Extensions allow requesting additional turns or time when budget limits are approached.

API Contract:
    - ExtensionRequest: Dataclass representing an extension request
    - request_extension(): Factory function to create extension requests

Example:
    >>> request = request_extension(
    ...     reason="Need more time for complex refactoring",
    ...     additional_turns=5,
    ...     additional_minutes=10
    ... )
    >>> request.reason
    'Need more time for complex refactoring'
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ExtensionRequest:
    """Request for extending turn or time budget.

    Attributes:
        reason: Human-readable explanation for the extension request
        additional_turns: Number of additional turns requested (optional)
        additional_minutes: Additional time in minutes requested (optional)

    At least one of additional_turns or additional_minutes must be specified.
    """

    reason: str
    additional_turns: Optional[int]
    additional_minutes: Optional[int]


def request_extension(
    reason: str,
    additional_turns: Optional[int] = None,
    additional_minutes: Optional[int] = None,
) -> ExtensionRequest:
    """Create an extension request with specified parameters.

    Args:
        reason: Explanation for why extension is needed
        additional_turns: Number of extra turns requested (None if not requesting turns)
        additional_minutes: Extra time in minutes requested (None if not requesting time)

    Returns:
        ExtensionRequest instance configured with provided parameters

    Example:
        >>> req = request_extension("Complex task", additional_turns=3)
        >>> req.additional_turns
        3
    """
    return ExtensionRequest(
        reason=reason,
        additional_turns=additional_turns,
        additional_minutes=additional_minutes,
    )
