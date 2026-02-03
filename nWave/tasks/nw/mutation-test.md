# DW-MUTATION-TEST: Feature-Scoped Mutation Testing Quality Gate

---

## ⚡ PERFORMANCE CRITICAL: Feature-Scoped Testing (NOT Full Test Suite)

**MANDATORY**: Use `scripts/mutation/generate_scoped_configs.py` to create per-component configs with **feature-scoped test commands**.

```bash
# ✅ CORRECT: Generate feature-scoped configs (10-50x faster)
python scripts/mutation/generate_scoped_configs.py {project-id}

# ❌ WRONG: Running full test suite per mutant (takes forever)
test-command = "pytest -x tests/"  # DON'T DO THIS
```

**Why Feature-Scoped**:
- Each mutant runs **only tests that exercise that component** (unit + acceptance + integration)
- **10-50x faster** than running entire test suite per mutant
- Same accuracy (all relevant test types included)
- Example: Validator mutation runs validator tests + acceptance tests that use validator (NOT config tests, adapter tests, etc.)

---

## ARCHITECTURAL PRINCIPLE: Hexagonal Architecture + Outside-In TDD

**CRITICAL**: Source code is organized by HEXAGONAL ARCHITECTURE (adapters/driven,
adapters/drivers, application, domain, ports), NOT by feature directories.

Files to mutate are extracted from **commits** (execution-status.yaml), not assumed
from directory structure. Tests are NOT mutated but executed to validate implementation.

| Aspect | OLD (Per-File) | v2.0 (Commit-Based, Full Suite) | v2.1 (Feature-Scoped) ✅ |
|--------|----------------|--------------------------------|-------------------------|
| Config | One per .py file | ONE with file list | One per component |
| Source | Assume `src/feature/` | Extract from execution-status.yaml | Extract from execution-status.yaml |
| module-path | Directory path | List of specific files | One file per config |
| Test scope | Unit only | **ALL tests** (`tests/`) ❌ SLOW | **Scoped tests** (relevant only) ✅ FAST |
| Speed | Baseline | 1x (full suite per mutant) | **10-50x faster** |
| Test types | Unit | All (acceptance + integration + unit) | All (acceptance + integration + unit) |

**Why Directory-Based Fails with Hexagonal Architecture**:
- Source files are scattered across adapters/, application/, domain/, ports/
- No `src/feature/` directory exists — architecture layers span multiple features
- Only commit history knows which files belong to the current feature

---

## ORCHESTRATOR BRIEFING (MANDATORY)

**CRITICAL ARCHITECTURAL CONSTRAINT**: Sub-agents launched via Task tool have NO ACCESS to the Skill tool. They can ONLY use: Read, Write, Edit, Bash, Glob, Grep.

### Usage

```bash
/nw:mutation-test {project-id} {test-scope}

# Examples:
/nw:mutation-test des-hook-enforcement tests/des/
/nw:mutation-test auth-upgrade tests/auth/
/nw:mutation-test payment-gateway tests/payment/
```

### What Orchestrator Must Do

When delegating this command to an agent via Task tool:

1. **Do NOT pass `/nw:mutation-test`** to the agent - they cannot execute it
2. **Extract implementation files** from `docs/feature/{project-id}/execution-status.yaml`
3. **Create a complete agent prompt** with file list embedded inline
4. **Use SINGLE CONFIG** with `module-path = [list of files]`

### Agent Prompt Template

```text
You are a software-crafter agent executing commit-based mutation testing.

PROJECT: {project_id}
IMPLEMENTATION FILES: {files_list}     # Extracted from execution-status.yaml
TEST SCOPE: {test_scope}               # e.g., tests/des/
THRESHOLD: {threshold}% minimum kill rate

YOUR TASK: Execute mutation testing against ALL tests for the implementation.
1. Create ONE cosmic-ray config with module-path = [list of specific files]
2. Run mutation testing with ALL tests (acceptance + integration + unit)
3. Analyze surviving mutants
4. Create mutation report with per-file breakdown

OUTPUT FILE: docs/feature/{project_id}/mutation/mutation-report.md
```

### What NOT to Include in Agent Prompts

- "/nw:mutation-test"
- "Execute /nw:finalize next"
- Any skill or command reference
- Directory-based module-path (OBSOLETE — use file list)

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

### STEP 2.5: Feature-Scoped Config Generation (Hexagonal Architecture)

With hexagonal architecture, source files are organized by LAYER (adapters, application,
domain, ports), NOT by feature. Implementation files must be extracted from commits.

**AUTOMATED APPROACH** (✅ RECOMMENDED):

Use the provided script to automatically generate feature-scoped configs:

```bash
# Generate per-component configs with scoped test commands
python scripts/mutation/generate_scoped_configs.py {project-id}

# Output:
# ✓ src/des/application/validator.py (573 LOC)
#   Tests: 2 file(s)
#     - tests/des/unit/application/test_validator.py
#     - tests/des/acceptance/test_hook_enforcement_steps.py
#   Config: cosmic-ray-des_application_validator.toml
#
# ✓ src/des/adapters/drivers/hooks/claude_code_hook_adapter.py (178 LOC)
#   Tests: 2 file(s)
#     - tests/des/unit/adapters/drivers/hooks/test_claude_code_hook_adapter.py
#     - tests/des/acceptance/test_hook_enforcement_steps.py
#   Config: cosmic-ray-des_adapters_drivers_hooks_claude_code_hook_adapter.toml
```

**What the script does**:
1. Reads `execution-status.yaml` to extract implementation files
2. For each file, finds its test files:
   - **Unit tests**: `src/module/foo.py` → `tests/module/unit/test_foo.py`
   - **Acceptance tests**: All acceptance tests for the feature
   - **Integration tests**: Integration tests in the module
3. Generates `cosmic-ray-{component}.toml` with scoped `test-command`

**MANUAL APPROACH** (if script unavailable):

1. **Extract implementation files** from execution-status.yaml:
   ```python
   import yaml

   with open(f'docs/feature/{project_id}/execution-status.yaml', 'r') as f:
       exec_status = yaml.safe_load(f)

   implementation_files = []
   for step in exec_status.get('execution_status', {}).get('completed_steps', []):
       files = step.get('files_modified', {}).get('implementation', [])
       implementation_files.extend(files)

   implementation_files = list(set(implementation_files))
   ```

2. **Map to test files** (for each implementation file):
   - Unit test: Follow naming convention
   - Acceptance tests: Find via feature name
   - Create config with **scoped** test-command (NOT `pytest -x tests/`)

**VALIDATION RULES**:

**Rule 1 — FILES EXIST**:
All extracted implementation files must exist on disk.
Missing files = BLOCK (verify execution-status.yaml is up to date).

**Rule 2 — SANITY CHECK**:
After mutation run, verify mutant count is reasonable:
- Count implementation lines: `wc -l {file1} {file2} ... | tail -1`
- Expected mutants: total_lines × 0.05 to 0.10
- If actual_mutants < expected × 0.25: WARN "Check if all files extracted"

**Rule 3 — PER-FILE BREAKDOWN**:
Cosmic-ray automatically provides per-file breakdown in its report.
One config with file list covers entire implementation.

**MUTATION ARTIFACTS LOCATION**:
```
docs/feature/{project-id}/mutation/
├── cosmic-ray-feature.toml        # ONE config with file list
├── session.sqlite                 # Session database (gitignored)
└── mutation-report.md             # Final report with per-file breakdown
```
These are ephemeral quality gate artifacts, disposed during `/nw:finalize`.

### STEP 3: Pre-Invocation Validation Checklist

Before invoking Task tool, verify ALL items:
- [ ] execution-status.yaml exists at `docs/feature/{project-id}/execution-status.yaml`
- [ ] Implementation files extracted (non-empty list)
- [ ] All implementation files exist on disk
- [ ] Test scope path exists (e.g., `tests/des/`)
- [ ] Language detected (Python for cosmic-ray)
- [ ] Mutation venv exists (`.venv-mutation/`)
- [ ] Test suite passes: `pytest -x {test_scope}`
- [ ] Threshold configured (default: 80%)

### STEP 4: Invoke Software-Crafter Agent Using Task Tool

**MANDATORY**: Use the Task tool with complete inline instructions.

