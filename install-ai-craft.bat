@echo off
REM AI-Craft Framework Installation Script for Windows
REM Installs the AI-Craft ATDD agent framework to global Claude config directory
REM 
REM Usage: install-ai-craft.bat [--backup-only] [--restore] [--help]

setlocal enabledelayedexpansion

REM Script configuration
set "SCRIPT_DIR=%~dp0"
set "CLAUDE_CONFIG_DIR=%USERPROFILE%\.claude"
set "FRAMEWORK_SOURCE=%SCRIPT_DIR%.claude"
set "INSTALL_LOG=%CLAUDE_CONFIG_DIR%\ai-craft-install.log"

REM Get current timestamp for backup
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set "BACKUP_TIMESTAMP=%datetime:~0,8%-%datetime:~8,6%"
set "BACKUP_DIR=%CLAUDE_CONFIG_DIR%\backups\ai-craft-%BACKUP_TIMESTAMP%"

REM Check command line arguments
if "%~1"=="--help" goto :show_help
if "%~1"=="-h" goto :show_help
if "%~1"=="--backup-only" goto :backup_only
if "%~1"=="--restore" goto :restore_backup
if not "%~1"=="" (
    echo ERROR: Unknown option: %~1
    echo Use --help for usage information
    exit /b 1
)

REM Main installation process
goto :main

:show_help
echo AI-Craft Framework Installation Script for Windows
echo.
echo DESCRIPTION:
echo     Installs the AI-Craft ATDD agent framework to your global Claude config directory.
echo     This makes all 41+ specialized agents and the cai/atdd command available across all projects.
echo.
echo USAGE:
echo     %~nx0 [OPTIONS]
echo.
echo OPTIONS:
echo     --backup-only    Create backup of existing AI-Craft installation without installing
echo     --restore        Restore from the most recent backup
echo     --help           Show this help message
echo.
echo EXAMPLES:
echo     %~nx0                      # Install AI-Craft framework
echo     %~nx0 --backup-only        # Create backup only
echo     %~nx0 --restore           # Restore from latest backup
echo.
echo WHAT GETS INSTALLED:
echo     - 41+ specialized AI agents in 9 categories
echo     - cai/atdd command interface with intelligent project analysis
echo     - Centralized configuration system (constants.md)
echo     - Wave processing architecture for clean ATDD workflows
echo     - Quality validation network with Level 1-6 refactoring
echo     - Second Way DevOps: Observability agents (metrics, logs, traces, performance)
echo     - Third Way DevOps: Experimentation agents (A/B testing, hypothesis validation, learning synthesis)
echo.
echo INSTALLATION LOCATION:
echo     %USERPROFILE%\.claude\agents\       # All agent specifications
echo     %USERPROFILE%\.claude\commands\     # Command integrations
echo.
echo FILES EXCLUDED:
echo     - README.md files (project-specific documentation)
echo     - docs\ directory (project working files)
echo     - Git configuration and project metadata
echo.
echo For more information: https://github.com/11PJ11/crafter-ai
exit /b 0

:log_message
set "level=%~1"
set "message=%~2"
echo [%date% %time%] %level%: %message%
echo [%date% %time%] %level%: %message% >> "%INSTALL_LOG%" 2>nul
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

:check_source
call :info "Checking source framework..."

if not exist "%FRAMEWORK_SOURCE%" (
    call :error_msg "AI-Craft framework source not found at: %FRAMEWORK_SOURCE%"
    call :error_msg "Please run this script from the ai-craft project directory."
    exit /b 1
)

if not exist "%FRAMEWORK_SOURCE%\agents\cai\constants.md" (
    call :error_msg "Framework appears incomplete - constants.md not found"
    exit /b 1
)

REM Count agent files (simple approach for Windows)
set /a agent_count=0
for /r "%FRAMEWORK_SOURCE%\agents\cai" %%f in (*.md) do (
    set "filename=%%~nf"
    if not "!filename!"=="README" (
        set /a agent_count+=1
    )
)

call :info "Found framework with %agent_count% agent files"

if %agent_count% LSS 40 (
    call :warn "Expected 40+ agents, found only %agent_count%. Continuing anyway..."
)
goto :eof

:create_backup
call :info "Creating backup of existing AI-Craft installation..."

