#!/bin/bash
# AI-Craft Framework - Managed File
# Part of Claude Code SuperClaude modular hook system
# PythonFormatter - Python language formatter strategy
# Part of Claude Code SuperClaude modular hook system

set -euo pipefail

# Source dependencies
HOOK_LIB_DIR="$(dirname "${BASH_SOURCE[0]}")/.."
source "${HOOK_LIB_DIR}/formatters/BaseFormatter.sh"
source "${HOOK_LIB_DIR}/tools/JsonUtils.sh"

# Override base formatter functions

get_formatter_name() {
    echo "PythonFormatter"
}

get_file_patterns() {
    echo "*.py"
}

get_required_tools() {
    echo "black:pipx:black isort:pipx:isort ruff:pipx:ruff"
}

can_format_language() {
    local language="$1"
    [[ "$language" = "python" ]]
}

format_files() {
    local language="$1"

    if ! can_format_language "$language"; then
        hook_log "$LOG_LEVEL_ERROR" "PythonFormatter" "Cannot format language: $language"
        return 1
    fi

    hook_log "$LOG_LEVEL_INFO" "PythonFormatter" "Starting Python formatting"

    # Check if Python files exist
    if ! has_files_for_patterns "$(get_file_patterns)"; then
        hook_log "$LOG_LEVEL_DEBUG" "PythonFormatter" "No Python files found"
        return 0
    fi

    # Ensure required tools
    if ! ensure_formatter_tools "$(get_required_tools)"; then
        hook_log "$LOG_LEVEL_WARN" "PythonFormatter" "Required tools not available, skipping Python formatting"
        return 1
    fi

    local success=true

    # Format with Black
    if command -v black >/dev/null 2>&1; then
        if ! execute_formatter "Black" "black --check --diff ." "python"; then
            hook_log "$LOG_LEVEL_INFO" "PythonFormatter" "Applying Black formatting"
            if ! execute_formatter "Black" "black ." "python"; then
                success=false
            fi
        fi
    fi

    # Sort imports with isort
    if command -v isort >/dev/null 2>&1; then
        if ! execute_formatter "isort" "isort --check-only --diff ." "python"; then
            hook_log "$LOG_LEVEL_INFO" "PythonFormatter" "Applying isort formatting"
            if ! execute_formatter "isort" "isort ." "python"; then
                success=false
            fi
        fi
    fi

    # Lint with Ruff (if available)
    if command -v ruff >/dev/null 2>&1; then
        if ! execute_formatter "Ruff" "ruff check ." "python"; then
            hook_log "$LOG_LEVEL_WARN" "PythonFormatter" "Ruff found issues"
            # Try to fix automatically
            if ! execute_formatter "Ruff Fix" "ruff check --fix ." "python"; then
                success=false
            fi
        fi
    fi

    # Check for pyproject.toml configuration
    if [[ -f "pyproject.toml" ]]; then
        hook_log "$LOG_LEVEL_DEBUG" "PythonFormatter" "Found pyproject.toml configuration"

        # Parse configuration if possible
        if validate_json_file "pyproject.toml" 2>/dev/null; then
            hook_log "$LOG_LEVEL_DEBUG" "PythonFormatter" "Using pyproject.toml settings"
        fi
    fi

    # Check for setup.py or requirements files
    if [[ -f "setup.py" ]] || [[ -f "requirements.txt" ]] || [[ -f "Pipfile" ]]; then
        hook_log "$LOG_LEVEL_DEBUG" "PythonFormatter" "Python project structure detected"
    fi

    if [[ "$success" = true ]]; then
        hook_log "$LOG_LEVEL_INFO" "PythonFormatter" "✅ Python formatting completed successfully"
        return 0
    else
        hook_log "$LOG_LEVEL_ERROR" "PythonFormatter" "❌ Python formatting encountered errors"
        return 1
    fi
}

# Python-specific helper functions

# Check for Python virtual environment
check_python_venv() {
    if [[ -n "${VIRTUAL_ENV:-}" ]]; then
        hook_log "$LOG_LEVEL_DEBUG" "PythonFormatter" "Virtual environment active: $VIRTUAL_ENV"
        return 0
    elif [[ -d "venv" ]] || [[ -d ".venv" ]] || [[ -d "env" ]]; then
        hook_log "$LOG_LEVEL_DEBUG" "PythonFormatter" "Virtual environment directory found"
        return 0
    fi
    return 1
}

# Get Python version
get_python_version() {
    if command -v python3 >/dev/null 2>&1; then
        python3 --version 2>&1 | cut -d' ' -f2
    elif command -v python >/dev/null 2>&1; then
        python --version 2>&1 | cut -d' ' -f2
    else
        echo "unknown"
    fi
}

# Check for Django project
is_django_project() {
    [[ -f "manage.py" ]] || [[ -f "django_project/settings.py" ]] || grep -q "django" requirements.txt 2>/dev/null
}

# Check for Flask project
is_flask_project() {
    grep -q "flask" requirements.txt 2>/dev/null || find . -name "*.py" -exec grep -l "from flask import\|import flask" {} \; | head -1 | grep -q .
}