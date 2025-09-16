# AI-Craft Agent Command Definitions

## Essential 11 Commands for Complete ATDD Workflow

These commands provide comprehensive coverage of the AI-Craft ATDD framework, from brownfield analysis through production deployment.

### 1. `cai:brownfield [scope]`
**Purpose**: Brownfield Project Analyzer - Understand existing codebase structure and technical debt
**Triggers**: technical-debt-tracker → technical-stakeholder → solution-architect
**Example**: `cai:brownfield --legacy "payment-system"`
**Flow**:
```yaml
technical-debt-tracker:
  - Identifies technical debt hotspots
  - Assesses code quality metrics
  - Maps dependency structure
technical-stakeholder:
  - Evaluates technical constraints
  - Documents integration points
  - Assesses modification risk
solution-architect:
  - Analyzes architectural patterns
  - Recommends modernization strategy
```

### 2. `cai:refactor [target] [level]`
**Purpose**: Systematic Refactoring - Execute Level 1-6 refactoring or complex Mikado Method
**Triggers**: systematic-refactorer → mikado-refactoring-specialist (if complex)
**Example**: `cai:refactor "auth-module" --level 3` or `cai:refactor "architecture" --mikado`
**Flow**:
```yaml
systematic-refactorer:
  level_1_readability: "Comments, dead code, naming, magic strings"
  level_2_complexity: "Method extraction, duplication elimination"
  level_3_responsibilities: "Class breakdown, coupling reduction"
  level_4_abstractions: "Parameter objects, value objects"
  level_5_patterns: "Strategy, State, Command patterns"
  level_6_solid: "SOLID principles application"
mikado-refactoring-specialist:
  - Complex architectural refactorings
  - Parallel change patterns
  - Multi-class structural changes
```

### 3. `cai:start [project-description]`
**Purpose**: Initialize ATDD workflow with intelligent workflow selection
**Triggers**: workflow-guidance-agent → atdd-wave-coordinator
**Example**: `cai:start "e-commerce checkout feature"`
**Flow**:
```yaml
workflow-guidance-agent:
  - Assesses project complexity and type
  - Recommends workflow: greenfield/brownfield/rapid-prototype
  - Provides numbered workflow options
atdd-wave-coordinator:
  - Initializes selected workflow
  - Sets up 5-wave progression (DISCUSS→ARCHITECT→DISTILL→DEVELOP→DEMO)
```

### 4. `cai:discuss [requirements]`
**Purpose**: Requirements gathering and stakeholder collaboration (Wave 1)
**Triggers**: business-analyst → domain experts (conditional)
**Example**: `cai:discuss "user authentication with MFA" --interactive`
**Flow**:
```yaml
business-analyst:
  - Captures business requirements
  - Creates user stories with acceptance criteria
  - Documents business constraints
conditional_experts:
  - user-experience-designer (UI-heavy projects)
  - security-expert (security-critical features)
  - legal-compliance-advisor (regulated domains)
```

### 5. `cai:architect [system-context]`
**Purpose**: System architecture design and technology decisions (Wave 2)
**Triggers**: solution-architect → technology-selector → architecture-diagram-manager
**Example**: `cai:architect "microservices with event sourcing"`
**Flow**:
```yaml
solution-architect:
  - Creates architectural design document
  - Defines component boundaries and patterns
  - Documents architectural decisions
technology-selector:
  - Evaluates technology stack options
  - Provides trade-off analysis with rationale
architecture-diagram-manager:
  - Creates/updates visual architecture representations
```

### 6. `cai:develop [story-id]`
**Purpose**: Outside-In TDD implementation (Wave 4)
**Triggers**: test-first-developer → systematic-refactorer
**Example**: `cai:develop "STORY-AUTH-001" --outside-in`
**Flow**:
```yaml
test-first-developer:
  - Implements using Outside-In TDD approach
  - Creates E2E acceptance test first
  - Steps down to unit tests (inner TDD loop)
  - Implements production code to pass tests
systematic-refactorer:
  - Applies Level 1-3 refactoring during development
  - Maintains clean code throughout TDD cycles
```

### 7. `cai:transition`
**Purpose**: Bridge planning phase to execution with context preservation
**Triggers**: phase-transition-manager → story-context-manager
**Example**: `cai:transition --validate`
**Flow**:
```yaml
phase-transition-manager:
  - Validates planning completeness (requirements, architecture, acceptance)
  - Executes document sharding (epics → stories)
  - Preserves architectural context during transition
story-context-manager:
  - Creates hyper-detailed development stories
  - Embeds architectural context and implementation guidance
  - Includes detailed acceptance criteria and quality gates
```

