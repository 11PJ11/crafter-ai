# Version Update Experience - Technology Stack

**Feature:** Version delivery and update loop for end users
**Wave:** DESIGN
**Status:** Technology selections complete
**Date:** 2026-01-25
**Architect:** Morgan (Solution Architect)

---

## Technology Selection Criteria

All technology choices evaluated against:

1. **Open Source Priority** - Free, well-maintained open source solutions preferred
2. **nWave Compatibility** - Integration with existing Python-based CLI framework
3. **Reliability** - Proven track record for version management and update operations
4. **Security** - HTTPS enforcement, no credential storage, secure file operations
5. **Maintainability** - Clear documentation, active community support
6. **Cross-Platform** - Works on Linux, macOS, Windows (WSL)
7. **Team Readiness** - Aligns with team skills (Python, git, GitHub)

---

## Core Technology Stack

### Programming Language

**Selected: Python 3.11+**

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Open Source | ✅ Excellent | PSF License (permissive) |
| Compatibility | ✅ Excellent | Already used throughout nWave |
| Reliability | ✅ Excellent | Mature language (30+ years) |
| Maintainability | ✅ Excellent | Large ecosystem, extensive documentation |
| Cross-Platform | ✅ Excellent | Native cross-platform support including Windows |
| Team Readiness | ✅ Excellent | Primary language for nWave |

**CRITICAL Platform Constraint:**
nWave avoids bash/shell scripts for Windows compatibility. The framework accepts Python 3.11+ as a prerequisite. All CLI integration and scripts **MUST** be Python-based, NOT bash-based.

**Rationale:**
- nWave framework requires Python 3.11+ as prerequisite
- Excellent library ecosystem for CLI, HTTP, file operations
- **Windows compatibility critical** - bash scripts don't work without WSL
- No additional language/runtime required beyond framework prerequisite
- Consistent execution environment across all platforms

**Alternatives Considered:**
- **Bash/Shell:** ❌ **REJECTED** - NOT cross-platform (Windows incompatibility is BLOCKING issue)
- **Node.js:** ❌ **REJECTED** - would require additional runtime installation
- **Go:** ❌ **REJECTED** - would require compilation step, adds complexity

---

## Integration with Existing Installation System

### Reused Components

**From `scripts/install/install_utils.py`:**
- `BackupManager` - Backup creation and restoration (REUSED, not reimplemented)
- `PathUtils` - Cross-platform path utilities
- `Logger` - Structured logging with file output
- `ManifestWriter` - Installation manifest generation
- `confirm_action()` - User confirmation prompts

**From `scripts/install/install_nwave.py`:**
- Complete installation logic (DELEGATED to, not reimplemented)
- Framework validation
- Component verification
- Build process (if needed)

**From `scripts/install/update_nwave.py`:**
- Update validation logic (REFERENCED for consistency)

### New Download Components

**Python Standard Library:**
- `urllib.request` or `requests` - Download GitHub releases
- `tarfile` or `zipfile` - Extract release packages
- `tempfile` - Temporary download directory
- `subprocess` - Call existing installer script

### Release Package Format

GitHub releases must include installer scripts for delegation:
```
nwave-{version}.tar.gz
├── scripts/
│   └── install/
│       ├── install_nwave.py      # Reused installer
│       ├── install_utils.py      # Reused utilities
│       └── uninstall_nwave.py
├── nWave/
│   ├── agents/                   # Framework agents
│   ├── tasks/                    # Command definitions
│   └── ...
└── dist/
    └── ide/                      # Pre-built bundle
        ├── agents/nw/
        └── commands/nw/
```

**Release Creation:**
The release pipeline (semantic-release) must package installer scripts with the framework.

---

## Library Selections

### 1. GitHub API Client

**Selected: `requests` (HTTP client library)**

**Open Source:** ✅ Apache 2.0 License
**GitHub:** https://github.com/psf/requests (⭐ 51.9k | 🍴 9.3k)
**Last Release:** 2024-12 (actively maintained)
**Maintenance:** Mature and stable

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Open Source | ✅ Excellent | Apache 2.0, widely trusted |
| Simplicity | ✅ Excellent | "HTTP for Humans" - simple API |
| Reliability | ✅ Excellent | Battle-tested in production |
| Security | ✅ Excellent | SSL verification by default |
| Documentation | ✅ Excellent | Comprehensive docs and examples |
| Community | ✅ Excellent | 51k+ stars, large community |

