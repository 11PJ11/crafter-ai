# AI-Craft Framework Uninstallation Script for PowerShell
# Completely removes AI-Craft framework from global Claude config directory
# 
# Usage: .\uninstall-ai-craft.ps1 [-Backup] [-Force] [-Help]

[CmdletBinding()]
param(
    [switch]$Backup,
    [switch]$Force,
    [switch]$Help
)

# Script configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ClaudeConfigDir = Join-Path $env:USERPROFILE ".claude"
$UninstallLog = Join-Path $ClaudeConfigDir "ai-craft-uninstall.log"

# Backup configuration
$BackupTimestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$BackupDir = Join-Path $ClaudeConfigDir "backups\ai-craft-uninstall-$BackupTimestamp"

# Color constants
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Cyan"

function Show-Help {
    Write-Host @"
AI-Craft Framework Uninstallation Script for PowerShell

DESCRIPTION:
    Completely removes the AI-Craft ATDD agent framework from your global Claude config directory.
    This removes all 41+ specialized agents, commands, configuration files, logs, and backups.

USAGE:
    .\uninstall-ai-craft.ps1 [OPTIONS]

OPTIONS:
    -Backup          Create backup before removal (recommended)
    -Force           Skip confirmation prompts
    -Help            Show this help message

EXAMPLES:
    .\uninstall-ai-craft.ps1                     # Interactive uninstall with confirmation
    .\uninstall-ai-craft.ps1 -Backup             # Create backup before removal
    .\uninstall-ai-craft.ps1 -Force              # Uninstall without confirmation prompts

WHAT GETS REMOVED:
    - All AI-Craft agents in agents/cai/ directory
    - All AI-Craft commands in commands/cai/ directory  
    - AI-Craft configuration files (constants.md, manifest)
    - AI-Craft installation logs and backup directories
    - AI-Craft project state files

IMPORTANT:
    This action cannot be undone unless you use -Backup option.
    All customizations and local changes will be lost.
"@ -ForegroundColor $Blue
}

