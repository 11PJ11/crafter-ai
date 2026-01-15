# nWave DEVELOP Workflow - Sequenza Temporale

## Diagramma Completo

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant D as /nw:develop<br/>(Orchestrator)
    participant B as /nw:baseline
    participant R as /nw:roadmap
    participant S as /nw:split
    participant RV as /nw:review
    participant E as /nw:execute
    participant F as /nw:finalize
    participant PC as Pre-Commit Hooks
    participant G as Git

    Note over U,G: === PHASE 1: INITIALIZATION ===

    U->>D: /nw:develop "feature description"
    D->>D: Create .develop-progress.json
    D->>D: Install hooks (if not present)

    Note over U,G: === PHASE 2: BASELINE ===

    D->>B: /nw:baseline "measure current state"
    B-->>D: baseline.yaml (metrics)
    D->>RV: /nw:review @researcher baseline
    RV-->>D: APPROVED / NEEDS_REVISION

    Note over U,G: === PHASE 3: ROADMAP ===

    D->>R: /nw:roadmap @solution-architect "goal"
    R-->>D: roadmap.yaml (phases, steps)
    D->>RV: /nw:review @solution-architect roadmap
    RV-->>D: APPROVED / NEEDS_REVISION

    Note over U,G: === PHASE 4: SPLIT ===

    D->>S: /nw:split @solution-architect "project-id"
    S->>S: Generate step files (01-01.json, 01-02.json, ...)
    S->>S: Embed phase_execution_log (14 phases each)
    S-->>D: steps/*.json created

    Note over S,PC: Step files MUST have phase_execution_log

    D->>RV: /nw:review @software-crafter step "steps/01-01.json"
    RV-->>D: APPROVED / NEEDS_REVISION

    Note over U,G: === PHASE 5: EXECUTE LOOP ===

    loop For each step file
        D->>E: /nw:execute @agent "steps/XX-YY.json"

        Note over E: Agent reads step file

        loop For each of 14 TDD phases
            E->>E: Update phase status to IN_PROGRESS
            E->>E: Execute phase
            E->>E: Update phase status to EXECUTED
            E->>E: Save step file (atomic write)
        end

        E->>E: Update .develop-progress.json
        E->>G: git add steps/XX-YY.json .develop-progress.json
        E->>G: git commit -m "feat: complete step XX-YY"

        G->>PC: Pre-commit triggered

        Note over PC: 3 Hooks Execute in Order

        PC->>PC: 1. nwave-step-structure-validation
        Note right of PC: Validates phase_execution_log exists<br/>Blocks if structure invalid

        PC->>PC: 2. nwave-tdd-phase-validation
        Note right of PC: Validates all 14 phases complete<br/>Blocks if phases incomplete

        alt All phases valid
            PC-->>G: PASS (exit 0)
            G-->>E: Commit accepted
        else Phases incomplete
            PC-->>G: BLOCK (exit 1)
            G-->>E: Commit rejected
            E->>E: Fix phase status
            E->>G: Retry commit
        end

        G->>PC: Post-commit triggered
        PC->>PC: 3. nwave-bypass-detector
        Note right of PC: Logs commit for audit

        E-->>D: Step complete
        D->>RV: /nw:review @software-crafter implementation
        RV-->>D: APPROVED / NEEDS_REVISION
    end

    Note over U,G: === PHASE 6: FINALIZE ===

    D->>F: /nw:finalize @devop "project-id"
    F->>F: Archive to docs/evolution/
    F->>F: Clean up feature files
    F-->>D: Evolution document created

    D-->>U: Feature complete!
```

## Ordine Temporale dei Hook

```
COMMIT TRIGGER
     │
     ▼
┌────────────────────────────────────────────────────────┐
│ PRE-COMMIT PHASE                                       │
├────────────────────────────────────────────────────────┤
│                                                        │
│  1. nwave-step-structure-validation                    │
│     ├─ Triggered by: files matching steps/*.json      │
│     ├─ Validates: phase_execution_log exists          │
│     ├─ Validates: All 14 phases present               │
│     └─ Exit 1 → BLOCKS commit if invalid              │
│                                                        │
│  2. nwave-tdd-phase-validation                         │
│     ├─ Triggered by: always_run=true                  │
│     ├─ Validates: All phases EXECUTED or SKIPPED      │
│     ├─ Validates: Progress file consistency           │
│     └─ Exit 1 → BLOCKS commit if incomplete           │
│                                                        │
└────────────────────────────────────────────────────────┘
     │
     ▼ (if all pass)
┌────────────────────────────────────────────────────────┐
│ COMMIT CREATED                                         │
└────────────────────────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────────────────────────┐
│ POST-COMMIT PHASE                                      │
├────────────────────────────────────────────────────────┤
│                                                        │
│  3. nwave-bypass-detector                              │
│     ├─ Logs commit hash, message, author              │
│     ├─ Records if --no-verify was used                │
│     └─ Never blocks (audit only)                      │
│                                                        │
└────────────────────────────────────────────────────────┘
```

## Flusso di Validazione Step File

```
┌─────────────────────┐
│    /nw:split        │
│   (generates)       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│          STEP FILE (XX-YY.json)         │
├─────────────────────────────────────────┤
│  {                                      │
│    "task_id": "01-01",                  │
│    "tdd_cycle": {                       │
│      "phase_execution_log": [           │
│        {"phase_name": "PREPARE",        │
│         "status": "NOT_EXECUTED"},      │
│        ... (14 total)                   │
│      ]                                  │
│    }                                    │
│  }                                      │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────┐
│    /nw:execute      │
│   (updates phases)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│          STEP FILE (after execute)      │
├─────────────────────────────────────────┤
│  "phase_execution_log": [               │
│    {"phase_name": "PREPARE",            │
│     "status": "EXECUTED",               │
│     "outcome": "PASS"},                 │
│    ... (all 14 phases EXECUTED)         │
│  ]                                      │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────┐
│     git commit      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│         PRE-COMMIT HOOKS                │
├─────────────────────────────────────────┤
│                                         │
│  ┌───────────────────────────────────┐  │
│  │ 1. STRUCTURE VALIDATION           │  │
│  │    ✓ phase_execution_log exists   │  │
│  │    ✓ 14 phases present            │  │
│  └───────────────────────────────────┘  │
│                 │                       │
│                 ▼                       │
│  ┌───────────────────────────────────┐  │
│  │ 2. PHASE VALIDATION               │  │
│  │    ✓ All phases EXECUTED/SKIPPED  │  │
│  │    ✓ No IN_PROGRESS phases        │  │
│  │    ✓ Progress file consistent     │  │
│  └───────────────────────────────────┘  │
│                                         │
└──────────┬──────────────────────────────┘
           │
           ▼
      COMMIT OK ✓
```

## Script Versions (v1.2.14)

| Script | Location | Purpose |
|--------|----------|---------|
| `install_nwave_target_hooks.py` | `~/.claude/scripts/` | Installa hooks nel progetto target |
| `validate_step_file.py` | `~/.claude/scripts/` | Valida struttura step dopo /nw:split |
| `nwave-step-structure-validator.py` | `{project}/scripts/hooks/` | Hook pre-commit per struttura |
| `nwave-tdd-validator.py` | `{project}/scripts/hooks/` | Hook pre-commit per fasi |
| `nwave-bypass-detector.py` | `{project}/scripts/hooks/` | Hook post-commit per audit |

## Gestione Errori

### Errore: Step file senza phase_execution_log

```
❌ docs/feature/auth/steps/01-01.json:
   • Missing phase_execution_log - step cannot track TDD phases

❌ nWave Structure: COMMIT BLOCKED
   Step files must have phase_execution_log with all 14 phases
   Run /nw:split to regenerate step files correctly
```

**Soluzione**: Rigenerare step files con `/nw:split`

### Errore: Fasi incomplete

```
❌ docs/feature/auth/steps/01-01.json:
   • REFACTOR_L2: Phase NOT_EXECUTED
   • REFACTOR_L3: Phase NOT_EXECUTED

❌ nWave TDD: COMMIT BLOCKED - Complete all 14 phases first
   Phases: PREPARE → RED → GREEN → REVIEW → REFACTOR → COMMIT
```

**Soluzione**: Completare tutte le fasi TDD prima del commit

### Errore: Progress file non sincronizzato

```
❌ Progress file issues:
   • Step 01-02 not tracked in progress file (current_step=01-01, completed=0)
   • ⚠️  Progress file not staged - run: git add .develop-progress.json
```

**Soluzione**: Aggiornare e stagare il progress file
