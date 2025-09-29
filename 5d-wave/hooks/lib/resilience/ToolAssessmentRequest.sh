#!/bin/bash
# ToolAssessmentRequest - Value object for tool assessment operations
# Part of Claude Code SuperClaude hook system resilience components

set -euo pipefail

# ToolAssessmentRequest value object
# Encapsulates all parameters needed for tool assessment operations
create_tool_assessment_request() {
    local tool_name="$1"
    local operation_type="$2"
    local target_files="${3:-}"
    local timeout_seconds="${4:-30}"
    local retry_attempts="${5:-1}"

    # Create request object as structured data
    local request_object
    request_object=$(cat <<EOF
{
    "tool_name": "$tool_name",
    "operation_type": "$operation_type",
    "target_files": "$target_files",
    "timeout_seconds": $timeout_seconds,
    "retry_attempts": $retry_attempts,
    "created_at": $(date +%s),
    "request_id": "req_$(date +%s)_$$"
}
EOF
    )

    echo "$request_object"
}

# Extract tool name from assessment request
get_request_tool_name() {
    local request="$1"
    echo "$request" | grep -o '"tool_name": "[^"]*"' | cut -d'"' -f4
}

# Extract operation type from assessment request
get_request_operation_type() {
    local request="$1"
    echo "$request" | grep -o '"operation_type": "[^"]*"' | cut -d'"' -f4
}

# Extract target files from assessment request
get_request_target_files() {
    local request="$1"
    echo "$request" | grep -o '"target_files": "[^"]*"' | cut -d'"' -f4
}

# Extract timeout seconds from assessment request
get_request_timeout_seconds() {
    local request="$1"
    echo "$request" | grep -o '"timeout_seconds": [0-9]*' | cut -d':' -f2 | tr -d ' '
}

# Extract retry attempts from assessment request
get_request_retry_attempts() {
    local request="$1"
    echo "$request" | grep -o '"retry_attempts": [0-9]*' | cut -d':' -f2 | tr -d ' '
}

# Extract request ID from assessment request
get_request_id() {
    local request="$1"
    echo "$request" | grep -o '"request_id": "[^"]*"' | cut -d'"' -f4
}

# Extract creation timestamp from assessment request
get_request_created_at() {
    local request="$1"
    echo "$request" | grep -o '"created_at": [0-9]*' | cut -d':' -f2 | tr -d ' '
}

# Validate tool assessment request
validate_tool_assessment_request() {
    local request="$1"

    local tool_name
    local operation_type
    local timeout_seconds
    local retry_attempts

    tool_name=$(get_request_tool_name "$request")
    operation_type=$(get_request_operation_type "$request")
    timeout_seconds=$(get_request_timeout_seconds "$request")
    retry_attempts=$(get_request_retry_attempts "$request")

    # Validation rules
    if [[ -z "$tool_name" ]]; then
        echo "Error: Tool name cannot be empty" >&2
        return 1
    fi

    if [[ -z "$operation_type" ]]; then
        echo "Error: Operation type cannot be empty" >&2
        return 1
    fi

    if [[ $timeout_seconds -lt 1 ]]; then
        echo "Error: Timeout must be at least 1 second" >&2
        return 1
    fi

    if [[ $retry_attempts -lt 0 ]]; then
        echo "Error: Retry attempts cannot be negative" >&2
        return 1
    fi

    # Validate operation type
    case "$operation_type" in
        "format"|"lint"|"check"|"test"|"build")
            # Valid operation types
            ;;
        *)
            echo "Warning: Unknown operation type: $operation_type" >&2
            ;;
    esac

    return 0
}

# Create formatting assessment request
create_format_assessment_request() {
    local tool_name="$1"
    local target_files="$2"
    local timeout_seconds="${3:-30}"

    create_tool_assessment_request "$tool_name" "format" "$target_files" "$timeout_seconds" 1
}

# Create health check assessment request
create_health_check_assessment_request() {
    local tool_name="$1"
    local timeout_seconds="${2:-10}"

    create_tool_assessment_request "$tool_name" "check" "" "$timeout_seconds" 0
}