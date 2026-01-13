# Root Cause Analysis: Subagent Invocation Failure in Slash Commands

**Date**: 2025-10-16
**Analyst**: Sage (troubleshooter)
**Problem**: Commands like `/nw:execute` and `/nw:review` fail to invoke specified subagents; main agent handles tasks directly instead

---

## Executive Summary

Commands with agent parameters (`/nw:execute`, `/nw:review`, `/nw:roadmap`, `/nw:split`, `/nw:finalize`) declare agent invocation capability in their YAML frontmatter but **do not contain actual invocation mechanisms** in their implementation. The commands document *how* a subagent *should* be invoked but lack the critical instruction that tells Claude Code to *actually invoke* the subagent using the Task tool.

**Impact**: High - Distributed workflow system cannot function as designed; tasks meant for specialized agents are handled by generalist main agent, degrading quality and violating architecture principles.

**Root Causes Identified**: 2 (multi-causal problem)

---

## Investigation Methodology

Applied Toyota 5 Whys technique with multi-causal investigation:
- Examined slash command implementations (`execute.md`, `review.md`, `develop.md`)
- Compared working agent-activation commands vs non-working agent-parameter commands
- Analyzed build process (command_processor.py)
- Traced from symptom → source files → generated outputs

---

## Evidence Collection

### Evidence 1: Agent-Parameter Commands Lack Invocation Instructions

**Source File**: `/mnt/c/Repositories/Projects/ai-craft/nWave/tasks/dw/execute.md`

**YAML Frontmatter** (Lines 1-8):
```yaml
---
description: 'Execute atomic task with state tracking [agent] [step-file-path]'
argument-hint: '[agent] [step-file-path] - Example: @researcher "steps/01-01.json"'
agent-activation:
  required: false
  agent-parameter: true
  agent-command: "*workflow-execute"
---
```

**Analysis**:
- `agent-parameter: true` declares agent comes from command parameter
- `agent-command: "*workflow-execute"` specifies command to send to agent
- **CRITICAL MISSING**: No instruction to actually invoke the agent using Task tool

**Agent Invocation Section** (Lines 53-58):
```markdown
## Agent Invocation

@{specified-agent}

Execute task from: {step-file-path}

### Primary Task Instructions
```

**Analysis**:
- This is **documentation** of what should happen, not executable instruction
- Template placeholders `@{specified-agent}` and `{step-file-path}` are never substituted
- No Task tool invocation present

---

### Evidence 2: Working Commands Use Different Pattern

**Source File**: `/mnt/c/Repositories/Projects/ai-craft/nWave/tasks/dw/develop.md`

**YAML Frontmatter** (Lines 1-8):
```yaml
---
agent-activation:
  required: true
  agent-id: software-crafter
  agent-name: "Crafty"
  agent-command: "*develop"
  auto-activate: true
---
```

**Analysis**:
- `required: true` declares agent activation mandatory
- `agent-id: software-crafter` specifies **fixed** agent (not parameter)
- `auto-activate: true` triggers automatic agent invocation

**Key Difference**:
- **Working commands** (`/nw:develop`, `/nw:discuss`) have `agent-id` field with fixed agent
- **Non-working commands** (`/nw:execute`, `/nw:review`) have `agent-parameter: true` but no fixed `agent-id`
- Build system likely handles `auto-activate: true` but not `agent-parameter: true`

---

### Evidence 3: Review Command Has Same Pattern

**Source File**: `/mnt/c/Repositories/Projects/ai-craft/nWave/tasks/dw/review.md`

**YAML Frontmatter** (Lines 1-8):
```yaml
---
description: 'Expert critique and quality review [agent] [artifact-type] [path] - Types: roadmap, task, implementation'
argument-hint: '[agent] [artifact-type] [artifact-path] - Example: @software-crafter task "steps/01-01.json"'
agent-activation:
  required: false
  agent-parameter: true
  agent-command: "*workflow-review"
---
```

**Agent Invocation Section** (Lines 47-52):
```markdown
## Agent Invocation

@{specified-agent}

Perform {artifact-type} review of: {artifact-path}

### Primary Task Instructions
```

**Analysis**: Identical pattern to `/nw:execute` - declares capability but lacks implementation

---

### Evidence 4: Build System Copies Files Verbatim

**Source File**: `/mnt/c/Repositories/Projects/ai-craft/tools/processors/command_processor.py`

