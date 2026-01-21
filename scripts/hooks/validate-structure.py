#!/usr/bin/env python3
"""
nWave Structure Validation Hook

Pre-commit hook coordinator for all nWave framework validators.
Orchestrates validation checks before allowing commits.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.validation.coordinator import run_all_validators, print_summary
except ImportError:
    print("❌ Cannot import validation coordinator")
    print("Ensure scripts/validation/ module is in PYTHONPATH")
    sys.exit(1)


def main() -> int:
    """Run all validators as pre-commit hook."""
    print("🔍 nWave Pre-Commit Structure Validation")

    # Run fast validators only (skip slow compliance checks)
    all_passed, results = run_all_validators(skip_slow=True)

    if all_passed:
        print("\n✓ All structure validations passed")
        return 0
    else:
        print_summary(all_passed, results)
        print("\n❌ Pre-commit validation failed")
        print("Fix issues above before committing")
        return 1


if __name__ == "__main__":
    sys.exit(main())
