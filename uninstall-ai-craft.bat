@echo off
REM AI-Craft Framework Uninstallation Script for Windows
REM Completely removes AI-Craft framework from global Claude config directory
REM 
REM Usage: uninstall-ai-craft.bat [--backup] [--force] [--help]

setlocal enabledelayedexpansion

REM Script configuration
set "SCRIPT_DIR=%~dp0"
set "CLAUDE_CONFIG_DIR=%USERPROFILE%\.claude"
set "UNINSTALL_LOG=%CLAUDE_CONFIG_DIR%\ai-craft-uninstall.log"

REM Get current timestamp for backup
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set "BACKUP_TIMESTAMP=%datetime:~0,8%-%datetime:~8,6%"
set "BACKUP_DIR=%CLAUDE_CONFIG_DIR%\backups\ai-craft-uninstall-%BACKUP_TIMESTAMP%"

REM Default options
set BACKUP_BEFORE_REMOVAL=false
set FORCE_REMOVAL=false

REM Check command line arguments
if "%~1"=="--help" goto :show_help
if "%~1"=="-h" goto :show_help
if "%~1"=="--backup" set BACKUP_BEFORE_REMOVAL=true
if "%~1"=="--force" set FORCE_REMOVAL=true
if "%~2"=="--backup" set BACKUP_BEFORE_REMOVAL=true
if "%~2"=="--force" set FORCE_REMOVAL=true
if not "%~1"=="" if not "%~1"=="--backup" if not "%~1"=="--force" (
    echo ERROR: Unknown option: %~1
    echo Use --help for usage information
    exit /b 1
)

REM Main uninstallation process
goto :main

:show_help
echo AI-Craft Framework Uninstallation Script for Windows
echo.
echo DESCRIPTION:
echo     Completely removes the AI-Craft ATDD agent framework from your global Claude config directory.
echo     This removes all 41+ specialized agents, commands, configuration files, logs, and backups.
echo.
echo USAGE:
echo     %~nx0 [OPTIONS]
echo.
echo OPTIONS:
echo     --backup         Create backup before removal (recommended)
echo     --force          Skip confirmation prompts
echo     --help           Show this help message
echo.
echo EXAMPLES:
echo     %~nx0                      # Interactive uninstall with confirmation
echo     %~nx0 --backup             # Create backup before removal
echo     %~nx0 --force              # Uninstall without confirmation prompts
echo.
echo WHAT GETS REMOVED:
echo     - All AI-Craft agents in agents/cai/ directory
echo     - All CAI commands in commands/cai/ directory (10 essential commands)
echo     - AI-Craft configuration files (constants.md, manifest)
echo     - Claude Code workflow hooks for CAI agents
echo     - AI-Craft installation logs and backup directories
echo     - AI-Craft project state files
echo.
echo IMPORTANT:
echo     This action cannot be undone unless you use --backup option.
echo     All customizations and local changes will be lost.
echo.
exit /b 0

:log_message
set "level=%~1"
set "message=%~2"
echo [%date% %time%] %level%: %message%
echo [%date% %time%] %level%: %message% >> "%UNINSTALL_LOG%" 2>nul
goto :eof

:info
call :log_message "INFO" "%~1"
goto :eof

:warn
call :log_message "WARN" "%~1"
goto :eof

:error_msg
call :log_message "ERROR" "%~1"
goto :eof

:check_installation
call :info "Checking for AI-Craft installation..."

set INSTALLATION_FOUND=false

REM Check for agents directory
if exist "%CLAUDE_CONFIG_DIR%\agents\cai" (
    set INSTALLATION_FOUND=true
    call :info "Found AI-Craft agents in: %CLAUDE_CONFIG_DIR%\agents\cai"
)

REM Check for commands directory
if exist "%CLAUDE_CONFIG_DIR%\commands\cai" (
    set INSTALLATION_FOUND=true
    call :info "Found AI-Craft commands in: %CLAUDE_CONFIG_DIR%\commands\cai"
)

REM Check for configuration files
if exist "%CLAUDE_CONFIG_DIR%\agents\cai\constants.md" (
    set INSTALLATION_FOUND=true
    call :info "Found AI-Craft configuration files"
)

REM Check for manifest
if exist "%CLAUDE_CONFIG_DIR%\ai-craft-manifest.txt" (
    set INSTALLATION_FOUND=true
    call :info "Found AI-Craft manifest file"
)

REM Check for installation logs
if exist "%CLAUDE_CONFIG_DIR%\ai-craft-install.log" (
    set INSTALLATION_FOUND=true
    call :info "Found AI-Craft installation logs"
)

