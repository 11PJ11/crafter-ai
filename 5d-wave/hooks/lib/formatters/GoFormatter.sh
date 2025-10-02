#!/bin/bash
# AI-Craft Framework - Managed File
# Part of Claude Code SuperClaude modular hook system
# GoFormatter - Go language formatter strategy
# Part of Claude Code SuperClaude modular hook system

set -euo pipefail

# Source dependencies
HOOK_LIB_DIR="$(dirname "${BASH_SOURCE[0]}")/.."
source "${HOOK_LIB_DIR}/formatters/BaseFormatter.sh"

# Override base formatter functions

get_formatter_name() {
    echo "GoFormatter"
}

get_file_patterns() {
    echo "*.go"
}

get_required_tools() {
    echo "gofmt:go:golang goimports:go:golang.org/x/tools/cmd/goimports gofumpt:go:mvdan.cc/gofumpt"
}

can_format_language() {
    local language="$1"
    [[ "$language" = "go" ]]
}

format_files() {
    local language="$1"

    if ! can_format_language "$language"; then
        hook_log "$LOG_LEVEL_ERROR" "GoFormatter" "Cannot format language: $language"
        return 1
    fi

    hook_log "$LOG_LEVEL_INFO" "GoFormatter" "Starting Go formatting"

    # Check if Go files exist
    if ! has_files_for_patterns "$(get_file_patterns)"; then
        hook_log "$LOG_LEVEL_DEBUG" "GoFormatter" "No Go files found"
        return 0
    fi

    # Find and format Go files
    local files_found=()
    while IFS= read -r -d '' file; do
        files_found+=("$file")
    done < <(find_files_to_format "$(get_file_patterns)")

    if [[ ${#files_found[@]} -eq 0 ]]; then
        hook_log "$LOG_LEVEL_DEBUG" "GoFormatter" "No Go files found to format"
        return 0
    fi

    hook_log "$LOG_LEVEL_INFO" "GoFormatter" "Processing ${#files_found[@]} Go files"

    local formatted_count=0
    local imports_fixed=0
    local success=true

    # Step 1: Format with gofumpt (enhanced gofmt) if available, otherwise gofmt
    if command -v gofumpt &> /dev/null; then
        local gofumpt_version=$(gofumpt --version 2>/dev/null || echo "unknown")
        hook_log "$LOG_LEVEL_INFO" "GoFormatter" "Using gofumpt: $gofumpt_version"

        for file in "${files_found[@]}"; do
            if [[ ! -f "$file" ]]; then
                hook_log "$LOG_LEVEL_WARN" "GoFormatter" "File not found: $file"
                continue
            fi

            if [[ ! -r "$file" ]]; then
                hook_log "$LOG_LEVEL_WARN" "GoFormatter" "Cannot read file: $file"
                continue
            fi

            # Format with gofumpt (writes in-place)
            if gofumpt -w "$file" 2>/dev/null; then
                hook_log "$LOG_LEVEL_DEBUG" "GoFormatter" "Formatted (gofumpt): $file"
                ((formatted_count++))
            else
                hook_log "$LOG_LEVEL_ERROR" "GoFormatter" "Failed to format with gofumpt: $file"
                success=false
            fi
        done

    elif command -v gofmt &> /dev/null; then
        local gofmt_version=$(go version 2>/dev/null | awk '{print $3}' || echo "unknown")
        hook_log "$LOG_LEVEL_INFO" "GoFormatter" "Using gofmt (Go $gofmt_version)"

        for file in "${files_found[@]}"; do
            if [[ ! -f "$file" ]]; then
                hook_log "$LOG_LEVEL_WARN" "GoFormatter" "File not found: $file"
                continue
            fi

            if [[ ! -r "$file" ]]; then
                hook_log "$LOG_LEVEL_WARN" "GoFormatter" "Cannot read file: $file"
                continue
            fi

            # Format with gofmt (writes in-place)
            if gofmt -w "$file" 2>/dev/null; then
                hook_log "$LOG_LEVEL_DEBUG" "GoFormatter" "Formatted (gofmt): $file"
                ((formatted_count++))
            else
                hook_log "$LOG_LEVEL_ERROR" "GoFormatter" "Failed to format with gofmt: $file"
                success=false
            fi
        done
    else
        hook_log "$LOG_LEVEL_WARN" "GoFormatter" "Neither gofmt nor gofumpt found, skipping formatting"
        hook_log "$LOG_LEVEL_INFO" "GoFormatter" "Install Go from: https://golang.org/dl/"
    fi

    # Step 2: Fix imports with goimports if available
    if command -v goimports &> /dev/null; then
        hook_log "$LOG_LEVEL_INFO" "GoFormatter" "Using goimports for import management"

        for file in "${files_found[@]}"; do
            if [[ ! -f "$file" ]]; then
                continue
            fi

            # Fix imports with goimports (writes in-place)
            if goimports -w "$file" 2>/dev/null; then
                hook_log "$LOG_LEVEL_DEBUG" "GoFormatter" "Fixed imports: $file"
                ((imports_fixed++))
            else
                hook_log "$LOG_LEVEL_WARN" "GoFormatter" "Failed to fix imports: $file"
                # Don't fail on import issues, just log warnings
            fi
        done
    else
        hook_log "$LOG_LEVEL_INFO" "GoFormatter" "goimports not found, skipping import optimization"
        hook_log "$LOG_LEVEL_INFO" "GoFormatter" "Install with: go install golang.org/x/tools/cmd/goimports@latest"
    fi

    # Step 3: Validate syntax if go build is possible
    if command -v go &> /dev/null && [[ -f "go.mod" ]]; then
        hook_log "$LOG_LEVEL_INFO" "GoFormatter" "Validating Go syntax"

        if go vet ./... 2>/dev/null; then
            hook_log "$LOG_LEVEL_DEBUG" "GoFormatter" "Go vet passed"
        else
            hook_log "$LOG_LEVEL_INFO" "GoFormatter" "Go vet found suggestions (review recommended)"
        fi
    elif [[ ! -f "go.mod" ]]; then
        hook_log "$LOG_LEVEL_INFO" "GoFormatter" "No go.mod found, skipping go vet"
    fi

    hook_log "$LOG_LEVEL_INFO" "GoFormatter" "Go processing completed: $formatted_count formatted, $imports_fixed imports fixed"

    if [[ "$success" == true ]]; then
        return 0
    else
        return 1
    fi
}

# Validate formatter setup
validate_formatter_setup() {
    local validation_success=true

    hook_log "$LOG_LEVEL_INFO" "GoFormatter" "Validating Go formatter setup"

    # Check Go installation
    if command -v go &> /dev/null; then
        local go_version=$(go version 2>/dev/null | awk '{print $3}' || echo "unknown")
        hook_log "$LOG_LEVEL_INFO" "GoFormatter" "Go found: $go_version"
    else
        hook_log "$LOG_LEVEL_WARN" "GoFormatter" "Go not found"
        hook_log "$LOG_LEVEL_INFO" "GoFormatter" "Install from: https://golang.org/dl/"
        validation_success=false
    fi

    # Check gofmt availability (should come with Go)
    if command -v gofmt &> /dev/null; then
        hook_log "$LOG_LEVEL_INFO" "GoFormatter" "gofmt found (included with Go)"

        # Test gofmt functionality
        local test_go="package main\n\nimport \"fmt\"\n\nfunc main() {\nfmt.Println(\"Hello\")\n}"
        if echo -e "$test_go" | gofmt >/dev/null 2>&1; then
            hook_log "$LOG_LEVEL_INFO" "GoFormatter" "gofmt can process Go code"
        else
            hook_log "$LOG_LEVEL_ERROR" "GoFormatter" "gofmt test failed"
            validation_success=false
        fi
    else
        hook_log "$LOG_LEVEL_ERROR" "GoFormatter" "gofmt not found"
        validation_success=false
    fi

    # Check gofumpt availability (optional, enhanced formatter)
    if command -v gofumpt &> /dev/null; then
        local gofumpt_version=$(gofumpt --version 2>/dev/null || echo "unknown")
        hook_log "$LOG_LEVEL_INFO" "GoFormatter" "gofumpt found: $gofumpt_version"
    else
        hook_log "$LOG_LEVEL_INFO" "GoFormatter" "gofumpt not found (optional enhancement)"
        hook_log "$LOG_LEVEL_INFO" "GoFormatter" "Install with: go install mvdan.cc/gofumpt@latest"
    fi

    # Check goimports availability (optional, import management)
    if command -v goimports &> /dev/null; then
        hook_log "$LOG_LEVEL_INFO" "GoFormatter" "goimports found"
    else
        hook_log "$LOG_LEVEL_INFO" "GoFormatter" "goimports not found (optional)"
        hook_log "$LOG_LEVEL_INFO" "GoFormatter" "Install with: go install golang.org/x/tools/cmd/goimports@latest"
    fi

    if [[ "$validation_success" == true ]]; then
        hook_log "$LOG_LEVEL_INFO" "GoFormatter" "Go formatter validation passed"
        return 0
    else
        hook_log "$LOG_LEVEL_WARN" "GoFormatter" "Go formatter validation had warnings"
        return 1
    fi
}