# Skill Runtime Integration Specification

## Executive Summary

**CRITICAL DISCOVERY**: The nWave SKILL.md format is **NOT COMPATIBLE** with Claude Code's native Agent Skills format.

This document:
1. Documents the incompatibility
2. Defines the nWave runtime consumer
3. Proposes a dual-format compatibility strategy
4. Establishes the integration architecture

---

## 1. Format Comparison

### Claude Code Native Format (Official)

**Source**: [Anthropic Agent Skills](https://github.com/anthropics/skills), [Engineering Blog](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

```yaml
---
name: my-skill-name
description: A clear description of what this skill does and when to use it
---

# Skill Title

[Instructions that Claude follows when skill is active]
```

**Required fields**: ONLY `name` and `description`

**Activation mechanism**: Claude reads `description` and determines semantic relevance to user request. **No regex patterns**.

**Location**: `~/.claude/skills/` or `.claude/skills/`

### nWave Format (Our Implementation)

```yaml
---
skill_id: develop
name: TDD Development
agent_association: software-crafter
wave: DEVELOP
phase: 3
triggers:
  - implement.*
  - TDD
  - outside-in
description: |
  Systematic test-driven development approach
---

# Activation Notice
...
```

**Required fields**: `skill_id`, `name`, `triggers`, `agent_association`, `workflow_integration`

**Activation mechanism**: Regex pattern matching against task context

**Location**: `dist/skills/{skill_id}/SKILL.md`

---

## 2. Incompatibility Analysis

| Aspect | Claude Code Native | nWave Format | Compatible? |
|--------|-------------------|--------------|-------------|
| **Required fields** | `name`, `description` | `skill_id`, `name`, `triggers`, `agent_association`, `workflow_integration` | **NO** |
| **Activation** | Semantic (description-based) | Regex patterns | **NO** |
| **Location** | `~/.claude/skills/` | `dist/skills/` | **NO** |
| **Runtime** | Claude Code built-in | nWave orchestrator | **NO** |
| **Discovery** | Auto-discovery by Claude | nWave skill registry | **NO** |

### Critical Differences

1. **No `triggers` in Claude Code**: Claude uses semantic matching on `description`, not regex patterns
2. **No `agent_association` in Claude Code**: Skills are available to all agents
3. **No `workflow_integration` in Claude Code**: No wave/phase concept
4. **No `skill_id` in Claude Code**: Uses `name` as identifier

---

## 3. Strategic Decision: Dual-Format Compatibility

### Architecture

nWave skills are **framework-specific extensions** that compile to **two output formats**:

```
TOON Source File (.toon)
        │
        ▼
   TOON Compiler
        │
        ├─────────────────────────────────┐
        ▼                                 ▼
[nWave SKILL.md]                  [Claude Code SKILL.md]
(Full nWave format)               (Native format)
        │                                 │
        ▼                                 ▼
dist/skills/{id}/                 .claude/skills/{name}/
   SKILL.md                          SKILL.md
        │                                 │
        ▼                                 ▼
nWave Orchestrator                Claude Code Runtime
(Regex pattern matching)          (Semantic matching)
```

### Output 1: nWave Format (Primary)

**Location**: `dist/skills/{skill_id}/SKILL.md`

**Consumer**: nWave Orchestrator (custom component)

**Purpose**: Full nWave workflow integration with:
- Regex-based trigger patterns
- Agent association (1:1, 1:N binding)
- Wave/phase positioning
- Custom metadata

### Output 2: Claude Code Format (Secondary)

**Location**: `.claude/skills/{name}/SKILL.md`

**Consumer**: Claude Code native runtime

**Purpose**: Native Claude Code integration allowing:
- Automatic discovery by Claude
- Semantic matching on description
- Hot-reload support
- Standard skill ecosystem compatibility

---

## 4. nWave Runtime Consumer Specification

### Component: nWave Skill Orchestrator

**Responsibility**: Load, match, and activate nWave skills during workflow execution

**Location**: Part of nWave framework (to be implemented)

**Interface**:

```python
class SkillOrchestrator:
    """nWave skill discovery and activation."""

    def __init__(self, skill_directory: str = "dist/skills"):
        """Initialize with skill directory path."""
        self.skills: Dict[str, LoadedSkill] = {}
        self._load_skills(skill_directory)

    def _load_skills(self, directory: str) -> None:
        """Scan directory and load all SKILL.md files."""
        # Parse YAML frontmatter from each SKILL.md
        # Build internal skill registry
        pass

    def match_skills(self, task_context: str) -> List[LoadedSkill]:
        """Find skills whose triggers match task context.

        Args:
            task_context: User task description or input

        Returns:
            List of matching skills (OR logic: any pattern match)
        """
        matches = []
        for skill in self.skills.values():
            for pattern in skill.triggers:
                if re.search(pattern, task_context, re.IGNORECASE):
                    matches.append(skill)
                    break  # One match is enough (OR logic)
        return matches

    def activate_skill(
        self,
        skill: LoadedSkill,
        agent_id: str
    ) -> Optional[str]:
        """Activate skill for given agent.

        Args:
            skill: Skill to activate
            agent_id: Agent requesting activation

        Returns:
            Skill content if agent authorized, None otherwise
        """
        if not self._is_agent_authorized(skill, agent_id):
            return None
        return skill.content

    def _is_agent_authorized(
        self,
        skill: LoadedSkill,
        agent_id: str
    ) -> bool:
        """Check if agent can use this skill."""
        assoc = skill.agent_association
        if isinstance(assoc, str):
            return assoc == agent_id
        return agent_id in assoc

@dataclass
class LoadedSkill:
    """Parsed skill from SKILL.md."""
    id: str
    name: str
    description: str
    triggers: List[re.Pattern]  # Pre-compiled regex patterns
    agent_association: Union[str, List[str]]
    workflow_integration: Dict[str, Any]
    content: str  # Full markdown content for injection
```

### Integration Point

The Skill Orchestrator integrates with nWave workflow at these points:

1. **Task Execution**: Before agent receives task, orchestrator checks for matching skills
2. **Skill Injection**: Matching skill content added to agent context
3. **Agent Validation**: Skill only activated if agent is authorized

```
User Task
    │
    ▼
nWave Orchestrator
    │
    ├── Match skills (regex against task)
    │
    ├── Filter by agent_association
    │
    ├── Inject skill content into agent context
    │
    ▼
Agent Execution (with skill context)
```

---

## 5. Template Modifications Required

### Skill Template Must Generate BOTH Formats

**Primary Output** (nWave): `dist/skills/{id}/SKILL.md`
- Full nWave format with all fields
- Consumed by nWave Skill Orchestrator

**Secondary Output** (Claude Code): `.claude/skills/{name}/SKILL.md`
- Claude Code native format
- Only `name` and `description`
- Consumed by Claude Code runtime

### Conversion Logic

```python
def convert_nwave_to_claude_code(nwave_skill: SkillData) -> str:
    """Convert nWave skill to Claude Code format.

    Key transformations:
    1. skill_id → name (convert underscores to hyphens)
    2. triggers → description (explain when skill activates)
    3. Drop: agent_association, workflow_integration, wave, phase
    """
    # Build description from triggers and original description
    trigger_description = f"Use this skill when: {', '.join(nwave_skill['triggers'])}"
    full_description = nwave_skill.get('description', '')
    if full_description:
        description = f"{full_description}\n\n{trigger_description}"
    else:
        description = trigger_description

    return f'''---
name: {nwave_skill['id'].replace('_', '-')}
description: |
  {description}
---

{nwave_skill.get('content', '')}
'''
```

---

## 6. Directory Structure

### After Compilation

```
project/
├── dist/
│   └── skills/
│       ├── develop/
│       │   └── SKILL.md          # nWave format
│       └── refactor/
│           └── SKILL.md          # nWave format
│
└── .claude/
    └── skills/
        ├── develop/
        │   └── SKILL.md          # Claude Code format
        └── refactor/
            └── SKILL.md          # Claude Code format
```

### Build Process

```bash
# TOON compile generates both formats
python -m tools.toon.compiler skills/develop.toon

# Outputs:
# - dist/skills/develop/SKILL.md (nWave)
# - .claude/skills/develop/SKILL.md (Claude Code)
```

---

## 7. Validation Requirements

### nWave Format Validation

Parser/compiler MUST validate:
1. All required nWave fields present
2. Triggers are valid regex patterns
3. Agent association references valid agents
4. Workflow integration has wave/phase

### Claude Code Format Validation

Generated output MUST:
1. Have `name` and `description` in frontmatter
2. Use hyphenated name (no underscores)
3. Include meaningful description for semantic matching
4. Be valid Markdown

---

## 8. Impact on Step Files

### Step 01-04 (Skill Jinja2 Template)

**Modification Required**:
- Template must generate TWO output files
- Primary: nWave SKILL.md format (existing spec)
- Secondary: Claude Code SKILL.md format

### Step 01-05 (TOON Compiler)

**Modification Required**:
- Compiler must write to TWO locations
- `dist/skills/{id}/SKILL.md` (nWave)
- `.claude/skills/{name}/SKILL.md` (Claude Code)

### New Step Required

**Suggested**: Step 01-07 (Skill Orchestrator)
- Implement `SkillOrchestrator` class
- Unit tests for pattern matching
- Integration with nWave workflow

---

## 9. Migration Path

### Phase 1: Document (COMPLETE)
- This document establishes the dual-format strategy
- All stakeholders understand the incompatibility

### Phase 2: Update Templates
- Modify skill template to output both formats
- Update compiler to write to both locations

### Phase 3: Implement Orchestrator
- Build nWave Skill Orchestrator
- Add pattern matching with compiled regex
- Add agent authorization checks

### Phase 4: Integration Tests
- Verify both formats are valid
- Test pattern matching logic
- Test Claude Code discovery

---

## 10. Open Questions (Resolved)

| Question | Resolution |
|----------|------------|
| Who consumes SKILL.md? | **Dual consumer**: nWave Orchestrator + Claude Code Runtime |
| Is nWave format compatible? | **No**, requires dual-format output |
| Do we need regex patterns? | **Yes** for nWave; converted to description for Claude Code |
| How does agent binding work? | **nWave only**; Claude Code skills available to all agents |

---

## Version History

- **v1.0** (2026-01-14): Initial specification documenting incompatibility and dual-format strategy

## References

- [Anthropic Agent Skills Repository](https://github.com/anthropics/skills)
- [Engineering Blog: Equipping Agents with Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Claude Code Skills Documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
