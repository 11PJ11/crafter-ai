#!/bin/bash
# AI-Craft Framework - Managed File
# Part of Claude Code SuperClaude modular hook system
# BaseFormatter - Base interface for all formatters
# Part of Claude Code SuperClaude modular hook system

set -euo pipefail

# Base formatter interface
# format_file() - Must be implemented by concrete formatters
# Parameters: file_path
# Returns: 0 on success, 1 on failure

format_file() {
    local file_path="$1"
    echo "BaseFormatter: format_file() must be implemented by subclass"
    return 1
}