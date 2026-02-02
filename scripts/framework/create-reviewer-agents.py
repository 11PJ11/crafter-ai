#!/usr/bin/env python3
"""
Create Haiku-powered reviewer agents from base agents.
Each reviewer agent is optimized for cost-efficient review operations.
"""

# Version - Must match nWave/framework-catalog.yaml version
__version__ = "1.2.26"

import re
import sys
from pathlib import Path


# Define agent mappings and review focus descriptions
AGENTS = {
    "acceptance-designer": "Acceptance criteria and BDD review specialist",
    "agent-builder": "Agent design and quality review specialist",
    "data-engineer": "Data architecture and pipeline review specialist",
    "devop": "Deployment readiness and operations review specialist",
    "illustrator": "Visual diagram and documentation review specialist",
    "product-owner": "Requirements and business alignment review specialist",
    "researcher": "Research quality and evidence review specialist",
    "skeleton-builder": "Walking skeleton and E2E review specialist",
    "software-crafter": "Code quality and implementation review specialist",
    "solution-architect": "Architecture design and patterns review specialist",
    "troubleshooter": "Risk analysis and failure mode review specialist",
    "visual-architect": "Architecture diagram accuracy review specialist",
}


def create_reviewer_agent(base_agent_name, review_description):
    """Create a reviewer version of a base agent."""

    base_path = Path(
        f"/mnt/c/Repositories/Projects/nwave/nWave/agents/{base_agent_name}.md"
    )
    reviewer_path = Path(
        f"/mnt/c/Repositories/Projects/nwave/nWave/agents/{base_agent_name}-reviewer.md"
    )

    if not base_path.exists():
        print(f"❌ Base agent not found: {base_agent_name}.md")
        return False

    # Read the base agent file
    with open(base_path, encoding="utf-8") as f:
        content = f.read()

    # Update YAML frontmatter
    # Change model from 'inherit' to 'haiku'
    content = re.sub(
        r"^model:\s+inherit.*$", "model: haiku", content, flags=re.MULTILINE
    )

    # Update name field
    content = re.sub(
        r"^name:\s+(.+)$",
        f"name: {base_agent_name}-reviewer",
        content,
        flags=re.MULTILINE,
    )

    # Update description field
    content = re.sub(
        r"^description:\s+(.+)$",
        f"description: {review_description} - Optimized for cost-efficient review operations using Haiku model",
        content,
        flags=re.MULTILINE,
    )

    # Update the agent id in YAML block
    content = re.sub(r"(\s+id:\s+)([^\s]+)", rf"\1{base_agent_name}-reviewer", content)

    # Update whenToUse field
    content = re.sub(
        r"(\s+whenToUse:\s+)(.+)",
        rf"\1Use for review and critique tasks - {review_description}. Runs on Haiku for cost efficiency.",
        content,
    )

    # Update the title
    content = re.sub(r"(\s+title:\s+)(.+)", r"\1\2 (Review Specialist)", content)

    # Add review focus to the role
    content = re.sub(r"(\s+role:\s+)(.+)", r"\1Review & Critique Expert - \2", content)

    # Update the header comment
    content = re.sub(
        f"^# {base_agent_name}$",
        f"# {base_agent_name}-reviewer",
        content,
        flags=re.MULTILINE,
    )

    # Add a note about review focus at the beginning of the persona section
    if "persona:" in content:
        content = re.sub(
            r"(persona:\s*\n)",
            r"\1  # Review-focused variant using Haiku model for cost efficiency\n",
            content,
        )

    # Write the reviewer agent file
    with open(reviewer_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Created: {base_agent_name}-reviewer.md")
    return True


def main():
    """Create all reviewer agents."""
    print("=" * 60)
    print("Creating Haiku-Powered Reviewer Agents")
    print("=" * 60)
    print()

    success_count = 0

    for agent_name, review_description in AGENTS.items():
        if create_reviewer_agent(agent_name, review_description):
            success_count += 1

    print()
    print("=" * 60)
    print(f"Summary: {success_count}/{len(AGENTS)} reviewer agents created")
    print("=" * 60)

    if success_count == len(AGENTS):
        print("\n✅ All reviewer agents created successfully!")
        print("\nNext steps:")
        print("1. Update review.md command to auto-append -reviewer suffix")
        print("2. Run build pipeline: ./scripts/update-nwave.sh")
        print("3. Test with: /nw:review @software-crafter task 'file.json'")
    else:
        print("\n⚠️ Some agents failed to create. Please check the errors above.")

    return success_count == len(AGENTS)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
