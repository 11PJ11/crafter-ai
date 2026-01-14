#!/usr/bin/env python3
"""
Remove YAML Frontmatter from Task Files

Removes YAML frontmatter from nWave/tasks/nw/*.md files since the build system
ignores it and uses framework-catalog.yaml as the source of truth instead.
"""

import re
from pathlib import Path


def remove_frontmatter(file_path: Path) -> bool:
    """
    Remove YAML frontmatter from a markdown file.

    Args:
        file_path: Path to markdown file

    Returns:
        bool: True if frontmatter was removed, False otherwise
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check if file starts with YAML frontmatter (---)
        if not content.startswith("---\n"):
            print(f"  ⏭️  {file_path.name} - No frontmatter detected")
            return False

        # Find the end of frontmatter (second ---)
        match = re.match(r"^---\n(.*?)\n---\n+", content, re.DOTALL)

        if not match:
            print(f"  ⚠️  {file_path.name} - Malformed frontmatter (no closing ---)")
            return False

        # Extract content after frontmatter
        content_without_frontmatter = content[match.end() :]

        # Write back without frontmatter
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content_without_frontmatter)

        print(
            f"  ✓  {file_path.name} - Frontmatter removed ({len(match.group(1).split('\\n'))} lines)"
        )
        return True

    except Exception as e:
        print(f"  ✗  {file_path.name} - Error: {e}")
        return False


def main():
    tasks_dir = Path(__file__).parent.parent / "nWave" / "tasks" / "nw"

    print("Removing YAML frontmatter from task files...")
    print(f"Directory: {tasks_dir}")
    print()

    task_files = sorted(tasks_dir.glob("*.md"))

    if not task_files:
        print("No task files found!")
        return

    removed_count = 0
    for task_file in task_files:
        if remove_frontmatter(task_file):
            removed_count += 1

    print()
    print(f"Summary: {removed_count}/{len(task_files)} files modified")
    print()
    print("Rationale: YAML frontmatter in task files is IGNORED by the build system.")
    print(
        "           framework-catalog.yaml is the SOURCE OF TRUTH for command metadata."
    )


if __name__ == "__main__":
    main()
