# Claude Code Auto Lint & Format Hook

This hook automatically runs language-specific linters and formatters whenever Claude Code writes or edits source files.

## Features

- **Language Detection**: Automatically detects programming language based on file extension
- **Multi-Tool Support**: Uses the best available formatter/linter for each language
- **Intelligent Fallback Strategy**: Multi-tier dependency resolution with graceful degradation
- **Interactive Installation**: Prompts user to install missing tools automatically
- **Cross-Platform**: Works on Windows, macOS, and Linux with platform-specific optimizations
- **Dependency Management**: Intelligent handling of missing dependencies (jq, formatters, etc.)
- **JSON Parsing Resilience**: Multiple fallback strategies for reliable JSON processing

## Supported Languages & Tools

| Language | Formatters | Linters | Fallbacks |
|----------|------------|---------|-----------|
| JavaScript/TypeScript | Prettier, npm format | ESLint, npm lint | Project-local tools |
| Python | Black, Ruff, autopep8 | Ruff, flake8 | Syntax validation |
| C# | dotnet format | - | - |
| Go | gofmt, goimports | - | - |
| Rust | rustfmt | - | - |
| Java | google-java-format | - | - |
| CSS/SCSS | Prettier, stylelint | stylelint | - |
| JSON | Prettier | - | PowerShell, Python json.tool |
| YAML | Prettier | yamllint | - |
| Markdown | Prettier | markdownlint | - |
| Shell | shfmt | shellcheck | - |
| PowerShell | - | PSScriptAnalyzer | - |

## Installation

### Unix/Linux/macOS

1. **Copy the hook script** to your desired location:
   ```bash
   cp hooks/lint-format.sh ~/.claude/hooks/
   chmod +x ~/.claude/hooks/lint-format.sh
   ```

