# Claude Code Command Integration: cai/atdd

This document specifies the integration of `cai/atdd` as a built-in Claude Code command, following the existing command patterns and architecture.

## Command Registration

### Command Definition
```yaml
command: "cai/atdd"
category: "Craft-AI Pipeline"
description: "Intelligent ATDD workflow initiation with project context analysis"
aliases: ["cai/atdd", "/cai/atdd"]
agent_delegation: "atdd-command-processor"
```

### Integration with Claude Code Command System

Following the pattern of existing commands like `/sc:analyze`, the `cai/atdd` command should be:

1. **Recognized by Claude Code** as a built-in command
2. **Auto-delegated** to the `atdd-command-processor` agent
3. **Integrated** with Claude Code's context and session management
4. **Supported** by command completion and help systems

## Command Syntax Integration

### Basic Command Pattern
```bash
cai/atdd [feature-description] [flags]
```

### Command Examples
```bash
# Basic usage
cai/atdd "implement user authentication system"

# With analysis flag
cai/atdd "add payment processing" --analyze-existing

# Stage specification
cai/atdd "OAuth2 integration" --from-stage=architect

# Resume workflow
cai/atdd --resume auth-feature-2024-01

# Status check
cai/atdd --status
```

### Flag Integration
Following Claude Code flag patterns:
- `--analyze-existing` - Analyze current project context
- `--from-stage=[stage]` - Start from specific ATDD stage
- `--project-scan` - Deep project context analysis  
- `--resume [id]` - Resume existing workflow
- `--status` - Show workflow status
- `--help` - Show command help and usage

## Claude Code Integration Points

### 1. Command Parser Integration
```javascript
// Pseudo-code for command recognition
const ATDD_COMMAND_PATTERN = /^(?:\/)?cai\/atdd\s*(.*)/;

function parseCommand(input) {
  const match = input.match(ATDD_COMMAND_PATTERN);
  if (match) {
    return {
      type: 'cai/atdd',
      args: parseATDDArgs(match[1]),
      shouldDelegate: true,
      targetAgent: 'atdd-command-processor'
    };
  }
  // ... other command parsing
}
```

### 2. Agent Delegation
```javascript
// Integration with existing agent delegation system
function delegateATDDCommand(command) {
  return delegateToAgent({
    agent: 'atdd-command-processor',
    context: {
      command: command.type,
      arguments: command.args,
      workingDirectory: getCurrentWorkingDirectory(),
      projectContext: getCurrentProjectContext()
    },
    tools: ['Read', 'Write', 'Edit', 'Grep', 'Glob', 'Task'],
    timeout: 300000 // 5 minutes for analysis
  });
}
```

### 3. Help System Integration
```yaml
command_help:
  name: "cai/atdd"
  description: "Craft-AI ATDD workflow with intelligent project analysis"
  usage: "cai/atdd [feature-description] [flags]"
  
  examples:
    - command: 'cai/atdd "implement user login"'
      description: "Start ATDD workflow for user login feature"
    - command: 'cai/atdd "add search" --analyze-existing'
      description: "Analyze project context before starting search feature"
    - command: 'cai/atdd --status'
      description: "Show current ATDD workflow status"
  
  flags:
    - flag: "--analyze-existing"
      description: "Analyze existing project context before starting"
    - flag: "--from-stage=[stage]"
      description: "Start from specific stage (discuss|architect|distill|develop|demo)"
    - flag: "--resume [id]"
      description: "Resume existing workflow by ID"
    - flag: "--status"
      description: "Show current workflow status and progress"
```

### 4. Context Integration
```javascript
// Integration with Claude Code's context system
function prepareATDDContext() {
  return {
    // Current session context
    sessionId: getCurrentSessionId(),
    workingDirectory: process.cwd(),
    
    // Project context
    projectRoot: findProjectRoot(),
    gitRepository: getGitRepository(),
    
    // Available tools and capabilities
    availableAgents: getAvailableAgents(),
    toolPermissions: getToolPermissions(),
    
    // User preferences
    userConfig: getUserConfig(),
    previousWorkflows: getPreviousATDDWorkflows()
  };
}
```

## Command Flow Integration

### 1. Command Recognition
```
User types: cai/atdd "add user registration"
   ↓
Claude Code recognizes cai/atdd command pattern
   ↓
Parses arguments and flags
   ↓
Prepares delegation context
```

### 2. Agent Delegation
```
Claude Code → atdd-command-processor agent
   ↓
Agent analyzes project context
   ↓
Agent determines optimal workflow entry point
   ↓
Agent delegates to atdd-wave-coordinator
   ↓
Wave coordinator orchestrates ATDD stages
```

### 3. Result Integration
```
ATDD workflow results → atdd-command-processor
   ↓
Command processor formats results
   ↓
Results returned to Claude Code
   ↓
Claude Code presents results to user
```

## Error Handling Integration

