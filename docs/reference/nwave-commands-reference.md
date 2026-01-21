# nWave Commands Reference

**Version**: 1.4.0
**Date**: 2026-01-21
**Status**: Production Ready

Quick reference for all nWave commands, agents, and file locations.

**Related Docs**:
- [Jobs To Be Done Guide](../guides/jobs-to-be-done-guide.md) (explanation)
- [How to Invoke Reviewers](../guides/how-to-invoke-reviewers.md) (how-to)

---

## Discovery Phase Commands

| Command | Agent | Purpose |
|---------|-------|---------|
| `/nw:start` | product-owner | Initialize nWave workflow with project brief |
| `/nw:discuss` | product-owner | Requirements gathering and business analysis |
| `/nw:design` | solution-architect | Architecture design with technology selection |
| `/nw:distill` | acceptance-designer | Acceptance test creation (Given-When-Then) |
| `/nw:skeleton` | skeleton-builder | Walking skeleton E2E validation |

---

## Execution Loop Commands

| Command | Agent | Purpose |
|---------|-------|---------|
| `/nw:baseline` | researcher | Establish measurement baseline (BLOCKS roadmap) |
| `/nw:roadmap` | varies | Create comprehensive planning document |
| `/nw:split` | varies | Generate atomic task files from roadmap |
| `/nw:execute` | varies | Execute atomic task with state tracking |
| `/nw:review` | *-reviewer | Expert critique and quality assurance |
| `/nw:finalize` | devop | Archive project and clean up workflow |
| `/nw:deliver` | devop | Production readiness validation |

---

## Cross-Wave Specialist Commands

| Command | Agent | Purpose |
|---------|-------|---------|
| `/nw:research` | researcher | Evidence-driven research with source verification |
| `/nw:root-why` | troubleshooter | Toyota 5 Whys root cause analysis |
| `/nw:mikado` | software-crafter | Complex refactoring roadmaps (Mikado Method) |
| `/nw:refactor` | software-crafter | Systematic code refactoring (Level 1-6) |
| `/nw:develop` | software-crafter | Outside-In TDD implementation |
| `/nw:diagram` | visual-architect | Architecture diagram lifecycle management |

---

## Utility Commands

| Command | Agent | Purpose |
|---------|-------|---------|
| `/nw:git` | devop | Git workflow operations (commit, branch, merge) |
| `/nw:forge` | agent-builder | Create new agents from templates |

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

### Reviewer Agents (Cost-Optimized)

Every agent has a corresponding `*-reviewer` variant using the Haiku model:

| Reviewer | Reviews |
|----------|---------|
| `@software-crafter-reviewer` | Code quality |
| `@solution-architect-reviewer` | Architecture |
| `@product-owner-reviewer` | Requirements |
| `@acceptance-designer-reviewer` | Test completeness |
| `@devop-reviewer` | Deployment readiness |
| `@researcher-reviewer` | Research quality |
| `@troubleshooter-reviewer` | RCA quality |

**Note**: `/nw:review` automatically routes to the reviewer variant.

---

## File Locations

| Artifact | Location |
|----------|----------|
| Research | `docs/research/{category}/{topic}.md` |
| Embedded Knowledge | `nWave/data/embed/{agent}/{topic}.md` |
| Baseline | `docs/workflow/{project-id}/baseline.yaml` |
| Roadmap | `docs/workflow/{project-id}/roadmap.yaml` |
| Tasks | `docs/workflow/{project-id}/steps/*.json` |
| Reviews | Embedded in task files |
| Architecture | `docs/architecture/` |
| Architecture Diagrams | `docs/architecture/diagrams/` |
| Requirements | `docs/requirements/` |
| Agents | `nWave/agents/` |

---

## Quick Job Reference Matrix

| Job | You Know What? | Sequence |
|-----|---------------|----------|
| **Greenfield** | No | [research] -> discuss -> design -> [diagram] -> distill -> baseline -> roadmap -> split -> execute -> review |
| **Brownfield** | Yes | [research] -> baseline -> roadmap -> split -> execute -> review |
| **Refactoring** | Partially | [research] -> baseline -> mikado/roadmap -> split -> execute -> review |
| **Bug Fix** | Yes (symptom) | [research] -> root-why -> develop -> deliver |
| **Research** | No | research -> (output informs next job) |

*Items in `[brackets]` are optional.*

---

## Command Parameters

### Common Flags

| Flag | Description | Commands |
|------|-------------|----------|
| `--architecture=<type>` | hexagonal, layered, microservices | design |
| `--format=<type>` | mermaid, plantuml, c4 | diagram |
| `--level=<type>` | context, container, component | diagram |
| `--embed-for=<agent>` | Target agent for knowledge | research |

### Command Syntax Examples

```bash
# Start new project
/nw:start "Project name"

# Requirements gathering
/nw:discuss "feature requirements"

# Architecture design
/nw:design --architecture=hexagonal

# Create diagram
/nw:diagram --format=mermaid --level=container

# Baseline before roadmap
/nw:baseline "goal description"

# Create roadmap
/nw:roadmap @solution-architect "goal description"

# Split into tasks
/nw:split @devop "project-id"

# Execute task
/nw:execute @software-crafter "path/to/step.json"

# Review task
/nw:review @software-crafter task "path/to/step.json"

# Research with embedding
/nw:research "topic" --embed-for=solution-architect

# Root cause analysis
/nw:root-why "problem description"

# Git operations
/nw:git commit
/nw:git branch "feature/name"
/nw:git push
```

---

**Last Updated**: 2026-01-21
**Type**: Reference
**Purity**: 98%+
