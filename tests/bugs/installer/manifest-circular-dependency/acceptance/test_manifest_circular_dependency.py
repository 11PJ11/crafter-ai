"""
Installer Bug: Manifest Circular Dependency - Acceptance Tests.

Tests that verify:
- Fresh installation creates manifest before validation
- Validation doesn't fail due to missing manifest
- Manifest creation is independent of validation result
- Installation completes successfully with manifest present
"""

from pytest_bdd import scenarios

# Import step definitions - must use star imports for pytest-bdd registration
from .steps.common_steps import *  # noqa: F403
from .steps.installer_steps import *  # noqa: F403
from .steps.manifest_steps import *  # noqa: F403


# Collect all scenarios from the feature file
scenarios("manifest-circular-dependency.feature")
