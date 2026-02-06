"""Integration tests for nWave source directory contract.

These tests validate that EXPECTED_*_COUNT constants match the actual
file counts in the nWave/ source directory. They catch drift when new
agents/commands/templates/scripts are added but constants aren't updated.

Marker: @pytest.mark.integration
"""

import pytest

from crafter_ai.installer.domain.ide_bundle_constants import (
    BUILD_AGENTS_SUBDIR,
    BUILD_COMMANDS_SUBDIR,
    BUILD_SCRIPTS_SUBDIR,
    BUILD_TEMPLATES_SUBDIR,
    DEFAULT_SOURCE_DIR,
    EXPECTED_AGENT_COUNT,
    EXPECTED_COMMAND_COUNT,
    EXPECTED_SCRIPT_COUNT,
    EXPECTED_TEMPLATE_COUNT,
)


@pytest.mark.integration
class TestNWaveSourceContract:
    """Validate constants match actual nWave/ directory contents.

    These tests fail fast when the source directory changes but
    ide_bundle_constants.py is not updated.
    """

    def test_agent_count_matches_nwave_agents_directory(self) -> None:
        """EXPECTED_AGENT_COUNT must match actual nWave/agents/*.md files.

        Counts actual .md files in nWave/agents/ and compares against
        the EXPECTED_AGENT_COUNT constant.

        Fails when: New agent added but constant not updated.
        """
        agents_dir = DEFAULT_SOURCE_DIR / BUILD_AGENTS_SUBDIR
        actual_agents = list(agents_dir.glob("*.md"))
        actual_count = len(actual_agents)

        assert actual_count == EXPECTED_AGENT_COUNT, (
            f"Agent count mismatch!\n"
            f"  Actual files in {agents_dir}: {actual_count}\n"
            f"  EXPECTED_AGENT_COUNT constant: {EXPECTED_AGENT_COUNT}\n"
            f"\n"
            f"Action required:\n"
            f"  1. Update EXPECTED_AGENT_COUNT = {actual_count} in\n"
            f"     src/crafter_ai/installer/domain/ide_bundle_constants.py\n"
            f"  2. Verify all integration tests still pass\n"
            f"\n"
            f"Actual agents:\n"
            + "\n".join(f"  - {a.name}" for a in sorted(actual_agents))
        )

    def test_command_count_matches_nwave_commands_directory(self) -> None:
        """EXPECTED_COMMAND_COUNT must match actual nWave/tasks/nw/*.md files."""
        commands_dir = DEFAULT_SOURCE_DIR / BUILD_COMMANDS_SUBDIR
        actual_commands = list(commands_dir.glob("*.md"))
        actual_count = len(actual_commands)

        assert actual_count == EXPECTED_COMMAND_COUNT, (
            f"Command count mismatch!\n"
            f"  Actual files in {commands_dir}: {actual_count}\n"
            f"  EXPECTED_COMMAND_COUNT constant: {EXPECTED_COMMAND_COUNT}\n"
            f"\n"
            f"Action required:\n"
            f"  Update EXPECTED_COMMAND_COUNT = {actual_count} in\n"
            f"  src/crafter_ai/installer/domain/ide_bundle_constants.py\n"
            f"\n"
            f"Actual commands:\n"
            + "\n".join(f"  - {c.name}" for c in sorted(actual_commands))
        )

    def test_template_count_matches_nwave_templates_directory(self) -> None:
        """EXPECTED_TEMPLATE_COUNT must match actual nWave/templates/*.{yaml,json} files.

        NOTE: Counts ALL .yaml and .json files, including hidden files (starting with .).
        """
        templates_dir = DEFAULT_SOURCE_DIR / BUILD_TEMPLATES_SUBDIR
        # Use glob patterns that include hidden files
        actual_yaml = list(templates_dir.glob("*.yaml")) + list(
            templates_dir.glob(".*.yaml")
        )
        actual_json = list(templates_dir.glob("*.json")) + list(
            templates_dir.glob(".*.json")
        )
        actual_templates = actual_yaml + actual_json
        actual_count = len(actual_templates)

        assert actual_count == EXPECTED_TEMPLATE_COUNT, (
            f"Template count mismatch!\n"
            f"  Actual files in {templates_dir}: {actual_count}\n"
            f"    (.yaml files: {len(actual_yaml)}, .json files: {len(actual_json)})\n"
            f"  EXPECTED_TEMPLATE_COUNT constant: {EXPECTED_TEMPLATE_COUNT}\n"
            f"\n"
            f"Action required:\n"
            f"  Update EXPECTED_TEMPLATE_COUNT = {actual_count} in\n"
            f"  src/crafter_ai/installer/domain/ide_bundle_constants.py\n"
            f"\n"
            f"Actual templates:\n"
            + "\n".join(f"  - {t.name}" for t in sorted(actual_templates))
        )

    def test_script_count_matches_nwave_scripts_directory(self) -> None:
        """EXPECTED_SCRIPT_COUNT must match actual nWave/scripts/des/*.py files."""
        scripts_dir = DEFAULT_SOURCE_DIR / BUILD_SCRIPTS_SUBDIR
        actual_scripts = list(scripts_dir.glob("*.py"))
        actual_count = len(actual_scripts)

        assert actual_count == EXPECTED_SCRIPT_COUNT, (
            f"Script count mismatch!\n"
            f"  Actual files in {scripts_dir}: {actual_count}\n"
            f"  EXPECTED_SCRIPT_COUNT constant: {EXPECTED_SCRIPT_COUNT}\n"
            f"\n"
            f"Action required:\n"
            f"  Update EXPECTED_SCRIPT_COUNT = {actual_count} in\n"
            f"  src/crafter_ai/installer/domain/ide_bundle_constants.py\n"
            f"\n"
            f"Actual scripts:\n"
            + "\n".join(f"  - {s.name}" for s in sorted(actual_scripts))
        )

    def test_all_agent_files_are_markdown(self) -> None:
        """All files in nWave/agents/ must be .md files (no stray files)."""
        agents_dir = DEFAULT_SOURCE_DIR / BUILD_AGENTS_SUBDIR
        all_files = list(agents_dir.iterdir())
        non_md_files = [f for f in all_files if f.suffix != ".md" and f.is_file()]

        assert len(non_md_files) == 0, (
            f"Found non-.md files in {agents_dir}:\n"
            + "\n".join(f"  - {f.name}" for f in non_md_files)
            + "\n\nOnly .md files allowed in agents directory."
        )

    def test_all_command_files_are_markdown(self) -> None:
        """All files in nWave/tasks/nw/ must be .md files (no stray files)."""
        commands_dir = DEFAULT_SOURCE_DIR / BUILD_COMMANDS_SUBDIR
        all_files = list(commands_dir.iterdir())
        non_md_files = [f for f in all_files if f.suffix != ".md" and f.is_file()]

        assert len(non_md_files) == 0, (
            f"Found non-.md files in {commands_dir}:\n"
            + "\n".join(f"  - {f.name}" for f in non_md_files)
            + "\n\nOnly .md files allowed in commands directory."
        )

    def test_all_template_files_are_yaml_or_json(self) -> None:
        """All files in nWave/templates/ must be .yaml or .json files.

        NOTE: Hidden files (starting with .) are allowed if they have .yaml or .json extensions.
        """
        templates_dir = DEFAULT_SOURCE_DIR / BUILD_TEMPLATES_SUBDIR
        all_files = list(templates_dir.iterdir())
        invalid_files = [
            f
            for f in all_files
            if f.suffix not in {".yaml", ".json", ".md"} and f.is_file()
        ]

        assert len(invalid_files) == 0, (
            f"Found invalid files in {templates_dir}:\n"
            + "\n".join(f"  - {f.name}" for f in invalid_files)
            + "\n\nOnly .yaml, .json, and .md files allowed in templates directory."
        )

    def test_all_script_files_are_python(self) -> None:
        """All files in nWave/scripts/des/ must be .py files."""
        scripts_dir = DEFAULT_SOURCE_DIR / BUILD_SCRIPTS_SUBDIR
        all_files = list(scripts_dir.iterdir())
        non_py_files = [f for f in all_files if f.suffix != ".py" and f.is_file()]

        assert len(non_py_files) == 0, (
            f"Found non-.py files in {scripts_dir}:\n"
            + "\n".join(f"  - {f.name}" for f in non_py_files)
            + "\n\nOnly .py files allowed in scripts directory."
        )