**Key Method** (Lines 182-218):
```python
def generate_command_content(self, task_file: Path, config: Dict[str, Any]) -> str:
    """Generate complete command content with Claude Code compatible YAML frontmatter."""
    # Read source task file
    task_content = self.file_manager.read_file(task_file)

    # Generate Claude Code compatible YAML frontmatter FIRST
    frontmatter = self.generate_command_frontmatter(task_name, command_info)

    # Generate command header
    header = self.generate_command_header(task_name, command_info, wave_info)

    # Process task content
    processed_content = self.process_task_dependencies(task_content)

    # Combine frontmatter, header and content
    return f"{frontmatter}{header}{processed_content}"
```

**Analysis**:
- Build process reads source task markdown
- Adds frontmatter and header
- **Does NOT substitute placeholders** like `@{specified-agent}`
- **Does NOT inject Task tool invocation** for `agent-parameter: true` commands
- Copies content mostly verbatim from source to output

---

## 5 Whys Analysis: Path A (Missing Invocation Logic)

**WHY #1A**: Why doesn't the subagent get invoked?
**ANSWER**: The slash command markdown contains no instruction to invoke a subagent using the Task tool.
**EVIDENCE**: Lines 53-112 of execute.md show documentation text, not executable Task tool invocation.

**WHY #2A**: Why is there no Task tool invocation in the command?
**ANSWER**: The source task file (`nWave/tasks/dw/execute.md`) contains only documentation of invocation, not implementation.
**EVIDENCE**: Agent Invocation section uses template placeholders `@{specified-agent}` that are never substituted.

**WHY #3A**: Why does the source file lack implementation?
**ANSWER**: The task file was written as a specification document describing desired behavior, not as an executable instruction set.
**EVIDENCE**: Language like "Agent receives complete context" and "Execute this task and provide outputs" is descriptive, not prescriptive to Claude Code.

**WHY #4A**: Why was it written as specification rather than implementation?
**ANSWER**: Author assumed Claude Code would interpret agent-parameter declaration in YAML frontmatter and automatically invoke the agent.
**EVIDENCE**: YAML frontmatter declares `agent-parameter: true` and `agent-command: "*workflow-execute"`, suggesting expected automatic handling.

**WHY #5A (ROOT CAUSE 1)**: Why was automatic handling assumed?
**ROOT CAUSE 1**: Design gap between YAML frontmatter capabilities and build system implementation - `agent-parameter: true` is not handled by build system or Claude Code, only `auto-activate: true` with fixed `agent-id` works.

---

## 5 Whys Analysis: Path B (Build System Limitation)

**WHY #1B**: Why doesn't the build system inject invocation logic?
**ANSWER**: The command_processor.py does not contain logic to handle `agent-parameter: true` declarations.
**EVIDENCE**: `generate_command_content()` method (lines 182-218) only concatenates frontmatter + header + content, no template substitution or Task tool injection.

**WHY #2B**: Why doesn't command_processor handle agent-parameter?
**ANSWER**: The build system was designed to handle fixed agent assignments (`agent-id` + `auto-activate`), not dynamic agent parameters.
**EVIDENCE**: Working commands like `/nw:develop` use `agent-id: software-crafter` and `auto-activate: true` pattern, which the system handles.

**WHY #3B**: Why was dynamic agent handling not implemented?
**ANSWER**: Dynamic agent invocation from parameters is architecturally more complex than fixed agent activation - requires parameter parsing, validation, and Task tool injection.
**EVIDENCE**: Fixed activation is simple (if auto-activate: true, invoke agent-id), but parameter-based requires runtime extraction of agent from command arguments.

**WHY #4B**: Why is parameter-based invocation more complex?
**ANSWER**: Claude Code slash commands expand at parse time (before execution), but agent parameter values are only known at runtime (user provides them).
**EVIDENCE**: `/nw:execute @researcher "file.json"` - the `@researcher` value is not available when slash command markdown is generated during build.

**WHY #5B (ROOT CAUSE 2)**: Why can't parse-time expansion handle runtime values?
**ROOT CAUSE 2**: Architectural limitation of static slash command expansion model - commands are expanded to static markdown before execution, but parameter-based agent selection requires dynamic behavior at execution time.

---

## Root Causes Summary

### Root Cause 1: Design Gap - Unimplemented YAML Frontmatter Feature
**Nature**: Specification-Implementation Mismatch
**Location**: YAML `agent-activation` specification vs. build system capabilities

