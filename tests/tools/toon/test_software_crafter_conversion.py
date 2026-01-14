"""Tests for software-crafter.md to TOON conversion validation

Step 02-01 acceptance criteria validation:
- TOON file contains all agent metadata
- TOON file contains all commands with descriptions
- TOON file contains all dependencies with paths
- TOON file contains embedded knowledge markers (BUILD:INJECT sections)
- TOON file follows v3.0 syntax (validated by compiler)
- Token baseline captured with required fields
"""

import json
import os
import tempfile
from pathlib import Path

import pytest

from tools.toon.compiler import compile_toon
from tools.toon.parser import TOONParser

# Test constants
TOON_FILE = Path("nWave/agents/software-crafter.toon")
ORIGINAL_MD = Path("nWave/agents/software-crafter.md")
BASELINE_FILE = Path("baseline/token-measurements/02-01-pre-conversion.json")

# Expected commands from original software-crafter.md
EXPECTED_COMMANDS = [
    "help",
    "develop",
    "implement-story",
    "validate-production",
    "mikado",
    "explore",
    "define-goal",
    "create-tree",
    "track-discovery",
    "execute-leaves",
    "refactor",
    "detect-smells",
    "progressive",
    "atomic-transform",
    "check-quality-gates",
    "commit-ready",
    "quality-metrics",
    "commit-transformation",
    "capture-golden-master",
    "detect-silent-failures",
    "validate-edge-cases",
    "document-api-assumptions",
    "audit-test-data",
    "tdd-to-refactor",
    "mikado-to-systematic",
    "handoff-demo",
    "exit",
]

# Expected dependencies from original
EXPECTED_TASKS = [
    "dw/develop.md",
    "dw/mikado.md",
    "dw/refactor.md",
]

EXPECTED_EMBED_PATHS = [
    "nWave/data/embed/software-crafter/README.md",
    "nWave/data/embed/software-crafter/mikado-method-progressive-refactoring.md",
    "nWave/data/embed/software-crafter/outside-in-tdd-methodology.md",
    "nWave/data/embed/software-crafter/property-based-mutation-testing.md",
    "nWave/data/embed/software-crafter/refactoring-patterns-catalog.md",
]


class TestTOONFileExists:
    """Verify TOON file was created"""

    def test_toon_file_exists(self):
        assert TOON_FILE.exists(), f"TOON file not found: {TOON_FILE}"

    def test_original_md_preserved(self):
        """Original .md file kept for comparison until Phase 8"""
        assert ORIGINAL_MD.exists(), f"Original MD file should be preserved: {ORIGINAL_MD}"


class TestTOONMetadata:
    """Verify all agent metadata is present in TOON"""

    @pytest.fixture
    def parsed_toon(self):
        parser = TOONParser()
        with open(TOON_FILE, "r") as f:
            return parser.parse(f.read())

    def test_toon_has_agent_id(self, parsed_toon):
        assert parsed_toon["id"] == "software-crafter"

    def test_toon_has_agent_type(self, parsed_toon):
        assert parsed_toon["type"] == "agent"

    def test_toon_has_version(self, parsed_toon):
        assert parsed_toon["toon_version"] == "v3.0"

    def test_toon_has_name_in_metadata(self, parsed_toon):
        assert "name" in parsed_toon["metadata"]
        assert parsed_toon["metadata"]["name"] == "Crafty"

    def test_toon_has_model_in_metadata(self, parsed_toon):
        assert "model" in parsed_toon["metadata"]
        assert parsed_toon["metadata"]["model"] == "inherit"

    def test_toon_has_role_in_metadata(self, parsed_toon):
        assert "role" in parsed_toon["metadata"]
        assert "software-crafter" in parsed_toon["metadata"]["role"]


