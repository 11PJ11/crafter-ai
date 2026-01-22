# Deterministic Execution System (DES) - Component Boundaries

**Version:** 1.0
**Date:** 2026-01-22
**Author:** Morgan (Solution Architect)
**Status:** DESIGN Wave Deliverable

---

## 1. Overview

This document defines the clear boundaries, interfaces, and responsibilities for each DES component. Following hexagonal architecture principles, each layer has explicit ports (interfaces) and adapters (implementations).

---

## 2. Layer 1: Command Filter

### 2.1 Purpose

Distinguish DES-managed Task invocations from ad-hoc exploration.

### 2.2 Responsibilities

| Responsibility | Description |
|----------------|-------------|
| Marker Detection | Detect `<!-- DES-VALIDATION: required -->` in prompts |
| Metadata Extraction | Extract origin, step file path from DES markers |
| Routing Decision | Determine if prompt requires validation |

### 2.3 Interface (Port)

```python
# nWave/ports/command_filter.py
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class DESMetadata:
    origin: str              # "command:/nw:execute" or "ad-hoc"
    step_file: str | None    # Path to step file if applicable
    requires_validation: bool # Whether validation gates apply

class CommandFilterPort(ABC):
    @abstractmethod
    def should_validate(self, prompt: str) -> bool:
        """Check if prompt requires DES validation."""
        pass

    @abstractmethod
    def extract_metadata(self, prompt: str) -> DESMetadata:
        """Extract DES metadata from prompt."""
        pass
```

### 2.4 Implementation (Adapter)

```python
# nWave/adapters/regex_command_filter.py
import re
from nWave.ports.command_filter import CommandFilterPort, DESMetadata

class RegexCommandFilter(CommandFilterPort):
    """Regex-based implementation of command filtering."""

    VALIDATION_MARKER = "<!-- DES-VALIDATION: required -->"
    ORIGIN_PATTERN = re.compile(r'<!-- DES-ORIGIN: (.+?) -->')
    STEP_FILE_PATTERN = re.compile(r'<!-- DES-STEP-FILE: (.+?) -->')

    def should_validate(self, prompt: str) -> bool:
        return self.VALIDATION_MARKER in prompt

    def extract_metadata(self, prompt: str) -> DESMetadata:
        origin_match = self.ORIGIN_PATTERN.search(prompt)
        step_match = self.STEP_FILE_PATTERN.search(prompt)

        return DESMetadata(
            origin=origin_match.group(1) if origin_match else "ad-hoc",
            step_file=step_match.group(1) if step_match else None,
            requires_validation=self.should_validate(prompt)
        )
```

### 2.5 Boundary Rules

| ALLOWED | FORBIDDEN |
|---------|-----------|
| Read prompt string | Modify prompt |
| Parse regex patterns | Make network calls |
| Return metadata | Access file system |
| Log decisions | Change step file state |

### 2.6 Command Registration

```yaml
# nWave/config/des-commands.yaml
validation_required:
  - command: "/nw:execute"
    full_validation: true
    step_file_required: true

  - command: "/nw:develop"
    full_validation: true
    step_file_required: true

validation_partial:
  - command: "/nw:baseline"
    validate_sections: [TASK_CONTEXT, BOUNDARY_RULES]

  - command: "/nw:split"
    validate_sections: [TASK_CONTEXT]

validation_none:
  - command: "/nw:research"
  - command: "/nw:review"
```

---

## 3. Layer 2: Template Engine

### 3.1 Purpose

Ensure all DES-managed prompts contain complete instructions.

### 3.2 Responsibilities

| Responsibility | Description |
|----------------|-------------|
| Template Loading | Load template from file system |
| Template Rendering | Substitute placeholders with step data |
| Section Validation | Verify all mandatory sections present |
| Phase Validation | Verify all 14 TDD phases enumerated |
| Error Reporting | Provide actionable error messages |

### 3.3 Interface (Port)

