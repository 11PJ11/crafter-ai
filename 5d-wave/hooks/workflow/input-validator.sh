#!/bin/bash
# AI-Craft Framework - Managed File
# Part of Claude Code SuperClaude modular hook system
# Craft-AI Input Validator Hook - Modular Architecture
# Validates agent file access for CAI workflows only
# Ensures agents read from correct input files

set -euo pipefail

# Source modular hook system
HOOK_DIR="$(dirname "${BASH_SOURCE[0]}")/.."
source "${HOOK_DIR}/lib/HookManager.sh"

# Initialize hook system
if ! init_hook_system; then
    hook_log "$LOG_LEVEL_ERROR" "InputValidator" "Failed to initialize hook system"
    exit 1
fi

# CAI Agent Detection Strategy
class_cai_agent_detector() {
    local strategy="$1"

    case "$strategy" in
        "environment")
            [[ "${CAI_WORKFLOW_ACTIVE:-}" = "true" ]]
            ;;
        "agent_context")
            [[ "${ACTIVE_AGENT:-}" =~ ^(acceptance-designer|test-first-developer|solution-architect|business-analyst)$ ]]
            ;;
        "pipeline_state")
            [[ -f "state/craft-ai/pipeline-state.json" ]]
            ;;
        *)
            hook_log "$LOG_LEVEL_ERROR" "InputValidator" "Unknown CAI detection strategy: $strategy"
            return 1
            ;;
    esac
}

# CAI Agent Detection Facade
is_cai_agent_active() {
    class_cai_agent_detector "environment" || \
    class_cai_agent_detector "agent_context" || \
    class_cai_agent_detector "pipeline_state"
}

# ATDD Stage Reader Strategy
class_stage_reader() {
    local strategy="$1"

    case "$strategy" in
        "pipeline_state")
            if [[ -f "state/craft-ai/pipeline-state.json" ]]; then
                python3 "$HOME/.claude/hooks/cai/workflow/json-utils.py" get "state/craft-ai/pipeline-state.json" "stage" "$(get_config "DEFAULT_STAGE")"
            else
                return 1
            fi
            ;;
        "default")
            echo "DISCUSS"
            ;;
        *)
            hook_log "$LOG_LEVEL_ERROR" "InputValidator" "Unknown stage reader strategy: $strategy"
            return 1
            ;;
    esac
}

# ATDD Stage Reader Facade
get_current_stage() {
    local stage
    if stage=$(class_stage_reader "pipeline_state" 2>/dev/null); then
        echo "$stage"
    else
        echo "DISCUSS"  # Default stage
    fi
}

# File Access Validator Factory
create_stage_validator() {
    local stage="$1"

    case "$stage" in
        "DISCUSS")
            echo "requirements.md stakeholder-analysis.md user-stories.md"
            ;;
        "ARCHITECT")
            echo "requirements.md business-constraints.md quality-attributes.md"
            ;;
        "DISTILL")
            echo "requirements.md architecture.md technology-decisions.md"
            ;;
        "DEVELOP")
            echo "acceptance-tests.md test-scenarios.md architecture.md validation-criteria.md"
            ;;
        "DEMO")
            echo "implementation-status.md development-log.md quality-report.md"
            ;;
        *)
            hook_log "$LOG_LEVEL_WARN" "InputValidator" "Unknown stage '$stage', using default validation"
            echo "requirements.md architecture.md acceptance-tests.md"
            ;;
    esac
}

# File Access Validation Strategy
class_file_validator() {
    local strategy="$1"
    local file_path="$2"
    local current_stage="$3"

    case "$strategy" in
        "cai_directory")
            if [[ "$file_path" =~ ^docs/craft-ai/ ]]; then
                local filename=$(basename "$file_path")
                local allowed_inputs=($(create_stage_validator "$current_stage"))

                for allowed in "${allowed_inputs[@]}"; do
                    if [[ "$filename" = "$allowed" ]]; then
                        return 0  # Access allowed
                    fi
                done

                # File not allowed for current stage
                hook_log "$LOG_LEVEL_ERROR" "InputValidator" "CAI INPUT VALIDATION ERROR"
                hook_log "$LOG_LEVEL_ERROR" "InputValidator" "Agent in $current_stage stage cannot read: $file_path"
                hook_log "$LOG_LEVEL_INFO" "InputValidator" "Allowed input files for $current_stage stage:"
                for allowed in "${allowed_inputs[@]}"; do
                    hook_log "$LOG_LEVEL_INFO" "InputValidator" "  - docs/craft-ai/$allowed"
                done
                hook_log "$LOG_LEVEL_INFO" "InputValidator" ""
                hook_log "$LOG_LEVEL_INFO" "InputValidator" "Please modify your request to read from appropriate input files."
                return 1
            else
                return 1  # Not CAI directory
            fi
            ;;
        "non_cai")
            if [[ ! "$file_path" =~ craft-ai ]]; then
                return 0  # Allow non-CAI files
            else
                return 1  # Is CAI file
            fi
            ;;
        "cai_warning")
            hook_log "$LOG_LEVEL_WARN" "InputValidator" "CAI ACCESS WARNING: Unusual file access detected: $file_path"
            return 0  # Allow but warn
            ;;
        *)
            hook_log "$LOG_LEVEL_ERROR" "InputValidator" "Unknown validation strategy: $strategy"
            return 1
            ;;
    esac
}

