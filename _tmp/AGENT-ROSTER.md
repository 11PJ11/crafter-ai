# nWave Framework - Agent Roster

> **Complete reference for all AI agents in the 5D-Wave methodology**

## Overview

The nWave Framework orchestrates **28 specialized AI agents** across five development waves, implementing ATDD (Acceptance Test Driven Development) with Outside-In TDD methodology.

### The 5D Flow

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ DISCUSS │───▶│ DESIGN  │───▶│ DISTILL │───▶│ DEVELOP │───▶│ DELIVER │
│  Riley  │    │  Morgan │    │  Quinn  │    │  Crafty │    │  Dakota │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
     │              │              │              │              │
     ▼              ▼              ▼              ▼              ▼
 Requirements   Architecture   Acceptance    Outside-In    Production
  Gathering       Design         Tests          TDD        Readiness
```

### Agent Architecture

- **14 Primary Agents**: Execute core responsibilities per wave
- **14 Reviewer Variants**: Haiku-optimized for cost-efficient quality gates (~50% cost reduction)
- **Reviewer Pattern**: Each primary agent has a reviewer buddy that validates outputs before wave handoff

---

## Wave Agents

### 🟦 DISCUSS Wave

> **Purpose**: Requirements gathering, stakeholder collaboration, business analysis

| Agent | Persona | Icon | Role | Reviewer |
|-------|---------|------|------|----------|
As you see, the product owner has his name that is Riley, and the product owner reviewer is a different agent with a different name. It's an agent designed to be the quality gatekeeper of the product owner. | `product-owner` | **Riley** | 📋 | Requirements Analyst & Stakeholder Facilitator | **Sage** |

#### Riley - Product Owner

| Attribute | Value |
|-----------|-------|
| **ID** | `product-owner` |
| **Command** | `/dw:discuss` → `*gather-requirements` |
| **Identity** | Expert who transforms user needs into structured requirements using LeanUX methodology |
| **Style** | Inquisitive, systematic, collaborative, business-focused, clarity-oriented |
| **Focus** | LeanUX backlog management, validated hypotheses, user story crafting, acceptance criteria definition |

**When to Use**: Processing user requirements and creating structured requirements document for ATDD discuss phase. Facilitates stakeholder collaboration and extracts business requirements with acceptance criteria.

#### Sage - Product Owner Reviewer

| Attribute | Value |
|-----------|-------|
| **ID** | `product-owner-reviewer` |
| **Title** | DoR Gate Enforcer & LeanUX Antipattern Detector |
| **Model** | Haiku (cost-optimized) |
| **Gate Type** | **HARD GATE** - blocks handoff if any DoR item fails |

**Validates**: Definition of Ready checklist (8 items), LeanUX antipatterns (8 types), story sizing compliance.

---

### 🟧 DESIGN Wave

> **Purpose**: Architecture design, technology selection, visual representation

| Agent | Persona | Icon | Role | Reviewer |
|-------|---------|------|------|----------|
| `solution-architect` | **Morgan** | 🏛️ | Solution Architect & Technical Design Lead | **Morgan** (reviewer) |
| `visual-architect` | **Archer** | 📐 | Visual Architecture Lifecycle Manager | **Archer** (reviewer) |

#### Morgan - Solution Architect

| Attribute | Value |
|-----------|-------|
| **ID** | `solution-architect` |
| **Command** | `/dw:design` → `*design-architecture` |
| **Identity** | Expert who transforms business requirements into robust technical architecture |
| **Style** | Strategic, technical, collaborative, decision-oriented, quality-focused |
| **Focus** | System architecture design, technology selection, component boundaries, integration patterns |

**When to Use**: Collaborates with user to define system architecture, component boundaries, and technical design decisions. Creates architectural design document through interactive sessions.

#### Archer - Visual Architect

| Attribute | Value |
|-----------|-------|
| **ID** | `visual-architect` |
| **Command** | `/dw:diagram` |
| **Identity** | Expert who maintains visual architecture representations throughout 5D-Wave development |
| **Style** | Visual, systematic, detail-oriented, evolution-tracking, collaborative |
| **Focus** | Visual architecture management, diagram synchronization, stakeholder communication |

**When to Use**: Maintains and updates architecture diagrams based on refactoring changes. Creates visual representations that stay synchronized with code evolution.

---

### 🟥 DISTILL Wave

> **Purpose**: Acceptance test creation, business validation, executable specifications

| Agent | Persona | Icon | Role | Reviewer |
|-------|---------|------|------|----------|
| `acceptance-designer` | **Quinn** | ✅ | Acceptance Test Designer & Business Validator | **Quinn** (reviewer) |

#### Quinn - Acceptance Designer

| Attribute | Value |
|-----------|-------|
| **ID** | `acceptance-designer` |
| **Command** | `/dw:distill` → `*create-acceptance-tests` |
| **Identity** | Expert who bridges business requirements and technical implementation through executable specifications |
| **Style** | Precise, business-focused, validation-oriented, systematic, collaborative |
| **Focus** | Acceptance test creation, business scenario validation, executable specifications, ATDD implementation |

**When to Use**: Creates E2E acceptance tests informed by architectural design using Given-When-Then format. Implements one E2E test at a time following outside-in TDD principles.

**Key Principles**:
- Business-Driven Acceptance Tests - validate business outcomes, not technical implementation
- One E2E Test at a Time - prevents commit blocks
- Production Service Integration - tests must call real production services
- DoD Validation Ownership - validates Definition of Done at DISTILL→DEVELOP transition

---

### 🟩 DEVELOP Wave

> **Purpose**: Outside-In TDD implementation, systematic refactoring, code quality

| Agent | Persona | Icon | Role | Reviewer |
|-------|---------|------|------|----------|
| `software-crafter` | **Crafty** | 🛠️ | Master Software Crafter (TDD, Refactoring, Quality) | **Crafty** (reviewer) |
| `skeleton-builder` | **Scout** | 🦴 | Walking Skeleton & E2E Automation Specialist | **Scout** (reviewer) |

#### Crafty - Software Crafter

| Attribute | Value |
|-----------|-------|
| **ID** | `software-crafter` |
| **Command** | `/dw:develop` → `*develop` |
| **Identity** | Complete software craftsmanship expert integrating Outside-In TDD with port-boundary test doubles policy, enhanced Mikado Method, and progressive systematic refactoring |
| **Style** | Methodical, test-driven, quality-obsessed, systematic, progressive, discovery-oriented |
| **Focus** | Test-first development, complex refactoring roadmaps, systematic quality improvement, architectural excellence |

**When to Use**: Complete DEVELOP wave execution - implementing features through Outside-In TDD, managing complex refactoring roadmaps with Mikado Method, and systematic code quality improvement.

**TDD Policy**:
- Classical TDD (real objects) inside hexagon
- Mockist TDD (test doubles) at port boundaries

#### Scout - Skeleton Builder

| Attribute | Value |
|-----------|-------|
| **ID** | `skeleton-builder` |
| **Command** | `/dw:skeleton` |
| **Identity** | Expert implementing Alistair Cockburn's Walking Skeleton methodology |
| **Style** | Risk-focused, minimal, iterative, validation-oriented, architecture-driven |
| **Focus** | Minimal E2E implementation, architecture validation, risk reduction, DevOps automation |

**When to Use**: Guides teams through creating minimal end-to-end implementations to validate architecture and reduce risk early in projects.

---

### 🟨 DELIVER Wave

> **Purpose**: Production readiness, stakeholder demonstration, business value delivery

| Agent | Persona | Icon | Role | Reviewer |
|-------|---------|------|------|----------|
| `devop` | **Dakota** | 🚀 | Feature Completion & Production Readiness Coordinator | **Dakota** (reviewer) |

#### Dakota - DevOp

| Attribute | Value |
|-----------|-------|
| **ID** | `devop` |
| **Command** | `/dw:deliver` → `*validate-production-readiness` |
| **Identity** | Expert who orchestrates complete feature delivery from development completion through production validation |
| **Style** | Systematic, quality-focused, stakeholder-oriented, results-driven, thorough |
| **Focus** | Production readiness validation, stakeholder demonstration, business value delivery, quality assurance |

**When to Use**: Coordinates end-to-end feature completion workflow from development through production deployment validation. Validates actual business value delivery, not just technical completion.

---

## Cross-Wave Specialists

> **Purpose**: Available across all waves for specialized tasks

### Core Specialists

| Agent | Persona | Icon | Role | Command | Reviewer |
|-------|---------|------|------|---------|----------|
| `agent-builder` | **Sage** | 🏛️ | AI Agent Architect & Safety Engineer | `/dw:forge` | **Sage** (reviewer) |
| `researcher` | **Nova** | 🤖 | Evidence-Driven Knowledge Researcher | `/dw:research` | **Nova** (reviewer) |
| `data-engineer` | **DataArch** | 🗄️ | Senior Data Engineering Architect | - | **DataArch** (reviewer) |
| `troubleshooter` | **Sage** | 🔍 | Root Cause Analysis & Problem Investigation | `/dw:root-why` | **Sage** (reviewer) |
| `illustrator` | **Luma** | 🎞️ | 2D Animation Designer & Motion Director | - | **Luma** (reviewer) |

#### Sage - Agent Builder

| Attribute | Value |
|-----------|-------|
| **ID** | `agent-builder` |
| **Command** | `/dw:forge` → `*forge` |
| **Identity** | Expert in designing and validating AI agents using research-validated patterns, safety frameworks, and quality assurance principles |
| **Style** | Systematic, security-conscious, quality-focused, research-driven, comprehensive |
| **Focus** | Agent architecture design, safety validation, specification compliance, quality assurance, testing frameworks |

**When to Use**: Creating new AI agents, validating agent specifications, implementing safety guardrails, or ensuring compliance with agentic coding best practices.

#### Nova - Researcher

| Attribute | Value |
|-----------|-------|
| **ID** | `researcher` |
| **Command** | `/dw:research` → `*research` |
| **Style** | Methodical, evidence-focused, inquisitive, thorough, critical thinker |
| **Focus** | Evidence-based research from reputable sources only |

**When to Use**: Evidence-driven research with source verification, clarification questions, and reputable knowledge gathering from web and files.

#### Sage - Troubleshooter

| Attribute | Value |
|-----------|-------|
| **ID** | `troubleshooter` |
| **Command** | `/dw:root-why` |
| **Identity** | Expert applying Toyota 5 Whys methodology and systematic investigation techniques |
| **Style** | Analytical, systematic, evidence-based, thorough, logical |
| **Focus** | Root cause identification, evidence-based analysis, systematic investigation, problem prevention |

**When to Use**: Investigating system failures, recurring issues, unexpected behaviors, or complex problems requiring systematic root cause analysis.

---

### Domain Specialists (No Reviewers)

| Agent | Persona | Icon | Role |
|-------|---------|------|------|
| `avvocato` | **Avvocato** | ⚖️ | Italian Contract Law & Software Contracts Specialist |
| `cv-optimizer` | **Marco** | 📋 | CV Optimization Specialist per Istituzioni Italiane |
| `novel-editor` | **Aria** | 📖 | Genre Fiction Novel Editor |

#### Avvocato

| Attribute | Value |
|-----------|-------|
| **ID** | `avvocato` |
| **Style** | Precise, methodical, bilingual (Italian/English), compliance-focused, risk-aware |
| **Focus** | Italian contract law (Codice Civile) application to software agreements |

**When to Use**: Analyzing software contracts under Italian law, ensuring GDPR compliance in Italian context, reviewing SaaS/cloud agreements, drafting Italian legal clauses.

#### Marco - CV Optimizer

| Attribute | Value |
|-----------|-------|
| **ID** | `cv-optimizer` |
| **Identity** | Esperto nella redazione e ottimizzazione di CV per profili IT destinati a concorsi pubblici |
| **Style** | Professionale, preciso, orientato ai risultati, attento ai dettagli, empatico |
| **Focus** | Ottimizzazione CV per istituzioni italiane, compliance GDPR, formattazione ATS-friendly |

**When to Use**: Optimizing CVs for IT profiles targeting Italian public institutions (Banca d'Italia, CONSOB, IVASS, AgID, Garante Privacy).

#### Aria - Novel Editor

| Attribute | Value |
|-----------|-------|
| **ID** | `novel-editor` |
| **Style** | Evidence-based, methodical, genre-aware, supportive, craft-focused |
| **Focus** | Plot hole detection, pacing analysis, style replication, developmental editing |

**When to Use**: Editing genre fiction novels (fantasy, sci-fi, romantasy). Specializes in plot hole detection, pacing analysis, and evidence-based narrative craft techniques.

---

## Command Reference

### Core 5D-Wave Commands

| Command | Wave | Agent | Purpose |
|---------|------|-------|---------|
| `/dw:start` | - | Riley | Initialize 5D-Wave workflow |
| `/dw:discuss` | DISCUSS | Riley | Requirements gathering and business analysis |
| `/dw:design` | DESIGN | Morgan | Architecture design with visual representation |
| `/dw:distill` | DISTILL | Quinn | Acceptance test creation and business validation |
| `/dw:develop` | DEVELOP | Crafty | Outside-In TDD implementation with refactoring |
| `/dw:deliver` | DELIVER | Dakota | Production readiness validation |

### Specialist Commands

| Command | Agent | Purpose |
|---------|-------|---------|
| `/dw:skeleton` | Scout | Walking skeleton E2E automation |
| `/dw:mikado` | Crafty | Complex refactoring roadmaps with visual tracking |
| `/dw:refactor` | Crafty | Systematic refactoring with Mikado Method |
| `/dw:research` | Nova | Evidence-driven research |
| `/dw:forge` | Sage | Create new agents |
| `/dw:diagram` | Archer | Architecture diagram management |
| `/dw:root-why` | Sage | Root cause analysis (Toyota 5 Whys) |
| `/dw:baseline` | - | Establish measurement baseline |
| `/dw:git` | - | Git workflow operations |

### Orchestration Commands (Agent-Parameterized)

| Command | Purpose | Example |
|---------|---------|---------|
| `/dw:roadmap` | Create comprehensive planning document | `@solution-architect "Migrate to microservices"` |
| `/dw:split` | Generate atomic task files from roadmap | `@devop "auth-upgrade"` |
| `/dw:review` | Expert critique and quality review | `@software-crafter task "steps/01-01.json"` |
| `/dw:execute` | Execute atomic task with state tracking | `@researcher "steps/01-01.json"` |
| `/dw:finalize` | Archive achievements and cleanup | `@devop "auth-upgrade"` |

---

## Agent Teams

Pre-configured team compositions for different project types:

### 5D-Wave Core Team
Standard projects with complete DISCUSS→DESIGN→DISTILL→DEVELOP→DELIVER methodology.

| Wave | Agent | Persona |
|------|-------|---------|
| DISCUSS | product-owner | Riley |
| DESIGN | solution-architect | Morgan |
| DESIGN | visual-architect | Archer |
| DISTILL | acceptance-designer | Quinn |
| DEVELOP | software-crafter | Crafty |
| DELIVER | devop | Dakota |

### 5D-Wave Greenfield Team
New projects with walking skeleton validation and clean architecture establishment.

Includes Core Team + `skeleton-builder` (Scout)

### 5D-Wave Brownfield Team
Legacy system enhancement with advanced refactoring specialists.

Includes Core Team + `skeleton-builder` (Scout) + Mikado Method capabilities

---

## Quality Gates

### Wave Handoff Pattern

Each wave transition includes:
1. **Primary Agent** completes work
2. **Reviewer Agent** validates output (Haiku-optimized)
3. **Checklist Validation** against wave-specific criteria
4. **Handoff Package** prepared for next wave

### Hard Gates

| Gate | Location | Enforcer | Blocks If |
|------|----------|----------|-----------|
| Definition of Ready (DoR) | DISCUSS → DESIGN | Sage (product-owner-reviewer) | Any of 8 DoR items fail |
| Definition of Done (DoD) | DISTILL → DEVELOP | Quinn (acceptance-designer) | Acceptance criteria incomplete |

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total Agents | 28 |
| Primary Agents | 14 |
| Reviewer Variants | 14 |
| Core Wave Agents | 5 |
| Cross-Wave Specialists | 9 |
| Domain Specialists | 3 |
| DW Commands | 20 |
| Pre-configured Teams | 3 |

---

*Generated for nWave Framework v1.0.0*
