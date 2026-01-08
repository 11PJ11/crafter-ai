#!/usr/bin/env python3
"""
Token Baseline Measurement Script

Measures token counts for Markdown files using OpenAI's tiktoken library.
Designed for AI-Craft Framework agent/command file migration tracking.

Usage:
    python measure-tokens.py --input-dir 5d-wave/agents --output-file baseline/phase-2-agents.json
    python measure-tokens.py --input-dir 5d-wave/commands --output-file baseline/phase-2-commands.json

Requirements:
    pip install tiktoken

Author: AI-Craft Framework Team
License: MIT
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

try:
    import tiktoken
except ImportError:
    print("ERROR: tiktoken library not found.", file=sys.stderr)
    print("Install with: pip install tiktoken", file=sys.stderr)
    sys.exit(1)


def count_tokens(file_path: Path, encoding) -> int:
    """
    Count tokens in a file using tiktoken encoding.
    
    Args:
        file_path: Path to the file to tokenize
        encoding: tiktoken encoding object
        
    Returns:
        Number of tokens in the file
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        tokens = encoding.encode(content)
        return len(tokens)
    except Exception as e:
        print(f"ERROR: Failed to tokenize {file_path}: {e}", file=sys.stderr)
        raise


def measure_file(file_path: Path, encoding) -> Dict[str, Any]:
    """
    Measure all metrics for a single file.
    
    Args:
        file_path: Path to the file to measure
        encoding: tiktoken encoding object
        
    Returns:
        Dictionary with file_path, byte_count, line_count, token_count
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        byte_count = len(content.encode('utf-8'))
        line_count = content.count('\n') + 1
        token_count = count_tokens(file_path, encoding)
        
        return {
            "file_path": str(file_path),
            "byte_count": byte_count,
            "line_count": line_count,
            "token_count": token_count
        }
    except Exception as e:
        print(f"ERROR: Failed to measure {file_path}: {e}", file=sys.stderr)
        raise


def discover_markdown_files(input_dir: Path) -> List[Path]:
    """
    Discover all .md files in the input directory recursively.
    
    Args:
        input_dir: Directory to search
        
    Returns:
        Sorted list of .md file paths
    """
    if not input_dir.exists():
        print(f"ERROR: Input directory does not exist: {input_dir}", file=sys.stderr)
        sys.exit(1)
        
    if not input_dir.is_dir():
        print(f"ERROR: Input path is not a directory: {input_dir}", file=sys.stderr)
        sys.exit(1)
    
    md_files = sorted(input_dir.rglob("*.md"))
    
    if not md_files:
        print(f"WARNING: No .md files found in {input_dir}", file=sys.stderr)
    
    return md_files


def validate_files(file_paths: List[Path]) -> None:
    """
    Validate that all files exist and are readable.
    
    Args:
        file_paths: List of file paths to validate
        
    Raises:
        SystemExit if any file is missing or unreadable
    """
    missing_files = []
    unreadable_files = []
    
    for file_path in file_paths:
        if not file_path.exists():
            missing_files.append(str(file_path))
        elif not file_path.is_file():
            unreadable_files.append(f"{file_path} (not a file)")
        else:
            try:
                file_path.read_text(encoding='utf-8')
            except Exception as e:
                unreadable_files.append(f"{file_path} ({e})")
    
    if missing_files or unreadable_files:
        if missing_files:
            print("ERROR: Missing files:", file=sys.stderr)
            for f in missing_files:
                print(f"  - {f}", file=sys.stderr)
        
        if unreadable_files:
            print("ERROR: Unreadable files:", file=sys.stderr)
            for f in unreadable_files:
                print(f"  - {f}", file=sys.stderr)
        
        sys.exit(1)


def create_baseline(input_dir: Path, output_file: Path) -> None:
    """
    Create baseline measurements for all .md files in input directory.
    
    Args:
        input_dir: Directory containing .md files to measure
        output_file: Path to write JSON baseline output
    """
    # Initialize tiktoken encoding (GPT-4)
    encoding = tiktoken.get_encoding("cl100k_base")
    
    # Discover files
    print(f"Discovering .md files in {input_dir}...")
    md_files = discover_markdown_files(input_dir)
    print(f"Found {len(md_files)} files")
    
    # Validate files
    print("Validating files...")
    validate_files(md_files)
    
    # Measure files
    print("Measuring tokens...")
    measurements = []
    total_bytes = 0
    total_tokens = 0
    
    for i, file_path in enumerate(md_files, 1):
        print(f"  [{i}/{len(md_files)}] {file_path.name}", end='\r')
        measurement = measure_file(file_path, encoding)
        measurements.append(measurement)
        total_bytes += measurement["byte_count"]
        total_tokens += measurement["token_count"]
    
    print()  # New line after progress indicator
    
    # Create baseline structure
    baseline = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "methodology": "tiktoken cl100k_base encoding (GPT-4 tokenizer)",
        "files": measurements,
        "summary": {
            "total_files": len(measurements),
            "total_bytes": total_bytes,
            "total_tokens": total_tokens
        }
    }
    
    # Write to output (atomic write via temp file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    temp_file = output_file.with_suffix('.tmp')
    
    try:
        temp_file.write_text(json.dumps(baseline, indent=2), encoding='utf-8')
        temp_file.rename(output_file)
        print(f"\nBaseline written to: {output_file}")
        print(f"Total files: {len(measurements)}")
        print(f"Total tokens: {total_tokens:,}")
    except Exception as e:
        print(f"ERROR: Failed to write output file: {e}", file=sys.stderr)
        if temp_file.exists():
            temp_file.unlink()
        sys.exit(1)


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Measure token counts for Markdown files using tiktoken",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Measure agents directory
  python measure-tokens.py --input-dir 5d-wave/agents --output-file baseline/agents.json
  
  # Measure commands directory
  python measure-tokens.py --input-dir 5d-wave/commands --output-file baseline/commands.json
  
  # Measure both and combine manually
  python measure-tokens.py --input-dir 5d-wave --output-file baseline/all-files.json
        """
    )
    
    parser.add_argument(
        '--input-dir',
        type=Path,
        required=True,
        help='Directory containing .md files to measure'
    )
    
    parser.add_argument(
        '--output-file',
        type=Path,
        required=True,
        help='Path to write JSON baseline output'
    )
    
    args = parser.parse_args()
    
    try:
        create_baseline(args.input_dir, args.output_file)
        return 0
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"FATAL ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
