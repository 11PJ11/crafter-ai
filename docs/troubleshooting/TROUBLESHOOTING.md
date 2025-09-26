# AI-Craft Framework Troubleshooting Guide

## 🚨 Quick Diagnostic

If you're experiencing issues with AI-Craft, run this quick diagnostic first:

```bash
# Quick system check
echo "=== AI-Craft Quick Diagnostic ==="
echo "Installation: $(ls ~/.claude/agents/cai/ 2>/dev/null && echo 'OK' || echo 'MISSING')"
echo "Hooks: $(ls ~/.claude/hooks/cai/ 2>/dev/null && echo 'OK' || echo 'MISSING')"
echo "Logging: HOOK_LOG_LEVEL=${HOOK_LOG_LEVEL:-not set}"
echo "Commands: $(ls ~/.claude/commands/cai/ 2>/dev/null | wc -l) found"
echo "Permissions: $(find ~/.claude/hooks/cai/ -name "*.sh" -executable 2>/dev/null | wc -l) executable hooks"
```

## 🔧 Installation Issues

### Framework Not Found

**Symptoms**:

- Commands like `cai:start` not recognized
- No agents directory found
- Missing framework files

**Solutions**:

```bash
# Check installation
ls ~/.claude/agents/cai/ ~/.claude/commands/cai/ ~/.claude/hooks/cai/

# If missing, reinstall
./install-ai-craft.sh

# If install fails, check source
ls .claude/agents/cai/constants.md
```

### Installation Fails

**Common Causes**:

1. **Missing source files**
2. **Permission issues**
3. **Python not available for settings merge**

**Debug Steps**:

```bash
# Check source framework
ls .claude/agents/cai/constants.md

# Check permissions
ls -la ~/.claude/

# Test with backup
./install-ai-craft.sh --backup-only

# Check Python availability
python3 --version
```

### Partial Installation

**Symptoms**:

- Some components missing
- Validation errors during install
- Incomplete functionality

**Solutions**:

```bash
# Uninstall and reinstall
./uninstall-ai-craft.sh --backup --force
./install-ai-craft.sh

# Check validation logs
cat ~/.claude/ai-craft-install.log
```

## 🔗 Hook System Issues

### Hooks Not Executing

**Symptoms**:

- No automatic formatting
- Workflow hooks not triggering
- Silent operation with no feedback

**Diagnostic Steps**:

```bash
# Check hook registration
grep -A 10 "cai-" ~/.claude/settings.local.json

# Check hook permissions
ls -la ~/.claude/hooks/cai/workflow/
ls -la ~/.claude/hooks/cai/code-quality/

# Test hook manually
env HOOK_LOG_LEVEL=3 ~/.claude/hooks/cai/code-quality/lint-format.sh test.py
```

**Solutions**:

```bash
# Fix permissions
chmod +x ~/.claude/hooks/cai/**/*.sh
chmod +x ~/.claude/hooks/cai/**/*.py

# Re-register hooks
./install-ai-craft.sh  # Will re-merge hook settings

# Enable logging for debugging
export HOOK_LOG_LEVEL=3
```

### Hook Errors

**Symptoms**:

- Error messages during hook execution
- Hooks exit with non-zero status
- Partial functionality

**Common Errors and Solutions**:

#### "Tool not found" Errors

```bash
# Install Python tools
pip install black isort ruff
# or with pipx
pipx install black
pipx install isort
pipx install ruff

# Install JavaScript tools
npm install -g prettier eslint

# Install shell tools
sudo apt install shellcheck  # Ubuntu/Debian
brew install shellcheck      # macOS
```

#### "Permission denied" Errors

```bash
# Fix hook permissions
find ~/.claude/hooks/cai/ -name "*.sh" -exec chmod +x {} \;
find ~/.claude/hooks/cai/ -name "*.py" -exec chmod +x {} \;

# Check file ownership
ls -la ~/.claude/hooks/cai/
```

#### "Configuration file not found" Errors

```bash
# Check hook configuration
ls ~/.claude/hooks/cai/lib/config/

# Reinstall if missing
./install-ai-craft.sh
```

### Logging Issues

**No Log Output**:

```bash
# Set logging level
export HOOK_LOG_LEVEL=2

# Test with explicit level
env HOOK_LOG_LEVEL=3 ~/.claude/hooks/cai/lib/HookManager.sh

# Add to shell profile
echo 'export HOOK_LOG_LEVEL=2' >> ~/.bashrc
source ~/.bashrc
```

