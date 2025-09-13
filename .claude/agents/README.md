# AI-Craft Agent Organization

This directory contains all AI-Craft pipeline agents organized by their primary responsibility category. Each agent follows the Single Responsibility Principle and has a clear, focused purpose.

## 🔧 **Configuration**

### **`constants.md`** - Shared Constants and Configuration
- **Purpose**: Centralized configuration for all agents including paths, file names, and common constants
- **Usage**: All agents reference `@constants.md` to use shared constants like `${DOCS_PATH}` instead of hardcoded paths
- **Benefit**: Easy maintenance - change paths once in constants.md and all agents automatically use new values

## 📁 Agent Categories

### 🔍 **requirements-analysis/**
Agents responsible for gathering, analyzing, and validating business and technical requirements with specialist expertise.

- **`business-analyst.md`** - Collaborates with users to gather business requirements and acceptance criteria
- **`technical-stakeholder.md`** - Validates technical feasibility and provides technical constraint analysis
- **`user-experience-designer.md`** - ⭐ **NEW** - User journey mapping and UX-focused acceptance criteria (conditionally activated)
- **`security-expert.md`** - ⭐ **NEW** - Security threat modeling and compliance requirements (conditionally activated)
- **`legal-compliance-advisor.md`** - ⭐ **NEW** - Legal and regulatory compliance analysis (conditionally activated)

### 🏗️ **architecture-design/**
Agents responsible for system architecture design, technology selection, and architectural documentation.

- **`solution-architect.md`** - Collaborative architectural design with user input and ADR creation
- **`technology-selector.md`** - Technology stack evaluation and selection with trade-off analysis
- **`architecture-diagram-manager.md`** - Visual architecture documentation and diagram management

### 🧪 **test-design/**
Agents responsible for acceptance test design and scenario creation.

- **`acceptance-designer.md`** - Creates acceptance test scenarios aligned with requirements and architecture

### 💻 **development/**
Agents responsible for implementation and development activities.

- **`test-first-developer.md`** - Outside-in TDD implementation with production service integration

### ✅ **quality-validation/**
Agents responsible for various aspects of quality validation and compliance checking.

- **`test-execution-validator.md`** - Test suite validation and ATDD compliance
- **`code-quality-validator.md`** - Static analysis, formatting, and complexity metrics
- **`architecture-compliance-validator.md`** - Component boundaries and architectural patterns
- **`security-performance-validator.md`** - Security standards and performance benchmarks
- **`production-service-integrator.md`** - Production service integration validation
- **`hexagonal-architecture-enforcer.md`** - Hexagonal architecture boundary validation
- **`commit-readiness-coordinator.md`** - Overall commit orchestration and final validation

### 🔄 **refactoring/**
Agents responsible for systematic code improvement and refactoring activities.

- **`mutation-testing-coordinator.md`** - Mutation testing validation and test enhancement
- **`systematic-refactorer.md`** - Level 1-6 progressive refactoring execution
- **`mikado-refactoring-specialist.md`** - Complex architectural refactoring using Mikado Method

### 🎯 **coordination/**
Agents responsible for workflow coordination, state management, and pipeline orchestration.

- **`atdd-cycle-coordinator.md`** - Five-stage ATDD workflow orchestration (Discuss→Architect→Distill→Develop→Demo)
- **`feature-completion-coordinator.md`** - End-to-end feature completion workflow management
- **`feature-completion-manager.md`** - Feature completion detection and cleanup
- **`pipeline-state-manager.md`** - Pipeline state persistence and resumption logic
- **`ci-cd-integration-manager.md`** - CI/CD pipeline monitoring and failure recovery
- **`technical-debt-tracker.md`** - Technical debt registry and management
- **`root-cause-analyzer.md`** - Toyota 5 Whys systematic root cause analysis
- **`walking-skeleton-helper.md`** - ⭐ **NEW** - Minimal end-to-end implementation guide (Alistair Cockburn methodology)
- **`production-readiness-helper.md`** - ⭐ **NEW** - Rapid go-live acceleration with quality safeguards

### 🗂️ **legacy-agents/**
Deprecated agents that violated Single Responsibility Principle. These have been split into focused agents above.

