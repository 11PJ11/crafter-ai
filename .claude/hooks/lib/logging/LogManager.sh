#!/bin/bash
# LogManager - Unified Logging Framework
# Part of Claude Code SuperClaude modular hook system

set -euo pipefail

# Log level constants (only define if not already defined)
if [ -z "${LOG_LEVEL_ERROR:-}" ]; then
    readonly LOG_LEVEL_ERROR=0
    readonly LOG_LEVEL_WARN=1
    readonly LOG_LEVEL_INFO=2
    readonly LOG_LEVEL_DEBUG=3
fi

# Default log level - ERROR only for production use (can be overridden)
LOG_LEVEL=${HOOK_LOG_LEVEL:-$LOG_LEVEL_ERROR}

# Unified logging function
hook_log() {
    local level="$1"
    local component="$2"
    local message="$3"

    if [ "$level" -le "$LOG_LEVEL" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') [$component] $message" >&2
    fi
}