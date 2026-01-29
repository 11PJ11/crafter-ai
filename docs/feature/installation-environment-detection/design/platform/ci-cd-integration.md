# CI/CD Integration: Installation Environment Detection

**Feature ID:** APEX-002
**Wave:** DESIGN (Platform Perspective)
**Created:** 2026-01-29

---

## 1. Current CI/CD Analysis

### 1.1 Existing Workflow Structure

The project has a comprehensive CI/CD pipeline in `.github/workflows/ci-cd.yml`:

```
Stage 1: Fast Checks (parallel, ~1 min)
    - commitlint: Conventional commits
    - code-quality: Ruff lint + format
    - file-quality: Whitespace, EOF, YAML, JSON
    - security-checks: Merge conflicts, private keys, shell prevention

Stage 2: Framework Validation (~2 min)
    - framework-validation: Catalog, docs, freshness, conflicts
    (depends on Stage 1)

Stage 3: Cross-Platform Tests (~10 min)
    - test: 3 OS x 2 Python = 6 matrix jobs
    (depends on Stage 2)

Stage 4: Agent Validation (~1 min)
    - agent-sync: Name synchronization
    (depends on Stage 3)

Stage 5: Build (tags only, ~5 min)
    - build: Create release packages
    (depends on Stage 4)

Stage 6: Release (tags only, ~2 min)
    - release: Publish to GitHub Releases
    (depends on Stage 5)
```

### 1.2 Current Pipenv Usage in CI

The workflow already uses pipenv correctly:

```yaml
- name: Install pipenv and dependencies
  run: |
    python3 -m pip install --upgrade pip setuptools wheel pipenv
    pipenv install --dev --deploy --ignore-pipfile || pipenv install --dev
  shell: bash
```

**Analysis:**
- `--deploy` flag ensures Pipfile.lock is used (reproducibility)
- `--ignore-pipfile` uses lock file exclusively
- Fallback `|| pipenv install --dev` handles lock file issues

### 1.3 Test Execution Pattern

```yaml
- name: Run pytest test suite
  run: |
    pipenv run pytest tests/ \
      --verbose \
      --tb=short \
      --cov=. \
      --cov-report=term-missing \
      --cov-report=xml \
      --cov-report=html \
      --junitxml=test-results-${{ matrix.os }}-py${{ matrix.python-version }}.xml
  shell: bash
```

---

## 2. Installation Pipeline Integration

### 2.1 Recommended Workflow Additions

Add installation verification to the test stage:

```yaml
# Add after "Install pipenv and dependencies"

- name: Verify installer preflight checks
  run: |
    pipenv run python -c "
    import sys
    sys.path.insert(0, 'scripts/install')
    from preflight_checker import PreflightChecker
    result = PreflightChecker().run_all_checks()
    print(f'Preflight checks: {\"PASSED\" if result.passed else \"FAILED\"}')
    for check in result.checks:
        status = 'PASS' if check.passed else 'FAIL'
        print(f'  [{status}] {check.name}')
    if not result.passed:
        sys.exit(1)
    "
  shell: bash

- name: Test installation (dry-run)
  run: |
    pipenv run python scripts/install/install_nwave.py --dry-run
  shell: bash
```

### 2.2 Installation Test Job

For comprehensive installation testing, add a dedicated job:

```yaml
installation-test:
  name: "Installation Test - ${{ matrix.os }}"
  runs-on: ${{ matrix.os }}
  timeout-minutes: 15
  needs: [framework-validation]
  strategy:
    fail-fast: false
    matrix:
      os: [ubuntu-latest, windows-latest, macos-latest]

  steps:
    - uses: actions/checkout@v4

    - uses: actions/setup-python@v5
      with:
        python-version: '3.12'

    - name: Install pipenv
      run: python3 -m pip install --upgrade pip pipenv
      shell: bash

    - name: Install dependencies
      run: pipenv install --dev
      shell: bash

    - name: Run preflight checks
      run: |
        pipenv run python scripts/install/install_nwave.py --dry-run
      shell: bash

    - name: Full installation test
      run: |
        pipenv run python scripts/install/install_nwave.py
      shell: bash

    - name: Verify installation
      run: |
        pipenv run python scripts/install/verify_nwave.py
      shell: bash

    - name: Cleanup
      if: always()
      run: |
        pipenv run python scripts/install/uninstall_nwave.py --force
      shell: bash
```

---

## 3. Pre-commit Hook Integration

### 3.1 Current Hook Analysis

The `.pre-commit-config.yaml` defines several local hooks:

| Hook | Stage | Impact on Installer |
|------|-------|---------------------|
| prevent-shell-scripts | pre-commit | Ensures installer stays Python |
| nwave-version-bump | pre-commit | May affect installer version |
| pytest-validation | post-commit | Tests installer code |
| yaml-validation | pre-commit | Validates installer configs |
| ruff | pre-commit | Lints installer code |

### 3.2 Installer Code Linting

Ensure installer code is included in ruff checks:

```yaml
# In .pre-commit-config.yaml
- id: ruff
  args: [--fix]
  files: ^(scripts/|tools/|tests/).*\.py$  # Already includes scripts/install/
```

### 3.3 Recommended New Hook

Add installation verification as a pre-push hook:

```yaml
# Add to .pre-commit-config.yaml

- id: installation-preflight
  name: Installation Preflight Check
  entry: python3 -c "import sys; sys.path.insert(0, 'scripts/install'); from preflight_checker import PreflightChecker; r = PreflightChecker().run_all_checks(); sys.exit(0 if r.passed else 1)"
  language: system
  pass_filenames: false
  stages: [pre-push]
  files: ^scripts/install/
```

---

## 4. Docker Integration Patterns

### 4.1 Docker Support Status

Per requirements, Docker-based installation is **out of scope** (see requirements.md Section 7).

However, document the pattern for future reference:

### 4.2 Multi-stage Dockerfile Pattern (Reference Only)

```dockerfile
# NOT FOR IMPLEMENTATION - Reference pattern only

# Stage 1: Build environment with pipenv
FROM python:3.12-slim as builder

WORKDIR /app
COPY Pipfile Pipfile.lock ./

# Install pipenv and dependencies
RUN pip install pipenv && \
    pipenv install --dev --system --deploy

# Stage 2: Runtime with installed dependencies
FROM python:3.12-slim as runtime

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY . .

# Run installer
RUN python scripts/install/install_nwave.py
```

### 4.3 CI Detection in Containers

When running in Docker within CI:

```python
def is_container_environment() -> bool:
    """Detect if running inside a container."""
    # Check for Docker
    if Path('/.dockerenv').exists():
        return True

    # Check for Kubernetes/container runtime
    if os.environ.get('KUBERNETES_SERVICE_HOST'):
        return True

    # Check cgroup for container indicators
    try:
        with open('/proc/1/cgroup', 'r') as f:
            return 'docker' in f.read() or 'kubepods' in f.read()
    except (FileNotFoundError, PermissionError):
        pass

    return False
```

---

## 5. GitHub Actions Best Practices

### 5.1 Caching Strategy

Current caching is well-implemented:

```yaml
- name: Cache pip dependencies
  uses: actions/cache@v4
  with:
    path: |
      ~/.cache/pip
      ~/Library/Caches/pip
      ~\AppData\Local\pip\Cache
    key: ${{ runner.os }}-pip-${{ env.CACHE_VERSION }}-${{ matrix.python-version }}-${{ hashFiles('Pipfile.lock') }}
    restore-keys: |
      ${{ runner.os }}-pip-${{ env.CACHE_VERSION }}-${{ matrix.python-version }}-
      ${{ runner.os }}-pip-${{ env.CACHE_VERSION }}-
```

### 5.2 Recommended: Cache pipenv virtualenvs

Add virtualenv caching for faster CI:

```yaml
- name: Cache pipenv virtualenv
  uses: actions/cache@v4
  with:
    path: |
      ~/.local/share/virtualenvs
      ~\.virtualenvs
    key: ${{ runner.os }}-pipenv-${{ env.CACHE_VERSION }}-${{ matrix.python-version }}-${{ hashFiles('Pipfile.lock') }}
    restore-keys: |
      ${{ runner.os }}-pipenv-${{ env.CACHE_VERSION }}-${{ matrix.python-version }}-
```

### 5.3 Timeout Configuration

Current timeouts are appropriate:

| Job | Timeout | Rationale |
|-----|---------|-----------|
| Fast checks | 5 min | Simple checks |
| Framework validation | 5 min | File operations |
| Test matrix | 30 min | Cross-platform, coverage |
| Build | 20 min | Package creation |
| Release | 10 min | Upload only |

### 5.4 Concurrency Control

Current concurrency is well-configured:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

This prevents redundant CI runs on rapid pushes.

---

## 6. Pipeline Gate Design

### 6.1 Quality Gate Mapping

| Gate | CI Stage | Blocking | Exit Code |
|------|----------|----------|-----------|
| Commits valid | commitlint | Yes | 1 on fail |
| Code linted | code-quality | Yes | 1 on fail |
| Files clean | file-quality | Yes | 1 on fail |
| No secrets | security-checks | Yes | 1 on fail |
| Catalog valid | framework-validation | Yes | 1 on fail |
| Tests pass | test | Yes | 1 on fail |
| Agents synced | agent-sync | Yes | 1 on fail |
| Build succeeds | build | Yes | 1 on fail |

