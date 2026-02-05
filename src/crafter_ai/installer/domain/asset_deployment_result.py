"""AssetDeploymentResult domain value object.

Immutable result of the asset deployment operation. This is a pure domain
object with no external dependencies beyond pathlib, following the same
frozen dataclass pattern as IdeBundleBuildResult.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AssetDeploymentResult:
    """Immutable result of asset deployment.

    Attributes:
        success: Whether deployment completed successfully.
        agents_deployed: Number of agent files deployed.
        commands_deployed: Number of command files deployed.
        templates_deployed: Number of template files deployed.
        scripts_deployed: Number of script files deployed.
        target_path: Deployment target directory (e.g. ~/.claude/).
        error_message: Error message if deployment failed.
    """

    success: bool
    agents_deployed: int
    commands_deployed: int
    templates_deployed: int
    scripts_deployed: int
    target_path: Path
    error_message: str | None = None
