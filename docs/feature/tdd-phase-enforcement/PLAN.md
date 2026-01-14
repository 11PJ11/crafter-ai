# Piano: Enforcement Granulare delle Fasi TDD

**Data**: 2026-01-14
**Stato**: IMPLEMENTAZIONE COMPLETATA
**Autori**: Utente + Lyra
**Completato**: 2026-01-14

## Implementazione Completata

Tutti i file sono stati creati/modificati come da piano:

| # | File | Stato |
|---|------|-------|
| 1 | `nWave/templates/step-tdd-cycle-schema.json` | COMPLETATO - Schema v2.0.0 con 14 fasi pre-popolate |
| 2 | `nWave/hooks/pre_commit_tdd_phases.py` | COMPLETATO - Hook Python cross-platform |
| 3 | `nWave/hooks/post_commit_bypass_logger.py` | COMPLETATO - Bypass detection |
| 4 | `nWave/hooks/README.md` | COMPLETATO - Documentazione hooks |
| 5 | `nWave/scripts/migrate_step_files.py` | COMPLETATO - Migrazione step esistenti |
| 6 | `nWave/scripts/validate_tdd_phases_ci.py` | COMPLETATO - Validazione CI/CD |
| 7 | `nWave/tasks/nw/split.md` | COMPLETATO - Regole pre-population |
| 8 | `nWave/tasks/nw/execute.md` | COMPLETATO - Protocollo tracking fasi |
| 9 | `nWave/tasks/nw/develop.md` | COMPLETATO - Installazione hook + 14 fasi |

---

---

## Decisioni Prese

| Questione | Decisione | Implicazioni |
|-----------|-----------|--------------|
| **Migrazione step esistenti** | Entrambi | Script `migrate_step_files.py` + hook tollerante per vecchi file |
| **Fasi SKIPPED** | Permesso con `blocked_by` | Status SKIPPED valido solo se `blocked_by` contiene motivazione documentata |
| **Bypass logging** | Log locale | Scrivere in `.git/nwave-bypass.log` quando si usa `--no-verify` |
| **CI Integration** | Script CI dedicato | Creare `validate_tdd_phases_ci.py` per GitHub Actions, GitLab CI, etc. |

---

## Problema Identificato

### Situazione Attuale

1. Il `phase_execution_log` negli step file è **inizialmente vuoto**
2. L'agente *dovrebbe* popolarlo ma **nulla lo obbliga**
3. La validazione in `develop.md:834` controlla solo se esiste `COMMIT/PASS`, non se tutte le fasi precedenti sono state eseguite
4. Un agente può saltare fasi senza conseguenze
5. Non c'è modo di sapere quali fasi sono state realmente eseguite vs saltate

### Conseguenze

- Impossibile fare audit del processo TDD
- Nessuna garanzia che tutte le fasi siano state eseguite
- Se l'esecuzione si interrompe, non si sa da dove riprendere
- Quality gate inefficace

---

## Soluzione Proposta

### Principio Fondamentale

**Pre-popolare lo step file con uno "scheletro" di tutte le fasi** già presenti ma con status `NOT_EXECUTED`. L'agente deve compilare ogni fase quando la esegue. La review e il pre-commit hook validano che tutte le fasi siano compilate.

### Architettura di Enforcement a 3 Livelli

```
┌─────────────────────────────────────────────────────────────┐
│                    LIVELLO 1: STRUTTURALE                   │
│  Step file nasce con tutte le fasi pre-popolate (vuote)     │
│  L'agente DEVE compilare ogni fase per procedere            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    LIVELLO 2: REVIEW                        │
│  software-crafter-reviewer valida completezza fasi          │
│  Blocca se mancano fasi o sono incomplete                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                 LIVELLO 3: PRE-COMMIT HOOK                  │
│  Hook Python automatico verifica TUTTE le fasi              │
│  Impossibile committare con fasi mancanti                   │
│  Cross-platform (Windows, Mac, Linux)                       │
└─────────────────────────────────────────────────────────────┘
```

---

## File da Modificare/Creare

### Riepilogo

| # | File | Azione | Priorità | Descrizione |
|---|------|--------|----------|-------------|
| 1 | `nWave/templates/step-tdd-cycle-schema.json` | Modifica | ALTA | Pre-popolare phase_execution_log + regole SKIPPED |
| 2 | `nWave/tasks/nw/split.md` | Modifica | ALTA | Generare step con fasi pre-popolate |
| 3 | `nWave/tasks/nw/execute.md` | Modifica | ALTA | Istruzioni compilazione fasi |
| 4 | `nWave/tasks/nw/develop.md` | Modifica | ALTA | Validazione + installazione hook |
| 5 | `nWave/tasks/nw/review.md` | Modifica | MEDIA | Dimensione review completezza + validazione SKIPPED |
| 6 | `nWave/agents/software-crafter.toon` | Modifica | MEDIA | Principio tracking fasi |
| 7 | `nWave/agents/software-crafter-reviewer.toon` | Modifica | MEDIA | Dimensione review fasi |
| 8 | `nWave/hooks/pre_commit_tdd_phases.py` | **Nuovo** | ALTA | Script Python cross-platform + bypass logging |
| 9 | `nWave/hooks/README.md` | **Nuovo** | BASSA | Documentazione hooks |
| 10 | `nWave/scripts/migrate_step_files.py` | **Nuovo** | MEDIA | Migrazione step file esistenti |
| 11 | `nWave/scripts/validate_tdd_phases_ci.py` | **Nuovo** | MEDIA | Script per CI/CD pipelines |

---

## Dettaglio Modifiche per File

### 1. `nWave/templates/step-tdd-cycle-schema.json`

**Obiettivo**: Pre-popolare `phase_execution_log` con tutte le 14 fasi TDD.

**Schema fase singola**:

