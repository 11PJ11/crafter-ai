#!/bin/bash
# Craft-AI Stage Transition Hook - Modular Architecture
# Handles automatic stage transitions in ATDD workflow
# Only processes CAI workflows

set -euo pipefail

# Source modular hook system
HOOK_DIR="$(dirname "${BASH_SOURCE[0]}")/.."
source "${HOOK_DIR}/lib/HookManager.sh"

# Initialize hook system
if ! init_hook_system; then
    hook_log "$LOG_LEVEL_ERROR" "StageTransition" "Failed to initialize hook system"
    exit 1
fi

# Configuration constants
readonly DEFAULT_STATE='{"stage":"DISCUSS","agent":"business-analyst","status":"pending"}'
readonly STATE_FILE="state/craft-ai/pipeline-state.json"
readonly LOG_FILE="state/craft-ai/stage-transitions.log"
readonly WAVE_FILE="state/craft-ai/wave-progress.json"

# CAI Workflow Detection Strategy
class_cai_workflow_detector() {
    local strategy="$1"

    case "$strategy" in
        "environment")
            [[ "${CAI_WORKFLOW_ACTIVE:-}" = "true" ]]
            ;;
        "pipeline_state")
            [[ -f "$STATE_FILE" ]]
            ;;
        "agent_context")
            [[ "${ACTIVE_AGENT:-}" =~ ^(acceptance-designer|test-first-developer|solution-architect|business-analyst)$ ]]
            ;;
        *)
            hook_log "$LOG_LEVEL_ERROR" "StageTransition" "Unknown CAI detection strategy: $strategy"
            return 1
            ;;
    esac
}

# CAI Workflow Detection Facade
is_cai_workflow_active() {
    class_cai_workflow_detector "environment" || \
    class_cai_workflow_detector "pipeline_state" || \
    class_cai_workflow_detector "agent_context"
}

# Pipeline State Management Strategy
class_pipeline_state_manager() {
    local strategy="$1"
    shift

    case "$strategy" in
        "load_default")
            echo "$DEFAULT_STATE"
            ;;
        "load_file")
            if [[ -f "$STATE_FILE" ]]; then
                cat "$STATE_FILE"
            else
                echo "$DEFAULT_STATE"
            fi
            ;;
        "update")
            local new_stage="$1"
            local new_agent="$2"
            mkdir -p "state/craft-ai"
            python3 "$HOME/.claude/hooks/cai/workflow/json-utils.py" update-pipeline "$new_stage" "$new_agent"
            ;;
        "get_field")
            local field="$1"
            local default="${2:-}"
            python3 "$HOME/.claude/hooks/cai/workflow/json-utils.py" get "$STATE_FILE" "$field" "$default"
            ;;
        *)
            hook_log "$LOG_LEVEL_ERROR" "StageTransition" "Unknown pipeline state strategy: $strategy"
            return 1
            ;;
    esac
}

# Pipeline State Management Facade
load_pipeline_state() {
    class_pipeline_state_manager "load_file"
}

update_pipeline_state() {
    local new_stage="$1"
    local new_agent="$2"
    class_pipeline_state_manager "update" "$new_stage" "$new_agent"
}

get_pipeline_field() {
    local field="$1"
    local default="${2:-}"
    class_pipeline_state_manager "get_field" "$field" "$default"
}

# Stage Completion Validator Factory
create_stage_completion_validator() {
    local stage="$1"

    case "$stage" in
        "DISCUSS")
            echo "docs/craft-ai/requirements.md"
            ;;
        "ARCHITECT")
            echo "docs/craft-ai/architecture.md docs/craft-ai/technology-decisions.md"
            ;;
        "DISTILL")
            echo "docs/craft-ai/acceptance-tests.md"
            ;;
        "DEVELOP")
            echo "docs/craft-ai/implementation-status.md"
            ;;
        "DEMO")
            # DEMO is final stage
            return 1
            ;;
        *)
            hook_log "$LOG_LEVEL_WARN" "StageTransition" "Unknown stage completion validator: $stage"
            return 1
            ;;
    esac
}