```python
# nWave/ports/template_engine.py
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class ValidationError:
    error_type: str    # "MISSING" | "INCOMPLETE" | "INVALID"
    element: str       # Name of missing/invalid element
    message: str       # Human-readable error message
    suggestion: str    # How to fix

@dataclass
class ValidationResult:
    valid: bool
    errors: list[ValidationError]
    warnings: list[str]

class TemplateEnginePort(ABC):
    @abstractmethod
    def load_template(self, template_name: str) -> str:
        """Load template content from file."""
        pass

    @abstractmethod
    def render_template(
        self,
        template: str,
        step_data: dict,
        agent_config: dict
    ) -> str:
        """Render template with step data."""
        pass

    @abstractmethod
    def validate_prompt(self, prompt: str) -> ValidationResult:
        """Validate prompt has all required sections."""
        pass
```

### 3.4 Implementation (Adapter)

```python
# nWave/adapters/markdown_template_engine.py
from pathlib import Path
from nWave.ports.template_engine import (
    TemplateEnginePort, ValidationResult, ValidationError
)

class MarkdownTemplateEngine(TemplateEnginePort):
    """Markdown-based template engine with section validation."""

    MANDATORY_SECTIONS = [
        "DES_METADATA",
        "AGENT_IDENTITY",
        "TASK_CONTEXT",
        "TDD_14_PHASES",
        "QUALITY_GATES",
        "OUTCOME_RECORDING",
        "BOUNDARY_RULES",
        "TIMEOUT_INSTRUCTION"
    ]

    REQUIRED_PHASES = [
        "PREPARE", "RED_ACCEPTANCE", "RED_UNIT", "GREEN_UNIT",
        "CHECK_ACCEPTANCE", "GREEN_ACCEPTANCE", "REVIEW",
        "REFACTOR_L1", "REFACTOR_L2", "REFACTOR_L3", "REFACTOR_L4",
        "POST_REFACTOR_REVIEW", "FINAL_VALIDATE", "COMMIT"
    ]

    TEMPLATE_DIR = Path("nWave/templates/prompt-templates")

    def load_template(self, template_name: str) -> str:
        template_path = self.TEMPLATE_DIR / template_name
        return template_path.read_text()

    def render_template(
        self,
        template: str,
        step_data: dict,
        agent_config: dict
    ) -> str:
        # Simple placeholder substitution
        result = template
        for key, value in step_data.items():
            result = result.replace(f"{{{key}}}", str(value))
        for key, value in agent_config.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result

    def validate_prompt(self, prompt: str) -> ValidationResult:
        errors = []

        # Check mandatory sections
        for section in self.MANDATORY_SECTIONS:
            if not self._section_present(prompt, section):
                errors.append(ValidationError(
                    error_type="MISSING",
                    element=section,
                    message=f"Mandatory section '{section}' not found",
                    suggestion=f"Add ## {section} section to prompt template"
                ))

        # Check all 14 phases present
        for phase in self.REQUIRED_PHASES:
            if phase not in prompt:
                errors.append(ValidationError(
                    error_type="INCOMPLETE",
                    element=phase,
                    message=f"TDD phase '{phase}' not mentioned",
                    suggestion=f"Add {phase} to TDD_14_PHASES section"
                ))

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=[]
        )

    def _section_present(self, prompt: str, section: str) -> bool:
        patterns = [
            f"## {section}",
            f"### {section}",
            f"# {section}",
            f"<!-- SECTION: {section} -->"
        ]
        return any(p in prompt for p in patterns)
```

### 3.5 Boundary Rules

| ALLOWED | FORBIDDEN |
|---------|-----------|
| Read template files | Modify templates at runtime |
| Substitute placeholders | Execute template code |
| Validate structure | Access step file directly |
| Return validation errors | Make network calls |
| Read section definitions | Change step file state |

### 3.6 Section Definitions

