"""CLI package for crafter-ai installer."""

# Import forge_install to register the install command with forge_app
from crafter_ai.installer.cli import forge_install as _forge_install  # noqa: F401
from crafter_ai.installer.cli.forge_build import forge_app


__all__ = ["forge_app"]
