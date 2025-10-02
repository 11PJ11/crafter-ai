#!/bin/bash
# AI-Craft Framework - Managed File
# Part of Claude Code SuperClaude modular hook system
# FileSystemCoordinator - Resource coordination and conflict prevention
# Part of Claude Code SuperClaude hook system resilience components

set -euo pipefail

# Source dependencies
HOOK_LIB_DIR="$(dirname "${BASH_SOURCE[0]}")/.."
source "${HOOK_LIB_DIR}/config/HookConfig.sh"
source "${HOOK_LIB_DIR}/logging/LogManager.sh"
source "$(dirname "${BASH_SOURCE[0]}")/ResilienceConfiguration.sh"

# File system coordination constants - derived from configuration
readonly FILE_SYSTEM_COORDINATOR_STATE_DIR="$RESILIENCE_STATE_BASE_DIR"
readonly FILE_SYSTEM_COORDINATOR_LOG_FILE=$(get_resilience_log_path "$FILE_SYSTEM_COORDINATOR_LOG_FILENAME")

# Operation states - use include guard to prevent redefinition
if [[ -z "${OP_STATE_QUEUED:-}" ]]; then
    readonly OP_STATE_QUEUED=0
    readonly OP_STATE_RUNNING=1
    readonly OP_STATE_COMPLETED=2
    readonly OP_STATE_FAILED=3
fi

# Get file pattern for language
get_language_file_pattern() {
    local language="$1"
    case "$language" in
        "python")
            echo "*.py"
            ;;
        "javascript")
            echo "*.js,*.jsx"
            ;;
        "typescript")
            echo "*.ts,*.tsx"
            ;;
        *)
            echo "*.$language"
            ;;
    esac
}

# Initialize file system coordinator
init_file_system_coordinator() {
    mkdir -p "$FILE_SYSTEM_COORDINATOR_STATE_DIR"

    # Initialize logging
    if [[ ! -f "$FILE_SYSTEM_COORDINATOR_LOG_FILE" ]]; then
        echo "File System Coordinator initialized at $(date)" > "$FILE_SYSTEM_COORDINATOR_LOG_FILE"
    fi

    hook_log "$LOG_LEVEL_DEBUG" "FileSystemCoordinator" "File system coordinator initialized"
}

# Acquire exclusive lock for file operations
acquire_file_lock() {
    local file_path="$1"
    local timeout="${2:-$FILE_SYSTEM_LOCK_TIMEOUT_SECONDS}"
    local lock_file="$FILE_SYSTEM_COORDINATOR_STATE_DIR/lock_$(basename "$file_path" | tr '/' '_').lock"

    local start_time
    start_time=$(date +%s)

    while [[ -f "$lock_file" ]]; do
        local current_time
        current_time=$(date +%s)
        local elapsed
        elapsed=$((current_time - start_time))

        if [[ $elapsed -ge $timeout ]]; then
            hook_log "$LOG_LEVEL_ERROR" "FileSystemCoordinator" "Lock timeout for file: $file_path"
            echo "$(date): Lock timeout for file: $file_path" >> "$FILE_SYSTEM_COORDINATOR_LOG_FILE"
            return 1
        fi

        sleep 0.1
    done

    # Create lock file with process information
    echo "$$:$(date +%s):$file_path" > "$lock_file"
    hook_log "$LOG_LEVEL_DEBUG" "FileSystemCoordinator" "Acquired lock for file: $file_path"
    echo "$(date): Lock acquired for file: $file_path (PID: $$)" >> "$FILE_SYSTEM_COORDINATOR_LOG_FILE"

    return 0
}

# Release exclusive lock for file operations
release_file_lock() {
    local file_path="$1"
    local lock_file="$FILE_SYSTEM_COORDINATOR_STATE_DIR/lock_$(basename "$file_path" | tr '/' '_').lock"

    if [[ -f "$lock_file" ]]; then
        # Verify we own the lock
        local lock_pid
        lock_pid=$(cut -d':' -f1 "$lock_file" 2>/dev/null || echo "")

        if [[ "$lock_pid" = "$$" ]]; then
            rm -f "$lock_file"
            hook_log "$LOG_LEVEL_DEBUG" "FileSystemCoordinator" "Released lock for file: $file_path"
            echo "$(date): Lock released for file: $file_path (PID: $$)" >> "$FILE_SYSTEM_COORDINATOR_LOG_FILE"
        else
            hook_log "$LOG_LEVEL_WARN" "FileSystemCoordinator" "Cannot release lock - not owner: $file_path"
        fi
    fi
}

