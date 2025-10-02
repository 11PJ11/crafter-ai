#!/bin/bash
# AI-Craft Framework - Managed File
# Part of Claude Code SuperClaude modular hook system
# FileOperationContext - Context object for coordinated file operations
# Part of Claude Code SuperClaude hook system resilience components

set -euo pipefail

# Source dependencies
source "$(dirname "${BASH_SOURCE[0]}")/ResilienceConfiguration.sh"

# FileOperationContext object
# Encapsulates context and metadata for coordinated file operations
create_file_operation_context() {
    local operation_id="$1"
    local operation_type="$2"
    local target_files="$3"
    local coordination_strategy="${4:-sequential}"
    local lock_timeout="${5:-$FILE_SYSTEM_LOCK_TIMEOUT_SECONDS}"

    # Create context object as structured data
    local context_object
    context_object=$(cat <<EOF
{
    "operation_id": "$operation_id",
    "operation_type": "$operation_type",
    "target_files": "$target_files",
    "coordination_strategy": "$coordination_strategy",
    "lock_timeout": $lock_timeout,
    "created_at": $(date +%s),
    "status": "created",
    "state_dir": "$FILE_SYSTEM_COORDINATOR_STATE_DIR",
    "log_file": "$FILE_SYSTEM_COORDINATOR_LOG_FILE"
}
EOF
    )

    echo "$context_object"
}

# Extract operation ID from context
get_context_operation_id() {
    local context="$1"
    echo "$context" | grep -o '"operation_id": "[^"]*"' | cut -d'"' -f4
}

# Extract operation type from context
get_context_operation_type() {
    local context="$1"
    echo "$context" | grep -o '"operation_type": "[^"]*"' | cut -d'"' -f4
}

# Extract target files from context
get_context_target_files() {
    local context="$1"
    echo "$context" | grep -o '"target_files": "[^"]*"' | cut -d'"' -f4
}

# Extract coordination strategy from context
get_context_coordination_strategy() {
    local context="$1"
    echo "$context" | grep -o '"coordination_strategy": "[^"]*"' | cut -d'"' -f4
}

# Extract lock timeout from context
get_context_lock_timeout() {
    local context="$1"
    echo "$context" | grep -o '"lock_timeout": [0-9]*' | cut -d':' -f2 | tr -d ' '
}

# Extract status from context
get_context_status() {
    local context="$1"
    echo "$context" | grep -o '"status": "[^"]*"' | cut -d'"' -f4
}

# Extract creation timestamp from context
get_context_created_at() {
    local context="$1"
    echo "$context" | grep -o '"created_at": [0-9]*' | cut -d':' -f2 | tr -d ' '
}

# Extract state directory from context
get_context_state_dir() {
    local context="$1"
    echo "$context" | grep -o '"state_dir": "[^"]*"' | cut -d'"' -f4
}

# Extract log file from context
get_context_log_file() {
    local context="$1"
    echo "$context" | grep -o '"log_file": "[^"]*"' | cut -d'"' -f4
}

# Update context status
update_context_status() {
    local context="$1"
    local new_status="$2"

    # Replace status in context object
    echo "$context" | sed "s/\"status\": \"[^\"]*\"/\"status\": \"$new_status\"/"
}

# Validate file operation context
validate_file_operation_context() {
    local context="$1"

    local operation_id
    local operation_type
    local lock_timeout

    operation_id=$(get_context_operation_id "$context")
    operation_type=$(get_context_operation_type "$context")
    lock_timeout=$(get_context_lock_timeout "$context")

    # Validation rules
    if [[ -z "$operation_id" ]]; then
        echo "Error: Operation ID cannot be empty" >&2
        return 1
    fi

    if [[ -z "$operation_type" ]]; then
        echo "Error: Operation type cannot be empty" >&2
        return 1
    fi

    if [[ $lock_timeout -lt 1 ]]; then
        echo "Error: Lock timeout must be at least 1 second" >&2
        return 1
    fi

    # Validate coordination strategy
    local coordination_strategy
    coordination_strategy=$(get_context_coordination_strategy "$context")
    case "$coordination_strategy" in
        "sequential"|"parallel"|"batch")
            # Valid coordination strategies
            ;;
        *)
            echo "Warning: Unknown coordination strategy: $coordination_strategy" >&2
            ;;
    esac

    return 0
}

# Create batch operation context
create_batch_operation_context() {
    local operation_id="$1"
    local target_files="$2"
    local lock_timeout="${3:-$FILE_SYSTEM_LOCK_TIMEOUT_SECONDS}"

    create_file_operation_context "$operation_id" "batch" "$target_files" "batch" "$lock_timeout"
}

# Create single file operation context
create_single_file_operation_context() {
    local operation_id="$1"
    local target_file="$2"
    local operation_type="$3"
    local lock_timeout="${4:-$FILE_SYSTEM_LOCK_TIMEOUT_SECONDS}"

    create_file_operation_context "$operation_id" "$operation_type" "$target_file" "sequential" "$lock_timeout"
}