function Write-Log {
    param(
        [string]$Level,
        [string]$Message
    )
    
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] $Level`: $Message"
    
    Write-Host $LogEntry -ForegroundColor $(
        switch ($Level) {
            "INFO" { $Green }
            "WARN" { $Yellow }
            "ERROR" { $Red }
            default { "White" }
        }
    )
    
    try {
        Add-Content -Path $UninstallLog -Value $LogEntry -ErrorAction SilentlyContinue
    } catch {
        # Ignore log write errors
    }
}

function Write-Info {
    param([string]$Message)
    Write-Log "INFO" $Message
}

function Write-Warn {
    param([string]$Message)
    Write-Log "WARN" $Message
}

function Write-Error {
    param([string]$Message)
    Write-Log "ERROR" $Message
}

function Test-AiCraftInstallation {
    Write-Info "Checking for AI-Craft installation..."
    
    $InstallationFound = $false
    
    # Check for agents directory
    $AgentsCaiDir = Join-Path $ClaudeConfigDir "agents\cai"
    if (Test-Path $AgentsCaiDir) {
        $InstallationFound = $true
        Write-Info "Found AI-Craft agents in: $AgentsCaiDir"
    }
    
    # Check for commands directory
    $CommandsCaiDir = Join-Path $ClaudeConfigDir "commands\cai"
    if (Test-Path $CommandsCaiDir) {
        $InstallationFound = $true
        Write-Info "Found AI-Craft commands in: $CommandsCaiDir"
    }
    
    # Check for configuration files
    $ConstantsFile = Join-Path $ClaudeConfigDir "agents\cai\constants.md"
    if (Test-Path $ConstantsFile) {
        $InstallationFound = $true
        Write-Info "Found AI-Craft configuration files"
    }
    
    # Check for manifest
    $ManifestFile = Join-Path $ClaudeConfigDir "ai-craft-manifest.txt"
    if (Test-Path $ManifestFile) {
        $InstallationFound = $true
        Write-Info "Found AI-Craft manifest file"
    }
    
    # Check for installation logs
    $InstallLogFile = Join-Path $ClaudeConfigDir "ai-craft-install.log"
    if (Test-Path $InstallLogFile) {
        $InstallationFound = $true
        Write-Info "Found AI-Craft installation logs"
    }
    
    # Check for backup directories
    $BackupsDir = Join-Path $ClaudeConfigDir "backups"
    if (Test-Path $BackupsDir) {
        $AiCraftBackups = Get-ChildItem -Path $BackupsDir -Directory -Name "ai-craft-*" -ErrorAction SilentlyContinue
        if ($AiCraftBackups.Count -gt 0) {
            $InstallationFound = $true
            Write-Info "Found AI-Craft backup directories"
        }
    }
    
    if (-not $InstallationFound) {
        Write-Info "No AI-Craft installation found"
        Write-Host ""
        Write-Host "No AI-Craft framework installation detected." -ForegroundColor $Yellow
        Write-Host "Nothing to uninstall." -ForegroundColor $Yellow
        exit 0
    }
    
    return $InstallationFound
}

function Confirm-Removal {
    if ($Force) {
        return $true
    }
    
    Write-Host ""
    Write-Host "WARNING: This will completely remove the AI-Craft framework from your system." -ForegroundColor $Red
    Write-Host ""
    Write-Host "The following will be removed:" -ForegroundColor $Yellow
    Write-Host "  - All AI-Craft agents (41+ specialized agents)" -ForegroundColor $Yellow
    Write-Host "  - All AI-Craft commands (cai/atdd and related commands)" -ForegroundColor $Yellow
    Write-Host "  - Configuration files (constants.md, manifest)" -ForegroundColor $Yellow
    Write-Host "  - Installation logs and backup directories" -ForegroundColor $Yellow
    Write-Host "  - Any customizations or local changes" -ForegroundColor $Yellow
    Write-Host ""
    
    if ($Backup) {
        Write-Host "A backup will be created before removal at:" -ForegroundColor $Green
        Write-Host "  $BackupDir" -ForegroundColor $Green
        Write-Host ""
    } else {
        Write-Host "WARNING: No backup will be created. This action cannot be undone." -ForegroundColor $Red
        Write-Host "To create a backup, cancel and run with -Backup option." -ForegroundColor $Red
        Write-Host ""
    }
    
    $Confirmation = Read-Host "Are you sure you want to proceed? (y/N)"
    return ($Confirmation -eq "y" -or $Confirmation -eq "yes" -or $Confirmation -eq "Y" -or $Confirmation -eq "YES")
}

function New-UninstallBackup {
    if (-not $Backup) {
        return
    }
    
    Write-Info "Creating backup before removal..."
    
    try {
        New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
        
        # Backup agents directory if it exists
        $AgentsCaiDir = Join-Path $ClaudeConfigDir "agents\cai"
        if (Test-Path $AgentsCaiDir) {
            $BackupAgentsDir = Join-Path $BackupDir "agents\cai"
            New-Item -ItemType Directory -Path (Split-Path $BackupAgentsDir -Parent) -Force | Out-Null
            Copy-Item -Path $AgentsCaiDir -Destination $BackupAgentsDir -Recurse -Force
            Write-Info "Backed up agents directory"
        }
        
        # Backup commands directory if it exists
        $CommandsCaiDir = Join-Path $ClaudeConfigDir "commands\cai"
        if (Test-Path $CommandsCaiDir) {
            $BackupCommandsDir = Join-Path $BackupDir "commands\cai"
            New-Item -ItemType Directory -Path (Split-Path $BackupCommandsDir -Parent) -Force | Out-Null
            Copy-Item -Path $CommandsCaiDir -Destination $BackupCommandsDir -Recurse -Force
            Write-Info "Backed up commands directory"
        }
        
        # Backup configuration files
        $ManifestFile = Join-Path $ClaudeConfigDir "ai-craft-manifest.txt"
        if (Test-Path $ManifestFile) {
            Copy-Item -Path $ManifestFile -Destination $BackupDir -Force
            Write-Info "Backed up manifest file"
        }
        
        $InstallLogFile = Join-Path $ClaudeConfigDir "ai-craft-install.log"
        if (Test-Path $InstallLogFile) {
            Copy-Item -Path $InstallLogFile -Destination $BackupDir -Force
            Write-Info "Backed up installation log"
        }
        
        # Create backup manifest
        $BackupManifest = @"
AI-Craft Framework Uninstall Backup
Created: $(Get-Date)
Source: $env:COMPUTERNAME`:$ClaudeConfigDir
Backup Type: Pre-uninstall backup
Backup contents:
  - AI-Craft agents and commands
  - Configuration files and logs
  - Complete framework state before removal