```json
{
  "phase_name": "PREPARE",
  "phase_index": 0,
  "status": "NOT_EXECUTED",
  "started_at": null,
  "ended_at": null,
  "duration_minutes": null,
  "outcome": null,
  "outcome_details": null,
  "artifacts_created": [],
  "artifacts_modified": [],
  "test_results": {
    "total": null,
    "passed": null,
    "failed": null,
    "skipped": null
  },
  "notes": null,
  "blocked_by": null
}
```

**Fasi da pre-popolare** (14 totali):

```json
"phase_execution_log": [
  { "phase_name": "PREPARE", "phase_index": 0, "status": "NOT_EXECUTED", ... },
  { "phase_name": "RED_ACCEPTANCE", "phase_index": 1, "status": "NOT_EXECUTED", ... },
  { "phase_name": "RED_UNIT", "phase_index": 2, "status": "NOT_EXECUTED", ... },
  { "phase_name": "GREEN_UNIT", "phase_index": 3, "status": "NOT_EXECUTED", ... },
  { "phase_name": "CHECK_ACCEPTANCE", "phase_index": 4, "status": "NOT_EXECUTED", ... },
  { "phase_name": "GREEN_ACCEPTANCE", "phase_index": 5, "status": "NOT_EXECUTED", ... },
  { "phase_name": "REVIEW", "phase_index": 6, "status": "NOT_EXECUTED", ... },
  { "phase_name": "REFACTOR_L1", "phase_index": 7, "status": "NOT_EXECUTED", ... },
  { "phase_name": "REFACTOR_L2", "phase_index": 8, "status": "NOT_EXECUTED", ... },
  { "phase_name": "REFACTOR_L3", "phase_index": 9, "status": "NOT_EXECUTED", ... },
  { "phase_name": "REFACTOR_L4", "phase_index": 10, "status": "NOT_EXECUTED", ... },
  { "phase_name": "POST_REFACTOR_REVIEW", "phase_index": 11, "status": "NOT_EXECUTED", ... },
  { "phase_name": "FINAL_VALIDATE", "phase_index": 12, "status": "NOT_EXECUTED", ... },
  { "phase_name": "COMMIT", "phase_index": 13, "status": "NOT_EXECUTED", ... }
]
```

**Aggiunta regole validazione**:

```json
"phase_validation_rules": {
  "all_phases_required": true,
  "valid_statuses": ["NOT_EXECUTED", "IN_PROGRESS", "EXECUTED", "SKIPPED", "BLOCKED"],
  "commit_requires": {
    "all_phases_executed": true,
    "no_in_progress": true,
    "no_blocked_without_reason": true,
    "sequential_order": true
  },
  "skip_allowed_only_if": "blocked_by is not null AND documented"
}
```

---

### 2. `nWave/tasks/nw/split.md`

**Obiettivo**: Assicurare che gli step file generati includano le fasi pre-popolate.

**Sezioni da modificare**:

1. **Step Generation Rules** (~linea 486): Aggiungere regola esplicita
2. **Schema JSON generato**: Includere phase_execution_log completo
3. **TDD Cycle Template Embedding**: Verificare merge corretto

**Aggiunta testo**:

```markdown
### Phase Pre-Population Rule

**CRITICAL**: Every generated step file MUST include the complete `phase_execution_log`
with all 14 phases pre-populated with status `NOT_EXECUTED`.

This is NON-NEGOTIABLE. The agent cannot add phases - they must already exist.
The agent can only UPDATE existing phase entries.

Verification:
- After generating step file, count entries in phase_execution_log
- MUST be exactly 14 entries
- All must have status "NOT_EXECUTED"
- All must have phase_index 0-13 in order
```

---

### 3. `nWave/tasks/nw/execute.md`

**Obiettivo**: Istruzioni esplicite per l'agente su come aggiornare ogni fase.

**Aggiunta sezione**:

```markdown
## MANDATORY: Phase Tracking Protocol

The step file contains a pre-populated `phase_execution_log` with all 14 TDD phases.
You MUST update each phase as you execute it.

### Before Starting a Phase

1. READ the step file
2. LOCATE the phase entry in `tdd_cycle.phase_execution_log` by `phase_name`
3. UPDATE the entry:
   ```json
   {
     "status": "IN_PROGRESS",
     "started_at": "<current ISO timestamp>"
   }
   ```
4. SAVE the step file

### After Completing a Phase

5. UPDATE the entry:
   ```json
   {
     "status": "EXECUTED",
     "ended_at": "<current ISO timestamp>",
     "duration_minutes": <calculated>,
     "outcome": "PASS" or "FAIL",
     "outcome_details": "<description if FAIL>",
     "artifacts_created": ["<list of files created>"],
     "artifacts_modified": ["<list of files modified>"],
     "test_results": {
       "total": <number>,
       "passed": <number>,
       "failed": <number>,
       "skipped": <number>
     },
     "notes": "<any relevant notes>"
   }
   ```
6. SAVE the step file IMMEDIATELY

### Critical Rules

- **NEVER batch updates** - Save after EACH phase
- **NEVER skip phases** - All 14 must be executed
- **NEVER leave IN_PROGRESS** - Complete or mark as BLOCKED
- **If blocked**: Set `status: "BLOCKED"` and `blocked_by: "<reason>"`

### Validation Before Commit

Before the COMMIT phase, verify:
- All 13 previous phases have status "EXECUTED"
- No phase has status "IN_PROGRESS" or "NOT_EXECUTED"
- If any phase is "BLOCKED", document reason and get approval
```

---

### 4. `nWave/tasks/nw/develop.md`

**Obiettivo**:
1. Verificare/installare pre-commit hook
2. Validare tutte le fasi prima di considerare step completato

**Aggiunta Sezione - Phase 0: Pre-Commit Hook**:

```markdown
## Phase 0: Pre-Commit Hook Verification

Before executing any step, verify the TDD phase validation hook is installed.

### Hook Detection

```python
import os
import sys

def get_hook_path():
    """Get the pre-commit hook path, cross-platform."""
    git_dir = ".git"
    if not os.path.isdir(git_dir):
        return None
    hooks_dir = os.path.join(git_dir, "hooks")
    return os.path.join(hooks_dir, "pre-commit")

def check_hook_installed():
    """Check if nWave TDD hook is installed."""
    hook_path = get_hook_path()
    if not hook_path or not os.path.exists(hook_path):
        return False

    with open(hook_path, 'r', encoding='utf-8') as f:
        content = f.read()

    return "nWave-TDD-PHASE-VALIDATION" in content
```

### If Hook Not Installed - User Prompt

```
┌─────────────────────────────────────────────────────────────┐
│  nWave TDD Phase Validation Hook                            │
├─────────────────────────────────────────────────────────────┤
│  This project uses 14-phase TDD methodology.                │
│  A pre-commit hook can enforce that ALL phases are          │
│  completed before allowing commits.                         │
│                                                             │
│  The hook will:                                             │
│  ✓ Check step files have all phases executed                │
│  ✓ Block commits with incomplete phases                     │
│  ✓ Show which phases are missing                            │
│  ✓ Work on Windows, Mac, and Linux                          │
│                                                             │
│  Install pre-commit hook?                                   │
│                                                             │
│  [1] Yes, install the hook (Recommended)                    │
│  [2] No, skip hook installation                             │
│  [3] Show me the hook code first                            │
└─────────────────────────────────────────────────────────────┘
```

### Hook Installation Logic

```python
import shutil
import stat

def install_hook():
    """Install the nWave TDD pre-commit hook."""
    source = "nWave/hooks/pre_commit_tdd_phases.py"
    hook_path = get_hook_path()
    hooks_dir = os.path.dirname(hook_path)

    # Ensure hooks directory exists
    os.makedirs(hooks_dir, exist_ok=True)

    # Check if pre-commit already exists
    if os.path.exists(hook_path):
        # Read existing hook
        with open(hook_path, 'r', encoding='utf-8') as f:
            existing = f.read()

        # Check if already contains our hook
        if "nWave-TDD-PHASE-VALIDATION" in existing:
            print("✓ nWave hook already installed")
            return True

        # Append our hook call to existing
        with open(hook_path, 'a', encoding='utf-8') as f:
            f.write("\n\n# nWave TDD Phase Validation\n")
            f.write(f'python3 "{os.path.abspath(source)}" "$@"\n')
    else:
        # Create new hook that calls our Python script
        shebang = "#!/bin/sh" if os.name != 'nt' else ""
        with open(hook_path, 'w', encoding='utf-8') as f:
            if shebang:
                f.write(shebang + "\n")
            f.write("# nWave TDD Phase Validation\n")
            f.write(f'python3 "{os.path.abspath(source)}" "$@"\n')

    # Make executable (Unix only)
    if os.name != 'nt':
        st = os.stat(hook_path)
        os.chmod(hook_path, st.st_mode | stat.S_IEXEC)

    print("✓ nWave pre-commit hook installed")
    return True
```

### Skip Warning

If user selects [2]:
```
⚠️ WARNING: Without the hook, commits with incomplete TDD phases are possible.
   The review process will still catch these, but earlier detection is better.

   You can install later with: /nw:develop --install-hook
```
```

**Aggiunta - Validazione fasi in Phase 7**:

```python
def validate_all_phases_executed(step_file_path):
    """
    Validate ALL phases are executed, not just COMMIT.
    Returns dict with validation result and details.
    """
    import json

    with open(step_file_path, 'r', encoding='utf-8') as f:
        step_data = json.load(f)

    phase_log = step_data.get('tdd_cycle', {}).get('phase_execution_log', [])

    required_phases = [
        "PREPARE",
        "RED_ACCEPTANCE",
        "RED_UNIT",
        "GREEN_UNIT",
        "CHECK_ACCEPTANCE",
        "GREEN_ACCEPTANCE",
        "REVIEW",
        "REFACTOR_L1",
        "REFACTOR_L2",
        "REFACTOR_L3",
        "REFACTOR_L4",
        "POST_REFACTOR_REVIEW",
        "FINAL_VALIDATE",
        "COMMIT"
    ]

    missing_phases = []
    incomplete_phases = []
    in_progress_phases = []
    blocked_phases = []
    last_executed_phase = None
    last_executed_index = -1

    for i, phase_name in enumerate(required_phases):
        phase_entry = next(
            (p for p in phase_log if p.get('phase_name') == phase_name),
            None
        )

        if not phase_entry:
            missing_phases.append(phase_name)
        else:
            status = phase_entry.get('status', 'NOT_EXECUTED')

            if status == 'NOT_EXECUTED':
                incomplete_phases.append(phase_name)
            elif status == 'IN_PROGRESS':
                in_progress_phases.append(phase_name)
            elif status == 'BLOCKED':
                blocked_phases.append({
                    'phase': phase_name,
                    'blocked_by': phase_entry.get('blocked_by', 'Unknown')
                })
            elif status == 'EXECUTED':
                last_executed_phase = phase_name
                last_executed_index = i

    # Determine first phase to resume from
    resume_from = None
    if in_progress_phases:
        resume_from = in_progress_phases[0]
    elif incomplete_phases:
        resume_from = incomplete_phases[0]
    elif missing_phases:
        resume_from = missing_phases[0]

    # Check for gaps (executed phases after non-executed)
    gaps = []
    for i, phase_name in enumerate(required_phases):
        phase_entry = next(
            (p for p in phase_log if p.get('phase_name') == phase_name),
            None
        )
        if phase_entry and phase_entry.get('status') == 'EXECUTED':
            if i > last_executed_index + 1:
                # There's a gap - phases were skipped
                for j in range(last_executed_index + 1, i):
                    gaps.append(required_phases[j])
            last_executed_index = i

    is_valid = (
        not missing_phases and
        not incomplete_phases and
        not in_progress_phases and
        not gaps
    )

    return {
        "valid": is_valid,
        "missing_phases": missing_phases,
        "incomplete_phases": incomplete_phases,
        "in_progress_phases": in_progress_phases,
        "blocked_phases": blocked_phases,
        "gaps": gaps,
        "last_executed_phase": last_executed_phase,
        "resume_from": resume_from,
        "total_phases": len(required_phases),
        "executed_count": len(required_phases) - len(missing_phases) - len(incomplete_phases) - len(in_progress_phases)
    }
```