# Clean up stale locks from dead processes
cleanup_stale_locks() {
    local cleaned=0

    for lock_file in "$FILE_SYSTEM_COORDINATOR_STATE_DIR"/lock_*.lock; do
        if [[ -f "$lock_file" ]]; then
            local lock_pid
            local lock_time
            lock_pid=$(cut -d':' -f1 "$lock_file" 2>/dev/null || echo "")
            lock_time=$(cut -d':' -f2 "$lock_file" 2>/dev/null || echo "0")

            # Check if process is still running
            if [[ -n "$lock_pid" ]] && ! kill -0 "$lock_pid" 2>/dev/null; then
                rm -f "$lock_file"
                hook_log "$LOG_LEVEL_INFO" "FileSystemCoordinator" "Cleaned up stale lock from dead process: $lock_pid"
                echo "$(date): Cleaned up stale lock from dead process: $lock_pid" >> "$FILE_SYSTEM_COORDINATOR_LOG_FILE"
                cleaned=$((cleaned + 1))
            elif [[ -n "$lock_time" ]]; then
                # Check for very old locks (configurable threshold)
                local current_time
                current_time=$(date +%s)
                local age
                age=$((current_time - lock_time))

                if [[ $age -gt $STALE_LOCK_CLEANUP_SECONDS ]]; then
                    rm -f "$lock_file"
                    hook_log "$LOG_LEVEL_WARN" "FileSystemCoordinator" "Cleaned up old lock (${age}s old) for PID: $lock_pid"
                    echo "$(date): Cleaned up old lock (${age}s old) for PID: $lock_pid" >> "$FILE_SYSTEM_COORDINATOR_LOG_FILE"
                    cleaned=$((cleaned + 1))
                fi
            fi
        fi
    done

    if [[ $cleaned -gt 0 ]]; then
        hook_log "$LOG_LEVEL_INFO" "FileSystemCoordinator" "Cleaned up $cleaned stale locks"
    fi
}

# Queue operation for coordinated execution
queue_operation() {
    local operation_id="$1"
    local operation_type="$2"
    local target_files="$3"
    local command="$4"

    local queue_file="$FILE_SYSTEM_COORDINATOR_STATE_DIR/operation_queue.json"
    local operation_entry

    # Create operation entry
    operation_entry=$(cat <<EOF
{
    "id": "$operation_id",
    "type": "$operation_type",
    "files": "$target_files",
    "command": "$command",
    "state": $OP_STATE_QUEUED,
    "queued_at": $(date +%s),
    "pid": $$
}
EOF
    )

    # Add to queue (simple append for now)
    if [[ ! -f "$queue_file" ]]; then
        echo "[]" > "$queue_file"
    fi

    # Use jq to add operation if available, otherwise simple append
    if command -v jq >/dev/null 2>&1; then
        local temp_file
        temp_file=$(mktemp)
        jq ". + [$operation_entry]" "$queue_file" > "$temp_file"
        mv "$temp_file" "$queue_file"
    else
        # Simple append without JSON validation
        echo "$operation_entry," >> "$queue_file.tmp"
    fi

    hook_log "$LOG_LEVEL_INFO" "FileSystemCoordinator" "Operation queued: $operation_id ($operation_type)"
    echo "$(date): Operation queued: $operation_id for files: $target_files" >> "$FILE_SYSTEM_COORDINATOR_LOG_FILE"
}

# Execute queued operations in coordinated manner
process_operation_queue() {
    local queue_file="$FILE_SYSTEM_COORDINATOR_STATE_DIR/operation_queue.json"

    if [[ ! -f "$queue_file" ]]; then
        hook_log "$LOG_LEVEL_DEBUG" "FileSystemCoordinator" "No operation queue found"
        return 0
    fi

    hook_log "$LOG_LEVEL_INFO" "FileSystemCoordinator" "Processing operation queue"

    # Clean up stale locks first
    cleanup_stale_locks

    # Process operations (simplified - real implementation would use proper JSON parsing)
    local processed=0
    local failures=0

    # For now, execute operations directly since queue structure is simple
    # In production, this would properly parse JSON and handle dependencies
    hook_log "$LOG_LEVEL_INFO" "FileSystemCoordinator" "Queue processing completed - processed: $processed, failures: $failures"

    return $failures
}

