# DW-MUTATION-TEST: Mutation Testing Quality Gate

---
## ORCHESTRATOR BRIEFING (MANDATORY)

**CRITICAL ARCHITECTURAL CONSTRAINT**: Sub-agents launched via Task tool have NO ACCESS to the Skill tool. They can ONLY use: Read, Write, Edit, Bash, Glob, Grep.

### What Orchestrator Must Do

When delegating this command to an agent via Task tool:

1. **Do NOT pass `/nw:mutation-test`** to the agent - they cannot execute it
2. **Create a complete agent prompt** with all instructions embedded inline
3. **Include**: project ID, detected language, tool configuration, threshold
4. **Embed**: mutation tool commands, report structure, quality criteria

### Agent Prompt Template

```text
You are a software-crafter agent executing mutation testing.

PROJECT: {project_id}
LANGUAGE: {detected_language}
MUTATION_TOOL: {tool_name}
THRESHOLD: {threshold}% minimum kill rate

YOUR TASK: Execute mutation testing to validate test suite quality.
1. Run mutation testing tool
2. Analyze surviving mutants
3. Create mutation report
4. Evaluate against threshold

OUTPUT FILE: docs/feature/{project_id}/mutation-report.md
```

### What NOT to Include in Agent Prompts

- "/nw:mutation-test"
- "Execute /nw:finalize next"
- Any skill or command reference

---

## CRITICAL: Agent Invocation Protocol

**YOU ARE THE COORDINATOR** - Orchestrate mutation testing through the software-crafter agent.

### STEP 1: Detect Project Language

```python
def detect_project_language(project_root):
    """Detect primary language from project configuration files."""
    detectors = [
        ('pyproject.toml', 'python'),
        ('setup.py', 'python'),
        ('requirements.txt', 'python'),
        ('pom.xml', 'java-maven'),
        ('build.gradle', 'java-gradle'),
        ('build.gradle.kts', 'kotlin-gradle'),
        ('package.json', 'javascript'),
        ('tsconfig.json', 'typescript'),
        ('*.csproj', 'csharp'),
        ('go.mod', 'go'),
        ('Cargo.toml', 'rust'),
    ]

    for pattern, language in detectors:
        if '*' in pattern:
            if glob.glob(os.path.join(project_root, pattern)):
                return language
        elif os.path.exists(os.path.join(project_root, pattern)):
            return language

    return 'unknown'

language = detect_project_language('.')
```

### STEP 2: Select Mutation Testing Tool

| Language | Tool | Install Command | Run Command |
|----------|------|-----------------|-------------|
| Python | cosmic-ray | `.venv-mutation/bin/pip install cosmic-ray` | `.venv-mutation/bin/cosmic-ray exec {config} {session}.sqlite` |
| Java (Maven) | PIT | Add plugin to pom.xml | `mvn pitest:mutationCoverage` |
| Java (Gradle) | PIT | Add plugin to build.gradle | `gradle pitest` |
| JavaScript | Stryker | `npm i -D @stryker-mutator/core` | `npx stryker run` |
| TypeScript | Stryker | `npm i -D @stryker-mutator/core @stryker-mutator/typescript-checker` | `npx stryker run` |
| C# | Stryker.NET | `dotnet tool install -g dotnet-stryker` | `dotnet stryker` |
| Go | go-mutesting | `go install github.com/zimmski/go-mutesting/cmd/go-mutesting@latest` | `go-mutesting ./...` |

### STEP 2.1: Python Virtual Environment Setup (MANDATORY for Python)

PEP 668 (externally-managed environments) blocks `pip install` on modern Linux distributions (Ubuntu 24.04+, Debian 12+). All Python mutation testing tools MUST be installed in an isolated virtual environment.

```bash
VENV_DIR=".venv-mutation"
if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
  "$VENV_DIR/bin/pip" install cosmic-ray
fi

# Verify
.venv-mutation/bin/cosmic-ray --version

# All subsequent cosmic-ray commands use:
.venv-mutation/bin/cosmic-ray init ...
.venv-mutation/bin/cosmic-ray exec ...
.venv-mutation/bin/cr-report ...
```

