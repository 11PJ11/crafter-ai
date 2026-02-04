# DES (Deterministic Execution System) - Piano di Test Esplorativo

**Data:** 2026-02-04
**Versione:** 1.0
**Tester:** Lyra (AI Test Assistant)
**Obiettivo:** Verificare funzionamento completo del DES dopo installazione

---

## 1. Obiettivi del Test

### 1.1 Obiettivi Primari
- ✅ Verificare che gli hook DES siano correttamente installati e funzionanti
- ✅ Validare che PreToolUse hook filtri correttamente le invocazioni Task
- ✅ Validare che SubagentStop hook esegua validazioni post-esecuzione
- ✅ Verificare conformità a CLAUDE.md: tutte le Task devono avere max_turns esplicito
- ✅ Testare casi di validazione positiva (dovrebbero passare)
- ✅ Testare casi di validazione negativa (dovrebbero fallire)

### 1.2 Aree di Test
1. **Hook Installation & Configuration**
2. **PreToolUse Hook Behavior**
3. **SubagentStop Hook Behavior**
4. **max_turns Compliance**
5. **Validation Gates**
6. **Error Handling & Recovery**

---

## 2. Test Suite: Hook Installation & Configuration

### TC-001: Verificare installazione hook in settings
**Obiettivo:** Confermare che gli hook siano configurati in ~/.claude/settings.local.json

**Passi:**
1. Leggere ~/.claude/settings.local.json
2. Verificare presenza sezione "hooks"
3. Verificare presenza hook "PreToolUse"
4. Verificare presenza hook "SubagentStop"

**Criteri di successo:**
- ✅ File settings.local.json esiste
- ✅ Sezione hooks è presente
- ✅ PreToolUse hook configurato con matcher "Task"
- ✅ SubagentStop hook configurato
- ✅ Comandi Python puntano a moduli DES corretti

**Dati attesi:**
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Task",
      "command": "PYTHONPATH=/home/alexd/.claude/lib/python python3 -m des.adapters.drivers.hooks.claude_code_hook_adapter pre-task"
    }],
    "SubagentStop": [{
      "command": "PYTHONPATH=/home/alexd/.claude/lib/python python3 -m des.adapters.drivers.hooks.claude_code_hook_adapter subagent-stop"
    }]
  }
}
```

---

### TC-002: Verificare moduli hook esistono e sono importabili
**Obiettivo:** Confermare che i moduli Python DES siano installati e importabili

**Passi:**
1. Verificare esistenza file ~/.claude/lib/python/des/adapters/drivers/hooks/claude_code_hook_adapter.py
2. Tentare import del modulo
3. Verificare presenza funzioni principali

**Criteri di successo:**
- ✅ File claude_code_hook_adapter.py esiste
- ✅ Modulo è importabile senza errori
- ✅ Funzione/classe per pre-task presente
- ✅ Funzione/classe per subagent-stop presente

**Comando test:**
```bash
PYTHONPATH=~/.claude/lib/python python3 -c "from des.adapters.drivers.hooks.claude_code_hook_adapter import *; print('OK')"
```

---

## 3. Test Suite: PreToolUse Hook Behavior

### TC-003: Hook attivazione con marker DES
**Obiettivo:** Verificare che PreToolUse hook si attivi SOLO per Task con marker DES

**Scenario 1: Task CON marker DES (dovrebbe validare)**
```python
Task(
    subagent_type="Explore",
    prompt="""
    <!-- DES-VALIDATION: required -->
    <!-- DES-ORIGIN: command:/nw:execute -->

    Find all Python files
    """,
    max_turns=10
)
```

**Scenario 2: Task SENZA marker DES (dovrebbe ignorare)**
```python
Task(
    subagent_type="Explore",
    prompt="Find all Python files",
    max_turns=10
)
```

**Criteri di successo:**
- ✅ Scenario 1: Hook esegue validazione
- ✅ Scenario 2: Hook passa attraverso senza validazione
- ✅ Log/output distingue i due casi

---

### TC-004: Validazione prompt con sezioni mancanti
**Obiettivo:** Verificare che hook blocchi Task con prompt incompleti

**Prompt invalido (mancante TIMEOUT_INSTRUCTION):**
```markdown
<!-- DES-VALIDATION: required -->
<!-- DES-STEP-FILE: test.json -->

## AGENT_IDENTITY
You are a test agent

## TASK_CONTEXT
Test task

## TDD_14_PHASES
All 14 phases listed...

