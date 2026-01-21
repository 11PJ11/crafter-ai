# nWave Framework Rationalization - DISCUSS Wave Output

**Wave:** DISCUSS
**Status:** Requirements gathered
**Next Wave:** DESIGN
**Feature:** Framework rationalization for open source publication

---

## Business Objectives

1. **Multi-platform support** - Claude Code + Codex (always build both)
2. **GitHub releases** - Semantic versioning with downloadable packages
3. **Cross-platform installation** - Windows, Linux, macOS
4. **Fork-friendly structure** - Clear documentation for contributors
5. **Agent quality** - Radical Candor communication principles
6. **Simplified wave handoffs** - Feature-centric output organization

---

## Phase 1: Multi-Platform Build System

### 1.1 Platform Abstraction Layer

**Create `tools/platforms/` directory with Strategy Pattern:**

```
tools/platforms/
├── __init__.py          # Platform registry and factory
├── base.py              # Abstract PlatformFormatter base class
├── claude.py            # Claude Code formatter
└── codex.py             # OpenAI Codex formatter
```

**Key files to modify:**
- [build_ide_bundle.py](tools/build_ide_bundle.py) - Always build BOTH platforms
- [agent_processor.py](tools/processors/agent_processor.py) - Use platform formatter for frontmatter
- [command_processor.py](tools/processors/command_processor.py) - Use platform formatter for commands

**New output structure:**
```
dist/
├── claude-code/      # Claude Code compatible output
│   ├── agents/nw/
│   └── commands/nw/
├── codex/            # OpenAI Codex compatible output
│   ├── agents/nw/
│   └── commands/nw/
└── releases/         # Packaged releases for download
    ├── nwave-{version}-claude-code.zip
    └── nwave-{version}-codex.zip
```

### 1.2 Platform-Specific Formatting

Each platform formatter handles:
- YAML frontmatter format differences
- Tool naming conventions
- System prompt structure
- Model selection syntax

---

## Phase 2: Data Rationalization (Single Source of Truth)

### 2.1 Extract Shared Content

**Problem identified:** `critique-dimensions.md` duplicated across 12 agents (~630 lines each)

**Solution:** Create `BUILD:INCLUDE` markers for shared content injection

**New structure:**
```
nWave/data/
├── core/                      # Shared content (NEW)
│   └── critique/
│       └── priority-validation.md  # Extracted from critique-dimensions
├── embed/                     # Agent-specific embeds (EXISTING)
│   └── {agent-name}/
│       └── critique-dimensions.md  # Now uses BUILD:INCLUDE
├── methodologies/             # Methodology references (EXISTING)
└── research/                  # Research documents (EXISTING)
```

### 2.2 BUILD:INCLUDE Mechanism

**Current:** `<!-- BUILD:INJECT nWave/data/embed/{agent}/file.md -->`
**New:** `<!-- BUILD:INCLUDE nWave/data/core/critique/priority-validation.md -->`

**Modify:** [dependency_resolver.py](tools/utils/dependency_resolver.py) to support INCLUDE marker

### 2.3 Consolidation Targets

| Content | Duplication | Action |
|---------|-------------|--------|
| Priority Validation framework | 12 agents | Extract to `core/critique/` |
| Critique dimensions structure | 12 agents | Reference shared template |
| BDD methodology | 2 agents | Keep separate (agent-specific) |

---

## Phase 3: Documentation Restructuring

### 3.1 Root-Level Enterprise Files (NEW)

| File | Purpose |
|------|---------|
| `AGENTS.md` | Agent catalog with capabilities and usage |
| `CONTRIBUTING.md` | Contribution guidelines and code standards |
| `CHANGELOG.md` | Version history (auto-generated from commits) |
| `STYLEGUIDE.md` | Code and documentation style guide |

### 3.2 Reorganized docs/ Directory

```
docs/
├── getting-started/
│   ├── quickstart.md
│   ├── installation.md
│   └── first-project.md
├── architecture/
│   ├── build-system.md
│   ├── agent-lifecycle.md
│   └── platform-abstraction.md
├── guides/
│   ├── creating-agents.md          # NEW: Agent creation with researcher+agent-builder
│   ├── creating-commands.md        # NEW: Command creation workflow
│   ├── defining-workflows.md
│   └── extending-platforms.md
├── reference/
│   ├── commands.md
│   ├── agents.md
│   └── configuration.md
└── platforms/
    ├── claude-code.md
    └── codex.md
```

