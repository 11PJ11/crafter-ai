#!/bin/bash
# RubyFormatter - Ruby language formatter strategy
# Part of Claude Code SuperClaude modular hook system

set -euo pipefail

# Source dependencies
HOOK_LIB_DIR="$(dirname "${BASH_SOURCE[0]}")/.."
source "${HOOK_LIB_DIR}/formatters/BaseFormatter.sh"

# Override base formatter functions

get_formatter_name() {
    echo "RubyFormatter"
}

get_file_patterns() {
    echo "*.rb,*.rake,Rakefile,Gemfile"
}

get_required_tools() {
    echo "rubocop:gem:rubocop standardrb:gem:standard"
}

can_format_language() {
    local language="$1"
    [[ "$language" = "ruby" ]]
}

format_files() {
    local language="$1"

    if ! can_format_language "$language"; then
        hook_log "$LOG_LEVEL_ERROR" "RubyFormatter" "Cannot format language: $language"
        return 1
    fi

    hook_log "$LOG_LEVEL_INFO" "RubyFormatter" "Starting Ruby formatting"

    # Check if Ruby files exist
    if ! has_files_for_patterns "$(get_file_patterns)"; then
        hook_log "$LOG_LEVEL_DEBUG" "RubyFormatter" "No Ruby files found"
        return 0
    fi

    # Find and format Ruby files
    local files_found=()
    while IFS= read -r -d '' file; do
        files_found+=("$file")
    done < <(find_files_to_format "$(get_file_patterns)")

    if [[ ${#files_found[@]} -eq 0 ]]; then
        hook_log "$LOG_LEVEL_DEBUG" "RubyFormatter" "No Ruby files found to format"
        return 0
    fi

    hook_log "$LOG_LEVEL_INFO" "RubyFormatter" "Processing ${#files_found[@]} Ruby files"

    local formatted_count=0
    local success=true

    # Try Standard Ruby first (simpler, opinionated), then RuboCop
    if command -v standardrb &> /dev/null; then
        local standardrb_version=$(standardrb --version 2>/dev/null || echo "unknown")
        hook_log "$LOG_LEVEL_INFO" "RubyFormatter" "Using StandardRB: $standardrb_version"

        # Format with StandardRB (auto-fix mode)
        if standardrb --fix "${files_found[@]}" 2>/dev/null; then
            hook_log "$LOG_LEVEL_DEBUG" "RubyFormatter" "Formatted ${#files_found[@]} Ruby files with StandardRB"
            formatted_count=${#files_found[@]}
        else
            # Try individual files if batch fails
            for file in "${files_found[@]}"; do
                if [[ ! -f "$file" ]]; then
                    hook_log "$LOG_LEVEL_WARN" "RubyFormatter" "File not found: $file"
                    continue
                fi

                if standardrb --fix "$file" 2>/dev/null; then
                    hook_log "$LOG_LEVEL_DEBUG" "RubyFormatter" "Formatted: $file"
                    ((formatted_count++))
                else
                    hook_log "$LOG_LEVEL_WARN" "RubyFormatter" "StandardRB couldn't format: $file"
                fi
            done
        fi

    elif command -v rubocop &> /dev/null; then
        local rubocop_version=$(rubocop --version 2>/dev/null | head -n1 || echo "unknown")
        hook_log "$LOG_LEVEL_INFO" "RubyFormatter" "Using RuboCop: $rubocop_version"

        # Format with RuboCop (auto-correct mode)
        if rubocop --autocorrect-all "${files_found[@]}" 2>/dev/null; then
            hook_log "$LOG_LEVEL_DEBUG" "RubyFormatter" "Formatted ${#files_found[@]} Ruby files with RuboCop"
            formatted_count=${#files_found[@]}
        else
            # Try individual files if batch fails
            for file in "${files_found[@]}"; do
                if [[ ! -f "$file" ]]; then
                    hook_log "$LOG_LEVEL_WARN" "RubyFormatter" "File not found: $file"
                    continue
                fi

                if [[ ! -r "$file" ]]; then
                    hook_log "$LOG_LEVEL_WARN" "RubyFormatter" "Cannot read file: $file"
                    continue
                fi

                # Format individual file
                if rubocop --autocorrect-all "$file" 2>/dev/null; then
                    hook_log "$LOG_LEVEL_DEBUG" "RubyFormatter" "Formatted: $file"
                    ((formatted_count++))
                else
                    hook_log "$LOG_LEVEL_ERROR" "RubyFormatter" "Failed to format: $file"
                    success=false
                fi
            done
        fi
    else
        hook_log "$LOG_LEVEL_WARN" "RubyFormatter" "Neither StandardRB nor RuboCop found, skipping formatting"
        hook_log "$LOG_LEVEL_INFO" "RubyFormatter" "Install with: gem install standard (recommended) or gem install rubocop"
    fi

    hook_log "$LOG_LEVEL_INFO" "RubyFormatter" "Ruby processing completed: $formatted_count formatted"

    if [[ "$success" == true ]]; then
        return 0
    else
        return 1
    fi
}

# Validate formatter setup
validate_formatter_setup() {
    local validation_success=true

    hook_log "$LOG_LEVEL_INFO" "RubyFormatter" "Validating Ruby formatter setup"

    # Check Ruby installation
    if command -v ruby &> /dev/null; then
        local ruby_version=$(ruby --version 2>/dev/null | awk '{print $2}' || echo "unknown")
        hook_log "$LOG_LEVEL_INFO" "RubyFormatter" "Ruby found: v$ruby_version"
    else
        hook_log "$LOG_LEVEL_WARN" "RubyFormatter" "Ruby not found"
        hook_log "$LOG_LEVEL_INFO" "RubyFormatter" "Install from: https://www.ruby-lang.org/en/downloads/"
        validation_success=false
    fi

    # Check StandardRB availability (preferred)
    if command -v standardrb &> /dev/null; then
        local standardrb_version=$(standardrb --version 2>/dev/null || echo "unknown")
        hook_log "$LOG_LEVEL_INFO" "RubyFormatter" "StandardRB found: $standardrb_version"

        # Test StandardRB functionality
        local test_ruby="def hello\nputs 'world'\nend"
        if echo "$test_ruby" | standardrb --stdin test.rb --autocorrect 2>/dev/null >/dev/null; then
            hook_log "$LOG_LEVEL_INFO" "RubyFormatter" "StandardRB can process Ruby code"
        else
            hook_log "$LOG_LEVEL_ERROR" "RubyFormatter" "StandardRB test failed"
            validation_success=false
        fi

    # Check RuboCop availability (alternative)
    elif command -v rubocop &> /dev/null; then
        local rubocop_version=$(rubocop --version 2>/dev/null | head -n1 || echo "unknown")
        hook_log "$LOG_LEVEL_INFO" "RubyFormatter" "RuboCop found: $rubocop_version"

        # Test RuboCop functionality
        local test_ruby="def hello\nputs 'world'\nend"
        if echo "$test_ruby" | rubocop --stdin test.rb --autocorrect-all 2>/dev/null >/dev/null; then
            hook_log "$LOG_LEVEL_INFO" "RubyFormatter" "RuboCop can process Ruby code"
        else
            hook_log "$LOG_LEVEL_ERROR" "RubyFormatter" "RuboCop test failed"
            validation_success=false
        fi
    else
        hook_log "$LOG_LEVEL_WARN" "RubyFormatter" "Neither StandardRB nor RuboCop found"
        hook_log "$LOG_LEVEL_INFO" "RubyFormatter" "Install with: gem install standard (recommended)"
        hook_log "$LOG_LEVEL_INFO" "RubyFormatter" "Or install with: gem install rubocop"
        validation_success=false
    fi

    if [[ "$validation_success" == true ]]; then
        hook_log "$LOG_LEVEL_INFO" "RubyFormatter" "Ruby formatter validation passed"
        return 0
    else
        hook_log "$LOG_LEVEL_WARN" "RubyFormatter" "Ruby formatter validation had warnings"
        return 1
    fi
}