Add `.venv-mutation/` to `.gitignore` if not present.

**Background execution**: When running as part of `/nw:develop` Phase 2.25, each `cosmic-ray exec` can be launched as a background job (using `run_in_background`) to run in parallel with architecture refactoring.

### STEP 2.5: Scope Completeness Check (MANDATORY)

Before configuring mutation testing, the orchestrator MUST discover the
complete implementation scope. This prevents partial testing that creates
false confidence (e.g., testing 1 of 3 implementation files and reporting
aggregate 100% when actual coverage is 33%).

**DISCOVERY METHOD** (in priority order):

1. **FROM execution-status.yaml** (most reliable — actual files modified):
   ```
   Read completed_steps[*].files_modified.implementation
   Deduplicate into file list
   ```

2. **FROM roadmap.yaml implementation_scope** (declared scope):
   ```
   Read implementation_scope.source_directories
   Use: find {dir} -name "*.py" -not -path "*__pycache__*" -not -name "__init__.py"
   ```

3. **FROM git history** (fallback):
   ```
   Use: git log --all --grep="{project-id}" --format=%H
   Then: git diff --name-only {first}^ {last} | grep "^src/"
   ```

**VALIDATION RULES**:

**Rule 1 — COMPLETENESS**:
Every discovered implementation file MUST have mutation testing coverage.
Missing file = BLOCK (create config, then continue).

**Rule 2 — SANITY**:
Expected mutants = implementation_lines x 0.05 to 0.10
- If actual_mutants < expected_min x 0.5: WARN "Mutant count seems low — verify scope"
- If actual_mutants < expected_min x 0.25: BLOCK "Mutant count too low — likely missing files"

**Rule 3 — PER-COMPONENT**:
Report mutation score per implementation file, not just aggregate.
Each component's score must be visible in the mutation report.

**MUTATION ARTIFACTS LOCATION**:
All mutation testing configs and session files go in:
```
docs/feature/{project-id}/mutation/
├── cosmic-ray-{component}.toml    # Per-component configs
├── {component}-session.sqlite     # Session databases (gitignored)
└── mutation-report.md             # Final report
```
These are ephemeral quality gate artifacts, disposed during `/nw:finalize`.

### STEP 3: Pre-Invocation Validation Checklist

Before invoking Task tool, verify ALL items:
- [ ] Language detected or explicitly specified
- [ ] Mutation tool available for the language
- [ ] Test suite exists and passes
- [ ] Source code paths identified
- [ ] Threshold configured (default: 75%)
- [ ] Implementation scope discovered (file list populated)
- [ ] ALL implementation files covered by mutation config
- [ ] Expected mutant range calculated and logged
- [ ] Per-component reporting configured

### STEP 4: Invoke Software-Crafter Agent Using Task Tool

**MANDATORY**: Use the Task tool with complete inline instructions.