REM Check for hooks directory
if exist "%CLAUDE_CONFIG_DIR%\hooks\cai" (
    set INSTALLATION_FOUND=true
    call :info "Found AI-Craft hooks in: %CLAUDE_CONFIG_DIR%\hooks\cai"
)

REM Check for backup directories
for /d %%D in ("%CLAUDE_CONFIG_DIR%\backups\ai-craft-*") do (
    set INSTALLATION_FOUND=true
    call :info "Found AI-Craft backup directories"
    goto :installation_check_done
)

:installation_check_done
if "%INSTALLATION_FOUND%"=="false" (
    call :info "No AI-Craft installation found"
    echo.
    echo No AI-Craft framework installation detected.
    echo Nothing to uninstall.
    exit /b 0
)

goto :eof

:confirm_removal
if "%FORCE_REMOVAL%"=="true" goto :eof

echo.
echo WARNING: This will completely remove the AI-Craft framework from your system.
echo.
echo The following will be removed:
echo   - All AI-Craft agents (41+ specialized agents)
echo   - All CAI commands (10 essential commands: brown-analyze, refactor, start, etc.)
echo   - Configuration files (constants.md, manifest)
echo   - Claude Code workflow hooks for CAI agents
echo   - Installation logs and backup directories
echo   - Any customizations or local changes
echo.

if "%BACKUP_BEFORE_REMOVAL%"=="true" (
    echo A backup will be created before removal at:
    echo   %BACKUP_DIR%
    echo.
) else (
    echo WARNING: No backup will be created. This action cannot be undone.
    echo To create a backup, cancel and run with --backup option.
    echo.
)

set /p CONFIRM="Are you sure you want to proceed? (y/N): "
if /i not "%CONFIRM%"=="y" if /i not "%CONFIRM%"=="yes" (
    echo.
    echo Uninstallation cancelled by user.
    exit /b 0
)

goto :eof

:create_backup
if "%BACKUP_BEFORE_REMOVAL%"=="false" goto :eof

call :info "Creating backup before removal..."

mkdir "%BACKUP_DIR%" 2>nul

REM Backup agents directory if it exists
if exist "%CLAUDE_CONFIG_DIR%\agents\cai" (
    mkdir "%BACKUP_DIR%\agents" 2>nul
    xcopy "%CLAUDE_CONFIG_DIR%\agents\cai" "%BACKUP_DIR%\agents\cai\" /E /I /Q >nul
    call :info "Backed up agents directory"
)

REM Backup commands directory if it exists
if exist "%CLAUDE_CONFIG_DIR%\commands\cai" (
    mkdir "%BACKUP_DIR%\commands" 2>nul
    xcopy "%CLAUDE_CONFIG_DIR%\commands\cai" "%BACKUP_DIR%\commands\cai\" /E /I /Q >nul
    call :info "Backed up commands directory"
)

REM Backup hooks directory if it exists
if exist "%CLAUDE_CONFIG_DIR%\hooks\cai" (
    mkdir "%BACKUP_DIR%\hooks" 2>nul
    xcopy "%CLAUDE_CONFIG_DIR%\hooks\cai" "%BACKUP_DIR%\hooks\cai\" /E /I /Q >nul
    call :info "Backed up CAI hooks directory"
)

REM Backup current settings.local.json
if exist "%CLAUDE_CONFIG_DIR%\settings.local.json" (
    copy "%CLAUDE_CONFIG_DIR%\settings.local.json" "%BACKUP_DIR%\settings.local.json.backup" >nul
    call :info "Backed up settings.local.json"
)

REM Backup configuration files
if exist "%CLAUDE_CONFIG_DIR%\ai-craft-manifest.txt" (
    copy "%CLAUDE_CONFIG_DIR%\ai-craft-manifest.txt" "%BACKUP_DIR%\" >nul
    call :info "Backed up manifest file"
)

if exist "%CLAUDE_CONFIG_DIR%\ai-craft-install.log" (
    copy "%CLAUDE_CONFIG_DIR%\ai-craft-install.log" "%BACKUP_DIR%\" >nul
    call :info "Backed up installation log"
)

REM Create backup manifest
(
echo AI-Craft Framework Uninstall Backup
echo Created: %date% %time%
echo Source: %COMPUTERNAME%:%CLAUDE_CONFIG_DIR%
echo Backup Type: Pre-uninstall backup
echo Backup contents:
echo   - AI-Craft agents and commands
echo   - Configuration files and logs
echo   - Complete framework state before removal
) > "%BACKUP_DIR%\uninstall-backup-manifest.txt"

call :info "Backup created successfully at: %BACKUP_DIR%"
goto :eof

:remove_agents
call :info "Removing AI-Craft agents..."

