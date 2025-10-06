#!/usr/bin/env python3
"""
Remove duplicate framework sections from agent files.

This script removes the duplicate "Production Frameworks (YAML Format)" sections
that were added at the end of agent files, keeping only the comprehensive frameworks
that appear earlier in the files.
"""

import re
from pathlib import Path

# Agent files to clean
AGENT_FILES = [
    "5d-wave/agents/acceptance-designer.md",
    "5d-wave/agents/architecture-diagram-manager.md",
    "5d-wave/agents/business-analyst.md",
    "5d-wave/agents/data-engineer.md",
    "5d-wave/agents/feature-completion-coordinator.md",
    "5d-wave/agents/knowledge-researcher.md",
    "5d-wave/agents/root-cause-analyzer.md",
    "5d-wave/agents/software-crafter.md",
    "5d-wave/agents/solution-architect.md",
    "5d-wave/agents/visual-2d-designer.md",
    "5d-wave/agents/walking-skeleton-helper.md",
]

def remove_duplicate_frameworks(file_path: Path) -> tuple[bool, str]:
    """
    Remove duplicate framework section from an agent file.

    Args:
        file_path: Path to agent file

    Returns:
        Tuple of (success, message)
    """
    try:
        content = file_path.read_text(encoding='utf-8')

        # Find the duplicate section marker
        marker = "# Production Frameworks (YAML Format)"

        if marker not in content:
            return (True, f"No duplicate frameworks found in {file_path.name}")

        # Split at the marker and keep only the part before it
        parts = content.split(marker)

        if len(parts) == 1:
            return (True, f"No duplicate frameworks found in {file_path.name}")

        # Keep everything before the duplicate section
        cleaned_content = parts[0].rstrip() + "\n"

        # Calculate what was removed
        original_lines = len(content.splitlines())
        cleaned_lines = len(cleaned_content.splitlines())
        removed_lines = original_lines - cleaned_lines

        # Write cleaned content back
        file_path.write_text(cleaned_content, encoding='utf-8')

        return (True, f"✅ {file_path.name}: Removed {removed_lines} lines of duplicate frameworks")

    except Exception as e:
        return (False, f"❌ {file_path.name}: Error - {str(e)}")


def main():
    """Main execution function."""
    print("🧹 Removing Duplicate Framework Sections from Agents\n")
    print("=" * 70)

    project_root = Path(__file__).parent.parent
    results = []
    success_count = 0
    total_removed_lines = 0

    for agent_file in AGENT_FILES:
        file_path = project_root / agent_file

        if not file_path.exists():
            results.append((False, f"❌ {agent_file}: File not found"))
            continue

        success, message = remove_duplicate_frameworks(file_path)
        results.append((success, message))

        if success:
            success_count += 1
            # Extract removed lines count from message
            if "Removed" in message:
                removed = int(message.split("Removed ")[1].split(" lines")[0])
                total_removed_lines += removed

    # Print results
    print("\n📊 Results:\n")
    for success, message in results:
        print(message)

    print("\n" + "=" * 70)
    print(f"\n✅ Successfully cleaned {success_count}/{len(AGENT_FILES)} agents")
    print(f"📉 Total lines removed: {total_removed_lines}")

    if success_count == len(AGENT_FILES):
        print("\n🎉 All agents cleaned successfully!")
        return 0
    else:
        print("\n⚠️  Some agents had issues - please review above")
        return 1


if __name__ == "__main__":
    exit(main())
