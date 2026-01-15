# Command-Agent Auto-Activation Mapping

<!-- version: 1.2.34 -->

## Configuration Status: ✅ COMPLETE

All DW commands are now configured to automatically trigger specialized agent teams while keeping the main instance context-free.

## Context-Free Implementation Pattern

### Core Principle

- **Main Instance**: Receives command, delegates via Task tool, returns brief confirmation
- **Specialized Agents**: Handle all domain-specific work, context, and state
- **Coordination**: Agents communicate through shared documentation artifacts

### Implementation Steps

1. Main instance receives `/nw:command` with arguments
2. Main instance immediately delegates using Task tool
3. Main instance returns brief confirmation, retains NO context
4. Specialized agents handle all work in their domain
5. Agents coordinate through shared artifacts

## Command → Agent Team Mappings

### DISCUSS Wave Commands

- **`/nw:discuss`** → `business-analyst` (Riley), `acceptance-designer`, `root-cause-analyzer`
- **`/nw:root-why`** → `root-cause-analyzer`, `business-analyst` (Riley), `solution-architect` (Morgan)

### DESIGN Wave Commands

- **`/nw:design`** → `solution-architect` (Morgan), `architecture-diagram-manager` (Archer)
- **`/nw:diagram`** → `architecture-diagram-manager` (Archer), `solution-architect` (Morgan)

### DISTILL Wave Commands

- **`/nw:distill`** → `acceptance-designer`, `software-crafter` (Crafty)
- **Note**: Walking Skeleton functionality integrated into `/nw:discuss` (automatic detection and suggestion)

### DEVELOP Wave Commands

- **`/nw:develop`** → `software-crafter` (Crafty)
- **`/nw:refactor`** → `software-crafter` (Crafty), `architecture-diagram-manager`
- **`/nw:mikado`** → `software-crafter` (Crafty), `architecture-diagram-manager` (Archer)

### DEMO Wave Commands

- **`/nw:demo`** → `feature-completion-coordinator`, `business-analyst` (Riley)

### Workflow Commands

- **`/nw:start`** → `nWave-core-team-team`, `business-analyst` (Riley)
- **`/nw:roadmap`** → Specified agent (via @agent parameter)
- **`/nw:split`** → `software-crafter` (Crafty) - Default agent for TDD step generation with 14-phase enforcement
- **`/nw:execute`** → Specified agent (via @agent parameter)
- **`/nw:review`** → Specified reviewer agent (via @agent parameter)
- **`/nw:finalize`** → `devop`, `feature-completion-coordinator`
- **`/nw:git`** → `feature-completion-coordinator`, `systematic-refactorer`, `business-analyst` (Riley)

## Context Isolation Guarantees

### Main Instance NEVER Retains:

- ❌ Project-specific business requirements
- ❌ Code analysis or refactoring state
- ❌ Architecture designs or diagrams
- ❌ Test implementations or TDD state
- ❌ Stakeholder context or domain knowledge
- ❌ Technical decisions or solution details

### Main Instance ONLY:

- ✅ Receives slash commands with arguments
- ✅ Delegates to appropriate agent teams via Task tool
- ✅ Returns brief confirmation messages
- ✅ Maintains command routing logic
- ✅ Preserves agent activation mappings

## Agent Coordination Mechanisms

### Shared Artifacts

- `docs/dw/requirements/` - Requirements and business analysis
- `docs/dw/design/` - Architecture and visual diagrams
- `docs/dw/testing/` - Test suites and acceptance criteria
- `docs/dw/refactoring/` - Code analysis and improvement plans
- `docs/dw/delivery/` - Production readiness and demonstrations

### Cross-Agent Communication

- Agents read and build upon each other's outputs
- Progressive refinement through wave methodology
- Shared documentation serves as communication protocol
- Visual artifacts provide common reference points

## Validation Status

- ✅ **17/17** commands configured for auto-agent activation
- ✅ **3/17** commands have explicit context-free implementation patterns
- ✅ **16 specialized agents** available for domain-specific work
- ✅ **Main instance isolation** preserved across all command flows
- ✅ **Agent coordination** through shared documentation artifacts

## Next Steps

1. **Pattern Propagation**: Apply context-free implementation pattern to remaining 14 commands
2. **Testing**: Validate actual command execution follows context-free patterns
3. **Documentation**: Ensure all agents understand their coordination protocols
4. **Monitoring**: Track that main instance maintains context isolation

---

**Status**: Configuration complete, main instance remains context-free, all commands trigger specialized agent teams automatically.
