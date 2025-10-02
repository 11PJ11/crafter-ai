#!/bin/bash
# AI-Craft Framework - Managed File
# Part of Claude Code SuperClaude modular hook system
# LanguageDetector - Project language detection module
# Part of Claude Code SuperClaude modular hook system

set -euo pipefail

# Source dependencies
HOOK_LIB_DIR="$(dirname "${BASH_SOURCE[0]}")/.."
source "${HOOK_LIB_DIR}/config/HookConfig.sh"
source "${HOOK_LIB_DIR}/logging/LogManager.sh"

# Language detection patterns
declare -A LANGUAGE_PATTERNS=(
    ["python"]="*.py"
    ["javascript"]="*.js,*.mjs"
    ["typescript"]="*.ts,*.tsx"
    ["csharp"]="*.cs,*.csproj"
    ["java"]="*.java,pom.xml,build.gradle"
    ["kotlin"]="*.kt,*.kts"
    ["go"]="*.go,go.mod"
    ["rust"]="*.rs,Cargo.toml"
    ["ruby"]="*.rb,Gemfile"
    ["php"]="*.php,composer.json"
    ["cpp"]="*.cpp,*.cxx,*.hpp,*.hxx,*.c,*.h,*.cc,CMakeLists.txt,meson.build"
    ["json"]="*.json"
    ["yaml"]="*.yml,*.yaml"
    ["markdown"]="*.md"
    ["css"]="*.css,*.scss,*.sass"
    ["shell"]="*.sh,*.bash"
)

# Package file patterns for enhanced detection
declare -A PACKAGE_PATTERNS=(
    ["python"]="requirements.txt,pyproject.toml,setup.py,Pipfile"
    ["javascript"]="package.json,yarn.lock"
    ["typescript"]="tsconfig.json,package.json"
    ["csharp"]="*.csproj,*.sln,global.json"
    ["java"]="pom.xml,build.gradle,gradle.properties"
    ["kotlin"]="build.gradle.kts,settings.gradle.kts"
    ["go"]="go.mod,go.sum"
    ["rust"]="Cargo.toml,Cargo.lock"
    ["ruby"]="Gemfile,Gemfile.lock,.ruby-version"
    ["php"]="composer.json,composer.lock"
    ["cpp"]="CMakeLists.txt,meson.build,Makefile,configure.ac,conanfile.txt"
)

# Detect languages in current project
detect_project_languages() {
    hook_log "$LOG_LEVEL_DEBUG" "LanguageDetector" "Starting language detection"

    local detected_languages=()
    local search_dirs=("." "src" "lib" "app" "tests" "test")

    # Check each language
    for lang in "${!LANGUAGE_PATTERNS[@]}"; do
        local patterns="${LANGUAGE_PATTERNS[$lang]}"
        local package_patterns="${PACKAGE_PATTERNS[$lang]:-}"
        local found=false

        # Check file patterns
        IFS=',' read -ra pattern_array <<< "$patterns"
        for pattern in "${pattern_array[@]}"; do
            for dir in "${search_dirs[@]}"; do
                if [[ -d "$dir" ]] && find "$dir" -name "$pattern" -type f | head -1 | grep -q .; then
                    found=true
                    break 2
                fi
            done

            # Also check current directory
            if find . -maxdepth 1 -name "$pattern" -type f | head -1 | grep -q .; then
                found=true
                break
            fi
        done

        # Check package patterns if file patterns not found
        if [[ "$found" = false && -n "$package_patterns" ]]; then
            IFS=',' read -ra pkg_pattern_array <<< "$package_patterns"
            for pkg_pattern in "${pkg_pattern_array[@]}"; do
                if find . -maxdepth 2 -name "$pkg_pattern" -type f | head -1 | grep -q .; then
                    found=true
                    break
                fi
            done
        fi

        # Add to detected languages if found
        if [[ "$found" = true ]]; then
            detected_languages+=("$lang")
            hook_log "$LOG_LEVEL_DEBUG" "LanguageDetector" "Detected language: $lang"
        fi
    done

    # Output detected languages
    printf '%s\n' "${detected_languages[@]}"

    hook_log "$LOG_LEVEL_INFO" "LanguageDetector" "Detection complete. Found: ${detected_languages[*]:-none}"
}

# Check if specific language is present
is_language_present() {
    local target_lang="$1"
    local languages
    mapfile -t languages < <(detect_project_languages)

    for lang in "${languages[@]}"; do
        if [[ "$lang" = "$target_lang" ]]; then
            return 0
        fi
    done
    return 1
}

# Get supported languages list
get_supported_languages() {
    printf '%s\n' "${!LANGUAGE_PATTERNS[@]}" | sort
}