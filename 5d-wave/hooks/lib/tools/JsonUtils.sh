#!/bin/bash
# AI-Craft Framework - Managed File
# Part of Claude Code SuperClaude modular hook system
# JsonUtils - JSON parsing utilities module
# Part of Claude Code SuperClaude modular hook system

set -euo pipefail

# Source dependencies
HOOK_LIB_DIR="$(dirname "${BASH_SOURCE[0]}")/.."
source "${HOOK_LIB_DIR}/config/HookConfig.sh"
source "${HOOK_LIB_DIR}/logging/LogManager.sh"

# JSON parsing with intelligent fallback
parse_json() {
    local json_input="$1"
    local key="$2"

    hook_log "$LOG_LEVEL_DEBUG" "JsonUtils" "Parsing JSON key: $key"

    # Try jq first if available
    if command -v jq >/dev/null 2>&1; then
        echo "$json_input" | jq -r ".$key // empty"
        return $?
    fi

    # Try Python as fallback
    if command -v python3 >/dev/null 2>&1; then
        echo "$json_input" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    keys = '$key'.split('.')
    value = data
    for k in keys:
        value = value.get(k, {})
    print(value if value != {} else '')
except:
    pass
"
        return $?
    elif command -v python >/dev/null 2>&1; then
        echo "$json_input" | python -c "
import json, sys
try:
    data = json.load(sys.stdin)
    keys = '$key'.split('.')
    value = data
    for k in keys:
        value = value.get(k, {})
    print(value if value != {} else '')
except:
    pass
"
        return $?
    fi

    # Simple bash fallback for basic keys
    if [[ "$key" =~ ^[a-zA-Z_][a-zA-Z0-9_]*$ ]]; then
        echo "$json_input" | grep -o "\"$key\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" | cut -d'"' -f4
    else
        hook_log "$LOG_LEVEL_WARN" "JsonUtils" "Complex key '$key' requires jq or python"
        return 1
    fi
}

# Check if JSON file exists and is valid
validate_json_file() {
    local file_path="$1"

    if [[ ! -f "$file_path" ]]; then
        hook_log "$LOG_LEVEL_DEBUG" "JsonUtils" "JSON file not found: $file_path"
        return 1
    fi

    if command -v jq >/dev/null 2>&1; then
        if jq empty "$file_path" >/dev/null 2>&1; then
            hook_log "$LOG_LEVEL_DEBUG" "JsonUtils" "Valid JSON file: $file_path"
            return 0
        else
            hook_log "$LOG_LEVEL_WARN" "JsonUtils" "Invalid JSON file: $file_path"
            return 1
        fi
    else
        # Basic validation without jq
        if [[ -s "$file_path" ]] && head -1 "$file_path" | grep -q '^[[:space:]]*{'; then
            hook_log "$LOG_LEVEL_DEBUG" "JsonUtils" "JSON file appears valid: $file_path"
            return 0
        else
            hook_log "$LOG_LEVEL_WARN" "JsonUtils" "JSON file may be invalid: $file_path"
            return 1
        fi
    fi
}

# Parse JSON from file
parse_json_file() {
    local file_path="$1"
    local key="$2"

    if ! validate_json_file "$file_path"; then
        return 1
    fi

    local json_content
    json_content="$(cat "$file_path")" || return 1
    parse_json "$json_content" "$key"
}