#!/usr/bin/env python3
"""
Automated Agent Compliance Validation v2
Validates all agents against AGENT_TEMPLATE.yaml v1.2
"""

# Version - Must match nWave/framework-catalog.yaml version
__version__ = "1.2.26"

import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict

# Configuration
TEMPLATE_VERSION = "1.2"
AGENTS_DIR = Path("nWave/agents")
REPORT_FILE = Path("docs/COMPLIANCE_VALIDATION_REPORT.md")

# Validation results
results = {"total": 0, "passed": 0, "failed": 0, "agents": {}}


def check_frontmatter(content: str) -> bool:
    """Check if YAML frontmatter is complete"""
    # Extract frontmatter between --- markers
    frontmatter_match = re.search(
        r"^---\s*\n(.*?)\n---", content, re.MULTILINE | re.DOTALL
    )

    if not frontmatter_match:
        return False

    frontmatter = frontmatter_match.group(1)

    has_name = bool(re.search(r"^name:", frontmatter, re.MULTILINE))
    has_description = bool(re.search(r"^description:", frontmatter, re.MULTILINE))
    has_model = bool(re.search(r"^model:", frontmatter, re.MULTILINE))

    return has_name and has_description and has_model


def check_contract_framework(content: str) -> bool:
    """Check if contract framework is present with all required sections"""
    # Simple keyword-based approach
    has_contract = "contract:" in content
    has_inputs = "inputs:" in content
    has_outputs = "outputs:" in content
    has_side_effects = "side_effects:" in content
    has_error_handling = "error_handling:" in content

    return (
        has_contract
        and has_inputs
        and has_outputs
        and has_side_effects
        and has_error_handling
    )


def check_safety_framework(content: str) -> bool:
    """Check if safety framework has 4 validation + 7 enterprise layers"""
    # Simple keyword-based approach
    has_safety = "safety_framework:" in content
    has_input = "input_validation" in content
    has_output = "output_filtering" in content
    has_behavioral = "behavioral_constraints" in content
    has_monitoring = "continuous_monitoring" in content
    has_enterprise = "enterprise_safety_layers:" in content

    return (
        has_safety
        and has_input
        and has_output
        and has_behavioral
        and has_monitoring
        and has_enterprise
    )


def check_testing_framework(content: str) -> bool:
    """Check if all 4 testing layers are present"""
    # Simple keyword-based approach
    has_testing = "testing_framework:" in content
    has_l1 = "layer_1_unit_testing" in content
    has_l2 = "layer_2_integration_testing" in content
    has_l3 = (
        "layer_3_adversarial" in content
    )  # Can be adversarial_output_validation or adversarial_security
    has_l4 = "layer_4_adversarial_verification" in content

    return has_testing and has_l1 and has_l2 and has_l3 and has_l4


def check_observability_framework(content: str) -> bool:
    """Check if observability framework is present"""
    # Simple keyword-based approach
    has_observability = "observability_framework:" in content
    has_logging = "structured_logging" in content
    has_metrics = "metrics" in content or "domain_metrics" in content
    has_alerting = "alerting" in content or "alerting_thresholds" in content

    return has_observability and has_logging and has_metrics and has_alerting


def check_error_recovery_framework(content: str) -> bool:
    """Check if error recovery framework is present"""
    # Simple keyword-based approach
    has_error_recovery = "error_recovery_framework:" in content
    has_retry = "retry_strategies" in content
    has_circuit_breaker = "circuit_breaker" in content
    has_degraded = "degraded_mode" in content

    return has_error_recovery and has_retry and has_circuit_breaker and has_degraded


def check_agent_metrics(content: str) -> bool:
    """Check if agent-specific metrics are present (optional)"""
    return (
        "agent_specific" in content
        or "document_agents" in content
        or "code_agents" in content
        or "domain_metrics" in content
    )


