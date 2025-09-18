#!/bin/bash

# Claude Code Auto Lint & Format Hook
# Automatically runs language-specific linters and formatters with dependency management

# Constants
readonly SCRIPT_NAME="Claude Code Auto Lint & Format"
readonly SUPPORTED_LANGUAGES="JavaScript/TypeScript|Python|C#|Go|Rust|Java|CSS/SCSS|JSON|YAML|Markdown|Shell"

# Messages
readonly MSG_STARTING="🔧 Auto-formatting"
readonly MSG_COMPLETE="🎉 Auto-formatting complete"
readonly MSG_SKIPPED="⚠️  Skipping - unsupported file type or missing tools"
readonly MSG_FORMAT_SUCCESS="✅"
readonly MSG_FORMAT_FAILED="❌"
readonly MSG_DEPENDENCY_MISSING="⚠️"
readonly MSG_INSTALL_PROMPT="Would you like to install"
readonly MSG_INSTALLING="📦 Installing"
readonly MSG_INSTALL_SUCCESS="✅ installed successfully"
readonly MSG_INSTALL_FAILED="❌ Installation failed"

# JSON parsing with intelligent fallback
parse_json() {
    local json_input="$1"
    local key="$2"

    # Try jq first if available
    if command -v jq >/dev/null 2>&1; then
        echo "$json_input" | jq -r ".$key // empty"
        return $?
    fi

    # Try Python as fallback
    if command -v python3 >/dev/null 2>&1; then
        echo "$json_input" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    keys = '$key'.split('.')
    value = data
    for k in keys:
        value = value.get(k, {})
    print(value if value != {} else '')
except:
    pass
"
        return $?
    elif command -v python >/dev/null 2>&1; then
        echo "$json_input" | python -c "
import json, sys
try:
    data = json.load(sys.stdin)
    keys = '$key'.split('.')
    value = data
    for k in keys:
        value = value.get(k, {})
    print(value if value != {} else '')
except:
    pass
"
        return $?
    fi

    # Manual parsing for simple cases as last resort
    case "$key" in
        "tool_input.file_path")
            echo "$json_input" | grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/'
            ;;
        *)
            echo ""
            ;;
    esac
}

# Install jq with user permission
install_jq() {
    echo "$MSG_DEPENDENCY_MISSING jq is not installed or not found in PATH"
    echo "$MSG_INSTALL_PROMPT jq for better JSON parsing? (y/N): "
    read -r response

    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "$MSG_INSTALLING jq..."

        # Detect OS and install appropriately
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            if command -v brew >/dev/null 2>&1; then
                brew install jq
            else
                echo "Homebrew not found. Please install jq manually: https://stedolan.github.io/jq/"
                return 1
            fi
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux
            if command -v apt-get >/dev/null 2>&1; then
                sudo apt-get update && sudo apt-get install -y jq
            elif command -v yum >/dev/null 2>&1; then
                sudo yum install -y jq
            elif command -v dnf >/dev/null 2>&1; then
                sudo dnf install -y jq
            elif command -v pacman >/dev/null 2>&1; then
                sudo pacman -S jq
            else
                echo "Package manager not found. Please install jq manually: https://stedolan.github.io/jq/"
                return 1
            fi
        elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
            # Git Bash/MSYS2/Cygwin on Windows
            echo "For Windows, please install jq manually: https://stedolan.github.io/jq/"
            echo "Or use Windows Subsystem for Linux (WSL)"
            return 1
        else
            echo "OS not detected. Please install jq manually: https://stedolan.github.io/jq/"
            return 1
        fi

        if [ $? -eq 0 ]; then
            echo "$MSG_INSTALL_SUCCESS jq $MSG_INSTALL_SUCCESS"
            return 0
        else
            echo "$MSG_INSTALL_FAILED for jq"
            return 1
        fi
    else
        echo "Continuing without jq (using Python fallback)"
        return 1
    fi
}

# Check tool availability and offer installation
check_and_install_tool() {
    local tool="$1"
    local install_cmd="$2"

    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "$MSG_DEPENDENCY_MISSING $tool is not installed or not found in PATH"
        echo "$MSG_INSTALL_PROMPT $tool? (y/N): "
        read -r response

        if [[ "$response" =~ ^[Yy]$ ]]; then
            echo "$MSG_INSTALLING $tool..."
            eval "$install_cmd"

            if [ $? -eq 0 ]; then
                echo "$MSG_INSTALL_SUCCESS $tool $MSG_INSTALL_SUCCESS"
                return 0
            else
                echo "$MSG_INSTALL_FAILED for $tool"
                return 1
            fi
        else
            return 1
        fi
    fi
    return 0
}