2. **Add hook configuration** to your Claude Code settings:

   **Project-specific configuration** (Add to your project's `.claude/settings.json`):
   ```json
   {
     "hooks": {
       "PostToolUse": [
         {
           "matcher": "Write|Edit|MultiEdit",
           "hooks": [
             {
               "type": "command",
               "command": "./hooks/lint-format.sh",
               "description": "Auto-lint and format source files"
             }
           ]
         }
       ]
     }
   }
   ```

### Windows

1. **Copy the hook script** to your desired location:
   ```cmd
   copy hooks\lint-format.bat %USERPROFILE%\.claude\hooks\
   ```

2. **Add hook configuration** to your Claude Code settings:

   **Project-specific configuration** (Add to your project's `.claude/settings.json`):
   ```json
   {
     "hooks": {
       "PostToolUse": [
         {
           "matcher": "Write|Edit|MultiEdit",
           "hooks": [
             {
               "type": "command",
               "command": "powershell.exe -Command \"$input = $input | Out-String; $json = $input | ConvertFrom-Json; $filePath = $json.tool_input.file_path; if ($filePath) { & 'C:/path/to/your/hooks/lint-format.bat' $filePath }\"",
               "description": "Auto-lint and format source files (Windows)"
             }
           ]
         }
       ]
     }
   }
   ```

   **Note**: Update the path `C:/path/to/your/hooks/lint-format.bat` to match your actual installation path.

### Global Configuration (All Platforms)

Add to `~/.claude/settings.json` (Unix/Linux/macOS) or `%USERPROFILE%\.claude\settings.json` (Windows):
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/lint-format.sh",
            "description": "Auto-lint and format source files"
          }
        ]
      }
    ]
  }
}
```

## Dependency Management & Intelligent Fallbacks

The hook includes sophisticated dependency management that addresses common issues:

### JSON Parsing Resilience
The hook uses multiple fallback strategies for JSON parsing to ensure reliable operation:

1. **Primary**: jq (if available) - Most efficient JSON processing
2. **Fallback 1**: Python - Widely available on most systems
3. **Fallback 2**: PowerShell (Windows) - Native Windows JSON processing
4. **Fallback 3**: Manual regex parsing - Basic cases as last resort

**jq Dependency Resolution**: When jq is missing, the hook will:
- Offer to install jq automatically with platform-specific package managers
- Gracefully fallback to Python/PowerShell if installation declined
- Continue operation without interruption

### Interactive Tool Installation

The hook will automatically prompt you to install missing tools when it encounters a file that needs formatting. You can:

1. **Let the hook install tools automatically** - When prompted, type 'y' and the hook will install the tool for you
2. **Install tools manually** - Use the commands below to pre-install tools

### Manual Installation (Optional)

#### JavaScript/TypeScript
```bash
npm install -g prettier eslint
# Or use project-local versions
npm install --save-dev prettier eslint
```

#### Python
```bash
pip install black ruff autopep8 flake8
```

#### C#
```bash
# dotnet format is included with .NET SDK
dotnet --version
```

#### Go
```bash
go install golang.org/x/tools/cmd/goimports@latest
```

#### Rust
```bash
# rustfmt is included with Rust installation
rustup component add rustfmt
```

#### CSS/Markdown
```bash
npm install -g prettier stylelint markdownlint-cli
```

#### Shell
```bash
# Install via package manager or Go
go install mvdan.cc/sh/v3/cmd/shfmt@latest
# shellcheck installation varies by OS
```

### Interactive Installation Process

When the hook detects a missing tool, you'll see:

```
⚠️  Prettier is not installed or not found in PATH
Would you like to install Prettier? (y/N): y
📦 Installing Prettier...
✅ Prettier installed successfully
✅ Prettier formatting applied
```

Simply type 'y' to install the tool, or 'N' to skip and continue without that tool.

## Configuration

The hook will automatically detect available tools and use them. No additional configuration is required, but you can customize tool behavior by adding configuration files:

- **Prettier**: `.prettierrc`
- **ESLint**: `.eslintrc.js`
- **Black**: `pyproject.toml`
- **Ruff**: `ruff.toml`
- **stylelint**: `.stylelintrc`

## Usage

Once installed, the hook runs automatically whenever Claude Code:
- Writes a new file (`Write` tool)
- Edits an existing file (`Edit` tool)
- Makes multiple edits (`MultiEdit` tool)

You'll see output like:
```
🔧 Auto-formatting src/components/Button.tsx
📝 Formatting JavaScript/TypeScript file...
✅ Prettier formatting applied
✅ ESLint fixes applied
🎉 Auto-formatting complete
```

## Troubleshooting

### Hook not running
- **Unix/Linux/macOS**: Verify the hook script is executable: `chmod +x path/to/lint-format.sh`
- **Windows**: Ensure PowerShell execution policy allows script execution
- Check Claude Code settings contain the correct hook configuration
- Ensure the script path is absolute or relative to project root

### JSON parsing errors (Resolved)
- ✅ **Fixed**: The hook now includes intelligent JSON parsing fallbacks
- If jq is missing, the hook automatically offers installation or uses Python/PowerShell
- No manual intervention required - the hook handles dependency issues gracefully

### Windows batch script syntax errors (Resolved)
- ✅ **Fixed**: Simplified batch script with robust error handling
- ✅ **Fixed**: PowerShell JSON parsing integration
- ✅ **Fixed**: Proper path handling and variable escaping

### Tools not found
- Install the required formatters/linters for your languages
- Verify tools are in your PATH: `which prettier`, `which black`, etc.
- For npm-based tools, ensure they're installed globally or locally in your project
- The hook will offer to install missing tools automatically

### Permission errors
- **Unix/Linux/macOS**: Make sure the hook script has execute permissions
- **Windows**: You may need to adjust PowerShell execution policy: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Common Issues & Solutions

#### "jq command not found"
- ✅ **Automatically resolved**: Hook now offers to install jq or uses fallback parsing
- Manual installation:
  - **macOS**: `brew install jq`
  - **Ubuntu/Debian**: `sudo apt-get install jq`
  - **Windows**: `choco install jq` or `scoop install jq`

#### Windows PowerShell syntax errors
- ✅ **Fixed**: Updated hook configuration with working PowerShell command
- Ensure you're using the latest `claude-hooks-config.json` configuration

#### Path not found errors on Windows
- ✅ **Fixed**: Improved path handling in batch script
- Use forward slashes in configuration paths: `C:/path/to/hooks/lint-format.bat`

## Customization

To add support for additional languages or tools:

1. Edit `hooks/lint-format.sh`
2. Add a new case in the file extension switch statement
3. Include the appropriate formatter and linter commands
4. Test with sample files

## Version History & Improvements

### Latest Version (Current)
- ✅ **Fixed**: Windows batch script syntax errors and hanging issues
- ✅ **Added**: Intelligent JSON parsing with multi-tier fallback system
- ✅ **Added**: Interactive jq installation with platform-specific package managers
- ✅ **Improved**: PowerShell integration for Windows Claude Code hooks
- ✅ **Enhanced**: Cross-platform compatibility and error handling
- ✅ **Added**: Support for PowerShell file formatting
- ✅ **Added**: Comprehensive dependency management framework

### Key Fixes Applied
1. **Root Cause Analysis**: Applied Toyota 5 Whys methodology to identify core issues
2. **Dependency Management**: Implemented systematic dependency detection and installation
3. **Platform Abstraction**: Created robust cross-platform compatibility layer
4. **Error Recovery**: Added graceful fallback strategies for all critical dependencies
5. **Testing Validation**: Comprehensive testing across multiple file types and scenarios

### Tested Functionality
- ✅ Python file formatting (Black)
- ✅ JSON file formatting (PowerShell fallback)
- ✅ JavaScript/TypeScript support
- ✅ Claude Code hook integration
- ✅ Windows PowerShell JSON parsing
- ✅ Cross-platform path handling

## Security Note

⚠️ **Important**: This hook executes shell commands automatically. Review the script carefully and ensure you trust all tools being executed. Consider running in a sandboxed environment if you have security concerns.