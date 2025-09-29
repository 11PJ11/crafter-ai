#!/bin/bash
# ResilientHookManager - Unified resilience orchestration for hook system
# Part of Claude Code SuperClaude hook system resilience components

set -euo pipefail

# Source dependencies
HOOK_LIB_DIR="$(dirname "${BASH_SOURCE[0]}")/.."
source "${HOOK_LIB_DIR}/config/HookConfig.sh"
source "${HOOK_LIB_DIR}/logging/LogManager.sh"
source "$(dirname "${BASH_SOURCE[0]}")/ResilienceConfiguration.sh"
source "${HOOK_LIB_DIR}/resilience/CircuitBreaker.sh"
source "${HOOK_LIB_DIR}/resilience/ToolCapabilityService.sh"
source "${HOOK_LIB_DIR}/resilience/FileSystemCoordinator.sh"
source "${HOOK_LIB_DIR}/resilience/OperationQueueManager.sh"

# Resilience manager constants - derived from configuration
readonly RESILIENT_HOOK_MANAGER_STATE_DIR="$RESILIENCE_STATE_BASE_DIR"
readonly RESILIENT_HOOK_MANAGER_LOG_FILE=$(get_resilience_log_path "$RESILIENCE_MANAGER_LOG_FILENAME")

# Resilience metrics
declare -g TOTAL_OPERATIONS=0
declare -g SUCCESSFUL_OPERATIONS=0
declare -g FAILED_OPERATIONS=0
declare -g DEGRADED_OPERATIONS=0

# Initialize resilient hook manager
init_resilient_hook_manager() {
    mkdir -p "$RESILIENT_HOOK_MANAGER_STATE_DIR"

    # Initialize all resilience components
    init_circuit_breaker
    init_tool_capability_service
    init_file_system_coordinator
    init_operation_queue_manager

    # Initialize logging
    if [[ ! -f "$RESILIENT_HOOK_MANAGER_LOG_FILE" ]]; then
        echo "Resilient Hook Manager initialized at $(date)" > "$RESILIENT_HOOK_MANAGER_LOG_FILE"
    fi

    hook_log "$LOG_LEVEL_INFO" "ResilientHookManager" "Resilient hook manager initialized"
    echo "$(date): Resilient hook manager session started" >> "$RESILIENT_HOOK_MANAGER_LOG_FILE"
}

# Execute with resilience for multiple languages
execute_with_resilience() {
    local languages="$1"

    init_resilient_hook_manager

    hook_log "$LOG_LEVEL_INFO" "ResilientHookManager" "Starting resilient execution for languages: $languages"

    local overall_success=true
    local operation_id=1

    IFS=',' read -ra lang_array <<< "$languages"

    # Reset metrics for this session
    TOTAL_OPERATIONS=0
    SUCCESSFUL_OPERATIONS=0
    FAILED_OPERATIONS=0
    DEGRADED_OPERATIONS=0

    # Process each language with full resilience
    for language in "${lang_array[@]}"; do
        language=$(echo "$language" | xargs)  # Trim whitespace

        hook_log "$LOG_LEVEL_INFO" "ResilientHookManager" "Processing language: $language"

        TOTAL_OPERATIONS=$((TOTAL_OPERATIONS + 1))

        if execute_resilient_language_processing "$language" "$operation_id"; then
            local exit_code=$?
            case $exit_code in
                0)
                    SUCCESSFUL_OPERATIONS=$((SUCCESSFUL_OPERATIONS + 1))
                    hook_log "$LOG_LEVEL_INFO" "ResilientHookManager" "Language processing succeeded: $language"
                    ;;
                2)
                    DEGRADED_OPERATIONS=$((DEGRADED_OPERATIONS + 1))
                    hook_log "$LOG_LEVEL_WARN" "ResilientHookManager" "Language processing degraded but continued: $language"
                    # Don't mark as overall failure for graceful degradation
                    ;;
                *)
                    FAILED_OPERATIONS=$((FAILED_OPERATIONS + 1))
                    hook_log "$LOG_LEVEL_ERROR" "ResilientHookManager" "Language processing failed: $language"
                    overall_success=false
                    ;;
            esac
        else
            FAILED_OPERATIONS=$((FAILED_OPERATIONS + 1))
            hook_log "$LOG_LEVEL_ERROR" "ResilientHookManager" "Language processing failed: $language"
            overall_success=false
        fi

        operation_id=$((operation_id + 1))
    done

    # Generate resilience summary
    generate_resilience_summary

    # Check if we met success rate target
    local success_rate
    success_rate=$(calculate_success_rate)

    if [[ $success_rate -ge $RESILIENCE_SUCCESS_RATE_TARGET ]]; then
        hook_log "$LOG_LEVEL_INFO" "ResilientHookManager" "Resilient execution completed successfully (success rate: ${success_rate}%)"
        echo "$(date): Resilience summary - success_rate: ${success_rate}% (target: ${SUCCESS_RATE_TARGET}%)" >> "$RESILIENT_HOOK_MANAGER_LOG_FILE"
        return 0
    else
        hook_log "$LOG_LEVEL_WARN" "ResilientHookManager" "Success rate below target: ${success_rate}% (target: ${SUCCESS_RATE_TARGET}%)"
        echo "$(date): Success rate below target: ${success_rate}% (target: ${SUCCESS_RATE_TARGET}%)" >> "$RESILIENT_HOOK_MANAGER_LOG_FILE"
        return 1
    fi
}

