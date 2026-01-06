# Phase 1 Critical Corrections Summary

**Date**: 2026-01-06
**Analyst**: Lyra (software-crafter)
**Source**: Adversarial reviews of steps 01-01 through 01-06

## CRITICAL BLOCKER - MUST RESOLVE BEFORE ANY IMPLEMENTATION

### Foundational Issue: tools/toon/ Directory Missing

**Status**: CONFIRMED - Directory does not exist in repository
**Impact**: CATASTROPHIC - All Phase 1 steps assume this infrastructure exists
**Evidence**: `ls /mnt/c/Repositories/Projects/ai-craft/tools/` shows no `toon/` subdirectory

**Resolution Required**:
1. Create `tools/toon/` directory structure
2. Add `__init__.py` for Python module initialization
3. Establish this infrastructure BEFORE starting 01-01

---

## Step 01-01: Create TOON Parser Core

### Critical Issues from Adversarial Review

1. **TOON Version Mismatch** (Risk Score: 9.5/10)
   - **Issue**: Task requires TOON v3.0, but test fixture (`agents/novel-editor-chatgpt-toon.txt`) is v1.0
   - **Evidence**: File header shows "TOON v1.0"
   - **Impact**: Parser will fail against provided test data
   - **Correction**:
     ```json
     "tdd_approach": {
       "prerequisite_validation": {
         "action": "Verify TOON version compatibility",
         "steps": [
           "Check agents/novel-editor-chatgpt-toon.txt version (currently v1.0)",
           "DECISION: Support v1.0 OR convert fixture to v3.0 OR implement version detection",
           "Document version strategy in execution_guidance"
         ]
       }
     }
     ```

2. **Library Availability Not Pre-Validated** (Blocking)
   - **Issue**: Task says "use python-toon if available" but no pre-execution validation
   - **Correction**:
     ```json
     "blocking_prerequisite_check": {
       "required_before_execution": [
         {
           "name": "Validate python-toon library availability",
           "command": "pip index versions python-toon || pip show python-toon",
           "go_criteria": "Library exists with API documentation",
           "no_go_criteria": "Library unavailable → use custom parser (add 12-16 hours, not 8)"
         }
       ]
     }
     ```

3. **Parser Output Schema Undefined** (Circular Dependency)
   - **Issue**: Templates (01-02 through 01-04) need parser schema to design, but parser doesn't define output
   - **Correction**:
     ```json
     "deliverables": {
       "parser_output_schema": {
         "type": "TypedDict or dataclass",
         "required_fields": {
           "id": "str",
           "type": "Literal['agent', 'command', 'skill']",
           "metadata": "dict",
           "sections": "dict[str, Any]"
         },
         "example": {
           "id": "software-crafter",
           "type": "agent",
           "metadata": {"name": "Crafty", "version": "1.0"},
           "sections": {"commands": [...], "dependencies": [...]}
         }
       }
     }
     ```

4. **Revised Time Estimate**
   - **Original**: 4-6 hours (optimistic)
   - **Corrected**:
     - With python-toon library: 4-6 hours
     - Custom parser (likely): 14-18 hours
     - Version compatibility resolution: +2 hours
     - **Total realistic**: 16-20 hours if custom implementation required

---

## Step 01-02: Create Agent Jinja2 Template

### Critical Issues from Adversarial Review

1. **Circular Dependency on 01-01** (Risk Score: 8/10)
   - **Issue**: Cannot design template without knowing parser output structure
   - **Correction**:
     ```json
     "dependencies": ["1.1"],
     "prerequisites": {
       "blocking": [
         "Step 1.1 MUST complete parser_output_schema definition",
         "Example showing: TOON input → parsed output → template input"
       ]
     }
     ```

2. **Claude Code Agent Spec Not Referenced**
   - **Issue**: AC says "validates against Claude Code agent spec" but spec not included
   - **Correction**:
     ```json
     "context": {
       "reference_specifications": [
         {
           "name": "Claude Code Agent Structure",
           "location": "~/.claude/agents/*.md (existing agents)",
           "required_sections": [
             "YAML frontmatter (name, description, model)",
             "Activation notice",
             "Agent YAML block (commands, dependencies)"
           ]
         }
       ]
     }
     ```

3. **YAML Escaping Not Specified**
   - **Issue**: Special characters in agent descriptions will break YAML
   - **Correction**:
     ```json
     "tdd_approach": {
       "inner_tests": [
         "test_template_frontmatter_valid_yaml",
         "test_template_escapes_yaml_special_chars",  // NEW
         "test_template_handles_multiline_strings",   // NEW
         "test_template_activation_notice_present"
       ]
     }
     ```