if not exist "%CLAUDE_CONFIG_DIR%\agents" if not exist "%CLAUDE_CONFIG_DIR%\commands" (
    call :info "No existing AI-Craft installation found, skipping backup"
    goto :eof
)

mkdir "%BACKUP_DIR%" 2>nul

REM Backup existing agents directory
if exist "%CLAUDE_CONFIG_DIR%\agents" (
    xcopy "%CLAUDE_CONFIG_DIR%\agents" "%BACKUP_DIR%\agents\" /E /I /Q >nul
    call :info "Backed up agents directory"
)

REM Backup existing commands directory
if exist "%CLAUDE_CONFIG_DIR%\commands" (
    xcopy "%CLAUDE_CONFIG_DIR%\commands" "%BACKUP_DIR%\commands\" /E /I /Q >nul
    call :info "Backed up commands directory"
)

REM Create backup manifest
(
echo AI-Craft Framework Backup
echo Created: %date% %time%
echo Source: %COMPUTERNAME%:%CLAUDE_CONFIG_DIR%
echo Backup contents:
echo Framework files backed up
) > "%BACKUP_DIR%\backup-manifest.txt"

call :info "Backup created at: %BACKUP_DIR%"
goto :eof

:restore_backup
call :info "Looking for backups to restore..."

set "latest_backup="
for /f "delims=" %%d in ('dir "%CLAUDE_CONFIG_DIR%\backups\ai-craft-*" /b /ad 2^>nul') do (
    set "latest_backup=%CLAUDE_CONFIG_DIR%\backups\%%d"
)

if "!latest_backup!"=="" (
    call :error_msg "No backups found in %CLAUDE_CONFIG_DIR%\backups"
    exit /b 1
)

call :info "Restoring from backup: !latest_backup!"

REM Remove current installation
rmdir /s /q "%CLAUDE_CONFIG_DIR%\agents" 2>nul
rmdir /s /q "%CLAUDE_CONFIG_DIR%\commands\cai" 2>nul

REM Restore from backup
if exist "!latest_backup!\agents" (
    xcopy "!latest_backup!\agents" "%CLAUDE_CONFIG_DIR%\agents\" /E /I /Q >nul
    call :info "Restored agents directory"
)

if exist "!latest_backup!\commands" (
    xcopy "!latest_backup!\commands" "%CLAUDE_CONFIG_DIR%\commands\" /E /I /Q >nul
    call :info "Restored commands directory"
)

call :info "Restoration complete from backup: !latest_backup!"
exit /b 0

:backup_only
call :check_source
call :create_backup
call :info "Backup completed successfully"
exit /b 0

:install_framework
call :info "Installing AI-Craft framework to: %CLAUDE_CONFIG_DIR%"

REM Create target directories
mkdir "%CLAUDE_CONFIG_DIR%" 2>nul
mkdir "%CLAUDE_CONFIG_DIR%\agents" 2>nul
mkdir "%CLAUDE_CONFIG_DIR%\agents\cai" 2>nul
mkdir "%CLAUDE_CONFIG_DIR%\commands" 2>nul

REM Copy agents directory (excluding README.md)
call :info "Installing agents..."
if exist "%FRAMEWORK_SOURCE%\agents\cai" (
    for /r "%FRAMEWORK_SOURCE%\agents\cai" %%f in (*.md) do (
        set "filename=%%~nf"
        if not "!filename!"=="README" (
            set "source_file=%%f"
            set "relative_path=!source_file:%FRAMEWORK_SOURCE%\agents\cai\=!"
            set "target_file=%CLAUDE_CONFIG_DIR%\agents\cai\!relative_path!"
            
            REM Create target directory
            for %%t in ("!target_file!") do mkdir "%%~dpt" 2>nul
            
            REM Copy file
            copy "!source_file!" "!target_file!" >nul
        )
    )
    
    REM Count copied agents
    set /a copied_agents=0
    for /r "%CLAUDE_CONFIG_DIR%\agents\cai" %%f in (*.md) do set /a copied_agents+=1
    call :info "Installed !copied_agents! agent files"
)

