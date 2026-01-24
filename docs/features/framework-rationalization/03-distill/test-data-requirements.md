# Test Data Requirements for Framework Rationalization

**Wave:** DISTILL
**Feature:** Framework rationalization acceptance testing
**Purpose:** Define test data, fixtures, and production service configuration

---

## 1. Test Environment Configuration

### 1.1 Service Provider Setup

```python
# tests/acceptance/conftest.py

import pytest
from pathlib import Path
from tools.core.build_ide_bundle import IDEBundleBuilder
from tools.platforms import PlatformRegistry
from tools.utils.dependency_resolver import DependencyResolver
from tools.processors.agent_processor import AgentProcessor
from tools.processors.command_processor import CommandProcessor


class ServiceProvider:
    """Dependency injection container for acceptance tests."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self._services = {}
        self._initialize_services()

    def _initialize_services(self):
        """Register production services for testing."""
        # Core build services
        self._services["IDEBundleBuilder"] = IDEBundleBuilder(
            source_dir=self.project_root / "nWave",
            output_base_dir=self.project_root / "dist"
        )

        # Platform services
        self._services["PlatformRegistry"] = PlatformRegistry()

        # Dependency resolution
        self._services["DependencyResolver"] = DependencyResolver(
            source_dir=self.project_root / "nWave"
        )

        # Processors
        self._services["AgentProcessor"] = AgentProcessor()
        self._services["CommandProcessor"] = CommandProcessor()

    def get_required_service(self, service_name: str):
        """Get a registered service by name."""
        if service_name not in self._services:
            raise KeyError(f"Service '{service_name}' not registered")
        return self._services[service_name]


@pytest.fixture(scope="session")
def project_root():
    """Project root directory."""
    return Path(__file__).parent.parent.parent.parent


@pytest.fixture(scope="session")
def service_provider(project_root):
    """Production service provider for acceptance tests."""
    return ServiceProvider(project_root)


@pytest.fixture(scope="function", autouse=True)
def clean_test_outputs(project_root):
    """Clean test output directories before each test."""
    import shutil

    dist_dir = project_root / "dist"
    if dist_dir.exists():
        shutil.rmtree(dist_dir)

    yield

    # Cleanup after test
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
```

---

## 2. Phase 0: Command Template Test Data

### 2.1 Sample Existing Commands for Analysis

**Test Data Location:** `tests/fixtures/phase0/sample-commands/`

```
tests/fixtures/phase0/
├── sample-commands/           # Existing commands for pattern extraction
│   ├── good-minimal-command.md
│   ├── bloated-command.md     # Anti-pattern: >100 lines
│   ├── workflow-duplicate.md  # Anti-pattern: workflow in command
│   └── unclear-context.md     # Anti-pattern: missing file paths
├── expected-patterns/
│   ├── agent-activation-pattern.md
│   ├── context-bundling-pattern.md
│   └── delegation-pattern.md
└── improved-template/
    └── COMMAND_TEMPLATE-improved.yaml
```

### 2.2 Agent-Builder Test Data

```yaml
# tests/fixtures/phase0/agent-builder-test-data.yaml

test_agent_creation:
  agent_name: "test-automation-agent"
  dependencies:
    templates:
      - AGENT_TEMPLATE.yaml
      - COMMAND_TEMPLATE.yaml  # Should be present after Phase 0.2
  commands:
    - "*forge-command"  # Should be available after Phase 0.2

test_command_creation:
  command_name: "test-workflow"
  expected_structure:
    line_count_range: [50, 60]
    required_sections:
      - "agent_activation"
      - "context_bundling"
      - "delegation_pattern"
    forbidden_sections:
      - "workflow_implementation"
      - "business_logic"
```

---

## 3. Phase 1: Platform Abstraction Test Data

### 3.1 Sample Agent for Multi-Platform Build

```yaml
# tests/fixtures/phase1/sample-agent.yaml

agent:
  name: "test-agent"
  description: "Test agent for platform formatter validation"
  icon: "🧪"
  whenToUse: "Use for testing platform-specific output generation"
  model: "inherit"
  persona:
    role: "Test Agent"
    style: "Systematic, validation-focused"
  commands:
    - help: "Show available commands"
    - test: "Execute test workflow"
```

