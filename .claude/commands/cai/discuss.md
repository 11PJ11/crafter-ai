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
  - Provides guided requirements elicitation with multiple choice questions
  - Shows different stakeholder perspectives with role-based questioning
  - Allows iterative refinement of requirements with user input and validation
  - Enables collaborative requirements validation through stakeholder simulation
- `--stakeholders <list>`: Specify key stakeholders (business, technical, security, legal)
  - Focuses requirements gathering on specific stakeholder groups
  - Activates appropriate domain experts based on stakeholder types
  - Ensures comprehensive coverage of stakeholder concerns and priorities
  - Examples: "business,technical" or "security,legal,ux" for targeted sessions
- `--workshop`: Full requirements workshop mode
  - Conducts comprehensive requirements gathering session with all stakeholders
  - Facilitates collaborative requirements definition and priority setting
  - Includes requirements validation, conflict resolution, and consensus building
  - Generates detailed workshop outputs including acceptance criteria and risks
- `--elicitation`: Interactive elicitation with guided questions
  - Uses systematic questioning techniques to extract requirements
  - Applies requirements elicitation best practices and structured approaches
  - Guides users through comprehensive requirements discovery process
  - Ensures no critical requirements areas are missed through guided exploration

### Domain Focus
- `--focus business`: Business requirements and value proposition
  - Prioritizes business value, ROI analysis, and competitive advantage
  - Emphasizes success metrics, business constraints, and stakeholder priorities
  - Includes business process analysis, workflow requirements, and value streams
  - Generates business-focused user stories and acceptance criteria
- `--focus technical`: Technical requirements and constraints
  - Prioritizes technical feasibility, integration requirements, and system constraints
  - Emphasizes performance, scalability, maintainability, and technical architecture
  - Includes technology stack evaluation, infrastructure requirements, and system integration
  - Addresses technical debt, legacy system constraints, and migration requirements
- `--focus security`: Security and compliance requirements
  - Prioritizes security controls, threat modeling, and compliance validation
  - Emphasizes authentication, authorization, data protection, and audit requirements
  - Includes regulatory compliance, privacy requirements, and security architecture
  - Addresses vulnerability assessment, penetration testing, and security monitoring
- `--focus ux`: User experience and interface requirements
  - Prioritizes user journeys, personas, and interaction design requirements
  - Emphasizes usability, accessibility, and user satisfaction metrics
  - Includes responsive design, mobile experience, and cross-platform compatibility
  - Addresses user feedback, usability testing, and design system requirements
- `--focus integration`: Integration and interoperability requirements
  - Prioritizes API design, data exchange, and system interconnection requirements
  - Emphasizes data consistency, transaction management, and workflow coordination
  - Includes third-party integrations, legacy system connections, and data migration
  - Addresses messaging patterns, service orchestration, and integration testing

### Output Control
- `--detailed`: Comprehensive requirements documentation
  - Generates extensive documentation including all requirements aspects
  - Includes detailed user stories, comprehensive acceptance criteria, and technical specifications
  - Provides thorough business context, stakeholder analysis, and constraint documentation
  - Creates complete requirements traceability from business needs to acceptance criteria
- `--stories`: Generate user stories with acceptance criteria
  - Focuses output on user story format with Given-When-Then acceptance criteria
  - Applies INVEST criteria (Independent, Negotiable, Valuable, Estimable, Small, Testable)
  - Creates story-driven requirements that directly support ATDD development workflow
  - Includes story prioritization, estimation guidance, and implementation sequencing
- `--constraints`: Document business and technical constraints
  - Emphasizes identification and documentation of system and business limitations
  - Includes budget constraints, timeline restrictions, and resource limitations
  - Documents technical constraints, legacy system limitations, and integration restrictions
  - Provides constraint impact analysis and mitigation strategies
- `--acceptance`: Create initial acceptance criteria
  - Focuses on creating specific, measurable, testable acceptance criteria
  - Applies behavior-driven development (BDD) Given-When-Then format
  - Ensures acceptance criteria align with business value and user needs
  - Creates criteria that directly support automated acceptance testing

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

## Comprehensive Usage Examples

