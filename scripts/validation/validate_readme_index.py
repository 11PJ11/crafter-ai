#!/usr/bin/env python3
"""
README Index Validation

Validates that docs/README.md index is up-to-date with actual documentation files.
Deterministically ensures README navigation stays in sync with reality.
"""

import sys
from pathlib import Path


def scan_actual_docs(docs_dir: Path = Path("docs")) -> set[Path]:
    """
    Scan the actual documentation files.

    Returns:
        Set of relative paths to markdown files
    """
    if not docs_dir.exists():
        return set()

    md_files = set()
    for md_file in docs_dir.rglob("*.md"):
        if ".git" not in str(md_file):
            relative_path = md_file.relative_to(docs_dir.parent)
            md_files.add(relative_path)

    return md_files


def extract_readme_links(readme_path: Path = Path("docs/README.md")) -> set[Path]:
    """
    Extract all markdown links from README.md.

    Returns:
        Set of paths referenced in README
    """
    if not readme_path.exists():
        return set()

    import re

    links = set()

    with open(readme_path, encoding="utf-8") as f:
        content = f.read()

    # Find markdown links [text](path)
    pattern = r"\[.*?\]\((docs/[^\)]+\.md)\)"
    matches = re.findall(pattern, content)

    for match in matches:
        links.add(Path(match))

    return links


def validate_readme_index() -> tuple[bool, list[str]]:
    """
    Validate README index against actual files.

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    actual_docs = scan_actual_docs()
    readme_links = extract_readme_links()

    # Find files not in README
    undocumented = actual_docs - readme_links
    # Find README links to non-existent files
    broken_links = readme_links - actual_docs

    issues = []

    if undocumented:
        issues.append(f"Files not indexed in README: {len(undocumented)}")
        for file in sorted(undocumented)[:10]:  # Show first 10
            issues.append(f"  - {file}")
        if len(undocumented) > 10:
            issues.append(f"  ... and {len(undocumented) - 10} more")

    if broken_links:
        issues.append(f"Broken links in README: {len(broken_links)}")
        for link in sorted(broken_links):
            issues.append(f"  - {link}")

    return len(issues) == 0, issues


def main() -> int:
    """Main entry point."""
    print("🔍 Validating README.md index...")

    is_valid, issues = validate_readme_index()

    if is_valid:
        print("✓ README.md index is up-to-date")
        return 0
    else:
        print("\n⚠️  README.md index validation issues:")
        for issue in issues:
            print(issue)
        print(
            "\nPlease update docs/README.md to reflect current documentation structure."
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