**Too Verbose Logging**:

```bash
# Reduce to INFO level
export HOOK_LOG_LEVEL=2

# Or disable
export HOOK_LOG_LEVEL=0
```

## 🎯 Command Issues

### CAI Commands Not Found

**Symptoms**:

- `cai:start` command not recognized
- Commands not available in Claude Code
- Command completion not working

**Solutions**:

```bash
# Check command installation
ls ~/.claude/commands/cai/

# Expected commands
cat ~/.claude/commands/cai/help.md

# Reinstall commands
./install-ai-craft.sh
```

### Command Execution Errors

**Debug Steps**:

```bash
# Check command files
ls -la ~/.claude/commands/cai/

# Check permissions
find ~/.claude/commands/cai/ -name "*.md" -ls

# Verify command structure
head -20 ~/.claude/commands/cai/help.md
```

## 🤖 Agent Issues

### Agents Not Responding

**Symptoms**:

- Agent selection not working
- No agent-specific behavior
- Generic responses only

**Solutions**:

```bash
# Check agent installation
ls ~/.claude/agents/cai/

# Check agent categories
ls ~/.claude/agents/cai/coordination/
ls ~/.claude/agents/cai/quality-validation/

# Verify constants file
head -20 ~/.claude/agents/cai/constants.md
```

### Agent Context Issues

**Debug Steps**:

```bash
# Check agent specifications
ls ~/.claude/agents/cai/coordination/
cat ~/.claude/agents/cai/coordination/atdd-cycle-coordinator.md | head -20

# Verify agent organization
find ~/.claude/agents/cai/ -name "*.md" | grep -v README | wc -l
```

## 🔍 Performance Issues

### Slow Hook Execution

**Symptoms**:

- Long delays during file operations
- Timeouts during formatting
- Slow startup times

**Diagnostic**:

```bash
# Time hook execution
time env HOOK_LOG_LEVEL=3 ~/.claude/hooks/cai/code-quality/lint-format.sh test.py

# Check for tool availability
which black isort ruff prettier shellcheck
```

**Optimizations**:

```bash
# Install tools with pipx for better performance
pipx install black
pipx install isort
pipx install ruff

# Use local tool installations
npm install --save-dev prettier eslint
```

### Memory Issues

**Symptoms**:

- Out of memory errors
- System slowdown during hook execution
- Large log files

**Solutions**:

```bash
# Reduce logging level
export HOOK_LOG_LEVEL=1

# Clean up old logs
find ~/.claude/ -name "*.log" -mtime +7 -delete

# Monitor memory usage
ps aux | grep -E "(black|isort|ruff|prettier)"
```

## 🌐 Environment Issues

### WSL/Linux Issues

**Common Problems**:

- Path issues between Windows and WSL
- Permission mismatches
- Tool installation conflicts

**Solutions**:

```bash
# Check environment
echo $PATH
which python3 pip3

# Fix WSL permissions
sudo chmod -R 755 ~/.claude/hooks/cai/

# Install tools in WSL
pip3 install --user black isort ruff
```

### macOS Issues

**Common Problems**:

- Homebrew tool conflicts
- Python version issues
- Permission restrictions

**Solutions**:

```bash
# Use Homebrew for tools
brew install black isort ruff

# Check Python version
python3 --version
which python3

# Fix permissions
chmod +x ~/.claude/hooks/cai/**/*.sh
```

### Windows Issues

**Note**: Windows BAT/PS1 files have been removed. Use WSL for Windows environments.

**Setup WSL**:

```bash
# Enable WSL in Windows
wsl --install

# Install AI-Craft in WSL
cd /mnt/c/path/to/ai-craft
./install-ai-craft.sh
```

## 📊 Comprehensive Diagnostics

### Full System Check

