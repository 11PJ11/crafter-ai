"""
Test file for post-installation verification acceptance tests (AC-07, AC-08).

This file imports step definitions and loads scenarios from feature files.
pytest-bdd requires test files to be named test_*.py for discovery.
"""

from tests.acceptance.installation.step_defs.steps_verification import *  # noqa: F401, F403
from tests.acceptance.installation.step_defs.steps_preflight import *  # noqa: F401, F403
