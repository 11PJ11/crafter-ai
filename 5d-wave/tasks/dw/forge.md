---
agent-activation:
  required: true
  agent-id: agent-builder
  agent-name: "Sage"
  agent-command: "*forge"
  auto-activate: true
---

# DW-FORGE: Agent Creation with Research-Validated Patterns

**Wave**: CROSS_WAVE
**Agent**: Sage (agent-builder)
**Command**: `*forge`

## Overview

Execute agent creation using AGENT_TEMPLATE.yaml with comprehensive safety frameworks, 4-layer testing, structured observability, and production-grade error recovery.

Creates production-ready agents using 7 research-validated design patterns, 14 evidence-based core principles, comprehensive safety (4 validation + 7 security layers), and complete production frameworks.

## Context Files Required

- 5d-wave/templates/AGENT_TEMPLATE.yaml - Single source of truth for agent structure

## Previous Artifacts (Wave Handoff)

- None (agent creation is typically initiated independently)

## Agent Invocation

@agent-builder

Execute \*forge to create {agent-name} agent.

**Context Files:**

- 5d-wave/templates/AGENT_TEMPLATE.yaml

**Configuration:**

- agent_type: specialist # specialist/orchestrator/team/tool
- design_pattern: react # react/reflection/router/planning/orchestration
- wave_domain: DISCUSS # or DESIGN/DISTILL/DEVELOP/DEMO/CROSS_WAVE
- safety_level: high

## Success Criteria

Refer to Sage's quality gates in 5d-wave/agents/agent-builder.md.

**Key Validations:**

- [ ] AGENT_TEMPLATE.yaml compliance verified
- [ ] Design pattern from template's 7 validated patterns
- [ ] Safety framework complete (4 validation + 7 security layers)
- [ ] Testing framework complete (4-layer testing)
- [ ] Observability operational (logging, metrics, alerting)
- [ ] Error recovery resilient (retry, circuit breakers, degraded mode)

## Next Wave

**Handoff To**: Agent deployment and validation
**Deliverables**: Complete agent specification file

# Expected outputs (reference only):

# - 5d-wave/agents/{agent-name}.md
