# Test Scenarios Summary - nWave Versioning and Release Management

## Document Metadata

| Field | Value |
|-------|-------|
| Feature | nWave Versioning and Release Management |
| Wave | DISTILL |
| Author | Quinn (acceptance-designer) |
| Date | 2026-01-28 |
| Version | 1.0.0 |

---

## Scenario Index

### US-001: Check Installed Version (7 scenarios)

| # | Scenario | Priority | Status | Complexity |
|---|----------|----------|--------|------------|
| 1.1 | Display version with update available | P1 | ACTIVE | Low |
| 1.2 | Display version when up-to-date | P1 | @skip | Low |
| 1.3 | Display version when offline | P1 | @skip | Low |
| 1.4 | Daily auto-check updates watermark when stale | P2 | @skip | Medium |
| 1.5 | Skip update check when watermark is fresh | P2 | @skip | Medium |
| 1.6 | Handle missing VERSION file gracefully | P2 | @skip | Low |
| 1.7 | Handle GitHub API rate limit gracefully | P3 | @skip | Low |

### US-002: Update to Latest Release (11 scenarios)

| # | Scenario | Priority | Status | Complexity |
|---|----------|----------|--------|------------|
| 2.1 | Successful update with backup creation | P1 | ACTIVE | High |
| 2.2 | Major version change requires confirmation | P1 | @skip | Medium |
| 2.3 | Major version update proceeds with confirmation | P1 | @skip | Medium |
| 2.4 | Major version update cancelled with denial | P1 | @skip | Low |
| 2.5 | Local RC version triggers customization warning | P2 | @skip | Medium |
| 2.6 | Network failure during download leaves installation unchanged | P1 | @skip | High |
| 2.7 | Checksum validation failure aborts update | P1 | @skip | Medium |
| 2.8 | Backup rotation maintains exactly 3 copies | P2 | @skip | Medium |
| 2.9 | Non-nWave user content is preserved during update | P1 | @skip | High |
| 2.10 | Already up-to-date shows message without update | P2 | @skip | Low |

### US-003: Build Custom Local Distribution (7 scenarios)

| # | Scenario | Priority | Status | Complexity |
|---|----------|----------|--------|------------|
| 3.1 | Successful build with install prompt on main branch | P1 | ACTIVE | Medium |
| 3.2 | Build fails when tests fail | P1 | @skip | Low |
| 3.3 | RC counter increments on same day builds | P2 | @skip | Medium |
| 3.4 | RC counter resets on new day | P2 | @skip | Medium |
| 3.5 | Feature branch name included in RC version | P2 | @skip | Low |
| 3.6 | User declines install after successful build | P3 | @skip | Low |
| 3.7 | User accepts install after successful build | P2 | @skip | Medium |

### US-004: Install Built Distribution (5 scenarios)

| # | Scenario | Priority | Status | Complexity |
|---|----------|----------|--------|------------|
| 4.1 | Successful installation with smoke test | P1 | ACTIVE | Medium |
| 4.2 | Installation preserves non-nWave user content | P1 | @skip | Medium |
| 4.3 | Installation fails when dist/ directory does not exist | P1 | @skip | Low |
| 4.4 | Installation fails when dist/ is missing required files | P1 | @skip | Low |
| 4.5 | Smoke test failure reports error | P2 | @skip | Medium |

### US-005: Create Official Release (6 scenarios)

| # | Scenario | Priority | Status | Complexity |
|---|----------|----------|--------|------------|
| 5.1 | Successful release PR creation from development branch | P1 | ACTIVE | High |
| 5.2 | Release command fails on main branch | P1 | @skip | Low |
| 5.3 | Release command fails on feature branch | P1 | @skip | Low |
| 5.4 | Permission denied for non-admin user | P1 | @skip | Medium |
| 5.5 | Release fails with uncommitted changes | P1 | @skip | Low |
| 5.6 | Release shows pipeline status after PR creation | P2 | @skip | Medium |

---

## Implementation Priority Order

### Phase 1: Core Happy Paths (Week 1)

