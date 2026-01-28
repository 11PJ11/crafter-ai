#!/usr/bin/env python3
"""
Template Integrity Tests

Ensures the TDD cycle template embedded in split.md matches
the canonical source in step-tdd-cycle-schema.json.

These tests prevent drift between the template used by /nw:split
and the validators, which would cause format mismatches.
"""

import json
import re
import sys
from pathlib import Path

import pytest

# Add project root to path for importing from scripts.validation
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

CANONICAL_TEMPLATE = REPO_ROOT / "nWave/templates/step-tdd-cycle-schema.json"
SPLIT_MD = REPO_ROOT / "nWave/tasks/nw/split.md"


class TestCanonicalTemplateValidity:
    """Verify the canonical template is valid and complete."""

    @pytest.fixture
    def canonical_template(self) -> dict:
        """Load the canonical template."""
        with open(CANONICAL_TEMPLATE, encoding="utf-8") as f:
            return json.load(f)

    def test_canonical_template_exists(self):
        """Canonical template file must exist."""
        assert CANONICAL_TEMPLATE.exists(), (
            f"Canonical template not found: {CANONICAL_TEMPLATE}"
        )

    def test_canonical_template_is_valid_json(self, canonical_template):
        """Canonical template must be valid JSON."""
        assert isinstance(canonical_template, dict)
        assert "tdd_cycle" in canonical_template

    def test_canonical_has_8_phases(self, canonical_template):
        """Canonical template must have exactly 8 phases (schema v2.0)."""
        from nWave.constants.tdd_phases import PHASE_COUNT
        phases = canonical_template.get("tdd_cycle", {}).get("phase_execution_log", [])
        assert len(phases) == PHASE_COUNT, f"Expected {PHASE_COUNT} phases, found {len(phases)}"

    def test_canonical_phase_names_match_validator(self, canonical_template):
        """Phase names in template must match validator constants."""
        from scripts.validation.validate_steps import REQUIRED_PHASES

        template_phases = [
            p["phase_name"]
            for p in canonical_template.get("tdd_cycle", {}).get(
                "phase_execution_log", []
            )
        ]

        assert template_phases == REQUIRED_PHASES, (
            f"Template phases don't match validator.\n"
            f"Template: {template_phases}\n"
            f"Validator: {REQUIRED_PHASES}"
        )

    def test_canonical_phases_use_uppercase_underscore(self, canonical_template):
        """All phase names must use UPPERCASE_UNDERSCORE format."""
        phases = canonical_template.get("tdd_cycle", {}).get("phase_execution_log", [])

        for phase in phases:
            phase_name = phase.get("phase_name", "")
            # Must be uppercase
            assert phase_name == phase_name.upper(), (
                f"Phase name not uppercase: {phase_name}"
            )
            # Must not contain parentheses
            assert "(" not in phase_name and ")" not in phase_name, (
                f"Phase name contains parentheses: {phase_name}"
            )
            # Must use underscores (if multi-word)
            if len(phase_name) > 10:  # Multi-word phases
                assert "_" in phase_name or phase_name in [
                    "PREPARE",
                    "REVIEW",
                    "COMMIT",
                ], f"Multi-word phase should use underscore: {phase_name}"

    def test_canonical_has_required_sections(self, canonical_template):
        """Canonical template must have all required sections."""
        required_sections = [
            "tdd_cycle",
            "quality_gates",
            "phase_validation_rules",
        ]
        for section in required_sections:
            assert section in canonical_template, f"Missing required section: {section}"

    def test_canonical_phase_indices_sequential(self, canonical_template):
        """Phase indices must be sequential 0-7 (schema v2.0)."""
        phases = canonical_template.get("tdd_cycle", {}).get("phase_execution_log", [])

        for i, phase in enumerate(phases):
            assert phase.get("phase_index") == i, (
                f"Phase {phase.get('phase_name')} has wrong index: "
                f"expected {i}, got {phase.get('phase_index')}"
            )


