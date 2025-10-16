---
description: 'Create comprehensive planning document [agent] [goal-description]'
argument-hint: '[agent] [goal-description] - Example: @solution-architect "Migrate to microservices"'
agent-activation:
  required: false
  agent-parameter: true
  agent-command: "*workflow-roadmap"
---

# DW-ROADMAP: Comprehensive Goal Planning Document

**Type**: Ad-hoc Planning Tool
**Agent**: Specified as parameter
**Command**: `/dw:roadmap [agent] [goal-description]`

## Overview

Invokes an expert agent to create a comprehensive, structured roadmap document that defines all phases and steps required to achieve a specific goal. The agent parameter allows selection of the most appropriate expert for the domain.

Produces a token-efficient master plan designed to be split into self-contained, atomic task files that prevent context degradation during implementation.

## Usage Examples

```bash
# Software architecture roadmap
/dw:roadmap @solution-architect "Migrate monolith to microservices"

# Data engineering roadmap
/dw:roadmap @data-engineer "Build real-time analytics pipeline"

# Complex refactoring with Mikado
/dw:roadmap @software-crafter "Replace legacy authentication system"

# Product feature roadmap
/dw:roadmap @product-owner "Implement multi-tenant support"
```

## Context Files Required

- Goal description or requirements
- Relevant existing documentation
- docs/refactoring/mikado-graph.md - If using Mikado Method

## Agent Invocation

@{specified-agent}

Create comprehensive roadmap for achieving: {goal}

### Primary Task Instructions

**Task**: Analyze goal and generate comprehensive action plan

**Key Principles**:
- Each step must be **self-contained and atomic**
- Steps should be **executable without prior context**
- Include all necessary information within each step
- Design for parallel execution where possible
- Prevent context degradation through completeness

**Output Location**: `docs/workflow/{project-id}/roadmap.yaml`

**Roadmap Structure (YAML format for token efficiency):**

```yaml
project:
  id: "project-unique-id"  # kebab-case, no spaces
  name: "Human Readable Project Name"
  goal: "Clear description of end goal"
  methodology: "standard"  # or "mikado" for complex refactoring
  created: "2024-01-01T00:00:00Z"
  estimated_duration: "2 weeks"  # human estimate

phases:
  - number: 1
    name: "Planning"
    purpose: "Define scope and requirements"
    steps:
      - number: 1
        name: "Requirements Analysis"
        description: "Analyze and document functional requirements"
        motivation: "Clear requirements prevent scope creep"
        estimated_hours: 4
        dependencies: []  # step references like "1.2", "2.1"
        acceptance_criteria:
          - "All user stories documented"
          - "Acceptance criteria defined"
          - "Non-functional requirements identified"

      - number: 2
        name: "Technical Design"
        description: "Create technical architecture"
        motivation: "Architecture guides implementation"
        estimated_hours: 6
        dependencies: ["1.1"]
        acceptance_criteria:
          - "Component diagram created"
          - "Data flow documented"
          - "Technology stack selected"

  - number: 2
    name: "Implementation"
    purpose: "Build the solution"
    steps:
      - number: 1
        name: "Core Module Development"
        description: "Implement core business logic"
        motivation: "Core functionality enables all features"
        estimated_hours: 16
        dependencies: ["1.2"]
        acceptance_criteria:
          - "Core module passes all unit tests"
          - "API contracts fulfilled"
          - "Performance benchmarks met"

mikado_integration:  # Only if methodology: "mikado"
  graph_location: "docs/refactoring/mikado-graph.md"
  goal_node: "Replace legacy system"
  leaf_nodes:
    - "Extract interface"
    - "Create adapter"
    - "Implement new service"
  discovery_tracking: true
```

### Roadmap Creation Guidelines:

1. **Project Identification**:
   - Use kebab-case for project ID (e.g., "user-auth-refactor")
   - Keep IDs unique and descriptive
   - No spaces or special characters in ID

2. **Phase Organization**:
   - Typical phases: Planning, Design, Implementation, Testing, Deployment
   - Number phases sequentially (1, 2, 3...)
   - Each phase should have clear purpose

3. **Step Definition**:
   - Steps numbered within phase (1.1, 1.2, 2.1...)
   - Include concrete acceptance criteria
   - List explicit dependencies between steps
   - Provide realistic time estimates

4. **Mikado Method Integration**:
   - Set methodology: "mikado" for complex refactoring
   - Reference existing Mikado graph
   - Map leaf nodes to implementation steps
   - Include discovery tracking flag

5. **Token Optimization**:
   - Use YAML format (more compact than JSON)
   - Abbreviate where clear (hrs, deps, desc)
   - Avoid redundant descriptions
   - Keep acceptance criteria concise

### Example Minimal Roadmap:

```yaml
project:
  id: "auth-upgrade"
  name: "Authentication System Upgrade"
  goal: "Migrate from basic auth to OAuth2"
  methodology: "standard"
  created: "2024-01-01T00:00:00Z"

phases:
  - number: 1
    name: "Planning"
    purpose: "Define OAuth2 requirements"
    steps:
      - number: 1
        name: "OAuth2 Provider Selection"
        description: "Evaluate and select OAuth2 provider"
        motivation: "Provider choice affects entire implementation"
        estimated_hours: 3
        acceptance_criteria:
          - "Provider comparison documented"
          - "Cost analysis complete"
```

## Success Criteria

**Validation Checklist:**
- [ ] Valid YAML syntax
- [ ] Unique project ID in kebab-case
- [ ] All phases numbered sequentially
- [ ] Each step contains enough information to be self-contained
- [ ] Acceptance criteria are specific and measurable
- [ ] Dependencies properly mapped between steps
- [ ] Time estimates provided for planning
- [ ] File saved as `docs/workflow/{project-id}/roadmap.yaml`
- [ ] Mikado integration included if applicable

## Next Steps

**Handoff To**: DW-SPLIT command for atomic task generation
**Deliverables**:
- Comprehensive roadmap.yaml file
- All steps designed to be executable independently
- Clear dependency graph for parallel execution

## Notes

### Design Philosophy

The roadmap is designed to be the **single source of truth** that gets transformed into atomic, self-contained tasks. The expert agent creating the roadmap should:

1. **Include all context** needed for each step
2. **Avoid forward references** to information in later steps
3. **Make dependencies explicit** rather than implicit
4. **Design for parallel execution** where possible

### Integration with Mikado Method

For complex refactoring projects, the roadmap can integrate with Mikado Method:
- Set `methodology: "mikado"` in project metadata
- Reference the Mikado graph for dependency structure
- Map leaf nodes to specific implementation steps
- Ensure discovery tracking for exploration phases

### Context Degradation Prevention

By creating a comprehensive roadmap first, we capture the full context while the expert agent has complete visibility. The subsequent split into atomic tasks ensures each sub-agent can work effectively without context accumulation that degrades performance over time.