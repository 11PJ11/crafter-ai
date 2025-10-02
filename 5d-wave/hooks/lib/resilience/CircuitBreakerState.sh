#!/bin/bash
# AI-Craft Framework - Managed File
# Part of Claude Code SuperClaude modular hook system
# CircuitBreakerState - Specialized state management for circuit breaker pattern
# Part of Claude Code SuperClaude hook system resilience components

set -euo pipefail

# Source dependencies
HOOK_LIB_DIR="$(dirname "${BASH_SOURCE[0]}")/.."
source "${HOOK_LIB_DIR}/logging/LogManager.sh"
source "$(dirname "${BASH_SOURCE[0]}")/ResilienceConfiguration.sh"

# Circuit breaker state management interface
# Provides specialized operations for managing circuit breaker state files

# Get circuit breaker state for a tool
get_circuit_breaker_state() {
    local tool_name="$1"
    local state_file="$CIRCUIT_BREAKER_STATE_DIR/cb_${tool_name}.state"

    if [[ -f "$state_file" ]]; then
        cat "$state_file"
    else
        echo "$CIRCUIT_BREAKER_STATE_CLOSED"
    fi
}

# Set circuit breaker state for a tool
set_circuit_breaker_state() {
    local tool_name="$1"
    local state="$2"
    local state_file="$CIRCUIT_BREAKER_STATE_DIR/cb_${tool_name}.state"

    mkdir -p "$CIRCUIT_BREAKER_STATE_DIR"
    echo "$state" > "$state_file"
    echo "$(date +%s)" > "$CIRCUIT_BREAKER_STATE_DIR/cb_${tool_name}.timestamp"

    local state_name
    case "$state" in
        $CIRCUIT_BREAKER_STATE_CLOSED) state_name="CLOSED" ;;
        $CIRCUIT_BREAKER_STATE_OPEN) state_name="OPEN" ;;
        $CIRCUIT_BREAKER_STATE_HALF_OPEN) state_name="HALF_OPEN" ;;
        *) state_name="UNKNOWN" ;;
    esac

    echo "$(date): Circuit breaker $state_name for tool: $tool_name" >> "$CIRCUIT_BREAKER_LOG_FILE"
    hook_log "$LOG_LEVEL_DEBUG" "CircuitBreakerState" "Set circuit state for $tool_name: $state_name"
}

# Get failure count for a tool
get_circuit_breaker_failure_count() {
    local tool_name="$1"
    local failure_file="$CIRCUIT_BREAKER_STATE_DIR/cb_${tool_name}.failures"

    if [[ -f "$failure_file" ]]; then
        cat "$failure_file"
    else
        echo "0"
    fi
}

# Record failure for a tool
record_circuit_breaker_failure() {
    local tool_name="$1"
    local failure_file="$CIRCUIT_BREAKER_STATE_DIR/cb_${tool_name}.failures"
    local current_failures

    mkdir -p "$CIRCUIT_BREAKER_STATE_DIR"
    current_failures=$(get_circuit_breaker_failure_count "$tool_name")
    current_failures=$((current_failures + 1))
    echo "$current_failures" > "$failure_file"

    echo "$(date): Failure recorded for tool: $tool_name (count: $current_failures)" >> "$CIRCUIT_BREAKER_LOG_FILE"
    hook_log "$LOG_LEVEL_DEBUG" "CircuitBreakerState" "Recorded failure for $tool_name (count: $current_failures)"

    # Check if circuit should be opened - ensure threshold is available
    local threshold=${CIRCUIT_BREAKER_FAILURE_THRESHOLD:-3}
    if [[ $current_failures -ge $threshold ]]; then
        set_circuit_breaker_state "$tool_name" "$CIRCUIT_BREAKER_STATE_OPEN"
        hook_log "$LOG_LEVEL_WARN" "CircuitBreakerState" "Circuit breaker OPEN for $tool_name - failure threshold exceeded"
        echo "$(date): Circuit breaker OPEN for tool: $tool_name - threshold exceeded" >> "$CIRCUIT_BREAKER_LOG_FILE"
    fi
}

