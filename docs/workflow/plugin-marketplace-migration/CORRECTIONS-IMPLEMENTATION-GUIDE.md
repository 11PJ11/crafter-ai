# Adversarial Review Corrections Implementation Guide

**Status**: Ready for systematic application
**Date**: 2026-01-06
**Scope**: 16 step files across Phases 1, 4, 6, 7
**Priority**: Phase 1 > Phase 6 > Phase 7 > Phase 4

## Executive Summary

This guide documents all corrections identified in adversarial reviews that need to be applied to step files. Phase 5 already has CORRECTED versions applied. The remaining phases require systematic integration of critical fixes to resolve blockers and improve execution clarity.

## Phase 1: TOON Infrastructure Corrections (CRITICAL PRIORITY)

**Files**: 01-01.json through 01-06.json (6 files)
**Source**: `adversarial-reviews/PHASE_1_CRITICAL_CORRECTIONS.md` (14 KB)

### Global Changes for All Phase 1 Steps

#### 1. Add Mandatory Prerequisites Check Section
```json
"prerequisites": {
  "blocking": [
    "tools/toon/ directory MUST exist with README.md",
    "TOON format specification v3.0 must be accessible",
    "Parser output schema must be defined before template implementation"
  ],
  "validation": "Run: ls tools/toon/README.md. Must exist. If not: BLOCKER_001"
}
```

#### 2. Add BLOCKER_001 Status Check
All steps must reference:
```json
"critical_blocker_status": {
  "BLOCKER_001": {
    "title": "TOON Toolchain Missing",
    "status": "UNRESOLVED",
    "evidence": "tools/toon/ directory does not exist",
    "impact": "Cannot parse TOON files, blocks all Phase 1 steps",
    "resolution_options": [
      "A: Implement TOON toolchain (16-20h estimated)",
      "B: Pivot to Markdown templates (8-10h, loses TOON benefits)",
      "C: Block until external TOON library available"
    ]
  }
}
```

### Step 01-01 Specific Corrections

**Time Estimate Correction**:
- Current: 4-6h
- Corrected: 16-20h (custom parser scenario)

**Critical Additions**:
1. **TOON Version Mismatch Fix**:
```json
"toon_specification": {
  "required_version": "v3.0",
  "fixture_version": "v1.0",
  "mismatch_noted": true,
  "resolution": "Update fixture or clarify if v1.0 sufficient"
}
```

2. **Parser Output Schema Deliverable**:
```json
"deliverables": {
  "files_to_create": [
    "tools/toon/parser.py",
    "tools/toon/schema/parser_output.json",  // ADD THIS
    "tests/tools/toon/test_parser.py"
  ]
}
```

3. **python-toon Library Check**:
```json
"dependency_check": {
  "python_toon_library": {
    "required": true,
    "availability": "UNVERIFIED",
    "fallback": "Custom implementation if unavailable"
  }
}
```

### Steps 01-02, 01-03, 01-04 Shared Corrections

**Circular Dependency Resolution**:
```json
"dependencies": ["1.1"],
"dependency_notes": {
  "parser_schema_required": "Step 1.1 MUST complete with parser_output_schema definition",
  "cannot_proceed_without": "Documented parser output structure with examples"
},
"blocking_prerequisites": [
  "Step 01-01 parser_output_schema MUST be defined",
  "Example showing: TOON input → parsed output → expected template output"
]
```

**Time Estimate Updates**:
- 01-02: 2-3h → 4-5h (YAML escaping complexity)
- 01-03: 2h → 3-4h (command-specific terminology fixes)
- 01-04: 2h → 4-6h (skill definition undefined)

### Step 01-05, 01-06 Corrections

**Add TOON Directory Check**:
```json
"execution_guidance": {
  "workflow": [
    "0. PREREQUISITE CHECK: Verify tools/toon/ exists",
    "1. If not exists: HALT - refer to BLOCKER_001 resolution",
    // ... rest of workflow
  ]
}
```

---

## Phase 6: Template Migration Corrections (HIGH PRIORITY)

**Files**: 06-01.json through 06-03.json (3 files)
**Source**: `adversarial-reviews/PHASE_6_CORRECTION_SUMMARY.md` (14 KB)

### Global Changes for All Phase 6 Steps

