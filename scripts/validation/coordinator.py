#!/usr/bin/env python3
"""
Validation Coordinator

Orchestrates all nWave framework validators.
Used as pre-commit hook entry point.
"""

import sys


# Import validators
try:
    from scripts.validation import validate_formatter_env, validate_readme_index
    # Agent, command, and step validators are standalone scripts
except ImportError:
    import validate_formatter_env
    import validate_readme_index


def run_all_validators(skip_slow: bool = False) -> tuple[bool, dict[str, dict]]:
    """
    Run all validators and collect results.

    Args:
        skip_slow: Skip slow validators (agent, command compliance)

    Returns:
        Tuple of (all_passed, results_dict)
    """
    results = {}

    # Fast validators (always run)
    print("\n=== Running Fast Validators ===")

    # Formatter environment
    print("\n1. Formatter Environment...")
    env_valid, env_issues = validate_formatter_env.validate_formatter_environment()
    results["formatter_env"] = {"passed": env_valid, "issues": env_issues}

    # README index
    print("\n2. README Index...")
    readme_valid, readme_issues = validate_readme_index.validate_readme_index()
    results["readme_index"] = {"passed": readme_valid, "issues": readme_issues}

    # Slow validators (optional)
    if not skip_slow:
        print("\n=== Running Compliance Validators ===")
        print("(Note: Agent/Command/Step validators run as standalone scripts)")
        print("Run individually if needed:")
        print("  python scripts/validation/validate_agents.py")
        print("  python scripts/validation/validate_commands.py")
        print("  python scripts/validation/validate_steps.py")

    # Aggregate results
    all_passed = all(r["passed"] for r in results.values())

    return all_passed, results


def print_summary(all_passed: bool, results: dict[str, dict]) -> None:
    """Print validation summary."""
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    for validator_name, result in results.items():
        status = "✓ PASSED" if result["passed"] else "❌ FAILED"
        print(f"{validator_name}: {status}")
        if not result["passed"] and result["issues"]:
            for issue in result["issues"][:5]:  # Show first 5
                print(f"  {issue}")

    print("=" * 60)
    if all_passed:
        print("✓ ALL VALIDATIONS PASSED")
    else:
        print("❌ VALIDATION FAILURES DETECTED")
    print("=" * 60)


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Run nWave framework validators")
    parser.add_argument(
        "--skip-slow", action="store_true", help="Skip slow compliance validators"
    )
    parser.add_argument("--fast", action="store_true", help="Alias for --skip-slow")

    args = parser.parse_args()
    skip_slow = args.skip_slow or args.fast

    print("🔍 nWave Framework Validation")
    print(f"Mode: {'Fast' if skip_slow else 'Full'}")

    all_passed, results = run_all_validators(skip_slow=skip_slow)
    print_summary(all_passed, results)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
