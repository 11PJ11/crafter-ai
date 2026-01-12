---
description: 'Summarize achievements, archive to docs/evolution, clean up feature files [agent] [project-id] - Example: @devop "auth-upgrade"'
argument-hint: '[agent] [project-id] - Example: @devop "auth-upgrade"'
agent-activation:
  required: false
  agent-parameter: true
  agent-command: "*feature-finalize"
---

# DW-FINALIZE: Feature Completion, Archive, and Prepare for Push

## CRITICAL: Agent Invocation Protocol

**YOU ARE THE COORDINATOR** - Do NOT finalize the project yourself. Your role is to dispatch to the appropriate agent.

### STEP 1: Extract Agent Parameter

Parse the first argument to extract the agent name:
- User provides: `/dw:finalize @devop "auth-upgrade"`
- Extract agent name: `devop` (remove @ prefix)
- Validate agent name is one of: researcher, software-crafter, solution-architect, product-owner, acceptance-designer, devop

### STEP 2: Verify Agent Availability

Before proceeding to Task tool invocation:
- Verify the extracted agent name matches an available agent in the system
- Check agent is not at maximum concurrency
- Confirm agent type is compatible with this command

Valid agents: researcher, software-crafter, solution-architect, product-owner, acceptance-designer, devop

If agent unavailable:
- Return error: "Agent '{agent-name}' is not currently available. Available agents: {list}"
- Suggest alternative agents if applicable

### STEP 3: Extract Project ID

Extract the second argument (project ID):
- Example: `"auth-upgrade"`
- This should match the project-id in the feature directory

### Parameter Parsing Rules

Apply these rules to ALL extracted parameters:
1. Strip leading and trailing whitespace
2. Remove surrounding quotes (single or double) if present
3. Validate parameter is non-empty after stripping
4. Reject if extra parameters provided beyond expected count

Example for finalize.md:
- Input: `/dw:finalize  @devop  "auth-upgrade"`
- After parsing:
  - agent_name = "devop" (whitespace trimmed)
  - project_id = "auth-upgrade" (quotes removed)
- Input: `/dw:finalize @devop "auth-upgrade" extra`
- Error: "Too many parameters. Expected 2, got 3"

### STEP 4: Pre-Invocation Validation Checklist

Before invoking Task tool, verify ALL items:
- [ ] Agent name extracted and validated (not empty)
- [ ] Agent name in valid agent list
- [ ] Agent availability confirmed
- [ ] Project ID extracted and non-empty
- [ ] Project ID in valid kebab-case format
- [ ] Parameters contain no secrets or credentials
- [ ] Parameters within reasonable bounds (e.g., < 500 chars)
- [ ] No user input still has surrounding quotes

**ONLY proceed to Task tool invocation if ALL items above are checked.**

If any check fails, return specific error and stop.

### STEP 5: Invoke Agent Using Task Tool

**MANDATORY**: Use the Task tool to invoke the specified agent. Do NOT attempt to finalize the project yourself.

Invoke the Task tool with this exact pattern:

```
Task: "You are the {agent-name} agent.

Your specific role for this command: Summarize achievements, archive project evolution, and perform cleanup

Task type: finalize

Finalize and archive the completed feature: {project-id}

Your responsibilities:
1. Load project data from docs/feature/{project-id}/
2. Read roadmap.yaml and all step JSON files
3. Analyze execution history and completion metrics
4. Create comprehensive summary document
5. Archive to docs/evolution/ with date-feature naming (YYYY-MM-DD-{feature-name}.md)
6. Clean up temporary workflow files after user approval

CRITICAL: DO NOT COMMIT OR DELETE FILES - REQUEST APPROVAL FIRST

Processing Steps:

PHASE 1 - GATHER:
- Read docs/feature/{project-id}/roadmap.yaml
- Read all docs/feature/{project-id}/steps/*.json files
- Collect completion metrics, execution times, review feedback
- Identify key achievements and decisions

PHASE 2 - ANALYZE:
- Calculate completion statistics
- Extract execution times and token usage
- Document critical decisions made
- Summarize review outcomes
- Note deviations from plan

PHASE 3 - SUMMARIZE:
Create comprehensive markdown document with executive summary, original goal, phase-by-phase breakdown, key achievements, critical decisions table, quality metrics, challenges and solutions, deliverables and documentation, recommendations for future work, and lessons learned.

PHASE 4 - ARCHIVE:
- Ensure docs/evolution/ directory exists
- Save summary as: docs/evolution/YYYY-MM-DD-{project-id}.md (date-feature format for temporal ordering)
- Example: docs/evolution/2025-01-12-order-management.md
- Show user the archive location

PHASE 5 - CLEANUP (only after user approval):
- Delete docs/feature/{project-id}/steps/*.json
- Delete docs/feature/{project-id}/roadmap.yaml
- Delete docs/feature/{project-id}/ directory if empty
- Preserve the evolution archive and all deliverables

Show user a summary of what will be archived and deleted, then REQUEST APPROVAL before proceeding with cleanup."
```

