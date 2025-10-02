#!/bin/bash
# AI-Craft Framework - Managed File
# Part of Claude Code SuperClaude modular hook system
# CSharpFormatter - C# language formatter strategy
# Part of Claude Code SuperClaude modular hook system

set -euo pipefail

# Source dependencies
HOOK_LIB_DIR="$(dirname "${BASH_SOURCE[0]}")/.."
source "${HOOK_LIB_DIR}/formatters/BaseFormatter.sh"

# Override base formatter functions

get_formatter_name() {
    echo "CSharpFormatter"
}

get_file_patterns() {
    echo "*.cs,*.csx,*.cake"
}

get_required_tools() {
    echo "dotnet:system:dotnet-sdk"
}

can_format_language() {
    local language="$1"
    [[ "$language" = "csharp" ]]
}

format_files() {
    local language="$1"

    if ! can_format_language "$language"; then
        hook_log "$LOG_LEVEL_ERROR" "CSharpFormatter" "Cannot format language: $language"
        return 1
    fi

    hook_log "$LOG_LEVEL_INFO" "CSharpFormatter" "Starting C# formatting"

    # Check if C# files exist
    if ! has_files_for_patterns "$(get_file_patterns)"; then
        hook_log "$LOG_LEVEL_DEBUG" "CSharpFormatter" "No C# files found"
        return 0
    fi

    # Check if dotnet is available
    if ! command -v dotnet &> /dev/null; then
        hook_log "$LOG_LEVEL_WARN" "CSharpFormatter" "dotnet CLI not found, skipping C# formatting"
        return 1
    fi

    # Get dotnet version for logging
    local version=$(dotnet --version 2>/dev/null)
    hook_log "$LOG_LEVEL_INFO" "CSharpFormatter" "Using: dotnet CLI v$version"

    # Strategy 1: Try project-based formatting first
    if _try_project_based_formatting; then
        hook_log "$LOG_LEVEL_INFO" "CSharpFormatter" "Project-based formatting completed"
        return 0
    fi

    # Strategy 2: Fallback to individual file formatting
    hook_log "$LOG_LEVEL_INFO" "CSharpFormatter" "Project-based formatting not available, trying individual file formatting"

    # Find and format C# files
    local files_found=()
    while IFS= read -r -d '' file; do
        files_found+=("$file")
    done < <(find_files_to_format "$(get_file_patterns)")

    if [[ ${#files_found[@]} -eq 0 ]]; then
        hook_log "$LOG_LEVEL_DEBUG" "CSharpFormatter" "No C# files found to format"
        return 0
    fi

    hook_log "$LOG_LEVEL_INFO" "CSharpFormatter" "Formatting ${#files_found[@]} C# files"

    local formatted_count=0
    local success=true

    for file in "${files_found[@]}"; do
        if [[ ! -f "$file" ]]; then
            hook_log "$LOG_LEVEL_WARN" "CSharpFormatter" "File not found: $file"
            continue
        fi

        if [[ ! -r "$file" ]]; then
            hook_log "$LOG_LEVEL_WARN" "CSharpFormatter" "Cannot read file: $file"
            continue
        fi

        # Create a temporary minimal project for the file
        if _format_standalone_csharp_file "$file"; then
            hook_log "$LOG_LEVEL_DEBUG" "CSharpFormatter" "Formatted: $file"
            ((formatted_count++))
        else
            hook_log "$LOG_LEVEL_ERROR" "CSharpFormatter" "Failed to format: $file"
            success=false
        fi
    done

    hook_log "$LOG_LEVEL_INFO" "CSharpFormatter" "C# formatting completed: $formatted_count/${#files_found[@]} files formatted"

    if [[ "$success" == true ]]; then
        return 0
    else
        return 1
    fi
}

# Private helper functions

_try_project_based_formatting() {
    # Look for .NET project files in current and parent directories
    local project_file=""
    local search_dir="."

    for level in {0..3}; do
        local found_files=$(find "$search_dir" -maxdepth 1 \( -name "*.csproj" -o -name "*.sln" \) 2>/dev/null | head -n1)
        if [[ -n "$found_files" ]]; then
            project_file="$found_files"
            break
        fi
        search_dir="../$search_dir"
    done

    if [[ -n "$project_file" ]]; then
        hook_log "$LOG_LEVEL_DEBUG" "CSharpFormatter" "Found project file: $project_file"
        if dotnet format "$project_file" --verbosity quiet 2>/dev/null; then
            return 0
        else
            hook_log "$LOG_LEVEL_DEBUG" "CSharpFormatter" "Project-based formatting failed"
            return 1
        fi
    else
        hook_log "$LOG_LEVEL_DEBUG" "CSharpFormatter" "No .NET project file found"
        return 1
    fi
}

_format_standalone_csharp_file() {
    local file="$1"
    local temp_dir
    local temp_project

    # Create temporary directory for standalone formatting
    temp_dir=$(mktemp -d)
    temp_project="$temp_dir/TempProject.csproj"

    # Create minimal project file
    cat > "$temp_project" << 'EOF'
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net6.0</TargetFramework>
    <OutputType>Exe</OutputType>
  </PropertyGroup>
</Project>
EOF

    # Copy the C# file to temp directory
    local temp_file="$temp_dir/$(basename "$file")"
    cp "$file" "$temp_file"

    # Format using the temporary project
    local format_success=false
    if (cd "$temp_dir" && dotnet format --verbosity quiet 2>/dev/null); then
        # Copy formatted content back
        if cp "$temp_file" "$file"; then
            format_success=true
        fi
    fi

    # Clean up
    rm -rf "$temp_dir"

    return $([[ "$format_success" == true ]] && echo 0 || echo 1)
}

# Validate formatter setup
validate_formatter_setup() {
    hook_log "$LOG_LEVEL_INFO" "CSharpFormatter" "Validating C# formatter setup"

    if command -v dotnet &> /dev/null; then
        local version=$(dotnet --version 2>/dev/null)
        hook_log "$LOG_LEVEL_INFO" "CSharpFormatter" "dotnet CLI found: v$version"

        # Check if dotnet format is available
        if dotnet format --help &> /dev/null; then
            hook_log "$LOG_LEVEL_INFO" "CSharpFormatter" "dotnet format command available"
            return 0
        else
            hook_log "$LOG_LEVEL_ERROR" "CSharpFormatter" "dotnet format command not available"
            hook_log "$LOG_LEVEL_INFO" "CSharpFormatter" "Try: dotnet tool install -g dotnet-format"
            return 1
        fi
    else
        hook_log "$LOG_LEVEL_ERROR" "CSharpFormatter" "dotnet CLI not found"
        hook_log "$LOG_LEVEL_INFO" "CSharpFormatter" "Install from: https://dotnet.microsoft.com/download"
        return 1
    fi
}