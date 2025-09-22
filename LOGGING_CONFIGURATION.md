# AI-Craft Hook System Logging Configuration Guide

## 📋 Overview

The AI-Craft framework includes a sophisticated modular hook system with configurable logging designed for troubleshooting, monitoring, and understanding framework behavior. This guide provides comprehensive information on configuring and using the logging system.

## 🔧 Logging Architecture

### Core Components

The logging system is built on a modular architecture with the following components:

#### **LogManager.sh** (`~/.claude/hooks/cai/lib/logging/LogManager.sh`)
- **Purpose**: Unified logging framework for all hook components
- **Features**: Configurable log levels, timestamp formatting, component identification
- **Configuration**: Uses `HOOK_LOG_LEVEL` environment variable

#### **HookManager.sh** (`~/.claude/hooks/cai/lib/HookManager.sh`)
- **Purpose**: Central facade for hook system initialization
- **Logs**: System initialization, configuration loading, module coordination

#### **Component Loggers**
All hook components implement standardized logging:
- **ToolManager**: Tool detection and path configuration
- **FormatterRegistry**: Language detection and formatter coordination
- **LanguageDetector**: Project language analysis
- **BaseFormatter**: File pattern matching and tool validation
- **Language Formatters**: Python, JavaScript, JSON, Markdown formatters

## 📊 Log Levels

### Level Definitions

```bash
LOG_LEVEL_ERROR=0   # Critical errors only (default/silent)
LOG_LEVEL_WARN=1    # Warnings and errors
LOG_LEVEL_INFO=2    # Informational messages (recommended)
LOG_LEVEL_DEBUG=3   # Verbose debugging information
```

### Usage Recommendations

- **Production**: `HOOK_LOG_LEVEL=0` (silent)
- **Development**: `HOOK_LOG_LEVEL=2` (informational)
- **Debugging**: `HOOK_LOG_LEVEL=3` (verbose)
- **CI/CD**: `HOOK_LOG_LEVEL=1` (warnings only)

## ⚙️ Configuration

### Persistent Configuration

Add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
# AI-Craft hooks logging configuration
export HOOK_LOG_LEVEL=2  # INFO level (recommended)

# Alternative levels:
# export HOOK_LOG_LEVEL=0  # Silent (production)
# export HOOK_LOG_LEVEL=1  # Warnings only
# export HOOK_LOG_LEVEL=3  # Debug (verbose)
```

### Session-Only Configuration

For temporary debugging:

```bash
# Set for current session
export HOOK_LOG_LEVEL=3

# Set for single command
env HOOK_LOG_LEVEL=3 ~/.claude/hooks/cai/code-quality/lint-format.sh test.py
```

### Verification

Check current configuration:

```bash
echo "Current HOOK_LOG_LEVEL: ${HOOK_LOG_LEVEL:-not set}"
```

## 📝 Log Output Examples

### INFO Level (HOOK_LOG_LEVEL=2)

Minimal informational output:
```
2025-09-22 16:06:50 [LintFormat] 🔧 Auto-formatting
2025-09-22 16:07:16 [LanguageDetector] Detection complete. Found: shell json python markdown
2025-09-22 16:07:20 [PythonFormatter] Required tools not available, skipping Python formatting
```

### DEBUG Level (HOOK_LOG_LEVEL=3)

Comprehensive debugging output:
```
2025-09-22 16:06:50 [HookManager] Initializing modular hook system v1.0.0
2025-09-22 16:06:50 [HookManager] Configuration file found
2025-09-22 16:06:50 [LintFormat] 🔧 Auto-formatting
2025-09-22 16:06:50 [ToolManager] Setting up tool paths
2025-09-22 16:06:50 [ToolManager] Tool paths configured
2025-09-22 16:06:50 [FormatterRegistry] Initializing formatter registry
2025-09-22 16:06:50 [FormatterRegistry] Formatter registry initialized
2025-09-22 16:06:50 [LintFormat] Detecting project languages
2025-09-22 16:06:50 [LanguageDetector] Starting language detection
2025-09-22 16:06:51 [LanguageDetector] Detected language: shell
2025-09-22 16:07:05 [LanguageDetector] Detected language: python
2025-09-22 16:07:16 [LanguageDetector] Detection complete. Found: shell json python markdown
2025-09-22 16:07:16 [LintFormat] Detected languages: shell json python markdown
2025-09-22 16:07:16 [LintFormat] Processing language: python
2025-09-22 16:07:16 [FormatterRegistry] Dispatching formatter for language: python
2025-09-22 16:07:19 [PythonFormatter] Starting Python formatting
2025-09-22 16:07:19 [BaseFormatter] Finding files with patterns: *.py
2025-09-22 16:07:20 [BaseFormatter] Checking required tools: black:pipx:black isort:pipx:isort ruff:pipx:ruff
2025-09-22 16:07:20 [BaseFormatter] Tool not found: black
2025-09-22 16:07:20 [BaseFormatter] Tool available: ruff
2025-09-22 16:07:20 [BaseFormatter] Some required tools missing
2025-09-22 16:07:20 [PythonFormatter] Required tools not available, skipping Python formatting
```

## 🧪 Testing Logging

### Test Hook System Initialization

```bash
HOOK_LOG_LEVEL=3 bash -c 'cd ~/.claude/hooks/cai && source lib/HookManager.sh && init_hook_system'
```

### Test Specific Hook

```bash
# Create test file
echo 'print("Hello World")' > test.py

# Test with logging
env HOOK_LOG_LEVEL=3 ~/.claude/hooks/cai/code-quality/lint-format.sh test.py

