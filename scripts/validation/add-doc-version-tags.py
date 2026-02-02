#!/usr/bin/env python3
"""
Add Version Tags to Documentation Files

Adds semantic version tags to markdown documentation files that don't have them.
Uses HTML comment format: <!-- version: X.Y.Z -->

Usage:
    python scripts/add-doc-version-tags.py [--dry-run] [--initial-version VERSION]
"""

import argparse
import re
import sys
from pathlib import Path


class VersionTagger:
    """Add version tags to markdown documentation files"""

    def __init__(self, initial_version: str = "1.0.0", dry_run: bool = False):
        self.initial_version = initial_version
        self.dry_run = dry_run
        self.version_pattern = re.compile(
            r"<!--\s*version:\s*([0-9]+\.[0-9]+\.[0-9]+)\s*-->"
        )

    def has_version_tag(self, content: str) -> bool:
        """Check if content already has a version tag"""
        return bool(self.version_pattern.search(content))

    def add_version_tag(self, file_path: Path) -> tuple[bool, str]:
        """
        Add version tag to file if it doesn't have one.
        Returns (modified, message)
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            if self.has_version_tag(content):
                return False, f"Already has version tag: {file_path}"

            # Add version tag at the top (after any frontmatter if present)
            version_comment = f"<!-- version: {self.initial_version} -->\n\n"

            # Check for YAML frontmatter
            if content.startswith("---\n"):
                # Find end of frontmatter
                end_marker = content.find("\n---\n", 4)
                if end_marker != -1:
                    # Insert after frontmatter
                    new_content = (
                        content[: end_marker + 5]
                        + version_comment
                        + content[end_marker + 5 :]
                    )
                else:
                    # Malformed frontmatter, add at top
                    new_content = version_comment + content
            else:
                # No frontmatter, add at top
                new_content = version_comment + content

            if self.dry_run:
                return True, f"Would add version tag to: {file_path}"

            # Write updated content
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            return True, f"Added version tag to: {file_path}"

        except Exception as e:
            return False, f"Error processing {file_path}: {e}"

    def process_files(self, file_patterns: list[str]) -> dict:
        """
        Process multiple file patterns.
        Returns statistics dictionary.
        """
        stats = {"total": 0, "modified": 0, "skipped": 0, "errors": 0}

        for pattern in file_patterns:
            for file_path in Path().glob(pattern):
                if not file_path.is_file():
                    continue

                stats["total"] += 1
                modified, message = self.add_version_tag(file_path)

                if modified:
                    stats["modified"] += 1
                    print(f"✓ {message}")
                elif "Error" in message:
                    stats["errors"] += 1
                    print(f"✗ {message}", file=sys.stderr)
                else:
                    stats["skipped"] += 1
                    print(f"  {message}")

        return stats


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Add version tags to documentation files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without modifying files",
    )
    parser.add_argument(
        "--initial-version",
        default="1.0.0",
        help="Initial version to use (default: 1.0.0)",
    )
    parser.add_argument(
        "--pattern",
        action="append",
        help="File pattern to process (can be specified multiple times)",
    )

    args = parser.parse_args()

    # Default patterns if none specified
    patterns = args.pattern or [
        "README.md",
        "nWave/README.md",
        "scripts/README.md",
        "scripts/*/README.md",
        "tools/README.md",
        "nWave/*/README.md",
        "nWave/*/*/README.md",
        "docs/README.md",
        "docs/*/README.md",
    ]

    tagger = VersionTagger(initial_version=args.initial_version, dry_run=args.dry_run)

    print("Adding version tags to documentation files...")
    if args.dry_run:
        print("[DRY RUN MODE - No files will be modified]\n")

    stats = tagger.process_files(patterns)

    print("\n" + "=" * 60)
    print(f"Total files processed: {stats['total']}")
    print(f"Files modified: {stats['modified']}")
    print(f"Files skipped (already tagged): {stats['skipped']}")
    print(f"Errors: {stats['errors']}")
    print("=" * 60)

    return 0 if stats["errors"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