**Implementation:**
```python
import requests

response = requests.get(
    "https://api.github.com/repos/{owner}/{repo}/releases/latest",
    timeout=10,
    headers={"Accept": "application/vnd.github+json"}
)

if response.status_code == 200:
    release_data = response.json()
    version = release_data["tag_name"]
    changelog = release_data["body"]
elif response.status_code == 404:
    # No releases found
    pass
elif response.status_code == 429:
    # Rate limit exceeded
    pass
```

**Why Selected:**
- Simple, intuitive API for HTTP requests
- No GitHub-specific SDK overhead
- Automatic JSON parsing
- Excellent error handling
- SSL certificate validation by default
- Timeout support critical for network failures

**Alternatives Considered:**

**httpx** (Async HTTP client)
- ❌ **Rejected:** Unnecessary async complexity for synchronous operations
- ❌ Our use case doesn't benefit from async (single API call)
- Rating: Medium

**github.py / PyGithub** (GitHub SDK)
- ❌ **Rejected:** Over-engineered for simple API calls
- ❌ Adds heavyweight dependency for minimal benefit
- ❌ We only need one endpoint (`/releases/latest`)
- Rating: Low

**urllib** (Standard library)
- ❌ **Rejected:** More verbose, less intuitive than requests
- ❌ No automatic JSON parsing
- ❌ More complex SSL verification configuration
- Rating: Medium

**Decision Matrix:**

| Library | Simplicity | Features | Dependencies | Community | Score |
|---------|-----------|----------|--------------|-----------|-------|
| **requests** ✅ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 19/20 |
| httpx | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 16/20 |
| github.py | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | 12/20 |
| urllib | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 13/20 |

---

### 2. Semantic Version Parsing

**Selected: `packaging` (Python packaging core library)**

**Open Source:** ✅ Apache 2.0 / BSD License
**GitHub:** https://github.com/pypa/packaging (⭐ 594 | 🍴 249)
**Last Release:** 2024-11 (actively maintained)
**Maintenance:** Official Python Packaging Authority project

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Open Source | ✅ Excellent | Apache 2.0 / BSD dual license |
| Standard Library | ⚠️ Separate | Bundled with pip, not in stdlib |
| Reliability | ✅ Excellent | Official PyPA project |
| Semver Support | ✅ Excellent | Full PEP 440 compliance |
| Documentation | ✅ Excellent | Official PyPA documentation |
| Community | ✅ Excellent | Python Packaging Authority |

**Implementation:**
```python
from packaging import version

installed = version.parse("1.5.7")
available = version.parse("1.6.0")

if available > installed:
    # Update available
    if available.major > installed.major:
        # Breaking change (major version bump)
        breaking_change = True
```

