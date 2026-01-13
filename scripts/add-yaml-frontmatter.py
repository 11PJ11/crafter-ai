#!/usr/bin/env python3
"""
Add YAML Frontmatter to Agent Files for Claude Code Integration

This script adds Claude Code-compatible YAML frontmatter to agent files
that are missing it, ensuring 100% compliance validation.

YAML Frontmatter Format:
---
name: agent-name
description: Agent purpose and use case
model: inherit
---
"""

import re
import sys
from pathlib import Path
from typing import Dict, Optional


# Agent descriptions extracted from whenToUse fields
AGENT_DESCRIPTIONS = {
    "business-analyst": "Use for DISCUSS wave - processing user requirements and creating structured business requirements documentation with stakeholder collaboration",

    "solution-architect": "Use for DESIGN wave - collaborates with user to define system architecture, technology selection, and creates visual architecture diagrams with business value focus",

    "acceptance-designer": "Use for DISTILL wave - creates E2E acceptance tests informed by architectural context, with business validation and production service integration patterns",

    "software-crafter": "Use for complete DEVELOP wave execution - implementing features through Outside-In TDD, managing complex refactoring roadmaps with Mikado Method, and systematic code quality improvement through progressive refactoring",

    "feature-completion-coordinator": "Use for DEMO wave - coordinates end-to-end feature completion workflow including deployment readiness validation, stakeholder demonstration preparation, and production rollout coordination",

    "architecture-diagram-manager": "Maintains and updates architecture diagrams based on refactoring changes, ensuring visual documentation stays synchronized with code evolution",

    "visual-2d-designer": "Creates visual 2D diagrams and design artifacts for architecture, workflows, and system documentation using text-based diagram formats",

    "root-cause-analyzer": "Use when investigating system failures, recurring issues, unexpected behaviors, or complex bugs requiring systematic root cause analysis with evidence-based investigation",

    "walking-skeleton-helper": "Guides teams through creating minimal end-to-end implementations to validate architecture, technology choices, and deployment pipeline before full feature development",

    # These already have frontmatter, but include for completeness
    "agent-forger": "Use for creating high-quality, safe, and specification-compliant AI agents using research-validated patterns, comprehensive validation, and quality assurance frameworks",

    "knowledge-researcher": "Use for conducting evidence-based research with source verification, systematic knowledge synthesis, and comprehensive documentation of findings with citation tracking",

    "data-engineer": "Use for data engineering tasks including data pipeline design, ETL workflow implementation, data modeling, and integration with various data sources and processing frameworks"
}


def has_yaml_frontmatter(content: str) -> bool:
    """Check if content starts with YAML frontmatter."""
    return content.strip().startswith('---')


def extract_agent_name_from_content(content: str) -> Optional[str]:
    """Extract agent name from file content."""
    # Look for "# agent-name" heading
    match = re.search(r'^# ([a-z-]+)', content, re.MULTILINE)
    if match:
        return match.group(1)

    # Look for agent.id in YAML block
    match = re.search(r'^\s*id:\s*([a-z-]+)', content, re.MULTILINE)
    if match:
        return match.group(1)

    return None


def create_yaml_frontmatter(agent_name: str, description: str) -> str:
    """Create YAML frontmatter block."""
    return f"""---
name: {agent_name}
description: {description}
model: inherit
---

"""


def add_frontmatter_to_file(file_path: Path) -> bool:
    """
    Add YAML frontmatter to agent file if missing.
    Returns True if frontmatter was added, False if already present.
    """
    # Read file
    content = file_path.read_text(encoding='utf-8')

    # Check if frontmatter already present
    if has_yaml_frontmatter(content):
        print(f"  ✅ {file_path.name}: Frontmatter already present")
        return False

    # Extract agent name from content
    agent_name = extract_agent_name_from_content(content)
    if not agent_name:
        print(f"  ❌ {file_path.name}: Could not extract agent name")
        return False

    # Get description
    description = AGENT_DESCRIPTIONS.get(agent_name)
    if not description:
        print(f"  ⚠️  {file_path.name}: No description found for '{agent_name}', skipping")
        return False

    # Create frontmatter
    frontmatter = create_yaml_frontmatter(agent_name, description)

    # Remove leading blank lines from content
    content_stripped = content.lstrip('\n')

    # Prepend frontmatter
    new_content = frontmatter + content_stripped

    # Write back
    file_path.write_text(new_content, encoding='utf-8')

    print(f"  ✅ {file_path.name}: Added YAML frontmatter for '{agent_name}'")
    return True


def main():
    """Main execution function."""
    print("\n" + "=" * 70)
    print("ADD YAML FRONTMATTER TO AGENT FILES")
    print("=" * 70)
    print()

    # Get agents directory
    agents_dir = Path("nWave/agents")
    if not agents_dir.exists():
        print(f"❌ Error: Agents directory not found: {agents_dir}")
        return 1

    # Get all agent files
    agent_files = sorted(agents_dir.glob("*.md"))

    if not agent_files:
        print(f"❌ Error: No agent files found in {agents_dir}")
        return 1

    print(f"Found {len(agent_files)} agent files")
    print()

    # Process each file
    added_count = 0
    skipped_count = 0
    error_count = 0

    for file_path in agent_files:
        try:
            if add_frontmatter_to_file(file_path):
                added_count += 1
            else:
                skipped_count += 1
        except Exception as e:
            print(f"  ❌ {file_path.name}: Error - {e}")
            error_count += 1

    # Summary
    print()
    print("-" * 70)
    print("Summary:")
    print(f"  Frontmatter added: {added_count}")
    print(f"  Already present: {skipped_count}")
    print(f"  Errors: {error_count}")
    print("-" * 70)
    print()

    if error_count > 0:
        print("⚠️  Some files had errors. Review output above.")
        return 1

    if added_count > 0:
        print("✅ YAML frontmatter successfully added to all missing agents")
        print()
        print("Next steps:")
        print("  1. Validate compliance: python3 scripts/validate-agent-compliance-v2.py")
        print("  2. Verify 12/12 agents pass validation")
        print()
    else:
        print("✅ All agents already have YAML frontmatter")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