### 6.2 Installation-Specific Gates

| Gate | Condition | Blocking | Remediation |
|------|-----------|----------|-------------|
| Virtual env active | sys.prefix != sys.base_prefix | Yes | pipenv shell |
| Pipenv available | pipenv --version exits 0 | Yes | pip install pipenv |
| Deps installed | import yaml succeeds | Yes | pipenv install --dev |
| Python version | >= 3.8 | No (warn) | Upgrade Python |
| Agent count | >= 28 files | No (warn) | Rebuild |
| Command count | >= 23 files | No (warn) | Rebuild |

---

## 7. Error Handling in CI

### 7.1 Failure Notification

GitHub Actions provides built-in failure notifications. Consider adding:

```yaml
- name: Notify on failure
  if: failure()
  uses: actions/github-script@v7
  with:
    script: |
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: 'CI failed. Please check the [workflow run](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})'
      })
```

### 7.2 Artifact Collection on Failure

```yaml
- name: Upload logs on failure
  if: failure()
  uses: actions/upload-artifact@v4
  with:
    name: failure-logs-${{ matrix.os }}-py${{ matrix.python-version }}
    path: |
      ~/.nwave/install.log
      test-results-*.xml
    retention-days: 7
```

---

## 8. Release Pipeline Integration

### 8.1 Current Release Process

The workflow correctly handles releases:

```yaml
build:
  if: startsWith(github.ref, 'refs/tags/v')
  # ... builds release packages

release:
  if: startsWith(github.ref, 'refs/tags/v')
  # ... publishes to GitHub Releases
```

### 8.2 Version Consistency Check

The build job verifies version consistency:

```yaml
- name: Verify version consistency
  run: |
    TAG_VERSION="${{ steps.get_version.outputs.VERSION }}"
    CATALOG_VERSION=$(pipenv run python3 -c "import yaml; print(yaml.safe_load(open('nWave/framework-catalog.yaml'))['version'])")

    if [ "$TAG_VERSION" != "$CATALOG_VERSION" ]; then
      echo "::error::Version mismatch - tag: ${TAG_VERSION}, catalog: ${CATALOG_VERSION}"
      exit 1
    fi
```

### 8.3 Recommendation: Add Installer Version Check

```yaml
- name: Verify installer version consistency
  run: |
    TAG_VERSION="${{ steps.get_version.outputs.VERSION }}"
    INSTALLER_VERSION=$(pipenv run python3 -c "from scripts.install.install_nwave import __version__; print(__version__)")

    if [ "$TAG_VERSION" != "$INSTALLER_VERSION" ]; then
      echo "::warning::Installer version ($INSTALLER_VERSION) differs from tag ($TAG_VERSION)"
    fi
```

---

## 9. Metrics and Observability

### 9.1 CI Metrics to Track

| Metric | Source | Purpose |
|--------|--------|---------|
| CI duration | GitHub API | Identify slowdowns |
| Test pass rate | JUnit XML | Quality trend |
| Coverage | coverage.xml | Code quality |
| Cache hit rate | Actions logs | Efficiency |
| Failure rate | GitHub API | Stability |

### 9.2 GitHub Actions Job Summary

Leverage job summary for visibility:

```yaml
- name: Installation Summary
  if: always()
  run: |
    echo "## Installation Test Results" >> $GITHUB_STEP_SUMMARY
    echo "" >> $GITHUB_STEP_SUMMARY
    echo "| Check | Status |" >> $GITHUB_STEP_SUMMARY
    echo "|-------|--------|" >> $GITHUB_STEP_SUMMARY
    echo "| Preflight | ${{ steps.preflight.outcome }} |" >> $GITHUB_STEP_SUMMARY
    echo "| Installation | ${{ steps.install.outcome }} |" >> $GITHUB_STEP_SUMMARY
    echo "| Verification | ${{ steps.verify.outcome }} |" >> $GITHUB_STEP_SUMMARY
  shell: bash
```

---

## 10. Traceability

| Requirement | CI Integration Element | Section |
|-------------|----------------------|---------|
| NFR-04: Cross-platform | Matrix testing | 2.2 |
| FR-01: Pre-flight | CI preflight job | 2.1 |
| FR-06: Auto verification | Verify step | 2.2 |
| FR-08: Logging | Artifact upload | 7.2 |
| C-02: pipenv only | pipenv install | 1.2 |
