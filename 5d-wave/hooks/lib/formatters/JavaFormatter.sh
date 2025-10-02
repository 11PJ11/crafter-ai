#!/bin/bash
# AI-Craft Framework - Managed File
# Part of Claude Code SuperClaude modular hook system
# JavaFormatter - Java language formatter strategy
# Part of Claude Code SuperClaude modular hook system

set -euo pipefail

# Source dependencies
HOOK_LIB_DIR="$(dirname "${BASH_SOURCE[0]}")/.."
source "${HOOK_LIB_DIR}/formatters/BaseFormatter.sh"

# Override base formatter functions

get_formatter_name() {
    echo "JavaFormatter"
}

get_file_patterns() {
    echo "*.java"
}

get_required_tools() {
    echo "google-java-format:url:https://github.com/google/google-java-format spotbugs:url:https://spotbugs.github.io/"
}

can_format_language() {
    local language="$1"
    [[ "$language" = "java" ]]
}

format_files() {
    local language="$1"

    if ! can_format_language "$language"; then
        hook_log "$LOG_LEVEL_ERROR" "JavaFormatter" "Cannot format language: $language"
        return 1
    fi

    hook_log "$LOG_LEVEL_INFO" "JavaFormatter" "Starting Java formatting"

    # Check if Java files exist
    if ! has_files_for_patterns "$(get_file_patterns)"; then
        hook_log "$LOG_LEVEL_DEBUG" "JavaFormatter" "No Java files found"
        return 0
    fi

    # Find and format Java files
    local files_found=()
    while IFS= read -r -d '' file; do
        files_found+=("$file")
    done < <(find_files_to_format "$(get_file_patterns)")

    if [[ ${#files_found[@]} -eq 0 ]]; then
        hook_log "$LOG_LEVEL_DEBUG" "JavaFormatter" "No Java files found to format"
        return 0
    fi

    hook_log "$LOG_LEVEL_INFO" "JavaFormatter" "Processing ${#files_found[@]} Java files"

    local formatted_count=0
    local validated_count=0
    local success=true

    # Format with google-java-format if available
    if command -v google-java-format &> /dev/null; then
        local gjf_version=$(google-java-format --version 2>/dev/null || echo "unknown")
        hook_log "$LOG_LEVEL_INFO" "JavaFormatter" "Using google-java-format: $gjf_version"

        for file in "${files_found[@]}"; do
            if [[ ! -f "$file" ]]; then
                hook_log "$LOG_LEVEL_WARN" "JavaFormatter" "File not found: $file"
                continue
            fi

            if [[ ! -r "$file" ]]; then
                hook_log "$LOG_LEVEL_WARN" "JavaFormatter" "Cannot read file: $file"
                continue
            fi

            # Format with google-java-format (replace in-place)
            if google-java-format --replace "$file" 2>/dev/null; then
                hook_log "$LOG_LEVEL_DEBUG" "JavaFormatter" "Formatted: $file"
                ((formatted_count++))
            else
                hook_log "$LOG_LEVEL_ERROR" "JavaFormatter" "Failed to format: $file"
                success=false
            fi
        done
    else
        hook_log "$LOG_LEVEL_WARN" "JavaFormatter" "google-java-format not found, skipping formatting"
        hook_log "$LOG_LEVEL_INFO" "JavaFormatter" "Install from: https://github.com/google/google-java-format/releases"
    fi

    # Validate with basic compilation check if javac is available
    if command -v javac &> /dev/null; then
        local javac_version=$(javac -version 2>&1 | head -n1)
        hook_log "$LOG_LEVEL_INFO" "JavaFormatter" "Using javac: $javac_version"

        for file in "${files_found[@]}"; do
            if [[ ! -f "$file" ]]; then
                continue
            fi

            # Basic syntax validation (no output files, just check syntax)
            if javac -proc:none -Xlint:none "$file" -d /tmp 2>/dev/null; then
                hook_log "$LOG_LEVEL_DEBUG" "JavaFormatter" "Validated: $file"
                ((validated_count++))
                # Clean up any generated class files
                rm -f /tmp/*.class 2>/dev/null || true
            else
                hook_log "$LOG_LEVEL_WARN" "JavaFormatter" "Compilation warnings in: $file"
                # Don't fail on compilation warnings, just log them
            fi
        done
    else
        hook_log "$LOG_LEVEL_INFO" "JavaFormatter" "javac not found, skipping syntax validation"
        hook_log "$LOG_LEVEL_INFO" "JavaFormatter" "Install with: sudo apt install default-jdk"
    fi

    hook_log "$LOG_LEVEL_INFO" "JavaFormatter" "Java processing completed: $formatted_count formatted, $validated_count validated"

    if [[ "$success" == true ]]; then
        return 0
    else
        return 1
    fi
}

# Validate formatter setup
validate_formatter_setup() {
    local validation_success=true

    hook_log "$LOG_LEVEL_INFO" "JavaFormatter" "Validating Java formatter setup"

    # Check google-java-format availability
    if command -v google-java-format &> /dev/null; then
        local gjf_version=$(google-java-format --version 2>/dev/null || echo "unknown")
        hook_log "$LOG_LEVEL_INFO" "JavaFormatter" "google-java-format found: $gjf_version"

        # Test formatting functionality
        local test_java="public class Test { public static void main(String[] args) { System.out.println(\"Hello\"); } }"
        if echo "$test_java" | google-java-format - >/dev/null 2>&1; then
            hook_log "$LOG_LEVEL_INFO" "JavaFormatter" "google-java-format can process Java code"
        else
            hook_log "$LOG_LEVEL_ERROR" "JavaFormatter" "google-java-format test failed"
            validation_success=false
        fi
    else
        hook_log "$LOG_LEVEL_WARN" "JavaFormatter" "google-java-format not found"
        hook_log "$LOG_LEVEL_INFO" "JavaFormatter" "Download from: https://github.com/google/google-java-format/releases"
        hook_log "$LOG_LEVEL_INFO" "JavaFormatter" "Or install via package manager"
        validation_success=false
    fi

    # Check Java compiler availability (optional)
    if command -v javac &> /dev/null; then
        local javac_version=$(javac -version 2>&1 | head -n1)
        hook_log "$LOG_LEVEL_INFO" "JavaFormatter" "javac found: $javac_version"
    else
        hook_log "$LOG_LEVEL_INFO" "JavaFormatter" "javac not found (optional)"
        hook_log "$LOG_LEVEL_INFO" "JavaFormatter" "Install with: sudo apt install default-jdk"
    fi

    if [[ "$validation_success" == true ]]; then
        hook_log "$LOG_LEVEL_INFO" "JavaFormatter" "Java formatter validation passed"
        return 0
    else
        hook_log "$LOG_LEVEL_WARN" "JavaFormatter" "Java formatter validation had warnings"
        return 1
    fi
}