```yaml
# nWave/templates/prompt-templates/_section-definitions.yaml
execute_step:
  mandatory_sections:
    DES_METADATA:
      description: "Origin, step file, validation flag"
      markers: ["<!-- DES-ORIGIN:", "<!-- DES-STEP-FILE:", "<!-- DES-VALIDATION:"]

    AGENT_IDENTITY:
      description: "Agent role and capabilities"
      markers: ["## AGENT_IDENTITY", "# AGENT_IDENTITY"]

    TASK_CONTEXT:
      description: "Project, step, background, specification"
      markers: ["## TASK_CONTEXT", "# TASK_CONTEXT"]

    TDD_14_PHASES:
      description: "Complete 14-phase TDD cycle with gates"
      markers: ["## TDD_14_PHASES", "# TDD_14_PHASES", "## TDD"]
      required_content: ["PREPARE", "RED_ACCEPTANCE", "RED_UNIT", "GREEN_UNIT",
                        "CHECK_ACCEPTANCE", "GREEN_ACCEPTANCE", "REVIEW",
                        "REFACTOR_L1", "REFACTOR_L2", "REFACTOR_L3", "REFACTOR_L4",
                        "POST_REFACTOR_REVIEW", "FINAL_VALIDATE", "COMMIT"]

    QUALITY_GATES:
      description: "G1-G6 gate definitions"
      markers: ["## QUALITY_GATES", "# QUALITY_GATES"]
      required_content: ["G1", "G2", "G3", "G4", "G5", "G6"]

    OUTCOME_RECORDING:
      description: "How to record phase results"
      markers: ["## OUTCOME_RECORDING", "# OUTCOME_RECORDING"]

    BOUNDARY_RULES:
      description: "Scope limitations and forbidden actions"
      markers: ["## BOUNDARY_RULES", "# BOUNDARY_RULES"]
      required_content: ["ALLOWED", "FORBIDDEN"]

    TIMEOUT_INSTRUCTION:
      description: "Turn budget and early exit protocol"
      markers: ["## TIMEOUT_INSTRUCTION", "# TIMEOUT_INSTRUCTION"]
```

---

## 4. Layer 3: Lifecycle Manager

### 4.1 Purpose

Manage execution state and prevent scope creep or runaway execution.

### 4.2 Responsibilities

| Responsibility | Description |
|----------------|-------------|
| State Machine | Enforce valid state transitions |
| Turn Discipline | Include timeout instructions in prompts |
| Stale Detection | Detect abandoned IN_PROGRESS phases |
| Boundary Enforcement | Specify allowed/forbidden actions |

### 4.3 Interface (Port)

```python
# nWave/ports/lifecycle_manager.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

class TaskState(Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"

class PhaseState(Enum):
    NOT_EXECUTED = "NOT_EXECUTED"
    IN_PROGRESS = "IN_PROGRESS"
    EXECUTED = "EXECUTED"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"

@dataclass
class StaleExecution:
    step_file: str
    phase_name: str
    started_at: str
    age_minutes: int

@dataclass
class TransitionResult:
    allowed: bool
    error: str | None

class LifecycleManagerPort(ABC):
    @abstractmethod
    def validate_task_transition(
        self,
        current: TaskState,
        target: TaskState
    ) -> TransitionResult:
        """Check if task state transition is valid."""
        pass

    @abstractmethod
    def validate_phase_transition(
        self,
        current: PhaseState,
        target: PhaseState
    ) -> TransitionResult:
        """Check if phase state transition is valid."""
        pass

    @abstractmethod
    def check_stale_executions(
        self,
        project_dir: str,
        threshold_minutes: int = 30
    ) -> list[StaleExecution]:
        """Find IN_PROGRESS phases older than threshold."""
        pass
```

### 4.4 Implementation (Adapter)