"@
        
        $BackupManifestFile = Join-Path $BackupDir "uninstall-backup-manifest.txt"
        Set-Content -Path $BackupManifestFile -Value $BackupManifest
        
        Write-Info "Backup created successfully at: $BackupDir"
        
    } catch {
        Write-Error "Failed to create backup: $($_.Exception.Message)"
        throw
    }
}

function Remove-AiCraftAgents {
    Write-Info "Removing AI-Craft agents..."
    
    $AgentsCaiDir = Join-Path $ClaudeConfigDir "agents\cai"
    if (Test-Path $AgentsCaiDir) {
        Remove-Item -Path $AgentsCaiDir -Recurse -Force -ErrorAction SilentlyContinue
        Write-Info "Removed agents/cai directory"
    }
    
    # Remove agents directory if it's empty and only contained cai
    $AgentsDir = Join-Path $ClaudeConfigDir "agents"
    if (Test-Path $AgentsDir) {
        $RemainingItems = Get-ChildItem -Path $AgentsDir -ErrorAction SilentlyContinue
        if ($RemainingItems.Count -eq 0) {
            Remove-Item -Path $AgentsDir -Force -ErrorAction SilentlyContinue
            Write-Info "Removed empty agents directory"
        } else {
            Write-Info "Kept agents directory (contains other files)"
        }
    }
}

function Remove-AiCraftCommands {
    Write-Info "Removing AI-Craft commands..."
    
    $CommandsCaiDir = Join-Path $ClaudeConfigDir "commands\cai"
    if (Test-Path $CommandsCaiDir) {
        Remove-Item -Path $CommandsCaiDir -Recurse -Force -ErrorAction SilentlyContinue
        Write-Info "Removed commands/cai directory"
    }
    
    # Remove commands directory if it's empty and only contained cai
    $CommandsDir = Join-Path $ClaudeConfigDir "commands"
    if (Test-Path $CommandsDir) {
        $RemainingItems = Get-ChildItem -Path $CommandsDir -ErrorAction SilentlyContinue
        if ($RemainingItems.Count -eq 0) {
            Remove-Item -Path $CommandsDir -Force -ErrorAction SilentlyContinue
            Write-Info "Removed empty commands directory"
        } else {
            Write-Info "Kept commands directory (contains other files)"
        }
    }
}

function Remove-AiCraftConfigFiles {
    Write-Info "Removing AI-Craft configuration files..."
    
    $ManifestFile = Join-Path $ClaudeConfigDir "ai-craft-manifest.txt"
    if (Test-Path $ManifestFile) {
        Remove-Item -Path $ManifestFile -Force -ErrorAction SilentlyContinue
        Write-Info "Removed ai-craft-manifest.txt"
    }
    
    $InstallLogFile = Join-Path $ClaudeConfigDir "ai-craft-install.log"
    if (Test-Path $InstallLogFile) {
        Remove-Item -Path $InstallLogFile -Force -ErrorAction SilentlyContinue
        Write-Info "Removed ai-craft-install.log"
    }
}

function Remove-AiCraftBackups {
    Write-Info "Removing AI-Craft backup directories..."
    
    $BackupsDir = Join-Path $ClaudeConfigDir "backups"
    if (Test-Path $BackupsDir) {
        $AiCraftBackups = Get-ChildItem -Path $BackupsDir -Directory -Name "ai-craft-*" -ErrorAction SilentlyContinue
        
        foreach ($BackupName in $AiCraftBackups) {
            $BackupPath = Join-Path $BackupsDir $BackupName
            Remove-Item -Path $BackupPath -Recurse -Force -ErrorAction SilentlyContinue
        }
        
        if ($AiCraftBackups.Count -gt 0) {
            Write-Info "Removed $($AiCraftBackups.Count) AI-Craft backup directories"
        } else {
            Write-Info "No AI-Craft backup directories found"
        }
    }
}

function Remove-AiCraftProjectFiles {
    Write-Info "Removing AI-Craft project files..."
    
    $ProjectsDir = Join-Path $ClaudeConfigDir "projects"
    if (Test-Path $ProjectsDir) {
        $AiCraftProjects = Get-ChildItem -Path $ProjectsDir -Directory -Name "*ai-craft*" -ErrorAction SilentlyContinue
        
        foreach ($ProjectName in $AiCraftProjects) {
            $ProjectPath = Join-Path $ProjectsDir $ProjectName
            Remove-Item -Path $ProjectPath -Recurse -Force -ErrorAction SilentlyContinue
            Write-Info "Removed project directory: $ProjectName"
        }
    }
}