<!-- MANCANTE: TIMEOUT_INSTRUCTION -->
```

**Criteri di successo:**
- ✅ Hook rileva sezione mancante
- ✅ Task invocation viene bloccata
- ✅ Messaggio errore chiaro indica sezione mancante
- ✅ Audit log registra tentativo bloccato

---

### TC-005: Validazione step file path
**Obiettivo:** Verificare che hook validi esistenza step file

**Scenario 1: Step file esiste**
```markdown
<!-- DES-VALIDATION: required -->
<!-- DES-STEP-FILE: docs/feature/test/steps/01-01.json -->
```

**Scenario 2: Step file NON esiste**
```markdown
<!-- DES-VALIDATION: required -->
<!-- DES-STEP-FILE: /path/inesistente/step.json -->
```

**Criteri di successo:**
- ✅ Scenario 1: Validazione passa
- ✅ Scenario 2: Validazione fallisce con errore "step file not found"

---

## 4. Test Suite: SubagentStop Hook Behavior

### TC-006: Hook attivazione dopo completamento sub-agent
**Obiettivo:** Verificare che SubagentStop hook si attivi dopo ogni Task completato

**Passi:**
1. Eseguire Task semplice che completa con successo
2. Monitorare se hook viene chiamato
3. Verificare che riceva context corretto

**Criteri di successo:**
- ✅ Hook viene chiamato dopo Task completa
- ✅ Hook riceve agent_id corretto
- ✅ Hook riceve agent_transcript_path valido
- ✅ Log mostra esecuzione hook

---

### TC-007: Validazione step file con fasi IN_PROGRESS abbandonate
**Obiettivo:** Verificare rilevamento fasi abbandonate

**Step file con fase IN_PROGRESS:**
```json
{
  "task_id": "test-001",
  "tdd_cycle": {
    "phase_execution_log": [
      {
        "phase_name": "PREPARE",
        "status": "IN_PROGRESS",
        "started_at": "2026-02-04T10:00:00Z"
      }
    ]
  }
}
```

**Criteri di successo:**
- ✅ Hook rileva fase IN_PROGRESS
- ✅ Errore registrato: "Phase PREPARE left IN_PROGRESS (abandoned)"
- ✅ Workflow bloccato (exit code 1)
- ✅ Audit log contiene evento SUBAGENT_STOP_VALIDATION con errore

---

### TC-008: Validazione fase EXECUTED senza outcome
**Obiettivo:** Verificare che fasi EXECUTED abbiano outcome obbligatorio

**Step file con EXECUTED senza outcome:**
```json
{
  "tdd_cycle": {
    "phase_execution_log": [
      {
        "phase_name": "RED_UNIT",
        "status": "EXECUTED",
        "started_at": "...",
        "ended_at": "..."
        // MANCANTE: "outcome"
      }
    ]
  }
}
```

**Criteri di successo:**
- ✅ Hook rileva outcome mancante
- ✅ Errore: "Phase RED_UNIT EXECUTED without outcome"

---

### TC-009: Validazione fase SKIPPED con blocked_by
**Obiettivo:** Verificare regole per fasi SKIPPED

**Scenario 1: SKIPPED con prefisso valido**
```json
{
  "phase_name": "REFACTOR_L4",
  "status": "SKIPPED",
  "blocked_by": "NOT_APPLICABLE: No refactoring needed"
}
```

**Scenario 2: SKIPPED con prefisso DEFERRED (blocca commit)**
```json
{
  "phase_name": "REFACTOR_L4",
  "status": "SKIPPED",
  "blocked_by": "DEFERRED: Will do later"
}
```

**Scenario 3: SKIPPED senza blocked_by**
```json
{
  "phase_name": "REFACTOR_L4",
  "status": "SKIPPED"
  // MANCANTE: blocked_by
}
```

**Criteri di successo:**
- ✅ Scenario 1: Accettato, warning log
- ✅ Scenario 2: Warning "has DEFERRED - blocks commit"
- ✅ Scenario 3: Errore "SKIPPED without blocked_by"

---

## 5. Test Suite: max_turns Compliance

### TC-010: Scansione codebase per Task senza max_turns
**Obiettivo:** CRITICAL - Verificare conformità a CLAUDE.md

**Secondo CLAUDE.md:**
> **CRITICAL**: Always include `max_turns` when invoking the Task tool.

**Passi:**
1. Grep tutto il codebase per chiamate `Task(`
2. Identificare tutte le invocazioni
3. Verificare che OGNI invocazione abbia parametro `max_turns`

**Criteri di successo:**
- ✅ TUTTE le chiamate Task hanno max_turns esplicito
- ✅ Nessuna chiamata Task manca max_turns
- ✅ Valori max_turns appropriati per tipo task:
  - Quick edit: 15
  - Background task: 25
  - Standard task: 30
  - Research: 35
  - Complex refactoring: 50

**Comando test:**
```bash
# Find all Task invocations
grep -rn "Task(" --include="*.py" --include="*.md" src/ dist/ nWave/

# Check if max_turns is always present
```

---

### TC-011: Validazione valori max_turns
**Obiettivo:** Verificare che valori max_turns siano appropriati

**Regole da CLAUDE.md:**
- Quick edit → 15
- Background task → 25
- Standard task → 30
- Research → 35
- Complex refactoring → 50

**Criteri di successo:**
- ✅ Nessun valore max_turns troppo basso (< 10)
- ✅ Nessun valore max_turns eccessivo (> 100)
- ✅ Valori allineati con complessità task

---

## 6. Test Suite: Validation Gates

### TC-012: Gate 1 - Pre-Invocation Validation
**Obiettivo:** Test completo del gate pre-invocation

**Test Matrix:**

| Test ID | Marker DES | Sezioni complete | Step file esiste | Risultato atteso |
|---------|------------|------------------|------------------|------------------|
| G1-01   | ✅         | ✅               | ✅               | PASS             |
| G1-02   | ✅         | ❌               | ✅               | FAIL - Sezioni mancanti |
| G1-03   | ✅         | ✅               | ❌               | FAIL - Step file not found |
| G1-04   | ❌         | N/A              | N/A              | PASS (no validation) |

---

### TC-013: Gate 2 - SubagentStop Validation
**Obiettivo:** Test completo del gate post-execution

**Test Matrix:**

| Test ID | Fasi IN_PROGRESS | Fasi EXECUTED senza outcome | Fasi SKIPPED senza blocked_by | Risultato atteso |
|---------|------------------|-----------------------------|-----------------------------|------------------|
| G2-01   | 0                | 0                           | 0                           | PASS             |
| G2-02   | 1+               | 0                           | 0                           | FAIL - Abandoned |
| G2-03   | 0                | 1+                          | 0                           | FAIL - No outcome |
| G2-04   | 0                | 0                           | 1+                          | FAIL - No blocked_by |

---

## 7. Test Suite: Error Handling & Recovery

### TC-014: Gestione transcript path invalido
**Obiettivo:** Verificare comportamento quando agent_transcript_path non esiste

**Scenario:**
```json
{
  "agent_transcript_path": "/path/inesistente/agent.jsonl"
}
```

**Criteri di successo:**
- ✅ Hook non crasha
- ✅ Gestione errore graceful
- ✅ Log indica problema con transcript
- ✅ Ritorna status appropriato

---

### TC-015: Gestione step file JSON invalido
**Obiettivo:** Verificare parsing robusto

**Step file con JSON malformato:**
```json
{
  "task_id": "test",
  "tdd_cycle": {
    "phase_execution_log": [
      // Virgola trailing invalida
    ],
  }
}
```

**Criteri di successo:**
- ✅ Errore JSON parsing rilevato
- ✅ Messaggio errore chiaro
- ✅ Non crasha l'intero hook system

---

## 8. Test Suite: Audit Trail

### TC-016: Creazione audit logs
**Obiettivo:** Verificare che eventi siano loggati

**Eventi da verificare:**
- TASK_INVOCATION_VALIDATED
- TASK_INVOCATION_REJECTED
- SUBAGENT_STOP_VALIDATION

**Criteri di successo:**
- ✅ File audit-YYYY-MM-DD.log creato
- ✅ Eventi in formato JSONL
- ✅ Ogni evento ha timestamp
- ✅ Eventi contengono dati completi

---

## 9. Execution Plan

### Fase 1: Verifiche Statiche (30 min)
1. TC-001: Hook configuration
2. TC-002: Module importability
3. TC-010: max_turns compliance scan
4. TC-011: max_turns values validation

### Fase 2: Test Hook PreToolUse (45 min)
5. TC-003: Hook activation
6. TC-004: Missing sections
7. TC-005: Step file validation

### Fase 3: Test Hook SubagentStop (45 min)
8. TC-006: Hook activation
9. TC-007: IN_PROGRESS detection
10. TC-008: Missing outcome
11. TC-009: SKIPPED validation

### Fase 4: Integration Tests (30 min)
12. TC-012: Gate 1 matrix
13. TC-013: Gate 2 matrix

### Fase 5: Error Handling (20 min)
14. TC-014: Invalid transcript
15. TC-015: Invalid JSON

### Fase 6: Audit Trail (15 min)
16. TC-016: Log creation

**Tempo totale stimato:** ~3 ore

---

## 10. Report Template

### Per ogni test completato:

```markdown
## TC-XXX: [Nome Test]
**Status:** ✅ PASS / ❌ FAIL / ⚠️ WARNING
**Data esecuzione:** YYYY-MM-DD HH:MM
**Durata:** X minuti

### Risultato
[Descrizione outcome]

### Output/Log
```
[Output rilevante]
```

### Issues trovati
- [Issue 1]
- [Issue 2]

### Note aggiuntive
[Osservazioni]
```

---

## 11. Exit Criteria

Il test è considerato completato quando:
- ✅ Tutti i test TC-001 a TC-016 sono stati eseguiti
- ✅ Almeno 80% dei test critici PASS
- ✅ Tutti i FAIL sono documentati con root cause
- ✅ Report finale con raccomandazioni è prodotto

---

**Prepared by:** Lyra (AI Test Assistant)
**Reviewers:** TBD
**Approval:** Pending
