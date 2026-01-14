# Skills Architecture - Complete Specification

## Executive Summary

This document consolidates all skill architecture decisions required to unblock Phase 1 steps (01-04, 01-05, 01-06).

**Critical Definitions**:
1. ✅ Skill data structure (DEFINED in skill-data-structure.md)
2. ✅ Skill markdown format (DEFINED in skill-markdown-format.md)
3. ✅ Trigger pattern semantics (THIS DOCUMENT)
4. ✅ Agent association model (THIS DOCUMENT)
5. ✅ Workflow integration requirements (THIS DOCUMENT)
6. ✅ Runtime integration & Claude Code compatibility (DEFINED in skill-runtime-integration.md)
7. ✅ Regex performance safeguards (THIS DOCUMENT, Section 1.1)
8. ✅ Phase number semantics (THIS DOCUMENT, Section 3.1)

---

## 1. Trigger Pattern Semantics

### Definition

Triggers are **regex patterns** that activate a skill when matched against task context.

### Pattern Matching Logic

```
Task Input: "Implement the login feature using outside-in TDD"

Skill: 'develop' with triggers=['implement.*', 'TDD', 'outside-in']
Evaluation:
  - Pattern 'implement.*' matches "Implement the login..." → MATCH
  - Pattern 'TDD' matches "outside-in TDD" → MATCH
  - Pattern 'outside-in' matches "outside-in" → MATCH

Result: Skill is ACTIVATED (OR logic: any match = activation)
```

### Pattern Matching Rules

1. **Case-Insensitive**: Patterns are matched case-insensitively
   ```
   Pattern: 'TDD'  matches:  'tdd', 'TDD', 'Tdd', 'tDD' ✓
   ```

2. **Partial Matching**: Patterns match anywhere in input (not just start/end)
   ```
   Pattern: 'implement.*'  matches:
     - "implement the feature" ✓
     - "I will implement X" ✓
     - "please implement Y" ✓
   ```

3. **OR Logic**: Multiple triggers = OR (activate if ANY pattern matches)
   ```
   triggers: ['refactor.*', 'simplify.*', 'optimize']

   "refactor this code" → ACTIVATE (pattern 0 matches)
   "simplify the logic" → ACTIVATE (pattern 1 matches)
   "optimize performance" → ACTIVATE (pattern 2 matches)
   "write more comments" → NO MATCH (no pattern matches)
   ```

