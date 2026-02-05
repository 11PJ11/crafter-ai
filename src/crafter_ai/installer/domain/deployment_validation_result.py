"""DeploymentValidationResult domain value object.

Immutable result of the deployment validation operation. This is a pure domain
object with no external dependencies, following the same frozen dataclass
pattern as AssetDeploymentResult and IdeBundleBuildResult.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DeploymentValidationResult:
    """Immutable result of deployment validation.

    Attributes:
        valid: Whether all validations passed.
        agent_count_match: Whether deployed agent count matches expected.
        command_count_match: Whether deployed command count matches expected.
        template_count_match: Whether deployed template count matches expected.
        script_count_match: Whether deployed script count matches expected.
        manifest_written: Whether manifest file was written successfully.
        schema_version: Schema version string (e.g. 'v3.0').
        schema_phases: Number of phases in schema (e.g. 7).
        mismatches: List of mismatch descriptions.
    """

    valid: bool
    agent_count_match: bool
    command_count_match: bool
    template_count_match: bool
    script_count_match: bool
    manifest_written: bool
    schema_version: str | None
    schema_phases: int | None
    mismatches: list[str]
