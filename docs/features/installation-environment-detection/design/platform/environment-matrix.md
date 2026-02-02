# Environment Compatibility Matrix: Installation Environment Detection

**Feature ID:** APEX-002
**Wave:** DESIGN (Platform Perspective)
**Created:** 2026-01-29

---

## 1. Cross-Platform Compatibility Matrix

### 1.1 Operating System Support

| OS | Version | Status | CI Tested | Notes |
|----|---------|--------|-----------|-------|
| macOS | 14.x (Sonoma) | Supported | Yes (macos-latest) | ARM64 (M1/M2/M3) |
| macOS | 13.x (Ventura) | Supported | Yes | Intel and ARM |
| macOS | 12.x (Monterey) | Supported | Legacy | Intel primarily |
| Ubuntu | 24.04 LTS | Supported | Yes (ubuntu-latest) | Primary Linux |
| Ubuntu | 22.04 LTS | Supported | Yes | Secondary Linux |
| Ubuntu | 20.04 LTS | Supported | Legacy | End of life soon |
| Windows | 11 | Supported | Yes (windows-latest) | x64 only |
| Windows | 10 | Supported | Yes | x64 only |
| Windows | Server 2022 | Supported | CI runners | Server workloads |
| WSL 2 | Ubuntu 22.04+ | Supported | Not directly | Uses Linux behavior |

### 1.2 Python Version Support

| Python Version | Status | CI Tested | End of Life | Notes |
|---------------|--------|-----------|-------------|-------|
| 3.8 | Supported | No | 2024-10 | Minimum per requirements |
| 3.9 | Supported | No | 2025-10 | Legacy support |
| 3.10 | Supported | No | 2026-10 | Common on Ubuntu 22.04 |
| 3.11 | Supported | Yes | 2027-10 | Recommended |
| 3.12 | Supported | Yes | 2028-10 | Latest stable |
| 3.13 | Untested | No | 2029-10 | Future compatibility |

**Note:** CI tests Python 3.11 and 3.12 as per existing workflow. Requirements specify 3.8+ minimum.

### 1.3 Pipenv Version Compatibility

| Pipenv Version | Status | Notes |
|---------------|--------|-------|
| 2024.x | Supported | Current recommended |
| 2023.x | Supported | Stable |
| 2022.x | Supported | Legacy but functional |
| < 2022 | Unsupported | May have breaking changes |

**Minimum Recommended:** pipenv >= 2022.1.8

---

## 2. Python Installation Methods by Platform

### 2.1 macOS

| Method | Python Path | Pipenv Behavior | Recommended |
|--------|-------------|-----------------|-------------|
| Homebrew (ARM) | /opt/homebrew/bin/python3 | Works directly | Yes |
| Homebrew (Intel) | /usr/local/bin/python3 | Works directly | Yes |
| python.org Installer | /Library/Frameworks/Python.framework/Versions/X.Y/bin/python3 | Works directly | Yes |
| pyenv | ~/.pyenv/shims/python | Works with shims | Yes (power users) |
| System Python | /usr/bin/python3 | Works but outdated | No |
| Xcode CLT | /Library/Developer/CommandLineTools/usr/bin/python3 | Works but limited | No |

### 2.2 Linux (Ubuntu/Debian)

| Method | Python Path | Pipenv Behavior | Recommended |
|--------|-------------|-----------------|-------------|
| apt (system) | /usr/bin/python3 | Works directly | Yes (simple) |
| deadsnakes PPA | /usr/bin/python3.X | Works with explicit version | Yes (multiple versions) |
| pyenv | ~/.pyenv/shims/python | Works with shims | Yes (power users) |
| Anaconda | ~/anaconda3/bin/python | Conflicts possible | No |
| Docker base image | /usr/local/bin/python | Works in container | Yes (containers) |

### 2.3 Windows

| Method | Python Path | Pipenv Behavior | Recommended |
|--------|-------------|-----------------|-------------|
| python.org Installer | C:\PythonXX\python.exe | Works, needs PATH | Yes |
| Windows Store | WindowsApps path | Works | Yes (simple) |
| pyenv-win | %USERPROFILE%\.pyenv\versions\X.Y.Z\python.exe | Works with shims | Yes (power users) |
| Chocolatey | C:\PythonXX\python.exe | Works, needs PATH | Yes |
| Anaconda | %USERPROFILE%\anaconda3\python.exe | Conflicts possible | No |
| WSL | /usr/bin/python3 (Linux) | Uses Linux behavior | Yes (Linux workflow) |