# Try formatting with multiple tools
try_multiple_formatters() {
    local file_path="$1"
    local tool1="$2"
    local cmd1="$3"
    local tool2="$4"
    local cmd2="$5"

    # Try first tool
    if command -v "$tool1" >/dev/null 2>&1; then
        echo "📝 Formatting with $tool1..."
        eval "$cmd1"
        if [ $? -eq 0 ]; then
            echo "$MSG_FORMAT_SUCCESS $tool1 formatting applied"
            return 0
        else
            echo "$MSG_FORMAT_FAILED $tool1 formatting failed"
        fi
    elif check_and_install_tool "$tool1" "npm install -g $tool1"; then
        echo "📝 Formatting with $tool1..."
        eval "$cmd1"
        if [ $? -eq 0 ]; then
            echo "$MSG_FORMAT_SUCCESS $tool1 formatting applied"
            return 0
        fi
    fi

    # Try second tool if provided
    if [ -n "$tool2" ] && [ -n "$cmd2" ]; then
        if command -v "$tool2" >/dev/null 2>&1; then
            echo "📝 Formatting with $tool2..."
            eval "$cmd2"
            if [ $? -eq 0 ]; then
                echo "$MSG_FORMAT_SUCCESS $tool2 formatting applied"
                return 0
            else
                echo "$MSG_FORMAT_FAILED $tool2 formatting failed"
            fi
        elif check_and_install_tool "$tool2" "pip install $tool2"; then
            echo "📝 Formatting with $tool2..."
            eval "$cmd2"
            if [ $? -eq 0 ]; then
                echo "$MSG_FORMAT_SUCCESS $tool2 formatting applied"
                return 0
            fi
        fi
    fi

    return 1
}

# Format JavaScript/TypeScript files
format_javascript() {
    local file_path="$1"
    echo "📝 Formatting JavaScript/TypeScript file..."

    local success=false

    # Try Prettier first, then ESLint
    if try_multiple_formatters "$file_path" "prettier" "prettier --write \"$file_path\"" "eslint" "eslint --fix \"$file_path\""; then
        success=true
    fi

    # Try project-local prettier
    if [ "$success" = false ] && [ -f "node_modules/.bin/prettier" ]; then
        echo "📝 Using project-local prettier..."
        ./node_modules/.bin/prettier --write "$file_path"
        if [ $? -eq 0 ]; then
            echo "$MSG_FORMAT_SUCCESS Prettier formatting applied"
            success=true
        fi
    fi

    # Try project-local eslint
    if [ "$success" = false ] && [ -f "node_modules/.bin/eslint" ]; then
        echo "📝 Using project-local eslint..."
        ./node_modules/.bin/eslint --fix "$file_path"
        if [ $? -eq 0 ]; then
            echo "$MSG_FORMAT_SUCCESS ESLint fixes applied"
            success=true
        fi
    fi

    # Try npm scripts as fallback
    if [ "$success" = false ] && [ -f "package.json" ]; then
        if grep -q '"format"' package.json; then
            echo "📝 Using npm format script..."
            npm run format
            success=true
        elif grep -q '"lint"' package.json; then
            echo "📝 Using npm lint script..."
            npm run lint
            success=true
        fi
    fi

    [ "$success" = true ]
}

# Format Python files
format_python() {
    local file_path="$1"
    echo "📝 Formatting Python file..."

    # Try Black first, then autopep8, then Ruff, then flake8
    if try_multiple_formatters "$file_path" "black" "black \"$file_path\"" "autopep8" "autopep8 --in-place \"$file_path\""; then
        return 0
    fi

    # Try Ruff
    if command -v ruff >/dev/null 2>&1; then
        echo "📝 Formatting with Ruff..."
        ruff format "$file_path"
        if [ $? -eq 0 ]; then
            echo "$MSG_FORMAT_SUCCESS Ruff formatting applied"
            return 0
        fi
    elif check_and_install_tool "ruff" "pip install ruff"; then
        ruff format "$file_path"
        if [ $? -eq 0 ]; then
            echo "$MSG_FORMAT_SUCCESS Ruff formatting applied"
            return 0
        fi
    fi

    # Try flake8 for linting
    if command -v flake8 >/dev/null 2>&1; then
        echo "📝 Linting with flake8..."
        flake8 "$file_path"
        if [ $? -eq 0 ]; then
            echo "$MSG_FORMAT_SUCCESS flake8 linting passed"
            return 0
        fi
    fi

    return 1
}

# Format other file types
format_csharp() {
    local file_path="$1"
    echo "📝 Formatting C# file..."

    if command -v dotnet >/dev/null 2>&1; then
        dotnet format --include "$file_path"
        if [ $? -eq 0 ]; then
            echo "$MSG_FORMAT_SUCCESS dotnet format applied"
            return 0
        fi
    fi
    return 1
}

format_go() {
    local file_path="$1"
    echo "📝 Formatting Go file..."

    if try_multiple_formatters "$file_path" "gofmt" "gofmt -w \"$file_path\"" "goimports" "goimports -w \"$file_path\""; then
        return 0
    fi
    return 1
}

format_rust() {
    local file_path="$1"
    echo "📝 Formatting Rust file..."

    if command -v rustfmt >/dev/null 2>&1; then
        rustfmt "$file_path"
        if [ $? -eq 0 ]; then
            echo "$MSG_FORMAT_SUCCESS rustfmt applied"
            return 0
        fi
    fi
    return 1
}