if exist "%CLAUDE_CONFIG_DIR%\agents\cai" (
    rmdir /s /q "%CLAUDE_CONFIG_DIR%\agents\cai" 2>nul
    call :info "Removed agents/cai directory"
)

REM Remove agents directory if it's empty and only contained cai
if exist "%CLAUDE_CONFIG_DIR%\agents" (
    rmdir "%CLAUDE_CONFIG_DIR%\agents" 2>nul
    if errorlevel 1 (
        call :info "Kept agents directory (contains other files)"
    ) else (
        call :info "Removed empty agents directory"
    )
)

goto :eof

:remove_commands
call :info "Removing AI-Craft commands..."

if exist "%CLAUDE_CONFIG_DIR%\commands\cai" (
    rmdir /s /q "%CLAUDE_CONFIG_DIR%\commands\cai" 2>nul
    call :info "Removed commands/cai directory"
)

REM Remove commands directory if it's empty and only contained cai
if exist "%CLAUDE_CONFIG_DIR%\commands" (
    rmdir "%CLAUDE_CONFIG_DIR%\commands" 2>nul
    if errorlevel 1 (
        call :info "Kept commands directory (contains other files)"
    ) else (
        call :info "Removed empty commands directory"
    )
)

goto :eof

:remove_craft_ai_hooks
call :info "Removing Craft-AI workflow hooks..."

REM Remove CAI hooks directory (preserve other hooks)
if exist "%CLAUDE_CONFIG_DIR%\hooks\cai" (
    rmdir /s /q "%CLAUDE_CONFIG_DIR%\hooks\cai" 2>nul
    call :info "Removed CAI hooks directory"
)

REM Remove hooks directory if it's empty and only contained cai
if exist "%CLAUDE_CONFIG_DIR%\hooks" (
    rmdir "%CLAUDE_CONFIG_DIR%\hooks" 2>nul
    if errorlevel 1 (
        call :info "Kept hooks directory (contains other files)"
    ) else (
        call :info "Removed empty hooks directory"
    )
)

REM Surgically remove CAI hooks from settings.local.json
call :clean_hook_settings

goto :eof

:clean_hook_settings
set "settings_file=%CLAUDE_CONFIG_DIR%\settings.local.json"

if not exist "%settings_file%" goto :eof

REM Backup before modification
copy "%settings_file%" "%settings_file%.pre-uninstall-backup" >nul
call :info "Created backup: %settings_file%.pre-uninstall-backup"

REM Note: Batch file JSON manipulation is complex and error-prone
REM We'll use PowerShell for safe JSON manipulation if available
powershell -Command "try { $settings = Get-Content '%settings_file%' | ConvertFrom-Json; if ($settings.hooks) { foreach ($event in ($settings.hooks | Get-Member -MemberType NoteProperty).Name) { $settings.hooks.$event = @($settings.hooks.$event | Where-Object { -not ($_.hooks | Where-Object { $_.id -like 'cai-*' }) }); if (-not $settings.hooks.$event) { $settings.hooks.PSObject.Properties.Remove($event) } } }; if ($settings.permissions.allow) { $settings.permissions.allow = @($settings.permissions.allow | Where-Object { $_ -notlike '*hooks/cai*' -and $_ -notlike '*craft-ai*' }) }; $settings | ConvertTo-Json -Depth 10 | Set-Content '%settings_file%'; Write-Host 'Successfully cleaned CAI hooks from settings.local.json' } catch { Write-Host 'Failed to clean hooks configuration - manual cleanup may be required'; Copy-Item '%settings_file%.pre-uninstall-backup' '%settings_file%' -Force }" 2>nul

if errorlevel 1 (
    call :warn "PowerShell not available or failed - hooks configuration not cleaned"
    call :warn "Manual cleanup of settings.local.json may be required"
)

goto :eof

:remove_config_files
call :info "Removing AI-Craft configuration files..."

if exist "%CLAUDE_CONFIG_DIR%\ai-craft-manifest.txt" (
    del /q "%CLAUDE_CONFIG_DIR%\ai-craft-manifest.txt" 2>nul
    call :info "Removed ai-craft-manifest.txt"
)

if exist "%CLAUDE_CONFIG_DIR%\ai-craft-install.log" (
    del /q "%CLAUDE_CONFIG_DIR%\ai-craft-install.log" 2>nul
    call :info "Removed ai-craft-install.log"
)

goto :eof

:remove_backups
call :info "Removing AI-Craft backup directories..."

set /a backup_count=0
for /d %%D in ("%CLAUDE_CONFIG_DIR%\backups\ai-craft-*") do (
    rmdir /s /q "%%D" 2>nul
    set /a backup_count+=1
)