4. **Revised Time Estimate**
   - **Original**: 2-3 hours
   - **Corrected**: 4-5 hours (YAML escaping complexity + schema coordination)

---

## Step 01-03: Create Command Jinja2 Template

### Critical Issues from Adversarial Review

1. **Domain Model Confusion** (Risk Score: 9/10)
   - **Issue**: AC uses agent terminology for commands ("agent-activation header")
   - **Correction**:
     ```json
     "acceptance_criteria": [
       "Template produces command metadata header (NOT agent-activation)",
       "Template includes wave, agent-reference, command-specific fields",
       "Template renders execution context and prerequisites",
       "Template includes success criteria as markdown checklist"
     ]
     ```

2. **Missing Dependency on 01-02**
   - **Issue**: Should reference 01-02 for template pattern consistency
   - **Correction**:
     ```json
     "dependencies": ["1.1", "1.2"],
     "execution_guidance": {
       "approach": "Review 01-02 agent template for Jinja2 patterns before implementing"
     }
     ```

3. **Revised Time Estimate**
   - **Original**: 2 hours
   - **Corrected**: 3-4 hours (after domain model clarification)

---

## Step 01-04: Create Skill Jinja2 Template

### Critical Issues from Adversarial Review

1. **Skill Data Structure Undefined** (Risk Score: 7.5/10)
   - **Issue**: No specification of what a "skill" is or its data fields
   - **Correction**:
     ```json
     "context": {
       "skill_definition": {
         "description": "Skills are workflow automation capabilities bound to agents",
         "required_fields": {
           "name": "str - Skill identifier",
           "triggers": "list[str] - Activation patterns",
           "agent_association": "str or list[str] - Bound agent IDs",
           "workflow_integration": "dict - Integration metadata"
         },
         "example": {
           "name": "develop",
           "triggers": ["implement.*", "TDD", "outside-in"],
           "agent_association": "software-crafter",
           "workflow_integration": {"wave": "DEVELOP", "phase": 3}
         }
       }
     }
     ```

2. **Trigger Pattern Semantics Undefined**
   - **Issue**: Unclear if triggers are strings, regex, or structured objects
   - **Correction**:
     ```json
     "acceptance_criteria": [
       "Template produces skill YAML frontmatter",
       "Template renders trigger patterns as regex strings",  // CLARIFIED
       "Template includes agent binding with cardinality validation",
       "Template includes workflow integration with required fields"
     ]
     ```

3. **Revised Time Estimate**
   - **Original**: 2 hours
   - **Corrected**: 4-6 hours (after skill definition + trigger semantics clarification)

---

## Step 01-05: Create TOON Compiler

### Critical Issues from Adversarial Review

1. **Cascading Dependency Failures** (Risk Score: 8.5/10)
   - **Issue**: Depends on 01-01 through 01-04, all of which have fundamental issues
   - **Correction**:
     ```json
     "dependencies": ["1.1", "1.2", "1.3", "1.4"],
     "prerequisites": {
       "blocking": [
         "01-01 MUST define parser API contract (parse() signature, return type, exceptions)",
         "01-02 through 01-04 MUST define template input schemas",
         "All templates MUST use consistent section naming"
       ]
     }
     ```

2. **File Type Detection Logic Undefined**
   - **Issue**: How does compiler know if TOON file is agent/command/skill?
   - **Correction**:
     ```json
     "deliverables": {
       "file_type_detection": {
         "strategy": "Parser output includes 'type' field",
         "implementation": "Compiler reads parsed_data['type'] to select template",
         "fallback": "If type missing, infer from filename pattern (agent.toon, command.toon, skill.toon)"
       }
     }
     ```

3. **Validation Schema for AC#5 Missing**
   - **Issue**: "Validates output has required sections" but sections undefined
   - **Correction**:
     ```json
     "acceptance_criteria": [
       "Compiler reads .toon file from path",
       "Compiler selects correct template based on parsed type field",
       "Compiler writes output to specified directory",
       "Compiler reports errors clearly with file path, line number, and suggested fix",
       "Compiler validates output against type-specific schema (agent: frontmatter + commands, command: metadata + execution, skill: triggers + workflow)"
     ]
     ```

4. **Revised Time Estimate**
   - **Original**: 3-4 hours
   - **Corrected**: 6-8 hours (after all dependencies stabilize)

---

## Step 01-06: Infrastructure Integration Tests

### Critical Issues from Adversarial Review