### 8. `cai:validate [scope]`
**Purpose**: Comprehensive quality validation and compliance checking
**Triggers**: commit-readiness-coordinator → specialized validators
**Example**: `cai:validate --full` or `cai:validate --security`
**Flow**:
```yaml
commit-readiness-coordinator:
  - Orchestrates all validation processes
validators:
  - code-quality-validator: "Static analysis, complexity, naming"
  - architecture-compliance-validator: "Pattern adherence, boundaries"
  - security-performance-validator: "Vulnerabilities, performance"
  - test-execution-validator: "Coverage, test quality"
```

### 9. `cai:complete [feature-name]`
**Purpose**: Feature finalization and production readiness (Wave 5)
**Triggers**: feature-completion-coordinator → production-readiness-helper
**Example**: `cai:complete "user-authentication" --deploy-ready`
**Flow**:
```yaml
feature-completion-coordinator:
  - Validates feature completeness against acceptance criteria
  - Triggers comprehensive Level 4-6 refactoring
  - Updates documentation and architecture diagrams
production-readiness-helper:
  - Identifies and resolves deployment blockers
  - Validates production environment compatibility
  - Prepares go-live checklist
```

### 10. `cai:skeleton [target-environment]`
**Purpose**: Walking Skeleton Production Readiness - Minimal E2E implementation with automated pipeline
**Triggers**: walking-skeleton-helper → production-readiness-helper → test-first-developer
**Example**: `cai:skeleton production --feature "user-auth" --timeline "2-weeks"`
**Flow**:
```yaml
walking-skeleton-helper:
  - Creates thinnest E2E implementation touching all architectural layers
  - Selects minimal feature with maximum architectural coverage
  - Designs simplest integration path through all system components
production-readiness-helper:
  - Identifies immediate production deployment blockers
  - Scores readiness across 9 categories with 36 questions framework
  - Generates gap analysis and prioritized remediation plan
test-first-developer:
  - Coordinates Outside-In TDD implementation of walking skeleton
  - Ensures real functionality delivery with proper integration testing
  - Guides CI/CD pipeline setup and automated testing implementation
```

### 11. `cai:help [agent-name]`
**Purpose**: Interactive guidance and agent transformation
**Triggers**: atdd-wave-coordinator (transformation) or interactive-wave-elicitation
**Example**: `cai:help architect` or `cai:help --interactive`
**Flow**:
```yaml
without_agent_name:
  - Shows complete command catalog with descriptions
  - Offers workflow guidance based on project context
  - Provides agent directory with specializations
with_agent_name:
  - Transforms wave coordinator into specified agent
  - Provides agent-specific command reference
  - Enables agent-focused interactive mode
interactive_mode:
  - Launches interactive elicitation with numbered options
  - Provides contextual guidance for current wave/phase
```

## Command Modifiers

### Scope Control
- `--legacy`: Focus on brownfield/legacy system analysis
- `--full`: Complete project scope processing
- `--epic [epic-id]`: Focus on specific epic
- `--story [story-id]`: Focus on specific story

### Workflow Control
- `--interactive`: Enable numbered option selection and guided workflows
- `--wave [name]`: Jump to specific wave (discuss/architect/distill/develop/demo)
- `--compress`: Enable context compression for efficient transitions
- `--validate`: Add comprehensive validation steps

### Refactoring Control
- `--level [1-6]`: Specify refactoring level (1=readability, 6=SOLID principles)
- `--mikado`: Use Mikado Method for complex architectural refactoring
- `--parallel-change`: Apply parallel change pattern for breaking changes

### Quality Control
- `--security`: Focus on security analysis and validation
- `--performance`: Focus on performance optimization
- `--outside-in`: Use Outside-In TDD methodology
- `--deploy-ready`: Include production readiness validation

### Production & Deployment Control
- `--assessment-only`: Production readiness analysis without implementation
- `--feature [name]`: Specify walking skeleton feature (e.g., "user-auth", "basic-crud")
- `--timeline [duration]`: Implementation timeline ("1-week", "2-weeks", "1-month")
- `--minimal`: Ultra-minimal implementation (happy path only)
- `--comprehensive`: Full implementation with error handling and edge cases
- `--pipeline [type]`: CI/CD pipeline type (github-actions, gitlab, jenkins, azure-devops)
- `--monitoring [level]`: Monitoring depth (basic, standard, comprehensive)

## Usage Examples

### Brownfield Project Analysis
```bash
# Analyze existing legacy system
cai:brownfield --legacy "monolithic-ecommerce-app"

# Focused technical debt assessment
cai:brownfield "payment-module" --scope module

# Full system architecture analysis
cai:brownfield --full --interactive
```