**Details**: The YAML frontmatter supports declaring `agent-parameter: true` to indicate an agent should be invoked based on command parameters, but neither the build system (`command_processor.py`) nor Claude Code runtime implements this feature. Only `auto-activate: true` with fixed `agent-id` is implemented.

**Evidence Files**:
- `/mnt/c/Repositories/Projects/ai-craft/nWave/tasks/dw/execute.md` (lines 4-7)
- `/mnt/c/Repositories/Projects/ai-craft/nWave/tasks/dw/review.md` (lines 4-7)
- `/mnt/c/Repositories/Projects/ai-craft/tools/processors/command_processor.py` (lines 182-218)

---

### Root Cause 2: Architectural Limitation - Static Expansion vs. Dynamic Parameters
**Nature**: Architectural Constraint
**Location**: Slash command expansion model

**Details**: Claude Code expands slash commands to markdown at parse time (static), but parameter-based agent selection requires knowing the parameter value at execution time (dynamic). The current architecture cannot bridge this static-to-dynamic gap without explicit Task tool invocation instructions in the expanded markdown.

**Evidence Files**:
- Comparison of `/nw:develop` (static, works) vs. `/nw:execute` (dynamic, fails)
- Build output in `/mnt/c/Repositories/Projects/ai-craft/dist/ide/commands/nw/execute.md` shows static content

---

## Backwards Chain Validation

### Validation of Root Cause 1 → Symptom
**Chain**: Design gap (unimplemented agent-parameter) → No invocation logic in command → Main agent handles task
**Validation**: ✅ VALID
- If `agent-parameter: true` were implemented, build system would inject Task tool invocation
- Injected invocation would cause subagent to handle task
- Without implementation, no invocation occurs, main agent proceeds

### Validation of Root Cause 2 → Symptom
**Chain**: Static expansion model → Cannot inject runtime parameter values → No dynamic agent selection → Main agent handles task
**Validation**: ✅ VALID
- Static markdown cannot contain "invoke agent from parameter $1"
- Requires explicit Task tool invocation with specific agent name
- Without ability to inject dynamic values, command must be handled by main agent

### Cross-Validation of Root Causes
**Test**: Do both root causes contradict each other?
**Result**: ❌ NO CONTRADICTION
- Root Cause 1 explains *why* no invocation logic exists (feature not implemented)
- Root Cause 2 explains *why* implementing it is non-trivial (architectural constraint)
- Both are necessary causes contributing to the problem

---

## Completeness Check

### Are any contributing factors missed?

**Question 1**: Could this be a Claude Code bug in parsing agent-parameter?
**Assessment**: No - evidence shows agent-parameter is a custom extension not recognized by Claude Code. It's a build system feature that was declared but not implemented.

**Question 2**: Could template substitution fix this without build changes?
**Assessment**: No - even with placeholder substitution (e.g., `@{specified-agent}` → actual value), there's still no Task tool invocation instruction present. The entire invocation mechanism is missing.

**Question 3**: Could working commands provide a pattern to copy?
**Assessment**: Partially - working commands use `auto-activate: true` but only work with fixed `agent-id`. This pattern cannot be directly applied to parameter-based agent selection without architectural changes.

**Conclusion**: Analysis is comprehensive - both root causes identified explain the full symptom, no major contributing factors missed.

---

## Recommended Solutions (NOT IMPLEMENTED - ANALYSIS ONLY)

### Solution 1: Implement Agent-Parameter Handling in Build System
**Approach**: Extend `command_processor.py` to detect `agent-parameter: true` and inject Task tool invocation template

**Pseudo-implementation**:
```python
def inject_agent_invocation(self, content: str, agent_activation: dict) -> str:
    if agent_activation.get('agent-parameter'):
        # Insert Task tool invocation at top of content
        agent_command = agent_activation.get('agent-command', '*execute')
        invocation = f"""
        **CRITICAL**: Extract agent name from first parameter (format: @agent-name)

        Then invoke using Task tool:
        ```
        You are the coordinator. The user has specified an agent parameter.
        Use the Task tool to invoke the specified agent with the command.

        Example: If user provides @researcher, invoke:
        Task: "You are @researcher. Execute {agent_command} with provided arguments."
        ```
        """
        return invocation + content
    return content
```