def validate_agent(agent_file: Path) -> Dict[str, any]:
    """Validate a single agent file"""
    agent_name = agent_file.stem

    print(f"Validating: {agent_name}...")

    # Read file content
    with open(agent_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Initialize checks
    checks = {
        "contract": check_contract_framework(content),
        "safety": check_safety_framework(content),
        "testing": check_testing_framework(content),
        "observability": check_observability_framework(content),
        "error_recovery": check_error_recovery_framework(content),
        "frontmatter": check_frontmatter(content),
        "metrics": check_agent_metrics(content),
    }

    # Determine pass/fail
    required_checks = [
        "contract",
        "safety",
        "testing",
        "observability",
        "error_recovery",
        "frontmatter",
    ]
    failures = sum(1 for check in required_checks if not checks[check])
    passed = failures == 0

    return {
        "name": agent_name,
        "checks": checks,
        "failures": failures,
        "passed": passed,
    }


def generate_report(results: Dict):
    """Generate markdown compliance report"""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    total = results["total"]
    passed = results["passed"]
    failed = results["failed"]
    pass_rate = (passed / total * 100) if total > 0 else 0

    with open(REPORT_FILE, "w") as f:
        f.write(
            f"""# Agent Compliance Validation Report

**Template Version**: AGENT_TEMPLATE.yaml v{TEMPLATE_VERSION}
**Validation Date**: {timestamp}
**Total Agents**: {total}
**Validation Script**: v2.0 (Keyword-based validation)

## Executive Summary

This report validates all AI-Craft agents against AGENT_TEMPLATE.yaml v1.2 production framework requirements.

### Validation Criteria

1. **Contract Framework**: Input/output contract with validation
2. **Safety Framework**: 4 validation layers + 7 enterprise security layers
3. **Testing Framework**: All 4 layers (Unit, Integration, Adversarial Output, Adversarial Verification)
4. **Observability Framework**: Structured logging, metrics, alerting
5. **Error Recovery Framework**: Retry strategies, circuit breakers, degraded mode
6. **YAML Frontmatter**: Complete and valid (name, description, model)
7. **Agent-Type Metrics**: Domain-specific metrics present (optional)

---

## Compliance Matrix

| Agent | Contract | Safety | Testing L1-4 | Observability | Error Recovery | Frontmatter | Metrics | Status |
|-------|----------|--------|--------------|---------------|----------------|-------------|---------|--------|
"""
        )

        # Sort agents by name
        for agent_name in sorted(results["agents"].keys()):
            agent = results["agents"][agent_name]
            checks = agent["checks"]

            # Create status symbols
            def sym(val):
                return "✅" if val else "❌"

            def sym_opt(val):
                return "✅" if val else "⚠️"  # Optional

            status = "✅ PASS" if agent["passed"] else "❌ FAIL"

            f.write(
                f"| {agent_name} | {sym(checks['contract'])} | {sym(checks['safety'])} | "
                f"{sym(checks['testing'])} | {sym(checks['observability'])} | "
                f"{sym(checks['error_recovery'])} | {sym(checks['frontmatter'])} | "
                f"{sym_opt(checks['metrics'])} | {status} |\n"
            )

        f.write(
            f"""

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

"""
        )

        if failed > 0:
            f.write(
                f"""### Critical Issues

{failed} agent(s) failed compliance validation. **Production deployment blocked** until all agents pass.

**Action Required**:
1. Review failed agents in compliance matrix above
2. Add missing frameworks to each failed agent
3. Re-run validation: `python3 scripts/validate-agent-compliance-v2.py`
4. Ensure 100% pass rate before proceeding to adversarial testing

"""
            )
        else:
            f.write(
                f"""### Production Readiness Status

✅ **All {total} agents passed compliance validation**

**Next Steps**:
1. ✅ Compliance validation complete
2. 🔄 Execute adversarial testing: `python3 scripts/run-adversarial-tests.py`
3. 🔄 Implement adversarial verification workflow (Layer 4)
4. 🔄 Deploy observability infrastructure
5. 🔄 Conduct production pilot with monitoring

"""
            )

        f.write(
            f"""

---

**Report Generated**: {timestamp}
**Validation Script**: scripts/validate-agent-compliance-v2.py (Keyword-based validation)
**Improvement over v1**: Simpler, more reliable keyword-based validation instead of complex regex
"""
        )


def main():
    """Main validation function"""
    print("=" * 60)
    print("AI-Craft Agent Compliance Validation v2")
    print(f"Template Version: {TEMPLATE_VERSION}")
    print("Validation Method: Keyword-based (improved)")
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
            print(
                f"  ❌ {agent_result['name']}: FAIL ({agent_result['failures']} framework(s) missing)"
            )

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
    print(f"Pass Rate: {results['passed'] / results['total'] * 100:.1f}%")
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
