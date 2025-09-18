# /cai:discuss - Requirements Gathering (Wave 1)

```yaml
---
command: "/cai:discuss"
category: "Planning & Analysis"
purpose: "Requirements gathering and stakeholder collaboration"
argument-hint: "[requirements] --interactive --stakeholders business,technical"
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

## 📖 Complete Documentation

For comprehensive usage examples, stakeholder engagement patterns, elicitation frameworks, and detailed configuration options:

```bash
/cai:man discuss                     # Full manual with all examples
/cai:man discuss --examples          # Usage examples only
/cai:man discuss --flags            # All flags and options
```

The manual includes:
- **Stakeholder Engagement**: `--interactive`, `--workshop`, `--elicitation`, `--stakeholders <list>`
- **Domain Focus**: `--focus business|technical|security|ux|integration`
- **Output Control**: `--detailed`, `--stories`, `--constraints`, `--acceptance`
- **Comprehensive Examples**: Interactive elicitation, domain-specific gathering, workshop sessions
- **Requirements Framework**: Stakeholder perspectives, documentation structure, quality gates
- **Integration Patterns**: Requirements-driven ATDD workflows, business analysis to architecture