# Cleanup
rm test.py
```

### Test All Components

```bash
# Test full workflow with logging
mkdir -p /tmp/ai-craft-test
cd /tmp/ai-craft-test
echo 'print("test")' > test.py
echo '{"test": "value"}' > test.json
echo 'console.log("test")' > test.js

env HOOK_LOG_LEVEL=3 ~/.claude/hooks/cai/code-quality/lint-format.sh .

cd -
rm -rf /tmp/ai-craft-test
```

## 🔍 Troubleshooting

### Common Issues

#### **No Log Output**
```bash
# Check environment variable
echo $HOOK_LOG_LEVEL

# Set if missing
export HOOK_LOG_LEVEL=2

# Test with explicit level
env HOOK_LOG_LEVEL=3 ~/.claude/hooks/cai/lib/HookManager.sh
```

#### **Permission Denied**
```bash
# Make hooks executable
chmod +x ~/.claude/hooks/cai/**/*.sh
chmod +x ~/.claude/hooks/cai/**/*.py

# Verify permissions
ls -la ~/.claude/hooks/cai/workflow/
ls -la ~/.claude/hooks/cai/code-quality/
```

#### **Hook Not Found**
```bash
# Verify installation
ls -la ~/.claude/hooks/cai/

# Check expected structure
ls -la ~/.claude/hooks/cai/lib/
ls -la ~/.claude/hooks/cai/workflow/
ls -la ~/.claude/hooks/cai/code-quality/
```

#### **Tool Missing Warnings**

For Python formatting:
```bash
# Install Python formatting tools
pip install black isort ruff
# or
pipx install black
pipx install isort
pipx install ruff
```

For JavaScript/JSON formatting:
```bash
# Install prettier
npm install -g prettier
```

For shell script validation:
```bash
# Install shellcheck
sudo apt install shellcheck  # Ubuntu/Debian
brew install shellcheck      # macOS
```

### Debug Information Collection

#### **Environment Check**
```bash
echo "=== AI-Craft Logging Debug Info ==="
echo "HOOK_LOG_LEVEL: ${HOOK_LOG_LEVEL:-not set}"
echo "Shell: $SHELL"
echo "Path: $PATH"
echo ""
echo "=== Hook Installation ==="
ls -la ~/.claude/hooks/cai/ 2>/dev/null || echo "Hooks not installed"
echo ""
echo "=== Hook Permissions ==="
find ~/.claude/hooks/cai/ -name "*.sh" -exec ls -la {} \; 2>/dev/null | head -5
echo ""
echo "=== Test Hook Loading ==="
bash -c 'cd ~/.claude/hooks/cai 2>/dev/null && source lib/HookManager.sh && echo "HookManager loaded successfully"' 2>&1
```

#### **Full Diagnostic**
```bash
# Save to file for support
{
    echo "=== AI-Craft Logging Diagnostic Report ==="
    echo "Date: $(date)"
    echo "User: $(whoami)"
    echo "System: $(uname -a)"
    echo ""
    echo "=== Environment ==="
    env | grep -E "(HOOK_|PATH|SHELL)" | sort
    echo ""
    echo "=== Installation Check ==="
    ls -la ~/.claude/hooks/cai/ 2>/dev/null || echo "Hooks not installed"
    echo ""
    echo "=== Test Execution ==="
    env HOOK_LOG_LEVEL=3 bash -c 'cd ~/.claude/hooks/cai && source lib/HookManager.sh && init_hook_system' 2>&1
} > ai-craft-debug-$(date +%Y%m%d-%H%M%S).log

echo "Debug report saved to: ai-craft-debug-$(date +%Y%m%d-%H%M%S).log"
```

## 📋 Configuration Checklist

### Initial Setup
- [ ] Set `HOOK_LOG_LEVEL` in shell profile
- [ ] Source shell profile: `source ~/.bashrc`
- [ ] Verify setting: `echo $HOOK_LOG_LEVEL`
- [ ] Test basic logging: `env HOOK_LOG_LEVEL=3 ~/.claude/hooks/cai/lib/HookManager.sh`

### Development Environment
- [ ] Set to INFO level: `export HOOK_LOG_LEVEL=2`
- [ ] Install formatting tools (black, isort, ruff, prettier)
- [ ] Test hook execution with sample files
- [ ] Verify logs appear in stderr

### Production Environment
- [ ] Set to ERROR level: `export HOOK_LOG_LEVEL=0`
- [ ] Verify silent operation
- [ ] Monitor for error logs only
- [ ] Document any recurring issues

### CI/CD Environment
- [ ] Set to WARN level: `export HOOK_LOG_LEVEL=1`
- [ ] Capture logs in build artifacts
- [ ] Set up log analysis for warnings
- [ ] Configure alerts for error patterns

## 📚 Related Documentation

- **Installation Guide**: `README.md` - Hook System Logging Configuration section
- **Hook Architecture**: `.claude/hooks/cai/lib/` - Modular hook system implementation
- **Settings Configuration**: `~/.claude/settings.local.json` - Hook registration and triggers
- **Troubleshooting**: This document - Common issues and solutions

## 🔄 Maintenance

### Regular Checks
- Verify log level is appropriate for environment
- Monitor for new warning patterns
- Update tool installations as needed
- Review and clean old debug logs

### Updates
- When updating AI-Craft, verify logging still works
- Check for new logging components in updates
- Update this documentation with new features
- Test logging after system changes

---

**Remember**: Logging is essential for troubleshooting AI-Craft hook issues. Always enable appropriate logging when investigating problems or developing with the framework.