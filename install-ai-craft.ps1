# AI-Craft Framework Installation Script for PowerShell
# Installs the AI-Craft ATDD agent framework to global Claude config directory
# 
# Usage: .\install-ai-craft.ps1 [-BackupOnly] [-Restore] [-Help]

param(
    [switch]$BackupOnly,
    [switch]$Restore,
    [switch]$Help
)

# Script configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ClaudeConfigDir = Join-Path $env:USERPROFILE ".claude"
$BackupTimestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$BackupDir = Join-Path $ClaudeConfigDir "backups\ai-craft-$BackupTimestamp"
$FrameworkSource = Join-Path $ScriptDir ".claude"
$InstallLog = Join-Path $ClaudeConfigDir "ai-craft-install.log"

# Logging functions
function Write-Log {
    param([string]$Level, [string]$Message)
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] $Level`: $Message"
    
    Write-Host $logEntry
    
    try {
        Add-Content -Path $InstallLog -Value $logEntry
    } catch {
        # Ignore logging errors
    }
}

function Write-Info { param([string]$Message) Write-Log "INFO" $Message }
function Write-Warn { param([string]$Message) Write-Log "WARN" $Message }
function Write-Error { param([string]$Message) Write-Log "ERROR" $Message }

# Help function
function Show-Help {
    Write-Host @"
AI-Craft Framework Installation Script for PowerShell

DESCRIPTION:
    Installs the AI-Craft ATDD agent framework to your global Claude config directory.
    This makes all 33+ specialized agents and the cai/atdd command available across all projects.

USAGE:
    .\install-ai-craft.ps1 [OPTIONS]

OPTIONS:
    -BackupOnly     Create backup of existing AI-Craft installation without installing
    -Restore        Restore from the most recent backup
    -Help           Show this help message

EXAMPLES:
    .\install-ai-craft.ps1                # Install AI-Craft framework
    .\install-ai-craft.ps1 -BackupOnly    # Create backup only
    .\install-ai-craft.ps1 -Restore       # Restore from latest backup

WHAT GETS INSTALLED:
    - 33+ specialized AI agents in 7 categories
    - cai/atdd command interface with intelligent project analysis
    - Centralized configuration system (constants.md)
    - Wave processing architecture for clean ATDD workflows
    - Quality validation network with Level 1-6 refactoring

INSTALLATION LOCATION:
    $env:USERPROFILE\.claude\agents\       # All agent specifications
    $env:USERPROFILE\.claude\commands\     # Command integrations

FILES EXCLUDED:
    - README.md files (project-specific documentation)
    - docs\ directory (project working files)
    - Git configuration and project metadata

For more information: https://github.com/11PJ11/crafter-ai
"@
}

# Check if source framework exists
function Test-SourceFramework {
    Write-Info "Checking source framework..."
    
    if (!(Test-Path $FrameworkSource)) {
        Write-Error "AI-Craft framework source not found at: $FrameworkSource"
        Write-Error "Please run this script from the ai-craft project directory."
        return $false
    }
    
    $constantsFile = Join-Path $FrameworkSource "agents\constants.md"
    if (!(Test-Path $constantsFile)) {
        Write-Error "Framework appears incomplete - constants.md not found"
        return $false
    }
    
    $agentFiles = Get-ChildItem -Path (Join-Path $FrameworkSource "agents") -Filter "*.md" -Recurse | 
                  Where-Object { $_.Name -ne "README.md" }
    $agentCount = $agentFiles.Count
    
    Write-Info "Found framework with $agentCount agent files"
    
    if ($agentCount -lt 30) {
        Write-Warn "Expected 30+ agents, found only $agentCount. Continuing anyway..."
    }
    
    return $true
}

# Create backup of existing installation
function New-Backup {
    Write-Info "Creating backup of existing AI-Craft installation..."
    
    $agentsDir = Join-Path $ClaudeConfigDir "agents"
    $commandsDir = Join-Path $ClaudeConfigDir "commands"
    
    if (!(Test-Path $agentsDir) -and !(Test-Path $commandsDir)) {
        Write-Info "No existing AI-Craft installation found, skipping backup"
        return
    }
    
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    
    # Backup existing agents directory
    if (Test-Path $agentsDir) {
        Copy-Item -Path $agentsDir -Destination $BackupDir -Recurse -Force
        Write-Info "Backed up agents directory"
    }
    
    # Backup existing commands directory
    if (Test-Path $commandsDir) {
        Copy-Item -Path $commandsDir -Destination $BackupDir -Recurse -Force
        Write-Info "Backed up commands directory"
    }
    
    # Create backup manifest
    $manifest = @"
AI-Craft Framework Backup
Created: $(Get-Date)
Source: $env:COMPUTERNAME`:$ClaudeConfigDir
Backup contents:
Framework files backed up
"@
    
    $manifestFile = Join-Path $BackupDir "backup-manifest.txt"
    Set-Content -Path $manifestFile -Value $manifest
    
    Write-Info "Backup created at: $BackupDir"
}