### Systematic Refactoring Workflows
```bash
# Basic code cleanup (Levels 1-2)
cai:refactor "user-service" --level 2

# Complex architectural refactoring
cai:refactor "authentication-system" --mikado --parallel-change

# Progressive refactoring with validation
cai:refactor "core-domain" --level 4 --validate
```

### Complete ATDD Feature Development
```bash
# New feature from requirements to deployment
cai:start "real-time notifications" --interactive
cai:discuss "push notifications with preferences" --interactive
cai:architect "event-driven notification system"
cai:transition --validate
cai:develop "STORY-NOTIFY-001" --outside-in
cai:validate --full
cai:skeleton production --assessment-only
cai:complete "notifications-feature" --deploy-ready
```

### Walking Skeleton Production Readiness Workflow
```bash
# Assess production readiness and identify blockers
cai:skeleton production --assessment-only --format report

# Implement minimal E2E feature with automated pipeline
cai:skeleton development --feature "user-auth" --minimal --pipeline github-actions

# Full production deployment with comprehensive monitoring
cai:skeleton production --feature "checkout-flow" --comprehensive --monitoring comprehensive --timeline "2-weeks"

# Quick MVP validation with basic observability
cai:skeleton staging --minimal --monitoring basic --pipeline gitlab
```

### Brownfield Enhancement Workflow
```bash
# Analyze existing system first
cai:brownfield --legacy "user-management-module"

# Plan enhancement based on analysis
cai:start "add OAuth2 to existing auth" --brownfield

# Assess production readiness before enhancement
cai:skeleton staging --assessment-only --feature "oauth2-integration"

# Refactor before adding new functionality
cai:refactor "auth-module" --level 3 --validate

# Continue with normal ATDD workflow
cai:discuss "OAuth2 integration requirements"
# ... rest of workflow
```

## Agent Transformation Examples

```bash
# Transform coordinator into specific agent
cai:help business-analyst
> *help - Show business analyst specific commands
> *requirements - Start requirements elicitation workshop
> *stakeholder - Simulate stakeholder perspectives
> *constraints - Document business constraints

# Interactive workflow guidance
cai:help --interactive
> 1. Start new ATDD workflow
> 2. Continue existing workflow
> 3. Analyze brownfield project
> 4. Execute refactoring plan
> Type your choice...
```

## Quick Reference Matrix

| Command | Primary Wave | Brownfield | Greenfield | Refactoring | Validation |
|---------|--------------|------------|------------|-------------|------------|
| `cai:brownfield` | Pre-planning | ✅ Essential | Optional | Planning | Analysis |
| `cai:refactor` | Any | ✅ Critical | ✅ Continuous | ✅ Core | Quality |
| `cai:start` | Wave 0 | ✅ Planning | ✅ Planning | Planning | Setup |
| `cai:discuss` | Wave 1 | ✅ Requirements | ✅ Requirements | Context | Business |
| `cai:architect` | Wave 2 | ✅ Modernization | ✅ Design | Structure | Technical |
| `cai:develop` | Wave 4 | ✅ Enhancement | ✅ Implementation | Code | Testing |
| `cai:transition` | Wave 2→3 | ✅ Context | ✅ Context | Planning | Validation |
| `cai:validate` | Any | ✅ Quality | ✅ Quality | ✅ Quality | ✅ Core |
| `cai:complete` | Wave 5 | ✅ Delivery | ✅ Delivery | Final | Production |
| `cai:skeleton` | Pre-production | ✅ Modernization | ✅ MVP | Pipeline | Production |
| `cai:help` | Any | ✅ Guidance | ✅ Guidance | ✅ Guidance | ✅ Support |

## Error Handling & Smart Defaults

### Automatic Prerequisites
- Commands automatically trigger required preceding steps
- Missing context prompts for information or uses intelligent defaults
- Incomplete workflows resume from last completed step

### Intelligent Routing
- **Brownfield Detection**: Automatically engages technical-debt-tracker when legacy systems detected
- **Complexity Assessment**: Routes to appropriate refactoring approach based on scope
- **Validation Triggers**: Automatically adds validation steps for critical operations

### Recovery Mechanisms
- **Rollback Support**: All refactoring operations include rollback capability
- **State Preservation**: Context maintained across wave transitions and interruptions
- **Failure Recovery**: Smart restart from last successful checkpoint

This command set provides complete coverage of both greenfield and brownfield development workflows while maintaining the essential ATDD methodology and supporting systematic refactoring practices.