- **`comprehensive-refactoring-specialist.md`** - ❌ DEPRECATED - Split into 5 refactoring agents
- **`quality-gates.md`** - ❌ DEPRECATED - Split into 5 quality validation agents
- **`atdd-orchestrator.md`** - ❌ DEPRECATED - Split into 3 coordination agents
- **`production-validator.md`** - ❌ DEPRECATED - Split into 2 validation agents

## 🔄 ATDD Pipeline Flow

The agents work together in the five-stage ATDD cycle:

```
DISCUSS → ARCHITECT → DISTILL → DEVELOP → DEMO
   ↓         ↓         ↓         ↓        ↓
business   solution  acceptance test-first feature
analyst    architect  designer  developer completion
   +         +         +         +        +
technical  technology    ∅      production refactoring
stakeholder selector             validator  agents
```

### Agent Flow by Phase:

1. **DISCUSS**: `business-analyst` + `technical-stakeholder`
2. **ARCHITECT**: `solution-architect` + `technology-selector` + `architecture-diagram-manager`  
3. **DISTILL**: `acceptance-designer`
4. **DEVELOP**: `test-first-developer` + quality validation agents
5. **DEMO**: refactoring agents + `feature-completion-manager`

### Quality Gates Integration:
- **Continuous**: All quality-validation agents run throughout development
- **Coordination**: `atdd-cycle-coordinator` orchestrates the full workflow
- **State Management**: `pipeline-state-manager` handles interruption/resumption

## 🎯 Single Responsibility Principle

Each agent now has a single, clear responsibility:

- **Analysis agents** → Gather and analyze requirements
- **Design agents** → Create architectural designs and select technologies  
- **Test agents** → Design acceptance scenarios
- **Development agents** → Implement features using TDD
- **Validation agents** → Validate different aspects of quality
- **Refactoring agents** → Improve code systematically
- **Coordination agents** → Orchestrate workflows and manage state

This organization makes the agent system more:
- **Maintainable** - Each agent is focused and easy to understand
- **Testable** - Clear boundaries and responsibilities  
- **Scalable** - New agents can be added to specific categories
- **Modular** - Agents can be used independently or in combination
- **Reliable** - Single responsibility reduces complexity and bugs

## 📈 Agent Evolution

The transformation from multi-responsibility to single-responsibility agents:

- **Before**: 4 complex agents with multiple responsibilities
- **After**: 23 focused agents with clear, single responsibilities (18 core + 3 specialist + 2 helper)
- **Specialists**: 3 conditionally-activated specialist agents for enhanced domain expertise
- **Helpers**: 2 project acceleration helpers for new and existing projects
- **Result**: Better separation of concerns, improved maintainability, enhanced modularity, specialized expertise integration, project acceleration support

## 🎯 Specialist Agent Activation

### Conditional Activation Criteria
**User Experience Designer**: Activated for projects with user-facing interfaces, UX-critical functionality, or accessibility requirements
**Security Expert**: Activated for projects handling sensitive data, requiring security compliance, or operating in security-critical environments  
**Legal Compliance Advisor**: Activated for projects in regulated industries, handling personal data, or with specific legal/regulatory requirements

### Specialist Integration Benefits
- **Enhanced Requirements**: Specialists add domain expertise to core requirements analysis
- **Improved Acceptance Criteria**: Tests include UX, security, and legal validation scenarios  
- **Collaborative Validation**: Multiple specialist perspectives ensure comprehensive coverage
- **Maintained SRP**: Each specialist has focused responsibility while collaborating seamlessly

## 🚀 Helper Agent Activation

### Project Acceleration Helpers
**Walking Skeleton Helper**: Activated for new projects or existing projects adopting AI-Craft workflow - creates minimal end-to-end implementations using Alistair Cockburn's methodology to validate architecture and reduce risk
**Production Readiness Helper**: Activated when rapid production deployment is needed - identifies and resolves deployment blockers while gathering feedback data and balancing speed with quality

### Helper Integration Benefits
- **Risk Reduction**: Early validation of architectural decisions and production readiness
- **Speed Optimization**: Accelerate time-to-market while maintaining quality safeguards
- **Learning Acceleration**: Enable rapid feedback loops and data-driven iteration
- **Legacy Integration**: Support existing projects transitioning to AI-Craft workflow

This structure supports the AI-Craft vision of systematic, high-quality software development through focused, specialized AI agents working together in a coordinated pipeline.