#!/bin/bash
# CircuitBreaker - Tool availability management with graceful degradation
# Part of Claude Code SuperClaude hook system resilience components

set -euo pipefail

# Source dependencies
HOOK_LIB_DIR="$(dirname "${BASH_SOURCE[0]}")/.."
source "${HOOK_LIB_DIR}/config/HookConfig.sh"
source "${HOOK_LIB_DIR}/logging/LogManager.sh"
source "$(dirname "${BASH_SOURCE[0]}")/ResilienceConfiguration.sh"
source "$(dirname "${BASH_SOURCE[0]}")/CircuitBreakerState.sh"

# Circuit breaker constants - use include guard to prevent redefinition
if [[ -z "${CIRCUIT_BREAKER_STATE_CLOSED:-}" ]]; then
    readonly CIRCUIT_BREAKER_STATE_CLOSED=0    # Normal operation
    readonly CIRCUIT_BREAKER_STATE_OPEN=1      # Circuit open, bypassing calls
    readonly CIRCUIT_BREAKER_STATE_HALF_OPEN=2 # Testing if service recovered
fi

# Circuit breaker state file location - derived from configuration
if [[ -z "${CIRCUIT_BREAKER_STATE_DIR:-}" ]]; then
    # Ensure configuration constants are available
    if [[ -z "${RESILIENCE_STATE_BASE_DIR:-}" ]]; then
        readonly RESILIENCE_STATE_BASE_DIR="/tmp/claude"
    fi
    if [[ -z "${CIRCUIT_BREAKER_LOG_FILENAME:-}" ]]; then
        readonly CIRCUIT_BREAKER_LOG_FILENAME="circuit-breaker.log"
    fi

    readonly CIRCUIT_BREAKER_STATE_DIR="$RESILIENCE_STATE_BASE_DIR"
    readonly CIRCUIT_BREAKER_LOG_FILE=$(get_resilience_log_path "$CIRCUIT_BREAKER_LOG_FILENAME")
fi

# Initialize circuit breaker state directory
init_circuit_breaker() {
    mkdir -p "$CIRCUIT_BREAKER_STATE_DIR"

    # Initialize logging
    if [[ ! -f "$CIRCUIT_BREAKER_LOG_FILE" ]]; then
        echo "Circuit Breaker initialized at $(date)" > "$CIRCUIT_BREAKER_LOG_FILE"
    fi

    hook_log "$LOG_LEVEL_DEBUG" "CircuitBreaker" "Circuit breaker system initialized"
}

# Delegate to state management module
get_circuit_state() {
    get_circuit_breaker_state "$@"
}

set_circuit_state() {
    set_circuit_breaker_state "$@"
}

record_failure() {
    record_circuit_breaker_failure "$@"
}

record_success() {
    record_circuit_breaker_success "$@"
}

should_attempt_reset() {
    should_circuit_breaker_attempt_reset "$@"
}

# Execute operation and handle result with circuit breaker pattern
execute_operation_with_result_handling() {
    local tool_name="$1"
    shift
    local operation_args=("$@")

    if execute_tool_operation "$tool_name" "${operation_args[@]}"; then
        record_success "$tool_name"
        return 0
    else
        record_failure "$tool_name"
        return 1
    fi
}

# Handle circuit breaker open state
handle_open_circuit_state() {
    local tool_name="$1"
    shift
    local operation_args=("$@")

    if should_attempt_reset "$tool_name"; then
        set_circuit_state "$tool_name" "$CIRCUIT_BREAKER_STATE_HALF_OPEN"
        hook_log "$LOG_LEVEL_INFO" "CircuitBreaker" "Circuit breaker transitioning to HALF_OPEN for $tool_name"
        execute_operation_with_result_handling "$tool_name" "${operation_args[@]}"
    else
        # Circuit still open - return graceful degradation
        hook_log "$LOG_LEVEL_WARN" "CircuitBreaker" "Circuit breaker OPEN for $tool_name - tool unavailable, graceful degradation"
        echo "$(date): Circuit breaker OPEN for tool: $tool_name - graceful degradation applied" >> "$CIRCUIT_BREAKER_LOG_FILE"
        return 2  # Special return code for graceful degradation
    fi
}