# Execute resilient processing for a single language
execute_resilient_language_processing() {
    local language="$1"
    local operation_id="$2"

    hook_log "$LOG_LEVEL_DEBUG" "ResilientHookManager" "Starting resilient processing for $language (operation $operation_id)"

    # Step 1: Assess tool capabilities
    local required_tools
    required_tools=$(get_required_tools_for_language "$language")

    local tool_assessment_result=true
    local available_tools=()
    local degraded_tools=()

    if [[ -n "$required_tools" ]]; then
        IFS=' ' read -ra tools_array <<< "$required_tools"

        for tool_spec in "${tools_array[@]}"; do
            local tool_name install_method package_name
            IFS=':' read -r tool_name install_method package_name <<< "$tool_spec"
            package_name="${package_name:-$tool_name}"

            local capability_result
            capability_result=$(assess_tool_capability "$tool_name" "$install_method" "$package_name")
            local state
            state=$(echo "$capability_result" | cut -d':' -f1)

            case $state in
                $TOOL_STATE_HEALTHY)
                    available_tools+=("$tool_name")
                    hook_log "$LOG_LEVEL_DEBUG" "ResilientHookManager" "Tool available: $tool_name"
                    ;;
                $TOOL_STATE_DEGRADED)
                    degraded_tools+=("$tool_name")
                    hook_log "$LOG_LEVEL_WARN" "ResilientHookManager" "Tool degraded: $tool_name"
                    # Attempt remediation
                    if attempt_tool_remediation "$tool_name" "$install_method" "$package_name"; then
                        available_tools+=("$tool_name")
                        hook_log "$LOG_LEVEL_INFO" "ResilientHookManager" "Tool remediated successfully: $tool_name"
                    fi
                    ;;
                $TOOL_STATE_UNAVAILABLE)
                    hook_log "$LOG_LEVEL_WARN" "ResilientHookManager" "Tool unavailable: $tool_name"
                    tool_assessment_result=false
                    ;;
            esac
        done
    fi

    # Step 2: Find files for processing
    local files_to_process
    files_to_process=$(find_files_for_language "$language")

    if [[ -z "$files_to_process" ]]; then
        hook_log "$LOG_LEVEL_DEBUG" "ResilientHookManager" "No files found for language: $language"
        return 0  # Success - nothing to process
    fi

    # Step 3: Execute with circuit breaker protection
    local processing_result=0

    if [[ ${#available_tools[@]} -gt 0 ]]; then
        # We have at least some tools available
        local primary_tool="${available_tools[0]}"

        hook_log "$LOG_LEVEL_DEBUG" "ResilientHookManager" "Executing with circuit breaker protection using tool: $primary_tool"

        if execute_protected_formatting "$primary_tool" "$language" "$files_to_process"; then
            processing_result=$?
            case $processing_result in
                0)
                    hook_log "$LOG_LEVEL_INFO" "ResilientHookManager" "Processing completed successfully with tool: $primary_tool"
                    ;;
                2)
                    hook_log "$LOG_LEVEL_WARN" "ResilientHookManager" "Processing completed with graceful degradation: $primary_tool"
                    ;;
                *)
                    hook_log "$LOG_LEVEL_ERROR" "ResilientHookManager" "Processing failed with tool: $primary_tool (exit code: $processing_result)"
                    ;;
            esac
        else
            processing_result=$?
            hook_log "$LOG_LEVEL_WARN" "ResilientHookManager" "Circuit breaker execution failed for $primary_tool (exit code: $processing_result)"
        fi
    else
        # No tools available - complete graceful degradation
        hook_log "$LOG_LEVEL_WARN" "ResilientHookManager" "No tools available for $language - graceful degradation"
        echo "$(date): Graceful degradation applied for language: $language (no tools available)" >> "$RESILIENT_HOOK_MANAGER_LOG_FILE"
        processing_result=2  # Degraded but not failed
    fi

    return $processing_result
}