### Interactive Requirements Elicitation
```bash
# Basic interactive requirements gathering with stakeholder simulation
/cai:discuss "e-commerce checkout process" --interactive --stories

# Guided elicitation with comprehensive questioning
/cai:discuss "customer relationship management system" --elicitation --detailed --constraints

# Multi-stakeholder interactive workshop
/cai:discuss "enterprise data platform" --interactive --workshop --stakeholders business,technical,security,legal

# User experience focused interactive session
/cai:discuss "mobile banking application" --interactive --focus ux --stories --acceptance
```

### Domain-Specific Requirements Gathering
```bash
# Business-focused requirements with value proposition
/cai:discuss "digital transformation initiative" --focus business --detailed --stories --workshop

# Technical requirements for system integration
/cai:discuss "microservices migration" --focus technical --constraints --detailed --stakeholders technical

# Security-critical system requirements
/cai:discuss "healthcare patient portal" --focus security --detailed --constraints --workshop --stakeholders security,legal

# UX-centered requirements for customer-facing systems
/cai:discuss "customer support portal redesign" --focus ux --stories --acceptance --interactive --stakeholders business,ux

# Integration-heavy requirements gathering
/cai:discuss "third-party API integration platform" --focus integration --constraints --detailed --stakeholders technical,business
```

### Comprehensive Workshop Sessions
```bash
# Full requirements workshop with all stakeholder types
/cai:discuss "enterprise resource planning system" --workshop --stakeholders business,technical,security,legal,ux --detailed

# Requirements workshop with constraint focus
/cai:discuss "regulatory compliance platform" --workshop --constraints --focus security --stakeholders security,legal,business

# Story-driven workshop for ATDD development
/cai:discuss "agile project management tool" --workshop --stories --acceptance --interactive --stakeholders business,technical,ux

# Technical feasibility workshop
/cai:discuss "real-time analytics dashboard" --workshop --focus technical --constraints --stakeholders technical,business,ux
```

### Output-Focused Requirements Sessions
```bash
# Comprehensive documentation generation
/cai:discuss "customer data platform" --detailed --constraints --stories --acceptance --workshop

# User story focused requirements
/cai:discuss "task management application" --stories --acceptance --interactive --focus business

# Constraint documentation emphasis
/cai:discuss "legacy system modernization" --constraints --detailed --focus technical --stakeholders technical,business

# Acceptance criteria development
/cai:discuss "automated testing framework" --acceptance --stories --focus technical --interactive
```

### Regulated Industry Requirements
```bash
# Financial services compliance requirements
/cai:discuss "banking transaction processing" --focus security --constraints --detailed --stakeholders security,legal,business --workshop

# Healthcare compliance and security
/cai:discuss "electronic health records system" --focus security --constraints --stakeholders security,legal,ux --workshop --detailed

# Government and public sector requirements
/cai:discuss "citizen services portal" --constraints --focus security --stakeholders security,legal,business,ux --workshop --detailed

# Data privacy and GDPR compliance
/cai:discuss "customer data management platform" --focus security --constraints --stakeholders security,legal --detailed --workshop
```

### Agile and ATDD-Ready Requirements
```bash
# ATDD-optimized requirements gathering
/cai:discuss "user registration workflow" --stories --acceptance --interactive --focus business --stakeholders business,ux

# Sprint planning requirements
/cai:discuss "search and filtering feature" --stories --acceptance --focus ux --detailed --stakeholders business,ux,technical

# Epic-level requirements breakdown
/cai:discuss "complete user onboarding experience" --workshop --stories --detailed --stakeholders business,ux,technical --acceptance

# Feature-driven development requirements
/cai:discuss "notification system" --stories --focus technical --acceptance --stakeholders technical,business --interactive
```

### Complex System Requirements
```bash
# Enterprise architecture requirements
/cai:discuss "enterprise service bus implementation" --focus technical --focus integration --detailed --constraints --workshop --stakeholders technical,business,security

# Multi-tenant SaaS requirements
/cai:discuss "cloud-native multi-tenant platform" --workshop --detailed --constraints --stakeholders business,technical,security --focus scalability

# Real-time system requirements
/cai:discuss "live chat and collaboration platform" --focus technical --focus ux --stories --acceptance --stakeholders technical,business,ux --interactive

# Data-intensive application requirements
/cai:discuss "business intelligence and analytics platform" --focus business --focus technical --detailed --workshop --stakeholders business,technical,ux
```

