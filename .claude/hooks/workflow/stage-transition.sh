#!/bin/bash
# Craft-AI Stage Transition Hook
# Handles automatic stage transitions in ATDD workflow
# Only processes CAI workflows

set -euo pipefail

# Function to check if CAI workflow is active
is_cai_workflow_active() {
    [[ "${CAI_WORKFLOW_ACTIVE:-}" = "true" ]] || \
    [[ -f "state/craft-ai/pipeline-state.json" ]] || \
    [[ "${ACTIVE_AGENT:-}" =~ ^(acceptance-designer|test-first-developer|solution-architect|business-analyst)$ ]]
}

# Function to load pipeline state
load_pipeline_state() {
    local state_file="state/craft-ai/pipeline-state.json"
    if [[ -f "$state_file" ]]; then
        cat "$state_file"
    else
        echo '{"stage":"DISCUSS","agent":"business-analyst","status":"pending"}'
    fi
}

# Function to update pipeline state
update_pipeline_state() {
    local new_stage="$1"
    local new_agent="$2"
    local state_file="state/craft-ai/pipeline-state.json"
    local temp_file=$(mktemp)

    # Create state directory if needed
    mkdir -p "state/craft-ai"

    # Update state using Python JSON utility
    python3 "$HOME/.claude/hooks/cai/workflow/json-utils.py" update-pipeline "$new_stage" "$new_agent"
}

# Function to check stage completion
check_stage_completion() {
    local current_stage="$1"

    case "$current_stage" in
        "DISCUSS")
            # Check for required DISCUSS outputs
            [[ -f "docs/craft-ai/requirements.md" ]] && \
            [[ -s "docs/craft-ai/requirements.md" ]]
            ;;
        "ARCHITECT")
            # Check for required ARCHITECT outputs
            [[ -f "docs/craft-ai/architecture.md" ]] && \
            [[ -s "docs/craft-ai/architecture.md" ]] && \
            [[ -f "docs/craft-ai/technology-decisions.md" ]]
            ;;
        "DISTILL")
            # Check for required DISTILL outputs
            [[ -f "docs/craft-ai/acceptance-tests.md" ]] && \
            [[ -s "docs/craft-ai/acceptance-tests.md" ]]
            ;;
        "DEVELOP")
            # Check for required DEVELOP outputs
            [[ -f "docs/craft-ai/implementation-status.md" ]] && \
            [[ -s "docs/craft-ai/implementation-status.md" ]]
            ;;
        "DEMO")
            # DEMO is final stage
            return 1
            ;;
        *)
            return 1
            ;;
    esac
}

# Function to get next stage and agent
get_next_stage() {
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

# Function to trigger next agent
trigger_next_agent() {
    local stage="$1"
    local agent="$2"

    echo "🔄 ATDD Stage Transition: $stage"
    echo "🤖 Next Agent: $agent"
    echo "📁 Expected inputs available for $stage stage"
    echo ""
    echo "You can now invoke the $agent for the $stage stage."
    echo "The agent will have access to the required input files and"
    echo "will be configured to produce the appropriate outputs."
}

# Function to log stage transition
log_stage_transition() {
    local from_stage="$1"
    local to_stage="$2"
    local agent="$3"
    local reason="$4"

    local log_file="state/craft-ai/stage-transitions.log"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    echo "[$timestamp] STAGE_TRANSITION: $from_stage → $to_stage (agent: $agent, reason: $reason)" >> "$log_file"

    # Also update wave progress if applicable
    if [[ -f "state/craft-ai/wave-progress.json" ]]; then
        python3 "$HOME/.claude/hooks/cai/workflow/json-utils.py" update-wave "$to_stage" "$agent"
    fi
}

# Function to validate transition
validate_transition() {
    local current_stage="$1"
    local file_written="$2"

    # Check if the written file is appropriate for the current stage
    case "$current_stage" in
        "DISCUSS")
            [[ "$file_written" =~ (requirements|stakeholder|business-constraints|user-stories)\.md$ ]]
            ;;
        "ARCHITECT")
            [[ "$file_written" =~ (architecture|technology-decisions|component-design)\.md$ ]]
            ;;
        "DISTILL")
            [[ "$file_written" =~ (acceptance-tests|test-scenarios|validation-criteria)\.md$ ]]
            ;;
        "DEVELOP")
            [[ "$file_written" =~ (implementation-status|development-log|quality-report)\.md$ ]]
            ;;
        "DEMO")
            [[ "$file_written" =~ (demo-report|completion-status|handover)\.md$ ]]
            ;;
        *)
            return 1
            ;;
    esac
}

# Main execution
main() {
    # Only process CAI workflows
    if ! is_cai_workflow_active; then
        exit 0  # Skip for non-CAI contexts
    fi

    # Get file that was written (from environment or arguments)
    local written_file=""
    if [[ -n "${CLAUDE_WRITE_FILE:-}" ]]; then
        written_file="$CLAUDE_WRITE_FILE"
    elif [[ $# -gt 0 ]]; then
        written_file="$1"
    fi

    # Skip if no file specified or not a CAI file
    if [[ -z "$written_file" ]] || [[ ! "$written_file" =~ craft-ai ]]; then
        exit 0
    fi

    # Load current pipeline state
    local current_stage=$(python3 "$HOME/.claude/hooks/cai/workflow/json-utils.py" get "state/craft-ai/pipeline-state.json" "stage" "DISCUSS")
    local current_agent=$(python3 "$HOME/.claude/hooks/cai/workflow/json-utils.py" get "state/craft-ai/pipeline-state.json" "agent" "business-analyst")

    # Validate that the written file is appropriate for current stage
    if ! validate_transition "$current_stage" "$written_file"; then
        echo "⚠️  Stage transition: File $written_file may not be appropriate for $current_stage stage"
    fi

    # Check if current stage is complete
    if check_stage_completion "$current_stage"; then
        local next_info=$(get_next_stage "$current_stage")

        if [[ -n "$next_info" ]]; then
            local next_stage=$(echo "$next_info" | cut -d' ' -f1)
            local next_agent=$(echo "$next_info" | cut -d' ' -f2)

            # Update pipeline state
            update_pipeline_state "$next_stage" "$next_agent"

            # Log transition
            log_stage_transition "$current_stage" "$next_stage" "$next_agent" "stage_completion"

            # Trigger next agent
            trigger_next_agent "$next_stage" "$next_agent"

            # Set environment for next agent
            export ATDD_STAGE="$next_stage"
            export ACTIVE_AGENT="$next_agent"
        else
            echo "✅ ATDD workflow complete! All stages finished."
            log_stage_transition "$current_stage" "COMPLETE" "none" "workflow_finished"
        fi
    else
        # Stage not complete, log activity
        log_stage_transition "$current_stage" "$current_stage" "$current_agent" "stage_progress"
    fi

    exit 0
}

# Execute main function
main "$@"