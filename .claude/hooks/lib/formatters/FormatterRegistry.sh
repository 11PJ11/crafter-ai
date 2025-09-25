#!/bin/bash
# FormatterRegistry - Formatter strategy registry and dispatcher
# Part of Claude Code SuperClaude modular hook system

set -euo pipefail

# Source dependencies
HOOK_LIB_DIR="$(dirname "${BASH_SOURCE[0]}")/.."
source "${HOOK_LIB_DIR}/config/HookConfig.sh"
source "${HOOK_LIB_DIR}/logging/LogManager.sh"
source "${HOOK_LIB_DIR}/formatters/BaseFormatter.sh"

# Source resilience components if available
if [[ -f "${HOOK_LIB_DIR}/resilience/FileSystemCoordinator.sh" ]]; then
    source "${HOOK_LIB_DIR}/resilience/FileSystemCoordinator.sh"
    RESILIENCE_AVAILABLE=true
    hook_log "$LOG_LEVEL_DEBUG" "FormatterRegistry" "File system coordination available"
else
    RESILIENCE_AVAILABLE=false
    hook_log "$LOG_LEVEL_DEBUG" "FormatterRegistry" "File system coordination not available - using standard processing"
fi

# Available formatters
declare -A FORMATTER_REGISTRY=(
    ["python"]="PythonFormatter"
    ["javascript"]="JavaScriptFormatter"
    ["typescript"]="JavaScriptFormatter"
    ["csharp"]="CSharpFormatter"
    ["java"]="JavaFormatter"
    ["go"]="GoFormatter"
    ["rust"]="RustFormatter"
    ["css"]="CssFormatter"
    ["json"]="JsonFormatter"
    ["yaml"]="YamlFormatter"
    ["markdown"]="MarkdownFormatter"
    ["shell"]="ShellFormatter"
)

# Initialize formatter registry
init_formatter_registry() {
    hook_log "$LOG_LEVEL_DEBUG" "FormatterRegistry" "Initializing formatter registry"

    # Note: Formatter modules are sourced on-demand during dispatch
    # This avoids function name conflicts in bash

    hook_log "$LOG_LEVEL_INFO" "FormatterRegistry" "Formatter registry initialized"
}

# Get formatter for language
get_formatter_for_language() {
    local language="$1"

    if [[ -n "${FORMATTER_REGISTRY[$language]:-}" ]]; then
        echo "${FORMATTER_REGISTRY[$language]}"
        return 0
    else
        hook_log "$LOG_LEVEL_WARN" "FormatterRegistry" "No formatter found for language: $language"
        return 1
    fi
}

# Dispatch formatting for language with resilience
dispatch_formatter() {
    local language="$1"

    hook_log "$LOG_LEVEL_INFO" "FormatterRegistry" "Dispatching formatter for language: $language"

    # Use coordinated formatting if resilience components are available
    if [[ "$RESILIENCE_AVAILABLE" = true ]]; then
        local files_to_format
        files_to_format=$(find_files_for_language_dispatch "$language")

        if [[ -n "$files_to_format" ]]; then
            hook_log "$LOG_LEVEL_DEBUG" "FormatterRegistry" "Using coordinated formatting for $language"

            case "$language" in
                "python")
                    if coordinate_concurrent_formatting "$language" "."; then
                        hook_log "$LOG_LEVEL_INFO" "FormatterRegistry" "Coordinated Python formatting completed"
                        return 0
                    else
                        hook_log "$LOG_LEVEL_WARN" "FormatterRegistry" "Coordinated Python formatting failed - falling back to standard"
                    fi
                    ;;
                "javascript"|"typescript")
                    if coordinate_concurrent_formatting "$language" "."; then
                        hook_log "$LOG_LEVEL_INFO" "FormatterRegistry" "Coordinated JavaScript/TypeScript formatting completed"
                        return 0
                    else
                        hook_log "$LOG_LEVEL_WARN" "FormatterRegistry" "Coordinated JavaScript/TypeScript formatting failed - falling back to standard"
                    fi
                    ;;
                *)
                    # For other languages, fall through to standard processing
                    hook_log "$LOG_LEVEL_DEBUG" "FormatterRegistry" "No coordinated processing for $language - using standard"
                    ;;
            esac
        else
            hook_log "$LOG_LEVEL_DEBUG" "FormatterRegistry" "No files found for coordinated $language formatting"
            return 0
        fi
    fi

    # Standard dispatch (original implementation or fallback)
    case "$language" in
        "python")
            format_python_language
            ;;
        "javascript"|"typescript")
            format_javascript_language "$language"
            ;;
        "csharp")
            format_csharp_files
            ;;
        "java")
            format_java_files
            ;;
        "go")
            format_go_files
            ;;
        "rust")
            format_rust_files
            ;;
        "css")
            format_css_files
            ;;
        "json")
            format_json_files
            ;;
        "yaml")
            format_yaml_files
            ;;
        "markdown")
            format_markdown_files
            ;;
        "shell")
            format_shell_files
            ;;
        *)
            hook_log "$LOG_LEVEL_WARN" "FormatterRegistry" "Unsupported language: $language"
            return 0
            ;;
    esac
}

