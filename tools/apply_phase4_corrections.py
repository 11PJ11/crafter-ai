#!/usr/bin/env python3
"""
Apply Phase 4 corrections systematically to all 7 command migration steps.
"""

import json
from pathlib import Path
from typing import Dict, Any

def deep_merge(base: Dict[Any, Any], updates: Dict[Any, Any]) -> Dict[Any, Any]:
    """Deep merge updates dict into base dict."""
    result = base.copy()
    for key, value in updates.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result

def get_phase4_prerequisite_checks() -> Dict[str, Any]:
    """Get standard prerequisite checks for Phase 4."""
    return {
        "prerequisite_checks": {
            "phase_1_toon_infrastructure": {
                "requirement": "TOON parser and compiler from Phase 1 must be complete",
                "verification": "Confirm tools/toon/compiler.py exists and test_toon_parser passes",
                "blocking": True,
                "escalation": "If Phase 1 incomplete, STOP - escalate to project manager for decision on Option B (Markdown) or Option C (Block)"
            },
            "toon_format_specification": {
                "requirement": "TOON v3.0 format specification must be available",
                "verification": "Obtain from tools/toon/TOON-v3.0-SPEC.md or reference implementation",
                "blocking": True,
                "escalation": "If spec unavailable, create from reverse-engineering agents/novel-editor-chatgpt-toon.txt"
            },
            "baseline_measurements": {
                "requirement": "Baseline measurements from Phase 0 must be complete",
                "verification": "Confirm docs/workflow/plugin-marketplace-migration/baseline.yaml exists with command metrics",
                "blocking": True,
                "escalation": "If baseline missing, execute Phase 0 baseline measurement first"
            }
        }
    }

def get_phase4_toon_compiler_spec() -> Dict[str, Any]:
    """Get TOON compiler specification for Phase 4."""
    return {
        "toon_compiler": {
            "tool_location": "tools/toon/compiler.py (from Phase 1)",
            "purpose": "Transforms TOON source to Claude Code compliant output",
            "input": "5d-wave/tasks/dw/*.toon (TOON format)",
            "output": "dist/commands/dw/*.md (Markdown format)",
            "invocation": "python tools/toon/compiler.py <input.toon> --validate --output <output.md>",
            "success_criteria": [
                "Exit code = 0 (no errors)",
                "No errors in stderr",
                "Output file size > 1000 bytes (non-trivial content)",
                "Metadata validates against TOON v3.0 schema",
                "Output markdown is Claude Code compliant"
            ],
            "validation": "pytest tests/tools/toon/test_compiler.py"
        }
    }

def get_phase4_error_handling() -> Dict[str, Any]:
    """Get error handling section for Phase 4."""
    return {
        "error_handling": {
            "scenario_1_compiler_not_found": {
                "error": "TOON compiler not found at tools/toon/compiler.py",
                "handling": "Log error with clear message: 'Phase 1 TOON infrastructure required. Run Phase 1.1-1.5 first or choose Option B (Markdown).'",
                "recovery": "STOP execution, escalate to user for decision",
                "test": "test_error_compiler_not_found"
            },
            "scenario_2_compilation_failure": {
                "error": "TOON compiler exits with non-zero code",
                "handling": "Log compilation error with file path and stderr output. Skip failed file, continue with others. Generate error report.",
                "recovery": "Review TOON syntax, fix errors, retry compilation",
                "test": "test_error_compilation_failure_graceful"
            },
            "scenario_3_metadata_validation_failure": {
                "error": "Compiled output fails metadata validation (missing required fields)",
                "handling": "Log validation errors with specific missing fields. Mark file as failed. Continue processing other files.",
                "recovery": "Add missing metadata to source TOON file, recompile",
                "test": "test_error_metadata_validation_failure"
            },
            "scenario_4_partial_batch_failure": {
                "error": "Some files in batch succeed, others fail",
                "handling": "Complete all processable files. Generate summary report: X succeeded, Y failed. List failed files with error reasons.",
                "recovery": "Fix failed files individually, rerun batch",
                "test": "test_error_partial_batch_failure_reporting"
            }
        }
    }

def get_phase4_test_specifications() -> Dict[str, Any]:
    """Get detailed test specifications for Phase 4."""
    return {
        "test_specifications": {
            "unit_tests": [
                {
                    "name": "test_toon_parser_valid_command_input",
                    "purpose": "Verify parser handles valid TOON command syntax correctly",
                    "input": "Sample TOON command file with all required fields (name, description, parameters)",
                    "expected": "Parsed dict with command metadata: {name, description, parameters, dependencies}"
                },
                {
                    "name": "test_template_rendering_with_parsed_command",
                    "purpose": "Verify Jinja2 template renders command.md from parsed data",
                    "input": "Parsed command dict from parser output",
                    "expected": "Valid Markdown output with command syntax section, parameters table, usage examples"
                },
                {
                    "name": "test_output_validation_against_claude_code_spec",
                    "purpose": "Verify compiled output meets Claude Code command specification",
                    "input": "Generated command.md file",
                    "expected": "Validation passes: Has frontmatter, execution context, success criteria sections"
                }
            ],
            "integration_tests": [
                {
                    "name": "test_e2e_command_migration_pipeline",
                    "purpose": "Verify complete migration: TOON → Parse → Template → Validate → Output",
                    "input": "Real TOON command file from 5d-wave/tasks/dw/",
                    "steps": "Parse TOON → Apply command template → Validate output → Write to dist/",
                    "expected": "Valid command.md in dist/commands/dw/ matching Claude Code spec"
                },
                {
                    "name": "test_batch_migration_all_commands",
                    "purpose": "Verify batch processing of all command files",
                    "input": "All TOON command files (8 dw: commands)",
                    "expected": "All 8 commands migrated successfully with validation report"
                }
            ],
            "error_scenario_tests": [
                {
                    "name": "test_compiler_not_found_error_handling",
                    "purpose": "Verify graceful failure when compiler missing",
                    "setup": "Remove or rename tools/toon/compiler.py",
                    "expected": "Clear error message, execution stops, no partial output"
                },
                {
                    "name": "test_malformed_toon_syntax_error_handling",
                    "purpose": "Verify parser reports syntax errors clearly",
                    "input": "TOON file with missing ## section header",
                    "expected": "Parser error with line number, specific syntax issue description"
                },
                {
                    "name": "test_validation_failure_error_handling",
                    "purpose": "Verify validation errors reported clearly",
                    "input": "TOON file missing required 'description' field",
                    "expected": "Validation error: 'Missing required field: description' with file path"
                }
            ]
        }
    }

