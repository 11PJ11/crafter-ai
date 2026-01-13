#!/bin/bash
# Automated Agent Compliance Validation
# Validates all 12 agents against AGENT_TEMPLATE.yaml v1.2
# Version: 1.0
# Date: 2025-10-05

set -euo pipefail

# Configuration
TEMPLATE_VERSION="1.2"
AGENTS_DIR="nWave/agents"
REPORT_FILE="docs/COMPLIANCE_VALIDATION_REPORT.md"
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
TOTAL_AGENTS=0
PASSED_AGENTS=0
FAILED_AGENTS=0

# Initialize report
init_report() {
    cat > "$REPORT_FILE" <<EOF
# Agent Compliance Validation Report

**Template Version**: AGENT_TEMPLATE.yaml v${TEMPLATE_VERSION}
**Validation Date**: ${TIMESTAMP}
**Total Agents**: TBD

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
EOF
}

# Check if file contains a section
check_section() {
    local file=$1
    local section=$2

    if grep -q "^${section}:" "$file"; then
        return 0
    else
        return 1
    fi
}

# Check if file contains subsection
check_subsection() {
    local file=$1
    local section=$2
    local subsection=$3

    # Check if section exists and has the subsection
    if grep -A 50 "^${section}:" "$file" | grep -q "^  ${subsection}:"; then
        return 0
    else
        return 1
    fi
}

# Check YAML frontmatter
check_frontmatter() {
    local file=$1
    local has_name=0
    local has_description=0
    local has_model=0

    # Extract frontmatter (between --- lines)
    if grep -q "^---$" "$file"; then
        if grep -A 10 "^---$" "$file" | grep -q "^name:"; then
            has_name=1
        fi
        if grep -A 10 "^---$" "$file" | grep -q "^description:"; then
            has_description=1
        fi
        if grep -A 10 "^---$" "$file" | grep -q "^model:"; then
            has_model=1
        fi

        if [[ $has_name -eq 1 && $has_description -eq 1 && $has_model -eq 1 ]]; then
            return 0
        fi
    fi
    return 1
}

# Check testing framework layers
check_testing_layers() {
    local file=$1
    local has_l1=0
    local has_l2=0
    local has_l3=0
    local has_l4=0

    if grep -A 20 "testing_framework:" "$file" | grep -q "layer_1_unit"; then
        has_l1=1
    fi
    if grep -A 40 "testing_framework:" "$file" | grep -q "layer_2_integration"; then
        has_l2=1
    fi
    if grep -A 60 "testing_framework:" "$file" | grep -q "layer_3_adversarial_output"; then
        has_l3=1
    fi
    if grep -A 80 "testing_framework:" "$file" | grep -q "layer_4_adversarial_verification"; then
        has_l4=1
    fi

    if [[ $has_l1 -eq 1 && $has_l2 -eq 1 && $has_l3 -eq 1 && $has_l4 -eq 1 ]]; then
        return 0
    fi
    return 1
}

# Check safety framework layers
check_safety_layers() {
    local file=$1
    local validation_layers=0
    local security_layers=0

    # Check 4 validation layers
    if grep -A 100 "safety_framework:" "$file" | grep -q "input_validation:"; then
        ((validation_layers++))
    fi
    if grep -A 100 "safety_framework:" "$file" | grep -q "output_filtering:"; then
        ((validation_layers++))
    fi
    if grep -A 100 "safety_framework:" "$file" | grep -q "behavioral_constraints:"; then
        ((validation_layers++))
    fi
    if grep -A 100 "safety_framework:" "$file" | grep -q "continuous_monitoring:"; then
        ((validation_layers++))
    fi

    # Check 7 enterprise security layers
    if grep -A 150 "safety_framework:" "$file" | grep -q "enterprise_safety_layers:"; then
        security_layers=1
    fi

    if [[ $validation_layers -eq 4 && $security_layers -eq 1 ]]; then
        return 0
    fi
    return 1
}

# Validate a single agent
validate_agent() {
    local agent_file=$1
    local agent_name=$(basename "$agent_file" .md)

    ((TOTAL_AGENTS++))

    local contract="❌"
    local safety="❌"
    local testing="❌"
    local observability="❌"
    local error_recovery="❌"
    local frontmatter="❌"
    local metrics="❌"
    local status="❌ FAIL"
    local failures=0

    echo -e "${YELLOW}Validating: ${agent_name}${NC}"

    # Check Contract Framework
    if check_section "$agent_file" "contract"; then
        if check_subsection "$agent_file" "contract" "inputs" && \
           check_subsection "$agent_file" "contract" "outputs" && \
           check_subsection "$agent_file" "contract" "side_effects" && \
           check_subsection "$agent_file" "contract" "error_handling"; then
            contract="✅"
        else
            ((failures++))
        fi
    else
        ((failures++))
    fi

    # Check Safety Framework
    if check_safety_layers "$agent_file"; then
        safety="✅"
    else
        ((failures++))
    fi

    # Check Testing Framework (all 4 layers)
    if check_testing_layers "$agent_file"; then
        testing="✅"
    else
        ((failures++))
    fi

    # Check Observability Framework
    if check_section "$agent_file" "observability_framework"; then
        if check_subsection "$agent_file" "observability_framework" "structured_logging" && \
           check_subsection "$agent_file" "observability_framework" "metrics" && \
           check_subsection "$agent_file" "observability_framework" "alerting"; then
            observability="✅"
        else
            ((failures++))
        fi
    else
        ((failures++))
    fi

    # Check Error Recovery Framework
    if check_section "$agent_file" "error_recovery_framework"; then
        if check_subsection "$agent_file" "error_recovery_framework" "retry_strategies" && \
           check_subsection "$agent_file" "error_recovery_framework" "circuit_breakers" && \
           check_subsection "$agent_file" "error_recovery_framework" "degraded_mode"; then
            error_recovery="✅"
        else
            ((failures++))
        fi
    else
        ((failures++))
    fi

    # Check YAML Frontmatter
    if check_frontmatter "$agent_file"; then
        frontmatter="✅"
    else
        ((failures++))
    fi

    # Check Agent-Type Metrics (in observability_framework)
    if grep -A 200 "observability_framework:" "$agent_file" | grep -q "agent_specific"; then
        metrics="✅"
    else
        # Some agents may not have agent-specific metrics (optional)
        metrics="⚠️"
    fi

    # Determine overall status
    if [[ $failures -eq 0 ]]; then
        status="✅ PASS"
        ((PASSED_AGENTS++))
        echo -e "${GREEN}✅ ${agent_name}: PASS${NC}"
    else
        status="❌ FAIL"
        ((FAILED_AGENTS++))
        echo -e "${RED}❌ ${agent_name}: FAIL (${failures} framework(s) missing)${NC}"
    fi

    # Append to report
    echo "| ${agent_name} | ${contract} | ${safety} | ${testing} | ${observability} | ${error_recovery} | ${frontmatter} | ${metrics} | ${status} |" >> "$REPORT_FILE"
}