# Record success for a tool
record_circuit_breaker_success() {
    local tool_name="$1"
    local success_file="$CIRCUIT_BREAKER_STATE_DIR/cb_${tool_name}.successes"
    local current_successes

    mkdir -p "$CIRCUIT_BREAKER_STATE_DIR"

    # Reset failure count on success
    local failure_file="$CIRCUIT_BREAKER_STATE_DIR/cb_${tool_name}.failures"
    echo "0" > "$failure_file"

    current_successes=$(cat "$success_file" 2>/dev/null || echo "0")
    current_successes=$((current_successes + 1))
    echo "$current_successes" > "$success_file"

    echo "$(date): Success recorded for tool: $tool_name (count: $current_successes)" >> "$CIRCUIT_BREAKER_LOG_FILE"
    hook_log "$LOG_LEVEL_DEBUG" "CircuitBreakerState" "Recorded success for $tool_name (count: $current_successes)"

    # Close circuit if success threshold met in half-open state
    local current_state
    current_state=$(get_circuit_breaker_state "$tool_name")
    local success_threshold=${CIRCUIT_BREAKER_SUCCESS_THRESHOLD:-2}
    if [[ $current_state -eq $CIRCUIT_BREAKER_STATE_HALF_OPEN ]] && [[ $current_successes -ge $success_threshold ]]; then
        set_circuit_breaker_state "$tool_name" "$CIRCUIT_BREAKER_STATE_CLOSED"
        hook_log "$LOG_LEVEL_INFO" "CircuitBreakerState" "Circuit breaker CLOSED for $tool_name - service recovered"
        echo "$(date): Circuit breaker CLOSED for tool: $tool_name - service recovered" >> "$CIRCUIT_BREAKER_LOG_FILE"
    fi
}

# Check if circuit should transition from open to half-open
should_circuit_breaker_attempt_reset() {
    local tool_name="$1"
    local timestamp_file="$CIRCUIT_BREAKER_STATE_DIR/cb_${tool_name}.timestamp"

    if [[ ! -f "$timestamp_file" ]]; then
        return 1
    fi

    local last_change
    last_change=$(cat "$timestamp_file")
    local current_time
    current_time=$(date +%s)
    local time_diff
    time_diff=$((current_time - last_change))

    local timeout_seconds=${CIRCUIT_BREAKER_TIMEOUT_SECONDS:-300}
    [[ $time_diff -ge $timeout_seconds ]]
}

# Reset circuit breaker state for a tool (for testing/maintenance)
reset_circuit_breaker_state() {
    local tool_name="$1"

    rm -f "$CIRCUIT_BREAKER_STATE_DIR/cb_${tool_name}".state
    rm -f "$CIRCUIT_BREAKER_STATE_DIR/cb_${tool_name}".timestamp
    rm -f "$CIRCUIT_BREAKER_STATE_DIR/cb_${tool_name}".failures
    rm -f "$CIRCUIT_BREAKER_STATE_DIR/cb_${tool_name}".successes

    hook_log "$LOG_LEVEL_INFO" "CircuitBreakerState" "Circuit breaker state reset for $tool_name"
    echo "$(date): Circuit breaker state reset for tool: $tool_name" >> "$CIRCUIT_BREAKER_LOG_FILE"
}

# Get circuit breaker status for monitoring
get_circuit_breaker_status() {
    local tool_name="$1"
    local state
    local failures
    local timestamp_file="$CIRCUIT_BREAKER_STATE_DIR/cb_${tool_name}.timestamp"

    state=$(get_circuit_breaker_state "$tool_name")
    failures=$(get_circuit_breaker_failure_count "$tool_name")

    local last_change="never"
    if [[ -f "$timestamp_file" ]]; then
        last_change=$(date -d "@$(cat "$timestamp_file")" 2>/dev/null || echo "unknown")
    fi

    echo "Tool: $tool_name, State: $state, Failures: $failures, Last Change: $last_change"
}