**Utilizzo nella validazione post-step**:

```python
# After step execution, validate completeness
validation = validate_all_phases_executed(step_file)

if not validation['valid']:
    print(f"\n❌ Step {step_id} incomplete!")
    print(f"   Executed: {validation['executed_count']}/{validation['total_phases']} phases")

    if validation['in_progress_phases']:
        print(f"   ⚠️ Phases left IN_PROGRESS: {validation['in_progress_phases']}")

    if validation['incomplete_phases']:
        print(f"   ⚠️ Phases NOT_EXECUTED: {validation['incomplete_phases']}")

    if validation['gaps']:
        print(f"   ⚠️ Gaps detected (phases skipped): {validation['gaps']}")

    if validation['blocked_phases']:
        print(f"   ⚠️ Blocked phases: {validation['blocked_phases']}")

    print(f"\n   Resume from: {validation['resume_from']}")
    print(f"   Command: /nw:execute @software-crafter \"{step_file}\"")

    EXIT  # Stop execution
```

---

### 5. `nWave/tasks/nw/review.md`

**Obiettivo**: Aggiungere dimensione review per completezza fasi.

**Aggiunta sezione**:

```markdown
## Step/Implementation Review: Phase Completeness Validation

When reviewing artifacts of type `step` or `implementation`, MANDATORY phase validation.

### Validation Checklist

| Check | Description | Severity |
|-------|-------------|----------|
| All phases present | 14 entries in phase_execution_log | HIGH |
| No NOT_EXECUTED gaps | No phase NOT_EXECUTED between EXECUTED phases | HIGH |
| No IN_PROGRESS abandoned | No phase left with status IN_PROGRESS | HIGH |
| Sequential execution | Phases executed in valid_transitions order | MEDIUM |
| Timestamps coherent | ended_at > started_at for all EXECUTED phases | LOW |
| Artifacts documented | Each phase has artifacts_created or artifacts_modified | LOW |
| Test results recorded | Phases with tests have test_results populated | LOW |

### Validation Algorithm

```python
def validate_phase_completeness(step_data):
    """
    Validate phase completeness for review.
    Returns list of issues found.
    """
    issues = []
    phase_log = step_data.get('tdd_cycle', {}).get('phase_execution_log', [])

    required_phases = [
        "PREPARE", "RED_ACCEPTANCE", "RED_UNIT", "GREEN_UNIT",
        "CHECK_ACCEPTANCE", "GREEN_ACCEPTANCE", "REVIEW",
        "REFACTOR_L1", "REFACTOR_L2", "REFACTOR_L3", "REFACTOR_L4",
        "POST_REFACTOR_REVIEW", "FINAL_VALIDATE", "COMMIT"
    ]

    # Check all phases present
    if len(phase_log) != 14:
        issues.append({
            "check": "All phases present",
            "severity": "HIGH",
            "issue": f"Expected 14 phases, found {len(phase_log)}",
            "phases_found": [p.get('phase_name') for p in phase_log]
        })

    # Check no NOT_EXECUTED or IN_PROGRESS
    last_executed_idx = -1
    for i, phase_name in enumerate(required_phases):
        entry = next((p for p in phase_log if p.get('phase_name') == phase_name), None)

        if not entry:
            issues.append({
                "check": "Phase exists",
                "severity": "HIGH",
                "issue": f"Phase {phase_name} missing from log"
            })
            continue

        status = entry.get('status')

        if status == 'EXECUTED':
            # Check for gaps
            if last_executed_idx >= 0 and i > last_executed_idx + 1:
                skipped = required_phases[last_executed_idx + 1:i]
                issues.append({
                    "check": "No gaps",
                    "severity": "HIGH",
                    "issue": f"Phases skipped between {required_phases[last_executed_idx]} and {phase_name}",
                    "skipped_phases": skipped
                })
            last_executed_idx = i

            # Check timestamps
            started = entry.get('started_at')
            ended = entry.get('ended_at')
            if started and ended and ended < started:
                issues.append({
                    "check": "Timestamps coherent",
                    "severity": "LOW",
                    "issue": f"Phase {phase_name}: ended_at before started_at"
                })

        elif status == 'IN_PROGRESS':
            issues.append({
                "check": "No IN_PROGRESS abandoned",
                "severity": "HIGH",
                "issue": f"Phase {phase_name} left in IN_PROGRESS status"
            })

        elif status == 'NOT_EXECUTED':
            # Only issue if there are EXECUTED phases after this
            later_executed = any(
                next((p for p in phase_log if p.get('phase_name') == later_phase), {}).get('status') == 'EXECUTED'
                for later_phase in required_phases[i+1:]
            )
            if later_executed:
                issues.append({
                    "check": "No NOT_EXECUTED gaps",
                    "severity": "HIGH",
                    "issue": f"Phase {phase_name} NOT_EXECUTED but later phases are EXECUTED"
                })

    return issues
```

### Review Decision Based on Phase Validation

```yaml
if HIGH_severity_issues:
  approval_status: REJECTED
  rejection_reason: "TDD phase completeness validation failed"
  ready_for_execution: false
  recovery_instruction: "Resume from phase: {first_issue_phase}"

