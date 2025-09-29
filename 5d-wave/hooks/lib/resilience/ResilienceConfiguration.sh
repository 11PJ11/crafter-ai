#!/bin/bash
# ResilienceConfiguration - Business configuration constants for resilience system
# Part of Claude Code SuperClaude hook system resilience components

set -euo pipefail

# Resilience configuration constants - use include guard to prevent redefinition
if [[ -z "${RESILIENCE_STATE_BASE_DIR:-}" ]]; then
    # Resilience system base directories
    readonly RESILIENCE_STATE_BASE_DIR="/tmp/claude"

    # Circuit Breaker Business Configuration
    readonly CIRCUIT_BREAKER_TIMEOUT_SECONDS=300          # 5 minutes - Time before attempting reset
    readonly CIRCUIT_BREAKER_FAILURE_THRESHOLD=3          # Number of failures before opening circuit
    readonly CIRCUIT_BREAKER_SUCCESS_THRESHOLD=2          # Number of successes needed to close circuit
    readonly CIRCUIT_BREAKER_LOG_FILENAME="circuit-breaker.log"

    # Tool Capability Service Configuration
    readonly TOOL_CAPABILITY_CACHE_TTL_SECONDS=900        # 15 minutes - Cache validity period
    readonly TOOL_HEALTH_CHECK_TIMEOUT_SECONDS=30         # Maximum time for tool health check

    # File System Coordinator Configuration
    readonly FILE_SYSTEM_LOCK_TIMEOUT_SECONDS=30          # Maximum time to wait for file lock
    readonly FILE_SYSTEM_OPERATION_QUEUE_SIZE=100         # Maximum operations in queue
    readonly FILE_SYSTEM_COORDINATOR_LOG_FILENAME="fs-coordinator.log"
    readonly STALE_LOCK_CLEANUP_SECONDS=600               # 10 minutes - When to clean stale locks

    # Operation Queue Manager Configuration
    readonly OPERATION_QUEUE_MAX_SIZE=1000                # Maximum operations in system queue
    readonly OPERATION_QUEUE_MAX_CONCURRENT=3             # Maximum concurrent operations
    readonly OPERATION_QUEUE_LOG_FILENAME="operation-queue.log"

    # Resilient Hook Manager Configuration
    readonly RESILIENCE_SUCCESS_RATE_TARGET=95            # Target success rate percentage
    readonly RESILIENCE_MANAGER_LOG_FILENAME="resilient-manager.log"

    # Timeout and retry configuration
    readonly DEFAULT_TOOL_OPERATION_TIMEOUT_SECONDS=60    # Default tool operation timeout
    readonly FILE_OPERATION_RETRY_ATTEMPTS=3              # Number of retry attempts for file operations
fi

# Initialize resilience configuration
init_resilience_configuration() {
    # Ensure state directories exist
    mkdir -p "$RESILIENCE_STATE_BASE_DIR"

    # Set proper permissions for resilience state directory
    chmod 755 "$RESILIENCE_STATE_BASE_DIR" 2>/dev/null || true
}

# Get configuration-based file paths
get_resilience_log_path() {
    local log_filename="$1"
    echo "$RESILIENCE_STATE_BASE_DIR/$log_filename"
}

# Configuration validation
validate_resilience_configuration() {
    # Validate numeric configuration values
    local config_errors=0

    if [[ $CIRCUIT_BREAKER_TIMEOUT_SECONDS -lt 60 ]]; then
        echo "Warning: Circuit breaker timeout is less than 60 seconds" >&2
        config_errors=$((config_errors + 1))
    fi

    if [[ $TOOL_CAPABILITY_CACHE_TTL_SECONDS -lt 300 ]]; then
        echo "Warning: Tool capability cache TTL is less than 5 minutes" >&2
        config_errors=$((config_errors + 1))
    fi

    if [[ $RESILIENCE_SUCCESS_RATE_TARGET -lt 80 || $RESILIENCE_SUCCESS_RATE_TARGET -gt 100 ]]; then
        echo "Warning: Success rate target should be between 80-100%" >&2
        config_errors=$((config_errors + 1))
    fi

    return $config_errors
}

# Export configuration for use in other modules
export RESILIENCE_STATE_BASE_DIR
export CIRCUIT_BREAKER_TIMEOUT_SECONDS
export CIRCUIT_BREAKER_FAILURE_THRESHOLD
export CIRCUIT_BREAKER_SUCCESS_THRESHOLD
export TOOL_CAPABILITY_CACHE_TTL_SECONDS
export FILE_SYSTEM_LOCK_TIMEOUT_SECONDS
export OPERATION_QUEUE_MAX_SIZE
export RESILIENCE_SUCCESS_RATE_TARGET

# Initialize configuration on source
init_resilience_configuration