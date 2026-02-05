"""IdeBundleBuildResult domain value object.

Immutable result of the IDE bundle build operation. This is a pure domain
object with no external dependencies beyond pathlib, following the same
frozen dataclass pattern as CheckResult.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class IdeBundleBuildResult:
    """Immutable result of the IDE bundle build.

    Attributes:
        success: Whether the build completed successfully.
        output_dir: Path to dist/ide/ output directory.
        agent_count: Number of agent files processed.
        command_count: Number of command files processed.
        template_count: Number of template files processed.
        script_count: Number of script files processed.
        team_count: Number of team files processed.
        yaml_warnings: List of non-blocking YAML parse warnings.
        embed_injection_count: Number of embed injections performed.
        error_message: Error message if build failed.
    """

    success: bool
    output_dir: Path | None
    agent_count: int
    command_count: int
    template_count: int
    script_count: int
    team_count: int
    yaml_warnings: list[str]
    embed_injection_count: int
    error_message: str | None = None
