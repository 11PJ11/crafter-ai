"""DES Extension Approval Engine.

This module implements approval logic for extension requests, evaluating
whether requests should be approved or denied based on business criteria.

Business Rules:
    - Approve if reason is justified (>20 characters)
    - Deny if max extensions exceeded (e.g., 2 per phase)
    - Deny if requested extension unreasonably large (>200% original)
    - Return ApprovalResult with decision and rationale

Example:
    >>> from des.extension_api import ExtensionRequest
    >>> engine = ExtensionApprovalEngine()
    >>> request = ExtensionRequest(
    ...     reason="Need more time for complex refactoring",
    ...     additional_turns=5,
    ...     additional_minutes=None
    ... )
    >>> result = engine.evaluate(
    ...     request,
    ...     current_extensions=0,
    ...     phase_max_extensions=2,
    ...     original_turns=10
    ... )
    >>> result.approved
    True
"""

from dataclasses import dataclass
from typing import Optional

from des.extension_api import ExtensionRequest


@dataclass
class ApprovalResult:
    """Result of extension approval evaluation.

    Attributes:
        approved: Whether the extension request was approved
        reason: Human-readable explanation for the decision
    """

    approved: bool
    reason: str


class ExtensionApprovalEngine:
    """Engine for evaluating extension requests against approval criteria.

    This class implements business logic to approve or deny extension requests
    based on justification quality, extension limits, and reasonableness checks.
    """

    MINIMUM_REASON_LENGTH = 20
    MAXIMUM_EXTENSION_PERCENTAGE = 200  # 200% of original

    def evaluate(
        self,
        request: ExtensionRequest,
        current_extensions: int,
        phase_max_extensions: int,
        original_turns: Optional[int] = None,
        original_minutes: Optional[int] = None,
    ) -> ApprovalResult:
        """Evaluate extension request against approval criteria.

        Args:
            request: ExtensionRequest to evaluate
            current_extensions: Number of extensions already granted in current phase
            phase_max_extensions: Maximum extensions allowed per phase
            original_turns: Original turn budget (required if requesting turn extension)
            original_minutes: Original time budget (required if requesting time extension)

        Returns:
            ApprovalResult with approval decision and rationale
        """
        # Check if max extensions exceeded
        if current_extensions >= phase_max_extensions:
            return ApprovalResult(
                approved=False,
                reason=f"Maximum extensions limit reached ({phase_max_extensions} per phase)",
            )

        # Check if reason is justified
        if len(request.reason) <= self.MINIMUM_REASON_LENGTH:
            return ApprovalResult(
                approved=False,
                reason=f"Insufficient justification: reason must exceed {self.MINIMUM_REASON_LENGTH} characters",
            )

        # Check if turn extension is unreasonably large
        if request.additional_turns is not None and original_turns is not None:
            percentage = (request.additional_turns / original_turns) * 100
            if percentage > self.MAXIMUM_EXTENSION_PERCENTAGE:
                return ApprovalResult(
                    approved=False,
                    reason=f"Extension too large: requesting {percentage:.0f}% of original (max {self.MAXIMUM_EXTENSION_PERCENTAGE}%)",
                )

        # Check if minute extension is unreasonably large
        if request.additional_minutes is not None and original_minutes is not None:
            percentage = (request.additional_minutes / original_minutes) * 100
            if percentage > self.MAXIMUM_EXTENSION_PERCENTAGE:
                return ApprovalResult(
                    approved=False,
                    reason=f"Extension too large: requesting {percentage:.0f}% of original (max {self.MAXIMUM_EXTENSION_PERCENTAGE}%)",
                )

        # All criteria met - approve
        return ApprovalResult(
            approved=True, reason="Extension request approved: criteria satisfied"
        )
