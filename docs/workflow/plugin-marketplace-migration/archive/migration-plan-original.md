# Piano Migrazione AI-Craft a Plugin Claude Code

## Status: READY FOR BASELINE

---

## Analisi Corrente: Gerarchia Comandi e Skills

### Struttura Identificata dal Jobs-To-Be-Done

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PHASE 1: DISCOVERY                                 │
│                    (Quando NON SAI cosa costruire)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   DISCUSS Wave                DESIGN Wave              DISTILL Wave          │
│   ┌─────────────┐            ┌─────────────┐          ┌─────────────┐       │
│   │ start       │     →      │ design      │    →     │ distill     │       │
│   │ discuss     │            │ diagram*    │          │ skeleton    │       │
│   └─────────────┘            └─────────────┘          └─────────────┘       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 2: EXECUTION LOOP                               │
│                    (Quando SAI cosa deve cambiare)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   DEVELOP Wave (Macro Loop)                                                  │
│   ┌─────────────────────────────────────────────────────────────────┐       │
│   │                                                                  │       │
│   │   baseline → roadmap → split → execute → review                  │       │
│   │                           │        │        │                    │       │
│   │                           │        ▼        │                    │       │
│   │                           │   ┌────────┐    │                    │       │
│   │                           │   │ INNER  │◄───┘ (loop per task)    │       │
│   │                           │   │ LOOP   │                         │       │
│   │                           │   └────────┘                         │       │
│   │                           │        │                             │       │
│   │                           │        ▼                             │       │
│   │                           │   ┌──────────────────┐               │       │
│   │                           │   │ develop (TDD)    │               │       │
│   │                           │   │ refactor         │               │       │
│   │                           │   │ mikado           │               │       │
│   │                           │   └──────────────────┘               │       │
│   │                                                                  │       │
│   └─────────────────────────────────────────────────────────────────┘       │
│                                                                              │
│   DEMO Wave                                                                  │
│   ┌─────────────┐                                                           │
│   │ deliver     │                                                           │
│   │ finalize    │                                                           │
│   └─────────────┘                                                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          CROSS-WAVE (Any Time)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│   research    │   root-why    │   diagram*    │   git    │   forge          │
│   (evidence)  │   (5 Whys)    │   (visuals)   │  (VCS)   │   (agents)       │
└─────────────────────────────────────────────────────────────────────────────┘

* diagram è sia DESIGN wave che CROSS_WAVE
```

---

## Categorizzazione Comandi per Plugin

### 1. Commands (Invocazione Manuale /nw:xxx)

| Comando | Wave | Agente | Tipo |
|---------|------|--------|------|
| `start` | DISCUSS | product-owner | Entry point |
| `discuss` | DISCUSS | product-owner | Discovery |
| `design` | DESIGN | solution-architect | Discovery |
| `distill` | DISTILL | acceptance-designer | Discovery |
| `skeleton` | DISTILL | skeleton-builder | Discovery |
| `baseline` | DEVELOP | researcher | Execution gate |
| `roadmap` | DEVELOP | varies | Planning |
| `split` | DEVELOP | varies | Task breakdown |
| `execute` | DEVELOP | varies | Task execution |
| `review` | DEVELOP | *-reviewer | Quality gate |
| `finalize` | DEMO | devop | Closure |
| `deliver` | DEMO | devop | Deployment |
| `research` | CROSS_WAVE | researcher | Evidence |
| `root-why` | CROSS_WAVE | troubleshooter | Investigation |
| `diagram` | CROSS_WAVE | visual-architect | Visualization |
| `git` | CROSS_WAVE | devop | Version control |
| `forge` | CROSS_WAVE | agent-builder | Agent creation |

### 2. Skills (Auto-invocate dal Modello)

| Skill | Trigger Context | Agente |
|-------|-----------------|--------|
| `develop` | "implementa", "scrivi codice", "TDD" | software-crafter |
| `refactor` | "refactoring", "migliora codice", "pulisci" | software-crafter |
| `mikado` | "refactoring complesso", "dipendenze" | software-crafter |

### 3. Inner Loop (FULL WORKFLOW)

```
┌──────────────────────────────────────────────────────────────────┐
│                    FULL WORKFLOW PER STEP                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. IMPLEMENT ──→ 2. REVIEW ──→ 3. APPLY FIXES ──→ 4. REFACTOR  │
│       │              │               │                  │        │
│       ▼              ▼               ▼                  ▼        │
│  "Starting      "Review         "Fix applied"      "Refactoring │
│   impl..."      completed"                          completed"   │
│                                                                  │
│  ESCALATE TO USER IF ANYTHING UNEXPECTED HAPPENS                 │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Pattern Ricorrenti (Default Constraints)