REM Copy commands directory
call :info "Installing commands..."
if exist "%FRAMEWORK_SOURCE%\commands" (
    xcopy "%FRAMEWORK_SOURCE%\commands" "%CLAUDE_CONFIG_DIR%\commands\" /E /I /Q >nul
    
    REM Count copied commands
    set /a copied_commands=0
    for /r "%CLAUDE_CONFIG_DIR%\commands" %%f in (*.md) do set /a copied_commands+=1
    call :info "Installed !copied_commands! command files"
)
goto :eof

:validate_installation
call :info "Validating installation..."

set /a errors=0

REM Check constants.md exists
if not exist "%CLAUDE_CONFIG_DIR%\agents\cai\constants.md" (
    call :error_msg "Missing constants.md - core configuration file"
    set /a errors+=1
)

REM Check cai/atdd command exists
if not exist "%CLAUDE_CONFIG_DIR%\commands\cai\atdd.md" (
    call :error_msg "Missing cai/atdd command file"
    set /a errors+=1
)

REM Count installed files
set /a total_agents=0
set /a total_commands=0
for /r "%CLAUDE_CONFIG_DIR%\agents\cai" %%f in (*.md) do set /a total_agents+=1
for /r "%CLAUDE_CONFIG_DIR%\commands" %%f in (*.md) do set /a total_commands+=1

call :info "Installation summary:"
call :info "  - Agents installed: %total_agents%"
call :info "  - Commands installed: %total_commands%"
call :info "  - Installation directory: %CLAUDE_CONFIG_DIR%"

REM Check agent categories
set "categories=requirements-analysis architecture-design test-design development quality-validation refactoring coordination observability experimentation"
for %%c in (%categories%) do (
    if exist "%CLAUDE_CONFIG_DIR%\agents\cai\%%c" (
        set /a count=0
        for %%f in ("%CLAUDE_CONFIG_DIR%\agents\cai\%%c\*.md") do set /a count+=1
        call :info "  - %%c: !count! agents"
    ) else (
        call :warn "  - %%c: directory not found"
    )
)

if %total_agents% LSS 40 (
    call :warn "Expected 40+ agents, found %total_agents%"
)

if %errors% EQU 0 (
    call :info "Installation validation: PASSED"
    goto :eof
) else (
    call :error_msg "Installation validation: FAILED (%errors% errors)"
    exit /b 1
)

:create_manifest
set "manifest_file=%CLAUDE_CONFIG_DIR%\ai-craft-manifest.txt"

(
echo AI-Craft Framework Installation Manifest
echo ========================================
echo Installed: %date% %time%
echo Source: %SCRIPT_DIR%
echo Version: Production Ready ^(2025-01-13^)
echo.
echo Installation Summary:
echo - Installation directory: %CLAUDE_CONFIG_DIR%
echo - Backup directory: %BACKUP_DIR%
echo.
echo Framework Components:
echo - 41+ specialized AI agents with Single Responsibility Principle
echo - Wave processing architecture with clean context isolation
echo - cai/atdd command interface with intelligent project analysis
echo - Centralized configuration system ^(constants.md^)
echo - Quality validation network with Level 1-6 refactoring
echo - Second Way DevOps: Observability agents ^(metrics, logs, traces, performance^)
echo - Third Way DevOps: Experimentation agents ^(A/B testing, hypothesis validation, learning synthesis^)
echo.
echo Usage:
echo - Use 'cai/atdd "feature description"' in any project
echo - All agents available globally across projects
echo - Centralized constants work project-wide
echo.
echo For help: https://github.com/11PJ11/crafter-ai
) > "%manifest_file%"

call :info "Installation manifest created: %manifest_file%"
goto :eof

:main
call :info "AI-Craft Framework Installation Script"
call :info "======================================"

call :check_source
if errorlevel 1 exit /b 1

call :create_backup

call :install_framework

call :validate_installation
if errorlevel 1 (
    call :error_msg "Installation failed validation"
    call :warn "You can restore the previous installation with: %~nx0 --restore"
    exit /b 1
)

call :create_manifest

echo.
call :info "✅ AI-Craft Framework installed successfully!"
echo.
call :info "Next steps:"
call :info "1. Navigate to any project directory"
call :info "2. Use: cai/atdd \"your feature description\""
call :info "3. Access 41+ specialized agents globally"
echo.
call :info "For help: cai/atdd --help"
call :info "Documentation: https://github.com/11PJ11/crafter-ai"

exit /b 0