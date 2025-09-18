# /cai:complete - Feature Completion (Wave 5)

```yaml
---
command: "/cai:complete"
category: "Deployment & Completion"
purpose: "Feature finalization and production readiness validation"
argument-hint: "[feature] --deploy-ready --comprehensive --stakeholder-demo"
wave-enabled: true
performance-profile: "comprehensive"
---
```

## Overview

Comprehensive feature completion and production readiness validation for ATDD Wave 5 (DEMO phase), ensuring features are fully implemented, tested, and ready for production deployment.

## Auto-Persona Activation
- **Feature Completion Coordinator**: Completion orchestration and validation (mandatory)
- **Production Readiness Helper**: Production deployment preparation (mandatory)
- **QA**: Final quality validation and testing (conditional)
- **DevOps**: Production deployment and monitoring setup (conditional)
- **Architect**: Final architectural validation and documentation updates (conditional)

## MCP Server Integration
- **Primary**: Sequential (systematic completion validation and production readiness assessment)
- **Secondary**: Playwright (final E2E validation and production testing)
- **Tertiary**: Context7 (production best practices and deployment patterns)

## Tool Orchestration
- **Task**: Specialized completion agents activation
- **Bash**: Final testing, building, and deployment validation
- **Read**: Feature completeness assessment and documentation validation
- **Write**: Production documentation and deployment guides
- **Edit**: Final documentation updates and architecture alignment

## Agent Flow
```yaml
feature-completion-coordinator:
  completion_validation:
    - Validates feature completeness against acceptance criteria
    - Detects feature completion automatically
    - Triggers comprehensive Level 4-6 refactoring
    - Manages feature completion cleanup and documentation

  quality_orchestration:
    - Coordinates final quality validation across all domains
    - Ensures all acceptance tests are passing
    - Validates business requirements satisfaction
    - Manages stakeholder approval and sign-off process

production-readiness-helper:
  deployment_preparation:
    - Identifies and resolves production deployment blockers
    - Validates production environment compatibility
    - Ensures infrastructure readiness and capacity
    - Implements 2024 production readiness best practices

  go_live_validation:
    - Creates comprehensive go-live checklist
    - Validates monitoring and alerting setup
    - Ensures rollback and recovery procedures
    - Conducts final production environment testing
```

## Command Execution Pattern

### Activation Instructions
When this command is invoked:
1. Parse feature context and completion requirements
2. Invoke feature-completion-coordinator agent for end-to-end coordination
3. Chain to production-readiness-helper agent for deployment validation
4. Execute comprehensive feature finalization
5. Return production-ready feature with deployment checklist

### Agent Invocation Workflow
```yaml
execution-flow:
  step1-coordination:
    agent: feature-completion-coordinator
    task: |
      Coordinate complete feature finalization:
      - Feature: {parsed_feature_name}
      - Deploy Ready: {deploy_ready_flag_status}
      - Production Mode: {production_flag_status}

      Execute feature completion including:
      - Validate feature completeness against acceptance criteria
      - Trigger comprehensive Level 4-6 refactoring
      - Update documentation and architecture diagrams
      - Coordinate end-to-end feature validation

  step2-production-readiness:
    agent: production-readiness-helper
    task: |
      Ensure production deployment readiness:
      - Review feature completion from coordinator
      - Identify and resolve deployment blockers
      - Validate production environment compatibility
      - Prepare comprehensive go-live checklist

  step3-quality-gates:
    agent: quality-gates
    task: |
      Enforce final commit requirements:
      - Execute comprehensive quality validation
      - Validate all tests passing and quality gates
      - Ensure production service integration
      - Confirm deployment readiness criteria
```

### Arguments Processing
- Parse `[feature-name]` argument for completion scope
- Apply `--deploy-ready`, `--production` flags to readiness validation
- Process `--comprehensive`, `--quality-gates` flags for validation depth
- Enable production deployment preparation

### Output Generation
Return production-ready feature including:
- Validated feature completeness with acceptance criteria met
- Comprehensive Level 4-6 refactoring applied
- Production deployment checklist and readiness validation
- Updated documentation and architecture diagrams

## 📖 Complete Documentation

For comprehensive usage examples, completion frameworks, production readiness validation, and detailed configuration options:

```bash
/cai:man complete                    # Full manual with all examples
/cai:man complete --examples         # Usage examples only
/cai:man complete --flags           # All flags and options
```

The manual includes:
- **Completion Scope**: `--deploy-ready`, `--comprehensive`, `--stakeholder-demo`, `--production-validation`
- **Quality Control**: `--final-validation`, `--performance-validation`, `--security-validation`, `--user-acceptance`
- **Documentation Control**: `--update-architecture`, `--user-documentation`, `--api-documentation`, `--deployment-guide`
- **Comprehensive Examples**: Production-ready completion, epic completion, quality-focused workflows
- **Completion Framework**: Detection criteria, refactoring integration, production readiness validation
- **Integration Patterns**: ATDD completion workflows, quality gates, stakeholder coordination