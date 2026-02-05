"""
Test that execute.md TDD phases stay in sync with validator source of truth.

This test ensures the execute.md template uses the canonical TDD phases
from TDDPhaseValidator.MANDATORY_PHASES_V3 without drift.

Business Value:
- Prevents execute.md from getting out of sync with validator
- Single source of truth for TDD phases (TDDPhaseValidator)
- Fails fast when template needs updating
"""

import re

from src.des.application.validator import TDDPhaseValidator


class TestExecuteTemplateSync:
    """Verify execute.md TDD phases match validator source of truth."""

    def test_execute_md_uses_canonical_v3_phases(self):
        """
        GIVEN execute.md template file
        WHEN we extract the TDD_7_PHASES section
        THEN the phases MUST match TDDPhaseValidator.MANDATORY_PHASES exactly

        Source of Truth: TDDPhaseValidator.MANDATORY_PHASES (from schema v3.0)
        Template File: nWave/tasks/nw/execute.md

        This test prevents drift between template and validator.
        """
        # Arrange: Get canonical phases from validator (single source of truth)
        validator = TDDPhaseValidator()
        canonical_phases = validator.MANDATORY_PHASES

        # Act: Read execute.md and extract TDD phases
        with open("nWave/tasks/nw/execute.md") as f:
            content = f.read()

        # Extract phase names from execute.md
        # Pattern: "0. PREPARE", "1. RED_ACCEPTANCE", etc.
        phase_pattern = r"^\d+\.\s+([A-Z_]+)\s+-"
        extracted_phases = []

        # Find TDD_7_PHASES section
        tdd_section_start = content.find("# TDD_7_PHASES")
        assert tdd_section_start != -1, "TDD_7_PHASES section not found in execute.md"

        # Extract next ~15 lines after TDD_7_PHASES
        lines = content[tdd_section_start:].split("\n")[:15]

        for line in lines:
            match = re.match(phase_pattern, line)
            if match:
                extracted_phases.append(match.group(1))

        # Convert list to tuple for comparison with schema (which returns tuple)
        extracted_phases = tuple(extracted_phases)

        # Assert: Phases match canonical source exactly
        assert extracted_phases == canonical_phases, f"""
execute.md TDD phases do NOT match validator source of truth!

Expected (from TDDPhaseValidator.MANDATORY_PHASES - schema v3.0):
{canonical_phases}

Found in execute.md:
{extracted_phases}

ACTION REQUIRED:
Update nWave/tasks/nw/execute.md TDD_7_PHASES section to match
TDDPhaseValidator.MANDATORY_PHASES (loaded from step-tdd-cycle-schema.json).

The validator is the single source of truth.
"""

    def test_execute_md_declares_schema_v3(self):
        """
        GIVEN execute.md template
        WHEN we check the TDD_7_PHASES section comment
        THEN it MUST declare Schema v3.0 and reference TDDPhaseValidator

        This ensures future maintainers know where the canonical phases live.
        """
        with open("nWave/tasks/nw/execute.md") as f:
            content = f.read()

        # Find TDD_7_PHASES section
        tdd_section_start = content.find("# TDD_7_PHASES")
        assert tdd_section_start != -1, "TDD_7_PHASES section not found"

        # Get next 5 lines
        section = content[tdd_section_start : tdd_section_start + 300]

        # Verify schema declaration
        assert "Schema v3.0" in section, (
            "execute.md must declare 'Schema v3.0' in TDD_7_PHASES section"
        )

        assert "TDDPhaseValidator.MANDATORY_PHASES_V3" in section, (
            "execute.md must reference TDDPhaseValidator.MANDATORY_PHASES_V3 as source of truth"
        )
