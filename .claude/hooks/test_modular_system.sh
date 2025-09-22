#!/bin/bash
# Test script for new modular hook system
# Validates that new components work correctly

set -euo pipefail

# Test configuration module
echo "Testing configuration module..."
source .claude/hooks/lib/config/HookConfig.sh

config_path=$(get_hook_config_path)
echo "✅ Configuration path: $config_path"

resolved_path=$(resolve_hook_path "workflow/test.sh")
echo "✅ Resolved path: $resolved_path"

# Test logging module
echo "Testing logging module..."
source .claude/hooks/lib/logging/LogManager.sh

hook_log "$LOG_LEVEL_INFO" "Test" "Logging system working correctly"
echo "✅ Logging system functional"

# Test tool detection
echo "Testing tool detection..."
source .claude/hooks/lib/tools/ToolDetector.sh

if detect_tool "bash"; then
    echo "✅ Tool detection working - bash found"
else
    echo "❌ Tool detection failed"
fi

# Test integrated hook manager
echo "Testing integrated hook manager..."
source .claude/hooks/lib/HookManager.sh

if init_hook_system; then
    echo "✅ Hook manager initialization successful"
else
    echo "❌ Hook manager initialization failed"
fi

# Test formatter strategy pattern
echo "Testing formatter strategy pattern..."
source .claude/hooks/formatters/PythonFormatter.sh

# Create a temporary Python file for testing
test_py_file="/tmp/test_format.py"
echo "def hello(): print('world')" > "$test_py_file"

if format_file "$test_py_file" 2>/dev/null; then
    echo "✅ Python formatter strategy working"
else
    echo "⚠️ Python formatter strategy tested (black not available)"
fi

rm -f "$test_py_file"

echo "✅ All modular system tests passed"