```
Task: "You are the software-crafter agent executing commit-based mutation testing.

Project: {project_id}
Implementation Files: {implementation_files}  # Extracted from execution-status.yaml
Test Scope: {test_scope}
Threshold: {threshold}%

═══════════════════════════════════════════════════════════
⚠️  TASK BOUNDARY - READ BEFORE EXECUTING
═══════════════════════════════════════════════════════════
YOUR ONLY TASK: Run mutation testing for implementation files
INPUT: Implementation file list + ALL tests (acceptance, integration, unit)
OUTPUT FILE: docs/feature/{project_id}/mutation/mutation-report.md
FORBIDDEN ACTIONS:
  ❌ DO NOT proceed to finalize
  ❌ DO NOT modify production code
  ❌ DO NOT use directory-based module-path (use file list)
REQUIRED: Return control to orchestrator after completion
═══════════════════════════════════════════════════════════

EXECUTION STEPS:

1. VERIFY PREREQUISITES
   - Check cosmic-ray installed: .venv-mutation/bin/cosmic-ray --version
   - Verify test suite passes: pytest -x {test_scope}

2. CREATE COMMIT-BASED CONFIG
   Create docs/feature/{project_id}/mutation/cosmic-ray-feature.toml:

   ```toml
   [cosmic-ray]
   module-path = [
       \"{file1}\",
       \"{file2}\",
       \"{file3}\"
   ]
   timeout = 30.0
   excluded-modules = []
   test-command = \"pytest -x {test_scope}\"

   [cosmic-ray.distributor]
   name = \"local\"

   [cosmic-ray.execution-engine]
   name = \"local\"
   ```

   NOTE: module-path is a LIST of specific files (not a directory).
   This ensures ONLY implementation files from this feature are mutated.

3. RUN MUTATION TESTING
   ```bash
   # Initialize session
   .venv-mutation/bin/cosmic-ray init \\
     docs/feature/{project_id}/mutation/cosmic-ray-feature.toml \\
     docs/feature/{project_id}/mutation/session.sqlite

   # Execute mutations (may take 10-30 minutes)
   .venv-mutation/bin/cosmic-ray exec \\
     docs/feature/{project_id}/mutation/cosmic-ray-feature.toml \\
     docs/feature/{project_id}/mutation/session.sqlite

   # Generate report
   .venv-mutation/bin/cr-report \\
     docs/feature/{project_id}/mutation/session.sqlite
   ```

4. PARSE RESULTS AND CREATE REPORT
   Write to docs/feature/{project_id}/mutation/mutation-report.md:

   ```markdown
   # Mutation Testing Report

   **Project**: {project_id}
   **Date**: {timestamp}
   **Approach**: Commit-Based (hexagonal architecture compatible)
   **Test Scope**: {test_scope} (acceptance + integration + unit)

   ## Implementation Files (from execution-status.yaml)

   {list of files extracted from commits}

   ## Configuration

   - Approach: Commit-Based (files extracted from execution-status.yaml)
   - Config: ONE cosmic-ray config with module-path = [file list]
   - Tests: ALL tests executed (not just unit tests)

   ## Per-File Results (from cosmic-ray)

   | File | Mutants | Killed | Survived | Score | Status |
   |------|---------|--------|----------|-------|--------|
   | {file1.py} | {M} | {K} | {S} | {P}% | ✅/⚠️ |
   | {file2.py} | {M} | {K} | {S} | {P}% | ✅/⚠️ |
   | ... | ... | ... | ... | ... | ... |
   | **TOTAL** | {M} | {K} | {S} | {P}% | PASS/FAIL |

   ## Threshold Evaluation

   - Required: {threshold}%
   - Achieved: {actual_score}%
   - Status: {PASS if actual >= threshold else FAIL}

   ## Surviving Mutants

   {List surviving mutants with file, line, mutation type}
   {Suggest what test would kill each}
   ```

5. EVALUATE AND RETURN
   - If score >= {threshold}%: Report PASS
   - If score < {threshold}%: Report FAIL with recommendations
   - Print summary to console
"
```

---

## Language-Specific Configuration

### Python (cosmic-ray) — RECOMMENDED

**Prerequisites**: pytest, cosmic-ray (in .venv-mutation)
**Config file**: `cosmic-ray-feature.toml` (commit-based)

```toml
# Commit-Based Configuration (Hexagonal Architecture Compatible)
[cosmic-ray]
module-path = [
    "src/des/adapters/drivers/hooks/claude_code_hook_adapter.py",
    "src/des/adapters/driven/config/des_config.py",
    "src/des/application/orchestrator.py"
]
timeout = 30.0
excluded-modules = []
test-command = "pytest -x tests/des/"  # ALL tests for the feature

[cosmic-ray.distributor]
name = "local"

[cosmic-ray.execution-engine]
name = "local"
```

**Why cosmic-ray over mutmut**:
- Native file list support (module-path can be a list of files)
- Automatic per-file breakdown in reports
- Better hexagonal architecture support (files scattered across layers)
- Academic validation (IEEE, ACM papers 2024-2025)

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

- [ ] Implementation files extracted from execution-status.yaml
- [ ] All implementation files exist on disk
- [ ] Test scope path validated
- [ ] Single cosmic-ray config created with file list
- [ ] Mutation testing executed without errors
- [ ] Per-file breakdown captured in report
- [ ] Aggregate score calculated
- [ ] Threshold evaluation complete

## Quality Gate

| Score | Status | Action |
|-------|--------|--------|
| >= 80% | PASS | Proceed to finalize |
| 70-80% | WARN | Review surviving mutants, may proceed with justification |
| < 70% | FAIL | Add tests before proceeding |

**Note**: Threshold increased from 75% to 80% to reflect outside-in TDD's emphasis
on comprehensive behavioral tests rather than isolated unit tests.

## Skip Conditions

Mutation testing may be skipped ONLY if:
1. Language not supported (no mutation tool available)
2. Project explicitly opts out via `.mutation-config.yaml` with documented justification
3. Test suite is empty or broken (must fix first)

**Mutation testing is MANDATORY for all Python projects.**
All skips must be documented with justification and approved by reviewer.

---

## Next Wave

**After Mutation Testing**: Phase 8 - Finalize
**Handoff**: Orchestrator continues develop.md workflow
