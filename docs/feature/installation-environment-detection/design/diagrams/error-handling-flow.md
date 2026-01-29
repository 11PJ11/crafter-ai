# Error Handling Flow Diagrams

## Complete Error Handling Architecture

```mermaid
flowchart TB
    subgraph "Error Detection"
        A[Pre-flight Check]
        B[Build Phase]
        C[Verification Phase]
    end

    subgraph "Error Classification"
        D{Error Type}
        E[ENV_NO_VENV]
        F[ENV_NO_PIPENV]
        G[ENV_PYTHON_VERSION]
        H[DEP_MISSING]
        I[BUILD_FAILED]
        J[VERIFY_FAILED]
    end

    subgraph "Error Metadata"
        K[error_codes.py]
        L{Recoverable?}
        M[remediation command]
        N[no remediation]
    end

    subgraph "Output Routing"
        O{Context?}
        P[TerminalFormatter]
        Q[JsonFormatter]
    end

    subgraph "Output Channels"
        R[Terminal stdout]
        S[JSON stdout]
        T[Log file]
    end

    A --> D
    B --> D
    C --> D

    D --> E
    D --> F
    D --> G
    D --> H
    D --> I
    D --> J

    E --> K
    F --> K
    G --> K
    H --> K
    I --> K
    J --> K

    K --> L
    L -->|Yes| M
    L -->|No| N

    M --> O
    N --> O

    O -->|TERMINAL| P
    O -->|CLAUDE_CODE| Q

    P --> R
    Q --> S

    K --> T
```

## Error Code Decision Tree

```mermaid
flowchart TD
    A[Error Occurs] --> B{Where?}

    B -->|Pre-flight| C{Which check?}
    B -->|Build| I[BUILD_FAILED]
    B -->|Verification| J[VERIFY_FAILED]

    C -->|Virtual Env| D[ENV_NO_VENV]
    C -->|Pipenv| E[ENV_NO_PIPENV]
    C -->|Dependencies| F[DEP_MISSING]
    C -->|Python Version| G[ENV_PYTHON_VERSION]

    D --> K{Recoverable?}
    E --> K
    F --> K
    G --> L[NOT recoverable]
    I --> L
    J --> K

    K -->|Yes| M[Provide remediation]
    L -->|No| N[Provide guidance only]

    M --> O[User can fix and retry]
    N --> P[Manual intervention needed]

    style D fill:#ffeb3b
    style E fill:#ffeb3b
    style F fill:#ffeb3b
    style G fill:#ff9800
    style I fill:#f44336
    style J fill:#ffeb3b
```

## Terminal Error Format Structure

```mermaid
flowchart LR
    subgraph "Error Structure"
        A["[ERROR]"] --> B[Red text]
        C["[FIX]"] --> D[Yellow text]
        E["[THEN]"] --> F[Blue text]
    end

    subgraph "Example Output"
        G["[ERROR] Virtual environment required..."]
        H["[FIX] Run: pipenv install --dev && pipenv shell"]
        I["[THEN] Run: python scripts/install/install_nwave.py"]
    end

    A --> G
    C --> H
    E --> I

    style A fill:#ff6b6b,color:#fff
    style C fill:#ffd93d,color:#000
    style E fill:#6bcb77,color:#fff
```

## JSON Error Format Structure

```mermaid
flowchart TB
    subgraph "JSON Schema"
        A[status: error]
        B[error_code: string]
        C[message: string]
        D[remediation: string|null]
        E[recoverable: boolean]
        F[details: object]
    end

    subgraph "Details Object"
        G[python_version]
        H[sys_prefix]
        I[missing_modules]
        J[exit_code]
        K[stderr]
    end

    F --> G
    F --> H
    F --> I
    F --> J
    F --> K
```

## Error Recovery Flow

```mermaid
stateDiagram-v2
    [*] --> PreflightCheck

    PreflightCheck --> VenvCheck
    VenvCheck --> PipenvCheck: PASSED
    VenvCheck --> ErrorOutput: FAILED

    PipenvCheck --> DepCheck: PASSED
    PipenvCheck --> ErrorOutput: FAILED

    DepCheck --> VersionCheck: PASSED
    DepCheck --> ErrorOutput: FAILED

    VersionCheck --> Installation: PASSED
    VersionCheck --> ErrorOutput: FAILED

    Installation --> Verification: SUCCESS
    Installation --> ErrorOutput: BUILD_FAILED

    Verification --> Success: PASSED
    Verification --> ErrorOutput: FAILED

    ErrorOutput --> UserAction
    UserAction --> PreflightCheck: Retry after fix

    Success --> [*]

    note right of ErrorOutput
        Context-aware formatting:
        - Terminal: [ERROR]/[FIX]/[THEN]
        - Claude Code: JSON object
    end note

    note right of UserAction
        Recoverable errors provide
        exact commands to fix
    end note
```

## Logging Strategy

```mermaid
flowchart TB
    subgraph "Log Levels"
        INFO[INFO]
        WARN[WARN]
        ERROR[ERROR]
    end

    subgraph "Log Events"
        A[Session start]
        B[Check passed]
        C[Check failed]
        D[Build started]
        E[Build failed]
        F[Verification result]
    end

    subgraph "Log File"
        G["~/.nwave/install.log"]
    end

    A --> INFO
    B --> INFO
    C --> ERROR
    D --> INFO
    E --> ERROR
    F --> INFO

    INFO --> G
    WARN --> G
    ERROR --> G

    style INFO fill:#4caf50
    style WARN fill:#ff9800
    style ERROR fill:#f44336
```

## Multi-Error Handling

```mermaid
flowchart TB
    A[Run all checks] --> B[Collect results]

    B --> C{Any failures?}

    C -->|No| D[Continue installation]
    C -->|Yes| E[Collect all failures]

    E --> F{How many?}

    F -->|1 error| G[Show single error]
    F -->|Multiple| H[Show all errors]

    G --> I[Terminal format]
    H --> I

    I --> J["First error details"]
    I --> K["Additional errors summary"]

    subgraph "Terminal Output"
        L["[ERROR] Virtual environment required...
        [FIX] Run: pipenv install --dev && pipenv shell

        [ALSO] 2 additional issues found:
        - Missing module: yaml
        - Python version: 3.7 (requires 3.8+)"]
    end

    J --> L
    K --> L
```

## Recovery Actions by Error Type

```mermaid
graph LR
    subgraph "Errors"
        A[ENV_NO_VENV]
        B[ENV_NO_PIPENV]
        C[DEP_MISSING]
        D[ENV_PYTHON_VERSION]
        E[BUILD_FAILED]
        F[VERIFY_FAILED]
    end

    subgraph "Recovery Actions"
        G["pipenv install --dev && pipenv shell"]
        H["pip3 install pipenv"]
        I["pipenv install --dev"]
        J["Install Python 3.8+"]
        K["Check build logs"]
        L["Re-run installer"]
    end

    A --> G
    B --> H
    C --> I
    D --> J
    E --> K
    F --> L

    style G fill:#c8e6c9
    style H fill:#c8e6c9
    style I fill:#c8e6c9
    style J fill:#ffecb3
    style K fill:#ffcdd2
    style L fill:#c8e6c9
```
