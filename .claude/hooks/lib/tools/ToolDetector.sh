#!/bin/bash
# ToolDetector - Tool Detection Interface
# Part of Claude Code SuperClaude modular hook system

set -euo pipefail

# Source dependencies
source "$(dirname "${BASH_SOURCE[0]}")/../logging/LogManager.sh"

# Tool detection interface
detect_tool() {
    local tool_name="$1"
    if command -v "$tool_name" >/dev/null 2>&1; then
        hook_log "$LOG_LEVEL_DEBUG" "ToolDetector" "Tool '$tool_name' found"
        return 0
    else
        hook_log "$LOG_LEVEL_DEBUG" "ToolDetector" "Tool '$tool_name' not found"
        return 1
    fi
}