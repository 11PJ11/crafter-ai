# Wave Checkpoint Documentation

## Current Wave Status

- **Wave**: [Current wave number and name]
- **Status**: [NOT_STARTED | IN_PROGRESS | COMPLETED | FAILED]
- **Progress**: [Percentage complete]
- **Started**: [Timestamp when wave began]
- **Estimated Completion**: [Expected completion time]

## Feature Context

- **Feature Name**: [Name of feature being developed]
- **Session ID**: [Unique session identifier]
- **Development Start**: [When feature development began]
- **Business Priority**: [High | Medium | Low]

## Current Wave Details

### Wave Objective
[Clear description of what this wave aims to accomplish]

### Primary Agent
- **Agent**: [Name of primary agent responsible]
- **Status**: [QUEUED | EXECUTING | COMPLETED | FAILED]
- **Started**: [When agent execution began]
- **Context**: [Key context information for agent]

### Specialist Agents
[List of specialist agents and their status]
- **[Agent Name]**: [Status] - [Context/Notes]
- **[Agent Name]**: [Status] - [Context/Notes]

### Input Files Required
[List of files needed for current wave]
- ✅ `${DOCS_PATH}/[filename]` - [Status/Notes]
- ⚠️ `${DOCS_PATH}/[filename]` - [Status/Notes]
- ❌ `${DOCS_PATH}/[filename]` - [Status/Notes]

### Expected Output Files
[List of files this wave will produce]
- 📝 `${DOCS_PATH}/[filename]` - [Expected content description]
- 📝 `${DOCS_PATH}/[filename]` - [Expected content description]

## Quality Gates Status

### Current Wave Gates
[Completion criteria for current wave]
- ✅ [Completed criterion]
- 🔄 [In progress criterion] 
- ❌ [Not started criterion]

### Overall Quality Status
- **Requirements Validation**: [Status]
- **Architecture Alignment**: [Status]
- **Test Coverage**: [Status]
- **Code Quality**: [Status]
- **Security Compliance**: [Status]

## Context Isolation

### Current Wave Context
[Key information for current wave agents]
```yaml
business_context: [Essential business information]
technical_context: [Technical constraints and requirements]
quality_requirements: [Quality standards to meet]
```

### Next Wave Context
[Information being prepared for next wave]
```yaml
handoff_deliverables: [What will be passed to next wave]
validation_status: [Current validation state]
open_questions: [Issues to resolve before handoff]
```

## Progress Tracking

### Completed Waves
1. **DISCUSS**: ✅ [Completion date] - [Key deliverables]
2. **ARCHITECT**: ✅ [Completion date] - [Key deliverables]

### Current Wave Progress
- **Overall Progress**: [X]% complete
- **Agent Execution**: [X]% complete
- **Quality Validation**: [X]% complete
- **Output Generation**: [X]% complete

### Remaining Waves
4. **DEVELOP**: ⏳ [Estimated start] - [Expected deliverables]
5. **DEMO**: ⏳ [Estimated start] - [Expected deliverables]

## Interruption Recovery Information

### Last Safe Checkpoint
- **Checkpoint Time**: [Timestamp of last safe state]
- **Checkpoint Wave**: [Wave number and status at checkpoint]
- **Files State**: [State of all files at checkpoint]

### Resume Capability
- **Can Resume**: [Yes | No]
- **Resume Point**: [Where execution should continue]
- **Context Preservation**: [Status of preserved context]
- **Required Actions**: [What needs to be done to resume]

### Recovery Context
```yaml
execution_state: [State of current execution]
agent_context: [Preserved agent context]
file_dependencies: [Status of file dependencies]
quality_state: [Current quality validation status]
```

## Issues and Blockers

### Current Issues
[Any issues preventing progress]
- 🚨 **[Issue Type]**: [Description] - [Impact] - [Required Resolution]

### Blockers
[Dependencies blocking current wave progression]
- 🛑 **[Blocker Type]**: [Description] - [Blocking Agent/Process] - [Resolution Required]

### Warnings
[Potential issues that need monitoring]
- ⚠️ **[Warning Type]**: [Description] - [Potential Impact] - [Monitoring Required]

## Next Actions Required

### Immediate Actions
[Actions required to continue current wave]
1. [Action description] - [Responsible agent/person] - [Expected completion]
2. [Action description] - [Responsible agent/person] - [Expected completion]

### Wave Transition Actions
[Actions needed for successful wave handoff]
1. [Action description] - [Validation criteria] - [Expected completion]
2. [Action description] - [Validation criteria] - [Expected completion]

### Quality Assurance Actions
[Actions needed to meet quality gates]
1. [Action description] - [Quality metric] - [Acceptance criteria]
2. [Action description] - [Quality metric] - [Acceptance criteria]

## State Management

### File System State
- **Created Files**: [Count] files created this session
- **Modified Files**: [Count] files modified this session
- **Validated Files**: [Count] files validated this session

### Agent Execution State
- **Active Agents**: [Count] agents currently executing
- **Completed Agents**: [Count] agents successfully completed
- **Failed Agents**: [Count] agents that failed execution

### Context Preservation State
- **Context Size**: [Size of preserved context]
- **Context Validity**: [Valid | Stale | Corrupted]
- **Context Backup**: [Backup available | No backup]

---

*This checkpoint document is maintained by the pipeline-state-manager agent and updated at each wave transition and critical execution point.*

*File Location: `${STATE_PATH}/${WAVE_CHECKPOINT_FILE}`*

*Last Updated: [Timestamp]*