# Get required tools for a language
get_required_tools_for_language() {
    local language="$1"

    case "$language" in
        "python")
            echo "black:pipx:black"
            ;;
        "javascript"|"typescript")
            echo "prettier:npm:prettier"
            ;;
        "shell")
            echo "shellcheck:apt:shellcheck"
            ;;
        "json")
            echo "jq:apt:jq prettier:npm:prettier"
            ;;
        *)
            echo ""  # No specific tools required
            ;;
    esac
}

# Find files for a language
find_files_for_language() {
    local language="$1"
    local patterns

    case "$language" in
        "python")
            patterns="*.py"
            ;;
        "javascript")
            patterns="*.js,*.jsx"
            ;;
        "typescript")
            patterns="*.ts,*.tsx"
            ;;
        "shell")
            patterns="*.sh,*.bash"
            ;;
        "json")
            patterns="*.json"
            ;;
        *)
            patterns="*.$language"
            ;;
    esac

    # Use existing BaseFormatter functionality
    find_files_to_format "$patterns" | head -20 | tr '\n' ' '
}

# Enhanced protected formatting with file coordination
execute_protected_formatting() {
    local tool_name="$1"
    local language="$2"
    local files_to_process="$3"

    hook_log "$LOG_LEVEL_DEBUG" "ResilientHookManager" "Executing protected formatting: $tool_name for $language"

    # Use circuit breaker for tool availability
    local cb_result
    if execute_protected_operation_with_coordination "$tool_name" "$language" "$files_to_process"; then
        cb_result=$?
    else
        cb_result=$?
    fi

    case $cb_result in
        0)
            hook_log "$LOG_LEVEL_INFO" "ResilientHookManager" "Protected formatting succeeded"
            return 0
            ;;
        2)
            hook_log "$LOG_LEVEL_WARN" "ResilientHookManager" "Protected formatting degraded but graceful"
            return 2
            ;;
        *)
            hook_log "$LOG_LEVEL_ERROR" "ResilientHookManager" "Protected formatting failed (exit code: $cb_result)"
            return $cb_result
            ;;
    esac
}

# Execute protected operation with file system coordination
execute_protected_operation_with_coordination() {
    local tool_name="$1"
    local language="$2"
    local files_to_process="$3"

    # Queue the operation for coordinated processing
    local operation_id="resilient_${tool_name}_$$_$(date +%s)"

    if enqueue_operation "$operation_id" "$language" "$files_to_process" "format_with_$tool_name" "$PRIORITY_NORMAL"; then
        hook_log "$LOG_LEVEL_DEBUG" "ResilientHookManager" "Operation queued successfully: $operation_id"
    else
        hook_log "$LOG_LEVEL_ERROR" "ResilientHookManager" "Failed to queue operation: $operation_id"
        return 1
    fi

    # Process the queue immediately for this operation
    # In a real implementation, this could be done asynchronously
    local processing_result=0

    case "$language" in
        "python")
            if execute_coordinated_python_formatting "$files_to_process"; then
                hook_log "$LOG_LEVEL_DEBUG" "ResilientHookManager" "Python formatting coordinated successfully"
            else
                processing_result=$?
                hook_log "$LOG_LEVEL_WARN" "ResilientHookManager" "Python formatting coordination failed (exit code: $processing_result)"
            fi
            ;;
        "javascript"|"typescript")
            if execute_coordinated_javascript_formatting "$files_to_process"; then
                hook_log "$LOG_LEVEL_DEBUG" "ResilientHookManager" "JavaScript formatting coordinated successfully"
            else
                processing_result=$?
                hook_log "$LOG_LEVEL_WARN" "ResilientHookManager" "JavaScript formatting coordination failed (exit code: $processing_result)"
            fi
            ;;
        "shell")
            if execute_coordinated_shell_checking "$files_to_process"; then
                hook_log "$LOG_LEVEL_DEBUG" "ResilientHookManager" "Shell checking coordinated successfully"
            else
                processing_result=$?
                hook_log "$LOG_LEVEL_WARN" "ResilientHookManager" "Shell checking coordination failed (exit code: $processing_result)"
            fi
            ;;
        *)
            hook_log "$LOG_LEVEL_WARN" "ResilientHookManager" "No coordinated processing available for language: $language"
            processing_result=2  # Graceful degradation
            ;;
    esac

    # Update operation status based on result
    if [[ $processing_result -eq 0 ]]; then
        mark_operation_completed "$operation_id"
    else
        mark_operation_failed "$operation_id"
    fi

    return $processing_result
}