# Restore from backup
function Restore-Backup {
    Write-Info "Looking for backups to restore..."
    
    $backupsDir = Join-Path $ClaudeConfigDir "backups"
    $latestBackup = Get-ChildItem -Path $backupsDir -Directory -Filter "ai-craft-*" 2>$null | 
                    Sort-Object Name | Select-Object -Last 1
    
    if (!$latestBackup) {
        Write-Error "No backups found in $backupsDir"
        return $false
    }
    
    Write-Info "Restoring from backup: $($latestBackup.FullName)"
    
    # Remove current installation
    $agentsDir = Join-Path $ClaudeConfigDir "agents"
    $caiCommandsDir = Join-Path $ClaudeConfigDir "commands\cai"
    
    if (Test-Path $agentsDir) { Remove-Item -Path $agentsDir -Recurse -Force }
    if (Test-Path $caiCommandsDir) { Remove-Item -Path $caiCommandsDir -Recurse -Force }
    
    # Restore from backup
    $backupAgents = Join-Path $latestBackup.FullName "agents"
    $backupCommands = Join-Path $latestBackup.FullName "commands"
    
    if (Test-Path $backupAgents) {
        Copy-Item -Path $backupAgents -Destination $ClaudeConfigDir -Recurse -Force
        Write-Info "Restored agents directory"
    }
    
    if (Test-Path $backupCommands) {
        Copy-Item -Path $backupCommands -Destination $ClaudeConfigDir -Recurse -Force
        Write-Info "Restored commands directory"
    }
    
    Write-Info "Restoration complete from backup: $($latestBackup.FullName)"
    return $true
}

# Install framework files
function Install-Framework {
    Write-Info "Installing AI-Craft framework to: $ClaudeConfigDir"
    
    # Create target directories
    New-Item -ItemType Directory -Path $ClaudeConfigDir -Force | Out-Null
    
    # Install agents (excluding README.md)
    Write-Info "Installing agents..."
    $sourceAgentsDir = Join-Path $FrameworkSource "agents"
    $targetAgentsDir = Join-Path $ClaudeConfigDir "agents"
    
    if (Test-Path $sourceAgentsDir) {
        New-Item -ItemType Directory -Path $targetAgentsDir -Force | Out-Null
        
        $agentFiles = Get-ChildItem -Path $sourceAgentsDir -Filter "*.md" -Recurse | 
                      Where-Object { $_.Name -ne "README.md" }
        
        foreach ($file in $agentFiles) {
            $relativePath = $file.FullName.Substring($sourceAgentsDir.Length + 1)
            $targetFile = Join-Path $targetAgentsDir $relativePath
            $targetDir = Split-Path $targetFile -Parent
            
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
            Copy-Item -Path $file.FullName -Destination $targetFile -Force
        }
        
        $copiedAgents = (Get-ChildItem -Path $targetAgentsDir -Filter "*.md" -Recurse).Count
        Write-Info "Installed $copiedAgents agent files"
    }
    
    # Install commands
    Write-Info "Installing commands..."
    $sourceCommandsDir = Join-Path $FrameworkSource "commands"
    $targetCommandsDir = Join-Path $ClaudeConfigDir "commands"
    
    if (Test-Path $sourceCommandsDir) {
        New-Item -ItemType Directory -Path $targetCommandsDir -Force | Out-Null
        Copy-Item -Path "$sourceCommandsDir\*" -Destination $targetCommandsDir -Recurse -Force
        
        $copiedCommands = (Get-ChildItem -Path $targetCommandsDir -Filter "*.md" -Recurse).Count
        Write-Info "Installed $copiedCommands command files"
    }
}

