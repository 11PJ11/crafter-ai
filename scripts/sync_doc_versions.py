#!/usr/bin/env python3
"""
Synchronize all documentation versions with framework version.

Reads version from nWave/framework-catalog.yaml and updates all
markdown documents with **Version**: fields to match.
"""

import re
import sys
from datetime import date
from pathlib import Path

import yaml


def get_framework_version():
    """Get version from framework-catalog.yaml."""
    catalog_path = Path(__file__).parent.parent / "nWave" / "framework-catalog.yaml"

    with open(catalog_path) as f:
        catalog = yaml.safe_load(f)

    return catalog["version"]


def find_docs_with_versions():
    """Find all markdown files with **Version**: fields."""
    docs_dir = Path(__file__).parent.parent / "docs"
    version_policy = Path(__file__).parent.parent / "VERSION_POLICY.md"

    files_with_versions = []

    # Check docs directory
    for md_file in docs_dir.rglob("*.md"):
        content = md_file.read_text()
        if re.search(r"^\*\*Version\*\*:", content, re.MULTILINE):
            files_with_versions.append(md_file)

    # Check VERSION_POLICY.md
    if version_policy.exists():
        content = version_policy.read_text()
        if re.search(r"^\*\*Version\*\*:", content, re.MULTILINE):
            files_with_versions.append(version_policy)

    return files_with_versions


def update_doc_version(file_path, target_version):
    """Update version field in a markdown file."""
    content = file_path.read_text()

    # Pattern: **Version**: X.Y.Z or X.Y
    pattern = r"(\*\*Version\*\*:)\s*[\d.]+(?:\.\d+)?(?:\.\d+)?"
    replacement = rf"\1 {target_version}"

    updated_content = re.sub(pattern, replacement, content)

    # Update date if **Date**: field exists
    date_pattern = r"(\*\*Date\*\*:)\s*\d{4}-\d{2}-\d{2}"
    date_replacement = rf"\1 {date.today().isoformat()}"
    updated_content = re.sub(date_pattern, date_replacement, updated_content)

    if content != updated_content:
        file_path.write_text(updated_content)
        return True

    return False


def main():
    print("Synchronizing documentation versions with framework...")

    # Get framework version
    framework_version = get_framework_version()
    print(f"✓ Framework version: {framework_version}")

    # Find all docs with versions
    docs = find_docs_with_versions()
    print(f"✓ Found {len(docs)} documents with version fields")

    # Update each document
    updated_count = 0
    for doc in docs:
        relative_path = doc.relative_to(Path(__file__).parent.parent)
        if update_doc_version(doc, framework_version):
            print(f"  • Updated: {relative_path}")
            updated_count += 1
        else:
            print(f"  ✓ Already current: {relative_path}")

    print(
        f"\n✓ Synchronized {updated_count}/{len(docs)} documents to version {framework_version}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
