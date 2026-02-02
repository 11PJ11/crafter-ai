"""CelebrationService for displaying welcome and celebration messages.

This module provides the CelebrationService application service that:
- Displays ASCII art welcome banner for nWave
- Shows success celebration with version and checkmark
- Shows next steps with numbered list
- Shows failure message with error and help links
- Supports CI mode with simple text output

Used by: forge:install CLI commands for user-facing messages
"""

import os
from typing import IO

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from crafter_ai.installer.config.urls import URLConfig, get_default_urls


# ASCII art banner for nWave
NWAVE_BANNER = r"""
     __          __
    /\ \  __    /\ \
    \_\ \/\_\   \ \ \____   ___   __  __    __
    /' _ `\/\ \   \ \  __ \/\  `\/\  \/\ \/\ \/ /\ \
   /\ \/\ \ \ \   \ \ \/\ \ \ \_/ \ \ \_/ \_/  \ \ \
   \ \_\ \_\ \_\   \ \____/\ \___\ \____/\_____/\ \_\
    \/_/\/_/\/_/    \/___/  \/__/  \___/ \/_____/ \/_/

    ███╗   ██╗██╗    ██╗ █████╗ ██╗   ██╗███████╗
    ████╗  ██║██║    ██║██╔══██╗██║   ██║██╔════╝
    ██╔██╗ ██║██║ █╗ ██║███████║██║   ██║█████╗
    ██║╚██╗██║██║███╗██║██╔══██║╚██╗ ██╔╝██╔══╝
    ██║ ╚████║╚███╔███╔╝██║  ██║ ╚████╔╝ ███████╗
    ╚═╝  ╚═══╝ ╚══╝╚══╝ ╚═╝  ╚═╝  ╚═══╝  ╚══════╝
"""


class CelebrationService:
    """Application service for displaying welcome and celebration messages.

    This service:
    - Uses Rich library for interactive terminal output
    - Falls back to simple text in CI mode
    - Displays welcome banner, success celebration, and failure messages
    """

    # Status indicators
    CHECKMARK = "[green]✓[/green]"
    CROSS = "[red]✗[/red]"

    def __init__(
        self,
        console: Console | None = None,
        file: IO[str] | None = None,
        urls: URLConfig | None = None,
    ) -> None:
        """Initialize CelebrationService.

        Args:
            console: Optional Rich Console for output. If None, creates one.
            file: Optional file for CI mode output. If None, uses stdout.
            urls: Optional URL configuration. If None, uses default URLs.
        """
        self._file = file
        if console is not None:
            self._console = console
        else:
            self._console = Console()

        self._urls = urls if urls is not None else get_default_urls()

    def is_ci_mode(self) -> bool:
        """Check if running in CI mode.

        CI mode is detected via CI environment variable set to 'true' or '1'.

        Returns:
            True if in CI mode, False otherwise.
        """
        ci_value = os.environ.get("CI", "").lower()
        return ci_value in ("true", "1")

    def display_welcome(self) -> None:
        """Display welcome banner and message.

        Shows ASCII art banner in interactive mode, simple text in CI mode.
        """
        if self.is_ci_mode():
            self._print_ci("=" * 60)
            self._print_ci("nWave - The AI-Powered Development Framework")
            self._print_ci("=" * 60)
            self._print_ci("")
            self._print_ci("Welcome to nWave installation!")
            self._print_ci("")
            return

        # Rich mode: show colorful banner
        self._console.print()
        self._console.print(
            Panel(
                Text(NWAVE_BANNER, style="cyan bold"),
                border_style="cyan",
                padding=(0, 2),
            )
        )
        self._console.print()
        self._console.print(
            "[bold cyan]Welcome to nWave - The AI-Powered Development Framework[/bold cyan]"
        )
        self._console.print()

    def display_success(self, version: str) -> None:
        """Display success celebration message.

        Args:
            version: The version that was installed successfully.
        """
        if self.is_ci_mode():
            self._print_ci("")
            self._print_ci("[OK] Installation Complete!")
            self._print_ci(f"nWave {version} installed successfully!")
            self._print_ci("")
            return

        # Rich mode: show colorful celebration
        self._console.print()
        success_text = Text()
        success_text.append("✓ ", style="green bold")
        success_text.append("Installation Complete!", style="green bold")

        self._console.print(
            Panel(
                success_text,
                border_style="green",
                padding=(0, 2),
            )
        )
        self._console.print()
        self._console.print(
            f"[bold green]nWave {version} installed successfully![/bold green]"
        )
        self._console.print()

    def display_next_steps(self) -> None:
        """Display next steps after successful installation.

        Shows numbered list of recommended next steps.
        """
        if self.is_ci_mode():
            self._print_ci("Next Steps:")
            self._print_ci("  1. Run 'nw setup' to configure your project")
            self._print_ci("  2. Run 'nw doctor' to verify installation")
            self._print_ci(f"  3. Visit {self._urls.docs_url} for documentation")
            self._print_ci("  4. Run 'nw --help' for available commands")
            self._print_ci("")
            return

        # Rich mode: show formatted panel with next steps
        next_steps = f"""[bold]Next Steps:[/bold]

  [cyan]1.[/cyan] Run [bold]'nw setup'[/bold] to configure your project
  [cyan]2.[/cyan] Run [bold]'nw doctor'[/bold] to verify installation
  [cyan]3.[/cyan] Visit [link={self._urls.docs_url}]{self._urls.docs_url}[/link] for documentation
  [cyan]4.[/cyan] Run [bold]'nw --help'[/bold] for available commands"""

        self._console.print(
            Panel(
                next_steps,
                title="[bold]Getting Started[/bold]",
                border_style="blue",
                padding=(1, 2),
            )
        )
        self._console.print()

    def display_failure(self, error_message: str) -> None:
        """Display failure message with error and help links.

        Args:
            error_message: The error message to display.
        """
        if self.is_ci_mode():
            self._print_ci("")
            self._print_ci("[FAIL] Installation Failed")
            self._print_ci(f"Error: {error_message}")
            self._print_ci("")
            self._print_ci("Troubleshooting:")
            self._print_ci("  - Check your network connection")
            self._print_ci("  - Try running with 'pip install --verbose'")
            self._print_ci(f"  - Report issues at: {self._urls.issues_url}")
            self._print_ci("")
            return

        # Rich mode: show formatted error panel
        self._console.print()

        error_text = Text()
        error_text.append("✗ ", style="red bold")
        error_text.append("Installation Failed", style="red bold")

        self._console.print(
            Panel(
                error_text,
                border_style="red",
                padding=(0, 2),
            )
        )
        self._console.print()
        self._console.print(f"[bold red]Error:[/bold red] {error_message}")
        self._console.print()

        troubleshooting = f"""[bold]Troubleshooting:[/bold]

  [dim]•[/dim] Check your network connection
  [dim]•[/dim] Try running with [bold]'pip install --verbose'[/bold]
  [dim]•[/dim] Report issues at: [link={self._urls.issues_url}]{self._urls.issues_url}[/link]"""

        self._console.print(
            Panel(
                troubleshooting,
                title="[bold]Need Help?[/bold]",
                border_style="yellow",
                padding=(1, 2),
            )
        )
        self._console.print()

    def _print_ci(self, text: str) -> None:
        """Print text in CI mode.

        Args:
            text: Text to print.
        """
        if self._file is not None:
            self._file.write(text + "\n")
        else:
            print(text)