**Parameter Substitution**:
- Replace `{agent-name}` with the extracted agent name (e.g., "devop")
- Replace `{project-id}` with the project ID

### Agent Registry

Valid agents are: researcher, software-crafter, solution-architect, product-owner, acceptance-designer, devop

Note: This list is maintained in sync with the agent registry at `~/.claude/agents/dw/`. If you encounter "agent not found" errors, verify the agent is registered in that location.

Each agent has specific capabilities:
- **researcher**: Information gathering, analysis, documentation
- **software-crafter**: Implementation, testing, refactoring, code quality
- **solution-architect**: System design, architecture decisions, planning
- **product-owner**: Requirements, business analysis, stakeholder alignment
- **acceptance-designer**: Test definition, acceptance criteria, BDD
- **devop**: Deployment, operations, infrastructure, lifecycle management

### Example Invocations

**For devop finalizing auth-upgrade project**:
```
Task: "You are the devop agent.

Your specific role for this command: Summarize achievements, archive project evolution, and perform cleanup

Task type: finalize

Finalize and archive the completed feature: auth-upgrade

[... rest of instructions ...]"
```

**For solution-architect finalizing microservices project**:
```
Task: "You are the solution-architect agent.

Your specific role for this command: Summarize achievements, archive project evolution, and perform cleanup

Task type: finalize

Finalize and archive the completed feature: microservices-migration

[... rest of instructions ...]"
```

### Error Handling

**Invalid Agent Name**:
- If agent name is not in the valid list, respond with error:
  "Invalid agent name: {name}. Must be one of: researcher, software-crafter, solution-architect, product-owner, acceptance-designer, devop"

**Missing Project ID**:
- If project ID is not provided, respond with error:
  "Project ID is required. Usage: /dw:finalize @agent 'project-id'"

**Project Not Found**:
- If project directory doesn't exist, respond with error:
  "Project not found: docs/feature/{project-id}/. Please verify project ID."

**Project Not Complete**:
- If project has incomplete tasks, warn user:
  "Warning: Project has {count} incomplete tasks. Are you sure you want to finalize?"

---

## Overview

Invokes an agent to create a comprehensive summary of completed workflow, archive it for historical tracking, and clean up all intermediary working files. Maintains project evolution history while keeping the repository clean.

Creates permanent record in docs/evolution/ and removes temporary workflow artifacts.

## Usage Examples

```bash
# Finalize completed authentication upgrade project
/dw:finalize @devop "auth-upgrade"

# Finalize microservices migration with architect summary
/dw:finalize @solution-architect "microservices-migration"

# Finalize data pipeline project
/dw:finalize @data-engineer "analytics-pipeline"
```

## Complete Workflow Integration

These commands work together to form a complete workflow:

```bash
# Step 1: Create comprehensive plan
/dw:roadmap @solution-architect "Migrate authentication system"

# Step 2: Decompose into atomic tasks
/dw:split @solution-architect "auth-migration"

# Step 3: Execute first research task
/dw:execute @researcher "docs/feature/auth-migration/steps/01-01.json"

# Step 4: Review before implementation
/dw:review @software-crafter task "docs/feature/auth-migration/steps/02-01.json"

# Step 5: Execute implementation
/dw:execute @software-crafter "docs/feature/auth-migration/steps/02-01.json"

# Step 6: Finalize when all tasks complete
/dw:finalize @devop "auth-migration"
```

For details on each command, see respective sections.

## Context Files Required

