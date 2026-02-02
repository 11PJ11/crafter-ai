"""
CLI module for nWave commands.

Contains driving adapters (CLI entry points) for user interaction.
"""

import click


@click.group()
@click.version_option(version="0.0.0", prog_name="nw")
def main():
    """nWave CLI - AI-driven software development workflow."""
    pass


@main.command()
def version():
    """Show version information."""
    click.echo("nWave version 0.0.0")


if __name__ == "__main__":
    main()
