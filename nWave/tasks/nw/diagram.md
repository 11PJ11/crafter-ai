# DW-DIAGRAM: Visual Architecture Lifecycle Management

**Wave**: CROSS_WAVE (primarily DESIGN integration)
**Agent**: Archer (visual-architect)
**Command**: `*create-diagrams`

## Overview

Execute comprehensive visual architecture lifecycle management through dynamic diagram generation, evolution tracking, and stakeholder communication using automated synchronization with implementation reality.

Provides visual understanding and communication at all levels: system context, component architecture, deployment topology, sequence flows, and data architecture.

## Orchestrator Briefing

**CRITICAL ARCHITECTURAL CONSTRAINT**: Sub-agents launched via Task tool have NO ACCESS to the Skill tool. They can ONLY use: Read, Write, Edit, Bash, Glob, Grep.

### What Orchestrator Must Do

1. **Read all architecture files** and embed complete specifications inline
2. **Create a complete agent prompt** that includes:
   - Full architecture design and component boundaries (inline, not paths)
   - Complete diagram format specifications for Mermaid, PlantUML, and C4 (inline syntax)
   - Diagram types and rendering procedures for each (component, deployment, sequence, data, context)
   - Multi-audience visualization strategies (business stakeholders, technical teams, operations)
   - Synchronization procedures for keeping diagrams aligned with implementation
   - All bash commands for diagram generation and validation
   - Expected output formats and file structure
3. **Do NOT reference any /nw:* commands** in the agent prompt (agent cannot invoke them)
4. **Embed all diagram creation and rendering procedures** - agent executes directly, no command delegation

### Agent Prompt Must Contain

- Full architecture design and component boundaries (inline, not path reference)
- Complete diagram format specifications with syntax rules:
  - Mermaid: syntax rules, node types, connection styles, examples for C4 components
  - PlantUML: syntax, stereotypes, layout directives, examples
  - C4 Model: context/container/component/code levels with concrete examples
- Diagram types with rendering procedures:
  - System Context: Actor identification, system boundaries, external dependencies
  - Component Architecture: Component relationships, interfaces, dependencies
  - Deployment Architecture: Infrastructure, deployment targets, communication patterns
  - Sequence Diagrams: Interaction flows, timing, system boundaries
  - Data Architecture: Data flows, storage, transformations
- Multi-audience visualization strategies (business stakeholders get high-level context, technical teams get component details, operations get deployment topology)
- Synchronization procedures to maintain alignment between diagrams and implementation
- Bash commands for diagram rendering (mermaid-cli, plantuml, graphviz)
- Expected deliverables with file paths and naming conventions
- Quality gate criteria for diagram accuracy and clarity

### What NOT to Include

- ❌ "Agent should invoke /nw:design to get architecture" (agent receives inline)
- ❌ "Use /nw:execute to validate diagrams" (agent validates directly)
- ❌ Any reference to skills or other commands the agent should call
- ❌ References to next wave invocation (orchestrator handles wave transitions)
- ❌ Path references without complete specification embedded (agent needs format specs, not tool references)
- ❌ Tool references (mermaid-cli, plantuml) without complete command syntax embedded

### Example: What TO Do

✅ "Generate C4 context diagram using this format specification: [COMPLETE MERMAID SYNTAX WITH EXAMPLES]"
✅ "Create component architecture diagram following this structure: [DIAGRAM TYPES WITH COMPLETE SPECIFICATIONS]"
✅ "Render diagrams using these bash commands: [COMPLETE COMMANDS WITH OPTIONS]"
✅ "Synchronize diagrams with implementation using this procedure: [COMPLETE SYNCHRONIZATION STEPS]"
✅ "Provide these visual outputs: system-context.svg, component-architecture.svg, deployment-architecture.svg"

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
