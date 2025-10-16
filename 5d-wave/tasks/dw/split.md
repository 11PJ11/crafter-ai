---
description: 'Generate atomic task files from roadmap [agent] [project-id]'
argument-hint: '[agent] [project-id] - Example: @devop "auth-upgrade"'
agent-activation:
  required: false
  agent-parameter: true
  agent-command: "*workflow-split"
---

# DW-SPLIT: Atomic Task Generation from Roadmap

**Type**: Task Decomposition Tool
**Agent**: Specified as parameter
**Command**: `/dw:split [agent] [project-id]`

## Overview

Invokes an agent to parse a comprehensive roadmap and generate self-contained, atomic task files that sub-agents can execute independently without context degradation.

Each generated task file contains all information needed for completion, enabling parallel execution and preventing the accumulation of context that degrades LLM performance over long conversations.

## Usage Examples

```bash
# Split architecture roadmap into tasks
/dw:split @devop "microservices-migration"

# Split data pipeline roadmap
/dw:split @data-engineer "analytics-pipeline"

# Split refactoring roadmap
/dw:split @software-crafter "auth-refactor"
```

## Key Benefits

- **Context Preservation**: Each task is self-contained with all required information
- **Parallel Execution**: Sub-agents can work on tasks independently
- **Progress Tracking**: Individual task state management
- **Quality Consistency**: Each task starts from clean context
- **Scalability**: Handle complex projects without context overflow

## Context Files Required

- docs/workflow/{project-id}/roadmap.yaml - Master roadmap document
- Must be created by DW-ROADMAP command first

## Agent Invocation

@{specified-agent}

Generate atomic task files from roadmap for project: {project-id}

### Primary Task Instructions

**⚠️ CRITICAL: DO NOT COMMIT FILES - REQUEST APPROVAL FIRST**

**Task**: Transform roadmap into self-contained atomic task files

**Input**: `docs/workflow/{project-id}/roadmap.yaml`
**Output**: `docs/workflow/{project-id}/steps/*.json`

**Core Principle**: Each generated file must be **completely self-contained** so a sub-agent can execute it without any prior context or knowledge of other steps.

**Processing Steps:**
1. Parse the roadmap.yaml file
2. Extract and enrich each step with complete context
3. Ensure all dependencies are explicitly documented
4. Include all necessary background information
5. Generate atomic task files for sub-agent execution

**Generated Atomic Task Schema:**

Each file (`{phase:02d}-{step:02d}.json`) is a complete, executable unit:

```json
{
  "task_id": "{phase:02d}-{step:02d}",
  "project_id": "from-roadmap",
  "execution_agent": "auto-selected-or-specified",
  "self_contained_context": {
    "background": "Complete context for this specific task",
    "prerequisites_completed": ["List of completed dependencies"],
    "relevant_files": ["Files needed for this task"],
    "technical_context": "Any technical details required"
  },
  "task_specification": {
    "name": "from-roadmap-step",
    "description": "What needs to be done",
    "motivation": "Why this is important",
    "detailed_instructions": "Step-by-step guide with all needed info",
    "acceptance_criteria": ["Clear success conditions"],
    "estimated_hours": "from-roadmap"
  },
  "dependencies": {
    "requires": ["task-ids that must complete first"],
    "blocking": ["task-ids waiting for this"]
  },
  "state": {
    "status": "TODO",
    "assigned_to": null,
    "started_at": null,
    "completed_at": null,
    "updated": "current-timestamp"
  }
}
```

**Optional Fields (add only when needed):**
- `token_limit`: number (default: 0 = unlimited)
- `examples`: Array of code examples
  ```json
  [{
    "id": 1,
    "language": "python",
    "code": "actual code here",
    "tags": ["best_practice"]
  }]
  ```
- `state_history`: Track state transitions
  ```json
  [{
    "status": "TODO",
    "result": "Initial creation",
    "updated": "2024-01-01T00:00:00Z"
  }]
  ```
- `critiques`: Review feedback
  ```json
  [{
    "id": 1,
    "reviewer": "user",
    "description": "Feedback text",
    "created": "2024-01-01T00:00:00Z"
  }]
  ```

**Valid Enumerations:**
- Status: `TODO`, `IN_PROGRESS`, `DONE`, `FAILED`, `WAITING`
- Tags: `error`, `warning`, `best_practice`, `antipattern`

### Folder Structure Created:
```
docs/workflow/
├── {project-id}/
│   ├── roadmap.yaml          # Source roadmap (already exists)
│   └── steps/                # Generated tracking files
│       ├── 01-01.json        # Phase 1, Step 1
│       ├── 01-02.json        # Phase 1, Step 2
│       ├── 02-01.json        # Phase 2, Step 1
│       └── ...
```

