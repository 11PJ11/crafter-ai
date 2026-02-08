# DW-DESIGN: Architecture Design with Visual Representation

**Wave**: DESIGN
**Agent**: Morgan (solution-architect)
**Command**: `*design-architecture`

## Overview

Execute DESIGN wave of nWave methodology through comprehensive architecture design, technology selection, and visual representation creation. Transforms business requirements into robust technical architecture balancing business needs with technical excellence.

Architecture serves business objectives while enabling quality attributes (performance, security, reliability, scalability).

**CRITICAL DESIGN PRINCIPLE**: Always analyze and integrate with existing systems BEFORE designing new components. Prefer reusing existing infrastructure and open-source solutions over reimplementation.

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

**MANDATORY: Existing System Analysis Instructions**

The agent prompt MUST include these analysis requirements:

1. **Codebase Analysis Phase** (BEFORE designing):
   - Search for existing scripts/utilities related to the feature domain
   - Identify existing components that could be reused
   - Find existing data models and infrastructure
   - Locate existing configuration and installation systems
   - Document what already exists and works

2. **Integration-First Mindset**:
   - "Analyze the existing codebase in [relevant directories] BEFORE designing new components"
   - "Search for existing utilities, scripts, and infrastructure that solve similar problems"
   - "Prefer extending/integrating existing systems over creating new ones"
   - "Document why new components are necessary vs. reusing existing ones"

3. **Open Source Research**:
   - "Research existing open-source libraries for [specific functionality]"
   - "Evaluate mature solutions (GitHub stars, maintenance, license) before custom implementation"
   - "Document trade-offs: custom vs. library (complexity, maintenance, features)"

4. **Reuse Checklist** (include in prompt):
   ```
   Before designing each component, ask:
   [ ] Does this functionality already exist in the codebase?
   [ ] Is there an existing script/utility that does this?
   [ ] Is there a mature open-source library for this?
   [ ] Can we extend an existing component instead of creating new?
   [ ] What's the cost of integration vs. reimplementation?
   ```

5. **Anti-Pattern Detection**:
   - "Flag any design that duplicates existing functionality"
   - "Identify overlapping responsibilities between new and existing components"
   - "Document integration points with existing systems"

### What NOT to Include

- ❌ "Agent should invoke /nw:distill after architecture design"
- ❌ "Use /nw:diagram to create visual representations"
- ❌ Any reference to skills or other commands the agent should call
- ❌ References to next wave invocation (orchestrator handles wave transitions)
- ❌ Path references without full content embedded (agent needs content, not file paths)

**Anti-Patterns to AVOID in Agent Prompts:**

- ❌ "Design a complete backup system from scratch" (without checking if one exists)
- ❌ "Implement installation logic" (without analyzing existing installers)
- ❌ "Create new utilities for path handling" (without checking PathUtils, etc.)
- ❌ Designing components that duplicate existing functionality
- ❌ Ignoring existing scripts, utilities, and infrastructure
- ❌ Not researching open-source alternatives before custom implementation

### Example: What TO Do

✅ "FIRST: Analyze existing system in scripts/, nWave/, tools/ directories for related functionality"
✅ "Search for existing installation, backup, update scripts before designing new ones"
✅ "Research open-source libraries for [specific functionality] and document evaluation"
✅ "Design the system architecture according to these requirements: [FULL REQUIREMENTS]"
✅ "Select technology stack based on these criteria: [COMPLETE CRITERIA WITH RATIONALE]"
✅ "REUSE existing components: [LIST OF EXISTING UTILITIES/SCRIPTS WITH PATHS]"
✅ "Generate C4 diagrams following this specification: [FULL DIAGRAM SPECS]"
✅ "Create hexagonal architecture with these boundaries: [SPECIFIC PORT/ADAPTER DEFINITIONS]"
✅ "Document integration points with existing system: [EXISTING SCRIPTS/COMPONENTS]"
✅ "Provide these architecture outputs: architecture-design.md, technology-stack.md, component-boundaries.md, diagrams/"

**Example: Existing System Analysis Prompt**

✅ "Before designing, analyze the existing codebase:
   1. Use Glob to find: scripts/**/*.py, nWave/**/*.py, tools/**/*.py
   2. Search for keywords related to the feature (installation, backup, update, etc.)
   3. Read relevant existing scripts and understand their structure
   4. Identify reusable components: BackupManager, PathUtils, Logger, etc.
   5. Document what exists and how the new design integrates with it
   6. ONLY design new components if no existing solution can be reused/extended"

## Context Files Required

- docs/feature/{feature-name}/discuss/requirements.md - (from DISCUSS wave)
- docs/feature/{feature-name}/discuss/user-stories.md - (from DISCUSS wave)
- docs/feature/{feature-name}/design/constraints.md - Technical and business constraints

## Previous Artifacts (Wave Handoff)

- docs/feature/{feature-name}/discuss/requirements.md - (from DISCUSS wave)
- docs/feature/{feature-name}/discuss/user-stories.md - (from DISCUSS wave)
- docs/feature/{feature-name}/discuss/domain-model.md - (from DISCUSS wave)

## Agent Invocation

@solution-architect

Execute \*design-architecture for {feature-name}.

**Context Files:**

- docs/feature/{feature-name}/discuss/requirements.md
- docs/feature/{feature-name}/discuss/user-stories.md
- docs/feature/{feature-name}/design/constraints.md

**Previous Artifacts:**

- docs/feature/{feature-name}/discuss/requirements.md
- docs/feature/{feature-name}/discuss/user-stories.md
- docs/feature/{feature-name}/discuss/domain-model.md

**Configuration:**

- interactive: moderate
- output_format: markdown
- diagram_format: c4
- architecture: hexagonal

## Success Criteria

Refer to Morgan's quality gates in nWave/agents/solution-architect.md.

**Key Validations:**

- [ ] **Existing system analyzed BEFORE design** (codebase search performed)
- [ ] **Integration points documented** (how design integrates with existing scripts/utilities)
- [ ] **Reuse justified** (documented why new components vs. existing ones)
- [ ] **Open-source research performed** (evaluated libraries vs. custom implementation)
- [ ] Architecture supports all business requirements
- [ ] Technology stack selected with clear rationale
- [ ] Component boundaries defined (hexagonal architecture)
- [ ] **No duplication of existing functionality** (anti-pattern check passed)
- [ ] Visual diagrams complete and accessible
- [ ] Handoff accepted by acceptance-designer (DISTILL wave)
- [ ] Layer 4 peer review approval obtained

## Next Wave

**Handoff To**: acceptance-designer (DISTILL wave)
**Deliverables**: See Morgan's handoff package specification in agent file

# Expected outputs (reference only):

# - docs/feature/{feature-name}/design/architecture-design.md

# - docs/feature/{feature-name}/design/technology-stack.md

# - docs/feature/{feature-name}/design/component-boundaries.md

# - docs/feature/{feature-name}/design/data-models.md

# - docs/feature/{feature-name}/design/diagrams/\*.svg
