"""
Test file for dependency verification acceptance tests (AC-06).

This file imports step definitions and loads scenarios from feature files.
pytest-bdd requires test files to be named test_*.py for discovery.
"""

from tests.acceptance.installation.step_defs.steps_dependency import *  # noqa: F401, F403
from tests.acceptance.installation.step_defs.steps_preflight import *  # noqa: F401, F403