### 3.3 Agent Creation Guide (`docs/guides/creating-agents.md`)

**Workflow documented:**
1. **Research Phase** - Use `@researcher` to gather domain knowledge
2. **Design Phase** - Use `@agent-builder` to design agent specification
3. **Implementation** - Create agent markdown file in `nWave/agents/`
4. **Data Embedding** - Create `nWave/data/embed/{agent-name}/` with knowledge files
5. **Build & Test** - Run build and verify agent functionality

**Templates location:** `nWave/templates/agent-templates/`

### 3.4 Command Creation Guide (`docs/guides/creating-commands.md`)

**Workflow documented:**
1. Add command to `framework-catalog.yaml` commands section
2. Create task file in `nWave/tasks/nw/{command}.md`
3. Define agent associations and outputs
4. Run build to generate command files

---

## Phase 3.5: Output Organization and Wave Handoffs

### Current Problem
- Research data scattered across multiple directories
- Wave handoff documents have no clear structure
- No consistent feature-centric organization

### Proposed Solution: Feature-Centric Output Structure

**User project outputs (happens in user environment):**
```
docs/
├── research/                      # User-requested research (via @researcher)
│   └── {topic}/
│       └── {topic}-research.md
└── features/                      # Wave execution outputs
    └── {feature-name}/
        ├── 01-discuss/            # DISCUSS wave output
        │   ├── requirements.md
        │   └── user-stories.md
        ├── 02-design/             # DESIGN wave output
        │   ├── architecture.md
        │   └── diagrams/
        ├── 03-distill/            # DISTILL wave output
        │   ├── acceptance-tests.md
        │   └── test-scenarios.md
        ├── 04-develop/            # DEVELOP wave output
        │   ├── baseline.yaml
        │   ├── roadmap.yaml
        │   └── steps/
        └── 05-deliver/            # DELIVER wave output
            └── release-notes.md
```

**Framework internal data (nWave source):**
```
nWave/data/
├── core/                          # Shared content (BUILD:INCLUDE)
│   └── critique/
├── embed/                         # Agent-specific embeds (BUILD:INJECT)
│   └── {agent-name}/
├── methodologies/                 # Methodology references
├── templates/                     # Templates for agent/command creation
│   ├── agent-template.md
│   └── command-template.md
└── research/                      # Agent creation research (INTERNAL)
    ├── reference/                 # Agent reference materials
    └── findings/                  # Agentic AI research findings
```

### Wave Handoff Simplification

| Wave | Input From | Output To | Handoff Document |
|------|-----------|-----------|------------------|
| DISCUSS | User request | `docs/features/{name}/01-discuss/` | `requirements.md` |
| DESIGN | DISCUSS output | `docs/features/{name}/02-design/` | `architecture.md` |
| DISTILL | DESIGN output | `docs/features/{name}/03-distill/` | `acceptance-tests.md` |
| DEVELOP | DISTILL output | `docs/features/{name}/04-develop/` | `roadmap.yaml` |
| DELIVER | DEVELOP output | `docs/features/{name}/05-deliver/` | `release-notes.md` |

### Configurable Output Paths

All waves support `--output` parameter to override default paths:
```bash
/nw:discuss "Auth feature" --output=custom/path/discuss/
```

### Research Output Routing

**User research (via @researcher in user environment):**
- Default: `docs/research/{topic}/`
- Override: `--output=custom/path/`
- NOT embedded into agents

**Agent creation research (internal to nWave development):**
- Output to `nWave/data/research/{agent-name}/`
- After agent-builder validates, move to `nWave/data/embed/{agent-name}/`

---

## Phase 4: Build System Updates

### 4.1 Modify framework-catalog.yaml

Add platform configuration section:
```yaml
platforms:
  claude-code:
    output_dir: "dist/claude-code"
    frontmatter_format: "yaml"
    tool_prefix: ""
  codex:
    output_dir: "dist/codex"
    frontmatter_format: "json"
    tool_prefix: "codex_"
```

### 4.2 Dependency Management

**Requirements files:**
```
tools/
├── requirements.txt          # Production dependencies (pinned)
├── requirements-dev.txt      # Development dependencies (testing, linting)
└── requirements.lock         # Fully resolved dependency tree
```

**Dependency policy:**
- All production dependencies pinned to exact versions
- Lock file for reproducible builds across environments
- Regular dependency updates via Dependabot or Renovate
- Security scanning in CI (pip-audit)