**Markdown Source:**

```markdown
# tests/fixtures/phase1/test-agent.md

name: test-agent
description: Test agent for platform formatter validation
icon: 🧪
whenToUse: Use for testing platform-specific output generation
model: inherit

## Persona

**Role:** Test Agent
**Style:** Systematic, validation-focused

## Commands

- help: Show available commands
- test: Execute test workflow
```

### 3.2 Expected Platform Outputs

**Claude Code Expected Frontmatter:**

```yaml
---
name: test-agent
description: Test agent for platform formatter validation
model: inherit
---
```

**Codex Expected Frontmatter (TBD - requires research):**

```json
{
  "name": "test-agent",
  "description": "Test agent for platform formatter validation",
  "model": "gpt-4"
}
```

---

## 4. Phase 2: BUILD:INCLUDE Test Data

### 4.1 Shared Content Files

```markdown
# tests/fixtures/phase2/core/radical-candor.md

## Communication Principles: Radical Candor

This agent operates with Radical Candor - caring personally while challenging directly:

1. **Be Specific, Not Vague**: "The function lacks null checks on lines 15-17" not "could be improved"
2. **Challenge Directly**: Point out issues clearly, don't dance around problems
3. **Care Personally**: Frame feedback constructively, explain the "why"
4. **No Ruinous Empathy**: Don't withhold feedback to avoid discomfort
```

### 4.2 Agent Source with BUILD:INCLUDE

```markdown
# tests/fixtures/phase2/agent-with-include.md

name: test-reviewer
description: Test reviewer agent with shared Radical Candor content
model: inherit

<!-- BUILD:INCLUDE tests/fixtures/phase2/core/radical-candor.md -->

## Reviewer Commands

- review: Perform code review with Radical Candor principles
```

### 4.3 Agent Source with Both INCLUDE and INJECT

```markdown
# tests/fixtures/phase2/agent-with-both.md

name: comprehensive-reviewer
description: Agent with both BUILD:INCLUDE and BUILD:INJECT
model: inherit

<!-- BUILD:INCLUDE tests/fixtures/phase2/core/radical-candor.md -->

## Agent-Specific Knowledge

<!-- BUILD:INJECT:START:tests/fixtures/phase2/embed/comprehensive-reviewer/critique-dimensions.md -->
<!-- Agent-specific critique dimensions will be injected here -->
<!-- BUILD:INJECT:END -->
```

---

## 5. Phase 3: Wave Handoff Test Data

### 5.1 Feature Directory Structure Template

```
tests/fixtures/phase3/
└── sample-feature/
    ├── 01-discuss/
    │   └── requirements.md
    ├── 02-design/
    │   └── architecture.md
    ├── 03-distill/
    │   └── acceptance-tests.feature
    ├── 04-develop/
    │   ├── baseline.yaml
    │   ├── roadmap.yaml
    │   └── steps/
    │       └── 01-01.json
    └── .nwave/
        └── metadata.yaml
```

### 5.2 Sample Metadata

```yaml
# tests/fixtures/phase3/sample-feature/.nwave/metadata.yaml

feature:
  name: "sample-feature"
  status: "in_progress"
  current_wave: "DEVELOP"
  created: "2024-01-15T10:30:00Z"
  waves_completed:
    - wave: "DISCUSS"
      completed_at: "2024-01-15T14:00:00Z"
      output_path: "docs/features/sample-feature/01-discuss/"
    - wave: "DESIGN"
      completed_at: "2024-01-16T16:30:00Z"
      output_path: "docs/features/sample-feature/02-design/"
    - wave: "DISTILL"
      completed_at: "2024-01-17T11:00:00Z"
      output_path: "docs/features/sample-feature/03-distill/"
```

### 5.3 Sample Evolution Archive