---

## 3. Virtual Environment Compatibility

### 3.1 Virtual Environment Tools

| Tool | Supported | Detection Method | Notes |
|------|-----------|------------------|-------|
| pipenv | Yes (required) | sys.prefix != sys.base_prefix | Official supported method |
| venv | Detected only | sys.prefix != sys.base_prefix | Rejected with guidance to use pipenv |
| virtualenv | Detected only | sys.prefix != sys.base_prefix | Rejected with guidance to use pipenv |
| conda | Detected only | CONDA_PREFIX env var | Rejected with guidance to use pipenv |
| poetry | Detected only | POETRY_ACTIVE env var | Rejected with guidance to use pipenv |

### 3.2 Virtual Environment Detection Matrix

```python
# Detection logic for various virtual environment tools

def detect_virtual_environment() -> Tuple[bool, str]:
    """Detect if in virtual environment and which type."""

    # Standard Python venv detection (works for pipenv, venv, virtualenv)
    if sys.prefix != sys.base_prefix:
        # Determine which tool created the venv
        if os.environ.get('PIPENV_ACTIVE'):
            return True, 'pipenv'
        elif os.environ.get('VIRTUAL_ENV'):
            venv_path = os.environ['VIRTUAL_ENV']
            if '.local/share/virtualenvs' in venv_path:
                return True, 'pipenv'
            else:
                return True, 'venv_or_virtualenv'
        else:
            return True, 'unknown_venv'

    # Conda detection (different mechanism)
    if os.environ.get('CONDA_PREFIX'):
        return True, 'conda'

    # Poetry detection
    if os.environ.get('POETRY_ACTIVE'):
        return True, 'poetry'

    return False, 'none'
```

### 3.3 Error Messages by Virtual Environment Type

| Detected Type | Error Message |
|--------------|---------------|
| none | "Virtual environment required. Run: pipenv install --dev && pipenv shell" |
| venv_or_virtualenv | "Detected venv/virtualenv but nWave requires pipenv. Run: pipenv install --dev && pipenv shell" |
| conda | "Detected conda environment but nWave requires pipenv. Deactivate conda and run: pipenv install --dev && pipenv shell" |
| poetry | "Detected poetry environment but nWave requires pipenv. Run: pipenv install --dev && pipenv shell" |

---

## 4. CI/CD Environment Matrix

### 4.1 GitHub Actions Runners

| Runner | OS | Python Pre-installed | Notes |
|--------|-----|---------------------|-------|
| ubuntu-latest | Ubuntu 22.04 | 3.10 (system) | setup-python used |
| ubuntu-22.04 | Ubuntu 22.04 | 3.10 (system) | Explicit version |
| ubuntu-24.04 | Ubuntu 24.04 | 3.12 (system) | Newer runner |
| windows-latest | Windows Server 2022 | 3.9 (pre-installed) | setup-python used |
| windows-2022 | Windows Server 2022 | 3.9 (pre-installed) | Explicit version |
| macos-latest | macOS 14 (Sonoma) | 3.12 (Homebrew) | ARM64 runner |
| macos-13 | macOS 13 (Ventura) | 3.11 (Homebrew) | Intel runner |

### 4.2 CI Environment Variables

| Platform | Variable | Value | Usage |
|----------|----------|-------|-------|
| GitHub Actions | `CI` | true | Generic CI detection |
| GitHub Actions | `GITHUB_ACTIONS` | true | Platform-specific |
| GitHub Actions | `RUNNER_OS` | Linux/Windows/macOS | OS detection |
| GitHub Actions | `GITHUB_WORKSPACE` | /path/to/repo | Working directory |
| GitLab CI | `CI` | true | Generic CI detection |
| GitLab CI | `GITLAB_CI` | true | Platform-specific |
| Jenkins | `CI` | true | If configured |
| Jenkins | `JENKINS_URL` | http://... | Platform-specific |

### 4.3 CI-Specific Test Matrix

Current CI workflow tests:

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    python-version: ['3.11', '3.12']