### Example Self-Contained Task (auth-upgrade/steps/01-01.json):

A complete, atomic task ready for sub-agent execution:

```json
{
  "task_id": "01-01",
  "project_id": "auth-upgrade",
  "execution_agent": "@researcher",
  "self_contained_context": {
    "background": "Current system uses basic auth with username/password stored in PostgreSQL. Company policy requires OAuth2 compliance by Q2. Budget allocated: $5000/year for provider costs.",
    "prerequisites_completed": [],
    "relevant_files": ["docs/current-auth-architecture.md", "requirements/security-policy.md"],
    "technical_context": "Stack: Node.js/Express backend, React frontend, PostgreSQL database. Current user base: 10,000 active users. Peak load: 500 concurrent sessions."
  },
  "task_specification": {
    "name": "OAuth2 Provider Selection",
    "description": "Research, evaluate and recommend OAuth2 provider for authentication system upgrade",
    "motivation": "Provider choice determines integration complexity, costs, and feature availability for entire authentication rewrite",
    "detailed_instructions": "1. Research OAuth2 providers supporting our tech stack (Auth0, Okta, AWS Cognito, Firebase Auth, Keycloak)\n2. Create comparison matrix: features, pricing, integration effort, documentation quality\n3. Evaluate against requirements: SSO support, MFA, user migration tools, API rate limits\n4. Perform cost analysis for 10K users with 20% yearly growth\n5. Document recommendation with justification in docs/workflow/auth-upgrade/provider-selection.md",
    "acceptance_criteria": [
      "Comparison matrix includes at least 5 providers",
      "Cost projections for 3 years included",
      "Integration complexity assessed for our stack",
      "Clear recommendation with pros/cons",
      "Decision document created"
    ],
    "estimated_hours": 4
  },
  "dependencies": {
    "requires": [],
    "blocking": ["01-02", "02-01"]
  },
  "state": {
    "status": "TODO",
    "assigned_to": null,
    "started_at": null,
    "completed_at": null,
    "updated": "2024-01-15T10:30:00Z"
  }
}
```

### Processing Logic:

1. **Context Enrichment**: For each step in roadmap:
   - Add complete background information
   - Include all technical context needed
   - List relevant files and resources
   - Document completed prerequisites

2. **Instruction Expansion**: Transform brief roadmap items into:
   - Detailed step-by-step instructions
   - Specific tool and command references
   - Clear output expectations
   - Concrete acceptance criteria

3. **Dependency Resolution**:
   - Map all inter-step dependencies
   - Identify which steps can run in parallel
   - Document blocking relationships

4. **Agent Assignment**:
   - Auto-select appropriate agent based on task type
   - Or use explicitly specified agent
   - Include agent-specific context

5. **File Generation**:
   - Create atomic JSON file per step
   - Ensure complete self-containment
   - No references requiring external context

## Success Criteria

**Validation Checklist:**
- [ ] Roadmap.yaml successfully parsed
- [ ] Project folder structure created: `docs/workflow/{project-id}/steps/`
- [ ] All JSON files are syntactically valid
- [ ] File names follow {phase:02d}-{step:02d}.json format
- [ ] All fields from roadmap preserved in JSON files
- [ ] Dependencies correctly mapped from roadmap
- [ ] ISO 8601 datetime format for timestamps
- [ ] Each file contains project_id reference
- [ ] No files committed without user approval

## Next Wave

**Handoff To**: Implementation teams working on individual steps
**Deliverables**:
- Individual JSON tracking files in `docs/workflow/{project-id}/steps/`
- Each file ready for state tracking and updates
- Consistent structure across all project steps

## Notes

### Context Degradation Prevention

This two-command system solves the critical problem of context degradation in long-running LLM conversations:

1. **DW-ROADMAP** → Expert agent creates comprehensive plan with full context
2. **DW-SPLIT** → Transforms plan into atomic, self-contained tasks

### Key Benefits of Atomic Task Architecture

**For Sub-Agents:**
- Start with clean context for each task
- No accumulated confusion from previous steps
- Consistent quality across all tasks
- Can execute in parallel without interference

**For Project Management:**
- Track progress at granular level
- Identify bottlenecks quickly
- Reassign tasks between agents easily
- Maintain audit trail of all changes

**For Quality:**
- Each task executed at peak LLM performance
- No context overflow errors
- Reduced hallucination risk
- Consistent output quality

### Implementation Flow

```
Goal → Expert Agent (ROADMAP) → Comprehensive Plan
                ↓
        Agent (SPLIT) → Atomic Tasks
                ↓
     Sub-Agents Execute Tasks (Clean Context Each Time)
```

This architecture enables complex projects to be completed with consistent quality, as each sub-agent operates at maximum effectiveness without the burden of accumulated context.