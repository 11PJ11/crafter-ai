#!/bin/bash
# AI-Craft Framework - Managed File
# Part of Claude Code SuperClaude modular hook system
# CppFormatter - C++ language formatter strategy
# Part of Claude Code SuperClaude modular hook system

set -euo pipefail

# Source dependencies
HOOK_LIB_DIR="$(dirname "${BASH_SOURCE[0]}")/.."
source "${HOOK_LIB_DIR}/formatters/BaseFormatter.sh"

# Override base formatter functions

get_formatter_name() {
    echo "CppFormatter"
}

get_file_patterns() {
    echo "*.cpp,*.cxx,*.cc,*.c,*.hpp,*.hxx,*.h,*.tpp,*.ipp"
}

get_required_tools() {
    echo "clang-format:system:clang-format"
}

can_format_language() {
    local language="$1"
    [[ "$language" = "cpp" ]]
}

format_files() {
    local language="$1"

    if ! can_format_language "$language"; then
        hook_log "$LOG_LEVEL_ERROR" "CppFormatter" "Cannot format language: $language"
        return 1
    fi

    hook_log "$LOG_LEVEL_INFO" "CppFormatter" "Starting C++ formatting"

    # Check if C++ files exist
    if ! has_files_for_patterns "$(get_file_patterns)"; then
        hook_log "$LOG_LEVEL_DEBUG" "CppFormatter" "No C++ files found"
        return 0
    fi

    # Check if clang-format is available
    if ! command -v clang-format &> /dev/null; then
        hook_log "$LOG_LEVEL_WARN" "CppFormatter" "clang-format not found, skipping C++ formatting"
        return 1
    fi

    # Get clang-format version for logging
    local version=$(clang-format --version 2>/dev/null | head -n1)
    hook_log "$LOG_LEVEL_INFO" "CppFormatter" "Using: $version"

    # Find and format C++ files
    local files_found=()
    while IFS= read -r -d '' file; do
        files_found+=("$file")
    done < <(find_files_to_format "$(get_file_patterns)")

    if [[ ${#files_found[@]} -eq 0 ]]; then
        hook_log "$LOG_LEVEL_DEBUG" "CppFormatter" "No C++ files found to format"
        return 0
    fi

    hook_log "$LOG_LEVEL_INFO" "CppFormatter" "Formatting ${#files_found[@]} C++ files"

    local formatted_count=0
    local success=true

    for file in "${files_found[@]}"; do
        if [[ ! -f "$file" ]]; then
            hook_log "$LOG_LEVEL_WARN" "CppFormatter" "File not found: $file"
            continue
        fi

        if [[ ! -r "$file" ]]; then
            hook_log "$LOG_LEVEL_WARN" "CppFormatter" "Cannot read file: $file"
            continue
        fi

        # Format the file in-place
        if clang-format -i "$file" 2>/dev/null; then
            hook_log "$LOG_LEVEL_DEBUG" "CppFormatter" "Formatted: $file"
            ((formatted_count++))
        else
            hook_log "$LOG_LEVEL_ERROR" "CppFormatter" "Failed to format: $file"
            success=false
        fi
    done

    hook_log "$LOG_LEVEL_INFO" "CppFormatter" "C++ formatting completed: $formatted_count/${#files_found[@]} files formatted"

    if [[ "$success" == true ]]; then
        return 0
    else
        return 1
    fi
}

# Validate formatter setup
validate_formatter_setup() {
    hook_log "$LOG_LEVEL_INFO" "CppFormatter" "Validating C++ formatter setup"

    if command -v clang-format &> /dev/null; then
        local version=$(clang-format --version 2>/dev/null | head -n1)
        hook_log "$LOG_LEVEL_INFO" "CppFormatter" "clang-format found: $version"
        return 0
    else
        hook_log "$LOG_LEVEL_ERROR" "CppFormatter" "clang-format not found"
        hook_log "$LOG_LEVEL_INFO" "CppFormatter" "Install with: sudo apt install clang-format (Ubuntu/Debian)"
        hook_log "$LOG_LEVEL_INFO" "CppFormatter" "Install with: brew install clang-format (macOS)"
        return 1
    fi
}