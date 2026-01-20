# DW-DESIGN: Architecture Design with Visual Representation

**Wave**: DESIGN
**Agent**: Morgan (solution-architect)
**Command**: `*design-architecture`

## Overview

Execute DESIGN wave of nWave methodology through comprehensive architecture design, technology selection, and visual representation creation. Transforms business requirements into robust technical architecture balancing business needs with technical excellence.

Architecture serves business objectives while enabling quality attributes (performance, security, reliability, scalability).

## Orchestrator Briefing

**CRITICAL ARCHITECTURAL CONSTRAINT**: Sub-agents launched via Task tool have NO ACCESS to the Skill tool. They can ONLY use: Read, Write, Edit, Bash, Glob, Grep.

### What Orchestrator Must Do

When delegating this command to an agent via Task tool:

1. **Read requirements files and constraints** and embed complete business context inline
2. **Create a complete agent prompt** that includes:
   - Full requirements.md, user-stories.md, and domain-model.md content (inline, not paths)
   - Architecture constraints and technical requirements
   - Hexagonal architecture principles and component boundary definitions
   - Technology selection criteria and evaluation framework
   - C4 diagram specifications and visual representation guidance
   - All deliverable formats and architecture decision templates
3. **Do NOT reference any /nw:* commands** in the agent prompt (agent cannot invoke them)
4. **Embed all architecture design procedures** - agent executes directly, no command delegation

### Agent Prompt Must Contain

- Full business requirements content (inline)
- Complete user stories with acceptance criteria (inline)
- Domain model and core business entities (inline)
- Technical constraints and quality attributes (performance, security, reliability, scalability)
- Architecture style specification (hexagonal architecture patterns)
- Component boundary definition procedures
- Port and adapter identification methodology
- Technology selection criteria and decision framework
- C4 diagram generation specifications (Context, Container, Component, Code levels)
- Expected deliverables with file paths and content structure
- Quality gate criteria for architecture completeness and consistency

### What NOT to Include

- ❌ "Agent should invoke /nw:distill after architecture design"
- ❌ "Use /nw:diagram to create visual representations"
- ❌ Any reference to skills or other commands the agent should call
- ❌ References to next wave invocation (orchestrator handles wave transitions)
- ❌ Path references without full content embedded (agent needs content, not file paths)

### Example: What TO Do

✅ "Design the system architecture according to these requirements: [FULL REQUIREMENTS]"
✅ "Select technology stack based on these criteria: [COMPLETE CRITERIA WITH RATIONALE]"
✅ "Generate C4 diagrams following this specification: [FULL DIAGRAM SPECS]"
✅ "Create hexagonal architecture with these boundaries: [SPECIFIC PORT/ADAPTER DEFINITIONS]"
✅ "Provide these architecture outputs: architecture-design.md, technology-stack.md, component-boundaries.md, diagrams/"

## Context Files Required

- docs/requirements/requirements.md - (from DISCUSS wave)
- docs/requirements/user-stories.md - (from DISCUSS wave)
- docs/architecture/constraints.md - Technical and business constraints

## Previous Artifacts (Wave Handoff)

- docs/requirements/requirements.md - (from DISCUSS wave)
- docs/requirements/user-stories.md - (from DISCUSS wave)
- docs/requirements/domain-model.md - (from DISCUSS wave)

## Agent Invocation

@solution-architect

Execute \*design-architecture for {feature-name}.

**Context Files:**

- docs/requirements/requirements.md
- docs/requirements/user-stories.md
- docs/architecture/constraints.md

**Previous Artifacts:**

- docs/requirements/requirements.md
- docs/requirements/user-stories.md
- docs/requirements/domain-model.md

**Configuration:**

- interactive: moderate
- output_format: markdown
- diagram_format: c4
- architecture: hexagonal

## Success Criteria

Refer to Morgan's quality gates in nWave/agents/solution-architect.md.

**Key Validations:**

- [ ] Architecture supports all business requirements
- [ ] Technology stack selected with clear rationale
- [ ] Component boundaries defined (hexagonal architecture)
- [ ] Visual diagrams complete and accessible
- [ ] Handoff accepted by acceptance-designer (DISTILL wave)
- [ ] Layer 4 peer review approval obtained

## Next Wave

**Handoff To**: acceptance-designer (DISTILL wave)
**Deliverables**: See Morgan's handoff package specification in agent file

# Expected outputs (reference only):

# - docs/architecture/architecture-design.md

# - docs/architecture/technology-stack.md

# - docs/architecture/component-boundaries.md

# - docs/architecture/diagrams/\*.svg
