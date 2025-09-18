@echo off
setlocal enabledelayedexpansion

rem Claude Code Auto Lint & Format Hook for Windows
rem Simplified working version with core functionality

echo 🔧 Auto-formatting %1

if "%~1"=="" (
    echo ❌ No file path provided
    exit /b 1
)

if not exist "%~1" (
    echo ❌ File not found: %~1
    exit /b 1
)

rem Get file extension
set "file_path=%~1"
set "extension=%~x1"
set "extension=!extension:~1!"

echo 📝 Processing file type: !extension!

rem Format based on extension
if /i "!extension!"=="py" goto format_python
if /i "!extension!"=="js" goto format_javascript
if /i "!extension!"=="ts" goto format_javascript
if /i "!extension!"=="jsx" goto format_javascript
if /i "!extension!"=="tsx" goto format_javascript
if /i "!extension!"=="json" goto format_json
if /i "!extension!"=="cs" goto format_csharp

echo ⚠️ Unsupported file type: !extension!
exit /b 0

:format_python
echo 📝 Formatting Python file...

where black >nul 2>&1
if %errorlevel% equ 0 (
    echo 📝 Using black formatter...
    black "!file_path!"
    if !errorlevel! equ 0 (
        echo ✅ black formatting applied
        goto success
    ) else (
        echo ❌ black formatting failed
    )
)

where python >nul 2>&1
if %errorlevel% equ 0 (
    echo 📝 Checking Python syntax...
    python -m py_compile "!file_path!"
    if !errorlevel! equ 0 (
        echo ✅ Python syntax check passed
        goto success
    ) else (
        echo ❌ Python syntax errors found
    )
)

echo ⚠️ No Python formatters available
exit /b 0

:format_javascript
echo 📝 Formatting JavaScript/TypeScript file...

where prettier >nul 2>&1
if %errorlevel% equ 0 (
    echo 📝 Using prettier formatter...
    prettier --write "!file_path!"
    if !errorlevel! equ 0 (
        echo ✅ prettier formatting applied
        goto success
    ) else (
        echo ❌ prettier formatting failed
    )
)

where eslint >nul 2>&1
if %errorlevel% equ 0 (
    echo 📝 Using eslint formatter...
    eslint --fix "!file_path!"
    if !errorlevel! equ 0 (
        echo ✅ eslint formatting applied
        goto success
    ) else (
        echo ❌ eslint formatting failed
    )
)

echo ⚠️ No JavaScript/TypeScript formatters available
exit /b 0

:format_json
echo 📝 Formatting JSON file...

where prettier >nul 2>&1
if %errorlevel% equ 0 (
    echo 📝 Using prettier formatter...
    prettier --write "!file_path!"
    if !errorlevel! equ 0 (
        echo ✅ prettier formatting applied
        goto success
    ) else (
        echo ❌ prettier formatting failed
    )
)

echo 📝 Using PowerShell JSON formatter...
powershell -NoProfile -Command "try { $json = Get-Content '!file_path!' -Raw | ConvertFrom-Json; $json | ConvertTo-Json -Depth 100 | Set-Content '!file_path!' -Encoding UTF8; Write-Host '✅ PowerShell JSON formatting applied'; exit 0 } catch { Write-Host '❌ JSON formatting failed'; exit 1 }"
if !errorlevel! equ 0 goto success

echo ⚠️ No JSON formatters available
exit /b 0

:format_csharp
echo 📝 Formatting C# file...

where dotnet >nul 2>&1
if %errorlevel% equ 0 (
    echo 📝 Using dotnet format...
    dotnet format --include "!file_path!"
    if !errorlevel! equ 0 (
        echo ✅ dotnet format applied
        goto success
    ) else (
        echo ❌ dotnet format failed
    )
)

echo ⚠️ No C# formatters available
exit /b 0

:success
echo 🎉 Auto-formatting complete
exit /b 0