### Command Validation
```javascript
function validateATDDCommand(args) {
  // Validate required arguments
  if (!args.featureDescription && !args.resume && !args.status) {
    throw new CommandError(
      "Feature description required", 
      "Usage: cai/atdd 'feature description'"
    );
  }
  
  // Validate stage specification
  if (args.fromStage && !VALID_STAGES.includes(args.fromStage)) {
    throw new CommandError(
      `Invalid stage: ${args.fromStage}`,
      `Valid stages: ${VALID_STAGES.join(', ')}`
    );
  }
  
  // Validate workflow ID for resume
  if (args.resume && !isValidWorkflowId(args.resume)) {
    throw new CommandError(
      "Invalid workflow ID",
      "Use 'cai/atdd --status' to see available workflows"
    );
  }
}
```

### Agent Error Handling
```javascript
function handleATDDAgentError(error) {
  switch (error.type) {
    case 'PROJECT_ANALYSIS_FAILED':
      return {
        message: "Unable to analyze project context",
        suggestion: "Ensure you're in a project directory with source code or documentation",
        fallback: "Starting with requirements gathering (DISCUSS stage)"
      };
      
    case 'WORKFLOW_NOT_FOUND':
      return {
        message: `Workflow '${error.workflowId}' not found`,
        suggestion: "Use 'cai/atdd --status' to see available workflows"
      };
      
    case 'AGENT_DELEGATION_FAILED':
      return {
        message: "Failed to start ATDD workflow",
        suggestion: "Check agent availability and try again"
      };
      
    default:
      return {
        message: "ATDD command failed",
        suggestion: "Try again or use 'cai/atdd --help' for usage information"
      };
  }
}
```

## Configuration Integration

### User Configuration
```yaml
# In user's Claude Code configuration
cai:
  atdd:
    # Default behavior settings
    default_analyze_existing: true
    auto_resume_workflows: true
    preferred_documentation_path: "docs/craft-ai"
    
    # Project detection settings
    project_indicators: [".git", "package.json", "requirements.txt", "pom.xml"]
    documentation_patterns: ["README*", "docs/**/*", "*.md"]
    
    # Workflow preferences
    default_entry_stage: "auto" # or specific stage
    context_confidence_threshold: 0.8
    enable_progress_notifications: true
```

### Global Configuration
```yaml
# In Claude Code global configuration
commands:
  "cai/atdd":
    enabled: true
    agent: "atdd-command-processor"
    timeout: 300000
    
    # Integration settings
    delegate_automatically: true
    preserve_context: true
    enable_workflows: true
    
    # Resource limits
    max_concurrent_workflows: 3
    max_analysis_time: 120000
    file_scan_limit: 1000
```

## Command Completion Integration

### Bash/Zsh Completion
```bash
# Auto-completion for cai/atdd command
_cai_atdd_completion() {
  local cur prev opts
  cur="${COMP_WORDS[COMP_CWORD]}"
  prev="${COMP_WORDS[COMP_CWORD-1]}"
  
  opts="--analyze-existing --from-stage --project-scan --resume --status --help"
  stages="discuss architect distill develop demo"
  
  case "${prev}" in
    --from-stage)
      COMPREPLY=( $(compgen -W "${stages}" -- ${cur}) )
      return 0
      ;;
    --resume)
      # Complete with available workflow IDs
      COMPREPLY=( $(compgen -W "$(cai/atdd --status --ids-only)" -- ${cur}) )
      return 0
      ;;
    *)
      COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
      return 0
      ;;
  esac
}

complete -F _cai_atdd_completion cai/atdd
```

## Progress Integration

### Status Reporting
```javascript
// Integration with Claude Code's progress reporting
function reportATDDProgress(workflowId, stage, progress) {
  ClaudeCode.progress.update({
    id: workflowId,
    title: `ATDD Workflow: ${workflowId}`,
    stage: stage,
    progress: progress,
    description: `Currently in ${stage} stage`,
    actions: [
      { label: "View Details", command: `cai/atdd --status ${workflowId}` },
      { label: "Cancel", command: `cai/atdd --cancel ${workflowId}` }
    ]
  });
}
```

### Notification Integration
```javascript
// Integration with Claude Code's notification system
function notifyATDDCompletion(workflowId, result) {
  ClaudeCode.notifications.show({
    type: result.success ? 'success' : 'error',
    title: 'ATDD Workflow Complete',
    message: `Feature '${result.featureName}' ${result.success ? 'completed successfully' : 'failed'}`,
    actions: [
      { label: "View Results", command: `open ${result.outputPath}` },
      { label: "Start New", command: "cai/atdd" }
    ]
  });
}
```

## Implementation Checklist

### Core Integration
- [ ] Add command pattern recognition for `cai/atdd`
- [ ] Implement argument parsing for ATDD-specific flags
- [ ] Integrate with existing agent delegation system
- [ ] Add error handling for ATDD-specific errors

### User Experience
- [ ] Add command to help system and documentation
- [ ] Implement command completion for shells
- [ ] Add progress reporting for long-running workflows
- [ ] Integrate with notification system

### Configuration
- [ ] Add ATDD-specific configuration options
- [ ] Support user preferences for workflow behavior
- [ ] Enable/disable command through configuration

### Testing
- [ ] Unit tests for command parsing
- [ ] Integration tests for agent delegation
- [ ] End-to-end tests for complete workflows
- [ ] Error handling test coverage

This integration specification provides the blueprint for making `cai/atdd` a first-class Claude Code command that leverages the existing AI-Craft agent infrastructure.