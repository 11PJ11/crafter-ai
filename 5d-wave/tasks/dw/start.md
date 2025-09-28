# DW-START: Initialize 5D-Wave Workflow

## Overview
Initialize 5D-Wave methodology workflow with project brief creation and stakeholder alignment.

## Mandatory Pre-Execution Steps
1. **Validate 5D-Wave Configuration**: Ensure expansion pack is properly loaded and configured
2. **Agent Availability Check**: Verify all required 5D-Wave agents are available
3. **Workspace Preparation**: Establish project workspace and documentation structure

## Execution Flow

### Phase 1: Project Context Establishment
**Primary Agent**: business-analyst (Riley)
**Command**: `*gather-requirements`

**Elicitation Process**:
```
📋 PROJECT INITIATION - 5D-WAVE METHODOLOGY

Please provide the following information to initialize your 5D-Wave project:

1. Project Name and Brief Description:
   [User input required]

2. Primary Business Objectives:
   [User input required]

3. Key Stakeholders:
   [User input required]

4. Target Users/Audience:
   [User input required]

5. Success Criteria:
   [User input required]

6. Timeline/Constraints:
   [User input required]

7. Technology Preferences (if any):
   [User input required]
```

### Phase 2: Architecture Diagram Manager Integration
**Secondary Agent**: architecture-diagram-manager (Archer)
**Command**: `*create-visual-design`

**Integration Points**:
- Establish visual architecture baseline
- Create stakeholder communication materials
- Prepare diagram templates for evolution tracking

### Phase 3: Project Brief Creation
**Template**: `project-brief-tmpl.yaml`
**Output**: `PROJECT_BRIEF.md`

**Content Structure**:
```yaml
project_context:
  name: "[Project Name]"
  description: "[Detailed Description]"
  business_objectives: "[Primary Objectives]"
  success_criteria: "[Measurable Success Criteria]"

stakeholder_analysis:
  primary_stakeholders: "[Key Decision Makers]"
  secondary_stakeholders: "[Influencers and Users]"
  communication_plan: "[Engagement Strategy]"

scope_definition:
  in_scope: "[Included Features/Capabilities]"
  out_of_scope: "[Explicitly Excluded Items]"
  assumptions: "[Key Assumptions]"
  constraints: "[Known Limitations]"

methodology_configuration:
  wave_sequence: ["DISCUSS", "DESIGN", "DISTILL", "DEVELOP", "DEMO"]
  agent_assignments:
    discuss: "business-analyst"
    design: "solution-architect + architecture-diagram-manager"
    distill: "acceptance-designer"
    develop: "test-first-developer + systematic-refactorer"
    demo: "feature-completion-coordinator"
  specialist_agents: ["mikado-refactoring-specialist-enhanced", "walking-skeleton-helper", "root-cause-analyzer"]
```

### Phase 4: Next Wave Preparation
**Handoff Preparation**:
- Create `DISCUSS_READINESS.md` with stakeholder engagement plan
- Prepare business-analyst for deep requirements gathering
- Schedule stakeholder workshops and collaboration sessions

## Quality Gates
- [ ] Project context clearly defined and documented
- [ ] Stakeholder analysis complete with engagement plan
- [ ] Success criteria measurable and time-bound
- [ ] Architecture diagram foundation established
- [ ] All 5D-Wave agents ready for workflow execution
- [ ] DISCUSS wave prepared with clear next steps

## Output Artifacts
1. `PROJECT_BRIEF.md` - Comprehensive project overview
2. `STAKEHOLDER_ANALYSIS.md` - Detailed stakeholder mapping
3. `5D_WAVE_PLAN.md` - Wave execution roadmap
4. `ARCHITECTURE_BASELINE.md` - Initial architecture foundation

## Success Criteria
- Project team aligned on objectives and approach
- Stakeholders identified and engaged
- 5D-Wave methodology properly initialized
- Clear path to DISCUSS wave execution
- Visual architecture foundation established

## Failure Recovery
If initialization fails:
1. **Incomplete Requirements**: Re-engage stakeholders for clarity
2. **Agent Unavailability**: Verify expansion pack installation
3. **Scope Confusion**: Facilitate scope definition workshop
4. **Timeline Issues**: Adjust methodology cadence and wave timing

## Handoff to DISCUSS Wave
**Next Command**: `*dw-discuss`
**Next Agent**: business-analyst (Riley)
**Handoff Content**:
- Complete project brief with business context
- Stakeholder analysis and engagement plan
- Initial requirements foundation
- Visual architecture preparation