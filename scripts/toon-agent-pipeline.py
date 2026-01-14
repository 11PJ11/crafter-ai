#!/usr/bin/env python3
"""
TOON Agent Conversion Pipeline - Automated verification and file generation.

This script automates the 4-step conversion process for each agent:
1. Parse MD and generate parsed YAML
2. Generate TOON file (manual step - script verifies)
3. Validate roundtrip equivalence
4. Measure tokens and generate metrics

Usage:
    python3 scripts/toon-agent-pipeline.py <agent-name> [--step N]
    python3 scripts/toon-agent-pipeline.py researcher-reviewer --step 4
    python3 scripts/toon-agent-pipeline.py solution-architect --all
"""

import os
import sys
import yaml
import json
import argparse
import re
from datetime import datetime

# Try to import tiktoken for token counting
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    print("Warning: tiktoken not available - token measurement will be skipped")


def get_agent_paths(agent_name):
    """Get all relevant file paths for an agent."""
    return {
        'md': f'nWave/agents/{agent_name}.md',
        'toon': f'nWave/agents/{agent_name}.toon',
        'parsed': f'docs/feature/toon-agent-conversion/parsed/{agent_name}-parsed.yaml',
        'baseline': f'docs/feature/toon-agent-conversion/measurements/{agent_name}-baseline.yaml',
        'comparison': f'docs/feature/toon-agent-conversion/measurements/{agent_name}-comparison.yaml',
        'test_parsing': f'tests/tools/toon/test_{agent_name.replace("-", "_")}_parsing.py',
        'test_toon': f'tests/toon/test_{agent_name.replace("-", "_")}_toon.py',
        'test_roundtrip': f'tests/tools/toon/test_{agent_name.replace("-", "_")}_roundtrip.py',
        'test_token': f'tests/tools/toon/test_{agent_name.replace("-", "_")}_token_measurement.py',
    }


def check_file_exists(filepath, description):
    """Check if file exists and report."""
    exists = os.path.exists(filepath)
    status = "✓" if exists else "✗"
    print(f"  {status} {description}: {filepath}")
    return exists


def parse_md_frontmatter(md_content):
    """Extract YAML frontmatter from MD file."""
    if md_content.startswith('---'):
        end_idx = md_content.find('---', 3)
        if end_idx > 0:
            frontmatter = md_content[3:end_idx].strip()
            try:
                return yaml.safe_load(frontmatter)
            except:
                pass

    # Try inline YAML extraction
    result = {}
    patterns = [
        (r'name:\s*(.+)', 'name'),
        (r'description:\s*(.+)', 'description'),
        (r'model:\s*(.+)', 'model'),
        (r'id:\s*(.+)', 'id'),
    ]
    for pattern, key in patterns:
        match = re.search(pattern, md_content[:1000])
        if match:
            result[key] = match.group(1).strip()
    return result


def extract_commands(md_content):
    """Extract commands from MD file."""
    commands = []
    # Look for command patterns like "- help:" or "- review:"
    pattern = r'-\s+(\w[\w-]*):\s*(.+?)(?=\n|$)'
    matches = re.findall(pattern, md_content)
    for name, desc in matches:
        if name.lower() not in ['type', 'format', 'example', 'inputs', 'outputs']:
            commands.append({'name': name, 'description': desc.strip()})
    return commands[:15]  # Limit to reasonable number


def count_tokens(content):
    """Count tokens using tiktoken."""
    if not TIKTOKEN_AVAILABLE:
        return 0
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(content))


def verify_step1_parse(agent_name, paths, verbose=True):
    """Verify Step 1: Parse MD and check parsed output."""
    print(f"\n=== Step 1: Parse {agent_name}.md ===")

    # Check MD exists
    if not os.path.exists(paths['md']):
        print(f"  ✗ ERROR: Source MD not found: {paths['md']}")
        return False

    with open(paths['md'], 'r', encoding='utf-8') as f:
        md_content = f.read()

    print(f"  ✓ MD file exists: {len(md_content)} chars, {len(md_content.splitlines())} lines")

    # Check parsed YAML
    if os.path.exists(paths['parsed']):
        print(f"  ✓ Parsed YAML exists: {paths['parsed']}")
        return True
    else:
        print(f"  ✗ Parsed YAML missing: {paths['parsed']}")
        print(f"    → Need to create parsed output")
        return False