def apply_phase4_corrections(step_file: Path, step_id: str) -> None:
    """Apply all Phase 4 corrections to a step file."""
    with open(step_file) as f:
        data = json.load(f)

    # 1. Add prerequisite checks
    prereq = get_phase4_prerequisite_checks()
    data = deep_merge(data, prereq)

    # 2. Add TOON compiler spec
    compiler = get_phase4_toon_compiler_spec()
    data = deep_merge(data, compiler)

    # 3. Add error handling
    errors = get_phase4_error_handling()
    data = deep_merge(data, errors)

    # 4. Add test specifications
    tests = get_phase4_test_specifications()
    data = deep_merge(data, tests)

    # 5. Update time estimates
    time_estimates = {
        "04-01": "4-6",
        "04-01b": "2-3",  # Keep existing
        "04-02": "3-4",
        "04-03": "3-4",
        "04-04": "8-12",
        "04-05": "3-4",
        "04-06": "4-6"
    }

    if step_id in time_estimates:
        data["step"]["estimated_hours"] = time_estimates[step_id]

    # 6. Step-specific additions
    if step_id == "04-04":
        # Add agent bindings table
        data["agent_bindings"] = {
            "description": "Maps each DEVELOP wave command to its primary agent",
            "bindings": {
                "dw:baseline": "software-crafter",
                "dw:roadmap": "software-crafter",
                "dw:split": "software-crafter",
                "dw:execute": "software-crafter",
                "dw:review": "software-crafter-reviewer",
                "dw:develop": "software-crafter",
                "dw:refactor": "software-crafter",
                "dw:mikado": "software-crafter"
            },
            "validation": "Each binding MUST have test validating command invokes correct agent"
        }

    if step_id == "04-05":
        # Add finalize complexity tests
        if "test_specifications" in data:
            data["test_specifications"]["finalize_complexity_tests"] = [
                {
                    "name": "test_finalize_parameter_parsing",
                    "purpose": "Verify finalize command parses all parameters correctly",
                    "input": "Command with multiple parameters (--project, --phase, --output)",
                    "expected": "All parameters parsed, validated, and accessible"
                },
                {
                    "name": "test_finalize_agent_validation",
                    "purpose": "Verify finalize validates agent bindings completeness",
                    "input": "Command bindings for 8 dw: commands",
                    "expected": "Validation passes: All commands have agent bindings"
                },
                {
                    "name": "test_finalize_error_handling",
                    "purpose": "Verify finalize handles missing dependencies gracefully",
                    "input": "Finalize attempt with missing prerequisite (baseline.yaml)",
                    "expected": "Clear error: 'Missing prerequisite: baseline.yaml'"
                },
                {
                    "name": "test_finalize_metadata_preservation",
                    "purpose": "Verify finalize preserves all command metadata during processing",
                    "input": "Command with rich metadata (tags, dependencies, examples)",
                    "expected": "Output preserves all metadata fields without loss"
                }
            ]

    if step_id == "04-06":
        # Remove SC7 from acceptance criteria, add note
        if "deliverables" in data and "acceptance_criteria" in data["deliverables"]:
            # Remove any SC7 references
            ac = data["deliverables"]["acceptance_criteria"]
            data["deliverables"]["acceptance_criteria"] = [
                criterion for criterion in ac if "SC7" not in criterion and "60%" not in criterion
            ]
            # Add deferral note
            data["deliverables"]["acceptance_criteria"].append(
                "Token savings validation: Deferred to Phase 8 final validation (not measured in this step)"
            )

    with open(step_file, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    """Apply Phase 4 corrections to all 7 command migration steps."""
    base_path = Path("/mnt/c/Repositories/Projects/ai-craft/docs/workflow/plugin-marketplace-migration/steps")

    print("Applying Phase 4 Command Migration corrections...")
    print()

    step_ids = ["04-01", "04-01b", "04-02", "04-03", "04-04", "04-05", "04-06"]

    for step_id in step_ids:
        filename = f"{step_id}.json"
        step_file = base_path / filename

        if not step_file.exists():
            print(f"⚠️  {filename} not found, skipping...")
            continue

        print(f"📝 Processing {filename}...")
        try:
            apply_phase4_corrections(step_file, step_id)

            # Validate JSON
            with open(step_file) as f:
                json.load(f)

            print(f"   ✅ Corrections applied and validated")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    print()
    print("Phase 4 corrections application complete!")
    print("All 7 step files updated with:")
    print("  • Prerequisite checks (Phase 1, TOON spec, baseline)")
    print("  • TOON compiler specification")
    print("  • Error handling (4 scenarios)")
    print("  • Test specifications (unit, integration, error)")
    print("  • Updated time estimates")
    print("  • Step-specific additions (agent bindings, finalize tests, SC7 removal)")

if __name__ == "__main__":
    main()