```bash
#!/bin/bash
echo "=== AI-Craft Comprehensive Diagnostic ==="
echo "Date: $(date)"
echo "User: $(whoami)"
echo "System: $(uname -a)"
echo ""

echo "=== Environment ==="
echo "HOOK_LOG_LEVEL: ${HOOK_LOG_LEVEL:-not set}"
echo "CAI_WORKFLOW_ACTIVE: ${CAI_WORKFLOW_ACTIVE:-not set}"
echo "PATH: $PATH"
echo "Shell: $SHELL"
echo ""

echo "=== Installation Check ==="
echo "Agents: $(ls ~/.claude/agents/cai/ 2>/dev/null | wc -l) categories"
echo "Commands: $(ls ~/.claude/commands/cai/ 2>/dev/null | wc -l) commands"
echo "Hooks: $(find ~/.claude/hooks/cai/ -name "*.sh" 2>/dev/null | wc -l) shell scripts"
echo "Manual files: $(ls ~/.claude/manuals/cai/ 2>/dev/null | wc -l) manuals"
echo ""

echo "=== Hook Permissions ==="
find ~/.claude/hooks/cai/ -name "*.sh" -not -executable 2>/dev/null | head -5
echo ""

echo "=== Tool Availability ==="
for tool in python3 pip3 black isort ruff prettier eslint shellcheck; do
    if command -v "$tool" >/dev/null 2>&1; then
        echo "$tool: $(which $tool)"
    else
        echo "$tool: NOT FOUND"
    fi
done
echo ""

echo "=== Hook Test ==="
env HOOK_LOG_LEVEL=3 bash -c 'cd ~/.claude/hooks/cai 2>/dev/null && source lib/HookManager.sh && init_hook_system' 2>&1 | head -3
echo ""

echo "=== Settings Check ==="
if grep -q "cai-" ~/.claude/settings.local.json 2>/dev/null; then
    echo "CAI hooks registered: YES"
    grep -c "cai-" ~/.claude/settings.local.json
else
    echo "CAI hooks registered: NO"
fi
echo ""

echo "=== Recent Logs ==="
tail -5 ~/.claude/ai-craft-install.log 2>/dev/null || echo "No install log found"
```

### Log Collection

```bash
# Collect comprehensive logs for support
{
    echo "=== AI-Craft Support Information ==="
    echo "Generated: $(date)"
    echo "Version: $(head -5 ~/.claude/ai-craft-manifest.txt 2>/dev/null)"
    echo ""

    # Run full diagnostic
    bash comprehensive_diagnostic.sh

    echo ""
    echo "=== Recent Error Logs ==="
    find ~/.claude/ -name "*.log" -mtime -1 -exec echo "=== {} ===" \; -exec tail -10 {} \; 2>/dev/null

} > ai-craft-support-$(date +%Y%m%d-%H%M%S).log

echo "Support information collected in: ai-craft-support-$(date +%Y%m%d-%H%M%S).log"
```

## 🆘 Getting Help

### Before Reporting Issues

1. **Run Quick Diagnostic**: Use the quick diagnostic at the top of this document
2. **Check Logs**: Enable logging with `HOOK_LOG_LEVEL=3` and reproduce the issue
3. **Try Reinstallation**: Often fixes configuration issues
4. **Check Documentation**: Review `README.md`, `LOGGING_CONFIGURATION.md`, and `HOOK_SYSTEM.md`

### Reporting Issues

Include this information:

1. **Output of quick diagnostic**
2. **Complete error messages with logging enabled**
3. **Steps to reproduce the issue**
4. **Your environment details (OS, shell, Python version)**
5. **Recent changes to your system**

### Support Resources

- **Documentation**: `README.md`, `LOGGING_CONFIGURATION.md`, `HOOK_SYSTEM.md`
- **GitHub Issues**: [https://github.com/11PJ11/crafter-ai/issues](https://github.com/11PJ11/crafter-ai/issues)
- **Installation Logs**: `~/.claude/ai-craft-install.log`
- **Backup Recovery**: `./install-ai-craft.sh --restore`

## 🔄 Recovery Procedures

### Complete Reset

If all else fails, perform a complete reset:

```bash
# 1. Backup current state
./uninstall-ai-craft.sh --backup

# 2. Clean installation
./install-ai-craft.sh

# 3. Configure logging
echo 'export HOOK_LOG_LEVEL=2' >> ~/.bashrc
source ~/.bashrc

# 4. Test functionality
env HOOK_LOG_LEVEL=3 ~/.claude/hooks/cai/code-quality/lint-format.sh test.py
```

### Restore from Backup

```bash
# List available backups
ls ~/.claude/backups/

# Restore from backup
./install-ai-craft.sh --restore

# Or manually restore specific backup
# cp -r ~/.claude/backups/ai-craft-YYYYMMDD-HHMMSS/* ~/.claude/
```

---

**Remember**: Most issues can be resolved by enabling logging (`HOOK_LOG_LEVEL=3`) to see detailed error messages, followed by reinstallation if needed.
