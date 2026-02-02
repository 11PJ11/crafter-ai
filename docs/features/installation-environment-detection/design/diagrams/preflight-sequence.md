# Pre-flight Check Sequence Diagram

## Main Installation Flow with Pre-flight

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant Main as install_nwave.py
    participant CD as ContextDetector
    participant PF as PreflightChecker
    participant OF as OutputFormatter
    participant Log as Logger
    participant NWI as NWaveInstaller
    participant IV as InstallationVerifier

    User->>Main: python install_nwave.py

    %% Context Detection
    Main->>CD: detect()
    alt TTY stdout
        CD-->>Main: TERMINAL
    else Non-TTY stdout
        CD-->>Main: CLAUDE_CODE
    end

    %% Logger Setup
    Main->>Log: Logger(~/.nwave/install.log)
    Log-->>Main: logger instance

    %% Pre-flight Checks
    Main->>PF: run_all_checks()

    rect rgb(240, 248, 255)
        Note over PF: Check 1: Virtual Environment
        PF->>PF: sys.prefix != sys.base_prefix
        alt In venv
            PF->>PF: PASSED
        else Not in venv
            PF->>PF: FAILED (ENV_NO_VENV)
        end
    end

    rect rgb(240, 255, 240)
        Note over PF: Check 2: Pipenv Installed
        PF->>PF: subprocess.run(['pipenv', '--version'])
        alt Pipenv found
            PF->>PF: PASSED
        else Pipenv missing
            PF->>PF: FAILED (ENV_NO_PIPENV)
        end
    end

    rect rgb(255, 248, 240)
        Note over PF: Check 3: Dependencies
        PF->>PF: __import__('yaml'), __import__('pathlib')
        alt All modules present
            PF->>PF: PASSED
        else Modules missing
            PF->>PF: FAILED (DEP_MISSING)
        end
    end

    rect rgb(248, 240, 255)
        Note over PF: Check 4: Python Version
        PF->>PF: sys.version_info >= (3, 8)
        alt Python >= 3.8
            PF->>PF: PASSED
        else Python < 3.8
            PF->>PF: FAILED (ENV_PYTHON_VERSION)
        end
    end

    PF-->>Main: PreflightResult

    %% Result Handling
    alt All checks passed
        Main->>Log: "Pre-flight checks: ALL PASSED"
        Main->>NWI: Normal installation flow
        NWI-->>Main: Installation complete
        Main->>IV: verify()
        IV-->>Main: VerificationResult
        Main->>OF: format_verification_success()
        OF-->>Main: Formatted success
        Main->>User: Success message
        Main-->>User: exit(0)
    else Any check failed
        Main->>Log: "Pre-flight checks: FAILED"
        Main->>OF: format_preflight_error(result)
        alt TERMINAL context
            OF->>OF: TerminalFormatter
            OF-->>Main: "[ERROR]...[FIX]...[THEN]..."
        else CLAUDE_CODE context
            OF->>OF: JsonFormatter
            OF-->>Main: JSON error object
        end
        Main->>User: Error with remediation
        Main-->>User: exit(1)
    end
```

## Pre-flight Check Details

### Virtual Environment Check Flow

```mermaid
flowchart TD
    A[Start Check] --> B{sys.prefix != sys.base_prefix?}
    B -->|Yes| C[PASSED]
    B -->|No| D[FAILED]
    D --> E[error_code: ENV_NO_VENV]
    D --> F[message: Virtual environment required]
    D --> G[remediation: pipenv install --dev && pipenv shell]
    D --> H[recoverable: true]

    C --> I[Return CheckResult]
    E --> I
    F --> I
    G --> I
    H --> I
```

### Pipenv Check Flow

```mermaid
flowchart TD
    A[Start Check] --> B[subprocess.run pipenv --version]
    B --> C{returncode == 0?}
    C -->|Yes| D[PASSED]
    C -->|No| E{FileNotFoundError?}
    E -->|Yes| F[FAILED - not installed]
    E -->|No| G[FAILED - error running]

    F --> H[error_code: ENV_NO_PIPENV]
    F --> I[message: pipenv is required but not installed]
    F --> J[remediation: pip3 install pipenv]

    D --> K[Return CheckResult]
    H --> K
```

### Dependency Check Flow

```mermaid
flowchart TD
    A[Start Check] --> B[REQUIRED_MODULES = yaml, pathlib]
    B --> C[missing = empty list]
    C --> D{For each module}

    D --> E[try __import__ module]
    E --> F{ImportError?}
    F -->|Yes| G[Add to missing list]
    F -->|No| H[Continue]
    G --> D
    H --> D

    D --> I{missing list empty?}
    I -->|Yes| J[PASSED]
    I -->|No| K[FAILED]

    K --> L[error_code: DEP_MISSING]
    K --> M[message: Missing required modules: ...]
    K --> N[remediation: pipenv install --dev]

    J --> O[Return CheckResult]
    L --> O
```

## Error Output Formatting

### Terminal Format Flow

```mermaid
flowchart LR
    A[CheckResult] --> B{Context?}
    B -->|TERMINAL| C[TerminalFormatter]
    C --> D["[ERROR] message"]
    D --> E["[FIX] remediation"]
    E --> F["[THEN] Re-run installer"]

    style D fill:#ff6b6b
    style E fill:#ffd93d
    style F fill:#6bcb77
```

### Claude Code Format Flow

```mermaid
flowchart LR
    A[CheckResult] --> B{Context?}
    B -->|CLAUDE_CODE| C[JsonFormatter]
    C --> D[JSON Object]

    D --> E["status: error"]
    D --> F["error_code: ..."]
    D --> G["message: ..."]
    D --> H["remediation: ..."]
    D --> I["recoverable: true/false"]
    D --> J["details: {...}"]
```