```python
# nWave/adapters/fsm_lifecycle_manager.py
import json
from datetime import datetime, timedelta
from pathlib import Path
from nWave.ports.lifecycle_manager import (
    LifecycleManagerPort, TaskState, PhaseState,
    StaleExecution, TransitionResult
)

class FSMLifecycleManager(LifecycleManagerPort):
    """Finite State Machine implementation of lifecycle management."""

    TASK_TRANSITIONS = {
        TaskState.TODO: [TaskState.IN_PROGRESS],
        TaskState.IN_PROGRESS: [TaskState.DONE, TaskState.FAILED, TaskState.PARTIAL],
        TaskState.DONE: [],  # Terminal
        TaskState.FAILED: [TaskState.IN_PROGRESS],  # Retry
        TaskState.PARTIAL: [TaskState.IN_PROGRESS],  # Resume
    }

    PHASE_TRANSITIONS = {
        PhaseState.NOT_EXECUTED: [PhaseState.IN_PROGRESS],
        PhaseState.IN_PROGRESS: [
            PhaseState.EXECUTED, PhaseState.SKIPPED, PhaseState.FAILED
        ],
        PhaseState.EXECUTED: [],  # Terminal
        PhaseState.SKIPPED: [],   # Terminal
        PhaseState.FAILED: [PhaseState.IN_PROGRESS],  # Retry
    }

    def validate_task_transition(
        self,
        current: TaskState,
        target: TaskState
    ) -> TransitionResult:
        allowed = target in self.TASK_TRANSITIONS.get(current, [])
        return TransitionResult(
            allowed=allowed,
            error=None if allowed else
                  f"Invalid transition: {current.value} -> {target.value}"
        )

    def validate_phase_transition(
        self,
        current: PhaseState,
        target: PhaseState
    ) -> TransitionResult:
        allowed = target in self.PHASE_TRANSITIONS.get(current, [])
        return TransitionResult(
            allowed=allowed,
            error=None if allowed else
                  f"Invalid transition: {current.value} -> {target.value}"
        )

    def check_stale_executions(
        self,
        project_dir: str,
        threshold_minutes: int = 30
    ) -> list[StaleExecution]:
        stale = []
        threshold = datetime.now() - timedelta(minutes=threshold_minutes)

        for step_file in Path(project_dir).rglob("steps/*.json"):
            try:
                data = json.loads(step_file.read_text())
                phases = data.get("tdd_cycle", {}).get("phase_execution_log", [])

                for phase in phases:
                    if phase.get("status") == "IN_PROGRESS":
                        started_str = phase.get("started_at", "")
                        if started_str:
                            started = datetime.fromisoformat(started_str)
                            if started < threshold:
                                age = (datetime.now() - started).seconds // 60
                                stale.append(StaleExecution(
                                    step_file=str(step_file),
                                    phase_name=phase.get("phase_name", "UNKNOWN"),
                                    started_at=started_str,
                                    age_minutes=age
                                ))
            except (json.JSONDecodeError, KeyError):
                continue  # Skip malformed files

        return stale
```

### 4.5 Boundary Rules

| ALLOWED | FORBIDDEN |
|---------|-----------|
| Validate state transitions | Force state changes |
| Scan for stale phases | Modify step files |
| Return stale execution list | Make network calls |
| Read step file JSON | Delete step files |
| Enforce FSM rules | Skip validation |

### 4.6 State Machine Configuration

```yaml
# nWave/config/step-execution-fsm.yaml
name: StepExecutionFSM
version: "1.0"

task_states:
  TODO:
    description: "Step not started"
    terminal: false
    transitions: [IN_PROGRESS]

  IN_PROGRESS:
    description: "Agent actively working"
    terminal: false
    transitions: [DONE, FAILED, PARTIAL]

  DONE:
    description: "Step completed successfully"
    terminal: true
    transitions: []

  FAILED:
    description: "Step failed, needs intervention"
    terminal: false
    transitions: [IN_PROGRESS]  # Retry allowed

  PARTIAL:
    description: "Partial completion, can resume"
    terminal: false
    transitions: [IN_PROGRESS]

phase_states:
  NOT_EXECUTED:
    transitions: [IN_PROGRESS]

  IN_PROGRESS:
    transitions: [EXECUTED, SKIPPED, FAILED]

  EXECUTED:
    terminal: true
    requires: [outcome]

  SKIPPED:
    terminal: true
    requires: [blocked_by]
    blocked_by_prefixes:
      allow_commit: ["BLOCKED_BY_DEPENDENCY:", "NOT_APPLICABLE:", "APPROVED_SKIP:"]
      block_commit: ["DEFERRED:"]

  FAILED:
    transitions: [IN_PROGRESS]  # Retry allowed
```

---

## 5. Layer 4: Validation Gates

### 5.1 Purpose

Multi-point validation throughout execution lifecycle.

### 5.2 Gate Definitions

| Gate | Trigger Point | Responsibility |
|------|---------------|----------------|
| Gate 1 | Before Task invocation | Template completeness |
| Gate 2 | SubagentStop hook | Post-execution state |
| Gate 3 | Pre-commit hook | Final commit readiness |
| Gate 4 | All events | Audit trail logging |

### 5.3 Interface (Port)

```python
# nWave/ports/validation_gate.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

class GateResult(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"

@dataclass
class GateValidation:
    gate_id: str
    result: GateResult
    errors: list[str]
    warnings: list[str]
    recovery_suggestions: list[str]

class ValidationGatePort(ABC):
    @abstractmethod
    def validate(self, context: dict) -> GateValidation:
        """Run gate validation and return result."""
        pass

    @abstractmethod
    def get_gate_id(self) -> str:
        """Return unique gate identifier."""
        pass
```

