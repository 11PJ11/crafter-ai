# DW-MUTATION-TEST: Per-Feature Mutation Testing Quality Gate

---

## ARCHITECTURAL PRINCIPLE: Outside-In TDD Compatibility

**CRITICAL**: With outside-in TDD, unit tests are written from the PUBLIC INTERFACE,
not for individual internal classes. This has major implications for mutation testing:

| Aspect | OLD Approach (Per-File) | NEW Approach (Per-Feature) |
|--------|------------------------|---------------------------|
| Config | One config per .py file | ONE config per feature |
| Test mapping | `src/foo.py` → `tests/unit/test_foo.py` | `src/feature/` → `tests/feature/` |
| Test types | Unit only | Acceptance + Integration + Unit |
| Internal classes | Expects dedicated unit tests | Tests via public interface |

**Why Per-File Fails with Outside-In TDD**:
- Internal classes have NO dedicated unit tests (correct for outside-in)
- Per-file configs show 0% kill rate for internal classes (false negative)
- Mapping `src/internal.py` → `tests/unit/test_internal.py` finds nothing

---

## ORCHESTRATOR BRIEFING (MANDATORY)

**CRITICAL ARCHITECTURAL CONSTRAINT**: Sub-agents launched via Task tool have NO ACCESS to the Skill tool. They can ONLY use: Read, Write, Edit, Bash, Glob, Grep.

### Usage

```bash
/nw:mutation-test {feature-module} {test-scope}

# Examples:
/nw:mutation-test src/des/ tests/des/
/nw:mutation-test src/auth/ tests/auth/
/nw:mutation-test src/payment/ tests/payment/
```

### What Orchestrator Must Do

When delegating this command to an agent via Task tool:

1. **Do NOT pass `/nw:mutation-test`** to the agent - they cannot execute it
2. **Create a complete agent prompt** with all instructions embedded inline
3. **Include**: feature module path, test scope path, threshold
4. **Use SINGLE CONFIG** for entire feature (not per-file configs)

### Agent Prompt Template

```text
You are a software-crafter agent executing per-feature mutation testing.

PROJECT: {project_id}
FEATURE MODULE: {feature_module}       # e.g., src/des/
TEST SCOPE: {test_scope}               # e.g., tests/des/
THRESHOLD: {threshold}% minimum kill rate

YOUR TASK: Execute mutation testing against ALL tests for the feature.
1. Create ONE cosmic-ray config for entire feature module
2. Run mutation testing with ALL tests (acceptance + integration + unit)
3. Analyze surviving mutants
4. Create mutation report with per-file breakdown

OUTPUT FILE: docs/feature/{project_id}/mutation/mutation-report.md
```

### What NOT to Include in Agent Prompts

- "/nw:mutation-test"
- "Execute /nw:finalize next"
- Any skill or command reference
- Per-file config instructions (OBSOLETE)

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

### STEP 2.5: Per-Feature Scope Discovery (SIMPLIFIED)

With per-feature mutation testing, scope discovery is dramatically simpler:

**DISCOVERY METHOD**:

1. **Feature module** (from command argument or roadmap.yaml):
   ```
   feature_module = "src/des/"  # Entire feature implementation
   ```

2. **Test scope** (from command argument or roadmap.yaml):
   ```
   test_scope = "tests/des/"    # ALL tests: acceptance + integration + unit
   ```

3. **Validate scope exists**:
   ```bash
   # Verify implementation files exist
   find {feature_module} -name "*.py" -not -name "__init__.py" | head -5

   # Verify test files exist
   find {test_scope} -name "test_*.py" | head -5
   ```

**VALIDATION RULES**:

**Rule 1 — SCOPE EXISTS**:
Both `{feature_module}` and `{test_scope}` must contain Python files.
Empty scope = BLOCK (verify paths are correct).

