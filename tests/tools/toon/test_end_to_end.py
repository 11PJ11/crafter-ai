"""End-to-end tests for TOON toolchain walking skeleton.

Business language: Compile TOON source files into Claude Code agent definitions.
"""
from pathlib import Path
import pytest


def test_compile_novel_editor_toon_to_agent_md(tmp_path):
    """
    GIVEN a valid TOON v1.0 agent file (novel-editor-chatgpt-toon.txt)
    WHEN I compile it to output directory
    THEN output directory contains agent.md with valid Claude Code format

    Validates:
    - Pipeline works end-to-end (parse → select template → render → write)
    - Output has YAML frontmatter with mandatory keys
    - Agent definition is present
    """
    from tools.toon.compiler import compile_toon

    # GIVEN: Real TOON v1.0 file
    toon_path = Path('agents/novel-editor-chatgpt-toon.txt')
    output_dir = tmp_path / 'output'

    # WHEN: Compile TOON to agent.md
    compile_toon(str(toon_path), str(output_dir))

    # THEN: Output exists with valid format
    # Parser extracts ID from role field: "Aria | genre_editor" → "genre_editor"
    output_file = output_dir / 'genre_editor.md'
    assert output_file.exists(), "Agent markdown file should be created"

    content = output_file.read_text()

    # Validate YAML frontmatter present
    assert 'name:' in content, "YAML frontmatter should include 'name' key"
    assert 'description:' in content or 'spec:' in content, "YAML frontmatter should include description or spec"
    assert 'model:' in content, "YAML frontmatter should include 'model' key"

    # Validate agent content sections present
    assert 'NOVEL EDITOR AGENT' in content or 'Aria' in content, "Agent identity should be present"

    # AC#2: Activation notice present
    assert '> **Agent Activated**:' in content, "Activation notice section missing (AC#2)"

    # AC#3: Agent YAML block present with commands
    assert '```yaml' in content, "YAML code block missing (AC#3)"
    assert 'agent:' in content, "agent: key missing from YAML block (AC#3)"
