#!/bin/bash
# OperationQueueManager - Batch processing and conflict resolution
# Part of Claude Code SuperClaude hook system resilience components

set -euo pipefail

# Source dependencies
HOOK_LIB_DIR="$(dirname "${BASH_SOURCE[0]}")/.."
source "${HOOK_LIB_DIR}/config/HookConfig.sh"
source "${HOOK_LIB_DIR}/logging/LogManager.sh"
source "$(dirname "${BASH_SOURCE[0]}")/ResilienceConfiguration.sh"

# Check if file system coordinator functions are available
if ! declare -f acquire_file_lock >/dev/null 2>&1; then
    # Define minimal file locking functions if not available
    acquire_file_lock() {
        local file_path="$1"
        local timeout="${2:-30}"
        local lock_file="/tmp/claude/lock_$(basename "$file_path" | tr '/' '_').lock"

        mkdir -p "/tmp/claude"
        local start_time=$(date +%s)

        while [[ -f "$lock_file" ]]; do
            local current_time=$(date +%s)
            if [[ $((current_time - start_time)) -ge $timeout ]]; then
                return 1
            fi
            sleep 0.1
        done

        echo "$$:$(date +%s):$file_path" > "$lock_file"
        return 0
    }

    release_file_lock() {
        local file_path="$1"
        local lock_file="/tmp/claude/lock_$(basename "$file_path" | tr '/' '_').lock"
        if [[ -f "$lock_file" ]]; then
            local lock_pid=$(cut -d':' -f1 "$lock_file" 2>/dev/null)
            if [[ "$lock_pid" = "$$" ]]; then
                rm -f "$lock_file"
            fi
        fi
    }
fi

# Queue management constants
readonly QUEUE_STATE_DIR="/tmp/claude"
readonly QUEUE_LOG_FILE="$QUEUE_STATE_DIR/operation-queue.log"
readonly MAX_QUEUE_SIZE=1000
readonly MAX_CONCURRENT_OPERATIONS=3

# Operation priority levels - use include guard to prevent redefinition
if [[ -z "${PRIORITY_CRITICAL:-}" ]]; then
    readonly PRIORITY_CRITICAL=0
    readonly PRIORITY_HIGH=1
    readonly PRIORITY_NORMAL=2
    readonly PRIORITY_LOW=3
fi

# Initialize operation queue manager
init_operation_queue_manager() {
    mkdir -p "$QUEUE_STATE_DIR"

    # Initialize logging
    if [[ ! -f "$QUEUE_LOG_FILE" ]]; then
        echo "Operation Queue Manager initialized at $(date)" > "$QUEUE_LOG_FILE"
    fi

    hook_log "$LOG_LEVEL_DEBUG" "OperationQueueManager" "Operation queue manager initialized"
}

# Add operation to queue with priority
enqueue_operation() {
    local operation_id="$1"
    local operation_type="$2"
    local target_files="$3"
    local command="$4"
    local priority="${5:-$PRIORITY_NORMAL}"

    init_operation_queue_manager

    local queue_file="$QUEUE_STATE_DIR/operation_queue.jsonl"
    local operation_entry

    # Create operation entry in JSONL format for simplicity
    operation_entry=$(cat <<EOF
{"id":"$operation_id","type":"$operation_type","files":"$target_files","command":"$command","priority":$priority,"state":$OP_STATE_QUEUED,"queued_at":$(date +%s),"pid":$$}
EOF
    )

    # Check queue size
    local current_size=0
    if [[ -f "$queue_file" ]]; then
        current_size=$(wc -l < "$queue_file")
    fi

    if [[ $current_size -ge $MAX_QUEUE_SIZE ]]; then
        hook_log "$LOG_LEVEL_ERROR" "OperationQueueManager" "Queue size limit exceeded ($MAX_QUEUE_SIZE)"
        return 1
    fi

    # Add to queue
    echo "$operation_entry" >> "$queue_file"

    hook_log "$LOG_LEVEL_INFO" "OperationQueueManager" "Operation enqueued: $operation_id (priority: $priority)"
    echo "$(date): Operation enqueued: $operation_id for files: $target_files (priority: $priority)" >> "$QUEUE_LOG_FILE"

    return 0
}

