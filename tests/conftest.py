"""Root conftest.py for all tests - ensures test isolation."""

import os
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def restore_working_directory():
    """
    Automatically restore the working directory after each test.

    This fixture ensures that tests which change the working directory
    (e.g., using os.chdir()) don't affect subsequent tests.

    The working directory is restored to the project root, which is
    determined by finding the directory containing pytest.ini.
    """
    # Save original working directory
    original_cwd = os.getcwd()

    # Ensure we're in the project root (directory containing pytest.ini)
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    yield

    # Restore original working directory after test
    os.chdir(original_cwd)