Implement one at a time in this order:

1. **1.1** - Display version with update available
2. **2.1** - Successful update with backup creation
3. **3.1** - Successful build with install prompt
4. **4.1** - Successful installation with smoke test
5. **5.1** - Successful release PR creation

### Phase 2: Critical Error Handling (Week 2)

6. **1.3** - Display version when offline
7. **2.6** - Network failure leaves installation unchanged
8. **2.7** - Checksum validation failure
9. **3.2** - Build fails when tests fail
10. **4.3** - Installation fails without dist/

### Phase 3: User Content Protection (Week 2-3)

11. **2.9** - Non-nWave user content preserved
12. **4.2** - Installation preserves user content

### Phase 4: Confirmation Flows (Week 3)

13. **2.2** - Major version requires confirmation
14. **2.3** - Major version proceeds with confirmation
15. **2.4** - Major version cancelled

### Phase 5: Edge Cases (Week 3-4)

16. **1.2** - Version when up-to-date
17. **1.4** - Auto-check watermark stale
18. **1.5** - Skip check when fresh
19. **2.5** - Local RC warning
20. **2.8** - Backup rotation

### Phase 6: Release Command Errors (Week 4)

21. **5.2** - Release fails on main
22. **5.3** - Release fails on feature branch
23. **5.4** - Permission denied
24. **5.5** - Uncommitted changes

### Phase 7: Remaining Scenarios (Week 4+)

25-36. All remaining @skip scenarios

---

## Hexagonal Boundary Verification Checklist

### Before Each Scenario Implementation

| Check | Description | Pass/Fail |
|-------|-------------|-----------|
| **CLI Invocation** | Test invokes CLI entry point via subprocess | |
| **No Internal Imports** | No imports from nWave.core, nWave.domain, etc. | |
| **Observable Outcomes** | Assertions verify CLI output, files, exit codes | |
| **Mock Adapters Only** | Mocks limited to external boundaries | |

### Verification Questions

For each test, ask:

1. **"Does this test invoke the USER-FACING ENTRY POINT?"**
   - YES: Proceeds with validation
   - NO: STOP - Test at wrong boundary

2. **"Does this test import internal components directly?"**
   - YES: STOP - Violates hexagonal boundary
   - NO: Proceed

3. **"Does this test verify observable behavior?"**
   - YES: Valid assertion
   - NO: Consider if internal state check is necessary

### Forbidden Import Patterns

```python
# These imports are FORBIDDEN in acceptance tests:

# Domain layer
from nWave.domain.version import Version
from nWave.domain.backup_policy import BackupPolicy

# Application services
from nWave.application.version_service import VersionService
from nWave.application.update_service import UpdateService

# Core utilities
from nWave.core.version_management.version_comparator import VersionComparator
from nWave.core.version_management.changelog_parser import ChangelogParser

# Infrastructure adapters
from nWave.infrastructure.github_api_adapter import GitHubAPIAdapter
from nWave.infrastructure.file_system_adapter import FileSystemAdapter
```

### Allowed Test Infrastructure

```python
# These imports ARE allowed:
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import tempfile
import shutil
import json
import threading
from http.server import HTTPServer

# Test framework
import pytest
from behave import given, when, then
```

---

## Test Isolation Requirements

### Environment Variables

| Variable | Purpose | Test Value |
|----------|---------|------------|
| `NWAVE_HOME` | Override ~/.claude/ location | Temp directory path |
| `NWAVE_REPO` | Override repository location | Temp directory path |
| `MOCK_GITHUB_RESPONSE` | Inject mock GitHub API response | JSON string |
| `MOCK_TEST_RESULT` | Control test runner behavior | JSON string |
| `MOCK_DATE` | Override current date | ISO date string |

### Temp Directory Structure