#### Add Critical Blocker Section
```json
"critical_blocker_status": {
  "BLOCKER_001": {
    "title": "TOON Toolchain Missing",
    "status": "UNRESOLVED",
    "details": "tools/toon/ directory does not exist. Cannot migrate to TOON without toolchain.",
    "impact": "Blocks all template migration steps. Cannot proceed until resolved.",
    "resolution_options": {
      "option_a": {
        "name": "Implement TOON Toolchain",
        "effort": "16-20 hours",
        "benefits": "Enables TOON format benefits, structured migration",
        "risks": "Significant time investment, potential scope creep"
      },
      "option_b": {
        "name": "Pivot to Markdown Templates",
        "effort": "8-10 hours",
        "benefits": "Faster delivery, simpler implementation",
        "risks": "Loses TOON benefits, may require rework later"
      },
      "option_c": {
        "name": "Block Until External Library",
        "effort": "Wait time unknown",
        "benefits": "No custom implementation needed",
        "risks": "Indefinite delay, dependency on external team"
      }
    }
  }
}
```

#### Add Mandatory Prerequisite Check
```json
"mandatory_prerequisite_check": {
  "PRE-01": {
    "check": "tools/toon/README.md exists",
    "command": "ls tools/toon/README.md",
    "expected": "File found",
    "action_if_fail": "HALT - Refer to BLOCKER_001 resolution"
  },
  "PRE-02": {
    "check": "TOON parser functional",
    "command": "python tools/toon/parser.py --version",
    "expected": "Version output (v3.0+)",
    "action_if_fail": "HALT - Parser not implemented"
  },
  "PRE-03": {
    "check": "Parser output schema documented",
    "command": "cat tools/toon/schema/parser_output.json",
    "expected": "JSON schema with agent/command/skill structure",
    "action_if_fail": "HALT - Cannot template without schema"
  }
}
```

#### Add Workflow Options
Each step needs three workflow branches:

```json
"workflow_option_a": {
  "condition": "TOON toolchain implemented",
  "steps": [
    "1. Verify TOON parser available",
    "2. Migrate [agent/command/skill] to TOON format",
    // ... TOON-specific steps
  ]
},
"workflow_option_b": {
  "condition": "Pivot to Markdown templates",
  "steps": [
    "1. Create Markdown template for [agent/command/skill]",
    "2. Migrate using Jinja2/string interpolation",
    // ... Markdown-specific steps
  ]
},
"workflow_option_c": {
  "condition": "Blocked until TOON available",
  "steps": [
    "1. HALT execution",
    "2. Document dependency on external TOON library",
    "3. Escalate to project lead for decision"
  ]
}
```

#### Risk Score Update
```json
"risk_score": {
  "before_correction": 9.0,
  "after_correction": 4.0,
  "reduction_factors": [
    "Blocker explicitly documented",
    "Three resolution paths provided",
    "Prerequisite checks prevent false starts"
  ]
}
```

---

## Phase 7: Plugin Structure Corrections (HIGH PRIORITY)

**Files**: 07-01.json through 07-03.json (3 files)
**Source**: `adversarial-reviews/PHASE_7_AGENT_COUNT_CORRECTION.md` (8.2 KB)

### Step 07-01: Comprehensive Agent Count Fix

**CRITICAL**: Replace ALL instances of "28 agents" with "26 agents" + exclusion note

#### Locations to Update in 07-01.json:

1. **Line 35** (acceptance_criteria):
```json
"All 26 agents referenced (actual count: novel-editor and novel-editor-reviewer excluded from build)"
```

2. **Line 42** (outer_test):
```json
"THEN validation passes with no errors AND all 26 agents + 20 commands + 3 skills are discoverable"
```

3. **Line 65** (workflow step 2):
```json
"2. Add all 26 agent references organized by wave (DISCUSS, DESIGN, DISTILL, DEVELOP, DEMO) - excludes novel-editor and novel-editor-reviewer not in build"
```

4. **Line 78** (quality_gates):
```json
"All 26 agents referenced (verify count and names) - NOTE: novel-editor and novel-editor-reviewer excluded from build system"
```

5. **Additional locations** (from adversarial review):
- Line 91: review_status note
- Line 105: blocking prerequisite details
- Line 107: recommendation verification command
- Line 159: hidden_dependencies section
- Line 191: recommendations section
- Line 241: questions_for_user section
- Line 281-285: contradictions_found section
- Line 340: dangerous_assumptions section
- Line 444-448: failure_scenarios section
- Line 569-573: missing_prerequisites section
- Line 720: critical_blockers section