```markdown
# tests/fixtures/phase3/evolution-archive-sample.md

# Evolution Archive: Sample Feature Implementation

**Feature:** sample-feature
**Archived:** 2024-01-20T18:45:00Z
**Wave:** DEVELOP (completed)

## Summary

Complete implementation of sample feature with baseline measurements,
roadmap execution, and finalization.

## Wave Outputs

### DISCUSS (2024-01-15)
- Requirements documented in 01-discuss/requirements.md
- 5 user stories identified
- Acceptance criteria defined

### DESIGN (2024-01-16)
- Architecture documented in 02-design/architecture.md
- Hexagonal architecture pattern selected
- Component boundaries defined

### DISTILL (2024-01-17)
- 12 acceptance test scenarios created
- Given-When-Then format used
- Production service integration designed

### DEVELOP (2024-01-18 to 2024-01-20)
- Baseline: Complexity 45, Test Coverage 82%
- Final: Complexity 38, Test Coverage 95%
- 8 atomic steps implemented
- All acceptance tests passing

## Lessons Learned

1. Outside-In TDD prevented over-engineering
2. Component boundaries from DESIGN prevented coupling
3. Acceptance tests caught integration issues early
```

---

## 6. Phase 4: Pre-commit Hook Test Data

### 6.1 Sample Git Changes

```bash
# tests/fixtures/phase4/git-staged-changes.txt

M nWave/agents/researcher.md
M tools/build_ide_bundle.py
M nWave/framework-catalog.yaml
```

### 6.2 Expected Warnings

```
tests/fixtures/phase4/expected-warnings.txt:

WARNING: Agent files modified
  -> Consider updating: AGENTS.md

WARNING: Build system files modified
  -> Consider updating: docs/architecture/build-system.md

WARNING: Framework catalog modified
  -> Consider updating: CHANGELOG.md

============================================
  3 documentation sync warning(s)
  Commit will proceed, but please review.
============================================
```

---

## 7. Phase 5: Release Packaging Test Data

### 7.1 Sample Framework Catalog Version

```yaml
# tests/fixtures/phase5/framework-catalog-version.yaml

framework:
  name: "nWave"
  version: "1.2.48"  # Used for release packaging
  description: "5D-Wave Methodology Framework"
```

### 7.2 Expected Release Structure

```
tests/fixtures/phase5/expected-release-structure/
└── dist/releases/
    ├── nwave-1.2.48-claude-code.zip
    │   ├── agents/nw/
    │   ├── commands/nw/
    │   ├── install.sh
    │   ├── install.ps1
    │   ├── install.py
    │   ├── README.md
    │   └── VERSION
    ├── nwave-1.2.48-codex.zip
    │   └── [same structure]
    └── checksums.txt
```

### 7.3 Sample Checksums

```
# tests/fixtures/phase5/checksums-sample.txt

abc123def456...  nwave-1.2.48-claude-code.zip
789ghi012jkl...  nwave-1.2.48-codex.zip
```

---

## 8. Phase 6: CI/CD Test Data

### 8.1 Sample GitHub Actions Event

```json
{
  "ref": "refs/tags/v1.2.49",
  "repository": {
    "name": "nwave",
    "owner": {
      "login": "test-org"
    }
  },
  "pusher": {
    "name": "maintainer",
    "email": "maintainer@example.com"
  }
}
```

### 8.2 Expected CI Matrix

```yaml
# tests/fixtures/phase6/ci-matrix.yaml

strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
    python-version: ['3.11', '3.12']

expected_combinations:
  - os: ubuntu-latest
    python: 3.11
  - os: ubuntu-latest
    python: 3.12
  - os: macos-latest
    python: 3.11
  - os: macos-latest
    python: 3.12
  - os: windows-latest
    python: 3.11
  - os: windows-latest
    python: 3.12
```

---

## 9. Cross-Phase Integration Test Data

### 9.1 Complete Feature Lifecycle Data

```
tests/fixtures/integration/
└── payment-processing/
    ├── 01-discuss/
    │   └── requirements.md          # Business requirements
    ├── 02-design/
    │   └── architecture.md          # Hexagonal architecture design
    ├── 03-distill/
    │   └── acceptance-tests.feature # E2E scenarios
    ├── 04-develop/
    │   ├── baseline.yaml            # Measurements before implementation
    │   ├── roadmap.yaml             # Implementation plan
    │   └── steps/
    │       ├── 01-01.json           # Atomic task: Payment gateway adapter
    │       ├── 01-02.json           # Atomic task: Domain entities
    │       └── 01-03.json           # Atomic task: Application service
    └── .nwave/
        └── metadata.yaml            # Feature tracking
```

---