# Stage Completion Validation Strategy
class_stage_completion_validator() {
    local strategy="$1"
    local stage="$2"

    case "$strategy" in
        "file_existence")
            local required_files=($(create_stage_completion_validator "$stage" 2>/dev/null))
            if [[ ${#required_files[@]} -eq 0 ]]; then
                return 1  # No files required or invalid stage
            fi

            for file in "${required_files[@]}"; do
                if [[ ! -f "$file" ]] || [[ ! -s "$file" ]]; then
                    return 1  # File missing or empty
                fi
            done
            return 0  # All required files exist and non-empty
            ;;
        *)
            hook_log "$LOG_LEVEL_ERROR" "StageTransition" "Unknown completion validation strategy: $strategy"
            return 1
            ;;
    esac
}

# Stage Completion Validation Facade
check_stage_completion() {
    local current_stage="$1"
    class_stage_completion_validator "file_existence" "$current_stage"
}

# Stage Transition Factory
create_stage_transition() {
    local current_stage="$1"

    case "$current_stage" in
        "DISCUSS")
            echo "ARCHITECT solution-architect"
            ;;
        "ARCHITECT")
            echo "DISTILL acceptance-designer"
            ;;
        "DISTILL")
            echo "DEVELOP test-first-developer"
            ;;
        "DEVELOP")
            echo "DEMO feature-completion-coordinator"
            ;;
        *)
            echo ""
            ;;
    esac
}

# Agent Notification Strategy
class_agent_notifier() {
    local strategy="$1"
    local stage="$2"
    local agent="$3"

    case "$strategy" in
        "console_notification")
            hook_log "$LOG_LEVEL_INFO" "StageTransition" "🔄 ATDD Stage Transition: $stage"
            hook_log "$LOG_LEVEL_INFO" "StageTransition" "🤖 Next Agent: $agent"
            hook_log "$LOG_LEVEL_INFO" "StageTransition" "📁 Expected inputs available for $stage stage"
            hook_log "$LOG_LEVEL_INFO" "StageTransition" ""
            hook_log "$LOG_LEVEL_INFO" "StageTransition" "You can now invoke the $agent for the $stage stage."
            hook_log "$LOG_LEVEL_INFO" "StageTransition" "The agent will have access to the required input files and"
            hook_log "$LOG_LEVEL_INFO" "StageTransition" "will be configured to produce the appropriate outputs."
            ;;
        "environment_setup")
            export ATDD_STAGE="$stage"
            export ACTIVE_AGENT="$agent"
            ;;
        *)
            hook_log "$LOG_LEVEL_ERROR" "StageTransition" "Unknown agent notification strategy: $strategy"
            return 1
            ;;
    esac
}

# Agent Notification Facade
trigger_next_agent() {
    local stage="$1"
    local agent="$2"
    class_agent_notifier "console_notification" "$stage" "$agent"
    class_agent_notifier "environment_setup" "$stage" "$agent"
}

# Transition Logging Strategy
class_transition_logger() {
    local strategy="$1"
    local from_stage="$2"
    local to_stage="$3"
    local agent="$4"
    local reason="$5"

    case "$strategy" in
        "stage_log")
            local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
            mkdir -p "state/craft-ai"
            echo "[$timestamp] STAGE_TRANSITION: $from_stage → $to_stage (agent: $agent, reason: $reason)" >> "$LOG_FILE"
            ;;
        "wave_progress")
            if [[ -f "$WAVE_FILE" ]]; then
                python3 "$HOME/.claude/hooks/cai/workflow/json-utils.py" update-wave "$to_stage" "$agent"
            fi
            ;;
        *)
            hook_log "$LOG_LEVEL_ERROR" "StageTransition" "Unknown transition logging strategy: $strategy"
            return 1
            ;;
    esac
}

# Transition Logging Facade
log_stage_transition() {
    local from_stage="$1"
    local to_stage="$2"
    local agent="$3"
    local reason="$4"

    class_transition_logger "stage_log" "$from_stage" "$to_stage" "$agent" "$reason"
    class_transition_logger "wave_progress" "$from_stage" "$to_stage" "$agent" "$reason"
}

# File Validation Factory
create_file_validator() {
    local stage="$1"

    case "$stage" in
        "DISCUSS")
            echo "(requirements|stakeholder|business-constraints|user-stories)\.md$"
            ;;
        "ARCHITECT")
            echo "(architecture|technology-decisions|component-design)\.md$"
            ;;
        "DISTILL")
            echo "(acceptance-tests|test-scenarios|validation-criteria)\.md$"
            ;;
        "DEVELOP")
            echo "(implementation-status|development-log|quality-report)\.md$"
            ;;
        "DEMO")
            echo "(demo-report|completion-status|handover)\.md$"
            ;;
        *)
            hook_log "$LOG_LEVEL_WARN" "StageTransition" "Unknown file validation pattern for stage: $stage"
            echo ".*\.md$"  # Default pattern
            ;;
    esac
}

