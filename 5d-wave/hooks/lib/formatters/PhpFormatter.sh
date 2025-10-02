#!/bin/bash
# AI-Craft Framework - Managed File
# Part of Claude Code SuperClaude modular hook system
# PhpFormatter - PHP language formatter strategy
# Part of Claude Code SuperClaude modular hook system

set -euo pipefail

# Source dependencies
HOOK_LIB_DIR="$(dirname "${BASH_SOURCE[0]}")/.."
source "${HOOK_LIB_DIR}/formatters/BaseFormatter.sh"

# Override base formatter functions

get_formatter_name() {
    echo "PhpFormatter"
}

get_file_patterns() {
    echo "*.php,*.phtml,*.php3,*.php4,*.php5,*.phps"
}

get_required_tools() {
    echo "php-cs-fixer:composer:friendsofphp/php-cs-fixer phpstan:composer:phpstan/phpstan"
}

can_format_language() {
    local language="$1"
    [[ "$language" = "php" ]]
}

format_files() {
    local language="$1"

    if ! can_format_language "$language"; then
        hook_log "$LOG_LEVEL_ERROR" "PhpFormatter" "Cannot format language: $language"
        return 1
    fi

    hook_log "$LOG_LEVEL_INFO" "PhpFormatter" "Starting PHP formatting"

    # Check if PHP files exist
    if ! has_files_for_patterns "$(get_file_patterns)"; then
        hook_log "$LOG_LEVEL_DEBUG" "PhpFormatter" "No PHP files found"
        return 0
    fi

    # Find and format PHP files
    local files_found=()
    while IFS= read -r -d '' file; do
        files_found+=("$file")
    done < <(find_files_to_format "$(get_file_patterns)")

    if [[ ${#files_found[@]} -eq 0 ]]; then
        hook_log "$LOG_LEVEL_DEBUG" "PhpFormatter" "No PHP files found to format"
        return 0
    fi

    hook_log "$LOG_LEVEL_INFO" "PhpFormatter" "Processing ${#files_found[@]} PHP files"

    local formatted_count=0
    local success=true

    # Format with PHP CS Fixer if available
    if command -v php-cs-fixer &> /dev/null; then
        local phpcs_version=$(php-cs-fixer --version 2>/dev/null | head -n1 || echo "unknown")
        hook_log "$LOG_LEVEL_INFO" "PhpFormatter" "Using PHP CS Fixer: $phpcs_version"

        for file in "${files_found[@]}"; do
            if [[ ! -f "$file" ]]; then
                hook_log "$LOG_LEVEL_WARN" "PhpFormatter" "File not found: $file"
                continue
            fi

            if [[ ! -r "$file" ]]; then
                hook_log "$LOG_LEVEL_WARN" "PhpFormatter" "Cannot read file: $file"
                continue
            fi

            # Format with PHP CS Fixer (PSR-12 standard)
            if php-cs-fixer fix "$file" --rules=@PSR12 --quiet 2>/dev/null; then
                hook_log "$LOG_LEVEL_DEBUG" "PhpFormatter" "Formatted: $file"
                ((formatted_count++))
            else
                hook_log "$LOG_LEVEL_ERROR" "PhpFormatter" "Failed to format: $file"
                success=false
            fi
        done

    # Fallback to basic PHP syntax check if formatter not available
    elif command -v php &> /dev/null; then
        hook_log "$LOG_LEVEL_WARN" "PhpFormatter" "PHP CS Fixer not found, performing syntax validation only"
        local php_version=$(php --version 2>/dev/null | head -n1 | awk '{print $2}' || echo "unknown")
        hook_log "$LOG_LEVEL_INFO" "PhpFormatter" "Using PHP: v$php_version"

        for file in "${files_found[@]}"; do
            if [[ ! -f "$file" ]]; then
                continue
            fi

            # Basic syntax validation
            if php -l "$file" 2>/dev/null >/dev/null; then
                hook_log "$LOG_LEVEL_DEBUG" "PhpFormatter" "Syntax validated: $file"
                ((formatted_count++))
            else
                hook_log "$LOG_LEVEL_ERROR" "PhpFormatter" "Syntax error in: $file"
                success=false
            fi
        done
    else
        hook_log "$LOG_LEVEL_WARN" "PhpFormatter" "Neither PHP CS Fixer nor PHP found, skipping formatting"
        hook_log "$LOG_LEVEL_INFO" "PhpFormatter" "Install PHP from: https://www.php.net/downloads.php"
        hook_log "$LOG_LEVEL_INFO" "PhpFormatter" "Install PHP CS Fixer: composer global require friendsofphp/php-cs-fixer"
    fi

    hook_log "$LOG_LEVEL_INFO" "PhpFormatter" "PHP processing completed: $formatted_count processed"

    if [[ "$success" == true ]]; then
        return 0
    else
        return 1
    fi
}

# Validate formatter setup
validate_formatter_setup() {
    local validation_success=true

    hook_log "$LOG_LEVEL_INFO" "PhpFormatter" "Validating PHP formatter setup"

    # Check PHP installation
    if command -v php &> /dev/null; then
        local php_version=$(php --version 2>/dev/null | head -n1 | awk '{print $2}' || echo "unknown")
        hook_log "$LOG_LEVEL_INFO" "PhpFormatter" "PHP found: v$php_version"
    else
        hook_log "$LOG_LEVEL_WARN" "PhpFormatter" "PHP not found"
        hook_log "$LOG_LEVEL_INFO" "PhpFormatter" "Install from: https://www.php.net/downloads.php"
        validation_success=false
    fi

    # Check PHP CS Fixer availability
    if command -v php-cs-fixer &> /dev/null; then
        local phpcs_version=$(php-cs-fixer --version 2>/dev/null | head -n1 || echo "unknown")
        hook_log "$LOG_LEVEL_INFO" "PhpFormatter" "PHP CS Fixer found: $phpcs_version"

        # Test PHP CS Fixer functionality
        local test_php="<?php\necho 'Hello World';\n?>"
        local temp_file=$(mktemp --suffix=.php)
        echo -e "$test_php" > "$temp_file"

        if php-cs-fixer fix "$temp_file" --rules=@PSR12 --quiet 2>/dev/null; then
            hook_log "$LOG_LEVEL_INFO" "PhpFormatter" "PHP CS Fixer can process PHP code"
        else
            hook_log "$LOG_LEVEL_ERROR" "PhpFormatter" "PHP CS Fixer test failed"
            validation_success=false
        fi

        rm -f "$temp_file"
    else
        hook_log "$LOG_LEVEL_WARN" "PhpFormatter" "PHP CS Fixer not found"
        hook_log "$LOG_LEVEL_INFO" "PhpFormatter" "Install with: composer global require friendsofphp/php-cs-fixer"
        hook_log "$LOG_LEVEL_INFO" "PhpFormatter" "Make sure ~/.composer/vendor/bin is in your PATH"
        validation_success=false
    fi

    # Check Composer availability (optional)
    if command -v composer &> /dev/null; then
        local composer_version=$(composer --version 2>/dev/null | awk '{print $3}' || echo "unknown")
        hook_log "$LOG_LEVEL_INFO" "PhpFormatter" "Composer found: v$composer_version"
    else
        hook_log "$LOG_LEVEL_INFO" "PhpFormatter" "Composer not found (optional)"
        hook_log "$LOG_LEVEL_INFO" "PhpFormatter" "Install from: https://getcomposer.org/download/"
    fi

    if [[ "$validation_success" == true ]]; then
        hook_log "$LOG_LEVEL_INFO" "PhpFormatter" "PHP formatter validation passed"
        return 0
    else
        hook_log "$LOG_LEVEL_WARN" "PhpFormatter" "PHP formatter validation had warnings"
        return 1
    fi
}