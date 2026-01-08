"""Unit tests for TOON compiler - Walking Skeleton.

Business language: Compile TOON files to Claude Code agent format.
"""
from pathlib import Path
import pytest
from tools.toon.compiler import compile_toon


def test_compiler_prepares_output_location_for_agent_artifacts(tmp_path):
    """
    GIVEN a TOON file and non-existent output directory
    WHEN compiler runs
    THEN output directory is created
    """
    toon_path = Path('agents/novel-editor-chatgpt-toon.txt')
    output_dir = tmp_path / 'new_dir' / 'nested'

    compile_toon(str(toon_path), str(output_dir))

    assert output_dir.exists()
    assert output_dir.is_dir()


def test_compiler_produces_claude_code_agent_with_yaml_metadata(tmp_path):
    """
    GIVEN a TOON file
    WHEN compiler runs
    THEN output has valid YAML frontmatter with --- delimiters
    """
    toon_path = Path('agents/novel-editor-chatgpt-toon.txt')
    output_dir = tmp_path

    compile_toon(str(toon_path), str(output_dir))

    output_file = output_dir / 'genre_editor.md'
    content = output_file.read_text()

    assert content.startswith('---\n')
    assert '\n---\n' in content


def test_compiler_includes_agent_identity_in_yaml_frontmatter(tmp_path):
    """
    GIVEN a TOON file
    WHEN compiler runs
    THEN output frontmatter includes name, description, model
    """
    toon_path = Path('agents/novel-editor-chatgpt-toon.txt')
    output_dir = tmp_path

    compile_toon(str(toon_path), str(output_dir))

    output_file = output_dir / 'genre_editor.md'
    content = output_file.read_text()

    # Extract frontmatter section
    frontmatter = content.split('---')[1]

    assert 'name:' in frontmatter
    assert 'description:' in frontmatter
    assert 'model:' in frontmatter


def test_compiler_transforms_toon_sections_into_readable_markdown(tmp_path):
    """
    GIVEN a TOON file with sections
    WHEN compiler runs
    THEN output includes markdown headers for sections
    """
    toon_path = Path('agents/novel-editor-chatgpt-toon.txt')
    output_dir = tmp_path

    compile_toon(str(toon_path), str(output_dir))

    output_file = output_dir / 'genre_editor.md'
    content = output_file.read_text()

    assert '## Core Rules' in content or '## ' in content


def test_compiler_renders_agent_with_minimal_metadata(tmp_path):
    """
    GIVEN a TOON file with only name (minimal metadata)
    WHEN compiler runs
    THEN template renders successfully with available metadata
    """
    # Create minimal TOON file
    minimal_toon = tmp_path / 'minimal.toon'
    minimal_toon.write_text("""# MINIMAL AGENT (TOON v3.0)
## ID
role: Test | minimal-agent
""")

    output_dir = tmp_path / 'output'

    compile_toon(str(minimal_toon), str(output_dir))

    output_file = output_dir / 'minimal-agent.md'
    assert output_file.exists()
    content = output_file.read_text()

    # Should have frontmatter with at least name
    assert '---' in content
    assert 'name:' in content