elif MEDIUM_severity_issues:
  approval_status: NEEDS_REVISION
  revision_required: "Fix phase tracking issues before proceeding"
  ready_for_execution: false

else:
  # Proceed with normal review criteria
  approval_status: <based on other review dimensions>
```
```

---

### 6. `nWave/agents/software-crafter.toon`

**Obiettivo**: Aggiungere principio e protocollo esplicito.

**Aggiunte**:

```
## CORE_PRINCIPLES
→ Phase Tracking Discipline: Update step file IMMEDIATELY after each TDD phase

## TDD_EXECUTION_PROTOCOL
MANDATORY for each of the 14 TDD phases:

1. BEFORE starting phase:
   - Read step file
   - Find phase in phase_execution_log by phase_name
   - Set status: "IN_PROGRESS"
   - Set started_at: current timestamp
   - SAVE step file

2. EXECUTE phase work

3. AFTER completing phase:
   - Set status: "EXECUTED" (or "BLOCKED" if cannot complete)
   - Set ended_at: current timestamp
   - Calculate and set duration_minutes
   - Set outcome: "PASS" or "FAIL"
   - Populate artifacts_created, artifacts_modified
   - Populate test_results if applicable
   - Add notes if relevant
   - SAVE step file IMMEDIATELY

4. Only THEN proceed to next phase

VIOLATIONS:
- Batching updates → VIOLATION
- Skipping phases → VIOLATION
- Leaving IN_PROGRESS → VIOLATION
- Forgetting to save → VIOLATION

The pre-commit hook WILL block commits with incomplete phases.
```

---

### 7. `nWave/agents/software-crafter-reviewer.toon`

**Obiettivo**: Aggiungere dimensione review per completezza fasi.

**Aggiunte**:

```
## REVIEW_DIMENSIONS
phase_completeness:
  question: Are all TDD phases executed and documented?
  severity: HIGH (blocks approval)
  check_items:
    - All 14 phases present in phase_execution_log
    - No phase with status "NOT_EXECUTED" (except if all after it are also NOT_EXECUTED)
    - No phase with status "IN_PROGRESS" (indicates abandoned execution)
    - No gaps (NOT_EXECUTED between EXECUTED phases)
    - Timestamps present and coherent (ended_at > started_at)
    - Phases executed in valid sequential order
  threshold: Any violation → REJECTED
  recovery: "Resume from phase: {first_incomplete_phase}"
```

---

### 8. `nWave/hooks/pre_commit_tdd_phases.py` (NUOVO FILE)

**Obiettivo**: Script Python cross-platform per validazione pre-commit.

```python
#!/usr/bin/env python3
"""
nWave-TDD-PHASE-VALIDATION
Pre-commit hook to enforce TDD phase completeness.

Cross-platform: Works on Windows, Mac, and Linux.
No external dependencies beyond Python standard library.

Installed by /nw:develop command.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# Required TDD phases in order
REQUIRED_PHASES = [
    "PREPARE",
    "RED_ACCEPTANCE",
    "RED_UNIT",
    "GREEN_UNIT",
    "CHECK_ACCEPTANCE",
    "GREEN_ACCEPTANCE",
    "REVIEW",
    "REFACTOR_L1",
    "REFACTOR_L2",
    "REFACTOR_L3",
    "REFACTOR_L4",
    "POST_REFACTOR_REVIEW",
    "FINAL_VALIDATE",
    "COMMIT",
]


def get_staged_step_files() -> List[str]:
    """Get list of step files staged for commit."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            check=True,
        )
        files = result.stdout.strip().split("\n")

        # Filter for step files (pattern: steps/XX-XX.json)
        step_pattern = re.compile(r"steps/\d+-\d+\.json$")
        step_files = [f for f in files if f and step_pattern.search(f)]

        return step_files
    except subprocess.CalledProcessError:
        return []


def validate_step_file(file_path: str) -> Tuple[bool, List[Dict]]:
    """
    Validate a step file has all TDD phases executed.

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return False, [{"phase": "N/A", "issue": f"Cannot read file: {e}"}]

    # Get phase execution log
    phase_log = data.get("tdd_cycle", {}).get("phase_execution_log", [])

    if not phase_log:
        return False, [{"phase": "N/A", "issue": "No phase_execution_log found"}]

    # Build lookup by phase name
    phase_lookup = {p.get("phase_name"): p for p in phase_log}

    last_executed_index = -1

    for i, phase_name in enumerate(REQUIRED_PHASES):
        entry = phase_lookup.get(phase_name)

        if not entry:
            issues.append({
                "phase": phase_name,
                "status": "MISSING",
                "issue": "Phase not found in log"
            })
            continue

        status = entry.get("status", "NOT_EXECUTED")

        if status == "EXECUTED":
            # Check for gaps
            if last_executed_index >= 0 and i > last_executed_index + 1:
                for j in range(last_executed_index + 1, i):
                    skipped_phase = REQUIRED_PHASES[j]
                    if skipped_phase not in [iss["phase"] for iss in issues]:
                        issues.append({
                            "phase": skipped_phase,
                            "status": "SKIPPED",
                            "issue": f"Skipped (gap between {REQUIRED_PHASES[last_executed_index]} and {phase_name})"
                        })
            last_executed_index = i

        elif status == "IN_PROGRESS":
            issues.append({
                "phase": phase_name,
                "status": "IN_PROGRESS",
                "issue": "Phase left in progress (incomplete execution)"
            })

        elif status == "NOT_EXECUTED":
            issues.append({
                "phase": phase_name,
                "status": "NOT_EXECUTED",
                "issue": "Phase not executed"
            })

        elif status == "BLOCKED":
            blocked_by = entry.get("blocked_by", "Unknown reason")
            issues.append({
                "phase": phase_name,
                "status": "BLOCKED",
                "issue": f"Phase blocked: {blocked_by}"
            })

    return len(issues) == 0, issues


def print_validation_result(file_path: str, is_valid: bool, issues: List[Dict]) -> None:
    """Print validation result for a file."""
    print(f"\n  Checking: {file_path}")

    if is_valid:
        print("    ✓ All 14 phases completed")
    else:
        for issue in issues:
            phase = issue["phase"]
            status = issue.get("status", "?")
            issue_text = issue["issue"]
            print(f"    ✗ {phase}: {status} - {issue_text}")


def main() -> int:
    """Main entry point."""
    print("🔍 nWave TDD Phase Validation...")

    # Get staged step files
    step_files = get_staged_step_files()

    if not step_files:
        print("  ✓ No step files in commit")
        return 0

    print(f"  Found {len(step_files)} step file(s) to validate")

    # Validate each file
    all_valid = True
    failed_files = []

    for file_path in step_files:
        is_valid, issues = validate_step_file(file_path)
        print_validation_result(file_path, is_valid, issues)

        if not is_valid:
            all_valid = False
            failed_files.append({
                "file": file_path,
                "issues": issues
            })

    # Final result
    if all_valid:
        print("\n✓ TDD phase validation passed")
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ COMMIT BLOCKED: TDD phases incomplete")
        print("=" * 60)

        print("\nFiles with incomplete phases:")
        for failed in failed_files:
            print(f"\n  {failed['file']}:")

            # Group issues by type
            not_executed = [i for i in failed["issues"] if i.get("status") == "NOT_EXECUTED"]
            in_progress = [i for i in failed["issues"] if i.get("status") == "IN_PROGRESS"]
            blocked = [i for i in failed["issues"] if i.get("status") == "BLOCKED"]

            if in_progress:
                print(f"    IN_PROGRESS: {', '.join(i['phase'] for i in in_progress)}")
            if not_executed:
                print(f"    NOT_EXECUTED: {', '.join(i['phase'] for i in not_executed)}")
            if blocked:
                print(f"    BLOCKED: {', '.join(i['phase'] for i in blocked)}")

            # Suggest resume point
            first_issue = failed["issues"][0] if failed["issues"] else None
            if first_issue:
                print(f"    Resume from: {first_issue['phase']}")

        print("\n" + "-" * 60)
        print("To fix:")
        print("  1. Complete the missing TDD phases")
        print("  2. Update the step file with phase status")
        print("  3. Stage changes: git add <step-file>")
        print("  4. Try commit again")
        print("\nTo bypass (NOT RECOMMENDED):")
        print("  git commit --no-verify")
        print("=" * 60)

        return 1


if __name__ == "__main__":
    sys.exit(main())
```