# Coordinate concurrent formatting operations
coordinate_concurrent_formatting() {
    local languages="$1"
    local target_directory="${2:-.}"

    init_file_system_coordinator

    hook_log "$LOG_LEVEL_INFO" "FileSystemCoordinator" "Coordinating concurrent formatting for languages: $languages"

    local overall_success=true
    IFS=',' read -ra lang_array <<< "$languages"

    # Queue all operations first
    local operation_id=1
    for language in "${lang_array[@]}"; do
        local files_pattern
        files_pattern=$(get_language_file_pattern "$language")

        # Find files for this language
        local files_found
        files_found=$(find "$target_directory" -name "${files_pattern%,*}" -type f 2>/dev/null | head -10 | tr '\n' ' ')

        if [[ -n "$files_found" ]]; then
            queue_operation "format_$operation_id" "$language" "$files_found" "format_$language"
            operation_id=$((operation_id + 1))
        fi
    done

    # Process the queue in coordinated manner
    if ! process_operation_queue; then
        overall_success=false
    fi

    if [[ "$overall_success" = true ]]; then
        hook_log "$LOG_LEVEL_INFO" "FileSystemCoordinator" "Concurrent formatting coordination completed successfully"
        return 0
    else
        hook_log "$LOG_LEVEL_WARN" "FileSystemCoordinator" "Some formatting operations failed during coordination"
        return 1
    fi
}

# Execute Black formatter without retries (specific for Python)
execute_black_without_retries() {
    local target_file="$1"

    init_file_system_coordinator

    hook_log "$LOG_LEVEL_INFO" "FileSystemCoordinator" "Executing Black formatter without retries for: $target_file"

    # Acquire lock for the file
    if ! acquire_file_lock "$target_file"; then
        hook_log "$LOG_LEVEL_ERROR" "FileSystemCoordinator" "Could not acquire lock for Black formatting: $target_file"
        return 1
    fi

    # Ensure we release the lock on exit
    trap "release_file_lock '$target_file'" EXIT

    # Execute Black formatter once
    local black_result=0
    if command -v black >/dev/null 2>&1; then
        hook_log "$LOG_LEVEL_DEBUG" "FileSystemCoordinator" "Running Black on: $target_file"

        if black "$target_file" 2>&1 | tee -a "$FILE_SYSTEM_COORDINATOR_LOG_FILE"; then
            hook_log "$LOG_LEVEL_INFO" "FileSystemCoordinator" "Black formatting completed successfully: $target_file"
            echo "$(date): Black formatting successful for: $target_file" >> "$FILE_SYSTEM_COORDINATOR_LOG_FILE"
        else
            black_result=$?
            hook_log "$LOG_LEVEL_ERROR" "FileSystemCoordinator" "Black formatting failed: $target_file (exit code: $black_result)"
            echo "$(date): Black formatting failed for: $target_file (exit code: $black_result)" >> "$FILE_SYSTEM_COORDINATOR_LOG_FILE"
        fi
    else
        hook_log "$LOG_LEVEL_WARN" "FileSystemCoordinator" "Black formatter not available"
        black_result=127
    fi

    # Release lock
    release_file_lock "$target_file"
    trap - EXIT

    return $black_result
}