- docs/feature/{project-id}/roadmap.yaml - Original roadmap
- docs/feature/{project-id}/steps/*.json - All step tracking files

---

## Coordinator Success Criteria

Verify the coordinator performed these tasks:
- [ ] Agent name extracted from parameters correctly
- [ ] Agent name validated against known agents
- [ ] Project ID extracted and validated
- [ ] Pre-invocation validation checklist passed
- [ ] Task tool invocation prepared with correct parameters
- [ ] Task tool returned success status
- [ ] User received confirmation of agent invocation

## Agent Execution Success Criteria

The invoked agent must accomplish (Reference Only):
- [ ] All step files successfully read
- [ ] Roadmap file successfully parsed
- [ ] Comprehensive summary generated
- [ ] Evolution document created in docs/evolution/
- [ ] User approved summary content
- [ ] Workflow directory cleaned up
- [ ] Step files removed
- [ ] Roadmap file removed
- [ ] Project folder removed (if empty)

---

## Agent Invocation (Reference Documentation)

The following section documents what the invoked agent will do. **You (the coordinator) do not execute this - the agent does.**

### Primary Task Instructions

**CRITICAL: DO NOT COMMIT FILES - REQUEST APPROVAL FIRST**

**Task**: Summarize achievements, archive history, and clean up workflow files

**Input**: `docs/feature/{project-id}/`
**Output**: `docs/evolution/YYYY-MM-DD-{project-id}.md` (date-feature format for temporal ordering)

**Processing Steps:**

#### 1. GATHER PHASE

**Load Project Data**:
```python
1. Read roadmap.yaml - Get project goals and planned steps
2. Read all step JSON files - Extract execution history
3. Collect completion metrics
4. Identify key achievements
5. Extract review feedback and decisions
```

#### 2. ANALYSIS PHASE

**Analyze Project Execution**:
- Calculate completion statistics
- Identify completed vs skipped steps
- Extract execution times and token usage
- Document critical decisions made
- Summarize review outcomes
- Note any deviations from plan

#### 3. SUMMARY GENERATION PHASE

**Create Comprehensive Summary Document**:

```markdown
# Project Evolution: {project-name}

**Project ID**: {project-id}
**Completed**: {timestamp}
**Duration**: {start-date} to {end-date}
**Methodology**: {standard|mikado}

## Executive Summary

{2-3 paragraph overview of project goal, approach, and outcome}

## Original Goal

{from roadmap.yaml - original project goal}

## Project Phases

### Phase 1: {phase-name}
**Purpose**: {phase purpose}
**Steps Completed**: {X/Y}

#### Step 1.1: {step-name}
- **Status**: DONE
- **Execution Time**: {hours}
- **Agent**: {@agent-name}
- **Key Outcomes**:
  - {outcome 1}
  - {outcome 2}
- **Artifacts Created**:
  - {file 1}
  - {file 2}

### Phase 2: {phase-name}
...

## Key Achievements

1. **{Achievement 1}**
   - Description: {what was achieved}
   - Impact: {business/technical value}
   - Evidence: {artifacts/metrics}

2. **{Achievement 2}**
   ...

## Critical Decisions

| Decision | Context | Rationale | Outcome |
|----------|---------|-----------|---------|
| {decision} | {why needed} | {why chosen} | {result} |

## Quality Metrics

### Execution Statistics
- **Total Steps Planned**: {count}
- **Steps Completed**: {count} ({percentage}%)
- **Steps Skipped**: {count}
- **Total Execution Time**: {hours}
- **Average Step Duration**: {hours}

### Review Statistics
- **Roadmap Reviews**: {count}
- **Task Reviews**: {count}
- **Implementation Reviews**: {count}
- **Issues Found**: {HIGH: X, MEDIUM: Y, LOW: Z}
- **Issues Resolved**: {count}

### Resource Usage
- **Total Tokens**: {approximate total}
- **Estimated Cost**: {if available}
- **Agent Invocations**: {count by agent type}

## Challenges and Solutions

### Challenge 1: {challenge description}
- **Impact**: {what was affected}
- **Solution**: {how it was resolved}
- **Lesson Learned**: {takeaway}

### Challenge 2: {challenge description}
...

## Deliverables

### Production Artifacts
- {list of final deliverables}
- {documentation created}
- {systems deployed}

### Documentation
- {architecture diagrams}
- {technical documentation}
- {operational guides}

## Deviations from Plan

| Planned Step | Actual Execution | Reason |
|-------------|------------------|--------|
| {step} | {what happened} | {why different} |

## Review Feedback Incorporated

### Roadmap Review
- {key feedback item and how addressed}

### Implementation Reviews
- {quality improvements made}
- {issues resolved}

## Recommendations for Future Work

1. **{Recommendation 1}**
   - Priority: {HIGH|MEDIUM|LOW}
   - Effort: {estimate}
   - Value: {expected benefit}

2. **{Recommendation 2}**
   ...

## Lessons Learned

### What Worked Well
- {practice or approach that was effective}

### What Could Improve
- {area for improvement}

### Process Improvements
- {suggestions for future projects}

## Project Timeline

```
{visual timeline of major milestones}
Start: {date}
├─ Phase 1 Complete: {date}
├─ Phase 2 Complete: {date}
├─ Phase 3 Complete: {date}
└─ Project Complete: {date}
```

## References

- **Original Roadmap**: {brief description or key points}
- **Architecture Decisions**: {reference to ADRs if any}
- **Related Projects**: {links or references}

---

**Project Status**: COMPLETED
**Archived By**: {agent-name}
**Archive Date**: {timestamp}
```

#### 4. ARCHIVE PHASE

**Save Evolution Record**:
```python
1. Ensure docs/evolution/ directory exists
2. Generate filename using date-feature format: YYYY-MM-DD-{project-id}.md
   # Example: 2025-01-12-order-management.md
   # This format ensures temporal ordering when listing files
3. Write summary document
4. Verify file created successfully
```

#### 5. CLEANUP PHASE

**IMPORTANT: Only proceed after user confirms summary is acceptable**

**Remove Workflow Artifacts**:
```python
1. Delete docs/feature/{project-id}/steps/ directory
2. Delete docs/feature/{project-id}/roadmap.yaml
3. Delete docs/feature/{project-id}/ directory (if empty)
4. Verify cleanup completed
```

**Files to Remove**:
- `docs/feature/{project-id}/steps/*.json` - All step tracking files
- `docs/feature/{project-id}/roadmap.yaml` - Original roadmap
- `docs/feature/{project-id}/` - Project workflow directory

**Files to Preserve**:
- `docs/evolution/YYYY-MM-DD-{project-id}.md` - Permanent archive (date-feature format)
- Any deliverable artifacts referenced in summary
- Production code and documentation

### Folder Structure After Finalization

```
docs/
├── evolution/                    # Permanent project history (date-feature naming)
│   ├── 2025-01-12-auth-upgrade.md
│   ├── 2025-01-15-api-refactor.md
│   └── 2025-02-01-microservices-migration.md
└── feature/                      # Empty or removed (cleaned up)
```

**Note**: The date-feature naming (YYYY-MM-DD-{feature-name}.md) ensures:
- Temporal ordering when listing files
- Easy identification of when features were completed
- Chronological project evolution view

## Output Artifacts

- `docs/evolution/YYYY-MM-DD-{project-id}.md` - Permanent project archive (date-feature format)
- Console summary showing:
  - Steps completed
  - Total execution time
  - Key achievements
  - Archive location

## Notes

### Archive Philosophy

The evolution directory serves as the permanent historical record of project development:
- **Tracks progress over time**: See how the project evolved
- **Preserves decisions**: Understand why choices were made
- **Enables retrospectives**: Learn from past projects
- **Provides templates**: Reference successful patterns
- **Documents legacy**: Maintain institutional knowledge

### Cleanup Rationale

Removing intermediary workflow files:
- **Reduces repository clutter**: Keep only what matters long-term
- **Prevents confusion**: Avoid mixing active and completed projects
- **Encourages archival**: Forces proper documentation before cleanup
- **Maintains focus**: Active workflow directory shows current work only

### When to Finalize

Finalize a project when:
- All acceptance criteria met
- Implementation reviewed and approved
- Production deployment complete
- No pending tasks remain
- Team consensus on completion

### Recovery Options

If files need to be recovered:
1. Check git history (before cleanup commit)
2. Review evolution document for context
3. Restore from backups if available
4. Use evolution document to recreate workflow if needed

### Integration with Workflow

```
Execute Tasks → Review → All Complete
                          ↓
                   FINALIZE
                          ↓
              Archive + Cleanup
                          ↓
                Evolution Record
```

This finalization process ensures clean project closure while maintaining comprehensive historical records for organizational learning and future reference.
