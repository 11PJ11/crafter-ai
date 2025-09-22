# AI-Craft Hook System Architecture

## 🏗️ Overview

The AI-Craft framework includes a sophisticated modular hook system that provides automatic code quality enforcement, workflow management, and development assistance. This document describes the architecture, components, and configuration of the hook system.

## 📋 Architecture Components

### Core Architecture

```
~/.claude/hooks/cai/
├── lib/                           # Core modular libraries
│   ├── HookManager.sh            # Central facade and initialization
│   ├── config/
│   │   └── HookConfig.sh         # Configuration management
│   ├── logging/
│   │   └── LogManager.sh         # Unified logging framework
│   ├── tools/
│   │   ├── ToolDetector.sh       # Tool availability detection
│   │   ├── ToolManager.sh        # Tool path management
│   │   ├── LanguageDetector.sh   # Project language detection
│   │   └── JsonUtils.sh          # JSON processing utilities
│   └── formatters/
│       ├── FormatterRegistry.sh  # Formatter coordination
│       ├── BaseFormatter.sh      # Base formatter interface
│       ├── PythonFormatter.sh    # Python-specific formatting
│       └── JavaScriptFormatter.sh # JavaScript-specific formatting
├── workflow/                      # ATDD workflow hooks
│   ├── state-initializer.sh      # Initialize CAI workflow state
│   ├── input-validator.sh        # Validate file access and CAI workflow
│   ├── stage-transition.sh       # Manage ATDD stage transitions
│   ├── context-isolator.py       # Isolate agent context
│   └── output-monitor.py         # Monitor output and transitions
├── code-quality/                  # Code quality enforcement
│   └── lint-format.sh            # Auto-lint and format source files
├── config/                        # Configuration files
│   └── hooks-config.json         # Hook registration configuration
└── test_*.sh                     # Validation and testing scripts
```

## 🔧 Component Details

### HookManager.sh - Central Facade

**Purpose**: Main facade for the modular hook system providing unified initialization and configuration.

**Key Functions**:
```bash
init_hook_system()    # Initialize hook system with configuration validation
```

**Dependencies**:
- `HookConfig.sh` - Configuration management
- `LogManager.sh` - Logging framework
- `ToolDetector.sh` - Tool availability checking

**Configuration**: Uses centralized configuration from `HookConfig.sh`

### LogManager.sh - Unified Logging

**Purpose**: Provides consistent logging across all hook components with configurable verbosity.

**Log Levels**:
```bash
LOG_LEVEL_ERROR=0   # Critical errors only (default)
LOG_LEVEL_WARN=1    # Warnings and errors
LOG_LEVEL_INFO=2    # Informational messages
LOG_LEVEL_DEBUG=3   # Verbose debugging
```

**Configuration**:
```bash
export HOOK_LOG_LEVEL=2  # Set desired log level
```

**Usage Pattern**:
```bash
source "${HOOK_LIB_DIR}/logging/LogManager.sh"
hook_log "$LOG_LEVEL_INFO" "ComponentName" "Message text"
```

### ToolManager.sh - Tool Management

**Purpose**: Manages tool detection, path configuration, and availability checking for formatters.

**Key Functions**:
- Tool availability detection (black, isort, ruff, prettier, shellcheck)
- Tool path configuration and caching
- Installation method detection (pipx, npm, system packages)

**Supported Tools**:
- **Python**: black, isort, ruff
- **JavaScript/JSON**: prettier, eslint
- **Shell**: shellcheck
- **Markdown**: prettier

### FormatterRegistry.sh - Language Coordination

**Purpose**: Coordinates language detection and formatter dispatching using Strategy pattern.

**Architecture**:
- **Strategy Pattern**: Different formatters for different languages
- **Factory Pattern**: Dynamic formatter creation based on language detection
- **Registry Pattern**: Centralized formatter management

**Workflow**:
1. Language detection via `LanguageDetector.sh`
2. Formatter selection based on detected languages
3. Strategy pattern dispatch to appropriate formatter
4. Execution with tool availability validation

