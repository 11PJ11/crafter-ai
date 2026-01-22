# DW-DISCUSS: Requirements Gathering and Business Analysis

**Wave**: DISCUSS
**Agent**: Riley (product-owner)
**Command**: `/nw:discuss`

## Overview

Execute DISCUSS wave (wave 2 of 6) of nWave methodology through comprehensive requirements gathering, stakeholder collaboration, and business analysis. Establishes ATDD foundation (Customer-Developer-Tester collaboration) for all subsequent waves.

The DISCUSS wave creates shared understanding between stakeholders, developers, and testers through collaborative requirements elicitation, user story creation, and acceptance criteria definition.

## Context Files Required

- docs/project-brief.md - Project context and objectives
- docs/stakeholders.yaml - Stakeholder identification and roles
- docs/architecture/constraints.md - Technical and business constraints

## Previous Artifacts (Wave Handoff)

- docs/discovery/problem-validation.md - Problem statement from DISCOVER wave
- docs/discovery/opportunity-tree.md - Opportunity analysis from DISCOVER wave
- docs/discovery/lean-canvas.md - Lean Canvas from DISCOVER wave

## Walking Skeleton First Feature Check

**CRITICAL**: Before gathering functional requirements, determine if this is a greenfield project requiring Walking Skeleton validation.

### Detection Criteria

A Walking Skeleton should be considered when **ALL** of the following are true:

1. **No production code exists**:
   - `src/` directory doesn't exist OR is empty
   - No meaningful application code in repository

2. **No previous features implemented**:
   - `docs/feature/` directory doesn't exist OR is empty
   - No prior roadmaps or feature implementations

3. **Greenfield or architectural reset**:
   - New project initialization (< 10 commits)
   - OR major architectural change requiring validation

### Detection Logic

```python
def should_suggest_walking_skeleton():
    """
    Determine if Walking Skeleton should be suggested.
    Returns: (should_suggest: bool, reason: str)
    """
    # Check 1: Production code
    src_exists = path_exists("src/")
    src_empty = is_directory_empty("src/") if src_exists else True

    # Check 2: Previous features
    feature_exists = path_exists("docs/feature/")
    feature_empty = is_directory_empty("docs/feature/") if feature_exists else True

    # Check 3: Repository maturity
    commit_count = get_git_commit_count()
    is_greenfield = commit_count < 10

    # Decision
    if src_empty and feature_empty:
        return (True, "Greenfield project - no code or features exist")
    elif not src_empty and feature_empty:
        return (True, "Code exists but no documented features - consider WS for validation")
    else:
        return (False, "Existing features detected - WS not needed")
```

### User Interaction

If detection criteria are met, use **AskUserQuestion** tool:

**Question**: "Prima implementazione rilevata. Vuoi che la prima feature sia un Walking Skeleton per validare l'architettura end-to-end?"

**Options**:
1. **"Sì, crea Walking Skeleton come Feature 0"** (Recommended for greenfield)
   - Description: "Implementa la fetta E2E più semplice per validare wiring architetturale, deployment pipeline, e test automation prima di features complesse"

2. **"No, procedi con requisiti funzionali normali"**
   - Description: "Salta Walking Skeleton e raccogli requisiti per feature di business (scelta per progetti con architettura già validata)"

### If User Selects Walking Skeleton

**Document decision** in `docs/project-brief.md`:

```markdown
## Walking Skeleton Decision

- **Decision**: Walking Skeleton as Feature 0
- **Rationale**: Greenfield project requires architectural validation
- **Date**: {current-date}
- **Decided by**: {stakeholder-name}
```

**Adjust requirements gathering**:

1. **Feature ID**: "00-walking-skeleton" (precedes normal features)
2. **Scope**: Minimal end-to-end slice:
   - One happy-path scenario only
   - Simplest possible business logic
   - All architectural layers connected
   - Automated deployment pipeline
   - Basic monitoring/health checks

3. **User Story Template**:
```markdown
## Feature 00: Walking Skeleton

**As a** development team
**I want** to implement the thinnest possible E2E slice
**So that** I can validate architecture, deployment, and testing infrastructure

### Acceptance Criteria
- [ ] Request flows through all architectural layers (API → Domain → Persistence)
- [ ] Automated tests verify E2E connectivity
- [ ] CI/CD pipeline deploys to production-like environment
- [ ] Health check endpoint returns system status
- [ ] Monitoring captures basic metrics

### Out of Scope (defer to future features)
- Error handling (except critical failures)
- Edge cases and validation
- Performance optimization
- Complex business logic
```

4. **Proceed with DISCUSS → DESIGN → DISTILL → DEVELOP** for Walking Skeleton as first feature

### If User Declines Walking Skeleton

**Document decision** in `docs/project-brief.md`:

```markdown
## Walking Skeleton Decision

- **Decision**: Walking Skeleton not needed
- **Rationale**: {user-provided-reason}
- **Date**: {current-date}
- **Decided by**: {stakeholder-name}
```

**Proceed with normal requirements gathering** for functional features.

### Notes on Walking Skeleton Benefits

**When to use**:
- ✅ Greenfield projects (new architecture)
- ✅ Unproven technology stack
- ✅ Complex distributed systems
- ✅ First microservice in new domain
- ✅ Major architectural refactoring

**When to skip**:
- ⛔ Adding feature to existing validated system
- ⛔ Architecture already proven through previous features
- ⛔ Tight deadlines with known-good patterns
- ⛔ Simple monolithic CRUD applications

**Value delivered**:
- Early risk reduction (architectural mistakes caught early)
- Team alignment on technical approach
- Deployment automation from day one
- Foundation for all future features

## Agent Invocation

@product-owner

Execute `/nw:discuss` for {feature-name}.

**Context Files:**

- docs/project-brief.md
- docs/stakeholders.yaml
- docs/architecture/constraints.md

**Configuration:**

- interactive: high
- output_format: markdown
- elicitation_depth: comprehensive

## Success Criteria

Refer to Riley's quality gates in nWave/agents/product-owner.md.

**Key Validations:**

- [ ] Requirements completeness score > 0.95
- [ ] Stakeholder consensus achieved
- [ ] All acceptance criteria testable
- [ ] Handoff accepted by solution-architect (DESIGN wave)
- [ ] Layer 4 peer review approval obtained

## Next Wave

**Handoff To**: solution-architect (DESIGN wave)
**Deliverables**: See Riley's handoff package specification in agent file

# Expected outputs (reference only):

# - docs/requirements/requirements.md

# - docs/requirements/user-stories.md

# - docs/requirements/acceptance-criteria.md