class TestSplitMdEmbeddedTemplate:
    """Verify split.md doesn't contain wrong phase names."""

    @pytest.fixture
    def split_md_content(self) -> str:
        """Load split.md content."""
        return SPLIT_MD.read_text(encoding="utf-8")

    def test_split_md_exists(self):
        """split.md must exist."""
        assert SPLIT_MD.exists(), f"split.md not found: {SPLIT_MD}"

    def test_no_wrong_phase_names_in_json_context(self, split_md_content):
        """split.md must not use wrong phase names in JSON phase_name fields."""
        # These patterns detect wrong phase names used as actual JSON values
        # (not documentation about what's wrong)
        wrong_json_patterns = [
            r'"phase_name":\s*"RED \(Acceptance\)"',
            r'"phase_name":\s*"RED \(Unit\)"',
            r'"phase_name":\s*"GREEN \(Unit\)"',
            r'"phase_name":\s*"GREEN \(Acceptance\)"',
            r'"phase_name":\s*"CHECK"[^_]',  # CHECK without _ACCEPTANCE
            r'"phase_name":\s*"REFACTOR L\d"',  # Space instead of underscore
            r'"phase_name":\s*"POST-REFACTOR REVIEW"',
            r'"phase_name":\s*"FINAL VALIDATE"',
        ]

        for pattern in wrong_json_patterns:
            matches = re.findall(pattern, split_md_content)
            assert not matches, (
                f"split.md contains wrong phase name in JSON context: {matches}. "
                f"Should use underscore format (e.g., 'RED_ACCEPTANCE')"
            )

    def test_split_md_references_correct_phases(self, split_md_content):
        """split.md must reference correct phase names in examples."""
        from scripts.validation.validate_steps import REQUIRED_PHASES

        # Extract phase_name values from embedded JSON
        pattern = r'"phase_name":\s*"([A-Z_]+)"'
        matches = re.findall(pattern, split_md_content)

        if matches:
            # All found phase names should be valid
            invalid = set(matches) - set(REQUIRED_PHASES) - {"NOT_STARTED", "COMPLETED"}
            assert not invalid, (
                f"Invalid phase names found in split.md: {invalid}\n"
                f"Valid names are: {REQUIRED_PHASES}"
            )

    def test_split_md_has_format_validation_section(self, split_md_content):
        """split.md must have FORMAT VALIDATION section."""
        assert "FORMAT VALIDATION" in split_md_content, (
            "split.md missing FORMAT VALIDATION section"
        )

    def test_split_md_documents_wrong_patterns(self, split_md_content):
        """split.md must document rejection of wrong patterns."""
        required_rejections = [
            "step_id",  # Wrong field name
            "phase_id",  # Wrong field name
        ]

        for pattern in required_rejections:
            assert pattern in split_md_content, (
                f"split.md should document rejection of '{pattern}'"
            )

    def test_split_md_references_single_source_of_truth(self, split_md_content):
        """split.md must reference the canonical schema file."""
        assert "step-tdd-cycle-schema.json" in split_md_content, (
            "split.md should reference step-tdd-cycle-schema.json as source of truth"
        )


class TestValidatorSchemaAlignment:
    """Verify validator constants match the canonical template."""

    def test_validator_phases_count(self):
        """Validator must define exactly 8 phases (schema v2.0)."""
        from scripts.validation.validate_steps import REQUIRED_PHASES
        from nWave.constants.tdd_phases import PHASE_COUNT

        assert len(REQUIRED_PHASES) == PHASE_COUNT, (
            f"Validator should have {PHASE_COUNT} phases, has {len(REQUIRED_PHASES)}"
        )

    def test_validator_phases_uppercase_underscore(self):
        """Validator phase names must use UPPERCASE_UNDERSCORE format."""
        from scripts.validation.validate_steps import REQUIRED_PHASES

        for phase in REQUIRED_PHASES:
            assert phase == phase.upper(), f"Phase not uppercase: {phase}"
            assert "(" not in phase, f"Phase contains parentheses: {phase}"
            assert " " not in phase, f"Phase contains spaces: {phase}"

    def test_validator_required_fields_correct(self):
        """Validator must require correct fields."""
        from scripts.validation.validate_steps import REQUIRED_FIELDS

        # Must require task_id
        assert "task_id" in REQUIRED_FIELDS, "Validator must require task_id"

        # Must NOT require step_id or phase_id
        assert "step_id" not in REQUIRED_FIELDS, "Validator should not require step_id"
        assert "phase_id" not in REQUIRED_FIELDS, (
            "Validator should not require phase_id"
        )


class TestCrossFileConsistency:
    """Verify consistency across all related files."""

    def test_template_and_validator_in_sync(self):
        """Template phases must match validator phases exactly."""
        from scripts.validation.validate_steps import REQUIRED_PHASES

        with open(CANONICAL_TEMPLATE, encoding="utf-8") as f:
            template = json.load(f)

        template_phases = [
            p["phase_name"]
            for p in template.get("tdd_cycle", {}).get("phase_execution_log", [])
        ]

        assert template_phases == REQUIRED_PHASES, (
            "Template and validator are out of sync!\n"
            f"Template: {template_phases}\n"
            f"Validator: {REQUIRED_PHASES}\n"
            "Update one to match the other."
        )

    def test_mandatory_phases_list_matches(self):
        """mandatory_phases in template must use correct phase names."""
        from scripts.validation.validate_steps import REQUIRED_PHASES

        with open(CANONICAL_TEMPLATE, encoding="utf-8") as f:
            template = json.load(f)

        mandatory_phases = template.get("task_specification", {}).get(
            "mandatory_phases", []
        )

        # Each entry should start with a valid phase name
        for entry in mandatory_phases:
            # Extract phase name (before the " - " description)
            phase_name = entry.split(" - ")[0].strip()
            assert phase_name in REQUIRED_PHASES, (
                f"Invalid phase in mandatory_phases: '{phase_name}'\n"
                f"Valid phases: {REQUIRED_PHASES}"
            )
