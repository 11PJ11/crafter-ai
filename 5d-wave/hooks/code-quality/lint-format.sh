#!/bin/bash
# AI-Craft Framework - Managed File
# Part of Claude Code SuperClaude modular hook system
# Enhanced Format and Lint Hook - Modular Version
# Part of Claude Code SuperClaude modular hook system
# Uses new modular architecture with Strategy pattern for formatters

set -euo pipefail

# Source modular hook system
HOOK_DIR="$(dirname "${BASH_SOURCE[0]}")/.."
source "${HOOK_DIR}/lib/HookManager.sh"

# Initialize hook system
if ! init_hook_system; then
    echo "❌ Failed to initialize hook system" >&2
    exit 1
fi

# Source formatter components
source "${HOOK_DIR}/lib/tools/LanguageDetector.sh"
source "${HOOK_DIR}/lib/tools/ToolManager.sh"
source "${HOOK_DIR}/lib/tools/JsonUtils.sh"
source "${HOOK_DIR}/lib/formatters/FormatterRegistry.sh"

# Configuration
readonly MSG_STARTING="🔧 Auto-formatting"
readonly MSG_COMPLETE="🎉 Auto-formatting complete"
readonly MSG_SKIPPED="⚠️  Skipping - unsupported file type or missing tools"

# Main formatting orchestrator
main() {
    hook_log "$LOG_LEVEL_INFO" "LintFormat" "$MSG_STARTING"

    # Setup tool paths
    setup_tool_paths

    # Initialize formatter registry
    init_formatter_registry

    # Detect project languages
    hook_log "$LOG_LEVEL_DEBUG" "LintFormat" "Detecting project languages"
    local languages
    mapfile -t languages < <(detect_project_languages)

    if [[ ${#languages[@]} -eq 0 ]]; then
        hook_log "$LOG_LEVEL_INFO" "LintFormat" "No supported languages detected"
        hook_log "$LOG_LEVEL_INFO" "LintFormat" "$MSG_SKIPPED"
        return 0
    fi

    hook_log "$LOG_LEVEL_INFO" "LintFormat" "Detected languages: ${languages[*]}"

    # Format each detected language using Strategy pattern
    local overall_success=true
    for language in "${languages[@]}"; do
        hook_log "$LOG_LEVEL_INFO" "LintFormat" "Processing language: $language"

        if is_language_supported "$language"; then
            if ! dispatch_formatter "$language"; then
                hook_log "$LOG_LEVEL_WARN" "LintFormat" "Formatting failed for $language"
                overall_success=false
            fi
        else
            hook_log "$LOG_LEVEL_DEBUG" "LintFormat" "Language not supported: $language"
        fi
    done

    # Report final status
    if [[ "$overall_success" = true ]]; then
        hook_log "$LOG_LEVEL_INFO" "LintFormat" "$MSG_COMPLETE"
        return 0
    else
        hook_log "$LOG_LEVEL_WARN" "LintFormat" "Some formatting operations failed"
        return 1
    fi
}

# Enhanced error handling
handle_error() {
    local exit_code=$?
    local line_number=$1
    hook_log "$LOG_LEVEL_ERROR" "LintFormat" "Error occurred at line $line_number (exit code: $exit_code)"
    exit $exit_code
}

# Set up error trap
trap 'handle_error $LINENO' ERR

# Execute main function
main "$@"