### 5.4 Gate 1: Pre-Invocation

```python
# nWave/adapters/gates/pre_invocation_gate.py
from nWave.ports.validation_gate import ValidationGatePort, GateValidation, GateResult
from nWave.ports.template_engine import TemplateEnginePort

class PreInvocationGate(ValidationGatePort):
    """Validates prompt before Task tool invocation."""

    def __init__(self, template_engine: TemplateEnginePort):
        self.template_engine = template_engine

    def get_gate_id(self) -> str:
        return "GATE_1_PRE_INVOCATION"

    def validate(self, context: dict) -> GateValidation:
        prompt = context.get("prompt", "")
        step_file = context.get("step_file")

        # Validate prompt structure
        result = self.template_engine.validate_prompt(prompt)

        if not result.valid:
            return GateValidation(
                gate_id=self.get_gate_id(),
                result=GateResult.FAIL,
                errors=[f"{e.error_type}: {e.message}" for e in result.errors],
                warnings=result.warnings,
                recovery_suggestions=[e.suggestion for e in result.errors]
            )

        return GateValidation(
            gate_id=self.get_gate_id(),
            result=GateResult.PASS,
            errors=[],
            warnings=result.warnings,
            recovery_suggestions=[]
        )
```

### 5.5 Gate 2: SubagentStop Hook

```python
# nWave/adapters/gates/subagent_stop_gate.py
import json
from pathlib import Path
from nWave.ports.validation_gate import ValidationGatePort, GateValidation, GateResult

class SubagentStopGate(ValidationGatePort):
    """Validates step file state after sub-agent completion."""

    def get_gate_id(self) -> str:
        return "GATE_2_SUBAGENT_STOP"

    def validate(self, context: dict) -> GateValidation:
        step_file = context.get("step_file")
        if not step_file:
            return GateValidation(
                gate_id=self.get_gate_id(),
                result=GateResult.WARNING,
                errors=[],
                warnings=["No step file in context - DES validation skipped"],
                recovery_suggestions=[]
            )

        errors = []
        warnings = []
        suggestions = []

        try:
            data = json.loads(Path(step_file).read_text())
            phases = data.get("tdd_cycle", {}).get("phase_execution_log", [])
            task_status = data.get("state", {}).get("status", "")

            for phase in phases:
                status = phase.get("status", "NOT_EXECUTED")
                phase_name = phase.get("phase_name", "UNKNOWN")

                if status == "IN_PROGRESS":
                    errors.append(f"Phase {phase_name} left IN_PROGRESS (abandoned)")
                    suggestions.append(f"Reset {phase_name} to NOT_EXECUTED")

                elif status == "NOT_EXECUTED" and task_status in ["DONE", "COMPLETED"]:
                    errors.append(f"Task DONE but {phase_name} NOT_EXECUTED")
                    suggestions.append("Review agent transcript for skipped phases")

                elif status == "EXECUTED" and not phase.get("outcome"):
                    errors.append(f"Phase {phase_name} EXECUTED without outcome")
                    suggestions.append(f"Add outcome to {phase_name}")

                elif status == "SKIPPED":
                    blocked_by = phase.get("blocked_by", "")
                    if not blocked_by:
                        errors.append(f"Phase {phase_name} SKIPPED without blocked_by")
                        suggestions.append(f"Add blocked_by reason to {phase_name}")
                    elif blocked_by.startswith("DEFERRED:"):
                        warnings.append(f"Phase {phase_name} DEFERRED - blocks commit")

            result = GateResult.FAIL if errors else (
                GateResult.WARNING if warnings else GateResult.PASS
            )

            return GateValidation(
                gate_id=self.get_gate_id(),
                result=result,
                errors=errors,
                warnings=warnings,
                recovery_suggestions=suggestions
            )

        except (json.JSONDecodeError, FileNotFoundError) as e:
            return GateValidation(
                gate_id=self.get_gate_id(),
                result=GateResult.FAIL,
                errors=[f"Step file error: {e}"],
                warnings=[],
                recovery_suggestions=["Check step file exists and contains valid JSON"]
            )
```