1. **TOON Version Mismatch CATASTROPHIC** (Risk Score: 8/10)
   - **Issue**: Parser expects v3.0, test fixture is v1.0
   - **Correction**:
     ```json
     "tdd_approach": {
       "prerequisite_validation": {
         "action": "Verify test fixture compatibility",
         "steps": [
           "Confirm agents/novel-editor-chatgpt-toon.txt version",
           "If v1.0: EITHER convert to v3.0 OR update parser to support v1.0",
           "Document version strategy before implementing integration test"
         ]
       }
     }
     ```

2. **Output Specification Missing**
   - **Issue**: "Validates output structure" but structure undefined
   - **Correction**:
     ```json
     "execution_guidance": {
       "output_validation_specification": {
         "agent_output": {
           "required_sections": ["YAML frontmatter", "Activation notice", "Agent YAML block"],
           "validation_method": "Parse output as YAML, check required keys exist"
         },
         "command_output": {
           "required_sections": ["Command metadata", "Execution context", "Success criteria"],
           "validation_method": "Check markdown headers present"
         },
         "skill_output": {
           "required_sections": ["Skill frontmatter", "Trigger patterns", "Workflow integration"],
           "validation_method": "Parse YAML frontmatter, validate trigger list"
         }
       }
     }
     ```

3. **Revised Time Estimate**
   - **Original**: 2 hours
   - **Corrected**: 3-4 hours (after TOON version resolution + output spec definition)

---

## Cross-Cutting Corrections Required

### 1. Break Circular Dependency

**Problem**: Parser needs template feedback, templates need parser schema

**Solution**:
```
STEP 0 (NEW - 2 hours):
  Define parser output schema BEFORE implementing parser
  Document schema with examples
  Get sign-off from steps 01-02 through 01-04 owners

STEP 01-01:
  Implement parser conforming to agreed schema

STEPS 01-02 through 01-04:
  Implement templates consuming agreed schema
```

### 2. Establish TOON Version Strategy

**Problem**: v1.0 test fixture vs v3.0 parser spec

**Solution**:
```
DECISION REQUIRED:
  Option A: Update parser to support both v1.0 and v3.0 (add version detection)
  Option B: Convert all v1.0 fixtures to v3.0
  Option C: Implement v1.0 parser only, update spec references

RECOMMENDED: Option A (most flexible, supports existing content)
IMPACT: +3 hours to parser implementation
```

### 3. Revise Overall Phase 1 Estimate

**Original Total**: 15-19 hours (sum of individual estimates)

**Corrected Total**:
- Step 0 (Schema Definition): 2 hours
- Step 01-01 (Parser with version support): 18-20 hours
- Step 01-02 (Agent Template): 4-5 hours
- Step 01-03 (Command Template): 3-4 hours
- Step 01-04 (Skill Template): 4-6 hours
- Step 01-05 (Compiler): 6-8 hours
- Step 01-06 (Integration): 3-4 hours

**TOTAL: 40-49 hours** (not 15-19)

**Multiplier**: 2.6x original estimate

---

## Execution Recommendation

**DO NOT START PHASE 1 IMPLEMENTATION UNTIL**:

1. ✅ Create `tools/toon/` directory infrastructure
2. ✅ Define parser output schema (Step 0 - NEW)
3. ✅ Resolve TOON version strategy (v1.0 vs v3.0)
4. ✅ Validate python-toon library availability
5. ✅ Get stakeholder approval for revised timeline (40-49 hours vs 15-19 hours)

**Risk if started without corrections**: 80% probability of complete Phase 1 failure requiring restart

---

## Corrected Dependency Chain

```
PREREQUISITE PHASE:
  [Create tools/toon/ directory] (15 minutes)
  [Define parser output schema] (2 hours)
  [Resolve TOON version strategy] (1 hour)
  [Validate python-toon availability] (30 minutes)
                    ↓
STEP 01-01: Parser Core (18-20 hours)
                    ↓
         ┌──────────┴──────────┐
         ↓                     ↓
STEP 01-02: Agent     STEP 01-03: Command     STEP 01-04: Skill
Template (4-5h)       Template (3-4h)         Template (4-6h)
         ↓                     ↓                     ↓
         └──────────┬──────────┘──────────┬─────────┘
                    ↓                     ↓
              STEP 01-05: Compiler (6-8 hours)
                    ↓
              STEP 01-06: Integration Tests (3-4 hours)
```

---

## Next Actions

1. **Immediate**: Create corrected JSON files with above changes
2. **Before Implementation**: Execute prerequisite phase
3. **During Implementation**: Use revised time estimates for planning
4. **Quality Gate**: All prerequisites resolved before any coding begins

**Priority**: CRITICAL
**Blocking**: YES - Phase 1 cannot succeed without these corrections
**Owner**: Project lead + development team