def verify_step2_toon(agent_name, paths, verbose=True):
    """Verify Step 2: TOON file exists and has correct structure."""
    print(f"\n=== Step 2: Transform to TOON v3.0 ===")

    if not os.path.exists(paths['toon']):
        print(f"  ✗ TOON file missing: {paths['toon']}")
        return False

    with open(paths['toon'], 'r', encoding='utf-8') as f:
        toon_content = f.read()

    print(f"  ✓ TOON file exists: {len(toon_content)} chars, {len(toon_content.splitlines())} lines")

    # Verify structure
    checks = [
        ('## ID' in toon_content or '## id' in toon_content.lower(), 'Has ID section'),
        ('type: agent' in toon_content.lower() or 'type=agent' in toon_content.lower(), 'Type is agent'),
        ('v3' in toon_content.lower(), 'Has version v3'),
        ('commands' in toon_content.lower(), 'Has commands section'),
    ]

    all_pass = True
    for check, desc in checks:
        status = "✓" if check else "✗"
        print(f"  {status} {desc}")
        if not check:
            all_pass = False

    return all_pass


def verify_step3_roundtrip(agent_name, paths, verbose=True):
    """Verify Step 3: Roundtrip equivalence between MD and TOON."""
    print(f"\n=== Step 3: Roundtrip Validation ===")

    if not os.path.exists(paths['md']) or not os.path.exists(paths['toon']):
        print(f"  ✗ Missing source files for comparison")
        return False

    with open(paths['md'], 'r', encoding='utf-8') as f:
        md_content = f.read()
    with open(paths['toon'], 'r', encoding='utf-8') as f:
        toon_content = f.read()

    # Check key elements preserved
    md_lower = md_content.lower()
    toon_lower = toon_content.lower()

    checks = [
        (agent_name in toon_lower, f'Agent name "{agent_name}" preserved'),
        ('help' in md_lower and 'help' in toon_lower, 'Help command preserved'),
        ('exit' in md_lower and 'exit' in toon_lower, 'Exit command preserved'),
    ]

    # Check model preserved (if reviewer)
    if 'reviewer' in agent_name:
        checks.append(('haiku' in md_lower and 'haiku' in toon_lower, 'Haiku model preserved'))

    all_pass = True
    for check, desc in checks:
        status = "✓" if check else "✗"
        print(f"  {status} {desc}")
        if not check:
            all_pass = False

    return all_pass


def verify_step4_tokens(agent_name, paths, verbose=True):
    """Verify Step 4: Token measurement and compression ratio."""
    print(f"\n=== Step 4: Token Measurement ===")

    if not TIKTOKEN_AVAILABLE:
        print("  ⚠ tiktoken not available - skipping measurement")
        return None

    if not os.path.exists(paths['md']) or not os.path.exists(paths['toon']):
        print(f"  ✗ Missing source files for measurement")
        return None

    with open(paths['md'], 'r', encoding='utf-8') as f:
        md_content = f.read()
    with open(paths['toon'], 'r', encoding='utf-8') as f:
        toon_content = f.read()

    md_tokens = count_tokens(md_content)
    toon_tokens = count_tokens(toon_content)

    if toon_tokens == 0:
        print("  ✗ TOON has 0 tokens")
        return None

    reduction = md_tokens - toon_tokens
    reduction_pct = (reduction / md_tokens) * 100
    ratio = md_tokens / toon_tokens

    print(f"  Original (MD):  {md_tokens:,} tokens")
    print(f"  TOON:           {toon_tokens:,} tokens")
    print(f"  Reduction:      {reduction:,} ({reduction_pct:.1f}%)")
    print(f"  Compression:    {ratio:.2f}:1")

    # Check target
    if ratio >= 5.0:
        print(f"  ✓ Meets primary target (5:1)")
    elif ratio >= 4.0:
        print(f"  ⚠ Meets secondary target (4:1) - exception may be needed")
    else:
        print(f"  ✗ Below minimum target (4:1)")

    return {
        'md_tokens': md_tokens,
        'toon_tokens': toon_tokens,
        'reduction': reduction,
        'reduction_pct': reduction_pct,
        'ratio': ratio,
        'md_bytes': os.path.getsize(paths['md']),
        'toon_bytes': os.path.getsize(paths['toon']),
        'md_lines': len(md_content.splitlines()),
        'toon_lines': len(toon_content.splitlines()),
    }


def generate_baseline_yaml(agent_name, paths, metrics):
    """Generate baseline YAML file."""
    baseline = {
        'step_id': 'XX-04',  # Will be updated
        'agent_name': agent_name,
        'measurement_date': datetime.now().strftime('%Y-%m-%d'),
        'tokenizer': 'cl100k_base',
        'original': {
            'file': paths['md'],
            'tokens': metrics['md_tokens'],
            'bytes': metrics['md_bytes'],
            'lines': metrics['md_lines'],
        }
    }

    os.makedirs(os.path.dirname(paths['baseline']), exist_ok=True)
    with open(paths['baseline'], 'w', encoding='utf-8') as f:
        f.write(f"# Token Measurement Baseline for {agent_name}\n")
        f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d')}\n\n")
        yaml.dump(baseline, f, default_flow_style=False, sort_keys=False)

    print(f"  → Generated: {paths['baseline']}")


