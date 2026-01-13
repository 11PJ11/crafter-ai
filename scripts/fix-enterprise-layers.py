#!/usr/bin/env python3
"""
Add enterprise_safety_layers to existing safety_framework sections
"""

import re
from pathlib import Path

AGENTS_DIR = Path("/mnt/c/Repositories/Projects/ai-craft/nWave/agents")

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
    """Add enterprise layers to existing safety framework"""
    content = agent_file.read_text(encoding='utf-8')

    # Check if enterprise_safety_layers already exists
    if 'enterprise_safety_layers:' in content:
        print(f"  ✅ {agent_file.stem}: Already has enterprise layers")
        return False

    # Find the safety_framework section and add enterprise layers before the next section
    # Look for the pattern: safety_framework: ... continuous_monitoring: ... <next section>
    pattern = r'(safety_framework:.*?continuous_monitoring:.*?\n)(^[a-z_]+:)'

    def replacement(match):
        return match.group(1) + ENTERPRISE_LAYERS + '\n' + match.group(2)

    new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)

    if new_content != content:
        agent_file.write_text(new_content, encoding='utf-8')
        print(f"  ✅ {agent_file.stem}: Added enterprise_safety_layers")
        return True
    else:
        print(f"  ❌ {agent_file.stem}: Could not find safety_framework section")
        return False

def main():
    print("Adding enterprise_safety_layers to agents...")
    print("=" * 60)

    updated = 0
    for agent_file in sorted(AGENTS_DIR.glob("*.md")):
        if fix_agent(agent_file):
            updated += 1

    print("=" * 60)
    print(f"✅ Updated {updated} agents")
    print("\nNext: Remove duplicate framework sections at end of files")

if __name__ == "__main__":
    main()