**Pattern to Add Everywhere**:
```text
26 agents (novel-editor and novel-editor-reviewer excluded from build)
```

### Step 07-03: Recommendation Update

**Line 177** correction:
```json
"recommendation": "VERIFY BEFORE STARTING: (1) Confirm 'find 5d-wave/agents -name \"*.toon\" | wc -l' == 28 total files (26 agents for build, 2 excluded: novel-editor, novel-editor-reviewer)"
```

---

## Phase 4: Command Migration Corrections (MEDIUM PRIORITY)

**Files**: 04-01.json through 04-06.json + 04-01b.json (7 files)
**Source**: `adversarial-reviews/PHASE-4-CORRECTIONS-SUMMARY.md` (12 KB)

### Global Additions for All Phase 4 Steps

#### 1. Prerequisite Checks Section
```json
"prerequisite_checks": {
  "phase_1_complete": {
    "check": "Phase 1 TOON infrastructure complete",
    "validation": "tools/toon/parser.py exists and functional",
    "action_if_fail": "Cannot migrate commands without TOON toolchain"
  },
  "toon_spec_available": {
    "check": "TOON v3.0 specification accessible",
    "validation": "tools/toon/README.md documents format",
    "action_if_fail": "Cannot validate command TOON format without spec"
  },
  "baseline_established": {
    "check": "Baseline measurements complete",
    "validation": "docs/workflow/plugin-marketplace-migration/baseline.yaml exists",
    "action_if_fail": "Cannot validate migration without baseline metrics"
  }
}
```

#### 2. TOON Compiler Specification
```json
"toon_compiler": {
  "location": "tools/toon/compiler.py",
  "purpose": "Transforms TOON source to Claude Code compliant output",
  "input": "5d-wave/tasks/dw/*.toon (TOON format)",
  "output": "dist/commands/dw/*.md (Markdown format)",
  "validation": "pytest tests/tools/toon/test_compiler.py"
}
```

#### 3. Error Handling Section
```json
"error_handling": {
  "scenario_1": {
    "error": "TOON parser fails on malformed input",
    "handling": "Log error with line number, skip file, continue processing",
    "test": "test_parser_malformed_input_graceful_failure"
  },
  "scenario_2": {
    "error": "Output directory not writable",
    "handling": "Fail fast with clear error message, rollback partial writes",
    "test": "test_compiler_output_permission_error"
  },
  "scenario_3": {
    "error": "Template rendering exception",
    "handling": "Log template + data, fail file, continue with others",
    "test": "test_template_rendering_exception_handling"
  },
  "scenario_4": {
    "error": "Validation failure (output doesn't match spec)",
    "handling": "Report validation errors, mark file as failed, continue",
    "test": "test_validation_failure_reporting"
  }
}
```

#### 4. Test Specifications (Detailed)
```json
"test_specifications": {
  "unit_tests": [
    {
      "name": "test_toon_parser_valid_input",
      "purpose": "Verify parser handles valid TOON command correctly",
      "input": "Sample TOON command with all required fields",
      "expected": "Parsed dict with command metadata"
    },
    {
      "name": "test_template_rendering_with_real_data",
      "purpose": "Verify template renders with real parsed command data",
      "input": "Real parsed command dict from parser",
      "expected": "Valid Markdown output matching Claude Code spec"
    },
    {
      "name": "test_output_validation_against_spec",
      "purpose": "Verify output complies with Claude Code command spec",
      "input": "Generated command.md file",
      "expected": "Validation passes for all required fields"
    }
  ],
  "integration_tests": [
    {
      "name": "test_e2e_command_migration",
      "purpose": "Verify complete migration pipeline",
      "input": "Sample TOON command file",
      "steps": "Parse → Template → Validate → Output",
      "expected": "Valid command.md in dist/commands/dw/"
    }
  ]
}
```

### Individual Step Corrections

#### Step 04-01 Corrections
**Time Estimate**: 1h → 4-6h
**Reason**: Parser integration, template debugging, validation implementation

#### Step 04-01b Corrections
**Time Estimate**: Maintain 2-3h (already corrected in source)

