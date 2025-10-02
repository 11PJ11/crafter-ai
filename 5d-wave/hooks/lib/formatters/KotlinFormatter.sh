#!/bin/bash
# AI-Craft Framework - Managed File
# Part of Claude Code SuperClaude modular hook system
# KotlinFormatter - Kotlin language formatter strategy
# Part of Claude Code SuperClaude modular hook system

set -euo pipefail

# Source dependencies
HOOK_LIB_DIR="$(dirname "${BASH_SOURCE[0]}")/.."
source "${HOOK_LIB_DIR}/formatters/BaseFormatter.sh"

# Override base formatter functions

get_formatter_name() {
    echo "KotlinFormatter"
}

get_file_patterns() {
    echo "*.kt,*.kts"
}

get_required_tools() {
    echo "ktlint:curl:ktlint detekt:gradle:detekt-gradle-plugin"
}

can_format_language() {
    local language="$1"
    [[ "$language" = "kotlin" ]]
}

format_files() {
    local language="$1"

    if ! can_format_language "$language"; then
        hook_log "$LOG_LEVEL_ERROR" "KotlinFormatter" "Cannot format language: $language"
        return 1
    fi

    hook_log "$LOG_LEVEL_INFO" "KotlinFormatter" "Starting Kotlin formatting"

    # Check if Kotlin files exist
    if ! has_files_for_patterns "$(get_file_patterns)"; then
        hook_log "$LOG_LEVEL_DEBUG" "KotlinFormatter" "No Kotlin files found"
        return 0
    fi

    # Find and format Kotlin files
    local files_found=()
    while IFS= read -r -d '' file; do
        files_found+=("$file")
    done < <(find_files_to_format "$(get_file_patterns)")

    if [[ ${#files_found[@]} -eq 0 ]]; then
        hook_log "$LOG_LEVEL_DEBUG" "KotlinFormatter" "No Kotlin files found to format"
        return 0
    fi

    hook_log "$LOG_LEVEL_INFO" "KotlinFormatter" "Processing ${#files_found[@]} Kotlin files"

    local formatted_count=0
    local success=true

    # Format with ktlint if available
    if command -v ktlint &> /dev/null; then
        local ktlint_version=$(ktlint --version 2>/dev/null || echo "unknown")
        hook_log "$LOG_LEVEL_INFO" "KotlinFormatter" "Using ktlint: $ktlint_version"

        # Format all files with ktlint (auto-fix mode)
        if ktlint --format "${files_found[@]}" 2>/dev/null; then
            hook_log "$LOG_LEVEL_DEBUG" "KotlinFormatter" "Formatted ${#files_found[@]} Kotlin files"
            formatted_count=${#files_found[@]}
        else
            # Try formatting individual files if batch fails
            for file in "${files_found[@]}"; do
                if [[ ! -f "$file" ]]; then
                    hook_log "$LOG_LEVEL_WARN" "KotlinFormatter" "File not found: $file"
                    continue
                fi

                if [[ ! -r "$file" ]]; then
                    hook_log "$LOG_LEVEL_WARN" "KotlinFormatter" "Cannot read file: $file"
                    continue
                fi

                # Format individual file
                if ktlint --format "$file" 2>/dev/null; then
                    hook_log "$LOG_LEVEL_DEBUG" "KotlinFormatter" "Formatted: $file"
                    ((formatted_count++))
                else
                    hook_log "$LOG_LEVEL_ERROR" "KotlinFormatter" "Failed to format: $file"
                    success=false
                fi
            done
        fi
    else
        hook_log "$LOG_LEVEL_WARN" "KotlinFormatter" "ktlint not found, skipping formatting"
        hook_log "$LOG_LEVEL_INFO" "KotlinFormatter" "Install from: https://github.com/pinterest/ktlint/releases"
        hook_log "$LOG_LEVEL_INFO" "KotlinFormatter" "Or with: curl -sSLO https://github.com/pinterest/ktlint/releases/latest/download/ktlint && chmod a+x ktlint"
    fi

    hook_log "$LOG_LEVEL_INFO" "KotlinFormatter" "Kotlin processing completed: $formatted_count formatted"

    if [[ "$success" == true ]]; then
        return 0
    else
        return 1
    fi
}

# Validate formatter setup
validate_formatter_setup() {
    local validation_success=true

    hook_log "$LOG_LEVEL_INFO" "KotlinFormatter" "Validating Kotlin formatter setup"

    # Check ktlint availability
    if command -v ktlint &> /dev/null; then
        local ktlint_version=$(ktlint --version 2>/dev/null || echo "unknown")
        hook_log "$LOG_LEVEL_INFO" "KotlinFormatter" "ktlint found: $ktlint_version"

        # Test ktlint functionality
        local test_kotlin="fun main() { println(\"Hello\") }"
        if echo "$test_kotlin" | ktlint --stdin 2>/dev/null >/dev/null; then
            hook_log "$LOG_LEVEL_INFO" "KotlinFormatter" "ktlint can process Kotlin code"
        else
            hook_log "$LOG_LEVEL_ERROR" "KotlinFormatter" "ktlint test failed"
            validation_success=false
        fi
    else
        hook_log "$LOG_LEVEL_WARN" "KotlinFormatter" "ktlint not found"
        hook_log "$LOG_LEVEL_INFO" "KotlinFormatter" "Download from: https://github.com/pinterest/ktlint/releases"
        hook_log "$LOG_LEVEL_INFO" "KotlinFormatter" "Install with: curl -sSLO https://github.com/pinterest/ktlint/releases/latest/download/ktlint && chmod a+x ktlint && sudo mv ktlint /usr/local/bin/"
        validation_success=false
    fi

    # Check if Kotlin compiler is available (optional)
    if command -v kotlinc &> /dev/null; then
        local kotlinc_version=$(kotlinc -version 2>&1 | head -n1 || echo "unknown")
        hook_log "$LOG_LEVEL_INFO" "KotlinFormatter" "kotlinc found: $kotlinc_version"
    else
        hook_log "$LOG_LEVEL_INFO" "KotlinFormatter" "kotlinc not found (optional)"
        hook_log "$LOG_LEVEL_INFO" "KotlinFormatter" "Install from: https://kotlinlang.org/docs/command-line.html"
    fi

    if [[ "$validation_success" == true ]]; then
        hook_log "$LOG_LEVEL_INFO" "KotlinFormatter" "Kotlin formatter validation passed"
        return 0
    else
        hook_log "$LOG_LEVEL_WARN" "KotlinFormatter" "Kotlin formatter validation had warnings"
        return 1
    fi
}