class TestTOONCommands:
    """Verify all commands are present in TOON"""

    @pytest.fixture
    def toon_content(self):
        with open(TOON_FILE, "r") as f:
            return f.read()

    @pytest.fixture
    def parsed_toon(self, toon_content):
        parser = TOONParser()
        return parser.parse(toon_content)

    def test_commands_section_exists(self, parsed_toon):
        assert "commands" in parsed_toon["sections"]

    def test_all_commands_present(self, toon_content):
        """Verify each expected command is in the TOON file"""
        for command in EXPECTED_COMMANDS:
            assert (
                command in toon_content.lower()
            ), f"Command '{command}' missing from TOON"

    def test_help_command_present(self, toon_content):
        assert "- help:" in toon_content

    def test_develop_command_present(self, toon_content):
        assert "- develop:" in toon_content

    def test_mikado_command_present(self, toon_content):
        assert "- mikado:" in toon_content

    def test_refactor_command_present(self, toon_content):
        assert "- refactor:" in toon_content


class TestTOONDependencies:
    """Verify all dependencies are present in TOON"""

    @pytest.fixture
    def toon_content(self):
        with open(TOON_FILE, "r") as f:
            return f.read()

    @pytest.fixture
    def parsed_toon(self, toon_content):
        parser = TOONParser()
        return parser.parse(toon_content)

    def test_dependencies_section_exists(self, parsed_toon):
        assert "dependencies" in parsed_toon["sections"]

    def test_tasks_dependencies_present(self, toon_content):
        """Verify task dependencies are listed"""
        for task in EXPECTED_TASKS:
            assert task in toon_content, f"Task dependency '{task}' missing from TOON"

    def test_embed_knowledge_dependencies_present(self, toon_content):
        """Verify embed_knowledge paths are listed"""
        for path in EXPECTED_EMBED_PATHS:
            assert path in toon_content, f"Embed knowledge path '{path}' missing from TOON"


class TestTOONEmbeddedKnowledgeMarkers:
    """Verify BUILD:INJECT markers are preserved"""

    @pytest.fixture
    def toon_content(self):
        with open(TOON_FILE, "r") as f:
            return f.read()

    def test_build_inject_start_markers_present(self, toon_content):
        """Verify BUILD:INJECT:START markers are preserved"""
        assert "BUILD:INJECT:START" in toon_content

    def test_build_inject_end_markers_present(self, toon_content):
        """Verify BUILD:INJECT:END markers are preserved"""
        assert "BUILD:INJECT:END" in toon_content

    def test_readme_inject_marker_present(self, toon_content):
        assert "BUILD:INJECT:START:nWave/data/embed/software-crafter/README.md" in toon_content

    def test_mikado_inject_marker_present(self, toon_content):
        assert (
            "BUILD:INJECT:START:nWave/data/embed/software-crafter/mikado-method-progressive-refactoring.md"
            in toon_content
        )

    def test_tdd_inject_marker_present(self, toon_content):
        assert (
            "BUILD:INJECT:START:nWave/data/embed/software-crafter/outside-in-tdd-methodology.md"
            in toon_content
        )

    def test_inject_markers_count(self, toon_content):
        """Verify expected number of BUILD:INJECT pairs"""
        start_count = toon_content.count("BUILD:INJECT:START")
        end_count = toon_content.count("BUILD:INJECT:END")
        assert start_count >= 5, f"Expected at least 5 START markers, found {start_count}"
        assert start_count == end_count, f"Mismatched START ({start_count}) and END ({end_count}) markers"