#### Step 04-02, 04-03 Corrections
**Time Estimate**: 1h → 3-4h each
**Additions**: Full prerequisite_checks, error_handling, test_specifications

#### Step 04-04 Corrections
**Time Estimate**: 4h → 8-12h
**Critical Addition**: Explicit agent_bindings table

```json
"agent_bindings_table": {
  "purpose": "Map 8 DEVELOP commands to software-crafter agent",
  "bindings": [
    {"command": "dw:develop", "agent": "software-crafter", "auto_invoke": true},
    {"command": "dw:refactor", "agent": "software-crafter", "auto_invoke": true},
    {"command": "dw:mikado", "agent": "software-crafter", "auto_invoke": true},
    {"command": "dw:review", "agent": "software-crafter", "auto_invoke": false},
    {"command": "dw:baseline", "agent": "software-crafter", "auto_invoke": true},
    {"command": "dw:skeleton", "agent": "software-crafter", "auto_invoke": true},
    {"command": "dw:implement-story", "agent": "software-crafter", "auto_invoke": false},
    {"command": "dw:validate-production", "agent": "software-crafter", "auto_invoke": false}
  ],
  "validation": "Each binding MUST have test validating auto-invocation behavior"
}
```

#### Step 04-05 Corrections
**Time Estimate**: 1h → 3-4h
**Addition**: Finalize complexity tests

```json
"finalize_complexity_tests": {
  "purpose": "Validate migration preserved command complexity",
  "tests": [
    "test_command_parameter_count_preserved",
    "test_command_dependencies_mapped_correctly",
    "test_command_acceptance_criteria_complete"
  ]
}
```

#### Step 04-06 Corrections
**Time Estimate**: 2h → 4-6h
**Critical Fix**: Remove SC7 from individual step

```json
"success_criteria_mapping": {
  "SC2": "Build produces Claude Code compliant output",
  "NOTE": "SC7 (all commands auto-invocable) validated in Phase 8, not Phase 4"
}
```

---

## Implementation Sequence

### Priority Order
1. **Phase 1** (Foundation) - 6 files
2. **Phase 6** (Blocker documentation) - 3 files
3. **Phase 7** (Count fixes) - 3 files
4. **Phase 4** (Extensive additions) - 7 files

### Validation Checklist Per File
- [ ] JSON structurally valid (use `python -m json.tool < file.json`)
- [ ] All required sections present per correction guide
- [ ] Time estimates updated where specified
- [ ] Agent counts corrected (Phase 7)
- [ ] BLOCKER_001 added (Phase 1, 6)
- [ ] Prerequisite checks added (Phase 4)
- [ ] No regression on existing correct content

---

## Automation Potential

### JSON Merge Script Approach
Due to extensive corrections, consider creating a Python script to:
1. Load base JSON file
2. Apply corrections via dict merge
3. Validate JSON structure
4. Write corrected file

**Script skeleton**:
```python
import json
from pathlib import Path

def apply_corrections(base_file, corrections_dict):
    """Apply corrections to step file"""
    with open(base_file) as f:
        data = json.load(f)

    # Deep merge corrections
    data = deep_merge(data, corrections_dict)

    # Validate
    validate_json_structure(data)

    # Write
    with open(base_file, 'w') as f:
        json.dump(data, f, indent=2)

    return True
```

---

## Risk Mitigation

### Before Applying Corrections
1. **Backup all step files**: `cp steps/ steps.backup/`
2. **Version control**: Commit current state before modifications
3. **Test one file first**: Apply to 07-01.json, validate, review

### During Application
1. **Apply incrementally**: One phase at a time
2. **Validate after each file**: JSON structure check
3. **Review diffs**: Ensure only intended changes applied

### After Application
1. **Full validation**: All 16 files parse as valid JSON
2. **Spot check**: Review 2-3 files manually for correctness
3. **Create report**: Document all changes made

---

## Next Steps

1. **User Decision**: Approve this implementation guide
2. **Execution**: Apply corrections systematically (estimated 2-3 hours for all 16 files)
3. **Validation**: Verify all JSON valid + corrections applied
4. **Report**: Create CORRECTIONS-APPLIED-REPORT.md with details
5. **Commit**: Stage changes with detailed commit message

**Estimated Total Effort**: 3-4 hours for complete correction application and validation