# Dequeue operation based on priority
dequeue_operation() {
    local queue_file="$QUEUE_STATE_DIR/operation_queue.jsonl"

    if [[ ! -f "$queue_file" ]] || [[ ! -s "$queue_file" ]]; then
        return 1  # Queue is empty
    fi

    # Find highest priority queued operation
    local best_line=""
    local best_priority=$PRIORITY_LOW
    local line_number=0
    local best_line_number=0

    while IFS= read -r line; do
        line_number=$((line_number + 1))

        # Extract state and priority (simple parsing)
        local state priority

        # Extract state (simple grep-based parsing)
        if echo "$line" | grep -q '"state":0'; then
            state=$OP_STATE_QUEUED
        else
            continue  # Skip non-queued operations
        fi

        # Extract priority (simple grep-based parsing)
        if echo "$line" | grep -q '"priority":0'; then
            priority=$PRIORITY_CRITICAL
        elif echo "$line" | grep -q '"priority":1'; then
            priority=$PRIORITY_HIGH
        elif echo "$line" | grep -q '"priority":2'; then
            priority=$PRIORITY_NORMAL
        elif echo "$line" | grep -q '"priority":3'; then
            priority=$PRIORITY_LOW
        else
            priority=$PRIORITY_NORMAL
        fi

        # Check if this is higher priority than current best
        if [[ $priority -le $best_priority ]]; then
            best_priority=$priority
            best_line="$line"
            best_line_number=$line_number
        fi
    done < "$queue_file"

    if [[ -n "$best_line" ]]; then
        # Mark operation as running
        local temp_file
        temp_file=$(mktemp)

        # Update the selected line to running state
        awk -v ln="$best_line_number" -v new_state="$OP_STATE_RUNNING" '
            NR == ln { gsub(/"state":0/, "\"state\":" new_state); print }
            NR != ln { print }
        ' "$queue_file" > "$temp_file"

        mv "$temp_file" "$queue_file"

        echo "$best_line"
        return 0
    else
        return 1  # No queued operations found
    fi
}

# Process operation queue with conflict resolution
process_queue_with_conflict_resolution() {
    init_operation_queue_manager

    hook_log "$LOG_LEVEL_INFO" "OperationQueueManager" "Starting queue processing with conflict resolution"

    local processed_count=0
    local failed_count=0
    local concurrent_operations=0
    local active_pids=()

    while true; do
        # Clean up completed operations
        cleanup_completed_operations active_pids concurrent_operations

        # Check if we can start more operations
        if [[ $concurrent_operations -ge $MAX_CONCURRENT_OPERATIONS ]]; then
            sleep 1
            continue
        fi

        # Try to dequeue next operation
        local operation_line
        if ! operation_line=$(dequeue_operation); then
            # No more operations to process
            break
        fi

        # Extract operation details
        local operation_id operation_type target_files command
        operation_id=$(extract_json_field "$operation_line" "id")
        operation_type=$(extract_json_field "$operation_line" "type")
        target_files=$(extract_json_field "$operation_line" "files")
        command=$(extract_json_field "$operation_line" "command")

        hook_log "$LOG_LEVEL_DEBUG" "OperationQueueManager" "Processing operation: $operation_id ($operation_type)"

        # Start operation in background
        if start_operation_background "$operation_id" "$operation_type" "$target_files" "$command"; then
            processed_count=$((processed_count + 1))
            concurrent_operations=$((concurrent_operations + 1))
        else
            failed_count=$((failed_count + 1))
            mark_operation_failed "$operation_id"
        fi
    done

    # Wait for all remaining operations to complete
    wait_for_remaining_operations active_pids

    hook_log "$LOG_LEVEL_INFO" "OperationQueueManager" "Queue processing completed - processed: $processed_count, failed: $failed_count"
    echo "$(date): Queue processing completed - processed: $processed_count, failed: $failed_count" >> "$QUEUE_LOG_FILE"

    return $failed_count
}

# Start operation in background with conflict prevention
start_operation_background() {
    local operation_id="$1"
    local operation_type="$2"
    local target_files="$3"
    local command="$4"

    # Create conflict-free environment for operation
    local operation_log="$QUEUE_STATE_DIR/op_${operation_id}.log"

    {
        # Execute operation with file system coordination
        case "$operation_type" in
            "python"|"black")
                execute_coordinated_python_formatting "$target_files"
                ;;
            "javascript"|"prettier")
                execute_coordinated_javascript_formatting "$target_files"
                ;;
            "shell"|"shellcheck")
                execute_coordinated_shell_checking "$target_files"
                ;;
            *)
                execute_generic_coordinated_operation "$operation_type" "$target_files" "$command"
                ;;
        esac

        local operation_result=$?

        if [[ $operation_result -eq 0 ]]; then
            mark_operation_completed "$operation_id"
            echo "$(date): Operation $operation_id completed successfully" >> "$QUEUE_LOG_FILE"
        else
            mark_operation_failed "$operation_id"
            echo "$(date): Operation $operation_id failed (exit code: $operation_result)" >> "$QUEUE_LOG_FILE"
        fi

        return $operation_result
    } > "$operation_log" 2>&1 &

    local bg_pid=$!
    hook_log "$LOG_LEVEL_DEBUG" "OperationQueueManager" "Started operation $operation_id in background (PID: $bg_pid)"

    # Store PID for tracking
    echo "$bg_pid:$operation_id" >> "$QUEUE_STATE_DIR/active_operations.txt"

    return 0
}

