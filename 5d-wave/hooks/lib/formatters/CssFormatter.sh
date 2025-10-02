#!/bin/bash
# AI-Craft Framework - Managed File
# Part of Claude Code SuperClaude modular hook system
# CssFormatter - CSS/SCSS/Sass formatter strategy
# Part of Claude Code SuperClaude modular hook system

set -euo pipefail

# Source dependencies
HOOK_LIB_DIR="$(dirname "${BASH_SOURCE[0]}")/.."
source "${HOOK_LIB_DIR}/formatters/BaseFormatter.sh"

# Override base formatter functions

get_formatter_name() {
    echo "CssFormatter"
}

get_file_patterns() {
    echo "*.css,*.scss,*.sass,*.less"
}

get_required_tools() {
    echo "prettier:npm:prettier stylelint:npm:stylelint"
}

can_format_language() {
    local language="$1"
    [[ "$language" = "css" ]]
}

format_files() {
    local language="$1"

    if ! can_format_language "$language"; then
        hook_log "$LOG_LEVEL_ERROR" "CssFormatter" "Cannot format language: $language"
        return 1
    fi

    hook_log "$LOG_LEVEL_INFO" "CssFormatter" "Starting CSS/SCSS/Sass formatting"

    # Check if CSS files exist
    if ! has_files_for_patterns "$(get_file_patterns)"; then
        hook_log "$LOG_LEVEL_DEBUG" "CssFormatter" "No CSS files found"
        return 0
    fi

    # Find and format CSS files
    local files_found=()
    while IFS= read -r -d '' file; do
        files_found+=("$file")
    done < <(find_files_to_format "$(get_file_patterns)")

    if [[ ${#files_found[@]} -eq 0 ]]; then
        hook_log "$LOG_LEVEL_DEBUG" "CssFormatter" "No CSS files found to format"
        return 0
    fi

    hook_log "$LOG_LEVEL_INFO" "CssFormatter" "Processing ${#files_found[@]} CSS files"

    local formatted_count=0
    local linted_count=0
    local success=true

    # Step 1: Format with Prettier if available
    if command -v prettier &> /dev/null; then
        local prettier_version=$(prettier --version 2>/dev/null || echo "unknown")
        hook_log "$LOG_LEVEL_INFO" "CssFormatter" "Using Prettier: v$prettier_version"

        # Format all files in one command for efficiency
        local css_files=()
        local scss_files=()
        local sass_files=()
        local less_files=()

        for file in "${files_found[@]}"; do
            case "$file" in
                *.css) css_files+=("$file") ;;
                *.scss) scss_files+=("$file") ;;
                *.sass) sass_files+=("$file") ;;
                *.less) less_files+=("$file") ;;
            esac
        done

        # Format CSS files
        if [[ ${#css_files[@]} -gt 0 ]]; then
            if prettier --write "${css_files[@]}" 2>/dev/null; then
                hook_log "$LOG_LEVEL_DEBUG" "CssFormatter" "Formatted ${#css_files[@]} CSS files"
                ((formatted_count += ${#css_files[@]}))
            else
                hook_log "$LOG_LEVEL_WARN" "CssFormatter" "Failed to format some CSS files"
                success=false
            fi
        fi

        # Format SCSS files
        if [[ ${#scss_files[@]} -gt 0 ]]; then
            if prettier --write "${scss_files[@]}" 2>/dev/null; then
                hook_log "$LOG_LEVEL_DEBUG" "CssFormatter" "Formatted ${#scss_files[@]} SCSS files"
                ((formatted_count += ${#scss_files[@]}))
            else
                hook_log "$LOG_LEVEL_WARN" "CssFormatter" "Failed to format some SCSS files"
                success=false
            fi
        fi

        # Format Sass files (indented syntax)
        if [[ ${#sass_files[@]} -gt 0 ]]; then
            if prettier --write "${sass_files[@]}" 2>/dev/null; then
                hook_log "$LOG_LEVEL_DEBUG" "CssFormatter" "Formatted ${#sass_files[@]} Sass files"
                ((formatted_count += ${#sass_files[@]}))
            else
                hook_log "$LOG_LEVEL_WARN" "CssFormatter" "Failed to format some Sass files"
                success=false
            fi
        fi

        # Format Less files
        if [[ ${#less_files[@]} -gt 0 ]]; then
            if prettier --write "${less_files[@]}" 2>/dev/null; then
                hook_log "$LOG_LEVEL_DEBUG" "CssFormatter" "Formatted ${#less_files[@]} Less files"
                ((formatted_count += ${#less_files[@]}))
            else
                hook_log "$LOG_LEVEL_WARN" "CssFormatter" "Failed to format some Less files"
                success=false
            fi
        fi

    else
        hook_log "$LOG_LEVEL_WARN" "CssFormatter" "Prettier not found, skipping formatting"
        hook_log "$LOG_LEVEL_INFO" "CssFormatter" "Install with: npm install -g prettier"
    fi

    # Step 2: Lint with stylelint if available
    if command -v stylelint &> /dev/null; then
        local stylelint_version=$(stylelint --version 2>/dev/null || echo "unknown")
        hook_log "$LOG_LEVEL_INFO" "CssFormatter" "Using Stylelint: $stylelint_version"

        for file in "${files_found[@]}"; do
            if [[ ! -f "$file" ]]; then
                continue
            fi

            # Lint with stylelint (fix what's auto-fixable)
            if stylelint --fix "$file" 2>/dev/null; then
                hook_log "$LOG_LEVEL_DEBUG" "CssFormatter" "Linted: $file"
                ((linted_count++))
            else
                # Don't fail on lint errors, just log warnings
                hook_log "$LOG_LEVEL_DEBUG" "CssFormatter" "Stylelint warnings in: $file"
            fi
        done
    else
        hook_log "$LOG_LEVEL_INFO" "CssFormatter" "Stylelint not found, skipping linting"
        hook_log "$LOG_LEVEL_INFO" "CssFormatter" "Install with: npm install -g stylelint"
    fi

    hook_log "$LOG_LEVEL_INFO" "CssFormatter" "CSS processing completed: $formatted_count formatted, $linted_count linted"

    if [[ "$success" == true ]]; then
        return 0
    else
        return 1
    fi
}

# Validate formatter setup
validate_formatter_setup() {
    local validation_success=true

    hook_log "$LOG_LEVEL_INFO" "CssFormatter" "Validating CSS formatter setup"

    # Check Prettier availability
    if command -v prettier &> /dev/null; then
        local prettier_version=$(prettier --version 2>/dev/null || echo "unknown")
        hook_log "$LOG_LEVEL_INFO" "CssFormatter" "Prettier found: v$prettier_version"

        # Test Prettier functionality
        local test_css=".test { color: red;   }"
        if echo "$test_css" | prettier --parser css >/dev/null 2>&1; then
            hook_log "$LOG_LEVEL_INFO" "CssFormatter" "Prettier can process CSS"
        else
            hook_log "$LOG_LEVEL_ERROR" "CssFormatter" "Prettier CSS test failed"
            validation_success=false
        fi
    else
        hook_log "$LOG_LEVEL_WARN" "CssFormatter" "Prettier not found"
        hook_log "$LOG_LEVEL_INFO" "CssFormatter" "Install with: npm install -g prettier"
        validation_success=false
    fi

    # Check Stylelint availability (optional)
    if command -v stylelint &> /dev/null; then
        local stylelint_version=$(stylelint --version 2>/dev/null || echo "unknown")
        hook_log "$LOG_LEVEL_INFO" "CssFormatter" "Stylelint found: $stylelint_version"
    else
        hook_log "$LOG_LEVEL_INFO" "CssFormatter" "Stylelint not found (optional)"
        hook_log "$LOG_LEVEL_INFO" "CssFormatter" "Install with: npm install -g stylelint"
    fi

    if [[ "$validation_success" == true ]]; then
        hook_log "$LOG_LEVEL_INFO" "CssFormatter" "CSS formatter validation passed"
        return 0
    else
        hook_log "$LOG_LEVEL_WARN" "CssFormatter" "CSS formatter validation had warnings"
        return 1
    fi
}