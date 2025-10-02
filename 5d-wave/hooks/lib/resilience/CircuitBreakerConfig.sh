#!/bin/bash
# AI-Craft Framework - Managed File
# Part of Claude Code SuperClaude modular hook system
# CircuitBreakerConfig - Parameter object for circuit breaker configuration
# Part of Claude Code SuperClaude hook system resilience components

set -euo pipefail

# Source dependencies for configuration values
source "$(dirname "${BASH_SOURCE[0]}")/ResilienceConfiguration.sh"

# Initialize configuration if not already done
if [[ -z "${CIRCUIT_BREAKER_STATE_DIR:-}" ]]; then
    readonly CIRCUIT_BREAKER_STATE_DIR="$RESILIENCE_STATE_BASE_DIR"
    readonly CIRCUIT_BREAKER_LOG_FILE=$(get_resilience_log_path "$CIRCUIT_BREAKER_LOG_FILENAME")
fi

# CircuitBreakerConfig parameter object
# Encapsulates all configuration parameters for a circuit breaker instance
create_circuit_breaker_config() {
    local tool_name="$1"
    local timeout_seconds="${2:-$CIRCUIT_BREAKER_TIMEOUT_SECONDS}"
    local failure_threshold="${3:-$CIRCUIT_BREAKER_FAILURE_THRESHOLD}"
    local success_threshold="${4:-$CIRCUIT_BREAKER_SUCCESS_THRESHOLD}"

    # Create configuration object as associative array representation
    local config_object
    config_object=$(cat <<EOF
{
    "tool_name": "$tool_name",
    "timeout_seconds": $timeout_seconds,
    "failure_threshold": $failure_threshold,
    "success_threshold": $success_threshold,
    "state_dir": "$CIRCUIT_BREAKER_STATE_DIR",
    "log_file": "$CIRCUIT_BREAKER_LOG_FILE"
}
EOF
    )

    echo "$config_object"
}

# Extract tool name from config object
get_config_tool_name() {
    local config="$1"
    echo "$config" | grep -o '"tool_name": "[^"]*"' | cut -d'"' -f4
}

# Extract timeout seconds from config object
get_config_timeout_seconds() {
    local config="$1"
    echo "$config" | grep -o '"timeout_seconds": [0-9]*' | cut -d':' -f2 | tr -d ' '
}

# Extract failure threshold from config object
get_config_failure_threshold() {
    local config="$1"
    echo "$config" | grep -o '"failure_threshold": [0-9]*' | cut -d':' -f2 | tr -d ' '
}

# Extract success threshold from config object
get_config_success_threshold() {
    local config="$1"
    echo "$config" | grep -o '"success_threshold": [0-9]*' | cut -d':' -f2 | tr -d ' '
}

# Extract state directory from config object
get_config_state_dir() {
    local config="$1"
    echo "$config" | grep -o '"state_dir": "[^"]*"' | cut -d'"' -f4
}

# Extract log file from config object
get_config_log_file() {
    local config="$1"
    echo "$config" | grep -o '"log_file": "[^"]*"' | cut -d'"' -f4
}

# Validate circuit breaker configuration
validate_circuit_breaker_config() {
    local config="$1"

    local tool_name
    local timeout_seconds
    local failure_threshold
    local success_threshold

    tool_name=$(get_config_tool_name "$config")
    timeout_seconds=$(get_config_timeout_seconds "$config")
    failure_threshold=$(get_config_failure_threshold "$config")
    success_threshold=$(get_config_success_threshold "$config")

    # Validation rules
    if [[ -z "$tool_name" ]]; then
        echo "Error: Tool name cannot be empty" >&2
        return 1
    fi

    if [[ $timeout_seconds -lt 60 ]]; then
        echo "Warning: Timeout less than 60 seconds may cause frequent resets" >&2
    fi

    if [[ $failure_threshold -lt 1 ]]; then
        echo "Error: Failure threshold must be at least 1" >&2
        return 1
    fi

    if [[ $success_threshold -lt 1 ]]; then
        echo "Error: Success threshold must be at least 1" >&2
        return 1
    fi

    return 0
}

# Create default circuit breaker configuration
create_default_circuit_breaker_config() {
    local tool_name="$1"
    create_circuit_breaker_config "$tool_name"
}