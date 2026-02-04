"""
Acceptance tests for two-tier DES validation (orchestrator vs execution mode).

This test suite verifies the Hybrid Approach (1 + 3) implementation where:
- Execution tasks (/nw:execute) require full 8-section DES validation
- Orchestrator tasks (/nw:develop) use relaxed validation with DES-MODE: orchestrator

Business Value:
- Execution tasks get full validation for quality assurance
- Orchestrator tasks avoid verbose 8-section format (maintainability)
- Clear distinction via explicit DES-MODE marker
"""

import json
from io import StringIO
from unittest.mock import patch

from src.des.application.validator import TDDPhaseValidator


class TestTwoTierValidation:
    """
    Test suite for two-tier DES validation system.

    Scenarios:
    1. Execution mode (no DES-MODE marker) - requires all 8 sections
    2. Orchestrator mode (DES-MODE: orchestrator) - relaxed validation
    3. max_turns validation applies to both modes
    """

    def test_execution_mode_requires_all_8_sections(self):
        """
        GIVEN Task invocation with DES-VALIDATION marker but NO DES-MODE marker
        WHEN PreToolUse hook processes the invocation
        THEN hook performs full validation requiring all 8 mandatory sections
        AND blocks if sections are missing

        Mode: EXECUTION (default when DES-MODE marker absent)
        Expected: Strict validation with 8 mandatory sections
        """
        hook_input = {
            "tool": "Task",
            "tool_input": {
                "subagent_type": "software-crafter",
                "max_turns": 30,
                "prompt": """<!-- DES-VALIDATION: required -->
<!-- DES-STEP-FILE: docs/feature/test-project/steps/01-01.json -->
<!-- DES-ORIGIN: command:/nw:execute -->

You are a software crafter.

# TASK_CONTEXT
Implement feature X

# TDD_7_PHASES
All 7 phases listed

# Missing: QUALITY_GATES, OUTCOME_RECORDING, BOUNDARY_RULES, TIMEOUT_INSTRUCTION, DES_METADATA, AGENT_IDENTITY
""",
            },
        }

        # Act: Invoke hook
        exit_code, stdout, _stderr = self._invoke_hook(
            "pre-task", json.dumps(hook_input)
        )

        # Assert: Hook blocks due to missing mandatory sections
        assert exit_code == 2, "Hook should block when mandatory sections missing"
        response = json.loads(stdout)
        assert response["decision"] == "block"
        assert "MISSING: Mandatory section" in response["reason"]

    def test_orchestrator_mode_allows_simplified_format(self):
        """
        GIVEN Task invocation with DES-MODE: orchestrator marker
        WHEN PreToolUse hook processes the invocation
        THEN hook allows invocation WITHOUT requiring 8 mandatory sections
        AND only validates max_turns parameter

        Mode: ORCHESTRATOR (explicit via DES-MODE: orchestrator)
        Expected: Relaxed validation - no 8-section requirement
        """
        hook_input = {
            "tool": "Task",
            "tool_input": {
                "subagent_type": "researcher",
                "max_turns": 35,
                "prompt": """<!-- DES-VALIDATION: required -->
<!-- DES-MODE: orchestrator -->
<!-- DES-STEP-FILE: docs/feature/test-project/baseline.yaml -->
<!-- DES-ORIGIN: command:/nw:develop -->

You are a researcher creating a baseline.

YOUR TASK: Create baseline.yaml measurement file.

# Only basic sections needed, not all 8 mandatory sections
""",
            },
        }

        # Act: Invoke hook
        exit_code, stdout, _stderr = self._invoke_hook(
            "pre-task", json.dumps(hook_input)
        )

        # Assert: Hook allows orchestrator mode without 8 sections
        assert exit_code == 0, "Hook should allow orchestrator mode"
        response = json.loads(stdout)
        assert response["decision"] == "allow"

    def test_orchestrator_mode_still_requires_max_turns(self):
        """
        GIVEN Task invocation with DES-MODE: orchestrator but NO max_turns
        WHEN PreToolUse hook processes the invocation
        THEN hook BLOCKS due to missing max_turns
        AND provides guidance on max_turns requirement

        Validation Rule: max_turns is UNIVERSAL across all modes
        """
        hook_input = {
            "tool": "Task",
            "tool_input": {
                "subagent_type": "researcher",
                # ❌ MISSING: max_turns parameter
                "prompt": """<!-- DES-VALIDATION: required -->
<!-- DES-MODE: orchestrator -->
<!-- DES-ORIGIN: command:/nw:develop -->

You are a researcher.
""",
            },
        }

        # Act: Invoke hook
        exit_code, stdout, _stderr = self._invoke_hook(
            "pre-task", json.dumps(hook_input)
        )

        # Assert: Hook blocks due to missing max_turns
        assert exit_code == 2, "Hook should block when max_turns missing"
        response = json.loads(stdout)
        assert response["decision"] == "block"
        assert "MISSING_MAX_TURNS" in response["reason"]

    def test_execution_mode_with_all_8_sections_passes(self):
        """
        GIVEN Task invocation in execution mode with ALL 8 mandatory sections
        WHEN PreToolUse hook processes the invocation
        THEN hook ALLOWS invocation

        This verifies that execution mode works when properly formatted.
        """
        # Get canonical TDD phases from single source of truth
        validator = TDDPhaseValidator()
        tdd_phases = ", ".join(validator.MANDATORY_PHASES_V3)

        hook_input = {
            "tool": "Task",
            "tool_input": {
                "subagent_type": "software-crafter",
                "max_turns": 30,
                "prompt": f"""<!-- DES-VALIDATION: required -->
<!-- DES-STEP-FILE: docs/feature/test-project/steps/01-01.json -->
<!-- DES-ORIGIN: command:/nw:execute -->

# DES_METADATA
Step: 01-01.json
Schema: v3.0

# AGENT_IDENTITY
You are a software crafter.

# TASK_CONTEXT
Implement feature X

# TDD_7_PHASES
{tdd_phases}

# QUALITY_GATES
G1: Test active
G2-G6: Defined

# OUTCOME_RECORDING
Update execution-status.yaml

# BOUNDARY_RULES
Scope: feature files only

# TIMEOUT_INSTRUCTION
Target: 30 turns
""",
            },
        }

        # Act: Invoke hook
        exit_code, stdout, _stderr = self._invoke_hook(
            "pre-task", json.dumps(hook_input)
        )

        # Assert: Hook allows properly formatted execution mode task
        assert exit_code == 0, "Hook should allow when all sections present"
        response = json.loads(stdout)
        assert response["decision"] == "allow"

    def test_ad_hoc_task_still_works_without_des_markers(self):
        """
        GIVEN Task invocation WITHOUT any DES markers
        WHEN PreToolUse hook processes the invocation
        THEN hook validates max_turns but skips prompt validation
        AND allows execution

        This ensures backward compatibility with ad-hoc tasks.
        """
        hook_input = {
            "tool": "Task",
            "tool_input": {
                "subagent_type": "Explore",
                "max_turns": 30,
                "prompt": "Find all Python files in src/",
            },
        }

        # Act: Invoke hook
        exit_code, stdout, _stderr = self._invoke_hook(
            "pre-task", json.dumps(hook_input)
        )

        # Assert: Hook allows ad-hoc task
        assert exit_code == 0, "Hook should allow ad-hoc tasks"
        response = json.loads(stdout)
        assert response["decision"] == "allow"

    # Helper methods

    def _invoke_hook(self, command: str, stdin_data: str) -> tuple[int, str, str]:
        """Invoke hook adapter directly with mocked I/O."""
        from src.des.adapters.drivers.hooks.claude_code_hook_adapter import (
            handle_pre_task,
        )

        with patch("sys.stdin", StringIO(stdin_data)):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                exit_code = handle_pre_task()
                stdout = mock_stdout.getvalue()

        return exit_code, stdout, ""
