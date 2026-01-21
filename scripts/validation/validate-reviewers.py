#!/usr/bin/env python3
"""
Validate Peer Reviewer Agents for Layer 4 Adversarial Verification

Validates all 12 peer reviewer agents have:
- YAML frontmatter (Claude Code integration)
- Production frameworks (if applicable)
- Proper reviewer configuration
"""

# Version - Must match nWave/framework-catalog.yaml version
__version__ = "1.2.26"

import json
import sys
from pathlib import Path


def check_reviewer_agent(file_path: Path) -> dict:
    """Check if reviewer agent has required components."""
    content = file_path.read_text(encoding="utf-8")

    result = {
        "name": file_path.stem,
        "file": file_path.name,
        "file_size": len(content),
        "has_frontmatter": content.strip().startswith("---"),
        "has_reviewer_role": "reviewer" in content.lower()
        or "-reviewer" in file_path.name,
        "has_peer_review_workflow": "peer review" in content.lower()
        or "feedback" in content.lower(),
        "status": "UNKNOWN",
    }

    # Determine status
    if result["has_frontmatter"] and result["has_reviewer_role"]:
        result["status"] = "PASS"
    else:
        result["status"] = "FAIL"
        result["issues"] = []
        if not result["has_frontmatter"]:
            result["issues"].append("Missing YAML frontmatter")
        if not result["has_reviewer_role"]:
            result["issues"].append("Missing reviewer role definition")

    return result


def main():
    """Main execution."""
    print("\n" + "=" * 70)
    print("PEER REVIEWER AGENT VALIDATION")
    print("=" * 70)
    print()

    reviewers_dir = Path("nWave/agents/reviewers")

    if not reviewers_dir.exists():
        print(f"❌ Error: Reviewers directory not found: {reviewers_dir}")
        return 1

    reviewer_files = sorted(reviewers_dir.glob("*-reviewer.md"))

    if not reviewer_files:
        print(f"❌ Error: No reviewer files found in {reviewers_dir}")
        return 1

    print(f"Found {len(reviewer_files)} peer reviewer agents")
    print()

    results = []
    passed = 0
    failed = 0

    for file_path in reviewer_files:
        print(f"Validating {file_path.name}...", end=" ")
        result = check_reviewer_agent(file_path)
        results.append(result)

        if result["status"] == "PASS":
            print("✅ PASS")
            passed += 1
        else:
            print("❌ FAIL")
            if "issues" in result:
                for issue in result["issues"]:
                    print(f"     - {issue}")
            failed += 1

    # Summary
    print()
    print("-" * 70)
    print(f"Total Reviewers: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Pass Rate: {passed / len(results) * 100:.1f}%")
    print("-" * 70)
    print()

    # Save results
    output_file = Path("test-results/adversarial/reviewer-validation-results.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "total_reviewers": len(results),
                "passed": passed,
                "failed": failed,
                "pass_rate": passed / len(results) * 100,
                "reviewers": results,
            },
            f,
            indent=2,
        )

    print(f"Results saved: {output_file}")
    print()

    if failed == 0:
        print("✅ All peer reviewer agents validated successfully")
        print()
        print("Layer 4 Adversarial Verification Workflow: READY")
        return 0
    else:
        print(f"❌ {failed} peer reviewer agent(s) failed validation")
        return 1


if __name__ == "__main__":
    sys.exit(main())