---

### 9. `nWave/hooks/README.md` (NUOVO FILE)

```markdown
# nWave Git Hooks

This directory contains git hooks for the nWave development methodology.

## Available Hooks

### pre_commit_tdd_phases.py

**Purpose**: Validates that all TDD phases are completed before allowing commits on step files.

**Language**: Python 3 (cross-platform: Windows, Mac, Linux)

**Dependencies**: None (uses only Python standard library)

**Installation**:
- **Automatic**: Run `/nw:develop` and accept the hook installation prompt
- **Manual**:
  ```bash
  # Unix/Mac
  cp nWave/hooks/pre_commit_tdd_phases.py .git/hooks/pre-commit
  chmod +x .git/hooks/pre-commit

  # Windows (in .git/hooks/pre-commit)
  #!/bin/sh
  python3 "nWave/hooks/pre_commit_tdd_phases.py" "$@"
  ```

**What it validates**:
- All 14 TDD phases present in step files
- All phases have status "EXECUTED"
- No phases left "IN_PROGRESS" (indicates interrupted execution)
- No phases left "NOT_EXECUTED" (indicates skipped phases)
- No gaps in phase sequence

**Bypass** (not recommended):
```bash
git commit --no-verify
```

## Hook Architecture

```
Commit Attempt
     │
     ▼
┌─────────────────────────────┐
│  .git/hooks/pre-commit      │
│  (shell wrapper)            │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  pre_commit_tdd_phases.py   │
│  (Python validation)        │
├─────────────────────────────┤
│  1. Get staged step files   │
│  2. For each step file:     │
│     - Load JSON             │
│     - Check all 14 phases   │
│     - Verify EXECUTED status│
│  3. Block if incomplete     │
└──────────────┬──────────────┘
               │
     ┌─────────┴─────────┐
     │                   │
  ALL OK            INCOMPLETE
     │                   │
     ▼                   ▼
  COMMIT OK        ❌ BLOCKED
                   (exit code 1)
```

## Troubleshooting

### "Python not found"

The hook requires Python 3. Ensure `python3` is in your PATH:
```bash
python3 --version
```

### Hook not running

Verify the hook is executable:
```bash
# Unix/Mac
ls -la .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Windows
# Ensure the file exists and contains proper shebang
```

### False positives

If the hook blocks a valid commit:
1. Check the step file JSON is valid
2. Verify all phases have `status: "EXECUTED"`
3. Check for typos in phase names

## Adding New Hooks

To add a new nWave hook:
1. Create Python script in `nWave/hooks/`
2. Document in this README
3. Add installation logic to relevant `/nw:*` command
```

---

## Flusso Completo Aggiornato