### Vincoli di Default da Integrare

```yaml
output_constraints:
  - "DO NOT CREATE NEW REPORT FILES"
  - "FOCUS ON THE DELIVERABLES ONLY"
  - "EMBED THE CRITIQUE" # per review

commit_policy:
  - "DO NOT COMMIT BEFORE ASKING ME"
  - "CONFIRM PARAMETERS VALUES BEFORE PROCEEDING"
```

### Principi di Qualità da Embeddare

```yaml
quality_principles:
  tdd:
    - "Outside-in ATDD with outer and inner TDD loop"
    - "Tests names and logic should focus on business value and domain language"

  architecture:
    - "SOLID principles"
    - "Hexagonal architecture"
    - "Type system to make wrong state non-representable"
    - "Represent domain concepts in types"

  refactoring:
    - "Consider pre-refactoring if that would simplify implementation"
    - "After making a test pass refactor up to level 1,2,3 and 4"
    - "If any test is failing refactoring is not safe"
```

### Operazioni Parallele

```yaml
parallel_execution:
  pattern: "one agent per step/file to preserve context correctness"
  max_agents: 10
  use_case: ["review steps", "update steps", "implement independent steps"]
```

---

## Architettura TOON (Token Oriented Object Notation)

### TOON è uno Standard Formale

| Aspetto | Dettaglio |
|---------|-----------|
| **Versione** | v3.0 (24 novembre 2025) |
| **Spec** | github.com/toon-format/spec |
| **Media type** | text/toon (pending IANA) |
| **Estensione** | .toon |
| **Licenza** | MIT |
| **Implementazioni** | TypeScript, Python, C#, Rust, PHP, Elixir, Java |
| **Token savings** | 30-60% vs JSON (confermato) |

### Architettura Build

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ARCHITETTURA BUILD                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   SOURCE (TOON)              BUILD                 DIST (Claude Code)       │
│   Token-optimized            Compiler              Spec-compliant           │
│                                                                              │
│   ┌──────────────┐          ┌──────────┐          ┌────────────────────┐   │
│   │ agent.toon   │ ──────→  │          │ ──────→  │ agent.md           │   │
│   │              │          │  toon    │          │ (YAML frontmatter) │   │
│   └──────────────┘          │  -to-    │          └────────────────────┘   │
│                             │  claude  │                                    │
│   ┌──────────────┐          │          │          ┌────────────────────┐   │
│   │ skill.toon   │ ──────→  │          │ ──────→  │ SKILL.md           │   │
│   │              │          │          │          │ (YAML frontmatter) │   │
│   └──────────────┘          │          │          └────────────────────┘   │
│                             │          │                                    │
│   ┌──────────────┐          │          │          ┌────────────────────┐   │
│   │ command.toon │ ──────→  │          │ ──────→  │ command.md         │   │
│   │              │          │          │          │ (YAML frontmatter) │   │
│   └──────────────┘          └──────────┘          └────────────────────┘   │
│                                                                              │
│   ~60% token savings        Python                 100% Claude Code spec    │
│   Human-editable            + Jinja2 templates     Ready for installation   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Compilazione per Tipo

| Sorgente TOON | Output Claude Code | Formato Output |
|---------------|-------------------|----------------|
| `agents/*.toon` | `dist/agents/dw/*.md` | MD + YAML frontmatter |
| `commands/*.toon` | `dist/commands/dw/*.md` | MD + YAML frontmatter |
| `skills/*/SKILL.toon` | `dist/skills/*/SKILL.md` | MD + YAML frontmatter |
| `templates/*.toon` | `dist/templates/*.md` | MD (reference) |
| `baseline.toon` | `docs/workflow/*/baseline.toon` | TOON (interno) |
| `roadmap.toon` | `docs/workflow/*/roadmap.toon` | TOON (interno) |
| `steps/*.toon` | `docs/workflow/*/steps/*.toon` | TOON (interno) |

---

## Decisioni Confermate

1. **Inner Loop**: Ibrido (develop + sub-skills)
2. **Tool Restrictions**: Nessuna
3. **Thinking Budget**: Differenziato per agente
4. **Distribuzione**: GitHub marketplace
5. **Default Constraints**: Integrati nelle skill (no report extra, no auto-commit)
6. **Quality Principles**: SOLID, Hexagonal, TDD embedded
7. **Formato Sorgente**: TOON v3.0 Strict (interno, token-optimized)
8. **Formato Output**: MD + YAML frontmatter (Claude Code compliant)
9. **Workflow Files**: TOON interno (baseline, roadmap, steps)
10. **Templates in TOON**: AGENT_TEMPLATE.toon, COMMAND_TEMPLATE.toon, SKILL_TEMPLATE.toon
11. **Compilazione**: TOON → Claude Code spec (agents.md, commands.md, SKILL.md)
12. **Parser**: python-toon + Jinja2 per template output