### 5.6 Gate 4: Audit Trail

```python
# nWave/adapters/gates/audit_trail.py
import json
from datetime import datetime, date
from pathlib import Path
from nWave.ports.validation_gate import ValidationGatePort, GateValidation, GateResult

class AuditTrail(ValidationGatePort):
    """Logs all events to daily audit trail."""

    def get_gate_id(self) -> str:
        return "GATE_4_AUDIT_TRAIL"

    def validate(self, context: dict) -> GateValidation:
        # Audit trail always passes - it only logs
        return GateValidation(
            gate_id=self.get_gate_id(),
            result=GateResult.PASS,
            errors=[],
            warnings=[],
            recovery_suggestions=[]
        )

    def log_event(
        self,
        step_file: str,
        event_type: str,
        data: dict
    ) -> None:
        """Append event to daily audit log."""
        today = date.today().isoformat()
        audit_path = Path(step_file).parent / f"audit-{today}.log"

        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "step_file": step_file,
            **data
        }

        with open(audit_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
```

### 5.7 Boundary Rules

| ALLOWED | FORBIDDEN |
|---------|-----------|
| Read step file | Modify step file (except FAILED state) |
| Validate phase states | Skip phases |
| Log to audit trail | Delete audit entries |
| Report errors/warnings | Ignore validation failures |
| Suggest recovery actions | Auto-fix issues |

---

## 6. Integration Boundary

### 6.1 Hook Integration Contract

The SubagentStop hook receives a specific JSON schema via stdin:

```json
{
  "session_id": "uuid",
  "transcript_path": "/path/to/session.jsonl",
  "cwd": "/project/path",
  "permission_mode": "bypassPermissions",
  "hook_event_name": "SubagentStop",
  "stop_hook_active": false,
  "agent_id": "ab7af5b",
  "agent_transcript_path": "/path/to/subagents/agent-ab7af5b.jsonl"
}
```

### 6.2 Step File Contract

All components must read/write step files using this structure:

```json
{
  "task_id": "01-01",
  "project_id": "auth-feature",
  "state": {
    "status": "IN_PROGRESS|DONE|FAILED|PARTIAL",
    "failure_reason": "Optional error message",
    "recovery_suggestions": ["Array of suggestions"]
  },
  "tdd_cycle": {
    "phase_execution_log": [
      {
        "phase_name": "PREPARE",
        "status": "NOT_EXECUTED|IN_PROGRESS|EXECUTED|SKIPPED|FAILED",
        "started_at": "ISO timestamp",
        "ended_at": "ISO timestamp",
        "outcome": "PASS|FAIL",
        "outcome_details": "Description",
        "blocked_by": "PREFIX: reason (if SKIPPED)"
      }
    ]
  }
}
```

### 6.3 Audit Log Contract

All audit entries must follow this format:

```json
{
  "timestamp": "2026-01-22T14:30:00.000Z",
  "event": "EVENT_TYPE",
  "step_file": "path/to/step.json",
  "...additional_fields": "..."
}
```

---

## 7. Component Interaction Matrix

| Component | Reads | Writes | Calls |
|-----------|-------|--------|-------|
| Command Filter | Prompt | - | - |
| Template Engine | Templates, Section Defs | - | - |
| Lifecycle Manager | Step Files | - | - |
| Gate 1 | Prompt | - | Template Engine |
| Gate 2 | Step File, Transcript | Step File (FAILED) | - |
| Gate 3 | Step File, Audit Log | - | - |
| Gate 4 | - | Audit Log | - |

---

## 8. Error Propagation

```
Layer 1 Error → Block at Gate 1 (no Task invocation)
                ↓
        Log TASK_INVOCATION_REJECTED

Layer 2 Error → Block at Gate 1 (validation failure)
                ↓
        Log TASK_INVOCATION_REJECTED with errors

Layer 3 Error → Detected at Gate 2 (post-execution)
                ↓
        Log SUBAGENT_STOP_VALIDATION error
                ↓
        Set step file to FAILED
                ↓
        Populate recovery_suggestions

Layer 4 Error → Write failure to stderr
                ↓
        Execution continues (non-blocking)
```

---

*Component boundaries defined by Morgan (solution-architect) during DESIGN wave.*