class TestTOONCompilerAccepts:
    """Verify compiler accepts TOON syntax"""

    def test_compiler_accepts_toon_file(self):
        """TOON file compiles without errors"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Should not raise exception
            compile_toon(str(TOON_FILE), tmpdir)

            # Should produce output file
            output_files = list(Path(tmpdir).glob("*.md"))
            assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"

    def test_compiled_output_has_frontmatter(self):
        """Compiled output has YAML frontmatter"""
        with tempfile.TemporaryDirectory() as tmpdir:
            compile_toon(str(TOON_FILE), tmpdir)
            output_file = list(Path(tmpdir).glob("*.md"))[0]

            with open(output_file, "r") as f:
                content = f.read()

            assert content.startswith("---") or content.startswith("\n---")

    def test_compiled_output_has_name(self):
        """Compiled output includes agent name"""
        with tempfile.TemporaryDirectory() as tmpdir:
            compile_toon(str(TOON_FILE), tmpdir)
            output_file = list(Path(tmpdir).glob("*.md"))[0]

            with open(output_file, "r") as f:
                content = f.read()

            assert "name:" in content
            assert "software-crafter" in content.lower()


class TestTokenBaseline:
    """Verify token baseline was captured correctly"""

    def test_baseline_file_exists(self):
        assert BASELINE_FILE.exists(), f"Token baseline file not found: {BASELINE_FILE}"

    def test_baseline_has_required_fields(self):
        """Verify baseline has all required fields per step specification"""
        with open(BASELINE_FILE, "r") as f:
            baseline = json.load(f)

        required_fields = [
            "step_id",
            "file_path",
            "measurement_date",
            "tokenizer",
            "total_tokens",
            "file_size_bytes",
            "line_count",
        ]

        for field in required_fields:
            assert field in baseline, f"Required field '{field}' missing from baseline"

    def test_baseline_step_id_correct(self):
        with open(BASELINE_FILE, "r") as f:
            baseline = json.load(f)

        assert baseline["step_id"] == "02-01"

    def test_baseline_file_path_correct(self):
        with open(BASELINE_FILE, "r") as f:
            baseline = json.load(f)

        assert baseline["file_path"] == "nWave/agents/software-crafter.md"

    def test_baseline_tokenizer_correct(self):
        with open(BASELINE_FILE, "r") as f:
            baseline = json.load(f)

        assert baseline["tokenizer"] == "tiktoken/cl100k_base"

    def test_baseline_total_tokens_positive(self):
        with open(BASELINE_FILE, "r") as f:
            baseline = json.load(f)

        assert baseline["total_tokens"] > 0
        # software-crafter.md is large, should have significant tokens
        assert baseline["total_tokens"] > 20000, "Expected > 20k tokens for software-crafter.md"

    def test_baseline_file_size_positive(self):
        with open(BASELINE_FILE, "r") as f:
            baseline = json.load(f)

        assert baseline["file_size_bytes"] > 0

    def test_baseline_line_count_positive(self):
        with open(BASELINE_FILE, "r") as f:
            baseline = json.load(f)

        assert baseline["line_count"] > 0
        # software-crafter.md has many lines
        assert baseline["line_count"] > 2000, "Expected > 2000 lines for software-crafter.md"

    def test_baseline_measurement_date_iso_format(self):
        with open(BASELINE_FILE, "r") as f:
            baseline = json.load(f)

        # Should be ISO format like 2026-01-14T08:39:10.249079Z
        date = baseline["measurement_date"]
        assert "T" in date, "Measurement date should be ISO-8601 format"
        assert date.endswith("Z"), "Measurement date should end with Z (UTC)"


class TestTOONCompleteness:
    """Verify TOON captures key knowledge sections"""

    @pytest.fixture
    def toon_content(self):
        with open(TOON_FILE, "r") as f:
            return f.read()

    def test_11_phase_tdd_preserved(self, toon_content):
        """11-phase TDD methodology is captured"""
        assert "11_PHASE_TDD" in toon_content or "11-PHASE" in toon_content

    def test_mikado_methodology_preserved(self, toon_content):
        """Mikado methodology is captured"""
        assert "MIKADO" in toon_content.upper()

    def test_progressive_refactoring_preserved(self, toon_content):
        """Progressive refactoring levels are captured"""
        assert "PROGRESSIVE_REFACTORING" in toon_content or "Level 1" in toon_content

    def test_code_smells_preserved(self, toon_content):
        """Code smell taxonomy is captured"""
        assert "CODE_SMELL" in toon_content.upper() or "Bloaters" in toon_content

    def test_quality_framework_preserved(self, toon_content):
        """Quality framework is captured"""
        assert "QUALITY_FRAMEWORK" in toon_content or "100% required" in toon_content

    def test_collaboration_preserved(self, toon_content):
        """Collaboration patterns are captured"""
        assert "COLLABORATION" in toon_content or "acceptance_designer" in toon_content

    def test_hexagonal_architecture_preserved(self, toon_content):
        """Hexagonal architecture is mentioned"""
        assert "hexagonal" in toon_content.lower() or "ports" in toon_content.lower()
