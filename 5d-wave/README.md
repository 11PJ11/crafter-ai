# AI-Craft 5D-WAVE Framework

## Overview

The 5D-WAVE framework implements the comprehensive DISCUSS→DESIGN→DISTILL→DEVELOP→DEMO methodology. This framework converts the proven CAI ATDD framework into a streamlined, integrated workflow with complete knowledge preservation for critical technical execution agents.

## 5D-Wave Methodology

The 5D-WAVE methodology implements a systematic approach to software development through five distinct waves:

1. **DISCUSS**: Requirements gathering and business analysis
2. **DESIGN**: Architecture design with visual representation
3. **DISTILL**: Acceptance test creation and business validation scenarios
4. **DEVELOP**: Outside-In TDD with mandatory 11-phase discipline (PREPARE→RED→GREEN→REVIEW→REFACTOR→VALIDATE→COMMIT)
5. **DEMO**: Production readiness validation and stakeholder demonstration

## Core Agents (10 Total)

### 🌊 5D-Wave Core Agents

1. **business-analyst** → DISCUSS wave (requirements gathering)
2. **solution-architect** → DESIGN wave (architecture & technology)
3. **acceptance-designer** → DISTILL wave (test scenarios)
4. **test-first-developer** → DEVELOP wave (outside-in TDD)
5. **feature-completion-coordinator** → DEMO wave (production readiness)
6. **systematic-refactorer** → Essential for Level 1-6 refactoring

### 🔧 Specialist Agents (Standalone & Collaborative)

7. **mikado-refactoring-specialist-enhanced** → Complex refactoring roadmaps
8. **walking-skeleton-helper** → Thinnest E2E slice + DevOps automation
9. **root-cause-analyzer** → Debugging, post-mortem, problem research
10. **architecture-diagram-manager** → Visual architecture maintenance & updates

## Command Structure

### 5D-Wave Core Commands (DW Prefix)

- `*dw-start [project-description]` - Initialize 5D-Wave workflow
- `*dw-discuss [requirements]` - Wave 1: Business analysis
- `*dw-design [system-context]` - Wave 2: Architecture design
- `*dw-distill [acceptance-criteria]` - Wave 3: Test scenarios
- `*dw-develop [story-id]` - Wave 4: Outside-In TDD
- `*dw-demo [feature-name]` - Wave 5: Production readiness

### Specialist Commands

- `*mikado [target] [options]` - Complex refactoring roadmaps
- `*skeleton [environment] [feature]` - Walking skeleton E2E automation
- `*root-why [problem-description]` - Root cause analysis & debugging
- `*diagram [scope] [action]` - Architecture diagram management

## Knowledge Preservation Guarantee

This expansion pack implements **ZERO KNOWLEDGE REDUCTION** for the three critical technical execution agents:

- **test-first-developer**: Complete 925-line methodology preserved
- **systematic-refactorer**: COMPLETE refactoring mechanics database (24 techniques + safety protocols)
- **mikado-refactoring-specialist-enhanced**: Full enhanced methodology with discovery tracking

## Workflow Templates

### Greenfield Development

Complete greenfield project development with full visual architecture lifecycle.

### Brownfield Integration

Legacy system enhancement with visual refactoring roadmaps and systematic improvement.

### Rapid Prototyping

Streamlined validation workflow with essential visual architecture and accelerated feedback.

## Architecture Diagram Integration

The architecture-diagram-manager provides complete visual architecture lifecycle management:

- **Creation**: Architecture diagrams from solution-architect decisions
- **Evolution**: Real-time updates throughout development
- **Validation**: Visual verification against implementation
- **Synchronization**: Coordination with refactoring and development progress

## Installation

1. Place this framework in your AI-Craft installation:

   ```
   ai-craft/5d-wave/
   ```

2. Update your configuration to include the 5D-WAVE framework.

3. Agents will be available via the standard agent syntax.

## Usage Examples

### Start a New Greenfield Project

```
*dw-start "User authentication system with microservices architecture"
```

### Execute Full 5D-Wave Cycle

**Option 1: Automated DEVELOP Wave (Recommended)**
```bash
*dw-discuss "User registration and login requirements"
*dw-design "Microservices with JWT authentication"
*dw-distill "User can register and login securely"
*dw-develop "Implement user authentication with JWT"
  # Automatically: baseline → roadmap → split → execute all steps → finalize
  # Quality gates: 3 + 3N reviews (e.g., 10 steps = 33 reviews)
*dw-demo "user-authentication"
```

**Option 2: Manual Granular Control (Advanced)**
```bash
# DISCUSS and DESIGN waves
*dw-discuss "User registration requirements"
*dw-design "JWT authentication architecture"

# DEVELOP wave - manual orchestration
*dw-baseline "Implement user authentication"
*dw-roadmap @solution-architect "Implement user authentication"
*dw-split @devop "user-authentication"

# Execute individual steps with 11-phase TDD
*dw-execute @software-crafter "docs/feature/user-authentication/steps/01-01.json"
*dw-execute @software-crafter "docs/feature/user-authentication/steps/01-02.json"
# ... (repeat for all steps)

*dw-finalize @devop "user-authentication"

# DEMO wave
*dw-demo "user-authentication"
```

**Option 3: Execute Single Step with Complete 11-Phase TDD**
```bash
# For executing one specific step with full TDD workflow
*dw:execute @software-crafter "docs/feature/user-auth/steps/01-02.json"
  # Automatic: PREPARE → RED → GREEN → REVIEW → REFACTOR → VALIDATE → COMMIT
  # Includes mandatory reviews and progressive refactoring (L1-L4)
```

### Complex Refactoring with Visual Tracking

```
*mikado "legacy-auth-modernization" --with-diagrams
*diagram mikado-tree "auth-refactoring" --visualize-dependencies
```

### Walking Skeleton with Architecture Validation

```
*skeleton "production" "user-auth-flow"
*diagram skeleton "user-auth" --minimal-slice
```

## Quality Assurance

- Complete knowledge preservation for technical execution agents
- Zero-risk refactoring with comprehensive safety protocols
- Visual architecture validation throughout development lifecycle
- Full integration with AI-Craft core functionality

## Support

This framework provides complete functionality through the proven 5D-Wave methodology with comprehensive visual architecture integration.