# Results in 6 test combinations:
# - ubuntu-latest + 3.11
# - ubuntu-latest + 3.12
# - windows-latest + 3.11
# - windows-latest + 3.12
# - macos-latest + 3.11
# - macos-latest + 3.12
```

---

## 5. Known Issues and Workarounds

### 5.1 macOS Issues

| Issue | Symptom | Workaround |
|-------|---------|------------|
| Command Line Tools missing | xcode-select error | `xcode-select --install` |
| Homebrew Python not in PATH | python3 not found | Add /opt/homebrew/bin to PATH |
| pyenv shims slow | Slow shell startup | Use pyenv only when needed |
| Rosetta 2 confusion | Wrong architecture | Use native ARM Python |

### 5.2 Linux Issues

| Issue | Symptom | Workaround |
|-------|---------|------------|
| pip not installed | pip3: command not found | `sudo apt install python3-pip` |
| pipenv user install | pipenv not in PATH | Add ~/.local/bin to PATH |
| python-is-python3 missing | python: command not found | `sudo apt install python-is-python3` |
| venv module missing | No module named venv | `sudo apt install python3-venv` |

### 5.3 Windows Issues

| Issue | Symptom | Workaround |
|-------|---------|------------|
| Python not in PATH | python: not recognized | Add Python to PATH or reinstall with option |
| Scripts not in PATH | pipenv: not recognized | Add Scripts folder to PATH |
| Long path issues | Path too long errors | Enable long paths in Windows |
| ANSI colors not working | Garbled output | Use colorama or strip ANSI |
| Line ending issues | Git autocrlf problems | `git config core.autocrlf false` |

### 5.4 WSL Issues

| Issue | Symptom | Workaround |
|-------|---------|------------|
| Windows/Linux path confusion | /mnt/c/ vs C:\ | Use native Linux paths |
| Interop slow | Slow pip installs | Use Linux-native tools only |
| Clock skew | File timestamps wrong | `sudo hwclock -s` |

---

## 6. Pipenv Behavior Reference

### 6.1 Critical Pipenv Commands

| Command | Purpose | When Used |
|---------|---------|-----------|
| `pipenv install --dev` | Install all dependencies | Initial setup |
| `pipenv shell` | Activate virtual environment | Interactive use |
| `pipenv run <cmd>` | Run command in venv | Scripted use |
| `pipenv --venv` | Show venv path | Debugging |
| `pipenv --py` | Show Python path | Debugging |
| `pipenv sync --dev` | Sync from lock file | CI (reproducible) |
| `pipenv install --dev --deploy` | Install with strict lock | CI (fail if lock outdated) |

### 6.2 Pipenv Environment Variables

| Variable | Purpose | Effect |
|----------|---------|--------|
| `PIPENV_VENV_IN_PROJECT` | Create .venv in project | Venv at ./.venv |
| `PIPENV_IGNORE_VIRTUALENVS` | Ignore existing venv | Force new venv |
| `PIPENV_NO_INHERIT` | Don't inherit env vars | Isolated environment |
| `PIPENV_ACTIVE` | Set when in pipenv shell | Detection signal |
| `VIRTUAL_ENV` | Path to active venv | Standard venv indicator |

### 6.3 Pipenv Lock File Considerations

| Scenario | Behavior | CI Implication |
|----------|----------|----------------|
| Pipfile.lock exists | Use locked versions | Reproducible builds |
| Pipfile.lock outdated | pipenv install updates | May differ from dev |
| Pipfile.lock missing | Generate new lock | Non-reproducible |
| --deploy flag | Fail if lock outdated | CI safety check |

---

## 7. Recommendations

### 7.1 Minimum Version Requirements

Based on analysis, recommend these minimums:

| Component | Minimum | Recommended | Rationale |
|-----------|---------|-------------|-----------|
| Python | 3.8 | 3.11+ | 3.8 is minimum per requirements; 3.11+ has performance improvements |
| pipenv | 2022.1.8 | 2024.x | Earlier versions may have bugs |
| pip | 21.0 | Latest | Needed to install pipenv |

### 7.2 CI Test Matrix Recommendations

Current matrix (3.11, 3.12 on 3 OSes) is adequate. Consider adding:

- Python 3.10 for Ubuntu 22.04 system Python users
- Python 3.8 for minimum version validation (optional, low priority)

### 7.3 Documentation Recommendations

Document these scenarios explicitly:

1. Fresh macOS with Homebrew
2. Fresh Ubuntu 22.04
3. Fresh Windows 10/11
4. Existing pyenv setup
5. CI/CD environment

---

## 8. Traceability

| Requirement | Matrix Element | Section |
|-------------|---------------|---------|
| NFR-04: Cross-platform | OS Support Matrix | 1.1 |
| C-01: Python 3 only | Python Version Support | 1.2 |
| C-02: pipenv only | Virtual Env Matrix | 3 |
| FR-01: Pre-flight | Detection Methods | 3.2 |