# Main validation
main() {
    echo "================================================"
    echo "AI-Craft Agent Compliance Validation"
    echo "Template Version: ${TEMPLATE_VERSION}"
    echo "================================================"
    echo ""

    # Initialize report
    init_report

    # Find all agent files
    if [[ ! -d "$AGENTS_DIR" ]]; then
        echo -e "${RED}ERROR: Agents directory not found: ${AGENTS_DIR}${NC}"
        exit 1
    fi

    # Validate each agent
    for agent_file in "$AGENTS_DIR"/*.md; do
        if [[ -f "$agent_file" ]]; then
            validate_agent "$agent_file"
        fi
    done

    # Update total agents in report
    sed -i "s/\*\*Total Agents\*\*: TBD/\*\*Total Agents\*\*: ${TOTAL_AGENTS}/" "$REPORT_FILE"

    # Add summary to report
    cat >> "$REPORT_FILE" <<EOF

---

## Validation Results

- **Total Agents Validated**: ${TOTAL_AGENTS}
- **Agents Passed**: ${PASSED_AGENTS}
- **Agents Failed**: ${FAILED_AGENTS}
- **Pass Rate**: $(awk "BEGIN {printf \"%.1f\", (${PASSED_AGENTS}/${TOTAL_AGENTS})*100}")%

### Legend

- ✅ **PASS**: Framework present and complete
- ❌ **FAIL**: Framework missing or incomplete
- ⚠️ **OPTIONAL**: Optional feature not present

---

## Framework Descriptions

### 1. Contract Framework
- **Required**: \`contract:\` section with \`inputs\`, \`outputs\`, \`side_effects\`, \`error_handling\`
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
- **Required**: \`structured_logging\`, \`metrics\`, \`alerting\` subsections
- **Purpose**: Production monitoring and debugging

### 5. Error Recovery Framework
- **Required**: \`retry_strategies\`, \`circuit_breakers\`, \`degraded_mode\`
- **Purpose**: Graceful error handling and resilience

### 6. YAML Frontmatter
- **Required**: \`name\`, \`description\`, \`model\` fields in YAML frontmatter
- **Purpose**: Claude Code integration

### 7. Agent-Type Metrics
- **Optional**: Domain-specific metrics in observability framework
- **Purpose**: Specialized monitoring for agent type

---

## Recommendations

EOF

    if [[ $FAILED_AGENTS -gt 0 ]]; then
        cat >> "$REPORT_FILE" <<EOF
### Critical Issues

${FAILED_AGENTS} agent(s) failed compliance validation. **Production deployment blocked** until all agents pass.

**Action Required**:
1. Review failed agents in compliance matrix above
2. Add missing frameworks to each failed agent
3. Re-run validation: \`bash scripts/validate-agent-compliance.sh\`
4. Ensure 100% pass rate before proceeding to adversarial testing

EOF
    else
        cat >> "$REPORT_FILE" <<EOF
### Production Readiness Status

✅ **All ${TOTAL_AGENTS} agents passed compliance validation**

**Next Steps**:
1. ✅ Compliance validation complete
2. 🔄 Execute adversarial testing: \`python3 scripts/run-adversarial-tests.py\`
3. 🔄 Implement adversarial verification workflow (Layer 4)
4. 🔄 Deploy observability infrastructure
5. 🔄 Conduct production pilot with monitoring

EOF
    fi

    cat >> "$REPORT_FILE" <<EOF

---

**Report Generated**: ${TIMESTAMP}
**Validation Script**: scripts/validate-agent-compliance.sh
EOF

    # Print summary
    echo ""
    echo "================================================"
    echo "Validation Complete"
    echo "================================================"
    echo -e "Total Agents: ${TOTAL_AGENTS}"
    echo -e "${GREEN}Passed: ${PASSED_AGENTS}${NC}"
    echo -e "${RED}Failed: ${FAILED_AGENTS}${NC}"
    echo ""
    echo "Report generated: ${REPORT_FILE}"
    echo ""

    # Exit with appropriate code
    if [[ $FAILED_AGENTS -gt 0 ]]; then
        echo -e "${RED}❌ Compliance validation FAILED${NC}"
        exit 1
    else
        echo -e "${GREEN}✅ Compliance validation PASSED${NC}"
        exit 0
    fi
}

# Run main
main
