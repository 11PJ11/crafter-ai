# Jobs To Be Done Guide: 5D-Wave Framework

## Overview

This guide uses the **Outcome Driven Innovation (ODI)** framework to help you understand when and how to use the 5D-Wave agentic system based on your specific job context.

---

## Two Distinct Phases

The framework operates in **two fundamentally different phases** that can be used independently:

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                        PHASE 1: DISCOVERY                               │
│           (When you DON'T KNOW what to build)                           │
│                                                                         │
│   [research] ──→ discuss ──→ design ──→ distill ──→ [skeleton]          │
│       │            │           │          │                             │
│   GATHER        WHAT are    HOW should  WHAT does                       │
│   evidence      the needs?  it work?    "done" look like?               │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     PHASE 2: EXECUTION LOOP                             │
│              (When you KNOW what needs to change)                       │
│                                                                         │
│   [research] ──→ baseline ──→ roadmap ──→ split ──→ execute ──→ review  │
│       │            │            │           │          │          │     │
│   GATHER        MEASURE      PLAN it     BREAK it   DO each    CHECK    │
│   evidence      first!       completely  into atoms  task       quality │
│                                              │                          │
│                                  ◄───────────┘ (loop per task)          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Note**: `research` is a **CROSS_WAVE** capability - it can be invoked at any point when evidence-based decision making is needed.

---

## The Research Step (Cross-Wave)

Research is not a fixed step in a sequence - it's a capability you invoke **whenever you need evidence**:

| When to Research | Purpose |
|------------------|---------|
| Before discuss | Understand domain before gathering requirements |
| Before design | Evaluate technology options with evidence |
| Before baseline | Gather measurements and quantitative data |
| During roadmap execution | Research tasks as part of the plan |
| When stuck | Gather information to unblock decisions |

**Example Commands**:

```bash
# Domain research before requirements
/dw:research "multi-tenant architecture patterns"

# Technology evaluation
/dw:research "compare OAuth2 providers for enterprise"

# Performance research (quantitative)
/dw:research "analyze test execution bottlenecks"

# Research with embed for agent knowledge
/dw:research "Residuality Theory" --embed-for=solution-architect
```

---

## Jobs To Be Done

### JOB 1: Build Something New (Greenfield)

> *"I need to create something that doesn't exist yet"*

**Key Question**: What should we build?

**Sequence**:

```text
[research] → discuss → design → [diagram] → distill → [skeleton] → baseline → roadmap → split → execute → review
```

**Why each step**:

| Step | Purpose |
|------|---------|
| `research` | (Optional) Gather domain knowledge before requirements |
| `discuss` | Gather requirements - you don't know what's needed yet |
| `design` | Make architecture decisions, select technology |
| `diagram` | (Optional) Visualize architecture for stakeholder communication |
| `distill` | Define acceptance tests - what does "done" look like? |
| `skeleton` | (Optional) Prove architecture works with minimal E2E |
| `baseline` | Measure starting point for tracking improvement |
| `roadmap` | Create comprehensive plan while context is fresh |
| `split` | Break into atomic, self-contained tasks |
| `execute` | Do each task with clean context |
| `review` | Quality gate before proceeding |

**Example Commands**:

```bash
/dw:research "authentication best practices for SaaS"
/dw:start "Build user authentication system"
/dw:discuss "authentication requirements"
/dw:design --architecture=hexagonal
/dw:diagram --format=mermaid --level=container  # Visualize architecture
/dw:distill "user-login-story"
/dw:skeleton "auth-e2e-slice"
/dw:baseline "implement authentication"
/dw:roadmap @solution-architect "implement authentication"
/dw:split @devop "implement-authentication"
/dw:execute @software-crafter "docs/workflow/implement-authentication/steps/01-01.json"
/dw:review @software-crafter task "docs/workflow/implement-authentication/steps/01-02.json"
# After implementation, update diagrams if architecture evolved
/dw:diagram --format=mermaid --level=component
```

---

### JOB 2: Improve Existing System (Brownfield)

> *"I know what needs to change in our system"*

**Key Question**: How do I change it safely and incrementally?

**Sequence**:

```text
[research] → baseline → roadmap → split → execute → review (repeat)
```

**Why skip discovery**:

- You already understand the system
- Problem is identified
- Go straight to **measured, incremental execution**

**The baseline is CRITICAL**:

- Blocks roadmap creation until you MEASURE current state
- Prevents "optimizing the wrong thing" anti-pattern
- Forces evidence-based planning

**Example Commands**:

```bash
/dw:research "xUnit parallelization strategies"  # Optional: gather options
/dw:baseline "optimize test execution time"
/dw:roadmap @solution-architect "optimize test execution time"
/dw:split @devop "optimize-test-execution-time"
/dw:execute @researcher "docs/workflow/optimize-test-execution-time/steps/01-01.json"
/dw:review @software-crafter task "docs/workflow/optimize-test-execution-time/steps/02-01.json"
/dw:execute @software-crafter "docs/workflow/optimize-test-execution-time/steps/02-01.json"
# ... repeat execute → review for each task
/dw:finalize @devop "optimize-test-execution-time"
```

---

### JOB 3: Complex Refactoring

> *"Code works but structure needs improvement"*

**Key Question**: How do I restructure without breaking things?

**Sequence (simple refactoring)**:

```text
[root-why] → mikado → refactor (incremental)
```

**Sequence (complex refactoring with tracking)**:

```text
[research] → baseline → roadmap (methodology: mikado) → split → execute → review
```

**Why Mikado Method**:

- Explores dependencies BEFORE committing to changes
- Reversible at every step
- Discovery tracking for audit trail

**Example Commands**:

```bash
# Simple refactoring
/dw:mikado "extract payment processing module"
/dw:refactor --target="PaymentService" --level=3

# Complex refactoring with full tracking
/dw:research "strangler fig pattern for legacy replacement"
/dw:baseline "replace legacy authentication"
/dw:roadmap @software-crafter "replace legacy authentication"  # Sets methodology: mikado
/dw:split @devop "replace-legacy-authentication"
/dw:execute @software-crafter "docs/workflow/replace-legacy-authentication/steps/01-01.json"
```

---

### JOB 4: Investigate & Fix Issue

> *"Something is broken and I need to find why"*

**Key Question**: What's the root cause?

**Sequence**:

```text
[research] → root-why → develop → deliver
```

**Minimal sequence** - focused intervention only.

**Example Commands**:

```bash
/dw:research "JWT token expiration edge cases"  # Optional: if unfamiliar with area
/dw:root-why "authentication timeout errors in production"
/dw:develop "fix-auth-timeout"
/dw:deliver
```

---

### JOB 5: Research & Understand

> *"I need to gather information before deciding"*

**Key Question**: What are my options?

**Sequence**:

```text
research → [decision point: which job to pursue next]
```

**No execution** - pure information gathering that feeds into other jobs.

**Example Commands**:

```bash
# Technology evaluation
/dw:research "compare OAuth2 providers for enterprise use"

# Domain understanding
/dw:research "event sourcing patterns for audit trails"

# Research with knowledge embedding for future use
/dw:research "Hexagonal Architecture" --embed-for=solution-architect
```

**Research Output Locations**:

- Research files: `docs/research/{category}/{topic}.md`
- Embedded knowledge: `5d-wave/data/embed/{agent}/{topic}.md`

---

## Quick Reference Matrix

| Job | You Know What? | Sequence |
|-----|---------------|----------|
| **Greenfield** | No | [research] → discuss → design → [diagram] → distill → baseline → roadmap → split → execute → review |
| **Brownfield** | Yes | [research] → baseline → roadmap → split → execute → review |
| **Refactoring** | Partially | [research] → baseline → mikado/roadmap → split → execute → review |
| **Bug Fix** | Yes (symptom) | [research] → root-why → develop → deliver |
| **Research** | No | research → (output informs next job) |
| **Documentation** | Varies | [research] → design → diagram |

*Note: Items in `[brackets]` are optional - use when needed.*

**Cross-wave commands** (can be used anytime):

- `research` - Gather evidence
- `diagram` - Visualize architecture
- `root-why` - Investigate issues
- `git` - Version control operations

---

## Granular Jobs By Phase

This section breaks down what specific job each command fulfills.

### Discovery Phase Jobs

#### DISCUSS Wave

| Job | Command | Outcome |
|-----|---------|---------|
| Capture stakeholder needs | `/dw:discuss` | Requirements documented |
| Align business and tech | `/dw:discuss` | Shared understanding |
| Define acceptance criteria | `/dw:discuss` | Testable requirements |

#### DESIGN Wave

| Job | Command | Outcome |
|-----|---------|---------|
| Choose architecture pattern | `/dw:design` | Architecture decision |
| Select technology stack | `/dw:design` | Technology rationale |
| Define component boundaries | `/dw:design` | Clear module separation |
| Communicate architecture visually | `/dw:diagram` | Stakeholder-ready diagrams |

#### DISTILL Wave

| Job | Command | Outcome |
|-----|---------|---------|
| Define what "done" looks like | `/dw:distill` | Acceptance tests (Given-When-Then) |
| Validate architecture early | `/dw:skeleton` | Working E2E slice |
| Reduce integration risk | `/dw:skeleton` | Proven deployment pipeline |

### Execution Loop Jobs

#### BASELINE

| Job | Command | Outcome |
|-----|---------|---------|
| Measure current state | `/dw:baseline` | Quantified starting point |
| Identify biggest bottleneck | `/dw:baseline` | Prioritized problem |
| Find quick wins | `/dw:baseline` | Low-effort high-impact options |
| Prevent wrong-problem syndrome | `/dw:baseline` | Evidence-based focus |

#### ROADMAP

| Job | Command | Outcome |
|-----|---------|---------|
| Plan while context is fresh | `/dw:roadmap` | Comprehensive plan |
| Capture dependencies | `/dw:roadmap` | Sequenced steps |
| Enable parallel work | `/dw:roadmap` | Independent task identification |

#### SPLIT

| Job | Command | Outcome |
|-----|---------|---------|
| Prevent context degradation | `/dw:split` | Atomic self-contained tasks |
| Enable clean execution | `/dw:split` | Each task has full context |
| Track progress granularly | `/dw:split` | Individual task state |

#### EXECUTE

| Job | Command | Outcome |
|-----|---------|---------|
| Do work with max LLM quality | `/dw:execute` | Clean context per task |
| Track state transitions | `/dw:execute` | TODO → IN_PROGRESS → DONE |
| Capture execution results | `/dw:execute` | Evidence of completion |

#### REVIEW

| Job | Command | Outcome |
|-----|---------|---------|
| Catch issues before they propagate | `/dw:review` | Quality gate |
| Get expert critique | `/dw:review` | Domain-specific feedback |
| Validate acceptance criteria | `/dw:review` | APPROVED / NEEDS_REVISION |

### Cross-Wave Jobs

#### Research & Investigation

| Job | Command | Outcome |
|-----|---------|---------|
| Gather evidence before deciding | `/dw:research` | Cited findings |
| Evaluate technology options | `/dw:research` | Comparison analysis |
| Understand unfamiliar domain | `/dw:research` | Knowledge base |
| Find root cause (not symptoms) | `/dw:root-why` | 5 Whys analysis |
| Understand failure patterns | `/dw:root-why` | Multi-causal map |

#### Development

| Job | Command | Outcome |
|-----|---------|---------|
| Implement with TDD | `/dw:develop` | Test-first code |
| Refactor safely | `/dw:refactor` | Improved structure |
| Handle complex dependencies | `/dw:mikado` | Reversible change path |

#### Operations

| Job | Command | Outcome |
|-----|---------|---------|
| Commit with quality | `/dw:git` | Clean commits |
| Validate production readiness | `/dw:deliver` | Deployment confidence |
| Archive completed work | `/dw:finalize` | Clean project closure |

### Job Categories Summary

| Category | Core Job |
|----------|----------|
| **Understanding** | Know what to build and why |
| **Planning** | Break work into safe, trackable chunks |
| **Executing** | Do work without context degradation |
| **Validating** | Catch issues early with quality gates |
| **Communicating** | Share understanding via diagrams and docs |
| **Investigating** | Find truth before acting |

---

## When to Skip Discovery Phase

Skip `discuss → design → distill` when:

- You already understand the domain
- Requirements are clear
- Architecture is established
- Problem is well-defined

Go straight to the **execution loop** with baseline as the gate.

---

## The Execution Loop (Core Workflow)

The execution loop is the workhorse of brownfield work:

```text
[research] → baseline → roadmap → split → execute → review
                │                           │         │
                │                           └────────►│ (repeat per task)
                │                                      │
                └──────────────────────────────────────┘ (new baseline if scope changes)
```

### Why It Works

| Step | Benefit |
|------|---------|
| **research** | (Optional) Gather evidence to inform baseline and roadmap |
| **baseline** | Forces measurement before planning (prevents wrong-problem anti-pattern) |
| **roadmap** | Captures full plan while context is fresh |
| **split** | Creates atomic, self-contained tasks (prevents context degradation) |
| **execute** | Each task runs with clean context (max LLM quality) |
| **review** | Quality gate before proceeding |

### Key Principles

1. **Evidence Before Decisions**: Research when you need data to decide
2. **Measure Before Plan**: Baseline is a BLOCKING gate for roadmap
3. **Atomic Tasks**: Each task is self-contained with all context embedded
4. **Clean Context**: Each execute starts fresh (no accumulated confusion)
5. **Quality Gates**: Review before moving to next task

---

## Baseline Types

The `/dw:baseline` command supports three types:

### 1. Performance Optimization

Use when improving speed, reducing resource usage, or optimizing throughput.

**Required**:

- Timing measurements with breakdown
- Bottleneck ranking
- Target metrics with evidence
- Quick wins identified

### 2. Process Improvement

Use when fixing workflow issues, preventing incidents, or improving reliability.

**Required**:

- Incident references OR failure modes
- Simplest alternatives considered (with why insufficient)

### 3. Feature Development

Use when building new capabilities (greenfield or brownfield development).

**Required**:

- Current state analysis
- Requirements source and validation

---

## Agent Selection Guide

### Core Wave Agents

| Agent | Use For |
|-------|---------|
| `@product-owner` | Requirements, business analysis, stakeholder alignment |
| `@solution-architect` | Architecture design, technology selection, planning |
| `@acceptance-designer` | BDD scenarios, acceptance tests, test completeness |
| `@software-crafter` | Implementation, TDD, refactoring, code quality |
| `@devop` | Deployment, operations, lifecycle management, git workflow |

### Cross-Wave Specialist Agents

| Agent | Use For |
|-------|---------|
| `@researcher` | Information gathering, evidence collection, analysis |
| `@troubleshooter` | Root cause analysis, failure investigation (Toyota 5 Whys) |
| `@visual-architect` | Architecture diagrams, visual documentation |
| `@skeleton-builder` | Walking skeleton, early E2E validation |
| `@data-engineer` | Database systems, data pipelines, query optimization, data governance |
| `@illustrator` | Visual 2D diagrams, design artifacts, workflow visualizations |

### Utility Agents

| Agent | Use For |
|-------|---------|
| `@agent-builder` | Create new agents using validated patterns and templates |
| `@avvocato` | Italian contract law, GDPR compliance, software contracts (domain-specific) |

### Reviewer Agents (Cost-Optimized)

Every agent has a corresponding `*-reviewer` variant that uses the Haiku model for cost-efficient reviews:

- `@software-crafter-reviewer` - Code quality review
- `@solution-architect-reviewer` - Architecture review
- `@product-owner-reviewer` - Requirements review
- `@acceptance-designer-reviewer` - Test completeness review
- etc.

**Usage**: The `/dw:review` command automatically routes to the reviewer variant.

---

## Common Workflows

### New Feature on Existing Codebase

```bash
/dw:research "best practices for {feature-domain}"  # Optional
/dw:baseline "add multi-tenant support"
/dw:roadmap @solution-architect "add multi-tenant support"
/dw:split @devop "add-multi-tenant-support"
# execute → review loop
```

### Performance Optimization

```bash
/dw:research "profiling techniques for {technology}"  # Optional
/dw:baseline "optimize API response time"  # Type: performance_optimization
/dw:roadmap @solution-architect "optimize API response time"
/dw:split @devop "optimize-api-response-time"
# execute → review loop
```

### Legacy System Modernization

```bash
/dw:research "strangler fig pattern"
/dw:root-why "current system limitations"
/dw:baseline "migrate to microservices"
/dw:roadmap @solution-architect "migrate to microservices"
/dw:split @devop "migrate-to-microservices"
# execute → review loop with mikado for complex refactoring
```

### Quick Bug Fix

```bash
/dw:root-why "users cannot login after password reset"
/dw:develop "fix-password-reset-flow"
/dw:deliver
```

### Pure Research Task

```bash
/dw:research "event sourcing vs CRUD for audit requirements"
# Output: docs/research/architecture-patterns/event-sourcing-vs-crud.md
# Decision: proceed with JOB 1, 2, or 3 based on findings
```

### Architecture with Visual Documentation

```bash
/dw:design --architecture=hexagonal
/dw:diagram --format=mermaid --level=container
# Output: docs/architecture/diagrams/*.svg
```

### Data-Heavy Project

```bash
/dw:research "compare PostgreSQL vs MongoDB for {use-case}"
# Invoke data-engineer agent for specialized guidance
/dw:baseline "implement data pipeline"
/dw:roadmap @data-engineer "implement data pipeline"
/dw:split @devop "implement-data-pipeline"
# execute → review loop
```

### Git Workflow Integration

```bash
# After completing a task
/dw:git commit  # Auto-generates commit message
/dw:git branch "feature/auth-upgrade"
/dw:git push
```

### Creating a New Agent

```bash
/dw:forge  # Uses agent-builder to create new agent from template
# Output: 5d-wave/agents/{new-agent}.md
```

---

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Skip research | Decisions without evidence | Research when unfamiliar with domain |
| Skip baseline | Optimize wrong thing | Always baseline before roadmap |
| Monolithic tasks | Context degradation | Use split for atomic tasks |
| Skip review | Quality issues propagate | Review before each execute |
| Architecture before measurement | Over-engineering | Baseline identifies quick wins first |
| Forward references in tasks | Tasks not self-contained | Each task must have all context embedded |

---

## Complete Command Reference

### Discovery Phase Commands

| Command | Agent | Purpose |
|---------|-------|---------|
| `/dw:start` | product-owner | Initialize 5D-Wave workflow with project brief |
| `/dw:discuss` | product-owner | Requirements gathering and business analysis |
| `/dw:design` | solution-architect | Architecture design with technology selection |
| `/dw:distill` | acceptance-designer | Acceptance test creation (Given-When-Then) |
| `/dw:skeleton` | skeleton-builder | Walking skeleton E2E validation |

### Execution Loop Commands

| Command | Agent | Purpose |
|---------|-------|---------|
| `/dw:baseline` | researcher | Establish measurement baseline (BLOCKS roadmap) |
| `/dw:roadmap` | varies | Create comprehensive planning document |
| `/dw:split` | varies | Generate atomic task files from roadmap |
| `/dw:execute` | varies | Execute atomic task with state tracking |
| `/dw:review` | *-reviewer | Expert critique and quality assurance |
| `/dw:finalize` | devop | Archive project and clean up workflow |
| `/dw:deliver` | devop | Production readiness validation |

### Cross-Wave Specialist Commands

| Command | Agent | Purpose |
|---------|-------|---------|
| `/dw:research` | researcher | Evidence-driven research with source verification |
| `/dw:root-why` | troubleshooter | Toyota 5 Whys root cause analysis |
| `/dw:mikado` | software-crafter | Complex refactoring roadmaps (Mikado Method) |
| `/dw:refactor` | software-crafter | Systematic code refactoring (Level 1-6) |
| `/dw:develop` | software-crafter | Outside-In TDD implementation |
| `/dw:diagram` | visual-architect | Architecture diagram lifecycle management |

### Utility Commands

| Command | Agent | Purpose |
|---------|-------|---------|
| `/dw:git` | devop | Git workflow operations (commit, branch, merge) |
| `/dw:forge` | agent-builder | Create new agents from templates |

---

## File Locations

| Artifact | Location |
|----------|----------|
| Research | `docs/research/{category}/{topic}.md` |
| Embedded Knowledge | `5d-wave/data/embed/{agent}/{topic}.md` |
| Baseline | `docs/workflow/{project-id}/baseline.yaml` |
| Roadmap | `docs/workflow/{project-id}/roadmap.yaml` |
| Tasks | `docs/workflow/{project-id}/steps/*.json` |
| Reviews | Embedded in task files |
| Architecture | `docs/architecture/` |
| Architecture Diagrams | `docs/architecture/diagrams/` |
| Requirements | `docs/requirements/` |
| Agents | `5d-wave/agents/` |
