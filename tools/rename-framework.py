#!/usr/bin/env python3
"""
Framework Rename Automation Script
Renames nWave to nWave across all framework files
"""

import argparse
import re
from pathlib import Path
from typing import List, Dict, Tuple

# Replacement patterns (order matters - most specific first!)
REPLACEMENTS = [
    # Directory paths
    (r'nWave/', 'nWave/'),
    (r'"nWave"', '"nWave"'),
    (r"'nWave'", "'nWave'"),
    (r'=nWave', '=nWave'),

    # IDE category paths
    (r'agents/nw', 'agents/nw'),
    (r'commands/nw', 'commands/nw'),
    (r'"nw"', '"nw"'),  # In config contexts (quoted)

    # Command prefixes (with colon to avoid confusion)
    (r'/nw:', '/nw:'),

    # Branding (all variations)
    (r'nWave', 'nWave'),
    (r'nWave', 'nWave'),
    (r'nWave', 'nWave'),  # Remaining lowercase (not in paths)
]

EXCLUDE_DIRS = {'.git', 'dist', 'output', 'node_modules', '__pycache__'}
INCLUDE_EXTENSIONS = {'.md', '.py', '.sh', '.yaml', '.yml', '.json', '.txt'}

def should_process_file(file_path: Path) -> bool:
    """Determine if file should be processed."""
    if any(parent.name in EXCLUDE_DIRS for parent in file_path.parents):
        return False
    return file_path.suffix in INCLUDE_EXTENSIONS

def apply_replacements(content: str, file_path: Path, dry_run: bool, verbose: bool) -> Tuple[str, int]:
    """Apply all replacement patterns to content."""
    modified_content = content
    total_replacements = 0

    for pattern, replacement in REPLACEMENTS:
        count = len(re.findall(pattern, modified_content))
        if count > 0:
            modified_content = re.sub(pattern, replacement, modified_content)
            total_replacements += count
            if verbose:
                print(f"  {file_path.name}: {pattern} → {replacement} ({count}x)")

    return modified_content, total_replacements

def rename_files_in_directory(root_dir: Path, dry_run: bool = False, verbose: bool = False) -> Dict[str, int]:
    """Process all eligible files in directory tree."""
    stats = {
        'files_processed': 0,
        'files_modified': 0,
        'total_replacements': 0
    }

    for file_path in root_dir.rglob('*'):
        if not file_path.is_file() or not should_process_file(file_path):
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            modified_content, replacements = apply_replacements(
                original_content, file_path, dry_run, verbose
            )

            stats['files_processed'] += 1

            if replacements > 0:
                stats['files_modified'] += 1
                stats['total_replacements'] += replacements

                if not dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(modified_content)
                    print(f"✓ Modified: {file_path.relative_to(root_dir)} ({replacements}x)")
                else:
                    print(f"[DRY RUN] Would modify: {file_path.relative_to(root_dir)} ({replacements}x)")

        except Exception as e:
            print(f"✗ Error processing {file_path}: {e}")

    return stats

def main():
    parser = argparse.ArgumentParser(description='Rename nWave to nWave')
    parser.add_argument('--root', type=Path, default=Path.cwd(),
                       help='Root directory to process (default: current directory)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be changed without modifying files')
    parser.add_argument('--verbose', action='store_true',
                       help='Show detailed replacement information')

    args = parser.parse_args()

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Renaming framework: nWave → nWave")
    print(f"Root directory: {args.root}")
    print(f"Excluded: {', '.join(EXCLUDE_DIRS)}")
    print()

    stats = rename_files_in_directory(args.root, args.dry_run, args.verbose)

    print()
    print("=" * 60)
    print(f"Files processed: {stats['files_processed']}")
    print(f"Files modified: {stats['files_modified']}")
    print(f"Total replacements: {stats['total_replacements']}")
    print("=" * 60)

if __name__ == '__main__':
    main()
