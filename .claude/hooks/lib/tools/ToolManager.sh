#!/bin/bash
# ToolManager - Tool installation and management module
# Part of Claude Code SuperClaude modular hook system

set -euo pipefail

# Source dependencies
HOOK_LIB_DIR="$(dirname "${BASH_SOURCE[0]}")/.."
source "${HOOK_LIB_DIR}/config/HookConfig.sh"
source "${HOOK_LIB_DIR}/logging/LogManager.sh"

# Tool paths
export PATH="$HOME/.local/bin:$PATH"

# Setup tool paths
setup_tool_paths() {
    hook_log "$LOG_LEVEL_DEBUG" "ToolManager" "Setting up tool paths"

    # Add common tool directories to PATH
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$HOME/go/bin:$PATH"

    # Add npm global directory if it exists
    if command -v npm >/dev/null 2>&1; then
        local npm_global_dir
        npm_global_dir="$(npm config get prefix 2>/dev/null || echo "$HOME/.npm-global")"
        if [[ -d "$npm_global_dir/bin" ]]; then
            export PATH="$npm_global_dir/bin:$PATH"
        fi
    fi

    hook_log "$LOG_LEVEL_DEBUG" "ToolManager" "Tool paths configured"
}

# Ensure pipx is available
ensure_pipx() {
    hook_log "$LOG_LEVEL_DEBUG" "ToolManager" "Checking pipx availability"

    if command -v pipx >/dev/null 2>&1; then
        hook_log "$LOG_LEVEL_DEBUG" "ToolManager" "pipx found"
        return 0
    fi

    hook_log "$LOG_LEVEL_INFO" "ToolManager" "Installing pipx"
    if command -v python3 >/dev/null 2>&1; then
        python3 -m pip install --user pipx
        python3 -m pipx ensurepath
        export PATH="$HOME/.local/bin:$PATH"
        return 0
    else
        hook_log "$LOG_LEVEL_ERROR" "ToolManager" "Python3 not found, cannot install pipx"
        return 1
    fi
}

# Install Python tool via pipx
install_python_tool() {
    local tool_name="$1"
    local package_name="${2:-$tool_name}"

    hook_log "$LOG_LEVEL_INFO" "ToolManager" "Installing Python tool: $tool_name"

    if ! ensure_pipx; then
        hook_log "$LOG_LEVEL_ERROR" "ToolManager" "Failed to ensure pipx availability"
        return 1
    fi

    if pipx install "$package_name"; then
        hook_log "$LOG_LEVEL_INFO" "ToolManager" "Successfully installed $tool_name"
        return 0
    else
        hook_log "$LOG_LEVEL_ERROR" "ToolManager" "Failed to install $tool_name"
        return 1
    fi
}

# Install npm tool globally
install_npm_tool() {
    local tool_name="$1"
    local package_name="${2:-$tool_name}"

    hook_log "$LOG_LEVEL_INFO" "ToolManager" "Installing npm tool: $tool_name"

    if ! command -v npm >/dev/null 2>&1; then
        hook_log "$LOG_LEVEL_ERROR" "ToolManager" "npm not found"
        return 1
    fi

    if npm install -g "$package_name"; then
        hook_log "$LOG_LEVEL_INFO" "ToolManager" "Successfully installed $tool_name"
        return 0
    else
        hook_log "$LOG_LEVEL_ERROR" "ToolManager" "Failed to install $tool_name"
        return 1
    fi
}

# Check and install tool with user confirmation
check_and_install_tool() {
    local tool_name="$1"
    local install_method="$2"  # "pipx", "npm", "cargo", etc.
    local package_name="${3:-$tool_name}"

    hook_log "$LOG_LEVEL_DEBUG" "ToolManager" "Checking tool: $tool_name"

    if command -v "$tool_name" >/dev/null 2>&1; then
        hook_log "$LOG_LEVEL_DEBUG" "ToolManager" "Tool found: $tool_name"
        return 0
    fi

    hook_log "$LOG_LEVEL_WARN" "ToolManager" "Tool not found: $tool_name"

    # In non-interactive mode, skip installation
    if [[ "${CI:-false}" = "true" ]] || [[ ! -t 1 ]]; then
        hook_log "$LOG_LEVEL_WARN" "ToolManager" "Non-interactive mode, skipping installation of $tool_name"
        return 1
    fi

    # Ask user for installation
    echo "📦 Tool '$tool_name' is not installed. Would you like to install it? (y/n)"
    read -r response

    if [[ "$response" =~ ^[Yy]$ ]]; then
        case "$install_method" in
            "pipx")
                install_python_tool "$tool_name" "$package_name"
                ;;
            "npm")
                install_npm_tool "$tool_name" "$package_name"
                ;;
            "cargo")
                if command -v cargo >/dev/null 2>&1; then
                    cargo install "$package_name"
                else
                    hook_log "$LOG_LEVEL_ERROR" "ToolManager" "Cargo not found"
                    return 1
                fi
                ;;
            *)
                hook_log "$LOG_LEVEL_ERROR" "ToolManager" "Unknown install method: $install_method"
                return 1
                ;;
        esac
    else
        hook_log "$LOG_LEVEL_INFO" "ToolManager" "User declined installation of $tool_name"
        return 1
    fi
}

# Try multiple formatter options
try_multiple_formatters() {
    local file_pattern="$1"
    shift
    local formatters=("$@")

    local files_found=false
    if find . -name "$file_pattern" -type f | head -1 | grep -q .; then
        files_found=true
    fi

    if [[ "$files_found" = false ]]; then
        hook_log "$LOG_LEVEL_DEBUG" "ToolManager" "No files matching $file_pattern found"
        return 0
    fi

    for formatter in "${formatters[@]}"; do
        local tool_name
        local install_method
        local package_name

        # Parse formatter specification: tool_name:install_method:package_name
        IFS=':' read -r tool_name install_method package_name <<< "$formatter"
        package_name="${package_name:-$tool_name}"

        if command -v "$tool_name" >/dev/null 2>&1; then
            hook_log "$LOG_LEVEL_INFO" "ToolManager" "Using $tool_name for $file_pattern"
            return 0
        fi
    done

    # If no formatter found, try to install the first one
    if [[ ${#formatters[@]} -gt 0 ]]; then
        local formatter="${formatters[0]}"
        IFS=':' read -r tool_name install_method package_name <<< "$formatter"
        package_name="${package_name:-$tool_name}"

        check_and_install_tool "$tool_name" "$install_method" "$package_name"
        return $?
    fi

    return 1
}