# Execute coordinated Python formatting
execute_coordinated_python_formatting() {
    local target_files="$1"

    IFS=' ' read -ra files_array <<< "$target_files"
    for file in "${files_array[@]}"; do
        if [[ -f "$file" ]] && [[ "$file" == *.py ]]; then
            if ! execute_black_without_retries "$file"; then
                hook_log "$LOG_LEVEL_WARN" "OperationQueueManager" "Python formatting failed for: $file"
                return 1
            fi
        fi
    done

    return 0
}

# Execute coordinated JavaScript formatting
execute_coordinated_javascript_formatting() {
    local target_files="$1"

    if ! command -v prettier >/dev/null 2>&1; then
        hook_log "$LOG_LEVEL_WARN" "OperationQueueManager" "Prettier not available for JavaScript formatting"
        return 1
    fi

    IFS=' ' read -ra files_array <<< "$target_files"
    local temp_files=()

    # Collect valid JavaScript/TypeScript files
    for file in "${files_array[@]}"; do
        if [[ -f "$file" ]] && [[ "$file" =~ \.(js|jsx|ts|tsx)$ ]]; then
            temp_files+=("$file")
        fi
    done

    if [[ ${#temp_files[@]} -eq 0 ]]; then
        return 0
    fi

    # Execute prettier with file system coordination
    if coordinate_batch_operations "format" "${temp_files[@]}"; then
        return 0
    else
        hook_log "$LOG_LEVEL_WARN" "OperationQueueManager" "JavaScript formatting failed for files: ${temp_files[*]}"
        return 1
    fi
}

# Execute coordinated shell checking
execute_coordinated_shell_checking() {
    local target_files="$1"

    if ! command -v shellcheck >/dev/null 2>&1; then
        hook_log "$LOG_LEVEL_WARN" "OperationQueueManager" "Shellcheck not available"
        return 1
    fi

    IFS=' ' read -ra files_array <<< "$target_files"
    for file in "${files_array[@]}"; do
        if [[ -f "$file" ]] && [[ "$file" =~ \.(sh|bash)$ ]]; then
            if ! acquire_file_lock "$file"; then
                hook_log "$LOG_LEVEL_WARN" "OperationQueueManager" "Could not acquire lock for shell check: $file"
                return 1
            fi

            # Execute shellcheck
            local check_result=0
            if ! shellcheck "$file"; then
                check_result=$?
                hook_log "$LOG_LEVEL_WARN" "OperationQueueManager" "Shell check failed for: $file (exit code: $check_result)"
            fi

            release_file_lock "$file"

            if [[ $check_result -ne 0 ]]; then
                return $check_result
            fi
        fi
    done

    return 0
}

# Execute generic coordinated operation
execute_generic_coordinated_operation() {
    local operation_type="$1"
    local target_files="$2"
    local command="$3"

    hook_log "$LOG_LEVEL_DEBUG" "OperationQueueManager" "Executing generic operation: $operation_type"

    # Simple execution with basic coordination
    IFS=' ' read -ra files_array <<< "$target_files"
    for file in "${files_array[@]}"; do
        if [[ -f "$file" ]]; then
            if ! acquire_file_lock "$file"; then
                hook_log "$LOG_LEVEL_WARN" "OperationQueueManager" "Could not acquire lock for: $file"
                return 1
            fi

            # Execute command (simplified)
            local exec_result=0
            if ! eval "$command '$file'"; then
                exec_result=$?
            fi

            release_file_lock "$file"

            if [[ $exec_result -ne 0 ]]; then
                return $exec_result
            fi
        fi
    done

    return 0
}

# Helper function to extract JSON field (simple implementation)
extract_json_field() {
    local json_line="$1"
    local field="$2"

    # Simple regex-based extraction
    if [[ "$json_line" =~ \"$field\":\"([^\"]*)\"|\"$field\":([0-9]+) ]]; then
        echo "${BASH_REMATCH[1]}${BASH_REMATCH[2]}"
    else
        echo ""
    fi
}

# Mark operation as completed
mark_operation_completed() {
    local operation_id="$1"
    update_operation_state "$operation_id" "$OP_STATE_COMPLETED"
}

# Mark operation as failed
mark_operation_failed() {
    local operation_id="$1"
    update_operation_state "$operation_id" "$OP_STATE_FAILED"
}

# Update operation state in queue
update_operation_state() {
    local operation_id="$1"
    local new_state="$2"
    local queue_file="$QUEUE_STATE_DIR/operation_queue.jsonl"

    if [[ -f "$queue_file" ]]; then
        local temp_file
        temp_file=$(mktemp)

        # Update state for matching operation ID
        while IFS= read -r line; do
            if echo "$line" | grep -q "\"id\":\"$operation_id\""; then
                # Replace state in this line
                echo "$line" | sed "s/\"state\":[0-9]*/\"state\":$new_state/"
            else
                echo "$line"
            fi
        done < "$queue_file" > "$temp_file"

        mv "$temp_file" "$queue_file"
    fi
}

# Clean up completed operations
cleanup_completed_operations() {
    local -n pids_ref=$1
    local -n count_ref=$2

    local active_ops_file="$QUEUE_STATE_DIR/active_operations.txt"

    if [[ ! -f "$active_ops_file" ]]; then
        return 0
    fi

    local temp_file
    temp_file=$(mktemp)
    local active_count=0

    while IFS=':' read -r pid operation_id; do
        if kill -0 "$pid" 2>/dev/null; then
            # Process still running
            echo "$pid:$operation_id" >> "$temp_file"
            active_count=$((active_count + 1))
        else
            # Process completed
            hook_log "$LOG_LEVEL_DEBUG" "OperationQueueManager" "Operation completed: $operation_id (PID: $pid)"
        fi
    done < "$active_ops_file"

    mv "$temp_file" "$active_ops_file"
    count_ref=$active_count
}

# Wait for remaining operations
wait_for_remaining_operations() {
    local -n pids_ref=$1

    local active_ops_file="$QUEUE_STATE_DIR/active_operations.txt"

    if [[ ! -f "$active_ops_file" ]]; then
        return 0
    fi

    hook_log "$LOG_LEVEL_INFO" "OperationQueueManager" "Waiting for remaining operations to complete"

    while [[ -s "$active_ops_file" ]]; do
        cleanup_completed_operations pids_ref temp_count
        sleep 2
    done

    hook_log "$LOG_LEVEL_INFO" "OperationQueueManager" "All operations completed"
}

# Get queue status
get_queue_status() {
    init_operation_queue_manager

    local queue_file="$QUEUE_STATE_DIR/operation_queue.jsonl"

    echo "=== Operation Queue Status ==="
    echo "Generated: $(date)"
    echo

    if [[ ! -f "$queue_file" ]]; then
        echo "Queue: Empty"
        return 0
    fi

    local total_operations=0
    local queued_operations=0
    local running_operations=0
    local completed_operations=0
    local failed_operations=0

    while IFS= read -r line; do
        total_operations=$((total_operations + 1))

        if echo "$line" | grep -q '"state":0'; then
            queued_operations=$((queued_operations + 1))
        elif echo "$line" | grep -q '"state":1'; then
            running_operations=$((running_operations + 1))
        elif echo "$line" | grep -q '"state":2'; then
            completed_operations=$((completed_operations + 1))
        elif echo "$line" | grep -q '"state":3'; then
            failed_operations=$((failed_operations + 1))
        fi
    done < "$queue_file"

    echo "Total Operations: $total_operations"
    echo "Queued: $queued_operations"
    echo "Running: $running_operations"
    echo "Completed: $completed_operations"
    echo "Failed: $failed_operations"
}

# Command-line interface
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-}" in
        "enqueue")
            if [[ $# -ge 5 ]]; then
                enqueue_operation "$2" "$3" "$4" "$5" "${6:-$PRIORITY_NORMAL}"
            else
                echo "Usage: $0 enqueue <operation_id> <operation_type> <target_files> <command> [priority]"
                exit 1
            fi
            ;;
        "process")
            process_queue_with_conflict_resolution
            ;;
        "status")
            get_queue_status
            ;;
        *)
            echo "Usage: $0 {enqueue|process|status} [args...]"
            echo "  enqueue - Add operation to queue"
            echo "  process - Process queue with conflict resolution"
            echo "  status - Show queue status"
            exit 1
            ;;
    esac
fi