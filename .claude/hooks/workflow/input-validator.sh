#!/bin/bash
# Craft-AI Input Validator Hook
# Validates agent file access for CAI workflows only
# Ensures agents read from correct input files

set -euo pipefail

# Function to check if this is a CAI agent context
is_cai_agent_active() {
    [[ "${CAI_WORKFLOW_ACTIVE:-}" = "true" ]] || \
    [[ "${ACTIVE_AGENT:-}" =~ ^(acceptance-designer|test-first-developer|solution-architect|business-analyst)$ ]] || \
    [[ -f "state/craft-ai/pipeline-state.json" ]]
}

# Function to get current ATDD stage
get_current_stage() {
    if [[ -f "state/craft-ai/pipeline-state.json" ]]; then
        python3 "$HOME/.claude/hooks/cai/workflow/json-utils.py" get "state/craft-ai/pipeline-state.json" "stage" "DISCUSS"
    else
        echo "DISCUSS"
    fi
}

# Function to validate file access
validate_file_access() {
    local file_path="$1"
    local current_stage=$(get_current_stage)

    # Define allowed input files per stage
    case "$current_stage" in
        "DISCUSS")
            allowed_inputs=("requirements.md" "stakeholder-analysis.md" "user-stories.md")
            ;;
        "ARCHITECT")
            allowed_inputs=("requirements.md" "business-constraints.md" "quality-attributes.md")
            ;;
        "DISTILL")
            allowed_inputs=("requirements.md" "architecture.md" "technology-decisions.md")
            ;;
        "DEVELOP")
            allowed_inputs=("acceptance-tests.md" "test-scenarios.md" "architecture.md" "validation-criteria.md")
            ;;
        "DEMO")
            allowed_inputs=("implementation-status.md" "development-log.md" "quality-report.md")
            ;;
        *)
            # Default: allow common files
            allowed_inputs=("requirements.md" "architecture.md" "acceptance-tests.md")
            ;;
    esac

    # Check if file is in docs/craft-ai/ directory
    if [[ "$file_path" =~ ^docs/craft-ai/ ]]; then
        local filename=$(basename "$file_path")

        # Check if file is allowed for current stage
        for allowed in "${allowed_inputs[@]}"; do
            if [[ "$filename" = "$allowed" ]]; then
                return 0  # Access allowed
            fi
        done

        # File not allowed for current stage
        echo "❌ CAI INPUT VALIDATION ERROR"
        echo "Agent in $current_stage stage cannot read: $file_path"
        echo "Allowed input files for $current_stage stage:"
        printf "  - docs/craft-ai/%s\n" "${allowed_inputs[@]}"
        echo ""
        echo "Please modify your request to read from appropriate input files."
        return 1
    fi

    # Allow reading non-CAI files (preserve other frameworks)
    if [[ ! "$file_path" =~ craft-ai ]]; then
        return 0
    fi

    # Default deny for other craft-ai files
    echo "⚠️  CAI ACCESS WARNING: Unusual file access detected: $file_path"
    return 0  # Allow but warn
}

# Main execution
main() {
    # Only validate if CAI agent is active
    if ! is_cai_agent_active; then
        exit 0  # Skip validation for non-CAI contexts
    fi

    # Get file path from environment or arguments
    local file_path=""

    # Check common environment variables that contain file paths
    if [[ -n "${CLAUDE_READ_FILE:-}" ]]; then
        file_path="$CLAUDE_READ_FILE"
    elif [[ -n "${TARGET_FILE:-}" ]]; then
        file_path="$TARGET_FILE"
    elif [[ $# -gt 0 ]]; then
        # Extract file path from arguments
        for arg in "$@"; do
            if [[ "$arg" =~ \.(md|json|yaml|yml|txt)$ ]]; then
                file_path="$arg"
                break
            fi
        done
    fi

    # Skip validation if no file path found
    if [[ -z "$file_path" ]]; then
        exit 0
    fi

    # Validate file access
    if ! validate_file_access "$file_path"; then
        exit 1  # Block invalid access
    fi

    # Log valid access
    if [[ -w "state/craft-ai" ]]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] INPUT VALIDATION: Allowed read access to $file_path (stage: $(get_current_stage))" >> "state/craft-ai/session.log"
    fi

    exit 0
}

# Execute main function
main "$@"