---

## Piano di Implementazione

### Fase 1: Setup Infrastruttura TOON
1. Creare `tools/toon/` con parser e compiler
2. Aggiungere dipendenza `python-toon` (o implementazione custom)
3. Creare template Jinja2 per output Claude Code
4. Test del parser con file TOON esistente (`novel-editor-chatgpt-toon.txt`)

**File da creare:**
- `tools/toon/__init__.py`
- `tools/toon/parser.py`
- `tools/toon/compiler.py`
- `tools/toon/templates/agent.md.j2`
- `tools/toon/templates/command.md.j2`
- `tools/toon/templates/skill.md.j2`

### Fase 2: Migrazione Agenti a TOON
1. Convertire `nWave/agents/*.md` → `nWave/agents/*.toon`
2. Iniziare con 1 agente pilota (es. `software-crafter`)
3. Validare round-trip: TOON → MD → confronto con originale
4. Batch conversion degli altri agenti

**File da modificare:**
- `nWave/agents/software-crafter.md` → `.toon`
- `nWave/agents/*.md` → `*.toon` (28 file)

### Fase 3: Migrazione Comandi a TOON
1. Convertire `nWave/tasks/dw/*.md` → `*.toon`
2. Aggiornare build system per processare TOON

**File da modificare:**
- `nWave/tasks/dw/*.md` → `*.toon` (20 file)
- `tools/build_ide_bundle.py` (integrare TOON compiler)

### Fase 4: Creazione Skills
1. Creare directory `nWave/skills/`
2. Creare `develop/SKILL.toon` con full workflow integrato
3. Creare `refactor/SKILL.toon` come sub-skill
4. Creare `mikado/SKILL.toon` come sub-skill

**File da creare:**
- `nWave/skills/develop/SKILL.toon`
- `nWave/skills/refactor/SKILL.toon`
- `nWave/skills/mikado/SKILL.toon`

### Fase 5: Migrazione Templates
1. Convertire `nWave/templates/*.yaml` → `*.toon`
2. Creare SKILL_TEMPLATE.toon

**File da modificare:**
- `nWave/templates/AGENT_TEMPLATE.yaml` → `.toon`
- `nWave/templates/COMMAND_TEMPLATE.yaml` → `.toon`

### Fase 6: Migrazione Workflow Files
1. Definire schema TOON per baseline, roadmap, step
2. Creare converter per file esistenti
3. Aggiornare comandi per generare TOON invece di YAML/JSON

**File da creare/modificare:**
- `nWave/schemas/baseline.toon.schema`
- `nWave/schemas/roadmap.toon.schema`
- `nWave/schemas/step.toon.schema`

### Fase 7: Setup Plugin Structure
1. Creare `.claude-plugin/plugin.json`
2. Creare `marketplace.json`
3. Organizzare output per wave

**File da creare:**
- `.claude-plugin/plugin.json`
- `marketplace.json`
- `README.md` (plugin installation guide)

### Fase 8: Build & Distribuzione
1. Aggiornare `tools/build_ide_bundle.py` per generare plugin compliant
2. Creare script di installazione aggiornato
3. Test end-to-end del plugin
4. Push su GitHub con marketplace.json

**File da modificare:**
- `tools/build_ide_bundle.py`
- `scripts/install-ai-craft.sh`

---

## File Critici da Modificare

| File | Azione | Priorità |
|------|--------|----------|
| `tools/toon/parser.py` | Creare | P0 |
| `tools/toon/compiler.py` | Creare | P0 |
| `tools/build_ide_bundle.py` | Modificare | P1 |
| `nWave/agents/software-crafter.md` | Migrare a TOON (pilota) | P1 |
| `nWave/skills/develop/SKILL.toon` | Creare | P1 |
| `.claude-plugin/plugin.json` | Creare | P2 |
| `nWave/agents/*.md` | Migrare a TOON (batch) | P2 |
| `nWave/tasks/dw/*.md` | Migrare a TOON | P2 |
| `marketplace.json` | Creare | P3 |

---

## Criteri di Successo

1. Tutti i file sorgente in formato TOON v3.0
2. Build produce output Claude Code compliant (MD + YAML frontmatter)
3. Plugin installabile via `/plugin install`
4. Skills auto-invocate correttamente
5. Full workflow (implement → review → fix → refactor) funzionante
6. Default constraints integrati (no report extra, no auto-commit)
7. ~60% risparmio token nei file sorgente