### Integration Workflow Examples
```bash
# Requirements-driven ATDD workflow
/cai:start "customer portal development" --methodology atdd --interactive
/cai:discuss "customer portal requirements" --workshop --stories --acceptance --stakeholders business,ux,technical

# Business analysis to architecture workflow
/cai:discuss "e-commerce platform requirements" --detailed --constraints --workshop --stakeholders business,technical,security
/cai:architect "e-commerce platform architecture" --style microservices --focus scalability --workshop --validation

# Requirements to development workflow
/cai:discuss "user authentication requirements" --stories --acceptance --focus security --stakeholders security,business
/cai:develop "authentication implementation" --outside-in --real-system --validate --one-scenario

# Stakeholder collaboration to technical implementation
/cai:discuss "payment processing requirements" --workshop --interactive --focus security --stakeholders business,security,technical
/cai:architect "secure payment architecture" --focus security --focus reliability --validation --workshop
/cai:develop "payment system implementation" --validate --real-system --tdd-mode strict
```

### Requirements Validation and Refinement
```bash
# Requirements validation workshop
/cai:discuss "existing requirements review" --workshop --validation --stakeholders business,technical,ux --detailed

# Requirements refinement session
/cai:discuss "feature requirements refinement" --elicitation --interactive --stories --acceptance --stakeholders business,ux

# Cross-functional requirements alignment
/cai:discuss "system integration requirements" --workshop --focus integration --stakeholders technical,business,security --constraints --detailed

# Business value validation session
/cai:discuss "feature prioritization workshop" --focus business --workshop --stories --stakeholders business,ux,technical --interactive
```

## Command Execution Pattern

### Activation Instructions
When this command is invoked:
1. Parse requirements and stakeholder context
2. Invoke business-analyst agent for requirements gathering
3. Chain to conditional domain experts based on focus area
4. Facilitate stakeholder collaboration and requirement validation
5. Return structured requirements document with acceptance criteria

### Agent Invocation Workflow
```yaml
execution-flow:
  step1-requirements:
    agent: business-analyst
    task: |
      Capture and structure business requirements:
      - Requirements Context: {parsed_requirements}
      - Focus Area: {focus_domain_if_specified}
      - Interactive Mode: {interactive_flag_status}

      Execute requirements gathering including:
      - Business requirements capture and documentation
      - User stories creation with acceptance criteria
      - Business constraints and assumptions documentation
      - Stakeholder collaboration facilitation

  step2-domain-experts:
    conditional-agents:
      user-experience-designer:
        condition: focus == "ux" || ui_heavy_project
        task: |
          Define user experience requirements:
          - Review business requirements from business-analyst
          - Create user journeys and personas
          - Define UX-focused acceptance criteria
          - Document accessibility and usability requirements

      security-expert:
        condition: focus == "security" || security_critical
        task: |
          Define security requirements:
          - Review requirements for security implications
          - Define security acceptance criteria and compliance needs
          - Document threat model and security constraints
          - Establish security validation requirements

      legal-compliance-advisor:
        condition: regulatory_implications_detected
        task: |
          Ensure legal and regulatory compliance:
          - Review requirements for legal implications
          - Document regulatory compliance requirements
          - Establish legal constraints and validation criteria
          - Define compliance testing requirements

  step3-validation:
    agent: business-analyst
    task: |
      Validate and finalize requirements:
      - Synthesize inputs from domain experts
      - Validate requirements completeness and consistency
      - Resolve conflicts and ambiguities
      - Create final structured requirements document
```

### Arguments Processing
- Parse `[requirements]` argument for requirement context
- Apply `--focus`, `--constraints`, `--stories` flags to expert selection
- Process `--interactive`, `--elicitation` flags for stakeholder engagement
- Enable domain expert activation based on focus areas

### Output Generation
Return structured requirements document including:
- Comprehensive business requirements documentation
- User stories with detailed acceptance criteria
- Domain-specific requirements (UX, security, legal as applicable)
- Stakeholder collaboration artifacts and validation results