function Test-RemovalComplete {
    Write-Info "Validating complete removal..."
    
    $Errors = 0
    
    # Check that agents are removed
    $AgentsCaiDir = Join-Path $ClaudeConfigDir "agents\cai"
    if (Test-Path $AgentsCaiDir) {
        Write-Error "AI-Craft agents directory still exists"
        $Errors++
    }
    
    # Check that commands are removed
    $CommandsCaiDir = Join-Path $ClaudeConfigDir "commands\cai"
    if (Test-Path $CommandsCaiDir) {
        Write-Error "AI-Craft commands directory still exists"
        $Errors++
    }
    
    # Check that config files are removed
    $ManifestFile = Join-Path $ClaudeConfigDir "ai-craft-manifest.txt"
    if (Test-Path $ManifestFile) {
        Write-Error "AI-Craft manifest file still exists"
        $Errors++
    }
    
    $InstallLogFile = Join-Path $ClaudeConfigDir "ai-craft-install.log"
    if (Test-Path $InstallLogFile) {
        Write-Error "AI-Craft installation log still exists"
        $Errors++
    }
    
    # Check for remaining backup directories
    $BackupsDir = Join-Path $ClaudeConfigDir "backups"
    if (Test-Path $BackupsDir) {
        $RemainingBackups = Get-ChildItem -Path $BackupsDir -Directory -Name "ai-craft-*" -ErrorAction SilentlyContinue
        foreach ($BackupName in $RemainingBackups) {
            Write-Error "AI-Craft backup directory still exists: $BackupName"
            $Errors++
        }
    }
    
    if ($Errors -eq 0) {
        Write-Info "Uninstallation validation: PASSED"
        return $true
    } else {
        Write-Error "Uninstallation validation: FAILED ($Errors errors)"
        return $false
    }
}

function New-UninstallReport {
    $ReportFile = Join-Path $ClaudeConfigDir "ai-craft-uninstall-report.txt"
    
    $ReportContent = @"
AI-Craft Framework Uninstallation Report
========================================
Uninstalled: $(Get-Date)
Computer: $env:COMPUTERNAME
User: $env:USERNAME

Uninstall Summary:
- AI-Craft agents removed from: $ClaudeConfigDir\agents\cai
- AI-Craft commands removed from: $ClaudeConfigDir\commands\cai
- Configuration files removed
- Installation logs removed
- Backup directories cleaned

$(if ($Backup) {
"Backup Information:
- Backup created: $BackupDir
- Backup contains: Complete framework state before removal
"
} else { "" })
Uninstallation completed successfully.
Framework completely removed from system.
"@
    
    Set-Content -Path $ReportFile -Value $ReportContent
    Write-Info "Uninstallation report created: $ReportFile"
}

# Main execution
function Main {
    if ($Help) {
        Show-Help
        exit 0
    }
    
    Write-Info "AI-Craft Framework Uninstallation Script"
    Write-Info "======================================="
    
    # Check for installation
    if (-not (Test-AiCraftInstallation)) {
        exit 0
    }
    
    # Confirm removal
    if (-not (Confirm-Removal)) {
        Write-Host ""
        Write-Host "Uninstallation cancelled by user." -ForegroundColor $Yellow
        exit 0
    }
    
    try {
        # Create backup if requested
        New-UninstallBackup
        
        # Remove components
        Remove-AiCraftAgents
        Remove-AiCraftCommands
        Remove-AiCraftConfigFiles
        Remove-AiCraftBackups
        Remove-AiCraftProjectFiles
        
        # Validate removal
        if (-not (Test-RemovalComplete)) {
            Write-Error "Uninstallation failed validation"
            exit 1
        }
        
        # Create report
        New-UninstallReport
        
        # Success message
        Write-Host ""
        Write-Info "✅ AI-Craft Framework uninstalled successfully!"
        Write-Host ""
        Write-Info "Summary:"
        Write-Info "- All AI-Craft agents removed"
        Write-Info "- All AI-Craft commands removed"
        Write-Info "- Configuration files cleaned"
        Write-Info "- Backup directories removed"
        
        if ($Backup) {
            Write-Host ""
            Write-Info "💾 Backup available at:"
            Write-Info "   $BackupDir"
            Write-Info "   Use this backup to restore if needed"
        }
        
        Write-Host ""
        Write-Info "The AI-Craft framework has been completely removed from your system."
        
    } catch {
        Write-Error "Uninstallation failed: $($_.Exception.Message)"
        exit 1
    }
}

# Execute main function
Main