```
┌──────────────────────────────────────────────────────────────────┐
│ /nw:develop "feature"                                            │
├──────────────────────────────────────────────────────────────────┤
│ Phase 0: Pre-Commit Hook Check                                   │
│   │                                                              │
│   ├── Hook installed? ─── YES ──→ Continue to Phase 1            │
│   │                                                              │
│   └── Hook missing? ────→ AskUserQuestion:                       │
│                            │                                     │
│                            ├── [1] Install (Recommended)         │
│                            │      └── Copy hook + make executable│
│                            │          └── Continue to Phase 1    │
│                            │                                     │
│                            ├── [2] Skip                          │
│                            │      └── Warning message            │
│                            │          └── Continue to Phase 1    │
│                            │                                     │
│                            └── [3] Show code                     │
│                                   └── Display hook source        │
│                                       └── Re-prompt              │
├──────────────────────────────────────────────────────────────────┤
│ Phase 1-6: Setup, Baseline, Roadmap, Split, Reviews              │
│   └── /nw:split generates step files with 14 pre-populated phases│
├──────────────────────────────────────────────────────────────────┤
│ Phase 7: Execute Steps                                           │
│   │                                                              │
│   └── For each step file:                                        │
│       │                                                          │
│       ├── Agent executes phase                                   │
│       │   └── Updates phase_execution_log IMMEDIATELY            │
│       │       └── status: IN_PROGRESS → EXECUTED                 │
│       │           └── SAVE step file                             │
│       │                                                          │
│       ├── After all 14 phases:                                   │
│       │   └── validate_all_phases_executed()                     │
│       │       │                                                  │
│       │       ├── Valid ──→ Continue                             │
│       │       └── Invalid ──→ ERROR + resume_from                │
│       │                                                          │
│       └── COMMIT phase triggers:                                 │
│           └── git commit                                         │
│               │                                                  │
│               └── PRE-COMMIT HOOK (Python)                       │
│                   │                                              │
│                   ├── All phases EXECUTED ──→ Commit OK          │
│                   └── Any incomplete ──→ ❌ BLOCKED              │
│                       └── Show missing phases                    │
│                           └── Resume instruction                 │
├──────────────────────────────────────────────────────────────────┤
│ Phase 8: Finalize                                                │
└──────────────────────────────────────────────────────────────────┘
```

---

## Nuovi File da Creare

### 10. `nWave/scripts/migrate_step_files.py`

**Obiettivo**: Migrare step file esistenti aggiungendo le fasi pre-popolate.

```python
#!/usr/bin/env python3
"""
Migrate existing step files to include pre-populated TDD phases.

Usage:
    python migrate_step_files.py [--dry-run] [path/to/steps/]

Options:
    --dry-run    Show what would be changed without modifying files
    path         Directory containing step files (default: auto-detect)
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


REQUIRED_PHASES = [
    "PREPARE", "RED_ACCEPTANCE", "RED_UNIT", "GREEN_UNIT",
    "CHECK_ACCEPTANCE", "GREEN_ACCEPTANCE", "REVIEW",
    "REFACTOR_L1", "REFACTOR_L2", "REFACTOR_L3", "REFACTOR_L4",
    "POST_REFACTOR_REVIEW", "FINAL_VALIDATE", "COMMIT",
]


def create_phase_skeleton() -> List[Dict[str, Any]]:
    """Create the pre-populated phase skeleton."""
    return [
        {
            "phase_name": phase,
            "phase_index": i,
            "status": "NOT_EXECUTED",
            "started_at": None,
            "ended_at": None,
            "duration_minutes": None,
            "outcome": None,
            "outcome_details": None,
            "artifacts_created": [],
            "artifacts_modified": [],
            "test_results": {"total": None, "passed": None, "failed": None, "skipped": None},
            "notes": None,
            "blocked_by": None
        }
        for i, phase in enumerate(REQUIRED_PHASES)
    ]


def needs_migration(step_data: Dict) -> bool:
    """Check if a step file needs migration."""
    phase_log = step_data.get("tdd_cycle", {}).get("phase_execution_log", [])
    return not phase_log or len(phase_log) < len(REQUIRED_PHASES)


def migrate_step_file(step_data: Dict) -> Dict:
    """Migrate a step file to include pre-populated phases."""
    if "tdd_cycle" not in step_data:
        step_data["tdd_cycle"] = {}

    existing_log = step_data["tdd_cycle"].get("phase_execution_log", [])
    new_log = create_phase_skeleton()

    # Preserve existing phase data
    existing_by_name = {p.get("phase_name"): p for p in existing_log}
    for phase in new_log:
        if phase["phase_name"] in existing_by_name:
            existing = existing_by_name[phase["phase_name"]]
            for key in existing:
                if existing.get(key) is not None:
                    phase[key] = existing[key]

    step_data["tdd_cycle"]["phase_execution_log"] = new_log
    step_data["_migration"] = {
        "migrated_at": datetime.utcnow().isoformat() + "Z",
        "migrated_by": "migrate_step_files.py",
        "previous_phase_count": len(existing_log)
    }
    return step_data


def main():
    parser = argparse.ArgumentParser(description="Migrate step files")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("path", nargs="?", default=".")
    args = parser.parse_args()

    # Find and migrate step files
    # ... (implementation as shown in full spec)
    pass

if __name__ == "__main__":
    sys.exit(main())
```

---

### 11. `nWave/scripts/validate_tdd_phases_ci.py`

**Obiettivo**: Script per validazione in CI/CD pipelines.