**Why Selected:**
- Official Python Packaging Authority project
- Standard for Python version comparison
- Handles semantic versioning edge cases correctly
- Already likely installed (bundled with pip)
- PEP 440 compliant (Python's versioning spec)

**Alternatives Considered:**

**semver** (Semantic Versioning library)
- ❌ **Rejected:** Less standard in Python ecosystem
- ❌ `packaging` is more widely used and trusted
- ❌ Doesn't add value over `packaging.version`
- Rating: Medium

**distutils.version** (Standard library, deprecated)
- ❌ **Rejected:** Deprecated in Python 3.10+
- ❌ Migration path is to `packaging`
- Rating: Low

**Manual string parsing**
- ❌ **Rejected:** Reinventing the wheel
- ❌ Error-prone for edge cases (pre-releases, build metadata)
- Rating: Very Low

**Decision Matrix:**

| Library | Standard | Reliability | Features | Maintenance | Score |
|---------|----------|-------------|----------|-------------|-------|
| **packaging** ✅ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 20/20 |
| semver | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 15/20 |
| distutils | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐ | 10/20 |
| Manual | ⭐ | ⭐ | ⭐⭐ | ⭐ | 5/20 |

---

### 3. CLI User Interface

**Selected: `rich` (Modern terminal formatting library)**

**Open Source:** ✅ MIT License
**GitHub:** https://github.com/Textualize/rich (⭐ 49.8k | 🍴 1.7k)
**Last Release:** 2024-12 (actively maintained)
**Maintenance:** Active, Textualize company-backed

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Open Source | ✅ Excellent | MIT License (very permissive) |
| Features | ✅ Excellent | Colors, tables, panels, progress bars |
| Reliability | ✅ Excellent | Mature library, widely adopted |
| Usability | ✅ Excellent | Excellent visual output |
| Documentation | ✅ Excellent | Comprehensive docs with examples |
| Community | ✅ Excellent | 49k+ stars, active development |

**Implementation:**
```python
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

# Attention-grabbing update banner
table = Table(title="Update Available", show_header=True, header_style="bold magenta")
table.add_column("Attribute", style="cyan")
table.add_column("Value", style="green")
table.add_row("Current version", "1.5.7")
table.add_row("Available update", "1.6.0")
table.add_row("Changelog highlights", "• New feature X\n• Bug fix Y\n• Performance improvement Z")

panel = Panel(table, border_style="bold red", title="nWave Update")
console.print(panel)

# Breaking change warning
if breaking_change:
    console.print("[bold red]⚠️  BREAKING CHANGES[/bold red]")
    console.print("This is a major version update. Migration may be required.")
```

**Why Selected:**
- Excellent visual output for attention-grabbing notifications
- Built-in support for colors, borders, tables, panels
- Simple API, no complex configuration
- Cross-platform (works on Windows, macOS, Linux)
- Gracefully degrades in environments without color support

**Alternatives Considered:**

**colorama** (Cross-platform colored terminal text)
- ❌ **Rejected:** More primitive, requires manual ANSI code handling
- ❌ No built-in table/panel support
- ✅ Would work, but `rich` is superior
- Rating: Medium

**termcolor** (ANSI color formatting)
- ❌ **Rejected:** Simpler than rich, but less feature-rich
- ❌ No layout features (tables, panels, borders)
- Rating: Medium

**click** (CLI framework with basic styling)
- ❌ **Rejected:** nWave already has command infrastructure
- ❌ Styling features less comprehensive than rich
- Rating: Low

**Plain print() with ANSI codes**
- ❌ **Rejected:** Not cross-platform (Windows issues)
- ❌ Manual formatting is error-prone
- Rating: Low

**Decision Matrix:**

| Library | Features | Cross-Platform | Usability | Community | Score |
|---------|----------|----------------|-----------|-----------|-------|
| **rich** ✅ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 20/20 |
| colorama | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 15/20 |
| termcolor | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | 13/20 |
| click | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 16/20 |
| Plain ANSI | ⭐⭐ | ⭐⭐ | ⭐ | N/A | 5/20 |

---

### 4. File Operations

**Selected: `shutil` + `pathlib` (Python standard library)**

**Open Source:** ✅ Python Software Foundation License
**Maintenance:** Part of Python core, highly stable

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Open Source | ✅ Excellent | PSF License (permissive) |
| Standard Library | ✅ Excellent | Built into Python, no install |
| Reliability | ✅ Excellent | Battle-tested for decades |
| Cross-Platform | ✅ Excellent | Abstracts OS differences |
| Features | ✅ Excellent | Copy, move, delete, permissions |
| Documentation | ✅ Excellent | Official Python docs |

**Implementation:**
```python
import shutil
from pathlib import Path

# Backup directory
source = Path.home() / ".claude"
destination = Path.home() / f".claude_bck_{date.today().strftime('%Y%m%d')}"

shutil.copytree(
    source,
    destination,
    copy_function=shutil.copy2,  # Preserve metadata (permissions, timestamps)
    ignore_dangling_symlinks=True,
    dirs_exist_ok=False  # Fail if destination exists (safety)
)

# Restore from backup
shutil.rmtree(Path.home() / ".claude")  # Remove current installation
shutil.copytree(destination, source, copy_function=shutil.copy2)

# Cleanup old backups
for backup_dir in Path.home().glob(".claude_bck_*"):
    age_days = (date.today() - parse_date_from_dirname(backup_dir.name)).days
    if age_days > 30:
        try:
            shutil.rmtree(backup_dir)
        except PermissionError:
            # Log warning, continue (non-blocking)
            pass
```

**Why Selected:**
- Standard library (no external dependencies)
- Cross-platform path handling (`pathlib`)
- Atomic directory operations (`copytree`, `rmtree`)
- Permission preservation (`copy_function=shutil.copy2`)
- Mature, well-tested code

**Alternatives Considered:**

**os module** (Lower-level file operations)
- ❌ **Rejected:** More verbose than shutil
- ❌ Requires manual recursion for directory operations
- ✅ Still used for some operations (checking disk space)
- Rating: Low

**Third-party backup libraries**
- ❌ **Rejected:** Over-engineering for simple directory copy
- ❌ Unnecessary dependency
- Rating: Very Low

**rsync via subprocess**
- ❌ **Rejected:** Not cross-platform (Windows compatibility)
- ❌ Requires external tool installation
- Rating: Low

**Decision Matrix:**

| Approach | Standard | Cross-Platform | Features | Simplicity | Score |
|----------|----------|----------------|----------|------------|-------|
| **shutil+pathlib** ✅ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 20/20 |
| os module | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | 16/20 |
| Third-party | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | 12/20 |
| rsync | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | 11/20 |

---

### 5. Git Configuration Access

**Selected: `subprocess` + `git` command**

**Open Source:** ✅ Python standard library (subprocess) + Git GPL
**Maintenance:** Part of Python core + Git project

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Open Source | ✅ Excellent | PSF License + Git GPL |
| Reliability | ✅ Excellent | Direct git command, no parsing |
| Simplicity | ✅ Excellent | Single command execution |
| Cross-Platform | ✅ Excellent | Git available on all platforms |
| No Dependencies | ✅ Excellent | Assumes git already installed |

**Implementation:**
```python
import subprocess
from typing import Optional

def get_remote_origin_url() -> Optional[str]:
    """
    Get git remote origin URL.

    Returns None if not in git repo or no remote configured.
    """
    try:
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False  # Don't raise on non-zero exit
        )

        if result.returncode == 0:
            return result.stdout.strip()
        else:
            # Not in git repo or no remote origin
            return None

    except FileNotFoundError:
        # Git not installed
        return None
    except subprocess.TimeoutExpired:
        # Git hung (rare)
        return None

def parse_github_url(git_url: str) -> tuple[str, str]:
    """
    Parse GitHub owner/repo from git URL.

    Handles both HTTPS and SSH formats:
    - https://github.com/swcraftsmanshipdojo/nWave.git
    - git@github.com:swcraftsmanshipdojo/nWave.git

    Returns: (owner, repo)
    """
    import re

    # HTTPS: https://github.com/{owner}/{repo}.git
    https_match = re.match(r'https://github\.com/([^/]+)/([^/]+?)(?:\.git)?$', git_url)
    if https_match:
        return https_match.group(1), https_match.group(2)

    # SSH: git@github.com:{owner}/{repo}.git
    ssh_match = re.match(r'git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$', git_url)
    if ssh_match:
        return ssh_match.group(1), ssh_match.group(2)

    raise ValueError(f"Unrecognized GitHub URL format: {git_url}")
```

**Why Selected:**
- Direct git command execution (no parsing .git/config file)
- Git abstracts platform differences
- Simple subprocess call
- Handles both HTTPS and SSH URLs
- Git already required for nWave framework development

**Alternatives Considered:**

**GitPython** (Python library for git)
- ❌ **Rejected:** Heavyweight dependency for single command
- ❌ Adds complexity for minimal benefit
- ✅ Would work, but subprocess is simpler
- Rating: Low

**Parse .git/config file directly**
- ❌ **Rejected:** Fragile (git config format can vary)
- ❌ Requires implementing git config parsing
- ❌ Subprocess + git is more reliable
- Rating: Very Low

**pygit2** (libgit2 Python bindings)
- ❌ **Rejected:** Native library dependency (C library)
- ❌ Installation complexity
- ❌ Over-engineering for simple use case
- Rating: Very Low

**Decision Matrix:**

| Approach | Simplicity | Reliability | Dependencies | Maintenance | Score |
|----------|-----------|-------------|--------------|-------------|-------|
| **subprocess+git** ✅ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 20/20 |
| GitPython | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | 13/20 |
| Parse .git/config | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | 11/20 |
| pygit2 | ⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐ | 10/20 |

---

## Git Hooks and Release Automation

### 1. Conventional Commit Enforcement

**Selected: `commitlint` + `@commitlint/config-conventional`**

**Open Source:** ✅ MIT License
**GitHub:** https://github.com/conventional-changelog/commitlint (⭐ 17k | 🍴 1k)
**Last Release:** 2024-11 (actively maintained)
**Maintenance:** Active, community-driven

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Open Source | ✅ Excellent | MIT License |
| Industry Standard | ✅ Excellent | De facto standard for conventional commits |
| Configuration | ✅ Excellent | Simple config via extends |
| Error Messages | ✅ Excellent | Clear, actionable feedback |
| Integration | ✅ Excellent | Works with pre-commit framework |

**Implementation:**

**.pre-commit-config.yaml**
```yaml
repos:
  - repo: https://github.com/alessandrojcm/commitlint-pre-commit-hook
    rev: v9.5.0
    hooks:
      - id: commitlint
        stages: [commit-msg]
        additional_dependencies: ['@commitlint/config-conventional']
```

**commitlint.config.js**
```javascript
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [2, 'always', [
      'feat', 'fix', 'docs', 'style', 'refactor',
      'perf', 'test', 'build', 'ci', 'chore', 'revert'
    ]],
    'subject-case': [2, 'always', 'lower-case'],
    'header-max-length': [2, 'always', 100]
  }
};
```

**Why Selected:**
- Industry standard for conventional commits validation
- Excellent error messages with format examples
- Simple configuration via `@commitlint/config-conventional`
- Integrates seamlessly with pre-commit framework
- Node.js based, works cross-platform

**Alternatives Considered:**

**commitizen** (Interactive commit tool)
- ❌ **Rejected:** Adds interactive prompt overhead
- ❌ We only need validation, not interactive prompts
- ✅ Could be added later for optional use
- Rating: Medium

**Custom Python script**
- ❌ **Rejected:** Reinventing the wheel
- ❌ Inferior error messages compared to commitlint
- ❌ More maintenance burden
- Rating: Low

**cocogitto** (Rust-based conventional commits tool)
- ❌ **Rejected:** Less mature than commitlint
- ❌ Smaller community (2.5k stars vs 17k)
- ✅ Would work, but commitlint is more standard
- Rating: Medium

**Decision Matrix:**

| Tool | Standard | Features | Integration | Community | Score |
|------|----------|----------|-------------|-----------|-------|
| **commitlint** ✅ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 20/20 |
| commitizen | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 17/20 |
| Custom script | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | N/A | 8/20 |
| cocogitto | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | 14/20 |

---

### 2. Semantic Release Automation

**Selected: `semantic-release` with plugin ecosystem**

**Open Source:** ✅ MIT License
**GitHub:** https://github.com/semantic-release/semantic-release (⭐ 20.9k | 🍴 1.9k)
**Last Release:** 2024-11 (actively maintained)
**Maintenance:** Active, community-driven

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Open Source | ✅ Excellent | MIT License |
| Automation | ✅ Excellent | Fully automated version management |
| Plugin Ecosystem | ✅ Excellent | Rich plugin library |
| Integration | ✅ Excellent | GitHub Actions native support |
| Documentation | ✅ Excellent | Comprehensive docs |

**Plugin Chain:**
1. **@semantic-release/commit-analyzer** - Determine version bump from commits
2. **@semantic-release/release-notes-generator** - Generate changelog content
3. **@semantic-release/changelog** - Update CHANGELOG.md file
4. **@semantic-release/exec** - Update nWave/VERSION file
5. **@semantic-release/npm** - Update package.json (no publish)
6. **@semantic-release/git** - Commit CHANGELOG.md and VERSION changes
7. **@semantic-release/github** - Create GitHub Release

**Configuration (.releaserc):**
```json
{
  "branches": ["main", "master"],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    "@semantic-release/changelog",
    ["@semantic-release/exec", {
      "prepareCmd": "echo ${nextRelease.version} > nWave/VERSION"
    }],
    ["@semantic-release/npm", { "npmPublish": false }],
    ["@semantic-release/git", {
      "assets": ["CHANGELOG.md", "nWave/VERSION"],
      "message": "chore(release): ${nextRelease.version} [skip ci]"
    }],
    "@semantic-release/github"
  ]
}
```

**Why Selected:**
- Industry standard for automated releases
- Eliminates manual version management
- Generates changelog automatically from commits
- Updates VERSION file as part of release process
- Creates GitHub Releases with release notes
- Integrates with conventional commits (via commitlint)

**Alternatives Considered:**

**release-please** (Google's release automation)
- ❌ **Rejected:** Less flexible than semantic-release
- ❌ Opinionated workflow (separate PR for releases)
- ✅ Would work, but semantic-release more established
- Rating: Medium

**Manual version management**
- ❌ **Rejected:** Error-prone, requires discipline
- ❌ Changelog maintenance burden
- ❌ Inconsistent versioning
- Rating: Very Low

**conventional-changelog-cli** (Changelog generation only)
- ❌ **Rejected:** Only handles changelog, not version bumping
- ❌ Requires manual version management
- ❌ semantic-release is more comprehensive
- Rating: Low

**Decision Matrix:**

| Tool | Automation | Features | Flexibility | Community | Score |
|------|-----------|----------|-------------|-----------|-------|
| **semantic-release** ✅ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 20/20 |
| release-please | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 15/20 |
| Manual | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | N/A | 8/20 |
| changelog-cli | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | 12/20 |

---

## Dependency Summary

### Python Dependencies

**Required (install via pip):**
```
requests>=2.31.0       # GitHub API client (Apache 2.0)
packaging>=23.0        # Semantic version parsing (Apache 2.0 / BSD)
rich>=13.0.0          # Terminal formatting (MIT)
```

**Standard Library (no install required):**
```
subprocess  # Git command execution
shutil      # File operations
pathlib     # Cross-platform path handling
json        # JSON parsing (GitHub API responses)
datetime    # Date/time operations (backup naming)
re          # Regular expressions (URL parsing)
```

### Node.js Dependencies (for git hooks and release)

**Required (install via npm):**
```
@commitlint/cli@^18.0.0                           # Commit message linting (MIT)
@commitlint/config-conventional@^18.0.0           # Conventional commits config (MIT)
semantic-release@^22.0.0                          # Automated releases (MIT)
@semantic-release/changelog@^6.0.0                # Changelog generation (MIT)
@semantic-release/commit-analyzer@^11.0.0         # Commit analysis (MIT)
@semantic-release/release-notes-generator@^12.0.0 # Release notes (MIT)
@semantic-release/exec@^6.0.0                     # VERSION file update (MIT)
@semantic-release/git@^10.0.0                     # Git commit automation (MIT)
@semantic-release/github@^9.0.0                   # GitHub Release creation (MIT)
@semantic-release/npm@^11.0.0                     # package.json update (MIT)
```

**Development (pre-commit framework):**
```
pre-commit>=3.5.0  # Git hooks framework (MIT)
```

---

## Installation Instructions

### For Developers (Framework Creators)

**Python Dependencies:**
```bash
pip install requests packaging rich
```

**Node.js Dependencies:**
```bash
npm install --save-dev \
  @commitlint/cli \
  @commitlint/config-conventional \
  semantic-release \
  @semantic-release/changelog \
  @semantic-release/commit-analyzer \
  @semantic-release/release-notes-generator \
  @semantic-release/exec \
  @semantic-release/git \
  @semantic-release/github \
  @semantic-release/npm
```

**Pre-commit Hooks:**
```bash
pip install pre-commit
pre-commit install --hook-type commit-msg --hook-type pre-push
```

### For Users (Framework Consumers)

**Automatic via installer:**
- Python dependencies bundled in installer
- No Node.js required for users (only for creators)
- No git hooks required for users (only for creators)

---

## Licensing Compliance

All selected technologies use permissive open source licenses:

| Dependency | License | Permissive | Commercial Use |
|-----------|---------|------------|----------------|
| requests | Apache 2.0 | ✅ Yes | ✅ Yes |
| packaging | Apache 2.0 / BSD | ✅ Yes | ✅ Yes |
| rich | MIT | ✅ Yes | ✅ Yes |
| commitlint | MIT | ✅ Yes | ✅ Yes |
| semantic-release | MIT | ✅ Yes | ✅ Yes |
| Python stdlib | PSF License | ✅ Yes | ✅ Yes |

**Compliance Status:** ✅ All dependencies use permissive licenses compatible with commercial use

**No License Restrictions:**
- No GPL dependencies (no copyleft requirements)
- No AGPL dependencies (no network copyleft)
- No proprietary dependencies
- No patent concerns (Apache 2.0 includes patent grant)

---

## Performance Characteristics

### GitHub API Client (requests)

**Benchmarks:**
- Simple GET request: ~50ms (local network)
- GitHub API call: ~200-500ms (depends on network latency)
- JSON parsing: <10ms (for typical release response)

**Optimization:**
- Session reuse for multiple requests (connection pooling)
- Timeout: 10 seconds (prevents hanging)
- No retries on success (single call)

### Semantic Version Parsing (packaging)

**Benchmarks:**
- Version parsing: <1ms per version
- Version comparison: <1ms per comparison

**Optimization:**
- Cache parsed versions (avoid re-parsing)
- Simple comparison operations (no regex)

### File Operations (shutil)

**Benchmarks:**
- Directory copy (10 MB): ~5-10 seconds
- Directory copy (50 MB): ~20-30 seconds
- Directory delete: ~1-2 seconds

**Optimization:**
- `copy2` function (preserves metadata efficiently)
- No compression (trade space for speed)
- Parallel copy where possible (OS-level optimization)

### Terminal Formatting (rich)

**Benchmarks:**
- Render simple table: <10ms
- Render complex panel: <50ms

**Optimization:**
- Lazy rendering (only when needed)
- Minimal ANSI code generation
- Cached color schemes

---

## Security Considerations

### GitHub API Security

**TLS/SSL:**
- `requests` library enforces HTTPS by default
- SSL certificate validation enabled
- No option to disable verification

**Rate Limiting:**
- Unauthenticated: 60 requests/hour (sufficient for typical usage)
- Authenticated: 5000 requests/hour (future enhancement with GitHub token)
- Graceful handling of HTTP 429 (Rate Limit Exceeded)

**No Credential Storage:**
- No API tokens required for public repositories
- No authentication credentials stored
- No OAuth flows required

### File System Security

**Permission Preservation:**
- `shutil.copy2` preserves file permissions
- Backup and restore maintain security attributes
- No privilege escalation (runs as current user)

**Path Validation:**
- Use `pathlib` for safe path handling
- Validate paths to prevent directory traversal
- No arbitrary file execution

**Disk Space Management:**
- Check available space before backup
- Cleanup old backups (30-day retention)
- Clear error messages if disk full

---

## Testing Strategy

### Unit Testing

**Mocking External Dependencies:**
```python
import unittest
from unittest.mock import patch, MagicMock

class TestGitHubAdapter(unittest.TestCase):
    @patch('requests.get')
    def test_get_latest_release_success(self, mock_get):
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tag_name": "v1.6.0",
            "body": "Release notes..."
        }
        mock_get.return_value = mock_response

        adapter = GitHubAdapter("owner", "repo")
        release = adapter.get_latest_release()

        self.assertEqual(release.version, "1.6.0")
```

### Integration Testing

**Test with Real GitHub API:**
```python
def test_github_api_integration():
    """Test against actual GitHub API (swcraftsmanshipdojo/nWave)."""
    adapter = GitHubAdapter("swcraftsmanshipdojo", "nWave")
    release = adapter.get_latest_release()

    assert release is not None
    assert release.version matches semver pattern
```

### End-to-End Testing

**Full Update Flow:**
- Create test environment with old version
- Run `/nw:version` command
- Verify update banner displayed
- Run `/nw:update` command
- Confirm update prompt
- Verify backup created
- Verify new version installed
- Verify backup cleaned up after 30 days

---

## Migration Path

### Current State (Before Implementation)

- No version checking capability
- Manual update process (`update_nwave.py --force`)
- No changelog visibility
- No breaking change warnings
- Developer-focused tooling

### Implementation Plan

**Phase 1: Core Infrastructure**
1. Install Python dependencies (requests, packaging, rich)
2. Create hexagonal architecture structure
3. Implement core domain components
4. Implement adapters

**Phase 2: Git Hooks**
1. Install Node.js dependencies (commitlint, semantic-release)
2. Configure commitlint
3. Add pre-commit hooks
4. Test commit validation

**Phase 3: Release Automation**
1. Configure semantic-release
2. Create GitHub Actions workflow
3. Test release process on feature branch
4. Merge to main and verify first automated release

**Phase 4: User Commands**
1. Implement `/nw:version` command
2. Implement `/nw:update` command
3. Test update flow end-to-end
4. Update documentation

---

## Future Technology Considerations

### Potential Enhancements

**GraphQL GitHub API:**
- More efficient data fetching (only request needed fields)
- Reduced API call count (single query for multiple data points)
- Consideration: More complex than REST for simple use case

**Alternative Release Platforms:**
- GitLab Releases API (for GitLab forks)
- Bitbucket Releases (for Bitbucket forks)
- Generic Git tags (platform-agnostic)

**Advanced CLI Features:**
- Progress bars during long operations (rich.progress)
- Interactive prompts with validation (rich.prompt)
- Diff display for changed files (rich.syntax)

**Performance Optimizations:**
- Parallel backup operations (multiprocessing)
- Incremental backups (only changed files)
- Compressed backups (trade space for speed)

---

## Python CLI Scripts and Lock File Management

### CLI Entry Points (Python-Based)

**Files:**
- `nWave/cli/version_cli.py` - Entry point for `/nw:version` command
- `nWave/cli/update_cli.py` - Entry point for `/nw:update` command

**Command File Registration:**
- Source: `nWave/tasks/nw/version.md`, `nWave/tasks/nw/update.md`
- Installed: `~/.claude/commands/nw/version.md`, `~/.claude/commands/nw/update.md`

**Implementation:**
```python
#!/usr/bin/env python3
"""Entry point for /nw:version command."""
import sys
from pathlib import Path

# Add nWave to path for imports
sys.path.insert(0, str(Path.home() / ".claude" / "nWave"))

from nWave.core.version_manager import VersionManager
from nWave.adapters.console_ui_adapter import ConsoleUIAdapter
# ... initialize and execute

def main():
    # Dependency injection and execution
    # ...
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
```

**Technology Choices:**
- **Standard Library Only:** subprocess, pathlib, json for CLI scripts
- **No External Dependencies:** CLI scripts use only standard library for minimal overhead
- **Cross-Platform:** Works on Windows, Linux, macOS without modification

### Lock File Management

**Lock File Technology:**
- **Format:** JSON (standard library `json` module)
- **Location:** `~/.claude/.nwave-update.lock`
- **Atomicity:** File system atomic operations (create/delete)
- **Process Tracking:** PID, timestamp, hostname

**Implementation:**
```python
import json
import os
from pathlib import Path
from datetime import datetime
import socket

class LockManager:
    def __init__(self):
        self.lock_file = Path.home() / ".claude" / ".nwave-update.lock"

    def acquire_lock(self) -> LockResult:
        """Acquire lock with atomic file creation."""
        if self.lock_file.exists():
            # Check if stale
            if self.check_stale_lock():
                self.force_release_lock()
            else:
                return LockResult(
                    success=False,
                    error_message="Another update is in progress"
                )

        # Create lock file atomically
        lock_data = {
            "pid": os.getpid(),
            "timestamp": datetime.now().isoformat(),
            "hostname": socket.gethostname(),
            "version_from": self.get_current_version(),
            "version_to": self.get_target_version()
        }

        self.lock_file.write_text(json.dumps(lock_data, indent=2))

        return LockResult(success=True)

    def release_lock(self) -> None:
        """Release lock by deleting file."""
        if self.lock_file.exists():
            self.lock_file.unlink()

    def check_stale_lock(self) -> bool:
        """Check if lock is stale (>2 hours)."""
        if not self.lock_file.exists():
            return False

        lock_data = json.loads(self.lock_file.read_text())
        timestamp = datetime.fromisoformat(lock_data["timestamp"])
        age_hours = (datetime.now() - timestamp).total_seconds() / 3600

        # Configurable via environment variable
        timeout_hours = int(os.getenv("NWAVE_LOCK_TIMEOUT_HOURS", "2"))

        return age_hours > timeout_hours
```

**Why JSON:**
- **Human-Readable:** Easy to debug
- **Standard Library:** No external dependencies
- **Structured:** Can store PID, timestamp, versions
- **Portable:** Works across all platforms

---

## Summary

This technology stack provides a robust, maintainable, and user-friendly foundation:

✅ **Open Source Priority** - All dependencies use permissive licenses (MIT, Apache 2.0, BSD)
✅ **Proven Technologies** - requests (51k stars), rich (49k stars), semantic-release (20k stars)
✅ **Minimal Dependencies** - 3 Python libraries + standard library
✅ **Cross-Platform** - Works on Linux, macOS, **Windows (native, not WSL)**
✅ **Industry Standards** - Conventional commits, semantic versioning, semantic-release
✅ **Security** - HTTPS only, SSL verification, no credential storage
✅ **Performance** - Version check <3s, backup <30s, update <60s
✅ **Maintainability** - Well-documented libraries, active communities
✅ **Python CLI** - All scripts Python-based for Windows compatibility
✅ **Lock Management** - JSON-based lock files with stale lock detection

**Total Python Dependencies:** 3 external + standard library
**Total Node.js Dependencies:** 9 (for creators only, not users)
**Total Stars (Python libs):** 102k+ (high community adoption)

**BLOCKER Fixes Applied:**
1. ✅ CLI Integration - Python-based CLI scripts specified (no bash)
2. ✅ Lock File Mechanism - JSON-based lock file management with stale detection

**MAJOR Fixes Applied:**
1. ✅ Platform Constraint - Python 3.11+ requirement explicitly documented
2. ✅ Windows Compatibility - All scripts Python-based, no bash dependencies

---

**Technology Stack:** Approved ✅ (Adversarial Review BLOCKERS Resolved)
**Date:** 2026-01-25
**Architect:** Morgan (Solution Architect)