format_java() {
    local file_path="$1"
    echo "📝 Formatting Java file..."

    if command -v google-java-format >/dev/null 2>&1; then
        google-java-format --replace "$file_path"
        if [ $? -eq 0 ]; then
            echo "$MSG_FORMAT_SUCCESS google-java-format applied"
            return 0
        fi
    fi
    return 1
}

format_css() {
    local file_path="$1"
    echo "📝 Formatting CSS/SCSS file..."

    if try_multiple_formatters "$file_path" "prettier" "prettier --write \"$file_path\"" "stylelint" "stylelint --fix \"$file_path\""; then
        return 0
    fi
    return 1
}

format_json() {
    local file_path="$1"
    echo "📝 Formatting JSON file..."

    # Try prettier first
    if command -v prettier >/dev/null 2>&1; then
        prettier --write "$file_path"
        if [ $? -eq 0 ]; then
            echo "$MSG_FORMAT_SUCCESS Prettier formatting applied"
            return 0
        fi
    fi

    # Try jq as fallback
    if command -v jq >/dev/null 2>&1; then
        jq . "$file_path" > "${file_path}.tmp" && mv "${file_path}.tmp" "$file_path"
        if [ $? -eq 0 ]; then
            echo "$MSG_FORMAT_SUCCESS jq formatting applied"
            return 0
        fi
    fi

    # Try Python json.tool
    if command -v python3 >/dev/null 2>&1; then
        python3 -m json.tool "$file_path" "${file_path}.tmp" && mv "${file_path}.tmp" "$file_path"
        if [ $? -eq 0 ]; then
            echo "$MSG_FORMAT_SUCCESS Python json.tool formatting applied"
            return 0
        fi
    fi

    return 1
}

format_yaml() {
    local file_path="$1"
    echo "📝 Formatting YAML file..."

    if try_multiple_formatters "$file_path" "prettier" "prettier --write \"$file_path\"" "yamllint" "yamllint \"$file_path\""; then
        return 0
    fi
    return 1
}

format_markdown() {
    local file_path="$1"
    echo "📝 Formatting Markdown file..."

    if try_multiple_formatters "$file_path" "prettier" "prettier --write \"$file_path\"" "markdownlint" "markdownlint --fix \"$file_path\""; then
        return 0
    fi
    return 1
}

format_shell() {
    local file_path="$1"
    echo "📝 Formatting Shell script..."

    # Try shfmt first, then shellcheck
    if try_multiple_formatters "$file_path" "shfmt" "shfmt -w \"$file_path\"" "shellcheck" "shellcheck \"$file_path\""; then
        return 0
    fi
    return 1
}

# Main formatting dispatch
dispatch_formatter() {
    local file_path="$1"
    local extension="${file_path##*.}"
    local basename_ext="${file_path##*/}"

    case "$extension" in
        js|jsx|ts|tsx|mjs)
            format_javascript "$file_path"
            ;;
        py)
            format_python "$file_path"
            ;;
        cs)
            format_csharp "$file_path"
            ;;
        go)
            format_go "$file_path"
            ;;
        rs)
            format_rust "$file_path"
            ;;
        java)
            format_java "$file_path"
            ;;
        css|scss|sass|less)
            format_css "$file_path"
            ;;
        json)
            format_json "$file_path"
            ;;
        yml|yaml)
            format_yaml "$file_path"
            ;;
        md|markdown)
            format_markdown "$file_path"
            ;;
        sh|bash|zsh)
            format_shell "$file_path"
            ;;
        *)
            # Check for specific filenames
            case "$basename_ext" in
                Dockerfile|dockerfile)
                    echo "📝 Dockerfile detected - no standard formatter available"
                    return 1
                    ;;
                *)
                    echo "📝 Unsupported file type: $extension"
                    return 1
                    ;;
            esac
            ;;
    esac
}

# Main execution
main() {
    # Check if jq is available, offer to install if not
    if ! command -v jq >/dev/null 2>&1; then
        install_jq
    fi

    # Get file path from Claude Code hook input
    local file_path=""
    if [ $# -gt 0 ]; then
        # Direct file path argument
        file_path="$1"
    else
        # Parse from stdin (Claude Code hook format)
        local json_input
        json_input=$(cat)
        if [ -n "$json_input" ]; then
            file_path=$(parse_json "$json_input" "tool_input.file_path")
        fi
    fi

    if [ -z "$file_path" ]; then
        echo "❌ No file path provided"
        exit 1
    fi

    if [ ! -f "$file_path" ]; then
        echo "❌ File not found: $file_path"
        exit 1
    fi

    echo "$MSG_STARTING $file_path"
    echo "🔍 Supported languages: $SUPPORTED_LANGUAGES"

    if dispatch_formatter "$file_path"; then
        echo "$MSG_COMPLETE"
        exit 0
    else
        echo "$MSG_SKIPPED"
        exit 0
    fi
}

# Execute main function
main "$@"