# File Access Validation Facade
validate_file_access() {
    local file_path="$1"
    local current_stage=$(get_current_stage)

    # Check if file is in docs/craft-ai/ directory (strict validation)
    if [[ "$file_path" =~ ^docs/craft-ai/ ]]; then
        # Use CAI directory validation - this can return 1 for invalid files
        class_file_validator "cai_directory" "$file_path" "$current_stage"
        return $?
    fi

    # Check if it's a non-CAI file (allow these)
    if class_file_validator "non_cai" "$file_path" "$current_stage"; then
        return 0
    fi

    # Default: warn for other craft-ai files but allow
    class_file_validator "cai_warning" "$file_path" "$current_stage"
}

# File Path Extraction Strategy
class_path_extractor() {
    local strategy="$1"
    shift

    case "$strategy" in
        "claude_env")
            echo "${CLAUDE_READ_FILE:-}"
            ;;
        "target_env")
            echo "${TARGET_FILE:-}"
            ;;
        "argument_scan")
            for arg in "$@"; do
                if [[ "$arg" =~ \.(md|json|yaml|yml|txt)$ ]]; then
                    echo "$arg"
                    return 0
                fi
            done
            echo ""
            ;;
        *)
            hook_log "$LOG_LEVEL_ERROR" "InputValidator" "Unknown path extraction strategy: $strategy"
            return 1
            ;;
    esac
}

# File Path Extraction Facade
extract_file_path() {
    local file_path

    # Try environment variables first
    if file_path=$(class_path_extractor "claude_env") && [[ -n "$file_path" ]]; then
        echo "$file_path"
        return 0
    fi

    if file_path=$(class_path_extractor "target_env") && [[ -n "$file_path" ]]; then
        echo "$file_path"
        return 0
    fi

    # Try argument scanning
    if file_path=$(class_path_extractor "argument_scan" "$@") && [[ -n "$file_path" ]]; then
        echo "$file_path"
        return 0
    fi

    echo ""
    return 1
}

# Session Logging Strategy
log_validation_result() {
    local file_path="$1"
    local current_stage="$2"

    # Log to session log if available
    if [[ -w "state/craft-ai" ]]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] INPUT VALIDATION: Allowed read access to $file_path (stage: $current_stage)" >> "state/craft-ai/session.log"
    fi
}

# Main execution facade
main() {
    hook_log "$LOG_LEVEL_DEBUG" "InputValidator" "Starting CAI input validation"

    # Only validate if CAI agent is active
    if ! is_cai_agent_active; then
        hook_log "$LOG_LEVEL_DEBUG" "InputValidator" "Non-CAI context detected, skipping validation"
        exit 0
    fi

    hook_log "$LOG_LEVEL_INFO" "InputValidator" "CAI agent context detected, performing input validation"

    # Extract file path from environment or arguments
    local file_path
    if ! file_path=$(extract_file_path "$@"); then
        hook_log "$LOG_LEVEL_DEBUG" "InputValidator" "No file path found, skipping validation"
        exit 0
    fi

    hook_log "$LOG_LEVEL_DEBUG" "InputValidator" "Validating file access: $file_path"

    # Validate file access
    if ! validate_file_access "$file_path"; then
        hook_log "$LOG_LEVEL_ERROR" "InputValidator" "File access validation failed for: $file_path"
        exit 1
    fi

    # Log successful validation
    local current_stage=$(get_current_stage)
    log_validation_result "$file_path" "$current_stage"
    hook_log "$LOG_LEVEL_INFO" "InputValidator" "Input validation successful for: $file_path (stage: $current_stage)"

    exit 0
}

# Execute main function
main "$@"