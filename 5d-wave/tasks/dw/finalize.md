---
agent-activation:
  required: false
  agent-parameter: true
  agent-command: "*workflow-finalize"
---

# DW-FINALIZE: Project Completion and Archive

**Type**: Workflow Completion Tool
**Agent**: Specified as parameter
**Command**: `/dw:finalize [agent] [project-id]`

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

## Context Files Required

- docs/workflow/{project-id}/roadmap.yaml - Original roadmap
- docs/workflow/{project-id}/steps/*.json - All step tracking files

## Agent Invocation

@{specified-agent}

Finalize and archive project: {project-id}

### Primary Task Instructions

**⚠️ CRITICAL: DO NOT COMMIT FILES - REQUEST APPROVAL FIRST**

**Task**: Summarize achievements, archive history, and clean up workflow files

**Input**: `docs/workflow/{project-id}/`
**Output**: `docs/evolution/{project-id}-{timestamp}.md`

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

**Project Status**: COMPLETED ✅
**Archived By**: {agent-name}
**Archive Date**: {timestamp}
```

#### 4. ARCHIVE PHASE

**Save Evolution Record**:
```python
1. Ensure docs/evolution/ directory exists
2. Generate filename: {project-id}-{YYYYMMDD-HHMMSS}.md
3. Write summary document
4. Verify file created successfully
```

#### 5. CLEANUP PHASE

**⚠️ IMPORTANT: Only proceed after user confirms summary is acceptable**

**Remove Workflow Artifacts**:
```python
1. Delete docs/workflow/{project-id}/steps/ directory
2. Delete docs/workflow/{project-id}/roadmap.yaml
3. Delete docs/workflow/{project-id}/ directory (if empty)
4. Verify cleanup completed
```

**Files to Remove**:
- `docs/workflow/{project-id}/steps/*.json` - All step tracking files
- `docs/workflow/{project-id}/roadmap.yaml` - Original roadmap
- `docs/workflow/{project-id}/` - Project workflow directory

**Files to Preserve**:
- `docs/evolution/{project-id}-{timestamp}.md` - Permanent archive
- Any deliverable artifacts referenced in summary
- Production code and documentation

### Folder Structure After Finalization

```
docs/
├── evolution/                    # Permanent project history
│   ├── auth-upgrade-20240115-143000.md
│   ├── api-refactor-20240120-091500.md
│   └── microservices-20240201-165500.md
└── workflow/                     # Empty or removed
```

## Success Criteria

**Validation Checklist**:
- [ ] All step files successfully read
- [ ] Roadmap file successfully parsed
- [ ] Comprehensive summary generated
- [ ] Evolution document created in docs/evolution/
- [ ] User approved summary content
- [ ] Workflow directory cleaned up
- [ ] Step files removed
- [ ] Roadmap file removed
- [ ] Project folder removed (if empty)

## Output Artifacts

- `docs/evolution/{project-id}-{timestamp}.md` - Permanent project archive
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