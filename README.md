# AI-Craft: Intelligent ATDD Pipeline with Specialized Agent Network

🚀 **A systematic approach to software development using ATDD (Acceptance Test Driven Development) with intelligent AI agent orchestration**

## 🎯 Overview

AI-Craft is a comprehensive development pipeline that implements the 5-stage ATDD workflow through specialized AI agents, each following the Single Responsibility Principle. The system provides intelligent project analysis, automated workflow initiation, and systematic quality assurance.

### Core Philosophy
- **Outside-In Development**: Start with acceptance tests and work inward
- **Single Responsibility Principle**: Each agent has one focused responsibility
- **Clean Context Isolation**: Agents receive only essential context for their tasks
- **File-Based Handoffs**: Structured communication between pipeline stages
- **Systematic Quality**: Progressive refactoring and comprehensive validation

## 🏗️ Architecture

### ATDD Five-Stage Workflow
```
DISCUSS → ARCHITECT → DISTILL → DEVELOP → DEMO
   ↓         ↓         ↓         ↓        ↓
business   solution  acceptance test-first feature
analyst    architect  designer  developer completion
   +         +         +         +        +
technical  technology    ∅      production refactoring
stakeholder selector             validator  agents
```

### Agent Organization (33+ Specialized Agents)

#### 🟦 **Requirements Analysis** (5 agents)
- **Business Analyst** 🔵💼 - Business requirements and acceptance criteria
- **Technical Stakeholder** 🔷⚡ - Technical feasibility validation
- **User Experience Designer** 🟦🎨 - User journey mapping (conditional)
- **Security Expert** 🔹🛡️ - Security threat modeling (conditional)
- **Legal Compliance Advisor** 💙⚖️ - Regulatory compliance (conditional)

#### 🟧 **Architecture Design** (3 agents)
- **Solution Architect** 🟠🏗️ - Collaborative architectural design
- **Technology Selector** 🟧🔧 - Technology stack evaluation
- **Architecture Diagram Manager** 🔶📐 - Visual architecture documentation

#### ❤️ **Test Design** (1 agent)
- **Acceptance Designer** ❤️🧪 - Comprehensive acceptance test scenarios

#### 🟢 **Development** (1 agent)
- **Test-First Developer** 🌿💻 - Outside-in TDD implementation

#### ❤️ **Quality Validation** (8 agents)
- **Test Execution Validator** ❤️✅ - Test suite validation
- **Mutation Testing Coordinator** 🧬🧬 - Test effectiveness enhancement
- **Code Quality Validator** 💖🔍 - Static analysis and complexity metrics
- **Architecture Compliance Validator** 💕🏛️ - Architectural adherence
- **Security Performance Validator** 💗🚀 - Security and performance benchmarks
- **Production Service Integrator** 💓🔗 - Production integration validation
- **Hexagonal Architecture Enforcer** 💘⬢ - Boundary validation
- **Commit Readiness Coordinator** 💝🎯 - Final validation orchestration

#### 🔵 **Refactoring** (2 agents)
- **Systematic Refactorer** 💙🔄 - Level 1-6 progressive refactoring
- **Mikado Refactoring Specialist** 🟦🌳 - Complex architectural refactoring

#### ⚫ **Coordination** (11 agents)
- **ATDD Cycle Coordinator** ⚫🎭 - Five-stage workflow orchestration
- **ATDD Wave Coordinator** ⚪🌊 - Fixed workflow with clean context isolation
- **ATDD Command Processor** 🔷💻 - Intelligent project analysis and workflow initiation
- **Walking Skeleton Helper** 🟤🚶 - Minimal end-to-end implementation guide
- **Production Readiness Helper** 🤎🚀 - Rapid go-live acceleration
- **Feature Completion Coordinator** 🔘🏁 - End-to-end feature completion
- **Pipeline State Manager** 🔵💾 - State persistence and resumption
- **CI/CD Integration Manager** 🔴⚙️ - Pipeline monitoring and recovery
- **Technical Debt Tracker** 🟫📊 - Debt registry and management
- **Root Cause Analyzer** 🔲🔍 - Toyota 5 Whys systematic analysis
- **Feature Completion Manager** ⚪✔️ - Completion detection and cleanup

### 🚀 **Helper Agents** (2 agents)
- **Walking Skeleton Helper** 🟤🚶 - Alistair Cockburn methodology for new projects
- **Production Readiness Helper** 🤎🚀 - Quality-assured rapid deployment

## 🎮 Command Interface

### Primary Command: `cai/atdd`
Intelligent ATDD workflow initiation with automatic project analysis:

```bash
# Basic usage - analyze project and start appropriate workflow stage
cai/atdd "implement user authentication system"

# With explicit project analysis
cai/atdd "add payment processing" --analyze-existing

# Start from specific stage
cai/atdd "OAuth2 integration" --from-stage=architect

# Resume existing workflow
cai/atdd --resume auth-feature-2024-01

# Check workflow status
cai/atdd --status
```

### Command Features
- **Intelligent Project Analysis**: Scans existing documentation, tests, and source code
- **Optimal Entry Point Detection**: Determines best starting stage based on project state
- **Context Preparation**: Compiles relevant context for workflow agents
- **Workflow Resumption**: Continue interrupted workflows
- **Progress Tracking**: Real-time workflow status and validation

## 🌊 Wave Processing Architecture