# File Validation Strategy
class_file_validator() {
    local strategy="$1"
    local current_stage="$2"
    local file_written="$3"

    case "$strategy" in
        "stage_appropriate")
            local pattern=$(create_file_validator "$current_stage")
            [[ "$file_written" =~ $pattern ]]
            ;;
        *)
            hook_log "$LOG_LEVEL_ERROR" "StageTransition" "Unknown file validation strategy: $strategy"
            return 1
            ;;
    esac
}

# File Validation Facade
validate_transition() {
    local current_stage="$1"
    local file_written="$2"
    class_file_validator "stage_appropriate" "$current_stage" "$file_written"
}

# File Path Extraction Strategy
class_file_extractor() {
    local strategy="$1"
    shift

    case "$strategy" in
        "environment")
            echo "${CLAUDE_WRITE_FILE:-}"
            ;;
        "argument")
            echo "${1:-}"
            ;;
        *)
            hook_log "$LOG_LEVEL_ERROR" "StageTransition" "Unknown file extraction strategy: $strategy"
            return 1
            ;;
    esac
}

# File Path Extraction Facade
extract_written_file() {
    local file_path

    # Try environment variable first
    if file_path=$(class_file_extractor "environment") && [[ -n "$file_path" ]]; then
        echo "$file_path"
        return 0
    fi

    # Try argument
    if file_path=$(class_file_extractor "argument" "${1:-}") && [[ -n "$file_path" ]]; then
        echo "$file_path"
        return 0
    fi

    echo ""
    return 1
}

# Main execution facade
main() {
    hook_log "$LOG_LEVEL_DEBUG" "StageTransition" "Starting ATDD stage transition analysis"

    # Only process CAI workflows
    if ! is_cai_workflow_active; then
        hook_log "$LOG_LEVEL_DEBUG" "StageTransition" "Non-CAI context detected, skipping stage transition"
        exit 0
    fi

    hook_log "$LOG_LEVEL_INFO" "StageTransition" "CAI workflow detected, processing stage transition"

    # Get file that was written
    local written_file
    if ! written_file=$(extract_written_file "$@"); then
        hook_log "$LOG_LEVEL_DEBUG" "StageTransition" "No file specified, skipping stage transition"
        exit 0
    fi

    # Skip if not a CAI file
    if [[ ! "$written_file" =~ craft-ai ]]; then
        hook_log "$LOG_LEVEL_DEBUG" "StageTransition" "Non-CAI file written, skipping stage transition"
        exit 0
    fi

    hook_log "$LOG_LEVEL_DEBUG" "StageTransition" "Processing CAI file: $written_file"

    # Load current pipeline state
    local current_stage=$(get_pipeline_field "stage" "DISCUSS")
    local current_agent=$(get_pipeline_field "agent" "business-analyst")

    hook_log "$LOG_LEVEL_INFO" "StageTransition" "Current ATDD stage: $current_stage (agent: $current_agent)"

    # Validate that the written file is appropriate for current stage
    if ! validate_transition "$current_stage" "$written_file"; then
        hook_log "$LOG_LEVEL_WARN" "StageTransition" "File $written_file may not be appropriate for $current_stage stage"
    fi

    # Check if current stage is complete
    if check_stage_completion "$current_stage"; then
        local next_info=$(create_stage_transition "$current_stage")

        if [[ -n "$next_info" ]]; then
            local next_stage=$(echo "$next_info" | cut -d' ' -f1)
            local next_agent=$(echo "$next_info" | cut -d' ' -f2)

            hook_log "$LOG_LEVEL_INFO" "StageTransition" "Stage $current_stage complete, transitioning to $next_stage"

            # Update pipeline state
            update_pipeline_state "$next_stage" "$next_agent"

            # Log transition
            log_stage_transition "$current_stage" "$next_stage" "$next_agent" "stage_completion"

            # Trigger next agent
            trigger_next_agent "$next_stage" "$next_agent"
        else
            hook_log "$LOG_LEVEL_INFO" "StageTransition" "✅ ATDD workflow complete! All stages finished."
            log_stage_transition "$current_stage" "COMPLETE" "none" "workflow_finished"
        fi
    else
        # Stage not complete, log activity
        hook_log "$LOG_LEVEL_DEBUG" "StageTransition" "Stage $current_stage still in progress"
        log_stage_transition "$current_stage" "$current_stage" "$current_agent" "stage_progress"
    fi

    exit 0
}

# Execute main function
main "$@"