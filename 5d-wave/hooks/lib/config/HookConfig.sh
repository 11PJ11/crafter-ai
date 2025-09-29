#!/bin/bash
# HookConfig - Centralized Configuration Management
# Part of Claude Code SuperClaude modular hook system

set -euo pipefail

# Core configuration constants (only define if not already defined)
if [ -z "${HOOK_CONFIG_VERSION:-}" ]; then
    readonly HOOK_CONFIG_VERSION="1.0.0"
    readonly HOOK_BASE_DIR="${HOME}/.claude/hooks"
    readonly HOOK_CONFIG_FILE="${HOOK_BASE_DIR}/config/hooks-config.json"
    readonly HOOK_STATE_DIR="${HOME}/state/craft-ai"
    readonly HOOK_DOCS_DIR="${HOME}/docs/craft-ai"
fi

# Get hook configuration file path
get_hook_config_path() {
    echo "${HOOK_CONFIG_FILE}"
}

# Resolve hook script path
resolve_hook_path() {
    local hook_path="$1"
    echo "${HOOK_BASE_DIR}/${hook_path}"
}