# Calculate current success rate
calculate_success_rate() {
    if [[ $TOTAL_OPERATIONS -eq 0 ]]; then
        echo "100"  # No operations = 100% success
        return
    fi

    # Consider degraded operations as partial successes
    local effective_successful_operations=$((SUCCESSFUL_OPERATIONS + DEGRADED_OPERATIONS))
    local success_rate=$((effective_successful_operations * 100 / TOTAL_OPERATIONS))

    echo "$success_rate"
}

# Generate comprehensive resilience summary
generate_resilience_summary() {
    local success_rate
    success_rate=$(calculate_success_rate)

    local summary_file="$RESILIENT_HOOK_MANAGER_STATE_DIR/resilience_summary.log"

    {
        echo "=== Resilience Summary ==="
        echo "Generated: $(date)"
        echo "Session: $$"
        echo
        echo "Operations:"
        echo "  Total: $TOTAL_OPERATIONS"
        echo "  Successful: $SUCCESSFUL_OPERATIONS"
        echo "  Degraded: $DEGRADED_OPERATIONS"
        echo "  Failed: $FAILED_OPERATIONS"
        echo
        echo "Success Rate: ${success_rate}%"
        echo "Target Rate: ${SUCCESS_RATE_TARGET}%"
        echo "Status: $([ $success_rate -ge $RESILIENCE_SUCCESS_RATE_TARGET ] && echo "TARGET MET" || echo "BELOW TARGET")"
        echo
        echo "Tool Status:"
        get_tool_status_report black prettier shellcheck jq 2>/dev/null || echo "  Tool status unavailable"
        echo
        echo "Coordination Status:"
        get_coordination_status 2>/dev/null || echo "  Coordination status unavailable"
    } > "$summary_file"

    hook_log "$LOG_LEVEL_INFO" "ResilientHookManager" "Resilience summary generated: $summary_file"
    echo "$(date): Resilience summary generated - success_rate: ${success_rate}%" >> "$RESILIENT_HOOK_MANAGER_LOG_FILE"
}

# Health check for resilience system
health_check_resilience_system() {
    init_resilient_hook_manager

    echo "=== Resilience System Health Check ==="
    echo "Generated: $(date)"
    echo

    local health_issues=0

    # Check circuit breaker system
    echo "Circuit Breaker System:"
    if [[ -d "$CB_STATE_DIR" ]]; then
        echo "  Status: Initialized"
        local cb_states
        cb_states=$(ls "$CB_STATE_DIR"/cb_*.state 2>/dev/null | wc -l)
        echo "  Active Circuit Breakers: $cb_states"
    else
        echo "  Status: Not initialized"
        health_issues=$((health_issues + 1))
    fi

    # Check file system coordinator
    echo
    echo "File System Coordinator:"
    if [[ -d "$FS_COORD_STATE_DIR" ]]; then
        echo "  Status: Initialized"
        local active_locks
        active_locks=$(ls "$FS_COORD_STATE_DIR"/lock_*.lock 2>/dev/null | wc -l)
        echo "  Active Locks: $active_locks"
    else
        echo "  Status: Not initialized"
        health_issues=$((health_issues + 1))
    fi

    # Check operation queue
    echo
    echo "Operation Queue:"
    if [[ -f "$QUEUE_STATE_DIR/operation_queue.jsonl" ]]; then
        local queue_size
        queue_size=$(wc -l < "$QUEUE_STATE_DIR/operation_queue.jsonl")
        echo "  Status: Active"
        echo "  Queue Size: $queue_size"
    else
        echo "  Status: Empty"
    fi

    # Overall health status
    echo
    if [[ $health_issues -eq 0 ]]; then
        echo "Overall Health: HEALTHY"
        return 0
    else
        echo "Overall Health: ISSUES DETECTED ($health_issues)"
        return 1
    fi
}

# Command-line interface
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-}" in
        "execute_with_resilience")
            if [[ -n "${2:-}" ]]; then
                execute_with_resilience "$2"
            else
                echo "Usage: $0 execute_with_resilience <languages>"
                echo "  languages - Comma-separated list of languages (e.g., 'python,javascript,shell')"
                exit 1
            fi
            ;;
        "health")
            health_check_resilience_system
            ;;
        "summary")
            init_resilient_hook_manager
            generate_resilience_summary
            cat "$RESILIENT_HOOK_MANAGER_STATE_DIR/resilience_summary.log"
            ;;
        *)
            echo "Usage: $0 {execute_with_resilience|health|summary} [args...]"
            echo "  execute_with_resilience - Execute hook operations with full resilience"
            echo "  health - Check resilience system health"
            echo "  summary - Generate resilience summary report"
            exit 1
            ;;
    esac
fi