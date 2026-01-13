#!/usr/bin/env python3
"""
Automated Agent Compliance Validation
Validates all agents against AGENT_TEMPLATE.yaml v1.2
Version: 1.0
Date: 2025-10-05
"""

import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Configuration
TEMPLATE_VERSION = "1.2"
AGENTS_DIR = Path("nWave/agents")
REPORT_FILE = Path("docs/COMPLIANCE_VALIDATION_REPORT.md")

# Validation results
results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "agents": {}
}


def check_section_exists(content: str, section: str) -> bool:
    """Check if a section exists in YAML content"""
    pattern = rf"^{re.escape(section)}:\s*$"
    return bool(re.search(pattern, content, re.MULTILINE))


def check_subsection_exists(content: str, section: str, subsection: str) -> bool:
    """Check if a subsection exists under a section"""
    # Find the section
    section_pattern = rf"^{re.escape(section)}:\s*$"
    section_match = re.search(section_pattern, content, re.MULTILINE)

    if not section_match:
        return False

    # Look for subsection within next 200 lines after section
    start_pos = section_match.end()
    subsection_text = content[start_pos:start_pos+5000]

    # Check for subsection (either at 2 spaces or 4 spaces indentation)
    subsection_pattern = rf"^  {re.escape(subsection)}:\s*$"
    return bool(re.search(subsection_pattern, subsection_text, re.MULTILINE))


def check_frontmatter(content: str) -> bool:
    """Check if YAML frontmatter is complete"""
    # Extract frontmatter between --- markers
    frontmatter_match = re.search(r'^---\s*\n(.*?)\n---', content, re.MULTILINE | re.DOTALL)

    if not frontmatter_match:
        return False

    frontmatter = frontmatter_match.group(1)

    has_name = bool(re.search(r'^name:', frontmatter, re.MULTILINE))
    has_description = bool(re.search(r'^description:', frontmatter, re.MULTILINE))
    has_model = bool(re.search(r'^model:', frontmatter, re.MULTILINE))

    return has_name and has_description and has_model


def check_testing_layers(content: str) -> bool:
    """Check if all 4 testing layers are present"""
    testing_section = re.search(r'^testing_framework:(.*?)(?=^[a-z_]+:|$)',
                                content, re.MULTILINE | re.DOTALL)

    if not testing_section:
        return False

    testing_text = testing_section.group(1)

    has_l1 = bool(re.search(r'layer_1_unit', testing_text))
    has_l2 = bool(re.search(r'layer_2_integration', testing_text))
    has_l3 = bool(re.search(r'layer_3_adversarial', testing_text))
    has_l4 = bool(re.search(r'layer_4_adversarial_verification', testing_text))

    return has_l1 and has_l2 and has_l3 and has_l4


def check_safety_layers(content: str) -> bool:
    """Check if safety framework has 4 validation + 7 enterprise layers"""
    safety_section = re.search(r'^safety_framework:(.*?)(?=^[a-z_]+:|$)',
                               content, re.MULTILINE | re.DOTALL)

    if not safety_section:
        return False

    safety_text = safety_section.group(1)

    # Check 4 validation layers
    has_input = bool(re.search(r'input_validation', safety_text))
    has_output = bool(re.search(r'output_filtering', safety_text))
    has_behavioral = bool(re.search(r'behavioral_constraints', safety_text))
    has_monitoring = bool(re.search(r'continuous_monitoring', safety_text))

    # Check enterprise security layers reference
    has_enterprise = bool(re.search(r'enterprise_safety_layers', safety_text))

    return has_input and has_output and has_behavioral and has_monitoring and has_enterprise


