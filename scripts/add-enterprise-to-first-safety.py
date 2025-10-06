#!/usr/bin/env python3
"""
Add enterprise_safety_layers to the FIRST safety_framework section in each agent
"""

import re
from pathlib import Path

AGENTS_DIR = Path("/mnt/c/Repositories/Projects/ai-craft/5d-wave/agents")

ENTERPRISE_LAYERS = """
  enterprise_safety_layers:
    layer_1_identity: "Authentication, authorization, RBAC"
    layer_2_guardrails: "Input validation, output filtering, behavioral constraints"
    layer_3_evaluations: "Automated safety evaluations, benchmarks, quality metrics"
    layer_4_adversarial: "Red team exercises, attack simulation, vulnerability discovery"
    layer_5_data_protection: "Encryption, sanitization, privacy preservation"
    layer_6_monitoring: "Real-time tracking, anomaly detection, alert systems"
    layer_7_governance: "Policy enforcement, compliance validation, audit trails"
"""

def fix_agent(agent_file: Path):
    """Add enterprise layers to the FIRST safety_framework only"""
    content = agent_file.read_text(encoding='utf-8')

    # Find the FIRST safety_framework section
    # Pattern: safety_framework: ... agent_security_validation: ... pass_threshold ...
    # Insert enterprise_safety_layers after pass_threshold line

    pattern = r'(safety_framework:.*?pass_threshold: "100% of attacks blocked \(zero tolerance\)"\s*\n)'

    # Check if this already has enterprise layers right after it
    check_pattern = pattern + r'(\s*enterprise_safety_layers:)'
    if re.search(check_pattern, content, re.DOTALL):
        print(f"  ✅ {agent_file.stem}: Already has enterprise layers in first safety section")
        return False

    def replacement(match):
        return match.group(1) + '\n' + ENTERPRISE_LAYERS + '\n'

    new_content = re.sub(pattern, replacement, content, count=1, flags=re.DOTALL)

    if new_content != content:
        agent_file.write_text(new_content, encoding='utf-8')
        print(f"  ✅ {agent_file.stem}: Added enterprise_safety_layers to first safety section")
        return True
    else:
        print(f"  ⚠️  {agent_file.stem}: Could not find pattern to insert")
        return False

def main():
    print("Adding enterprise_safety_layers to FIRST safety_framework section...")
    print("=" * 60)

    updated = 0
    for agent_file in sorted(AGENTS_DIR.glob("*.md")):
        if fix_agent(agent_file):
            updated += 1

    print("=" * 60)
    print(f"✅ Updated {updated} agents")

if __name__ == "__main__":
    main()