# Execute protected operation with circuit breaker pattern
execute_protected_formatting() {
    local tool_name="$1"
    shift
    local operation_args=("$@")

    init_circuit_breaker

    local current_state
    current_state=$(get_circuit_state "$tool_name")

    hook_log "$LOG_LEVEL_DEBUG" "CircuitBreaker" "Executing protected formatting for $tool_name (state: $current_state)"

    case "$current_state" in
        $CIRCUIT_BREAKER_STATE_CLOSED)
            execute_operation_with_result_handling "$tool_name" "${operation_args[@]}"
            ;;
        $CIRCUIT_BREAKER_STATE_OPEN)
            handle_open_circuit_state "$tool_name" "${operation_args[@]}"
            ;;
        $CIRCUIT_BREAKER_STATE_HALF_OPEN)
            execute_operation_with_result_handling "$tool_name" "${operation_args[@]}"
            ;;
    esac
}

# Execute the actual tool operation (to be implemented by specific tools)
execute_tool_operation() {
    local tool_name="$1"
    shift
    local operation_args=("$@")

    hook_log "$LOG_LEVEL_DEBUG" "CircuitBreaker" "Executing tool operation: $tool_name with args: ${operation_args[*]}"

    # Handle different operation types
    case "$tool_name" in
        "python"|"black")
            # For Python/Black operations, check if we should execute formatting
            local language="${operation_args[0]:-python}"
            local files="${operation_args[1]:-}"

            if command -v black >/dev/null 2>&1; then
                hook_log "$LOG_LEVEL_DEBUG" "CircuitBreaker" "Black formatter available for $language"
                # Would execute actual formatting here in real implementation
                return 0
            else
                hook_log "$LOG_LEVEL_WARN" "CircuitBreaker" "Black formatter not available for $language"
                return 1
            fi
            ;;
        "javascript"|"prettier")
            if command -v prettier >/dev/null 2>&1; then
                hook_log "$LOG_LEVEL_DEBUG" "CircuitBreaker" "Prettier available"
                return 0
            else
                hook_log "$LOG_LEVEL_WARN" "CircuitBreaker" "Prettier not available"
                return 1
            fi
            ;;
        *)
            # Generic tool availability check
            if command -v "$tool_name" >/dev/null 2>&1; then
                hook_log "$LOG_LEVEL_DEBUG" "CircuitBreaker" "Tool $tool_name is available"
                return 0
            else
                hook_log "$LOG_LEVEL_WARN" "CircuitBreaker" "Tool $tool_name is not available"
                return 1
            fi
            ;;
    esac
}

# Reset circuit breaker state for a tool (for testing/maintenance)
reset_circuit_breaker() {
    reset_circuit_breaker_state "$@"
}

# Get circuit breaker status for monitoring
get_circuit_status() {
    get_circuit_breaker_status "$@"
}

# Command-line interface for circuit breaker management
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-}" in
        "execute_protected_formatting")
            shift
            execute_protected_formatting "$@"
            ;;
        "reset")
            if [[ -n "${2:-}" ]]; then
                reset_circuit_breaker "$2"
            else
                echo "Usage: $0 reset <tool_name>"
                exit 1
            fi
            ;;
        "status")
            if [[ -n "${2:-}" ]]; then
                get_circuit_status "$2"
            else
                echo "Usage: $0 status <tool_name>"
                exit 1
            fi
            ;;
        *)
            echo "Usage: $0 {execute_protected_formatting|reset|status} <tool_name> [args...]"
            echo "  execute_protected_formatting - Execute tool with circuit breaker protection"
            echo "  reset - Reset circuit breaker state for a tool"
            echo "  status - Get circuit breaker status for a tool"
            exit 1
            ;;
    esac
fi