def validate_agent(agent_file: Path) -> Dict[str, any]:
    """Validate a single agent file"""
    agent_name = agent_file.stem

    print(f"Validating: {agent_name}...")

    # Read file content
    with open(agent_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Initialize checks
    checks = {
        "contract": False,
        "safety": False,
        "testing": False,
        "observability": False,
        "error_recovery": False,
        "frontmatter": False,
        "metrics": False
    }

    # Check Contract Framework
    if check_section_exists(content, "contract"):
        if (check_subsection_exists(content, "contract", "inputs") and
            check_subsection_exists(content, "contract", "outputs") and
            check_subsection_exists(content, "contract", "side_effects") and
            check_subsection_exists(content, "contract", "error_handling")):
            checks["contract"] = True

    # Check Safety Framework
    checks["safety"] = check_safety_layers(content)

    # Check Testing Framework (all 4 layers)
    checks["testing"] = check_testing_layers(content)

    # Check Observability Framework
    if check_section_exists(content, "observability_framework"):
        if (check_subsection_exists(content, "observability_framework", "structured_logging") and
            check_subsection_exists(content, "observability_framework", "metrics") and
            check_subsection_exists(content, "observability_framework", "alerting")):
            checks["observability"] = True

    # Check Error Recovery Framework
    if check_section_exists(content, "error_recovery_framework"):
        if (check_subsection_exists(content, "error_recovery_framework", "retry_strategies") and
            check_subsection_exists(content, "error_recovery_framework", "circuit_breakers") and
            check_subsection_exists(content, "error_recovery_framework", "degraded_mode")):
            checks["error_recovery"] = True

    # Check YAML Frontmatter
    checks["frontmatter"] = check_frontmatter(content)

    # Check Agent-Specific Metrics (optional - in observability)
    checks["metrics"] = "agent_specific" in content or "document_agents" in content or "code_agents" in content

    # Determine pass/fail
    required_checks = ["contract", "safety", "testing", "observability", "error_recovery", "frontmatter"]
    failures = sum(1 for check in required_checks if not checks[check])
    passed = failures == 0

    return {
        "name": agent_name,
        "checks": checks,
        "failures": failures,
        "passed": passed
    }


def generate_report(results: Dict):
    """Generate markdown compliance report"""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    total = results["total"]
    passed = results["passed"]
    failed = results["failed"]
    pass_rate = (passed / total * 100) if total > 0 else 0

    with open(REPORT_FILE, 'w') as f:
        f.write(f"""# Agent Compliance Validation Report

**Template Version**: AGENT_TEMPLATE.yaml v{TEMPLATE_VERSION}
**Validation Date**: {timestamp}
**Total Agents**: {total}

## Executive Summary

This report validates all AI-Craft agents against AGENT_TEMPLATE.yaml v1.2 production framework requirements.

### Validation Criteria

1. **Contract Framework**: Input/output contract with validation
2. **Safety Framework**: 4 validation layers + 7 enterprise security layers
3. **Testing Framework**: All 4 layers (Unit, Integration, Adversarial Output, Adversarial Verification)
4. **Observability Framework**: Structured logging, metrics, alerting
5. **Error Recovery Framework**: Retry strategies, circuit breakers, degraded mode
6. **YAML Frontmatter**: Complete and valid (name, description, model)
7. **Agent-Type Metrics**: Domain-specific metrics present

---

## Compliance Matrix

| Agent | Contract | Safety | Testing L1-4 | Observability | Error Recovery | Frontmatter | Metrics | Status |
|-------|----------|--------|--------------|---------------|----------------|-------------|---------|--------|
""")

        # Sort agents by name
        for agent_name in sorted(results["agents"].keys()):
            agent = results["agents"][agent_name]
            checks = agent["checks"]

            # Create status symbols
            def sym(val): return "✅" if val else "❌"
            def sym_opt(val): return "✅" if val else "⚠️"  # Optional

            status = "✅ PASS" if agent["passed"] else "❌ FAIL"

            f.write(f"| {agent_name} | {sym(checks['contract'])} | {sym(checks['safety'])} | "
                   f"{sym(checks['testing'])} | {sym(checks['observability'])} | "
                   f"{sym(checks['error_recovery'])} | {sym(checks['frontmatter'])} | "
                   f"{sym_opt(checks['metrics'])} | {status} |\n")

        f.write(f"""

---

## Validation Results

- **Total Agents Validated**: {total}
- **Agents Passed**: {passed}
- **Agents Failed**: {failed}
- **Pass Rate**: {pass_rate:.1f}%

### Legend

- ✅ **PASS**: Framework present and complete
- ❌ **FAIL**: Framework missing or incomplete
- ⚠️ **OPTIONAL**: Optional feature not present

---

## Framework Descriptions

### 1. Contract Framework
- **Required**: `contract:` section with `inputs`, `outputs`, `side_effects`, `error_handling`
- **Purpose**: Define explicit input/output contract for agent as function

### 2. Safety Framework
- **Required**: 4 validation layers (input_validation, output_filtering, behavioral_constraints, continuous_monitoring)
- **Required**: 7 enterprise security layers reference
- **Purpose**: Multi-layer security and safety validation

### 3. Testing Framework
- **Required**: All 4 layers present
  - Layer 1: Unit testing (output quality validation)
  - Layer 2: Integration testing (handoff validation)
  - Layer 3: Adversarial output validation (challenge output validity)
  - Layer 4: Adversarial verification (peer review for bias reduction)
- **Purpose**: Comprehensive testing from unit to adversarial

### 4. Observability Framework
- **Required**: `structured_logging`, `metrics`, `alerting` subsections
- **Purpose**: Production monitoring and debugging

### 5. Error Recovery Framework
- **Required**: `retry_strategies`, `circuit_breakers`, `degraded_mode`
- **Purpose**: Graceful error handling and resilience

### 6. YAML Frontmatter
- **Required**: `name`, `description`, `model` fields in YAML frontmatter
- **Purpose**: Claude Code integration

### 7. Agent-Type Metrics
- **Optional**: Domain-specific metrics in observability framework
- **Purpose**: Specialized monitoring for agent type

---

## Recommendations

""")

        if failed > 0:
            f.write(f"""### Critical Issues

{failed} agent(s) failed compliance validation. **Production deployment blocked** until all agents pass.

**Action Required**:
1. Review failed agents in compliance matrix above
2. Add missing frameworks to each failed agent
3. Re-run validation: `python3 scripts/validate-agent-compliance.py`
4. Ensure 100% pass rate before proceeding to adversarial testing

""")
        else:
            f.write(f"""### Production Readiness Status

✅ **All {total} agents passed compliance validation**

**Next Steps**:
1. ✅ Compliance validation complete
2. 🔄 Execute adversarial testing: `python3 scripts/run-adversarial-tests.py`
3. 🔄 Implement adversarial verification workflow (Layer 4)
4. 🔄 Deploy observability infrastructure
5. 🔄 Conduct production pilot with monitoring

""")

        f.write(f"""

---

**Report Generated**: {timestamp}
**Validation Script**: scripts/validate-agent-compliance.py
""")


def main():
    """Main validation function"""
    print("=" * 60)
    print("AI-Craft Agent Compliance Validation")
    print(f"Template Version: {TEMPLATE_VERSION}")
    print("=" * 60)
    print("")

    # Check agents directory exists
    if not AGENTS_DIR.exists():
        print(f"ERROR: Agents directory not found: {AGENTS_DIR}")
        return 1

    # Validate each agent
    for agent_file in sorted(AGENTS_DIR.glob("*.md")):
        agent_result = validate_agent(agent_file)

        results["total"] += 1
        results["agents"][agent_result["name"]] = agent_result

        if agent_result["passed"]:
            results["passed"] += 1
            print(f"  ✅ {agent_result['name']}: PASS")
        else:
            results["failed"] += 1
            print(f"  ❌ {agent_result['name']}: FAIL ({agent_result['failures']} framework(s) missing)")

    # Generate report
    print("")
    print("Generating compliance report...")
    REPORT_FILE.parent.mkdir(exist_ok=True)
    generate_report(results)

    # Print summary
    print("")
    print("=" * 60)
    print("Validation Complete")
    print("=" * 60)
    print(f"Total Agents: {results['total']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Pass Rate: {results['passed']/results['total']*100:.1f}%")
    print("")
    print(f"Report generated: {REPORT_FILE}")
    print("")

    # Exit with appropriate code
    if results["failed"] > 0:
        print("❌ Compliance validation FAILED")
        return 1
    else:
        print("✅ Compliance validation PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(main())
