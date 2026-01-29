# Infrastructure Decisions: Installation Environment Detection

**Feature ID:** APEX-002
**Wave:** DESIGN (Platform Perspective)
**Created:** 2026-01-29

---

## PADR-001: Pipenv Version Pinning Strategy

### Status
**ACCEPTED**

### Context
The installation system relies on pipenv for environment management. We need to decide whether to:
1. Pin a specific pipenv version
2. Specify a minimum version
3. Accept any pipenv version

### Decision
**Specify minimum version with warning for older versions.**

Minimum required: pipenv >= 2022.1.8
Recommended: pipenv >= 2024.0.0

### Implementation

```python
PIPENV_MIN_VERSION = (2022, 1, 8)
PIPENV_RECOMMENDED_VERSION = (2024, 0, 0)

def check_pipenv_version() -> CheckResult:
    """Check pipenv version meets requirements."""
    try:
        result = subprocess.run(
            ['pipenv', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            return CheckResult(
                name='pipenv_version',
                passed=False,
                error_code='ENV_NO_PIPENV',
                message='Pipenv not installed',
            )

        # Parse version: "pipenv, version 2024.0.1"
        version_str = result.stdout.strip().split()[-1]
        version_tuple = tuple(int(x) for x in version_str.split('.'))

        if version_tuple < PIPENV_MIN_VERSION:
            return CheckResult(
                name='pipenv_version',
                passed=False,
                error_code='ENV_PIPENV_VERSION',
                message=f'Pipenv version {version_str} is below minimum {".".join(map(str, PIPENV_MIN_VERSION))}',
                recoverable=True,
                remediation='pip install --upgrade pipenv',
            )

        if version_tuple < PIPENV_RECOMMENDED_VERSION:
            # Warning, not blocking
            return CheckResult(
                name='pipenv_version',
                passed=True,
                warning=f'Pipenv version {version_str} is below recommended {".".join(map(str, PIPENV_RECOMMENDED_VERSION))}. Consider upgrading.',
            )

        return CheckResult(
            name='pipenv_version',
            passed=True,
            message=f'Pipenv version {version_str} OK',
        )

    except FileNotFoundError:
        return CheckResult(
            name='pipenv_version',
            passed=False,
            error_code='ENV_NO_PIPENV',
            message='Pipenv command not found',
            recoverable=True,
            remediation='pip3 install pipenv',
        )
```

### Rationale

| Option | Pros | Cons |
|--------|------|------|
| Pin specific version | Fully reproducible | Blocks users with different versions |
| Minimum version | Flexibility with safety | May have unknown issues with newer versions |
| Any version | Maximum flexibility | May break on old versions |

**Minimum version selected** because:
1. Pipenv 2022.1.8 introduced important stability fixes
2. Users may have organizational constraints on package versions
3. Newer versions are generally backward compatible
4. Warning for older-but-functional versions is user-friendly

### Consequences

**Positive:**
- Users with recent pipenv work without changes
- Users with old pipenv get clear upgrade path
- Flexibility for organizational constraints

**Negative:**
- Cannot guarantee behavior on untested pipenv versions
- May need to update minimum version as issues are discovered

---

## PADR-002: CI Environment Detection Strategy

### Status
**ACCEPTED**

