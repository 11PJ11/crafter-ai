"""
Fixtures for unit CLI tests.

Re-exports the cli_runner fixture from tests/cli/conftest.py.
"""

import pytest
from typer.testing import CliRunner


@pytest.fixture
def cli_runner() -> CliRunner:
    """
    Provide a standard CLI test runner for testing Typer commands.

    Returns:
        CliRunner: Typer CLI test runner.
    """
    return CliRunner()