```
Task: "You are the software-crafter agent (Crafty).

Your specific role: Execute mutation testing and create quality report

Project: {project_id}
Language: {language}
Tool: {mutation_tool}
Threshold: {threshold}%

═══════════════════════════════════════════════════════════
⚠️  TASK BOUNDARY - READ BEFORE EXECUTING
═══════════════════════════════════════════════════════════
YOUR ONLY TASK: Run mutation testing and analyze results
INPUT: Project source code and test suite
OUTPUT FILE: docs/feature/{project_id}/mutation-report.md
FORBIDDEN ACTIONS:
  ❌ DO NOT proceed to finalize
  ❌ DO NOT modify production code
REQUIRED: Return control to orchestrator after completion
═══════════════════════════════════════════════════════════

EXECUTION STEPS:

1. VERIFY PREREQUISITES
   - Check mutation tool is installed: {check_command}
   - If not installed, provide installation instructions and EXIT
   - Verify test suite passes: {test_command}

2. RUN MUTATION TESTING
   - Execute: {mutation_command}
   - Capture output (may take 10-30 minutes for large projects)
   - Handle timeout gracefully (max 30 minutes)

3. PARSE RESULTS
   - Extract mutation score (killed / total mutants)
   - Identify surviving mutants
   - Categorize mutants by file/module

4. CREATE MUTATION REPORT
   Write to docs/feature/{project_id}/mutation/mutation-report.md:

   ```markdown
   # Mutation Testing Report

   **Project**: {project_id}
   **Date**: {current_timestamp}
   **Language**: {language}
   **Tool**: {mutation_tool}

   ## Scope Completeness

   - Implementation files discovered: {N}
   - Implementation files tested: {N} (100%)
   - Expected mutant range: {min}-{max}
   - Actual mutants: {actual} (within range: YES/NO)

   ## Per-Component Results

   | Component | Lines | Mutants | Killed | Score | Status |
   |-----------|-------|---------|--------|-------|--------|
   | {file1}   | {L}   | {M}    | {K}    | {S}%  | PASS/WARN |
   | {file2}   | {L}   | {M}    | {K}    | {S}%  | PASS/WARN |
   | **TOTAL** | {L}   | {M}    | {K}    | {S}%  | PASS/FAIL |

   Threshold enforcement:
   - AGGREGATE score must meet threshold ({threshold}%)
   - ANY individual component below threshold triggers WARNING
   - Security-critical components (validators, auth, access control) must meet
     threshold INDIVIDUALLY — aggregate pass does not compensate

   ## Surviving Mutants Analysis

   ### By File

   | File | Survived | Line | Mutation |
   |------|----------|------|----------|
   | ... | ... | ... | ... |

   ### Recommendations

   {For each surviving mutant, suggest what test would kill it}

   ## Equivalent Mutants (if any)

   {Document mutants that are semantically equivalent and cannot be killed}
   ```

5. EVALUATE THRESHOLD
   - If score >= {threshold}%: Report PASS
   - If score < {threshold}%: Report FAIL with recommendations

6. RETURN RESULTS
   - Print summary to console
   - Report file path
   - Return pass/fail status
"
```

---

## Language-Specific Configuration

### Python (mutmut)

**Prerequisites**: pytest, mutmut
**Config file**: `setup.cfg` or `pyproject.toml`

```ini
[mutmut]
paths_to_mutate=src/
tests_dir=tests/
runner=python -m pytest
```

### Java (PIT)

**Prerequisites**: Maven or Gradle with PIT plugin
**Config**: pom.xml or build.gradle

```xml
<!-- Maven pom.xml -->
<plugin>
    <groupId>org.pitest</groupId>
    <artifactId>pitest-maven</artifactId>
    <version>1.15.0</version>
    <configuration>
        <targetClasses>
            <param>com.example.*</param>
        </targetClasses>
        <mutationThreshold>75</mutationThreshold>
    </configuration>
</plugin>
```

### JavaScript/TypeScript (Stryker)

**Prerequisites**: npm/yarn, stryker
**Config**: stryker.conf.js

```javascript
module.exports = {
  mutator: "typescript",
  packageManager: "npm",
  reporters: ["html", "progress"],
  testRunner: "jest",
  thresholds: { high: 80, low: 60, break: 75 }
};
```

---

## Success Criteria

- [ ] Language detected correctly
- [ ] Mutation tool executed without errors
- [ ] Mutation score calculated
- [ ] Report created at correct path
- [ ] Threshold evaluation complete

## Quality Gate

| Score | Status | Action |
|-------|--------|--------|
| >= 75% | PASS | Proceed to finalize |
| 60-75% | WARN | Review surviving mutants, may proceed with justification |
| < 60% | FAIL | Add tests before proceeding |

## Skip Conditions

Mutation testing may be skipped if:
1. Language not supported (no mutation tool available)
2. Project explicitly opts out via `.mutation-config.yaml`
3. Test suite is empty or broken

All skips must be documented with justification.

---

## Next Wave

**After Mutation Testing**: Phase 8 - Finalize
**Handoff**: Orchestrator continues develop.md workflow