# Helper function to find files for language dispatch
find_files_for_language_dispatch() {
    local language="$1"
    local patterns

    case "$language" in
        "python")
            patterns="*.py"
            ;;
        "javascript")
            patterns="*.js,*.jsx"
            ;;
        "typescript")
            patterns="*.ts,*.tsx"
            ;;
        "shell")
            patterns="*.sh,*.bash"
            ;;
        *)
            patterns="*.$language"
            ;;
    esac

    find_files_to_format "$patterns" | head -10 | tr '\n' ' '
}

# Language-specific formatter functions that source the appropriate modules

format_python_language() {
    # Source Python formatter in subshell to avoid function conflicts
    (
        source "${HOOK_LIB_DIR}/formatters/PythonFormatter.sh"
        format_files "python"
    )
}

format_javascript_language() {
    local language="$1"
    # Source JavaScript formatter in subshell to avoid function conflicts
    (
        source "${HOOK_LIB_DIR}/formatters/JavaScriptFormatter.sh"
        format_files "$language"
    )
}

# Get all supported languages
get_supported_languages() {
    printf '%s\n' "${!FORMATTER_REGISTRY[@]}" | sort
}

# Check if language is supported
is_language_supported() {
    local language="$1"
    [[ -n "${FORMATTER_REGISTRY[$language]:-}" ]]
}

# Placeholder formatters for languages not yet implemented

format_csharp_files() {
    hook_log "$LOG_LEVEL_INFO" "FormatterRegistry" "Formatting C# files"

    if ! has_files_for_patterns "*.cs"; then
        hook_log "$LOG_LEVEL_DEBUG" "FormatterRegistry" "No C# files found"
        return 0
    fi

    if command -v dotnet >/dev/null 2>&1; then
        execute_formatter "dotnet format" "dotnet format --verbosity quiet" "csharp"
    else
        hook_log "$LOG_LEVEL_WARN" "FormatterRegistry" "dotnet CLI not found, skipping C# formatting"
        return 1
    fi
}

format_java_files() {
    hook_log "$LOG_LEVEL_INFO" "FormatterRegistry" "Formatting Java files"

    if ! has_files_for_patterns "*.java"; then
        hook_log "$LOG_LEVEL_DEBUG" "FormatterRegistry" "No Java files found"
        return 0
    fi

    if command -v google-java-format >/dev/null 2>&1; then
        execute_formatter "google-java-format" "find . -name '*.java' -exec google-java-format --replace {} +" "java"
    else
        hook_log "$LOG_LEVEL_WARN" "FormatterRegistry" "google-java-format not found, skipping Java formatting"
        return 1
    fi
}

format_go_files() {
    hook_log "$LOG_LEVEL_INFO" "FormatterRegistry" "Formatting Go files"

    if ! has_files_for_patterns "*.go"; then
        hook_log "$LOG_LEVEL_DEBUG" "FormatterRegistry" "No Go files found"
        return 0
    fi

    if command -v gofmt >/dev/null 2>&1; then
        execute_formatter "gofmt" "gofmt -w ." "go"
    else
        hook_log "$LOG_LEVEL_WARN" "FormatterRegistry" "gofmt not found, skipping Go formatting"
        return 1
    fi
}