### Language-Specific Formatters

#### PythonFormatter.sh
**Purpose**: Python code formatting using black, isort, and ruff.

**Tools Required**:
```bash
black    # Code formatting
isort    # Import sorting
ruff     # Linting and additional formatting
```

**File Patterns**: `*.py`

#### JavaScriptFormatter.sh
**Purpose**: JavaScript/TypeScript formatting using prettier and eslint.

**Tools Required**:
```bash
prettier  # Code formatting
eslint    # Linting (optional)
```

**File Patterns**: `*.js`, `*.ts`, `*.jsx`, `*.tsx`

## 🔄 Workflow Hooks

### State Initializer (state-initializer.sh)

**Purpose**: Initialize CAI workflow state and environment setup.

**Trigger**: `UserPromptInit` event
**Function**:
- Initialize workflow state files
- Set up environment variables
- Prepare workspace for ATDD workflow

### Input Validator (input-validator.sh)

**Purpose**: Validate file access and CAI workflow compliance.

**Trigger**: `PreToolUse` with `Read` tool and `cai-workflow-active` condition
**Function**:
- Validate file access permissions
- Check CAI workflow compliance
- Ensure proper agent context

### Stage Transition (stage-transition.sh)

**Purpose**: Manage ATDD stage transitions (DISCUSS → ARCHITECT → DISTILL → DEVELOP → DEMO).

**Trigger**: `PostToolUse` with `Write` tool and `cai-workflow-active` condition
**Function**:
- Monitor stage completion criteria
- Trigger appropriate stage transitions
- Update workflow state documentation

### Code Quality (lint-format.sh)

**Purpose**: Automatic code quality enforcement through linting and formatting.

**Trigger**: `PostToolUse` with `Write|Edit|MultiEdit` tools
**Function**:
- Detect project languages
- Apply appropriate formatters
- Report formatting results
- Maintain code quality standards

## ⚙️ Configuration

### Hook Registration

Hooks are registered in `~/.claude/settings.local.json`:

```json
{
  "hooks": {
    "UserPromptInit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "/home/user/.claude/hooks/cai/workflow/state-initializer.sh",
            "id": "cai-state-initializer"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Read",
        "condition": "cai-workflow-active",
        "hooks": [
          {
            "type": "command",
            "command": "/home/user/.claude/hooks/cai/workflow/input-validator.sh",
            "id": "cai-input-validator"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "/home/user/.claude/hooks/cai/code-quality/lint-format.sh",
            "id": "cai-auto-lint-format"
          }
        ]
      }
    ]
  }
}
```

### Environment Configuration

```bash
# Logging configuration
export HOOK_LOG_LEVEL=2              # 0=ERROR, 1=WARN, 2=INFO, 3=DEBUG

# Tool paths (optional, auto-detected)
export PYTHON_FORMATTER_BLACK="/usr/local/bin/black"
export PYTHON_FORMATTER_ISORT="/usr/local/bin/isort"
export PYTHON_FORMATTER_RUFF="/usr/local/bin/ruff"

# Workflow configuration
export CAI_WORKFLOW_ACTIVE=true      # Enable CAI workflow hooks
```

## 🧪 Testing and Validation

### Test Scripts

#### test_modular_system.sh
**Purpose**: Validate modular hook system functionality.

**Tests**:
- HookManager initialization
- Component loading and integration
- Configuration validation
- Basic functionality verification

#### test_migration_validation.sh
**Purpose**: Validate migration from legacy to modular system.

**Tests**:
- Backward compatibility
- Feature equivalence
- Performance comparison
- Error handling consistency

### Manual Testing

#### Basic Functionality Test
```bash
# Test hook initialization
cd ~/.claude/hooks/cai
source lib/HookManager.sh
init_hook_system

# Test logging
env HOOK_LOG_LEVEL=3 ./code-quality/lint-format.sh test.py

# Test workflow hooks
./workflow/state-initializer.sh
./workflow/input-validator.sh docs/craft-ai/test.md
```