```
{tmp_path}/
  .claude/                    # Isolated installation directory
    agents/
      nw/                     # nWave agents (replaced on update)
      my-custom-agent/        # User agents (preserved)
    commands/
      nw/                     # nWave commands (replaced on update)
      my-custom-command/      # User commands (preserved)
    nwave.update              # Watermark file
    VERSION                   # Installed version

  .claude.backup.{timestamp}/ # Backup directories

  nwave-repo/                 # Isolated repository
    dist/                     # Build output
    pyproject.toml            # Version source
    .git/                     # Git repository

  downloads/                  # Mock download server content
```

### Cleanup Requirements

1. **After Each Test**
   - Stop mock download server
   - Remove temp directories (automatic with pytest tmp_path)

2. **Test State Reset**
   - Each test starts with fresh environment
   - No shared state between tests
   - No dependency on test execution order

---

## Mock Adapter Specifications

### MockGitHubAPI

```yaml
Purpose: Simulate GitHub API responses for release metadata

Methods:
  set_latest_release(version, checksum):
    Sets the latest release version and asset checksum

  set_unavailable():
    Simulates network unavailability

  set_rate_limited():
    Simulates HTTP 403 rate limit response

  get_response():
    Returns configured response for test

Response Format:
  success:
    status: 200
    tag_name: "v{version}"
    assets:
      - name: "nwave-release.tar.gz"
        browser_download_url: "https://..."
        checksum: "{sha256}"

  unavailable:
    status: 503
    error: "Service unavailable"

  rate_limited:
    status: 403
    headers:
      X-RateLimit-Remaining: "0"
```

### MockDownloadServer

```yaml
Purpose: Local HTTP server for release asset downloads

Methods:
  start(port):
    Starts HTTP server on specified port
    Returns: Base URL string

  stop():
    Stops HTTP server

  create_valid_asset(version, checksum):
    Creates release asset matching expected checksum

  create_corrupted_asset(version):
    Creates asset with wrong checksum

Configuration:
  simulate_failure: boolean
    When true, simulates network failure mid-download
```

### MockTestRunner

```yaml
Purpose: Control test pass/fail behavior for forge tests

Methods:
  set_tests_pass():
    Configure all tests to pass

  set_tests_fail(count):
    Configure specified number of tests to fail

  get_result():
    Returns test result for CLI consumption

Result Format:
  success:
    exit_code: 0
    output: "All tests passed"

  failure:
    exit_code: 1
    output: "{count} test(s) failed"
```

### MockGitHubCLI

```yaml
Purpose: Simulate gh CLI for release operations

Methods:
  set_admin_access(enabled):
    Configure whether user has admin access

  set_pr_creation_success(pr_number, url):
    Configure successful PR creation response

  set_permission_denied():
    Configure permission denied error

Response Format:
  success:
    exit_code: 0
    stdout: "https://github.com/.../pull/{pr_number}"

  permission_denied:
    exit_code: 1
    stderr: "HTTP 403: Must have admin rights..."
```

---

## Test Data Builders

### VersionBuilder

```python
class VersionBuilder:
    """Build VERSION file content for tests."""

    def __init__(self):
        self.version = "1.0.0"

    def with_version(self, version):
        self.version = version
        return self

    def with_rc(self, branch, date, counter):
        self.version = f"{self.version}-rc.{branch}.{date}.{counter}"
        return self

    def build(self):
        return self.version
```

### WatermarkBuilder

```python
class WatermarkBuilder:
    """Build watermark file content for tests."""

    def __init__(self):
        self.last_check = datetime.utcnow()
        self.latest_version = "1.0.0"

    def with_stale_check(self, hours_ago):
        self.last_check = datetime.utcnow() - timedelta(hours=hours_ago)
        return self

    def with_fresh_check(self):
        self.last_check = datetime.utcnow()
        return self

    def with_latest_version(self, version):
        self.latest_version = version
        return self

    def build(self):
        return f"""last_check: {self.last_check.isoformat()}Z
latest_version: {self.latest_version}
"""
```

### InstallationBuilder

