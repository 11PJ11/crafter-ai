# /cai:discuss - Requirements Gathering (Wave 1)

```yaml
---
command: "/cai:discuss"
category: "Planning & Analysis"
purpose: "Requirements gathering and stakeholder collaboration"
wave-enabled: true
performance-profile: "standard"
---
```

## Overview

Comprehensive requirements gathering and stakeholder collaboration for ATDD Wave 1 (DISCUSS phase).

## Auto-Persona Activation
- **Business Analyst**: Requirements capture and documentation (mandatory)
- **User Experience Designer**: UI-heavy projects (conditional)
- **Technical Stakeholder**: Technical constraints and feasibility (conditional)
- **Security Expert**: Security-critical features (conditional)
- **Legal Compliance Advisor**: Regulated domains (conditional)

## MCP Server Integration
- **Primary**: Sequential (structured requirements analysis and stakeholder simulation)
- **Secondary**: Context7 (requirements patterns and best practices)
- **Tertiary**: Magic (UI requirements visualization)

## Tool Orchestration
- **Task**: Specialized requirements agents activation
- **Write**: Requirements documentation creation
- **Read**: Existing requirements and context analysis
- **Edit**: Requirements refinement and updates
- **TodoWrite**: Requirements gathering progress tracking

## Agent Flow
```yaml
business-analyst:
  - Captures business requirements and constraints
  - Creates user stories with acceptance criteria
  - Documents stakeholder needs and priorities
  - Facilitates requirements workshops

conditional_domain_experts:
  user-experience-designer:
    trigger: "UI-heavy projects, user interaction focus"
    responsibility: "User journey mapping, interaction design, accessibility requirements"

  security-expert:
    trigger: "Authentication, authorization, data protection, compliance"
    responsibility: "Security requirements, threat modeling, compliance validation"

  legal-compliance-advisor:
    trigger: "Regulated industries, data privacy, legal constraints"
    responsibility: "Legal requirements, regulatory compliance, policy constraints"

  technical-stakeholder:
    trigger: "Complex integrations, legacy systems, technical constraints"
    responsibility: "Technical feasibility, integration requirements, constraint documentation"
```

## Arguments

### Basic Usage
```bash
/cai:discuss [requirements]
```

### Advanced Usage
```bash
/cai:discuss [requirements] --interactive --stakeholders <list> --focus <domain>
```

### Requirements Specification
- Natural language requirements description
- Examples: "user authentication with OAuth2", "payment processing with multiple providers", "real-time collaboration features"

### Stakeholder Engagement
- `--interactive`: Enable numbered option selection and stakeholder simulation
- `--stakeholders <list>`: Specify key stakeholders (business, technical, security, legal)
- `--workshop`: Full requirements workshop mode
- `--elicitation`: Interactive elicitation with guided questions

### Domain Focus
- `--focus business`: Business requirements and value proposition
- `--focus technical`: Technical requirements and constraints
- `--focus security`: Security and compliance requirements
- `--focus ux`: User experience and interface requirements
- `--focus integration`: Integration and interoperability requirements

### Output Control
- `--detailed`: Comprehensive requirements documentation
- `--stories`: Generate user stories with acceptance criteria
- `--constraints`: Document business and technical constraints
- `--acceptance`: Create initial acceptance criteria

## Requirements Elicitation Framework

### Stakeholder Perspectives
```yaml
end_users:
  focus: "What do they need to accomplish?"
  questions:
    - "What is the primary task users are trying to accomplish?"
    - "What are the pain points in their current workflow?"
    - "What would success look like from their perspective?"
    - "What are the edge cases or unusual scenarios they encounter?"

business_stakeholders:
  focus: "What business value is expected?"
  questions:
    - "What business problem does this solve?"
    - "How will success be measured?"
    - "What are the business constraints (budget, timeline, resources)?"
    - "What are the competitive advantages this provides?"

technical_team:
  focus: "What are the technical constraints and opportunities?"
  questions:
    - "What are the existing system constraints?"
    - "What integration points need to be considered?"
    - "What are the performance and scalability requirements?"
    - "What security and compliance requirements exist?"
```

### Interactive Elicitation Process
1. **Stakeholder Perspective Selection**: Choose which viewpoint to explore
2. **Requirements Deep Dive**: Systematic exploration of needs and constraints
3. **Story Creation**: Transform requirements into user stories
4. **Validation Workshop**: Review and validate requirements with stakeholders
5. **Acceptance Criteria**: Define specific, measurable success criteria

## Requirements Documentation Structure

### User Stories Format
```yaml
user_story_template:
  format: "As a [user type] I want [goal] so that [benefit]"
  components:
    - user_type: Specific user persona or role
    - goal: Specific functionality or capability
    - benefit: Business value or user benefit
    - acceptance_criteria: Specific, measurable, testable criteria
```

### Business Requirements
- **Business Value**: Clear articulation of business benefit
- **Success Metrics**: Measurable outcomes and KPIs
- **Business Constraints**: Budget, timeline, regulatory requirements
- **Stakeholder Priorities**: Relative importance and urgency

### Technical Requirements
- **Functional Requirements**: Specific system behaviors and capabilities
- **Non-Functional Requirements**: Performance, security, scalability, usability
- **Integration Requirements**: External system interactions and data flows
- **Technical Constraints**: Technology stack, infrastructure, legacy system limitations

## Quality Gates

### Requirements Completeness
- **User Stories**: All major user journeys captured as stories
- **Acceptance Criteria**: Specific, measurable, testable criteria for each story
- **Business Value**: Clear articulation of value for each requirement
- **Stakeholder Validation**: Key stakeholders have reviewed and approved requirements

### Requirements Quality
- **INVEST Criteria**: Independent, Negotiable, Valuable, Estimable, Small, Testable
- **Clarity**: Requirements are unambiguous and understandable
- **Traceability**: Requirements linked to business objectives and user needs
- **Consistency**: No conflicting or contradictory requirements

### Documentation Standards
- **Format Consistency**: Standardized user story and requirements format
- **Completeness**: All required sections documented
- **Accessibility**: Documentation accessible to all stakeholders
- **Version Control**: Requirements changes tracked and documented

## Output Artifacts

### Requirements Documents
- `${DOCS_PATH}/requirements.md`: Comprehensive business requirements
- `${DOCS_PATH}/user-stories.md`: User stories with acceptance criteria
- `${DOCS_PATH}/stakeholder-analysis.md`: Stakeholder needs and constraints
- `${DOCS_PATH}/business-constraints.md`: Business limitations and requirements

### Workshop Outputs
- **Requirements Backlog**: Prioritized list of requirements
- **User Journey Maps**: Visual representation of user workflows
- **Acceptance Criteria**: Detailed validation criteria for each story
- **Risk Assessment**: Identified risks and mitigation strategies

## Examples

### Basic Requirements Gathering
```bash
/cai:discuss "user authentication system with social login" --interactive
```

### Comprehensive Requirements Workshop
```bash
/cai:discuss "multi-tenant SaaS platform" --workshop --stakeholders business,technical,security
```

### Domain-Focused Requirements
```bash
/cai:discuss "payment processing integration" --focus security --detailed
```

### UI-Heavy Feature Requirements
```bash
/cai:discuss "responsive dashboard with real-time updates" --focus ux --stories
```

### Complex Integration Requirements
```bash
/cai:discuss "legacy system modernization" --focus technical --constraints --elicitation
```

ARGUMENTS: create the commands under the @.claude\commands\cai\ folder so we can install them together with the rest