#!/bin/bash
# BaseFormatter - Base formatter interface and common functionality
# Part of Claude Code SuperClaude modular hook system

set -euo pipefail

# Source dependencies
HOOK_LIB_DIR="$(dirname "${BASH_SOURCE[0]}")/.."
source "${HOOK_LIB_DIR}/config/HookConfig.sh"
source "${HOOK_LIB_DIR}/logging/LogManager.sh"
source "${HOOK_LIB_DIR}/tools/ToolManager.sh"

# Base formatter interface
# Implementations should override these functions

# Get formatter name
get_formatter_name() {
    echo "BaseFormatter"
}

# Get supported file patterns
get_file_patterns() {
    echo "*.*"
}

# Get required tools with installation methods
get_required_tools() {
    # Format: tool_name:install_method:package_name
    # Example: "black:pipx:black prettier:npm:prettier"
    echo ""
}

# Format files for this language
format_files() {
    local language="$1"
    hook_log "$LOG_LEVEL_ERROR" "BaseFormatter" "format_files not implemented for $language"
    return 1
}

# Check if formatter can handle language
can_format_language() {
    local language="$1"
    hook_log "$LOG_LEVEL_DEBUG" "BaseFormatter" "Base implementation cannot format $language"
    return 1
}

# Common helper functions

# Find files for formatting
find_files_to_format() {
    local patterns="$1"
    local search_dirs=("." "src" "lib" "app" "tests" "test")

    hook_log "$LOG_LEVEL_DEBUG" "BaseFormatter" "Finding files with patterns: $patterns"

    local files_found=()
    IFS=',' read -ra pattern_array <<< "$patterns"

    for pattern in "${pattern_array[@]}"; do
        # Check each search directory
        for dir in "${search_dirs[@]}"; do
            if [[ -d "$dir" ]]; then
                while IFS= read -r -d '' file; do
                    files_found+=("$file")
                done < <(find "$dir" -name "$pattern" -type f -print0 2>/dev/null || true)
            fi
        done

        # Also check current directory
        while IFS= read -r -d '' file; do
            files_found+=("$file")
        done < <(find . -maxdepth 1 -name "$pattern" -type f -print0 2>/dev/null || true)
    done

    # Remove duplicates and print
    printf '%s\n' "${files_found[@]}" | sort -u
}

# Check if any files exist for patterns
has_files_for_patterns() {
    local patterns="$1"
    local file_count
    file_count=$(find_files_to_format "$patterns" | wc -l)
    [[ $file_count -gt 0 ]]
}

# Execute formatter command with error handling
execute_formatter() {
    local formatter_name="$1"
    local command="$2"
    local language="$3"

    hook_log "$LOG_LEVEL_INFO" "BaseFormatter" "Running $formatter_name for $language"
    hook_log "$LOG_LEVEL_DEBUG" "BaseFormatter" "Command: $command"

    if eval "$command"; then
        hook_log "$LOG_LEVEL_INFO" "BaseFormatter" "✅ $formatter_name completed successfully"
        return 0
    else
        local exit_code=$?
        hook_log "$LOG_LEVEL_WARN" "BaseFormatter" "❌ $formatter_name failed with exit code $exit_code"
        return $exit_code
    fi
}

# Ensure required tools are available
ensure_formatter_tools() {
    local required_tools="$1"
    local all_available=true

    if [[ -z "$required_tools" ]]; then
        hook_log "$LOG_LEVEL_DEBUG" "BaseFormatter" "No tools required"
        return 0
    fi

    hook_log "$LOG_LEVEL_DEBUG" "BaseFormatter" "Checking required tools: $required_tools"

    local tools_array
    read -ra tools_array <<< "$required_tools"

    for tool_spec in "${tools_array[@]}"; do
        local tool_name install_method package_name
        IFS=':' read -r tool_name install_method package_name <<< "$tool_spec"
        package_name="${package_name:-$tool_name}"

        if ! command -v "$tool_name" >/dev/null 2>&1; then
            hook_log "$LOG_LEVEL_WARN" "BaseFormatter" "Tool not found: $tool_name"

            # Try to install if not in CI
            if [[ "${CI:-false}" != "true" ]] && [[ -t 1 ]]; then
                if check_and_install_tool "$tool_name" "$install_method" "$package_name"; then
                    hook_log "$LOG_LEVEL_INFO" "BaseFormatter" "Successfully installed $tool_name"
                else
                    hook_log "$LOG_LEVEL_ERROR" "BaseFormatter" "Failed to install $tool_name"
                    all_available=false
                fi
            else
                all_available=false
            fi
        else
            hook_log "$LOG_LEVEL_DEBUG" "BaseFormatter" "Tool available: $tool_name"
        fi
    done

    if [[ "$all_available" = true ]]; then
        hook_log "$LOG_LEVEL_DEBUG" "BaseFormatter" "All required tools available"
        return 0
    else
        hook_log "$LOG_LEVEL_WARN" "BaseFormatter" "Some required tools missing"
        return 1
    fi
}