### Wave Coordination Principles
1. **Fixed Sequence**: DISCUSS → ARCHITECT → DISTILL → DEVELOP → DEMO (no variations)
2. **Clean Context Isolation**: Each agent starts fresh with only role-specific context
3. **File-Based Handoffs**: Agents communicate through structured output files
4. **Specialized Agent Delegation**: Task tool invokes specific agents with minimal context
5. **Coordinator Oversight**: Monitor progress, validate handoffs, ensure quality gates

### Wave Benefits
- **Context Cleanliness**: No context contamination between stages
- **Focused Expertise**: Each agent works within their domain
- **Quality Gates**: Validation at each stage boundary
- **Resumable Workflows**: Can restart from any completed wave
- **Systematic Progress**: Methodical advancement through development stages

## 📁 Project Structure

```
ai-craft/
├── .claude/
│   ├── agents/                    # Agent specifications (33+ agents)
│   │   ├── constants.md          # Centralized configuration
│   │   ├── requirements-analysis/ # Business and technical analysis
│   │   ├── architecture-design/  # System design agents
│   │   ├── test-design/          # Acceptance test creation
│   │   ├── development/          # Implementation agents
│   │   ├── quality-validation/   # Quality assurance agents
│   │   ├── refactoring/          # Code improvement agents
│   │   ├── coordination/         # Workflow orchestration
│   │   └── legacy-agents/        # Deprecated multi-responsibility agents
│   └── commands/
│       └── cai/
│           ├── atdd.md          # Command integration specification
│           └── root-why.md      # Root cause analysis command
└── docs/
    └── craft-ai/                 # Pipeline working files
        ├── PROGRESS.md           # Project progress tracking
        ├── requirements.md       # Business requirements
        ├── architecture.md       # Architectural design
        ├── acceptance-tests.md   # Test scenarios
        ├── implementation-status.md # Development progress
        └── quality-report.md     # Quality validation results
```

## 🔧 Configuration System

### Centralized Constants (`constants.md`)
All agents reference shared constants for maintainability:
- `${DOCS_PATH}`: "docs/craft-ai"
- `${REQUIREMENTS_FILE}`: "requirements.md"
- `${ARCHITECTURE_FILE}`: "architecture.md"
- And 12+ other standardized file references

### Benefits
- **Easy Maintenance**: Change paths once, update everywhere
- **Consistency**: All agents use standardized file locations
- **Flexibility**: Simple reconfiguration for different projects

## 🎯 Key Features

### Intelligent Project Analysis
- **Documentation Scanning**: Analyzes existing READMEs, specs, and documentation
- **Source Code Analysis**: Understands project structure and patterns
- **Test Coverage Assessment**: Evaluates current testing approach
- **Architecture Detection**: Identifies architectural patterns and frameworks

### Conditional Agent Activation
- **User Experience Designer**: Activated for UI/UX-critical projects
- **Security Expert**: Activated for security-sensitive applications
- **Legal Compliance Advisor**: Activated for regulated industry projects
- **Production Helpers**: Activated for deployment acceleration needs

### Quality Assurance
- **Progressive Refactoring**: Systematic Level 1-6 code improvement
- **Comprehensive Testing**: Unit, integration, and acceptance test validation
- **Security Validation**: Threat modeling and vulnerability assessment
- **Performance Optimization**: Bottleneck identification and resolution

### Development Acceleration
- **Walking Skeleton**: Minimal end-to-end implementation for architecture validation
- **Production Readiness**: Rapid deployment with quality safeguards
- **Technical Debt Management**: Systematic debt tracking and resolution
- **CI/CD Integration**: Automated pipeline monitoring and recovery

## 🚀 Getting Started

1. **Initialize Workflow**: Use `cai/atdd "your feature description"` to start
2. **Review Analysis**: Examine the project analysis and recommended entry point
3. **Follow Stages**: Work through DISCUSS → ARCHITECT → DISTILL → DEVELOP → DEMO
4. **Quality Gates**: Each stage includes validation before progression
5. **Complete Feature**: Finish with comprehensive refactoring and documentation

## 🏆 Success Metrics

- **Single Responsibility**: 33+ focused agents vs previous 4 complex agents
- **Quality Gates**: 8-step validation cycle with evidence collection
- **Context Efficiency**: Clean isolation prevents context pollution
- **Workflow Flexibility**: Resume at any stage, conditional activation
- **Code Quality**: Level 1-6 progressive refactoring system
- **Production Ready**: Quality-assured rapid deployment capabilities

## 📚 Documentation

- **Agent Specifications**: Detailed role definitions in `.claude/agents/`
- **Command Reference**: Integration patterns in `.claude/commands/`
- **Workflow Documentation**: Process guides in `docs/craft-ai/`
- **Progress Tracking**: Comprehensive history in `PROGRESS.md`

## 🎨 Visual Organization

Each agent category has distinctive colors and emojis for easy identification:
- 🟦 **Blue Family**: Requirements Analysis
- 🟧 **Orange Family**: Architecture Design
- ❤️ **Bright Red Family**: Test Design & Quality Validation
- 🟢 **Dark Green Family**: Development
- 🔵 **Light Blue Family**: Refactoring
- ⚫ **Gray/Brown Family**: Coordination
- ⚙️ **Configuration**: System Configuration

---

**AI-Craft: Where systematic development meets intelligent automation** 🚀

*Built with Single Responsibility Principle | Powered by ATDD Methodology | Enhanced by AI Agent Orchestration*