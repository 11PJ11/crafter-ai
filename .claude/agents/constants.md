# AI-Craft Agent Constants

Shared constants and configuration values used across all AI-Craft pipeline agents.

## Path Constants

### Documentation Paths
```yaml
DOCS_PATH: "docs/craft-ai"
```

**Usage**: All agents should reference `${DOCS_PATH}` instead of hardcoding documentation paths.

**Examples**:
- Requirements file: `${DOCS_PATH}/requirements.md`
- Architecture file: `${DOCS_PATH}/architecture.md` 
- Acceptance tests: `${DOCS_PATH}/acceptance-tests.md`
- Progress tracking: `${DOCS_PATH}/PROGRESS.md`

## File Name Constants

### Core Documentation Files
```yaml
REQUIREMENTS_FILE: "requirements.md"
ARCHITECTURE_FILE: "architecture.md"
ACCEPTANCE_TESTS_FILE: "acceptance-tests.md"
PROGRESS_FILE: "PROGRESS.md"
QUALITY_REPORT_FILE: "quality-report.md"
TECHNICAL_DEBT_FILE: "technical-debt.md"
DEVELOPMENT_PLAN_FILE: "development-plan.md"
IMPLEMENTATION_STATUS_FILE: "implementation-status.md"
INTEGRATION_STATUS_FILE: "integration-status.md"
ARCHITECTURE_DIAGRAMS_FILE: "architecture-diagrams.md"
REFACTORING_NOTES_FILE: "refactoring-notes.md"
COMPREHENSIVE_REFACTORING_REPORT_FILE: "comprehensive-refactoring-report.md"
PIPELINE_STATUS_FILE: "pipeline-status.md"
```

## Agent Interaction Constants

### Collaboration Patterns
```yaml
SPECIALIST_ACTIVATION_THRESHOLD: "conditional"
QUALITY_GATES_REQUIRED: true
SINGLE_RESPONSIBILITY_PRINCIPLE: true
```

## Output Format Constants

### Standard Sections
```yaml
ANALYSIS_DATE_FORMAT: "[Timestamp]"
STATUS_INDICATORS:
  COMPLETE: "✅ COMPLETE"
  IN_PROGRESS: "🔄 IN PROGRESS"
  NEEDS_REVIEW: "⚠️ NEEDS REVIEW"
  VALIDATED: "✅ VALIDATED"
  COMPLIANT: "✅ COMPLIANT"
```

## Usage Guidelines

### Path References
Always use `${DOCS_PATH}/filename.md` format in agent files instead of hardcoded paths.

### File References  
Use `${DOCS_PATH}/${REQUIREMENTS_FILE}` instead of `docs/craft-ai/requirements.md`.

### Future Maintenance
When paths or file names need to change, only update this constants file - all agent references will automatically use the new values.

## Version
- **Created**: 2024-09-13
- **Purpose**: Centralize agent configuration and eliminate hardcoded paths
- **Scope**: All AI-Craft pipeline agents