def generate_comparison_yaml(agent_name, paths, metrics):
    """Generate comparison YAML file."""
    ratio_str = f"{metrics['ratio']:.2f}:1"

    comparison = {
        'step_id': 'XX-04',
        'agent_name': agent_name,
        'measurement_date': datetime.now().strftime('%Y-%m-%d'),
        'tokenizer': 'cl100k_base',
        'original': {
            'file': paths['md'],
            'tokens': metrics['md_tokens'],
            'bytes': metrics['md_bytes'],
            'lines': metrics['md_lines'],
        },
        'toon': {
            'file': paths['toon'],
            'tokens': metrics['toon_tokens'],
            'bytes': metrics['toon_bytes'],
            'lines': metrics['toon_lines'],
        },
        'compression': {
            'ratio': ratio_str,
            'token_reduction': metrics['reduction'],
            'token_reduction_percent': round(metrics['reduction_pct'], 1),
        },
        'target_analysis': {
            'primary_target_5_1': metrics['ratio'] >= 5.0,
            'secondary_target_4_1': metrics['ratio'] >= 4.0,
            'exception_required': metrics['ratio'] < 4.0,
        }
    }

    os.makedirs(os.path.dirname(paths['comparison']), exist_ok=True)
    with open(paths['comparison'], 'w', encoding='utf-8') as f:
        f.write(f"# Token Measurement Comparison for {agent_name}\n")
        f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d')}\n\n")
        yaml.dump(comparison, f, default_flow_style=False, sort_keys=False)

    print(f"  → Generated: {paths['comparison']}")


def run_full_pipeline(agent_name, generate_files=False):
    """Run full verification pipeline for an agent."""
    print(f"\n{'='*60}")
    print(f"TOON Pipeline Verification: {agent_name}")
    print(f"{'='*60}")

    paths = get_agent_paths(agent_name)

    # Step 1: Parse
    step1_ok = verify_step1_parse(agent_name, paths)

    # Step 2: TOON
    step2_ok = verify_step2_toon(agent_name, paths)

    # Step 3: Roundtrip
    step3_ok = verify_step3_roundtrip(agent_name, paths)

    # Step 4: Tokens
    metrics = verify_step4_tokens(agent_name, paths)
    step4_ok = metrics is not None and metrics['ratio'] >= 4.0

    # Generate files if requested
    if generate_files and metrics:
        print(f"\n=== Generating Measurement Files ===")
        generate_baseline_yaml(agent_name, paths, metrics)
        generate_comparison_yaml(agent_name, paths, metrics)

    # Summary
    print(f"\n{'='*60}")
    print(f"Summary for {agent_name}:")
    print(f"{'='*60}")
    print(f"  Step 1 (Parse):     {'✓ PASS' if step1_ok else '✗ FAIL'}")
    print(f"  Step 2 (TOON):      {'✓ PASS' if step2_ok else '✗ FAIL'}")
    print(f"  Step 3 (Roundtrip): {'✓ PASS' if step3_ok else '✗ FAIL'}")
    print(f"  Step 4 (Tokens):    {'✓ PASS' if step4_ok else '✗ FAIL' if metrics else '⚠ SKIP'}")

    all_pass = step1_ok and step2_ok and step3_ok and step4_ok
    print(f"\n  Overall: {'✓ ALL PASS' if all_pass else '✗ ISSUES FOUND'}")

    return all_pass, metrics


def list_agents():
    """List all agents in nWave/agents/."""
    agents_dir = 'nWave/agents'
    if not os.path.exists(agents_dir):
        print(f"Agents directory not found: {agents_dir}")
        return []

    agents = []
    for f in os.listdir(agents_dir):
        if f.endswith('.md'):
            agents.append(f.replace('.md', ''))
    return sorted(agents)


def main():
    parser = argparse.ArgumentParser(description='TOON Agent Conversion Pipeline')
    parser.add_argument('agent', nargs='?', help='Agent name (e.g., researcher-reviewer)')
    parser.add_argument('--step', type=int, choices=[1, 2, 3, 4], help='Run specific step only')
    parser.add_argument('--generate', '-g', action='store_true', help='Generate measurement files')
    parser.add_argument('--list', '-l', action='store_true', help='List all agents')
    parser.add_argument('--all', '-a', action='store_true', help='Run all steps')

    args = parser.parse_args()

    if args.list:
        print("Available agents:")
        for agent in list_agents():
            paths = get_agent_paths(agent)
            has_toon = "✓" if os.path.exists(paths['toon']) else "✗"
            print(f"  {has_toon} {agent}")
        return

    if not args.agent:
        parser.print_help()
        return

    run_full_pipeline(args.agent, generate_files=args.generate)


if __name__ == '__main__':
    main()