```python
class InstallationBuilder:
    """Build complete nWave installation for tests."""

    def __init__(self, base_path):
        self.base_path = base_path
        self.version = "1.0.0"
        self.custom_agents = []
        self.custom_commands = []

    def with_version(self, version):
        self.version = version
        return self

    def with_custom_agent(self, name):
        self.custom_agents.append(name)
        return self

    def with_custom_command(self, name):
        self.custom_commands.append(name)
        return self

    def build(self):
        """Create installation directory structure."""
        # Create nWave directories
        (self.base_path / "agents" / "nw").mkdir(parents=True)
        (self.base_path / "commands" / "nw").mkdir(parents=True)

        # Create VERSION file
        (self.base_path / "VERSION").write_text(self.version)

        # Create custom agents
        for agent in self.custom_agents:
            agent_path = self.base_path / "agents" / agent
            agent_path.mkdir(parents=True)
            (agent_path / "agent.md").write_text(f"# {agent}")

        # Create custom commands
        for command in self.custom_commands:
            cmd_path = self.base_path / "commands" / command
            cmd_path.mkdir(parents=True)
            (cmd_path / "command.md").write_text(f"# {command}")

        return self.base_path
```

---

## Scenario Coverage Matrix

### User Story to Scenario Mapping

| User Story | Total Scenarios | Happy Path | Error Paths | Edge Cases |
|------------|-----------------|------------|-------------|------------|
| US-001 | 7 | 2 | 3 | 2 |
| US-002 | 11 | 3 | 4 | 4 |
| US-003 | 7 | 3 | 1 | 3 |
| US-004 | 5 | 2 | 2 | 1 |
| US-005 | 6 | 2 | 3 | 1 |
| **Total** | **36** | **12** | **13** | **11** |

### Error Scenario Coverage

| Error Type | Scenarios Covering |
|------------|-------------------|
| Network failure | 1.3, 2.6, 1.7 |
| Validation failure | 2.7, 4.4 |
| Permission denied | 5.4 |
| Missing files | 1.6, 4.3 |
| Test failures | 3.2 |
| Wrong branch | 5.2, 5.3 |
| Uncommitted changes | 5.5 |

### Business Rule Coverage

| Business Rule | Scenarios Covering |
|---------------|-------------------|
| Major version warning | 2.2, 2.3, 2.4 |
| User content preservation | 2.9, 4.2 |
| Backup rotation (max 3) | 2.8 |
| RC version format | 3.1, 3.3, 3.4, 3.5 |
| Daily auto-check | 1.4, 1.5 |
| Atomic update | 2.1, 2.6, 2.7 |

---

## Success Criteria

### DISTILL Wave Completion

- [x] All user stories have acceptance tests (36 total)
- [x] Step definitions designed for production service integration
- [x] One-at-a-time implementation strategy established (@skip tags)
- [x] Architecture-informed test structure respects component boundaries
- [x] Hexagonal boundary check documented and enforced (CM-A)
- [x] Tests verify observable behavior (CLI output, files, exit codes)
- [x] Test isolation documented (temp directories, mock adapters)

### Quality Gates

| Gate | Requirement | Status |
|------|-------------|--------|
| Business Language | All scenarios use domain terminology | PASS |
| Hexagonal Compliance | No internal component imports | PASS |
| Scenario Coverage | All acceptance criteria have tests | PASS |
| Error Path Coverage | All error scenarios documented | PASS |
| Mock Strategy | External adapters only | PASS |

---

## Handoff to DEVELOP Wave

### Deliverables for Devon (test-first-developer)

1. **acceptance-tests.feature** - Complete Gherkin scenarios
2. **step-definitions-outline.md** - Implementation patterns
3. **test-scenarios.md** - This summary document

### Implementation Guidance

1. **Start with ACTIVE scenarios only** (no @skip tag)
2. **Follow priority order** in Implementation Priority section
3. **Enable one scenario at a time** after previous passes
4. **Use Outside-In TDD** - acceptance test drives unit tests
5. **Invoke through CLI entry points only** - no internal imports

### First Scenario to Implement

**1.1: Display version with update available**

This is the simplest happy path that establishes:
- CLI entry point structure
- GitHub API mock pattern
- VERSION file reading
- Watermark file management
- Output format validation

Once this passes, enable 2.1 (Successful update).
