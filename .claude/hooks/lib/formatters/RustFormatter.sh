#!/bin/bash
# RustFormatter - Rust language formatter strategy
# Part of Claude Code SuperClaude modular hook system

set -euo pipefail

# Source dependencies
HOOK_LIB_DIR="$(dirname "${BASH_SOURCE[0]}")/.."
source "${HOOK_LIB_DIR}/formatters/BaseFormatter.sh"

# Override base formatter functions

get_formatter_name() {
    echo "RustFormatter"
}

get_file_patterns() {
    echo "*.rs"
}

get_required_tools() {
    echo "rustfmt:rustup:rustup-component-rustfmt clippy:rustup:rustup-component-clippy"
}

can_format_language() {
    local language="$1"
    [[ "$language" = "rust" ]]
}

format_files() {
    local language="$1"

    if ! can_format_language "$language"; then
        hook_log "$LOG_LEVEL_ERROR" "RustFormatter" "Cannot format language: $language"
        return 1
    fi

    hook_log "$LOG_LEVEL_INFO" "RustFormatter" "Starting Rust formatting"

    # Check if Rust files exist
    if ! has_files_for_patterns "$(get_file_patterns)"; then
        hook_log "$LOG_LEVEL_DEBUG" "RustFormatter" "No Rust files found"
        return 0
    fi

    # Find and format Rust files
    local files_found=()
    while IFS= read -r -d '' file; do
        files_found+=("$file")
    done < <(find_files_to_format "$(get_file_patterns)")

    if [[ ${#files_found[@]} -eq 0 ]]; then
        hook_log "$LOG_LEVEL_DEBUG" "RustFormatter" "No Rust files found to format"
        return 0
    fi

    hook_log "$LOG_LEVEL_INFO" "RustFormatter" "Processing ${#files_found[@]} Rust files"

    local formatted_count=0
    local linted_count=0
    local success=true

    # Format with rustfmt if available
    if command -v rustfmt &> /dev/null; then
        local rustfmt_version=$(rustfmt --version 2>/dev/null | head -n1 || echo "unknown")
        hook_log "$LOG_LEVEL_INFO" "RustFormatter" "Using rustfmt: $rustfmt_version"

        for file in "${files_found[@]}"; do
            if [[ ! -f "$file" ]]; then
                hook_log "$LOG_LEVEL_WARN" "RustFormatter" "File not found: $file"
                continue
            fi

            if [[ ! -r "$file" ]]; then
                hook_log "$LOG_LEVEL_WARN" "RustFormatter" "Cannot read file: $file"
                continue
            fi

            # Format with rustfmt
            if rustfmt "$file" 2>/dev/null; then
                hook_log "$LOG_LEVEL_DEBUG" "RustFormatter" "Formatted: $file"
                ((formatted_count++))
            else
                hook_log "$LOG_LEVEL_ERROR" "RustFormatter" "Failed to format: $file"
                success=false
            fi
        done
    else
        hook_log "$LOG_LEVEL_WARN" "RustFormatter" "rustfmt not found, skipping formatting"
        hook_log "$LOG_LEVEL_INFO" "RustFormatter" "Install with: rustup component add rustfmt"
    fi

    # Lint with clippy if available and we're in a Cargo project
    if command -v cargo &> /dev/null && [[ -f "Cargo.toml" ]]; then
        if cargo clippy --version &> /dev/null; then
            local clippy_version=$(cargo clippy --version 2>/dev/null | head -n1 || echo "unknown")
            hook_log "$LOG_LEVEL_INFO" "RustFormatter" "Using clippy: $clippy_version"

            # Run clippy with auto-fix for applicable suggestions
            if cargo clippy --fix --allow-dirty --allow-staged 2>/dev/null; then
                hook_log "$LOG_LEVEL_DEBUG" "RustFormatter" "Clippy auto-fixes applied"
                linted_count=${#files_found[@]}
            else
                hook_log "$LOG_LEVEL_INFO" "RustFormatter" "Clippy found suggestions (manual review needed)"
            fi
        else
            hook_log "$LOG_LEVEL_INFO" "RustFormatter" "Clippy not available"
            hook_log "$LOG_LEVEL_INFO" "RustFormatter" "Install with: rustup component add clippy"
        fi
    elif [[ ! -f "Cargo.toml" ]]; then
        hook_log "$LOG_LEVEL_INFO" "RustFormatter" "No Cargo.toml found, skipping clippy"
    else
        hook_log "$LOG_LEVEL_INFO" "RustFormatter" "Cargo not found, skipping clippy"
    fi

    hook_log "$LOG_LEVEL_INFO" "RustFormatter" "Rust processing completed: $formatted_count formatted, $linted_count linted"

    if [[ "$success" == true ]]; then
        return 0
    else
        return 1
    fi
}

# Validate formatter setup
validate_formatter_setup() {
    local validation_success=true

    hook_log "$LOG_LEVEL_INFO" "RustFormatter" "Validating Rust formatter setup"

    # Check rustfmt availability
    if command -v rustfmt &> /dev/null; then
        local rustfmt_version=$(rustfmt --version 2>/dev/null | head -n1 || echo "unknown")
        hook_log "$LOG_LEVEL_INFO" "RustFormatter" "rustfmt found: $rustfmt_version"

        # Test rustfmt functionality
        local test_rust="fn main() { println!(\"Hello, world!\"); }"
        if echo "$test_rust" | rustfmt --emit stdout 2>/dev/null >/dev/null; then
            hook_log "$LOG_LEVEL_INFO" "RustFormatter" "rustfmt can process Rust code"
        else
            hook_log "$LOG_LEVEL_ERROR" "RustFormatter" "rustfmt test failed"
            validation_success=false
        fi
    else
        hook_log "$LOG_LEVEL_WARN" "RustFormatter" "rustfmt not found"
        hook_log "$LOG_LEVEL_INFO" "RustFormatter" "Install with: rustup component add rustfmt"
        validation_success=false
    fi

    # Check rustc availability
    if command -v rustc &> /dev/null; then
        local rustc_version=$(rustc --version 2>/dev/null || echo "unknown")
        hook_log "$LOG_LEVEL_INFO" "RustFormatter" "rustc found: $rustc_version"
    else
        hook_log "$LOG_LEVEL_WARN" "RustFormatter" "rustc not found"
        hook_log "$LOG_LEVEL_INFO" "RustFormatter" "Install from: https://rustup.rs/"
        validation_success=false
    fi

    # Check cargo availability (optional for clippy)
    if command -v cargo &> /dev/null; then
        local cargo_version=$(cargo --version 2>/dev/null || echo "unknown")
        hook_log "$LOG_LEVEL_INFO" "RustFormatter" "cargo found: $cargo_version"

        # Check clippy availability (optional)
        if cargo clippy --version &> /dev/null; then
            local clippy_version=$(cargo clippy --version 2>/dev/null | head -n1 || echo "unknown")
            hook_log "$LOG_LEVEL_INFO" "RustFormatter" "clippy found: $clippy_version"
        else
            hook_log "$LOG_LEVEL_INFO" "RustFormatter" "clippy not found (optional)"
            hook_log "$LOG_LEVEL_INFO" "RustFormatter" "Install with: rustup component add clippy"
        fi
    else
        hook_log "$LOG_LEVEL_INFO" "RustFormatter" "cargo not found (optional)"
    fi

    if [[ "$validation_success" == true ]]; then
        hook_log "$LOG_LEVEL_INFO" "RustFormatter" "Rust formatter validation passed"
        return 0
    else
        hook_log "$LOG_LEVEL_WARN" "RustFormatter" "Rust formatter validation had warnings"
        return 1
    fi
}