if %backup_count% gtr 0 (
    call :info "Removed %backup_count% AI-Craft backup directories"
) else (
    call :info "No AI-Craft backup directories found"
)

goto :eof

:remove_project_files
call :info "Removing AI-Craft project files..."

REM Remove any project state files related to ai-craft
for /d %%D in ("%CLAUDE_CONFIG_DIR%\projects\*ai-craft*") do (
    rmdir /s /q "%%D" 2>nul
    call :info "Removed project directory: %%~nxD"
)

goto :eof

:validate_removal
call :info "Validating complete removal..."

set /a errors=0

REM Check that agents are removed
if exist "%CLAUDE_CONFIG_DIR%\agents\cai" (
    call :error_msg "AI-Craft agents directory still exists"
    set /a errors+=1
)

REM Check that commands are removed
if exist "%CLAUDE_CONFIG_DIR%\commands\cai" (
    call :error_msg "AI-Craft commands directory still exists"
    set /a errors+=1
)

REM Check that hooks are removed
if exist "%CLAUDE_CONFIG_DIR%\hooks\cai" (
    call :error_msg "AI-Craft hooks directory still exists"
    set /a errors+=1
)

REM Check that CAI hooks are removed from settings
if exist "%CLAUDE_CONFIG_DIR%\settings.local.json" (
    findstr /C:"\"cai-" "%CLAUDE_CONFIG_DIR%\settings.local.json" >nul 2>nul
    if not errorlevel 1 (
        call :warn "CAI hooks may still be configured in settings.local.json"
    )
)

REM Check that config files are removed
if exist "%CLAUDE_CONFIG_DIR%\ai-craft-manifest.txt" (
    call :error_msg "AI-Craft manifest file still exists"
    set /a errors+=1
)

if exist "%CLAUDE_CONFIG_DIR%\ai-craft-install.log" (
    call :error_msg "AI-Craft installation log still exists"
    set /a errors+=1
)

REM Check for remaining backup directories
for /d %%D in ("%CLAUDE_CONFIG_DIR%\backups\ai-craft-*") do (
    call :error_msg "AI-Craft backup directory still exists: %%~nxD"
    set /a errors+=1
)

if %errors% EQU 0 (
    call :info "Uninstallation validation: PASSED"
    goto :eof
) else (
    call :error_msg "Uninstallation validation: FAILED (%errors% errors)"
    exit /b 1
)

:create_uninstall_report
set "report_file=%CLAUDE_CONFIG_DIR%\ai-craft-uninstall-report.txt"

(
echo AI-Craft Framework Uninstallation Report
echo ========================================
echo Uninstalled: %date% %time%
echo Computer: %COMPUTERNAME%
echo User: %USERNAME%
echo.
echo Uninstall Summary:
echo - AI-Craft agents removed from: %CLAUDE_CONFIG_DIR%\agents\cai
echo - CAI commands removed from: %CLAUDE_CONFIG_DIR%\commands\cai (10 essential commands)
echo - Claude Code workflow hooks removed
echo - Configuration files removed
echo - Installation logs removed
echo - Backup directories cleaned
echo.
if "%BACKUP_BEFORE_REMOVAL%"=="true" (
echo Backup Information:
echo - Backup created: %BACKUP_DIR%
echo - Backup contains: Complete framework state before removal
echo.
)
echo Uninstallation completed successfully.
echo Framework completely removed from system.
) > "%report_file%"

call :info "Uninstallation report created: %report_file%"
goto :eof

:main
call :info "AI-Craft Framework Uninstallation Script"
call :info "======================================="

call :check_installation
if errorlevel 1 exit /b 1

call :confirm_removal
if errorlevel 1 exit /b 1

call :create_backup

call :remove_agents
call :remove_commands
call :remove_craft_ai_hooks
call :remove_config_files
call :remove_backups
call :remove_project_files

call :validate_removal
if errorlevel 1 (
    call :error_msg "Uninstallation failed validation"
    exit /b 1
)

call :create_uninstall_report

echo.
call :info "✅ AI-Craft Framework uninstalled successfully!"
echo.
call :info "Summary:"
call :info "- All AI-Craft agents removed"
call :info "- All CAI commands removed (10 essential commands)"
call :info "- Claude Code workflow hooks removed"
call :info "- Configuration files cleaned"
call :info "- Backup directories removed"

if "%BACKUP_BEFORE_REMOVAL%"=="true" (
    echo.
    call :info "💾 Backup available at:"
    call :info "   %BACKUP_DIR%"
    call :info "   Use this backup to restore if needed"
)

echo.
call :info "The AI-Craft framework has been completely removed from your system."

exit /b 0