```python
#!/usr/bin/env python3
"""
Validate TDD phase completeness for CI/CD pipelines.

Usage:
    python validate_tdd_phases_ci.py [--strict] [--json] [path]

Exit codes:
    0 - All validations passed
    1 - Validation failures found
    2 - Configuration/runtime error

Integration Examples:

GitHub Actions:
    - name: Validate TDD Phases
      run: python nWave/scripts/validate_tdd_phases_ci.py docs/feature/*/steps/

GitLab CI:
    validate_tdd:
      script:
        - python nWave/scripts/validate_tdd_phases_ci.py

Azure Pipelines:
    - script: python nWave/scripts/validate_tdd_phases_ci.py
      displayName: 'Validate TDD Phases'
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


REQUIRED_PHASES = [
    "PREPARE", "RED_ACCEPTANCE", "RED_UNIT", "GREEN_UNIT",
    "CHECK_ACCEPTANCE", "GREEN_ACCEPTANCE", "REVIEW",
    "REFACTOR_L1", "REFACTOR_L2", "REFACTOR_L3", "REFACTOR_L4",
    "POST_REFACTOR_REVIEW", "FINAL_VALIDATE", "COMMIT",
]


def validate_step_file(file_path: Path, strict: bool = False) -> Tuple[bool, List[Dict]]:
    """Validate a single step file."""
    issues = []
    # ... validation logic checking:
    # - All phases present
    # - Status is EXECUTED or valid SKIPPED (with blocked_by)
    # - No IN_PROGRESS or NOT_EXECUTED
    # - SKIPPED requires blocked_by with valid prefix
    return len(issues) == 0, issues


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="Fail on SKIPPED too")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("path", nargs="?", default=".")
    args = parser.parse_args()

    # Find files, validate, output results
    # ... (implementation)
    pass

if __name__ == "__main__":
    sys.exit(main())
```

---

### Aggiornamento Hook: Bypass Logging

Aggiungere a `pre_commit_tdd_phases.py`:

```python
BYPASS_LOG_FILE = ".git/nwave-bypass.log"

def log_bypass_attempt(reason: str, files: List[str]) -> None:
    """Log when validation would be bypassed."""
    import subprocess
    from datetime import datetime

    try:
        user = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True, text=True
        ).stdout.strip() or "unknown"

        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True
        ).stdout.strip() or "unknown"

        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "user": user,
            "branch": branch,
            "reason": reason,
            "files": files
        }

        with open(BYPASS_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception:
        pass  # Silent fail


def check_for_recent_bypasses() -> List[Dict]:
    """Check for recent bypass attempts (for /nw:develop warning)."""
    try:
        if not os.path.exists(BYPASS_LOG_FILE):
            return []
        with open(BYPASS_LOG_FILE, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()][-5:]
    except Exception:
        return []
```

---

## Regole SKIPPED (Decisione Presa)

### Quando SKIPPED è Permesso

Una fase può avere `status: "SKIPPED"` SOLO se `blocked_by` contiene una motivazione con prefisso valido:

| Prefisso | Significato | Esempio |
|----------|-------------|---------|
| `BLOCKED_BY_DEPENDENCY:` | Dipendenza esterna non disponibile | `BLOCKED_BY_DEPENDENCY: Redis server not running` |
| `NOT_APPLICABLE:` | Fase non applicabile | `NOT_APPLICABLE: No unit tests for config-only change` |
| `DEFERRED:` | Posticipata con giustificazione | `DEFERRED: Will address in follow-up PR` |
| `APPROVED_SKIP:` | Skip approvato esplicitamente | `APPROVED_SKIP: Tech Lead Alice approved` |

### Validazione SKIPPED

```python
def validate_skipped_phase(entry: Dict) -> Tuple[bool, str]:
    blocked_by = entry.get("blocked_by", "")
    if not blocked_by:
        return False, "SKIPPED without blocked_by reason"

    valid_prefixes = ["BLOCKED_BY_DEPENDENCY:", "NOT_APPLICABLE:", "DEFERRED:", "APPROVED_SKIP:"]
    if not any(blocked_by.startswith(p) for p in valid_prefixes):
        return False, f"Invalid reason format: {blocked_by}"

    return True, "OK"
```

---

## Flusso Completo Finale

```
┌──────────────────────────────────────────────────────────────────┐
│ /nw:develop "feature"                                            │
├──────────────────────────────────────────────────────────────────┤
│ Phase 0: Hook Check                                              │
│   ├── Check bypass log → Warn if recent bypasses                 │
│   ├── Hook installed? → Continue                                 │
│   └── Hook missing? → Prompt [Install/Skip/Show]                 │
├──────────────────────────────────────────────────────────────────┤
│ Phase 1-6: Setup, Roadmap, Split                                 │
│   └── Split generates steps with 14 pre-populated phases         │
├──────────────────────────────────────────────────────────────────┤
│ Phase 7: Execute Steps                                           │
│   └── For each step:                                             │
│       ├── Execute phases, update JSON after EACH phase           │
│       ├── If cannot complete → SKIPPED + blocked_by: "PREFIX:..."│
│       ├── Validate all phases (EXECUTED or valid SKIPPED)        │
│       └── COMMIT → Hook validates → Log bypass if --no-verify    │
├──────────────────────────────────────────────────────────────────┤
│ CI/CD (optional)                                                 │
│   └── validate_tdd_phases_ci.py [--strict]                       │
├──────────────────────────────────────────────────────────────────┤
│ Phase 8: Finalize                                                │
└──────────────────────────────────────────────────────────────────┘
```

---

## Piano Implementazione

| Fase | File | Priorità |
|------|------|----------|
| 1 | `step-tdd-cycle-schema.json` | ALTA - Base strutturale |
| 2 | `pre_commit_tdd_phases.py` | ALTA - Core enforcement |
| 3 | `migrate_step_files.py` | MEDIA - Retrocompatibilità |
| 4 | `develop.md` | ALTA - Hook integration |
| 5 | `split.md` | ALTA - Generazione conforme |
| 6 | `execute.md` | MEDIA - Istruzioni agente |
| 7 | `validate_tdd_phases_ci.py` | MEDIA - CI integration |
| 8 | `review.md` | MEDIA - Review dimension |
| 9 | `software-crafter.toon` | MEDIA - Principi agente |
| 10 | `software-crafter-reviewer.toon` | MEDIA - Review agente |
| 11 | `README.md` (hooks) | BASSA - Documentazione |

---

*Piano aggiornato: 2026-01-14*
*Stato: PRONTO PER IMPLEMENTAZIONE*
*Decisioni: Tutte prese e documentate*