# Validate installation
function Test-Installation {
    Write-Info "Validating installation..."
    
    $errors = 0
    
    # Check constants.md exists
    $constantsFile = Join-Path $ClaudeConfigDir "agents\constants.md"
    if (!(Test-Path $constantsFile)) {
        Write-Error "Missing constants.md - core configuration file"
        $errors++
    }
    
    # Check cai/atdd command exists
    $caiAtddFile = Join-Path $ClaudeConfigDir "commands\cai\atdd.md"
    if (!(Test-Path $caiAtddFile)) {
        Write-Error "Missing cai/atdd command file"
        $errors++
    }
    
    # Count installed files
    $agentsDir = Join-Path $ClaudeConfigDir "agents"
    $commandsDir = Join-Path $ClaudeConfigDir "commands"
    
    $totalAgents = if (Test-Path $agentsDir) { 
        (Get-ChildItem -Path $agentsDir -Filter "*.md" -Recurse).Count 
    } else { 0 }
    
    $totalCommands = if (Test-Path $commandsDir) { 
        (Get-ChildItem -Path $commandsDir -Filter "*.md" -Recurse).Count 
    } else { 0 }
    
    Write-Info "Installation summary:"
    Write-Info "  - Agents installed: $totalAgents"
    Write-Info "  - Commands installed: $totalCommands"
    Write-Info "  - Installation directory: $ClaudeConfigDir"
    
    # Check agent categories
    $categories = @("requirements-analysis", "architecture-design", "test-design", 
                    "development", "quality-validation", "refactoring", "coordination")
    
    foreach ($category in $categories) {
        $categoryDir = Join-Path $agentsDir $category
        if (Test-Path $categoryDir) {
            $count = (Get-ChildItem -Path $categoryDir -Filter "*.md").Count
            Write-Info "  - $category`: $count agents"
        } else {
            Write-Warn "  - $category`: directory not found"
        }
    }
    
    if ($totalAgents -lt 30) {
        Write-Warn "Expected 30+ agents, found $totalAgents"
    }
    
    if ($errors -eq 0) {
        Write-Info "Installation validation: PASSED"
        return $true
    } else {
        Write-Error "Installation validation: FAILED ($errors errors)"
        return $false
    }
}

# Create installation manifest
function New-Manifest {
    $manifestFile = Join-Path $ClaudeConfigDir "ai-craft-manifest.txt"
    
    $agentsDir = Join-Path $ClaudeConfigDir "agents"
    $commandsDir = Join-Path $ClaudeConfigDir "commands"
    
    $totalAgents = if (Test-Path $agentsDir) { 
        (Get-ChildItem -Path $agentsDir -Filter "*.md" -Recurse).Count 
    } else { 0 }
    
    $totalCommands = if (Test-Path $commandsDir) { 
        (Get-ChildItem -Path $commandsDir -Filter "*.md" -Recurse).Count 
    } else { 0 }
    
    $manifest = @"
AI-Craft Framework Installation Manifest
========================================
Installed: $(Get-Date)
Source: $ScriptDir
Version: Production Ready (2025-01-13)

Installation Summary:
- Total agents: $totalAgents
- Total commands: $totalCommands
- Installation directory: $ClaudeConfigDir
- Backup directory: $BackupDir

Framework Components:
- 33+ specialized AI agents with Single Responsibility Principle
- Wave processing architecture with clean context isolation
- cai/atdd command interface with intelligent project analysis
- Centralized configuration system (constants.md)
- Quality validation network with Level 1-6 refactoring

Usage:
- Use 'cai/atdd "feature description"' in any project
- All agents available globally across projects
- Centralized constants work project-wide

For help: https://github.com/11PJ11/crafter-ai
"@
    
    Set-Content -Path $manifestFile -Value $manifest
    Write-Info "Installation manifest created: $manifestFile"
}

# Main execution
function Main {
    Write-Info "AI-Craft Framework Installation Script"
    Write-Info "======================================"
    
    # Handle command line arguments
    if ($Help) {
        Show-Help
        return
    }
    
    if ($BackupOnly) {
        if (!(Test-SourceFramework)) { return }
        New-Backup
        Write-Info "Backup completed successfully"
        return
    }
    
    if ($Restore) {
        if (!(Restore-Backup)) { return }
        Write-Info "Restoration completed successfully"
        return
    }
    
    # Normal installation process
    if (!(Test-SourceFramework)) { return }
    
    New-Backup
    Install-Framework
    
    if (Test-Installation) {
        New-Manifest
        
        Write-Host ""
        Write-Info "✅ AI-Craft Framework installed successfully!"
        Write-Host ""
        Write-Info "Next steps:"
        Write-Info "1. Navigate to any project directory"
        Write-Info "2. Use: cai/atdd `"your feature description`""
        Write-Info "3. Access 33+ specialized agents globally"
        Write-Host ""
        Write-Info "For help: cai/atdd --help"
        Write-Info "Documentation: https://github.com/11PJ11/crafter-ai"
    } else {
        Write-Error "Installation failed validation"
        Write-Warn "You can restore the previous installation with: .\install-ai-craft.ps1 -Restore"
    }
}

# Run main function
Main