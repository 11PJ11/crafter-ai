#!/bin/bash
# JavaScriptFormatter - JavaScript/TypeScript formatter strategy
# Part of Claude Code SuperClaude modular hook system

set -euo pipefail

# Source dependencies
HOOK_LIB_DIR="$(dirname "${BASH_SOURCE[0]}")/.."
source "${HOOK_LIB_DIR}/formatters/BaseFormatter.sh"
source "${HOOK_LIB_DIR}/tools/JsonUtils.sh"

# Override base formatter functions

get_formatter_name() {
    echo "JavaScriptFormatter"
}

get_file_patterns() {
    echo "*.js,*.jsx,*.ts,*.tsx,*.mjs"
}

get_required_tools() {
    echo "prettier:npm:prettier eslint:npm:eslint"
}

can_format_language() {
    local language="$1"
    [[ "$language" = "javascript" ]] || [[ "$language" = "typescript" ]]
}

format_files() {
    local language="$1"

    if ! can_format_language "$language"; then
        hook_log "$LOG_LEVEL_ERROR" "JavaScriptFormatter" "Cannot format language: $language"
        return 1
    fi

    hook_log "$LOG_LEVEL_INFO" "JavaScriptFormatter" "Starting JavaScript/TypeScript formatting"

    # Check if JS/TS files exist
    if ! has_files_for_patterns "$(get_file_patterns)"; then
        hook_log "$LOG_LEVEL_DEBUG" "JavaScriptFormatter" "No JavaScript/TypeScript files found"
        return 0
    fi

    # Ensure required tools
    if ! ensure_formatter_tools "$(get_required_tools)"; then
        hook_log "$LOG_LEVEL_WARN" "JavaScriptFormatter" "Required tools not available, skipping JS/TS formatting"
        return 1
    fi

    local success=true

    # Get file patterns for this project
    local file_patterns
    file_patterns=$(get_project_file_patterns)

    # Format with Prettier
    if command -v prettier >/dev/null 2>&1; then
        if ! execute_prettier_check "$file_patterns"; then
            hook_log "$LOG_LEVEL_INFO" "JavaScriptFormatter" "Applying Prettier formatting"
            if ! execute_prettier_format "$file_patterns"; then
                success=false
            fi
        fi
    fi

    # Lint with ESLint
    if command -v eslint >/dev/null 2>&1 && has_eslint_config; then
        if ! execute_eslint_check "$file_patterns"; then
            hook_log "$LOG_LEVEL_INFO" "JavaScriptFormatter" "Applying ESLint fixes"
            if ! execute_eslint_fix "$file_patterns"; then
                success=false
            fi
        fi
    fi

    # TypeScript specific checks
    if [[ "$language" = "typescript" ]] && command -v tsc >/dev/null 2>&1 && [[ -f "tsconfig.json" ]]; then
        if ! execute_formatter "TypeScript Check" "tsc --noEmit" "typescript"; then
            hook_log "$LOG_LEVEL_WARN" "JavaScriptFormatter" "TypeScript compilation errors found"
        fi
    fi

    if [[ "$success" = true ]]; then
        hook_log "$LOG_LEVEL_INFO" "JavaScriptFormatter" "✅ JavaScript/TypeScript formatting completed successfully"
        return 0
    else
        hook_log "$LOG_LEVEL_ERROR" "JavaScriptFormatter" "❌ JavaScript/TypeScript formatting encountered errors"
        return 1
    fi
}

# JavaScript-specific helper functions

# Get project-specific file patterns
get_project_file_patterns() {
    local patterns="*.js,*.jsx,*.mjs"

    # Add TypeScript patterns if TypeScript is detected
    if [[ -f "tsconfig.json" ]] || find . -name "*.ts" -o -name "*.tsx" | head -1 | grep -q .; then
        patterns="$patterns,*.ts,*.tsx"
    fi

    echo "$patterns"
}

# Check if ESLint configuration exists
has_eslint_config() {
    [[ -f ".eslintrc.json" ]] || [[ -f ".eslintrc.js" ]] || [[ -f ".eslintrc.yml" ]] || \
    [[ -f ".eslintrc.yaml" ]] || [[ -f "eslint.config.js" ]] || \
    (validate_json_file "package.json" && parse_json_file "package.json" "eslintConfig" | grep -q .)
}

# Execute prettier check
execute_prettier_check() {
    local patterns="$1"
    local prettier_args="--check"

    # Add project-specific patterns
    IFS=',' read -ra pattern_array <<< "$patterns"
    for pattern in "${pattern_array[@]}"; do
        prettier_args="$prettier_args '$pattern'"
    done

    execute_formatter "Prettier Check" "prettier $prettier_args" "javascript"
}

# Execute prettier format
execute_prettier_format() {
    local patterns="$1"
    local prettier_args="--write"

    # Add project-specific patterns
    IFS=',' read -ra pattern_array <<< "$patterns"
    for pattern in "${pattern_array[@]}"; do
        prettier_args="$prettier_args '$pattern'"
    done

    execute_formatter "Prettier Format" "prettier $prettier_args" "javascript"
}

# Execute ESLint check
execute_eslint_check() {
    local patterns="$1"
    local eslint_args="."

    # Use specific patterns if provided
    if [[ -n "$patterns" ]]; then
        eslint_args=""
        IFS=',' read -ra pattern_array <<< "$patterns"
        for pattern in "${pattern_array[@]}"; do
            eslint_args="$eslint_args --ext ${pattern#*.} ."
        done
    fi

    execute_formatter "ESLint Check" "eslint $eslint_args" "javascript"
}

# Execute ESLint fix
execute_eslint_fix() {
    local patterns="$1"
    local eslint_args="--fix ."

    # Use specific patterns if provided
    if [[ -n "$patterns" ]]; then
        eslint_args="--fix"
        IFS=',' read -ra pattern_array <<< "$patterns"
        for pattern in "${pattern_array[@]}"; do
            eslint_args="$eslint_args --ext ${pattern#*.} ."
        done
    fi

    execute_formatter "ESLint Fix" "eslint $eslint_args" "javascript"
}

# Check for React project
is_react_project() {
    validate_json_file "package.json" && {
        parse_json_file "package.json" "dependencies.react" | grep -q . ||
        parse_json_file "package.json" "devDependencies.react" | grep -q .
    }
}

# Check for Vue project
is_vue_project() {
    validate_json_file "package.json" && {
        parse_json_file "package.json" "dependencies.vue" | grep -q . ||
        parse_json_file "package.json" "devDependencies.vue" | grep -q .
    }
}

# Check for Angular project
is_angular_project() {
    [[ -f "angular.json" ]] || {
        validate_json_file "package.json" && {
            parse_json_file "package.json" "dependencies.@angular/core" | grep -q . ||
            parse_json_file "package.json" "devDependencies.@angular/core" | grep -q .
        }
    }
}

# Check for Node.js project
is_node_project() {
    [[ -f "package.json" ]] && ! is_react_project && ! is_vue_project && ! is_angular_project
}