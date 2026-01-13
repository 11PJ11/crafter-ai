---
agent-activation:
  required: true
  agent-id: visual-architect
  agent-name: "Archer"
  agent-command: "*create-diagrams"
  auto-activate: true
---

# DW-DIAGRAM: Visual Architecture Lifecycle Management

**Wave**: CROSS_WAVE (primarily DESIGN integration)
**Agent**: Archer (visual-architect)
**Command**: `*create-diagrams`

## Overview

Execute comprehensive visual architecture lifecycle management through dynamic diagram generation, evolution tracking, and stakeholder communication using automated synchronization with implementation reality.

Provides visual understanding and communication at all levels: system context, component architecture, deployment topology, sequence flows, and data architecture.

## Context Files Required

- docs/architecture/architecture-design.md - Architecture definition for visualization
- docs/architecture/component-boundaries.md - Component structure
- docs/architecture/technology-stack.md - Technology choices

## Previous Artifacts (Wave Handoff)

- Varies based on diagram type and wave context
- DESIGN wave: architecture specifications
- DEVELOP wave: implementation reality

## Agent Invocation

@visual-architect

Execute \*create-diagrams for {architecture-component}.

**Context Files:**

- docs/architecture/architecture-design.md
- docs/architecture/component-boundaries.md
- docs/architecture/technology-stack.md

**Configuration:**

- diagram_type: component # component/deployment/sequence/data/context
- format: mermaid # mermaid/plantuml/c4
- level: container # context/container/component
- output_directory: docs/architecture/diagrams/

## Success Criteria

Refer to Archer's quality gates in nWave/agents/visual-architect.md.

**Key Validations:**

- [ ] Diagrams accessible to target audiences
- [ ] Visual representation matches implementation
- [ ] Evolution tracking properly configured
- [ ] Stakeholder-specific visualizations created
- [ ] Automated synchronization operational

## Next Wave

**Handoff To**: {invoking-agent-returns-to-workflow}
**Deliverables**: Visual architecture documentation

# Expected outputs (reference only):

# - docs/architecture/diagrams/system-context.svg

# - docs/architecture/diagrams/component-architecture.svg

# - docs/architecture/diagrams/deployment-architecture.svg