**Rule 2 — SANITY CHECK**:
After mutation run, verify mutant count is reasonable:
- Count implementation lines: `find {feature_module} -name "*.py" -exec wc -l {} + | tail -1`
- Expected mutants: total_lines × 0.05 to 0.10
- If actual_mutants < expected × 0.25: WARN "Check if module-path is correct"

**Rule 3 — PER-FILE BREAKDOWN**:
Cosmic-ray automatically provides per-file breakdown in its report.
No need to create separate configs — one config covers entire feature.

**MUTATION ARTIFACTS LOCATION**:
```
docs/feature/{project-id}/mutation/
├── cosmic-ray-feature.toml        # ONE config for entire feature
├── session.sqlite                 # Session database (gitignored)
└── mutation-report.md             # Final report with per-file breakdown
```
These are ephemeral quality gate artifacts, disposed during `/nw:finalize`.

### STEP 3: Pre-Invocation Validation Checklist

Before invoking Task tool, verify ALL items:
- [ ] Feature module path exists (e.g., `src/des/`)
- [ ] Test scope path exists (e.g., `tests/des/`)
- [ ] Language detected (Python for cosmic-ray)
- [ ] Mutation venv exists (`.venv-mutation/`)
- [ ] Test suite passes: `pytest -x {test_scope}`
- [ ] Threshold configured (default: 80%)

### STEP 4: Invoke Software-Crafter Agent Using Task Tool

**MANDATORY**: Use the Task tool with complete inline instructions.

```
Task: "You are the software-crafter agent executing per-feature mutation testing.

Project: {project_id}
Feature Module: {feature_module}
Test Scope: {test_scope}
Threshold: {threshold}%

═══════════════════════════════════════════════════════════
⚠️  TASK BOUNDARY - READ BEFORE EXECUTING
═══════════════════════════════════════════════════════════
YOUR ONLY TASK: Run mutation testing for entire feature module
INPUT: Feature module + ALL feature tests (acceptance, integration, unit)
OUTPUT FILE: docs/feature/{project_id}/mutation/mutation-report.md
FORBIDDEN ACTIONS:
  ❌ DO NOT proceed to finalize
  ❌ DO NOT modify production code
  ❌ DO NOT create per-file configs (use ONE config for entire feature)
REQUIRED: Return control to orchestrator after completion
═══════════════════════════════════════════════════════════

EXECUTION STEPS:

1. VERIFY PREREQUISITES
   - Check cosmic-ray installed: .venv-mutation/bin/cosmic-ray --version
   - Verify test suite passes: pytest -x {test_scope}

2. CREATE SINGLE FEATURE CONFIG
   Create docs/feature/{project_id}/mutation/cosmic-ray-feature.toml:

   ```toml
   [cosmic-ray]
   module-path = \"{feature_module}\"
   timeout = 30.0
   excluded-modules = []
   test-command = \"pytest -x {test_scope}\"

   [cosmic-ray.distributor]
   name = \"local\"

   [cosmic-ray.execution-engine]
   name = \"local\"
   ```

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
   **Feature Module**: {feature_module}
   **Test Scope**: {test_scope} (acceptance + integration + unit)

   ## Configuration

   - Approach: Per-Feature (outside-in TDD compatible)
   - Config: ONE cosmic-ray config for entire feature
   - Tests: ALL feature tests (not just unit tests)

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
**Config file**: `cosmic-ray-feature.toml` (per-feature)

```toml
# Per-Feature Configuration (Outside-In TDD Compatible)
[cosmic-ray]
module-path = "src/{feature}/"           # Entire feature module
timeout = 30.0
excluded-modules = []
test-command = "pytest -x tests/{feature}/"  # ALL feature tests

[cosmic-ray.distributor]
name = "local"

[cosmic-ray.execution-engine]
name = "local"
```

**Why cosmic-ray over mutmut**:
- Native directory support (module-path can be a directory)
- Automatic per-file breakdown in reports
- Better src/ layout support
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

- [ ] Feature module path validated
- [ ] Test scope path validated
- [ ] Single cosmic-ray config created for feature
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