## 10. Production Service Validation Data

### 10.1 Service Integration Checklist

```yaml
# tests/fixtures/validation/service-integration-checklist.yaml

production_services_required:
  - service: "IDEBundleBuilder"
    validation: "Build must produce real output files"
    test: "Verify dist/claude-code/ and dist/codex/ exist"

  - service: "PlatformRegistry"
    validation: "Registry must return real formatter instances"
    test: "Call get_all() and verify ClaudeCodeFormatter, CodexFormatter"

  - service: "DependencyResolver"
    validation: "Resolver must process real BUILD:INCLUDE markers"
    test: "Verify file content injection from nWave/data/core/"

  - service: "AgentProcessor"
    validation: "Processor must generate real agent files"
    test: "Verify agent.md output with correct frontmatter"

  - service: "CommandProcessor"
    validation: "Processor must generate real command files"
    test: "Verify command.md output with task delegation"

forbidden_test_infrastructure:
  - pattern: "FakeBuildService"
    reason: "Must use real IDEBundleBuilder"

  - pattern: "MockPlatformFormatter"
    reason: "Must use real ClaudeCodeFormatter/CodexFormatter"

  - pattern: "StubDependencyResolver"
    reason: "Must use real file reading and marker processing"
```

---

## 11. Test Execution Fixtures

### 11.1 pytest-bdd Configuration

```python
# tests/acceptance/conftest.py (additional fixtures)

@pytest.fixture
def context():
    """Shared test context for step definitions."""
    class TestContext:
        def __init__(self):
            self.build_result = None
            self.platform_formatters = None
            self.processed_content = None
            self.release_archives = None
            self.ci_workflow_result = None

    return TestContext()


@pytest.fixture
def temp_feature_directory(tmp_path):
    """Temporary directory for feature outputs."""
    feature_dir = tmp_path / "docs" / "features" / "test-feature"
    feature_dir.mkdir(parents=True)
    return feature_dir
```

### 11.2 Custom Parsers

```python
# tests/acceptance/parsers.py

from pytest_bdd import parsers

# Custom type converter for version strings
parsers.parse.with_pattern(
    r"\d+\.\d+\.\d+",
    name="Version",
    type=lambda s: s  # Keep as string
)

# Custom type converter for file paths
parsers.parse.with_pattern(
    r"[a-zA-Z0-9_\-/]+\.[a-zA-Z0-9]+",
    name="FilePath",
    type=lambda s: Path(s)
)
```

---

## 12. Quality Gate Test Data

### 12.1 Test Coverage Requirements

```yaml
# tests/fixtures/quality-gates/coverage-requirements.yaml

minimum_coverage:
  phase_0: 85%  # Command template improvement
  phase_1: 90%  # Platform abstraction (critical)
  phase_2: 85%  # BUILD:INCLUDE mechanism
  phase_3: 80%  # Wave handoffs
  phase_4: 75%  # Pre-commit hooks
  phase_5: 90%  # Release packaging (critical)
  phase_6: 85%  # CI/CD integration

critical_paths:
  - "Platform formatter frontmatter generation"
  - "BUILD:INCLUDE marker replacement"
  - "Release archive creation"
  - "Multi-platform build orchestration"
```

### 12.2 Business Language Validation

```yaml
# tests/fixtures/quality-gates/business-language-validation.yaml

acceptable_business_terms:
  - "platform"
  - "agent"
  - "command"
  - "wave"
  - "handoff"
  - "release"
  - "installer"
  - "documentation"

forbidden_technical_jargon:
  - "class instantiation"
  - "dependency injection container"
  - "abstract base class"
  - "polymorphic dispatch"
  # Use business language instead: "formatter", "service", "pattern"
```

---

## Summary

All test data is organized to support **production service integration** with minimal mocking. Test doubles are used only for:

- **External GitHub API** (release creation)
- **File system operations** (can use temp directories)
- **Network calls** (if any)

**Production services used throughout:**
- IDEBundleBuilder
- PlatformRegistry
- PlatformFormatters (ClaudeCodeFormatter, CodexFormatter)
- DependencyResolver
- AgentProcessor
- CommandProcessor

This ensures acceptance tests validate **real system behavior** and drive Outside-In TDD implementation effectively.