4. **Character Escaping** in YAML:
   - Regex special chars DO NOT need escaping in TOON files (they're YAML values)
   - Example valid patterns:
     ```yaml
     triggers:
       - implement.*
       - refactor\s+\w+      # Whitespace handling
       - "test.*\(.*\)"       # Parentheses must be quoted
       - optimize|streamline  # OR operator in regex
     ```

### Validation

Parser MUST verify patterns are valid regex:
```python
import re

for pattern in triggers:
    try:
        re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        raise ValidationError(f"Invalid trigger pattern '{pattern}': {e}")
```

### Pattern Examples

```yaml
# Example 1: TDD-related triggers
triggers:
  - implement.*
  - test.*driven
  - TDD
  - outside-in.*test

# Example 2: Refactoring triggers
triggers:
  - refactor
  - simplify.*code
  - optimize.*performance
  - mikado.*method

# Example 3: Documentation triggers
triggers:
  - document.*
  - write.*readme
  - api.*documentation
  - "spec.*\(.*\)"
```

---

### 1.1 Regex Performance Safeguards

**Problem**: Regex patterns can cause performance issues (ReDoS, catastrophic backtracking).

**Solution**: Implement caching and complexity validation at compile-time.

#### Pattern Caching

All trigger patterns MUST be pre-compiled at skill load time:

```python
import re
from functools import lru_cache
from typing import List, Pattern

class TriggerPatternCache:
    """Thread-safe compiled regex pattern cache."""

    def __init__(self, max_patterns: int = 1000):
        self._cache: Dict[str, Pattern] = {}
        self._max_patterns = max_patterns

    def compile(self, pattern: str) -> Pattern:
        """Compile and cache pattern."""
        if pattern not in self._cache:
            if len(self._cache) >= self._max_patterns:
                # LRU eviction: remove oldest entry
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
            self._cache[pattern] = re.compile(pattern, re.IGNORECASE)
        return self._cache[pattern]

    def match_any(self, patterns: List[str], text: str) -> bool:
        """Check if any pattern matches (short-circuit on first match)."""
        for pattern_str in patterns:
            compiled = self.compile(pattern_str)
            if compiled.search(text):
                return True
        return False

# Global cache instance (singleton)
_pattern_cache = TriggerPatternCache()

def match_triggers(triggers: List[str], task_context: str) -> bool:
    """Public API for trigger matching with caching."""
    return _pattern_cache.match_any(triggers, task_context)
```

#### Complexity Validation

Parser MUST reject patterns that could cause ReDoS:

```python
import re
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class PatternComplexityResult:
    """Result of pattern complexity analysis."""
    pattern: str
    is_valid: bool
    complexity_score: int  # 0-100, higher = more risky
    warning: Optional[str] = None
    error: Optional[str] = None

# Dangerous pattern indicators
DANGEROUS_PATTERNS = [
    r'\(\.\*\)\+',      # Nested quantifiers: (.*)+
    r'\(\.\+\)\*',      # Nested quantifiers: (.+)*
    r'\(\.\*\)\*',      # Nested quantifiers: (.*)*
    r'\(\[.*\]\)\+',    # Repeated character class: ([...])+
    r'\.{10,}',         # Excessive wildcards: .........
    r'\w{50,}',         # Excessive word match
]

MAX_PATTERN_LENGTH = 200  # Characters
MAX_QUANTIFIER_NESTING = 2
MAX_ALTERNATIONS = 10

def validate_pattern_complexity(pattern: str) -> PatternComplexityResult:
    """Validate pattern for potential ReDoS vulnerabilities.

    Returns:
        PatternComplexityResult with validity and warnings
    """
    # Check length
    if len(pattern) > MAX_PATTERN_LENGTH:
        return PatternComplexityResult(
            pattern=pattern,
            is_valid=False,
            complexity_score=100,
            error=f"Pattern exceeds max length ({len(pattern)} > {MAX_PATTERN_LENGTH})"
        )

    # Check dangerous patterns
    for dangerous in DANGEROUS_PATTERNS:
        if re.search(dangerous, pattern):
            return PatternComplexityResult(
                pattern=pattern,
                is_valid=False,
                complexity_score=100,
                error=f"Pattern contains dangerous construct: {dangerous}"
            )

    # Check alternation count
    alternations = pattern.count('|')
    if alternations > MAX_ALTERNATIONS:
        return PatternComplexityResult(
            pattern=pattern,
            is_valid=False,
            complexity_score=80,
            error=f"Too many alternations ({alternations} > {MAX_ALTERNATIONS})"
        )

    # Calculate complexity score
    score = 0
    score += alternations * 5  # Each alternation adds complexity
    score += pattern.count('*') * 10  # Wildcards are expensive
    score += pattern.count('+') * 8
    score += pattern.count('?') * 3
    score += len(pattern) // 10  # Length contributes

    # Validate it compiles
    try:
        re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        return PatternComplexityResult(
            pattern=pattern,
            is_valid=False,
            complexity_score=100,
            error=f"Invalid regex: {e}"
        )

    warning = None
    if score > 50:
        warning = f"High complexity pattern (score={score}). Consider simplifying."

    return PatternComplexityResult(
        pattern=pattern,
        is_valid=True,
        complexity_score=min(score, 100),
        warning=warning
    )

def validate_all_triggers(triggers: List[str]) -> List[PatternComplexityResult]:
    """Validate all trigger patterns for a skill."""
    return [validate_pattern_complexity(p) for p in triggers]
```

#### Matching Timeout

Runtime matching MUST have timeout protection:

```python
import signal
from contextlib import contextmanager

MATCH_TIMEOUT_SECONDS = 1.0  # Max time for pattern matching

class MatchTimeoutError(Exception):
    """Raised when pattern matching exceeds timeout."""
    pass

@contextmanager
def match_timeout(seconds: float = MATCH_TIMEOUT_SECONDS):
    """Context manager for timeout on pattern matching."""
    def handler(signum, frame):
        raise MatchTimeoutError(f"Pattern matching exceeded {seconds}s timeout")

    # Note: signal.alarm only works on Unix
    # For cross-platform, use threading.Timer or concurrent.futures
    old_handler = signal.signal(signal.SIGALRM, handler)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old_handler)

def safe_match_triggers(triggers: List[str], task_context: str) -> bool:
    """Match triggers with timeout protection."""
    try:
        with match_timeout():
            return match_triggers(triggers, task_context)
    except MatchTimeoutError:
        # Log warning, return no match rather than crashing
        return False
```

---

## 2. Agent Association Model

### Cardinality Options

Skills support three binding modes:

### Mode 1: 1:1 (Single Agent)

**Definition**: Skill bound to exactly one agent

**Data Structure**:
```python
agent_association: str  # Single agent ID

# Example
agent_association: 'software-crafter'
```

**YAML Representation**:
```yaml
agent_association: software-crafter
```

**Semantics**:
- Skill is ONLY available to this agent
- Only this agent can invoke the skill
- Simple, clear responsibility

**Use Cases**:
- Skills specific to one agent's role
- Example: `'develop'` skill for software-crafter

### Mode 2: 1:N (One Skill → Multiple Agents)

**Definition**: Skill bound to multiple agents (any can invoke)

**Data Structure**:
```python
agent_association: List[str]  # Multiple agent IDs

# Example
agent_association: ['software-crafter', 'solution-architect']
```

**YAML Representation**:
```yaml
agent_association:
  - software-crafter
  - solution-architect
  - product-owner
```

**Semantics**:
- Skill is available to ALL listed agents
- Any listed agent can invoke the skill
- Useful for cross-agent workflows

**Use Cases**:
- Shared skills across multiple agents
- Example: `'review'` skill for software-crafter AND solution-architect
- Example: `'document'` skill for all agents

### Mode 3: N:M (Future Extension - Conditional Binding)

**Definition**: Skill with conditional agent access per agent

**Current Status**: RESERVED - Forward-compatible design documented below

**Data Structure** (future):
```python
agent_association: Dict[str, AgentPermission]  # Conditional model

# Future example
agent_association: {
    'software-crafter': {'permission': 'full'},
    'solution-architect': {'permission': 'read-only'},
    'product-owner': {'permission': 'invoke-only'}
}
```

---

### 2.1 N:M Forward-Compatible Design

This section documents the future N:M model to ensure current implementations remain compatible.

#### Permission Model

```python
from typing import TypedDict, Literal, Optional
from enum import Enum

class PermissionLevel(str, Enum):
    """Skill access permission levels."""
    FULL = 'full'           # Can invoke, modify, extend skill
    INVOKE_ONLY = 'invoke'  # Can only invoke skill (default)
    READ_ONLY = 'read'      # Can view skill definition only
    NONE = 'none'           # Explicitly denied access


class AgentPermission(TypedDict, total=False):
    """Permission configuration for one agent."""
    permission: PermissionLevel  # Access level (default: invoke)
    conditions: Optional[dict]   # Future: conditional access rules
    priority: Optional[int]      # Future: resolution priority for conflicts


# Full N:M structure
AgentAssociationNM = Dict[str, AgentPermission]
```

#### YAML Representation (Future)

```yaml
# Current 1:1 format (remains valid)
agent_association: software-crafter

# Current 1:N format (remains valid)
agent_association:
  - software-crafter
  - solution-architect

# Future N:M format (when implemented)
agent_association:
  software-crafter:
    permission: full
  solution-architect:
    permission: invoke
    conditions:
      wave: [DESIGN, DEVELOP]  # Only in these waves
  product-owner:
    permission: read
```

#### Forward-Compatible Parsing

Parser MUST handle all three formats transparently:

```python
from typing import Union, List, Dict

AgentAssociation = Union[str, List[str], Dict[str, dict]]

def parse_agent_association(value: Any) -> AgentAssociation:
    """Parse agent_association supporting all modes.

    Modes:
        1:1 - str → single agent ID
        1:N - list → multiple agent IDs (all with default permission)
        N:M - dict → agent IDs with explicit permissions

    Returns:
        Normalized agent association structure
    """
    if isinstance(value, str):
        # Mode 1:1: Single agent string
        return value

    if isinstance(value, list):
        # Mode 1:N: List of agent IDs
        if not value:
            raise ValidationError("agent_association list cannot be empty")
        if all(isinstance(item, str) for item in value):
            return value
        raise ValidationError("agent_association list must contain strings")

    if isinstance(value, dict):
        # Mode N:M: Dict with agent permissions
        if not value:
            raise ValidationError("agent_association dict cannot be empty")

        # Validate structure
        for agent_id, config in value.items():
            if not isinstance(agent_id, str):
                raise ValidationError(f"Agent ID must be string, got {type(agent_id)}")
            if config is not None and not isinstance(config, dict):
                raise ValidationError(
                    f"Agent config must be dict or null, got {type(config)}"
                )
        return value

    raise ValidationError(
        f"agent_association must be str, list, or dict; got {type(value).__name__}"
    )


def is_agent_authorized(
    agent_association: AgentAssociation,
    agent_id: str,
    required_permission: str = 'invoke'
) -> bool:
    """Check if agent has required permission level.

    Works with all three modes, providing backward compatibility.
    """
    # Mode 1:1
    if isinstance(agent_association, str):
        return agent_association == agent_id

    # Mode 1:N
    if isinstance(agent_association, list):
        return agent_id in agent_association

    # Mode N:M
    if isinstance(agent_association, dict):
        if agent_id not in agent_association:
            return False

        config = agent_association[agent_id]
        if config is None:
            # None means default (invoke) permission
            return required_permission in ['invoke', 'read']

        agent_perm = config.get('permission', 'invoke')

        # Permission hierarchy: full > invoke > read > none
        permission_hierarchy = ['none', 'read', 'invoke', 'full']

        try:
            agent_level = permission_hierarchy.index(agent_perm)
            required_level = permission_hierarchy.index(required_permission)
            return agent_level >= required_level
        except ValueError:
            return False

    return False
```

#### Migration Path

When N:M is implemented:

1. **No breaking changes**: Existing 1:1 and 1:N YAML files continue to work
2. **Automatic upgrade**: Parser converts old formats to N:M internally if needed
3. **Gradual adoption**: Teams can migrate skills to N:M format incrementally

```python
def normalize_to_nm(agent_association: AgentAssociation) -> Dict[str, dict]:
    """Convert any format to N:M for internal processing.

    Useful when N:M features are needed but input may be old format.
    """
    if isinstance(agent_association, str):
        return {agent_association: {'permission': 'full'}}

    if isinstance(agent_association, list):
        return {agent_id: {'permission': 'invoke'} for agent_id in agent_association}

    # Already N:M format
    return agent_association
```

#### Implementation Timeline

| Phase | Feature | Status |
|-------|---------|--------|
| v1.0 | 1:1 (single agent) | ✅ Implemented |
| v1.0 | 1:N (multiple agents) | ✅ Implemented |
| v1.1 | N:M parsing (forward-compat) | 📋 Designed |
| v2.0 | N:M runtime enforcement | 📋 Reserved |
| v2.1 | Conditional access rules | 📋 Reserved |

---

## 3. Workflow Integration Requirements

### Structure

```python
workflow_integration: Dict[str, any]  # Required fields:
{
    'wave': str,           # REQUIRED: nWave phase
    'phase': int,          # REQUIRED: Phase number (1-8)
    'context': Optional[str]  # OPTIONAL: Execution context
}
```

### Wave Values

Valid nWave phases:
- `'DISCUSS'`: Requirements gathering
- `'DESIGN'`: Architecture and design
- `'DEVELOP'`: Implementation (feature building)
- `'DISTILL'`: Acceptance testing and validation
- `'DELIVER'`: Deployment and release

### Phase Values

Phase numbers 1-8 represent distinct stages within each wave.

---

### 3.1 Phase Number Semantics by Wave

Each wave has its own phase progression with specific meanings:

#### DISCUSS Wave Phases

| Phase | Name | Purpose |
|-------|------|---------|
| 1 | **Context Gathering** | Collect background information and stakeholder needs |
| 2 | **Problem Definition** | Define the core problem to solve |
| 3 | **Requirements Elicitation** | Extract functional/non-functional requirements |
| 4 | **Prioritization** | Rank requirements by business value |
| 5 | **Acceptance Criteria** | Define measurable success criteria |
| 6 | **Scope Validation** | Verify scope with stakeholders |
| 7 | **Risk Identification** | Identify potential risks and blockers |
| 8 | **Handoff to Design** | Package requirements for DESIGN wave |

#### DESIGN Wave Phases

| Phase | Name | Purpose |
|-------|------|---------|
| 1 | **Architecture Analysis** | Analyze existing architecture and constraints |
| 2 | **Component Design** | Design new/modified components |
| 3 | **Interface Design** | Define APIs and integration points |
| 4 | **Data Modeling** | Design data structures and storage |
| 5 | **Security Design** | Address security requirements |
| 6 | **Performance Design** | Address performance requirements |
| 7 | **Design Review** | Validate design with stakeholders |
| 8 | **Handoff to Develop** | Package design for DEVELOP wave |

#### DEVELOP Wave Phases (TDD Cycle)

| Phase | Name | Purpose |
|-------|------|---------|
| 1 | **Outer Test (Red)** | Write failing acceptance test |
| 2 | **Inner Test (Red)** | Write failing unit test |
| 3 | **Implementation (Green)** | Write minimal code to pass |
| 4 | **Refactor (Blue)** | Improve code quality |
| 5 | **Integration** | Integrate with existing codebase |
| 6 | **Code Review** | Peer review and feedback |
| 7 | **Documentation** | Update technical documentation |
| 8 | **Handoff to Distill** | Package for acceptance testing |

#### DISTILL Wave Phases

| Phase | Name | Purpose |
|-------|------|---------|
| 1 | **Test Environment Setup** | Prepare testing environment |
| 2 | **Smoke Testing** | Verify basic functionality |
| 3 | **Functional Testing** | Verify all requirements |
| 4 | **Regression Testing** | Ensure no existing features broken |
| 5 | **Performance Testing** | Validate performance criteria |
| 6 | **Security Testing** | Validate security requirements |
| 7 | **User Acceptance Testing** | Stakeholder validation |
| 8 | **Handoff to Deliver** | Package for deployment |

#### DELIVER Wave Phases

| Phase | Name | Purpose |
|-------|------|---------|
| 1 | **Deployment Planning** | Plan rollout strategy |
| 2 | **Environment Preparation** | Prepare production environment |
| 3 | **Pre-deployment Checks** | Final validation before deploy |
| 4 | **Deployment Execution** | Execute deployment |
| 5 | **Post-deployment Verification** | Verify successful deployment |
| 6 | **Monitoring Setup** | Configure monitoring and alerts |
| 7 | **Documentation Update** | Update operational documentation |
| 8 | **Release Communication** | Communicate release to stakeholders |

#### Phase Usage in Skills

Skills specify which phase(s) they're relevant to:

```python
# Skill active during TDD implementation (DEVELOP phases 2-4)
workflow_integration = {
    'wave': 'DEVELOP',
    'phase': 3,  # Implementation phase
    'context': 'TDD cycle'
}

# Skill active during security design
workflow_integration = {
    'wave': 'DESIGN',
    'phase': 5,  # Security design phase
    'context': 'security analysis'
}
```

#### Phase Validation Rules

```python
PHASE_DEFINITIONS = {
    'DISCUSS': {
        1: 'Context Gathering',
        2: 'Problem Definition',
        3: 'Requirements Elicitation',
        4: 'Prioritization',
        5: 'Acceptance Criteria',
        6: 'Scope Validation',
        7: 'Risk Identification',
        8: 'Handoff to Design'
    },
    'DESIGN': {
        1: 'Architecture Analysis',
        2: 'Component Design',
        3: 'Interface Design',
        4: 'Data Modeling',
        5: 'Security Design',
        6: 'Performance Design',
        7: 'Design Review',
        8: 'Handoff to Develop'
    },
    'DEVELOP': {
        1: 'Outer Test (Red)',
        2: 'Inner Test (Red)',
        3: 'Implementation (Green)',
        4: 'Refactor (Blue)',
        5: 'Integration',
        6: 'Code Review',
        7: 'Documentation',
        8: 'Handoff to Distill'
    },
    'DISTILL': {
        1: 'Test Environment Setup',
        2: 'Smoke Testing',
        3: 'Functional Testing',
        4: 'Regression Testing',
        5: 'Performance Testing',
        6: 'Security Testing',
        7: 'User Acceptance Testing',
        8: 'Handoff to Deliver'
    },
    'DELIVER': {
        1: 'Deployment Planning',
        2: 'Environment Preparation',
        3: 'Pre-deployment Checks',
        4: 'Deployment Execution',
        5: 'Post-deployment Verification',
        6: 'Monitoring Setup',
        7: 'Documentation Update',
        8: 'Release Communication'
    }
}

def get_phase_name(wave: str, phase: int) -> str:
    """Get human-readable phase name."""
    return PHASE_DEFINITIONS.get(wave, {}).get(phase, f'Phase {phase}')

def validate_workflow_integration(wi: Dict) -> bool:
    """Validate workflow_integration against phase definitions."""
    wave = wi.get('wave')
    phase = wi.get('phase')

    if wave not in PHASE_DEFINITIONS:
        raise ValidationError(f"Invalid wave: {wave}")

    if phase not in PHASE_DEFINITIONS[wave]:
        raise ValidationError(f"Invalid phase {phase} for wave {wave}")

    return True
```

### Context Field

**Purpose**: Optional execution context/scope

**Values**: Free-form strings describing execution context
- `'TDD cycle'`: Indicates skill is used during TDD development
- `'refactoring improvement'`: Indicates skill relates to refactoring
- `'testing automation'`: Indicates skill relates to test automation

**Examples**:
```python
workflow_integration={
    'wave': 'DEVELOP',
    'phase': 3,
    'context': 'TDD cycle'
}

workflow_integration={
    'wave': 'DISTILL',
    'phase': 4,
    'context': 'acceptance testing'
}

workflow_integration={
    'wave': 'DELIVER',
    'phase': 7
    # context omitted if not relevant
}
```

### Parsing YAML

```yaml
workflow_integration:
  wave: DEVELOP
  phase: 3
  context: TDD cycle

# Parsed to Python dict:
{
    'wave': 'DEVELOP',
    'phase': 3,
    'context': 'TDD cycle'
}
```

### Validation Rules

Parser MUST enforce:
```python
# Required fields
assert 'wave' in workflow_integration, "Missing 'wave' field"
assert 'phase' in workflow_integration, "Missing 'phase' field"

# Wave validation
valid_waves = ['DISCUSS', 'DESIGN', 'DEVELOP', 'DISTILL', 'DELIVER']
assert workflow_integration['wave'] in valid_waves, \
    f"Invalid wave '{workflow_integration['wave']}'"

# Phase validation
assert isinstance(workflow_integration['phase'], int), \
    "Phase must be integer"
assert 1 <= workflow_integration['phase'] <= 8, \
    "Phase must be between 1 and 8"

# Context is optional
# (no validation needed if present)
```

---

## Summary Table

| Aspect | Definition | Status |
|--------|-----------|--------|
| **Skill Data Structure** | TypedDict with id, name, type, triggers, agent_association, workflow_integration | ✅ DEFINED |
| **Output Format** | SKILL.md with YAML frontmatter + sections | ✅ DEFINED |
| **Trigger Patterns** | Regex strings, case-insensitive, partial match, OR logic | ✅ DEFINED |
| **Pattern Validation** | YAML escaping rules, regex validation | ✅ DEFINED |
| **Agent Association (1:1)** | Single agent string | ✅ DEFINED |
| **Agent Association (1:N)** | List of agent strings | ✅ DEFINED |
| **Agent Association (N:M)** | Reserved for future extension | 📋 RESERVED |
| **Workflow Integration** | Dict with wave (str), phase (int), context (optional str) | ✅ DEFINED |
| **Wave Values** | DISCUSS, DESIGN, DEVELOP, DISTILL, DELIVER | ✅ DEFINED |
| **Phase Numbers** | 1-8 | ✅ DEFINED |
| **Context Field** | Optional free-form string | ✅ DEFINED |

---

## Impact on Phase 1 Steps

### Step 01-04: Create Skill Jinja2 Template

**Now Unblocked**:
- ✅ Skill data structure known → can write outer_test with proper data
- ✅ Skill output format defined → can validate template output
- ✅ Trigger pattern semantics clear → AC2 is measurable
- ✅ Agent association model defined → AC3 is measurable
- ✅ Workflow integration requirements defined → AC4 is measurable

**Acceptance Criteria** (now measurable):
1. Template produces valid YAML frontmatter with all required fields
2. Triggers rendered as YAML list with regex patterns properly escaped
3. Agent association rendered as string (1:1) or YAML list (1:N)
4. Workflow integration renders wave, phase, context fields
5. Output is valid SKILL.md format per skill-markdown-format.md

### Step 01-05: Create TOON Compiler

**Now Unblocked**:
- ✅ Knows expected skill template output structure
- ✅ Can route skill type to correct template
- ✅ Can validate output against type-specific schemas

### Step 01-06: Infrastructure Integration Tests

**Now Unblocked**:
- ✅ Can write integration tests with real skill data
- ✅ Can validate output against skill-markdown-format.md spec
- ✅ Can test trigger pattern rendering correctly

---

## Version History

- **v1.1** (2026-01-14): Opus review critical issue resolutions
  - Added Section 1.1: Regex performance safeguards (caching, complexity validation, timeout)
  - Added Section 3.1: Phase number semantics by wave (DISCUSS/DESIGN/DEVELOP/DISTILL/DELIVER)
  - Added Section 2.1: N:M forward-compatible design with permission model
  - Added reference to skill-runtime-integration.md for Claude Code compatibility
  - All critical/high issues from Opus review addressed

- **v1.0** (2026-01-14): Complete skills architecture specification
  - Skill data structure with TypedDict
  - Skill markdown format with examples
  - Trigger pattern semantics (regex, OR logic, escaping)
  - Agent association models (1:1, 1:N, N:M reserved)
  - Workflow integration with wave/phase/context
  - All validation rules and examples
  - Unblocks Phase 1 steps 01-04, 01-05, 01-06
