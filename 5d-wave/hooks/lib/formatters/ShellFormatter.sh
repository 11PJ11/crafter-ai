#!/bin/bash
# AI-Craft Framework - Managed File
# Part of Claude Code SuperClaude modular hook system
# ShellFormatter - Shell script formatter strategy
# Part of Claude Code SuperClaude modular hook system

set -euo pipefail

# Source dependencies
HOOK_LIB_DIR="$(dirname "${BASH_SOURCE[0]}")/.."
source "${HOOK_LIB_DIR}/formatters/BaseFormatter.sh"

# Override base formatter functions

get_formatter_name() {
    echo "ShellFormatter"
}

get_file_patterns() {
    echo "*.sh,*.bash,*.zsh,*.ksh"
}

get_required_tools() {
    echo "shfmt:go:mvdan.cc/sh/v3/cmd/shfmt shellcheck:system:shellcheck"
}

can_format_language() {
    local language="$1"
    [[ "$language" = "shell" ]]
}

format_files() {
    local language="$1"

    if ! can_format_language "$language"; then
        hook_log "$LOG_LEVEL_ERROR" "ShellFormatter" "Cannot format language: $language"
        return 1
    fi

    hook_log "$LOG_LEVEL_INFO" "ShellFormatter" "Starting shell script formatting"

    # Check if shell files exist
    if ! has_files_for_patterns "$(get_file_patterns)"; then
        hook_log "$LOG_LEVEL_DEBUG" "ShellFormatter" "No shell files found"
        return 0
    fi

    # Find and format shell files
    local files_found=()
    while IFS= read -r -d '' file; do
        files_found+=("$file")
    done < <(find_files_to_format "$(get_file_patterns)")

    if [[ ${#files_found[@]} -eq 0 ]]; then
        hook_log "$LOG_LEVEL_DEBUG" "ShellFormatter" "No shell files found to format"
        return 0
    fi

    hook_log "$LOG_LEVEL_INFO" "ShellFormatter" "Processing ${#files_found[@]} shell files"

    local formatted_count=0
    local validated_count=0
    local success=true

    # Step 1: Format with shfmt if available
    if command -v shfmt &> /dev/null; then
        local shfmt_version=$(shfmt --version 2>/dev/null || echo "unknown")
        hook_log "$LOG_LEVEL_INFO" "ShellFormatter" "Using shfmt: $shfmt_version"

        for file in "${files_found[@]}"; do
            if [[ ! -f "$file" ]]; then
                hook_log "$LOG_LEVEL_WARN" "ShellFormatter" "File not found: $file"
                continue
            fi

            if [[ ! -r "$file" ]]; then
                hook_log "$LOG_LEVEL_WARN" "ShellFormatter" "Cannot read file: $file"
                continue
            fi

            # Format with shfmt (4-space indentation, simplified format)
            if shfmt -i 4 -s -w "$file" 2>/dev/null; then
                hook_log "$LOG_LEVEL_DEBUG" "ShellFormatter" "Formatted: $file"
                ((formatted_count++))
            else
                hook_log "$LOG_LEVEL_WARN" "ShellFormatter" "Failed to format: $file"
            fi
        done
    else
        hook_log "$LOG_LEVEL_WARN" "ShellFormatter" "shfmt not found, skipping formatting"
        hook_log "$LOG_LEVEL_INFO" "ShellFormatter" "Install with: go install mvdan.cc/sh/v3/cmd/shfmt@latest"
    fi

    # Step 2: Validate with shellcheck if available
    if command -v shellcheck &> /dev/null; then
        local shellcheck_version=$(shellcheck --version | grep version: | awk '{print $2}' 2>/dev/null || echo "unknown")
        hook_log "$LOG_LEVEL_INFO" "ShellFormatter" "Using shellcheck: v$shellcheck_version"

        for file in "${files_found[@]}"; do
            if [[ ! -f "$file" ]]; then
                continue
            fi

            # Validate with shellcheck (suppress common false positives)
            if shellcheck -e SC1091 -e SC2034 -e SC2155 "$file" 2>/dev/null; then
                hook_log "$LOG_LEVEL_DEBUG" "ShellFormatter" "Validated: $file"
                ((validated_count++))
            else
                hook_log "$LOG_LEVEL_WARN" "ShellFormatter" "Shellcheck warnings in: $file"
                # Don't fail on shellcheck warnings, just log them
            fi
        done
    else
        hook_log "$LOG_LEVEL_WARN" "ShellFormatter" "shellcheck not found, skipping validation"
        hook_log "$LOG_LEVEL_INFO" "ShellFormatter" "Install with: sudo apt install shellcheck (Ubuntu/Debian)"
    fi

    hook_log "$LOG_LEVEL_INFO" "ShellFormatter" "Shell processing completed: $formatted_count formatted, $validated_count validated"

    return 0  # Always succeed, warnings don't fail the process
}

# Validate formatter setup
validate_formatter_setup() {
    local validation_success=true

    hook_log "$LOG_LEVEL_INFO" "ShellFormatter" "Validating shell formatter setup"

    # Check shfmt availability
    if command -v shfmt &> /dev/null; then
        local shfmt_version=$(shfmt --version 2>/dev/null || echo "unknown")
        hook_log "$LOG_LEVEL_INFO" "ShellFormatter" "shfmt found: $shfmt_version"
    else
        hook_log "$LOG_LEVEL_WARN" "ShellFormatter" "shfmt not found"
        hook_log "$LOG_LEVEL_INFO" "ShellFormatter" "Install with: go install mvdan.cc/sh/v3/cmd/shfmt@latest"
        validation_success=false
    fi

    # Check shellcheck availability
    if command -v shellcheck &> /dev/null; then
        local shellcheck_version=$(shellcheck --version | grep version: | awk '{print $2}' 2>/dev/null || echo "unknown")
        hook_log "$LOG_LEVEL_INFO" "ShellFormatter" "shellcheck found: v$shellcheck_version"
    else
        hook_log "$LOG_LEVEL_WARN" "ShellFormatter" "shellcheck not found"
        hook_log "$LOG_LEVEL_INFO" "ShellFormatter" "Install with: sudo apt install shellcheck (Ubuntu/Debian)"
    fi

    # Test shfmt functionality if available
    if command -v shfmt &> /dev/null; then
        local test_script="#!/bin/bash\necho 'test'"
        if echo -e "$test_script" | shfmt -i 4 -s >/dev/null 2>&1; then
            hook_log "$LOG_LEVEL_INFO" "ShellFormatter" "shfmt can process shell scripts"
        else
            hook_log "$LOG_LEVEL_ERROR" "ShellFormatter" "shfmt test formatting failed"
            validation_success=false
        fi
    fi

    if [[ "$validation_success" == true ]]; then
        hook_log "$LOG_LEVEL_INFO" "ShellFormatter" "Shell formatter validation passed"
        return 0
    else
        hook_log "$LOG_LEVEL_WARN" "ShellFormatter" "Shell formatter validation had warnings"
        return 1
    fi
}