### Context
When running in CI/CD environments, the installer should behave differently:
- No color output (CI logs don't support ANSI)
- More verbose logging
- Fail-fast on errors
- No interactive prompts

### Decision
**Detect CI via standard environment variables with platform-specific fallbacks.**

### Implementation

```python
class CIEnvironmentDetector:
    """Detects CI/CD environment for specialized behavior."""

    # Order matters: more specific checks first
    CI_INDICATORS = [
        ('GITHUB_ACTIONS', 'GitHub Actions'),
        ('GITLAB_CI', 'GitLab CI'),
        ('JENKINS_URL', 'Jenkins'),
        ('CIRCLECI', 'CircleCI'),
        ('TRAVIS', 'Travis CI'),
        ('TF_BUILD', 'Azure DevOps'),
        ('BUILDKITE', 'Buildkite'),
        ('CODEBUILD_BUILD_ID', 'AWS CodeBuild'),
        ('CI', 'Generic CI'),  # Last resort, many CIs set this
    ]

    @classmethod
    def detect(cls) -> Optional[str]:
        """Detect specific CI platform."""
        for env_var, platform_name in cls.CI_INDICATORS:
            if os.environ.get(env_var):
                return platform_name
        return None

    @classmethod
    def is_ci(cls) -> bool:
        """Return True if running in any CI environment."""
        return cls.detect() is not None

    @classmethod
    def get_ci_context(cls) -> Dict[str, Any]:
        """Get CI-specific context information."""
        platform = cls.detect()
        if not platform:
            return {'is_ci': False}

        context = {
            'is_ci': True,
            'platform': platform,
        }

        # Platform-specific context
        if platform == 'GitHub Actions':
            context.update({
                'repository': os.environ.get('GITHUB_REPOSITORY'),
                'ref': os.environ.get('GITHUB_REF'),
                'sha': os.environ.get('GITHUB_SHA'),
                'run_id': os.environ.get('GITHUB_RUN_ID'),
                'runner_os': os.environ.get('RUNNER_OS'),
            })
        elif platform == 'GitLab CI':
            context.update({
                'project': os.environ.get('CI_PROJECT_NAME'),
                'ref': os.environ.get('CI_COMMIT_REF_NAME'),
                'sha': os.environ.get('CI_COMMIT_SHA'),
                'job_id': os.environ.get('CI_JOB_ID'),
            })

        return context
```

### Rationale

| Option | Pros | Cons |
|--------|------|------|
| Check `CI` env var only | Simple | Many false positives, no platform info |
| Check platform-specific vars | Accurate platform detection | More code, may miss new platforms |
| Combined approach | Best of both | Slightly more complex |

**Combined approach selected** because:
1. Platform-specific detection enables tailored behavior
2. Fallback to generic `CI` catches unknown platforms
3. Context info useful for debugging CI issues

### CI-Specific Behavior

| Behavior | Terminal | CI Environment |
|----------|----------|----------------|
| Color output | Yes (if TTY) | No |
| Progress indicators | Yes | No (flood logs) |
| Interactive prompts | Allowed | Error (non-interactive) |
| Log verbosity | Normal | Verbose |
| Exit on warning | No | Configurable |

### Consequences

**Positive:**
- Installer behaves appropriately in CI
- Platform info helps debug CI-specific issues
- No user configuration needed

**Negative:**
- New CI platforms may not be detected specifically
- `CI=true` in development may trigger CI mode

---

## PADR-003: Container Support Approach

### Status
**ACCEPTED**

### Context
Per requirements (Section 7 - Out of Scope), Docker-based installation is explicitly excluded. However, we need to define behavior if someone attempts installation in a container.

### Decision
**Detect containers and provide informative message; do not block installation.**

### Implementation

```python
def detect_container_environment() -> Optional[str]:
    """Detect if running inside a container."""
    # Docker detection
    if Path('/.dockerenv').exists():
        return 'Docker'

    # Podman detection
    if Path('/run/.containerenv').exists():
        return 'Podman'

    # Kubernetes detection
    if os.environ.get('KUBERNETES_SERVICE_HOST'):
        return 'Kubernetes'

    # Generic cgroup detection
    try:
        with open('/proc/1/cgroup', 'r') as f:
            cgroup_content = f.read()
            if 'docker' in cgroup_content:
                return 'Docker (cgroup)'
            if 'kubepods' in cgroup_content:
                return 'Kubernetes (cgroup)'
            if 'containerd' in cgroup_content:
                return 'containerd'
    except (FileNotFoundError, PermissionError):
        pass

    return None


def handle_container_detection():
    """Handle detection of container environment."""
    container = detect_container_environment()
    if container:
        logger.warn(
            'CONTEXT',
            f'Running in container environment: {container}',
            note='Container installation is not officially supported. Proceed with caution.'
        )
        # Do not block - user may know what they're doing
```

### Rationale

| Option | Pros | Cons |
|--------|------|------|
| Block in containers | Enforces documented scope | Frustrates legitimate use cases |
| Warn and continue | Informative, flexible | May lead to support requests |
| Ignore containers | Simple | Users may be confused by issues |

**Warn and continue selected** because:
1. Some users may have legitimate container use cases
2. Warning sets expectation that support is limited
3. Blocking would be overly restrictive

### Consequences

**Positive:**
- Users informed of unsupported configuration
- Advanced users can still use containers
- Clear documentation of supported/unsupported

**Negative:**
- May receive support requests for container issues
- Container-specific bugs may be reported

---

## PADR-004: Telemetry Opt-in Design

### Status
**DEFERRED**

### Context
Anonymous usage telemetry could help improve the installation experience by identifying:
- Most common errors
- Platform distribution
- Success rates
- Performance metrics

### Decision
**Do not implement telemetry at this time. Design for future opt-in if needed.**

### Rationale

| Option | Pros | Cons |
|--------|------|------|
| No telemetry | Privacy-first, simple | No aggregate data for improvement |
| Opt-out telemetry | More data collected | Privacy concerns, GDPR complexity |
| Opt-in telemetry | User consent, privacy-respecting | Low adoption, less data |

**No telemetry selected** because:
1. Privacy-first approach aligns with developer expectations
2. Installation is infrequent (not ongoing telemetry)
3. Log files provide sufficient debugging info for support
4. Complexity not justified for current scope

### Future Telemetry Design (If Implemented)

If telemetry is added in the future, follow these principles:

1. **Explicit Opt-in:** User must actively enable telemetry
2. **Transparency:** Clear documentation of what is collected
3. **No PII:** Never collect paths, usernames, IPs, or identifiers
4. **Local First:** Aggregate locally, batch upload
5. **Easy Opt-out:** Single command to disable

```python
# Future implementation sketch

TELEMETRY_ENABLED = False  # Default off

def collect_anonymous_metrics() -> Dict[str, Any]:
    """Collect anonymous, aggregate metrics."""
    if not TELEMETRY_ENABLED:
        return {}

    return {
        # Anonymous platform info only
        'platform': platform.system(),
        'python_major_minor': f'{sys.version_info.major}.{sys.version_info.minor}',
        'install_success': True,  # or False
        'error_code': None,  # or error code if failed
        'duration_seconds': 45,
    }
```

### Consequences

**Positive:**
- Privacy-respecting by default
- No GDPR/privacy compliance complexity
- Simpler implementation

**Negative:**
- No aggregate data for improvement
- Rely on user-reported issues

---

## PADR-005: WSL (Windows Subsystem for Linux) Handling

### Status
**ACCEPTED**

### Context
WSL allows running Linux on Windows. The installer must decide:
1. Treat WSL as Linux?
2. Treat WSL as Windows?
3. Treat WSL as a special case?

### Decision
**Treat WSL as Linux with WSL-specific warnings.**

### Implementation

```python
def detect_wsl() -> bool:
    """Detect if running in Windows Subsystem for Linux."""
    # Check /proc/version for WSL indicator
    try:
        with open('/proc/version', 'r') as f:
            version = f.read().lower()
            return 'microsoft' in version or 'wsl' in version
    except FileNotFoundError:
        return False

def get_platform_context() -> Dict[str, Any]:
    """Get platform context with WSL awareness."""
    context = {
        'system': platform.system(),
        'release': platform.release(),
        'is_wsl': False,
    }

    if platform.system() == 'Linux' and detect_wsl():
        context['is_wsl'] = True
        context['wsl_note'] = 'Running in WSL. Use Linux paths (not /mnt/c/).'

    return context
```

### Rationale

WSL runs a real Linux kernel, so:
1. Python behaves as Linux
2. Paths are Linux-style (not Windows)
3. pipenv works as on Linux

However, users may have mixed expectations about Windows/Linux interop.

### WSL-Specific Guidance

| Aspect | Behavior | User Guidance |
|--------|----------|---------------|
| Path format | Linux (/home/user) | Avoid /mnt/c/ for project |
| Python | Linux Python | Use apt/pyenv, not Windows Python |
| pipenv | Linux behavior | Standard Linux installation |
| Installation target | ~/.claude/ | Same as Linux |

### Consequences

**Positive:**
- WSL works out of the box (it's Linux)
- Consistent with Linux behavior
- Warning helps users avoid path confusion

**Negative:**
- Users may expect Windows-specific handling
- /mnt/c/ access is slow (warning helps)

---

## PADR-006: Minimum Python Version Strategy

### Status
**ACCEPTED**

### Context
Requirements specify Python 3.8+ as minimum, but CI tests only 3.11 and 3.12.

### Decision
**Enforce Python 3.8+ as minimum; recommend 3.11+; test 3.11 and 3.12 in CI.**

### Implementation

```python
MIN_PYTHON_VERSION = (3, 8)
RECOMMENDED_PYTHON_VERSION = (3, 11)
TESTED_PYTHON_VERSIONS = [(3, 11), (3, 12)]

def check_python_version() -> CheckResult:
    """Check Python version meets requirements."""
    current = sys.version_info[:2]

    if current < MIN_PYTHON_VERSION:
        return CheckResult(
            name='python_version',
            passed=False,
            error_code='ENV_PYTHON_VERSION',
            message=f'Python {current[0]}.{current[1]} is below minimum {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}',
            recoverable=False,
            remediation='Install Python 3.8 or higher',
        )

    if current < RECOMMENDED_PYTHON_VERSION:
        return CheckResult(
            name='python_version',
            passed=True,
            warning=f'Python {current[0]}.{current[1]} works but 3.11+ is recommended for best performance',
        )

    if current not in TESTED_PYTHON_VERSIONS:
        return CheckResult(
            name='python_version',
            passed=True,
            warning=f'Python {current[0]}.{current[1]} is not in tested versions {TESTED_PYTHON_VERSIONS}',
        )

    return CheckResult(
        name='python_version',
        passed=True,
        message=f'Python {current[0]}.{current[1]} OK',
    )
```

### Rationale

| Version | Status | Rationale |
|---------|--------|-----------|
| 3.7 | Rejected | EOL, missing features |
| 3.8 | Minimum | Still supported, requirements say 3.8+ |
| 3.9 | Supported | Supported |
| 3.10 | Supported | Common on Ubuntu 22.04 |
| 3.11 | Recommended | Performance improvements, CI tested |
| 3.12 | Recommended | Latest stable, CI tested |
| 3.13 | Untested | Future |

### Consequences

**Positive:**
- Broad compatibility (3.8+)
- Clear recommendation (3.11+)
- CI coverage for recommended versions

**Negative:**
- 3.8-3.10 not tested in CI (may have undiscovered issues)
- Must maintain compatibility with older Python

---

## Summary of Infrastructure Decisions

| PADR | Decision | Status |
|------|----------|--------|
| PADR-001 | Pipenv minimum 2022.1.8, recommend 2024+ | Accepted |
| PADR-002 | CI detection via env vars, combined approach | Accepted |
| PADR-003 | Warn in containers, do not block | Accepted |
| PADR-004 | No telemetry, design for future opt-in | Deferred |
| PADR-005 | Treat WSL as Linux with warnings | Accepted |
| PADR-006 | Python 3.8+ minimum, 3.11+ recommended | Accepted |