**Minimum Python version:** 3.11+

### 4.3 Pre-Commit Hooks

**File:** `.pre-commit-config.yaml`

**Documentation reminder hook:**
When modifying key files, remind developers to update related documentation:

| Modified File Pattern | Reminder |
|----------------------|----------|
| `nWave/agents/*.md` | Update AGENTS.md catalog |
| `nWave/tasks/nw/*.md` | Update docs/reference/commands.md |
| `tools/*.py` | Update docs/architecture/build-system.md |
| `nWave/framework-catalog.yaml` | Update CHANGELOG.md |
| `tools/platforms/*.py` | Update docs/platforms/*.md |

**Standard hooks:**
- Python formatting and linting (ruff - replaces black, isort, flake8)
- Type checking (mypy)
- YAML validation
- Markdown linting
- Trailing whitespace removal
- End-of-file fixer

**Custom documentation check script:**
```bash
# tools/check-docs-sync.sh
# Validates that documentation is in sync with code changes
# Returns non-zero if docs update may be needed
```

### 4.4 Cross-Platform Installation Scripts

**Create platform-specific installers:**

| Script | Platform | Purpose |
|--------|----------|---------|
| `install.sh` | Linux/macOS | Bash installer with --platform parameter |
| `install.ps1` | Windows | PowerShell installer with -Platform parameter |
| `install.py` | All | Python installer (universal fallback) |

**Common installer features:**
- Detect IDE installation paths (Claude Code, Codex)
- Support `--platform` / `-Platform` parameter (claude-code|codex)
- Default to claude-code for backward compatibility
- Copy from `dist/{platform}/` based on selection
- Verify installation success

**Default installation paths:**

| OS | Claude Code | Codex |
|----|-------------|-------|
| Linux | `~/.claude/` | `~/.codex/` |
| macOS | `~/.claude/` | `~/.codex/` |
| Windows | `%USERPROFILE%\.claude\` | `%USERPROFILE%\.codex\` |

---

## Phase 5: GitHub Releases and Versioning

### 5.1 Release Packaging

**Create `tools/package_release.py`:**
- Read version from `framework-catalog.yaml`
- Create ZIP archives for each platform
- Generate checksums (SHA256)
- Output to `dist/releases/`

**Package contents:**
```
nwave-{version}-claude-code.zip
├── agents/nw/*.md
├── commands/nw/*.md
├── install.sh           # Linux/macOS installer (Bash)
├── install.ps1          # Windows installer (PowerShell)
├── install.py           # Universal installer (Python)
├── README.md            # Quick start guide
└── VERSION              # Version file for verification
```

### 5.2 GitHub Actions Workflows

**Create `.github/workflows/ci.yml` (continuous integration):**

```yaml
name: CI
on: [push, pull_request]

jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Build all platforms
        run: |
          cd tools
          python build_ide_bundle.py --clean
      - name: Test installation (Unix)
        if: runner.os != 'Windows'
        run: ./install.sh --platform claude-code --dry-run
      - name: Test installation (Windows)
        if: runner.os == 'Windows'
        run: .\install.ps1 -Platform claude-code -DryRun
```

**Create `.github/workflows/release.yml`:**

```yaml
name: Release
on:
  push:
    tags: ['v*']

jobs:
  build-and-release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Build all platforms
        run: |
          cd tools
          python build_ide_bundle.py --clean
          python package_release.py

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            dist/releases/nwave-*.zip
            dist/releases/checksums.txt
          generate_release_notes: true
```

### 5.3 Version Management

**Semantic versioning scheme:** `MAJOR.MINOR.PATCH`
- MAJOR: Breaking changes to agent/command API
- MINOR: New agents, commands, or features
- PATCH: Bug fixes and documentation

**Version source of truth:** `nWave/framework-catalog.yaml` (line 21)

### 5.4 Installation from Release

**For end users:**
```bash
# Download specific version
curl -LO https://github.com/{org}/nwave/releases/download/v1.2.48/nwave-1.2.48-claude-code.zip
unzip nwave-1.2.48-claude-code.zip
cd nwave-1.2.48-claude-code
./install.sh
```

**For developers (clone and build):**
```bash
git clone https://github.com/{org}/nwave.git
cd nwave/tools
python build_ide_bundle.py
./install-nwave.sh --platform claude-code
```

---

## Phase 6: Radical Candor Agent Attitude

### Rationale
All agents, especially reviewers, should embody **Radical Candor** principles:
- **Care Personally** - Genuine interest in helping the user succeed
- **Challenge Directly** - Honest, specific feedback without sugar-coating

### Implementation

**Add to shared agent preamble (BUILD:INCLUDE):**
```markdown
## Communication Principles: Radical Candor

This agent operates with Radical Candor - caring personally while challenging directly:

1. **Be Specific, Not Vague**: "The function lacks null checks on lines 15-17" not "could be improved"
2. **Challenge Directly**: Point out issues clearly, don't dance around problems
3. **Care Personally**: Frame feedback constructively, explain the "why"
4. **No Ruinous Empathy**: Don't withhold feedback to avoid discomfort
5. **No Obnoxious Aggression**: Critique the work, not the person
6. **No Manipulative Insincerity**: Be genuine, not political
```

**Reviewer-specific enhancement:**
```markdown
### Review Feedback Standards

- **BLOCKER**: Must be fixed before merge - explain impact clearly
- **SHOULD**: Strong recommendation - provide rationale
- **COULD**: Optional improvement - acknowledge trade-offs
- **PRAISE**: Explicitly call out good practices - reinforce what works

Never give empty praise. If something is good, explain WHY it's good.
Never soften criticism that affects quality. Say what needs to be said.
```

### Files to Update

| Agent Type | File Pattern | Changes |
|------------|-------------|---------|
| All agents | `nWave/agents/*.md` | Add Radical Candor preamble via BUILD:INCLUDE |
| Reviewers | `nWave/agents/*-reviewer.md` | Add reviewer-specific feedback standards |
| Core content | `nWave/data/core/radical-candor.md` | Create shared Radical Candor content |

---

## Phase 7: Open Source Legal & Governance (Final Step)

**Status:** To be addressed before public release

These items are critical for open source publication but will be decided after technical implementation is complete.

### 7.1 License Selection (CRITICAL)

| Option | Characteristics | Decision |
|--------|-----------------|----------|
| MIT | Simple, permissive, no patent protection | TBD |
| Apache 2.0 | Patent protection, corporate-friendly | TBD |
| GPL | Copyleft, limits corporate adoption | TBD |

**Files to create:**
- `LICENSE` - Full license text
- SPDX headers in Python files

### 7.2 Security Policy (CRITICAL)

**File:** `SECURITY.md`
- Supported versions policy
- Vulnerability reporting process (GitHub Security Advisories)
- Response timeline commitment
- CVE disclosure process

**CI Addition:**
- Dependency vulnerability scanning (pip-audit, Dependabot)

### 7.3 Contributor Agreement (HIGH)

**Approach:** CLA vs DCO - TBD
- CLA: Formal IP assignment (CLA Assistant GitHub App)
- DCO: Lightweight sign-off in commits

### 7.4 Code of Conduct (HIGH)

**File:** `CODE_OF_CONDUCT.md`
- Adopt Contributor Covenant v2.1
- Define enforcement contact
- Establish reporting process

### 7.5 Governance Model (HIGH)

**File:** `GOVERNANCE.md`
- Decision-making process (BDFL, maintainer council, consensus)
- Maintainer roles and responsibilities
- Path to becoming a maintainer
- Conflict resolution process

### 7.6 Community Documentation (MEDIUM)

**Additional docs to create:**
- Target audience definition
- Value proposition ("Why nWave?")
- Troubleshooting/FAQ section
- Success metrics and goals

---

## Deferred: Skills Feature

Skills feature will be planned and implemented in a separate iteration after core rationalization is complete. This allows focus on foundational improvements first.

---

## Implementation Order

1. **Radical Candor research** - @researcher gathers methodology for agent communication principles
2. **Codex CLI research** - @researcher determines format requirements for Codex platform
3. **Platform abstraction** (Phase 1.1) - Foundation for multi-platform
4. **Build script modifications** (Phase 1.2) - Always build both platforms
5. **BUILD:INCLUDE mechanism** (Phase 2.2) - Enable content sharing
6. **Extract shared content** (Phase 2.1, 2.3) - Consolidate duplications
7. **Radical Candor integration** (Phase 6) - Add to all agents, enhance reviewers
8. **Output organization** (Phase 3.5) - Feature-centric structure + wave handoffs
9. **Update wave commands** - Add `--output` parameter, standardize handoff paths
10. **Documentation restructuring** (Phase 3) - Enterprise-ready docs + creation guides
11. **Install script updates** (Phase 4.3) - End-user experience
12. **Release packaging** (Phase 5.1) - Create ZIP archives
13. **GitHub Actions workflow** (Phase 5.2) - Automated releases
14. **Legal & Governance** (Phase 7) - License, security policy, CoC, governance (before public release)

---

## Critical Files to Modify

| File | Changes |
|------|---------|
| `tools/build_ide_bundle.py` | Always build BOTH platforms, new output structure |
| `tools/processors/agent_processor.py` | Platform-aware frontmatter generation |
| `tools/processors/command_processor.py` | Platform-aware command generation |
| `tools/utils/dependency_resolver.py` | Add BUILD:INCLUDE support |
| `nWave/framework-catalog.yaml` | Add platforms configuration, update argument_hints with --output |
| `install-nwave.sh` | Add --platform parameter |

### Wave Command Updates (add --output parameter)

| Command | New argument_hint |
|---------|------------------|
| `discuss` | `[feature-name] --output=[path] --interactive=[high\|moderate]` |
| `design` | `[component-name] --output=[path] --architecture=[hexagonal\|layered]` |
| `distill` | `[story-id] --output=[path] --test-framework=[cucumber\|specflow]` |
| `develop` | `[feature-description] --output=[path]` |
| `deliver` | `[deployment-target] --output=[path] --environment=[staging\|production]` |
| `research` | `[topic] --output=[path]` |

## New Files to Create

| File | Purpose |
|------|---------|
| `tools/platforms/__init__.py` | Platform registry |
| `tools/platforms/base.py` | Abstract base formatter |
| `tools/platforms/claude.py` | Claude Code formatter |
| `tools/platforms/codex.py` | Codex formatter |
| `tools/package_release.py` | Release packaging script |
| `tools/requirements.txt` | Pinned production dependencies |
| `tools/requirements-dev.txt` | Development dependencies |
| `tools/requirements.lock` | Fully resolved dependency tree |
| `.pre-commit-config.yaml` | Pre-commit hooks configuration |
| `tools/check-docs-sync.sh` | Documentation sync validation script |
| `install.sh` | Linux/macOS installer (Bash) |
| `install.ps1` | Windows installer (PowerShell) |
| `install.py` | Universal installer (Python) |
| `.github/workflows/ci.yml` | Cross-platform CI workflow |
| `.github/workflows/release.yml` | GitHub Actions release workflow |
| `nWave/data/core/critique/priority-validation.md` | Shared critique framework |
| `nWave/data/core/radical-candor.md` | Radical Candor communication principles |
| `nWave/data/templates/agent-template.md` | Template for new agents |
| `nWave/data/templates/command-template.md` | Template for new commands |
| `docs/guides/creating-agents.md` | Agent creation guide |
| `docs/guides/creating-commands.md` | Command creation guide |
| `AGENTS.md` | Agent catalog |
| `CONTRIBUTING.md` | Contribution guide |
| `STYLEGUIDE.md` | Style guide |
| `LICENSE` | Open source license (Phase 7) |
| `SECURITY.md` | Vulnerability disclosure policy (Phase 7) |
| `CODE_OF_CONDUCT.md` | Community standards (Phase 7) |
| `GOVERNANCE.md` | Decision-making process (Phase 7) |

## Directories to Reorganize

### Framework Internal (nWave source)
| Current | New | Action |
|---------|-----|--------|
| `nWave/data/agents_research/` | `nWave/data/research/findings/` | Move |
| `nWave/data/agents_reference/` | `nWave/data/research/reference/` | Move |
| N/A | `nWave/data/core/` | Create |
| N/A | `nWave/data/templates/` | Create |

### User Project Structure (documented default paths)
| Directory | Purpose |
|-----------|---------|
| `docs/research/{topic}/` | User research outputs |
| `docs/features/{name}/01-discuss/` | DISCUSS wave output |
| `docs/features/{name}/02-design/` | DESIGN wave output |
| `docs/features/{name}/03-distill/` | DISTILL wave output |
| `docs/features/{name}/04-develop/` | DEVELOP wave output |
| `docs/features/{name}/05-deliver/` | DELIVER wave output |

---

## Verification Plan

1. **Build verification (both platforms):**
   ```bash
   cd tools && python build_ide_bundle.py --clean
   ```

2. **Output structure verification:**
   ```bash
   ls -la dist/claude-code/agents/nw/
   ls -la dist/codex/agents/nw/
   ```

3. **Release packaging verification:**
   ```bash
   cd tools && python package_release.py
   ls -la dist/releases/
   # Should show: nwave-{version}-claude-code.zip, nwave-{version}-codex.zip
   ```

4. **Cross-platform installation verification:**

   | Platform | Command |
   |----------|---------|
   | Linux/macOS | `./install.sh --platform claude-code` |
   | Windows | `.\install.ps1 -Platform claude-code` |
   | Universal | `python install.py --platform claude-code` |

5. **Agent functionality test:**
   - Invoke `/nw:develop` command
   - Verify agent loads and executes correctly

6. **Release workflow verification:**
   - Create test tag: `git tag v1.2.48-test`
   - Verify GitHub Actions triggers
   - Check release artifacts uploaded

7. **Cross-platform CI validation:**
   - GitHub Actions matrix: ubuntu-latest, macos-latest, windows-latest
   - Verify build works on all platforms

---

## Risk Mitigation

- **Backward compatibility:** Default to claude-code platform, existing scripts continue working
- **Incremental rollout:** Each phase independently deployable
- **Codex validation:** Research Codex formatting requirements before implementation
- **Release testing:** Use pre-release tags (e.g., v1.3.0-rc1) before stable releases

---

## DISCUSS Wave Handoff

### Requirements Summary

| Requirement | Priority | Acceptance Criteria |
|-------------|----------|---------------------|
| Multi-platform build | HIGH | Build produces both `dist/claude-code/` and `dist/codex/` |
| GitHub releases | HIGH | Tags trigger automated release with ZIP packages |
| Cross-platform install | HIGH | Installers work on Windows, Linux, macOS |
| Feature-centric output | MEDIUM | Waves output to `docs/features/{name}/0X-wave/` |
| Radical Candor | MEDIUM | All agents include RC principles, reviewers enhanced |
| Agent creation guide | MEDIUM | Documented workflow with researcher + agent-builder |
| Command creation guide | MEDIUM | Documented workflow with framework-catalog.yaml |
| BUILD:INCLUDE | MEDIUM | Shared content injection mechanism |
| Dependency management | MEDIUM | Pinned requirements, lock file, security scanning |
| Pre-commit hooks | MEDIUM | Documentation sync reminders, linting, formatting |
| License selection | FINAL | LICENSE file with chosen open source license |
| Security policy | FINAL | SECURITY.md with vulnerability disclosure process |
| Code of Conduct | FINAL | CODE_OF_CONDUCT.md adopted |
| Governance model | FINAL | GOVERNANCE.md with decision-making process |
| Contributor agreement | FINAL | CLA or DCO approach implemented |
| Skills feature | DEFERRED | Planned for separate iteration |

### Open Questions for DESIGN Wave

1. **Codex format specifics:** What are the exact frontmatter and tool naming requirements?
2. **Version source:** Should version remain in framework-catalog.yaml or move to dedicated VERSION file?
3. **Radical Candor depth:** How detailed should the RC guidelines be embedded in each agent?

### Open Questions for Phase 7 (Deferred to Final Step)

1. **License selection:** MIT vs Apache 2.0 vs other?
2. **Contributor agreement:** CLA vs DCO approach?
3. **Governance model:** BDFL vs maintainer council vs consensus?
4. **Target audience:** Explicit definition of primary users
5. **Value proposition:** Clear "Why nWave?" messaging
6. **Success metrics:** Measurable goals for open source launch

### Next Steps (DESIGN Wave)

1. Research Codex CLI requirements and formatting
2. Design platform abstraction layer architecture
3. Design BUILD:INCLUDE parser implementation
4. Create detailed technical specifications for each component

### Research Tasks Required

| Task | Agent | Purpose |
|------|-------|---------|
| **Radical Candor research** | @researcher | Gather comprehensive Radical Candor methodology to inform review command and all agent communication principles |
| **Codex CLI research** | @researcher | Determine exact frontmatter format, tool naming conventions, and system prompt requirements for OpenAI Codex |

**Note:** Radical Candor research should cover:
- Kim Scott's original framework (Care Personally + Challenge Directly)
- Anti-patterns (Ruinous Empathy, Obnoxious Aggression, Manipulative Insincerity)
- Application to code review feedback (BLOCKER/SHOULD/COULD/PRAISE)
- Integration patterns for AI agent communication
- Specific language patterns and examples for technical feedback