#### Integration Testing
```bash
# Create test project
mkdir -p /tmp/ai-craft-test
cd /tmp/ai-craft-test

# Create test files
echo 'print("Hello World")' > test.py
echo '{"test": "value"}' > test.json
echo 'console.log("test")' > test.js

# Test auto-formatting
env HOOK_LOG_LEVEL=2 ~/.claude/hooks/cai/code-quality/lint-format.sh .

# Cleanup
cd - && rm -rf /tmp/ai-craft-test
```

## 🔍 Troubleshooting

### Common Issues

#### Hook Not Executing
1. **Check Registration**: Verify hook is registered in `settings.local.json`
2. **Check Permissions**: Ensure hook scripts are executable (`chmod +x`)
3. **Check Conditions**: Verify trigger conditions are met
4. **Check Logging**: Enable debug logging (`HOOK_LOG_LEVEL=3`)

#### Tools Not Found
1. **Python Tools**: Install with `pip install black isort ruff` or `pipx install black isort ruff`
2. **JavaScript Tools**: Install with `npm install -g prettier eslint`
3. **Shell Tools**: Install with package manager (`apt install shellcheck`)

#### Logging Not Working
1. **Check Environment**: `echo $HOOK_LOG_LEVEL`
2. **Set Level**: `export HOOK_LOG_LEVEL=2`
3. **Test Directly**: `env HOOK_LOG_LEVEL=3 ./hook-script.sh`

### Debug Information

#### Environment Check
```bash
echo "HOOK_LOG_LEVEL: ${HOOK_LOG_LEVEL:-not set}"
echo "CAI_WORKFLOW_ACTIVE: ${CAI_WORKFLOW_ACTIVE:-not set}"
ls -la ~/.claude/hooks/cai/
```

#### Hook Execution Test
```bash
env HOOK_LOG_LEVEL=3 bash -c '
  cd ~/.claude/hooks/cai &&
  source lib/HookManager.sh &&
  init_hook_system
'
```

## 📚 Development Guidelines

### Adding New Hooks

1. **Create Hook Script**: Place in appropriate directory (`workflow/`, `code-quality/`)
2. **Follow Naming Convention**: Use kebab-case with `.sh` extension
3. **Include Logging**: Use `LogManager.sh` for consistent logging
4. **Add Error Handling**: Implement proper error handling and recovery
5. **Register Hook**: Add to `settings.local.json` with appropriate triggers
6. **Add Tests**: Create test cases in test scripts
7. **Update Documentation**: Document in this file

### Modifying Existing Hooks

1. **Maintain Compatibility**: Ensure backward compatibility
2. **Update Tests**: Modify test cases as needed
3. **Version Logging**: Update version information in logs
4. **Performance Testing**: Verify performance impact
5. **Documentation**: Update this documentation

### Best Practices

1. **Single Responsibility**: Each hook should have one clear purpose
2. **Error Handling**: Always handle errors gracefully
3. **Logging**: Use appropriate log levels and clear messages
4. **Performance**: Minimize execution time and resource usage
5. **Testing**: Include comprehensive test coverage
6. **Documentation**: Keep documentation current and comprehensive

## 🔄 Maintenance

### Regular Tasks

1. **Update Tools**: Keep formatting tools up to date
2. **Review Logs**: Monitor hook execution logs for issues
3. **Performance Check**: Monitor hook execution performance
4. **Test Validation**: Run test scripts regularly
5. **Documentation**: Keep documentation synchronized with code changes

### Upgrades

1. **Backup Settings**: Save current `settings.local.json`
2. **Test New Version**: Validate new hooks in test environment
3. **Migrate Configuration**: Update configuration as needed
4. **Validate Operation**: Run comprehensive tests
5. **Monitor**: Watch for issues after upgrade

---

**For detailed logging configuration, see `LOGGING_CONFIGURATION.md`**

**For installation and setup, see `README.md` and `install-ai-craft.sh`**