format_rust_files() {
    hook_log "$LOG_LEVEL_INFO" "FormatterRegistry" "Formatting Rust files"

    if ! has_files_for_patterns "*.rs"; then
        hook_log "$LOG_LEVEL_DEBUG" "FormatterRegistry" "No Rust files found"
        return 0
    fi

    if command -v rustfmt >/dev/null 2>&1; then
        execute_formatter "rustfmt" "find . -name '*.rs' -exec rustfmt {} +" "rust"
    else
        hook_log "$LOG_LEVEL_WARN" "FormatterRegistry" "rustfmt not found, skipping Rust formatting"
        return 1
    fi
}

format_css_files() {
    hook_log "$LOG_LEVEL_INFO" "FormatterRegistry" "Formatting CSS files"

    if ! has_files_for_patterns "*.css,*.scss,*.sass"; then
        hook_log "$LOG_LEVEL_DEBUG" "FormatterRegistry" "No CSS files found"
        return 0
    fi

    if command -v prettier >/dev/null 2>&1; then
        execute_formatter "prettier" "prettier --write '*.css' '*.scss' '*.sass'" "css"
    else
        hook_log "$LOG_LEVEL_WARN" "FormatterRegistry" "prettier not found, skipping CSS formatting"
        return 1
    fi
}

format_json_files() {
    hook_log "$LOG_LEVEL_INFO" "FormatterRegistry" "Formatting JSON files"

    if ! has_files_for_patterns "*.json"; then
        hook_log "$LOG_LEVEL_DEBUG" "FormatterRegistry" "No JSON files found"
        return 0
    fi

    if command -v jq >/dev/null 2>&1; then
        execute_formatter "jq" "find . -name '*.json' -exec sh -c 'jq . \"\$1\" > \"\$1.tmp\" && mv \"\$1.tmp\" \"\$1\"' _ {} +" "json"
    elif command -v prettier >/dev/null 2>&1; then
        execute_formatter "prettier" "prettier --write '*.json'" "json"
    else
        hook_log "$LOG_LEVEL_WARN" "FormatterRegistry" "jq or prettier not found, skipping JSON formatting"
        return 1
    fi
}

format_yaml_files() {
    hook_log "$LOG_LEVEL_INFO" "FormatterRegistry" "Formatting YAML files"

    if ! has_files_for_patterns "*.yml,*.yaml"; then
        hook_log "$LOG_LEVEL_DEBUG" "FormatterRegistry" "No YAML files found"
        return 0
    fi

    if command -v prettier >/dev/null 2>&1; then
        execute_formatter "prettier" "prettier --write '*.yml' '*.yaml'" "yaml"
    else
        hook_log "$LOG_LEVEL_WARN" "FormatterRegistry" "prettier not found, skipping YAML formatting"
        return 1
    fi
}

format_markdown_files() {
    hook_log "$LOG_LEVEL_INFO" "FormatterRegistry" "Formatting Markdown files"

    if ! has_files_for_patterns "*.md"; then
        hook_log "$LOG_LEVEL_DEBUG" "FormatterRegistry" "No Markdown files found"
        return 0
    fi

    if command -v prettier >/dev/null 2>&1; then
        execute_formatter "prettier" "prettier --write '*.md'" "markdown"
    else
        hook_log "$LOG_LEVEL_WARN" "FormatterRegistry" "prettier not found, skipping Markdown formatting"
        return 1
    fi
}

format_shell_files() {
    hook_log "$LOG_LEVEL_INFO" "FormatterRegistry" "Checking shell files"

    if ! has_files_for_patterns "*.sh,*.bash"; then
        hook_log "$LOG_LEVEL_DEBUG" "FormatterRegistry" "No shell files found"
        return 0
    fi

    if command -v shellcheck >/dev/null 2>&1; then
        execute_formatter "shellcheck" "find . -name '*.sh' -o -name '*.bash' | xargs shellcheck" "shell"
    else
        hook_log "$LOG_LEVEL_WARN" "FormatterRegistry" "shellcheck not found, skipping shell file checks"
        return 1
    fi
}