**Limitations**: Still requires runtime parameter extraction logic that may be complex

---

### Solution 2: Change Commands to Use Fixed Coordinator Agent
**Approach**: Create a `workflow-coordinator` agent that acts as dispatcher for all workflow commands

**Pattern**:
```yaml
---
agent-activation:
  required: true
  agent-id: workflow-coordinator
  agent-name: "Coordinator"
  agent-command: "*coordinate"
  auto-activate: true
---
```

**Coordinator Logic**:
- Read command parameters
- Extract agent name (e.g., `@researcher`)
- Use Task tool to invoke that agent with remaining parameters
- Return results to user

**Advantages**:
- Works with existing auto-activate mechanism
- Centralizes agent dispatch logic
- No build system changes needed

---

### Solution 3: Hybrid - Explicit Invocation Instructions in Markdown
**Approach**: Add explicit Task tool invocation instructions directly in command markdown (manual solution)

**Example Addition to execute.md**:
```markdown
## CRITICAL EXECUTION INSTRUCTION

**YOU ARE THE COORDINATOR** - Do not execute the task yourself.

**STEP 1**: Extract agent name from first parameter
- User provides: `/nw:execute @researcher "file.json"`
- Extract: `@researcher`

**STEP 2**: Extract remaining parameters
- Extract: `"file.json"` (step-file-path)

**STEP 3**: Invoke agent using Task tool
```
Task: "You are @researcher.
Read the step file at: {step-file-path}
Execute the task as specified in the file.
Update the file with execution results."
```

Return results to user.
```

**Advantages**:
- No build system changes required
- Works immediately
- Clear, explicit instructions

**Disadvantages**:
- Manual, repetitive across commands
- Prone to human error during updates

---

## Affected Commands

All commands with `agent-parameter: true`:
1. `/nw:execute` - Task execution engine
2. `/nw:review` - Quality review system
3. `/nw:roadmap` - Planning document creation
4. `/nw:split` - Task file generation
5. `/nw:finalize` - Workflow completion

All currently non-functional for subagent invocation.

---

## Risk Assessment

**Severity**: HIGH
**Impact**: Distributed workflow system cannot function - all specialized agent tasks handled by generalist main agent

**Consequences**:
- Lower quality outputs (wrong agent expertise applied)
- Violation of architecture principles (agent specialization bypassed)
- Context degradation (main agent accumulates context across multiple tasks)
- User confusion (commands don't work as documented)

**Urgency**: HIGH - Core functionality of nWave workflow system blocked

---

## Verification Strategy (For Implementer)

Once solution implemented, verify with:

**Test 1**: Execute command with agent parameter
```bash
/nw:execute @researcher "docs/workflow/test/steps/01-01.json"
```
**Expected**: Researcher agent activates and handles task, not main agent

**Test 2**: Review command with agent parameter
```bash
/nw:review @software-crafter task "docs/workflow/test/steps/02-01.json"
```
**Expected**: Software-crafter agent activates and provides review

**Test 3**: Verify main agent does NOT handle task
**Expected**: Main agent acts only as coordinator, delegating to specified agent

---

## Related Issues

**Potential Related Problems** (not investigated):
1. Do commands with `agent-parameter: true` have any working use cases?
2. Are there other unimplemented YAML frontmatter features?
3. Does Claude Code have any native support for parameter-based agent selection?

---

## Conclusion

The subagent invocation failure is caused by **two complementary root causes**:

1. **Design Gap**: YAML frontmatter feature `agent-parameter: true` was specified but never implemented in build system or runtime
2. **Architectural Limitation**: Static slash command expansion model cannot easily support dynamic agent selection from runtime parameters

**Both causes must be addressed** for full solution. The hybrid approach (Solution 3) provides immediate workaround, while Solutions 1 or 2 provide systematic long-term fixes.

**Critical files requiring attention**:
- Source: `/mnt/c/Repositories/Projects/ai-craft/nWave/tasks/dw/execute.md`
- Source: `/mnt/c/Repositories/Projects/ai-craft/nWave/tasks/dw/review.md`
- Build: `/mnt/c/Repositories/Projects/ai-craft/tools/processors/command_processor.py`
- Output: `/mnt/c/Repositories/Projects/ai-craft/dist/ide/commands/nw/*.md` (5 commands)

---

**Analysis Complete**: 2025-10-16
**Analyst**: Sage (troubleshooter)