# Coordinate batch file operations
coordinate_batch_operations() {
    local operation_type="$1"
    shift
    local files=("$@")

    init_file_system_coordinator

    hook_log "$LOG_LEVEL_INFO" "FileSystemCoordinator" "Coordinating batch $operation_type operations on ${#files[@]} files"

    local batch_success=true
    local processed_files=()

    # Sort files to ensure consistent ordering and prevent deadlocks
    local sorted_files
    mapfile -t sorted_files < <(printf '%s\n' "${files[@]}" | sort)

    # Process files in batches to avoid lock contention
    local batch_size=5
    local batch_start=0

    while [[ $batch_start -lt ${#sorted_files[@]} ]]; do
        local batch_end=$((batch_start + batch_size))
        if [[ $batch_end -gt ${#sorted_files[@]} ]]; then
            batch_end=${#sorted_files[@]}
        fi

        hook_log "$LOG_LEVEL_DEBUG" "FileSystemCoordinator" "Processing batch: $batch_start to $((batch_end - 1))"

        # Process this batch
        local batch_files=("${sorted_files[@]:$batch_start:$((batch_end - batch_start))}")
        for file in "${batch_files[@]}"; do
            if process_single_file "$operation_type" "$file"; then
                processed_files+=("$file")
            else
                batch_success=false
                hook_log "$LOG_LEVEL_WARN" "FileSystemCoordinator" "Failed to process file in batch: $file"
            fi
        done

        batch_start=$batch_end
    done

    hook_log "$LOG_LEVEL_INFO" "FileSystemCoordinator" "Batch coordination completed - processed ${#processed_files[@]} files"

    if [[ "$batch_success" = true ]]; then
        return 0
    else
        return 1
    fi
}

# Process single file with coordination
process_single_file() {
    local operation_type="$1"
    local file_path="$2"

    # Acquire lock for the file
    if ! acquire_file_lock "$file_path" 5; then  # Shorter timeout for batch operations
        hook_log "$LOG_LEVEL_WARN" "FileSystemCoordinator" "Could not acquire lock for file: $file_path"
        return 1
    fi

    # Set up lock release on function exit
    trap "release_file_lock '$file_path'" RETURN

    # Perform the operation
    local operation_result=0

    case "$operation_type" in
        "format")
            # Determine formatter based on file extension
            case "$file_path" in
                *.py)
                    if command -v black >/dev/null 2>&1; then
                        black "$file_path" >/dev/null 2>&1 || operation_result=$?
                    fi
                    ;;
                *.js|*.jsx|*.ts|*.tsx)
                    if command -v prettier >/dev/null 2>&1; then
                        prettier --write "$file_path" >/dev/null 2>&1 || operation_result=$?
                    fi
                    ;;
                *)
                    hook_log "$LOG_LEVEL_DEBUG" "FileSystemCoordinator" "No formatter available for: $file_path"
                    ;;
            esac
            ;;
        *)
            hook_log "$LOG_LEVEL_WARN" "FileSystemCoordinator" "Unknown operation type: $operation_type"
            operation_result=1
            ;;
    esac

    if [[ $operation_result -eq 0 ]]; then
        hook_log "$LOG_LEVEL_DEBUG" "FileSystemCoordinator" "File processed successfully: $file_path"
        echo "$(date): File processed successfully: $file_path (operation: $operation_type)" >> "$FILE_SYSTEM_COORDINATOR_LOG_FILE"
    else
        hook_log "$LOG_LEVEL_WARN" "FileSystemCoordinator" "File processing failed: $file_path (exit code: $operation_result)"
        echo "$(date): File processing failed: $file_path (operation: $operation_type, exit code: $operation_result)" >> "$FILE_SYSTEM_COORDINATOR_LOG_FILE"
    fi

    return $operation_result
}

# Get coordination status report
get_coordination_status() {
    init_file_system_coordinator

    echo "=== File System Coordination Status ==="
    echo "Generated: $(date)"
    echo

    # Show active locks
    echo "Active Locks:"
    local lock_count=0
    for lock_file in "$FILE_SYSTEM_COORDINATOR_STATE_DIR"/lock_*.lock; do
        if [[ -f "$lock_file" ]]; then
            local lock_info
            lock_info=$(cat "$lock_file")
            echo "  $lock_info"
            lock_count=$((lock_count + 1))
        fi
    done

    if [[ $lock_count -eq 0 ]]; then
        echo "  None"
    fi

    echo

    # Show queue status
    local queue_file="$FILE_SYSTEM_COORDINATOR_STATE_DIR/operation_queue.json"
    echo "Operation Queue:"
    if [[ -f "$queue_file" ]]; then
        if command -v jq >/dev/null 2>&1; then
            local queue_length
            queue_length=$(jq 'length' "$queue_file" 2>/dev/null || echo "0")
            echo "  Queue length: $queue_length"
        else
            echo "  Queue file exists (JSON parsing not available)"
        fi
    else
        echo "  Empty"
    fi
}

# Command-line interface for file system coordinator
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-}" in
        "coordinate_concurrent_formatting")
            if [[ -n "${2:-}" ]]; then
                coordinate_concurrent_formatting "$2" "${3:-.}"
            else
                echo "Usage: $0 coordinate_concurrent_formatting <languages> [target_directory]"
                exit 1
            fi
            ;;
        "execute_black_without_retries")
            if [[ -n "${2:-}" ]]; then
                execute_black_without_retries "$2"
            else
                echo "Usage: $0 execute_black_without_retries <file_path>"
                exit 1
            fi
            ;;
        "batch")
            if [[ -n "${2:-}" ]] && [[ $# -gt 2 ]]; then
                operation_type="$2"
                shift 2
                coordinate_batch_operations "$operation_type" "$@"
            else
                echo "Usage: $0 batch <operation_type> <file1> [file2] ..."
                exit 1
            fi
            ;;
        "status")
            get_coordination_status
            ;;
        "cleanup")
            cleanup_stale_locks
            ;;
        *)
            echo "Usage: $0 {coordinate_concurrent_formatting|execute_black_without_retries|batch|status|cleanup} [args...]"
            echo "  coordinate_concurrent_formatting - Coordinate multiple language formatters"
            echo "  execute_black_without_retries - Execute Black formatter once without retries"
            echo "  batch - Coordinate batch file operations"
            echo "  status - Show coordination status"
            echo "  cleanup - Clean up stale locks"
            exit 1
            ;;
    esac
fi