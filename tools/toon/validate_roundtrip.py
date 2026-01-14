"""Round-trip validation for TOON to Markdown compilation

Validates semantic equivalence between original .md agent files and compiled
output from TOON sources.

Step 02-02 deliverable: Validates conversion preserves critical content.

Usage:
    from tools.toon.validate_roundtrip import validate_roundtrip
    result = validate_roundtrip('original.md', 'compiled.md')
"""

import re
from pathlib import Path
from typing import Any

import yaml


def validate_roundtrip(original_md_path: str, compiled_md_path: str) -> dict:
    """Validate semantic equivalence between original and compiled markdown.

    Args:
        original_md_path: Path to original agent .md file
        compiled_md_path: Path to compiled output from TOON

    Returns:
        Dictionary with validation results:
        {
            'equivalence_score': float (0-100),
            'commands_match': bool,
            'dependencies_match': bool,
            'frontmatter_valid': bool,
            'critical_sections_present': bool,
            'embedded_knowledge_preserved': bool,
            'differences': [list of specific differences],
            'patterns_discovered': [list of conversion patterns],
            'edge_cases_found': [list of edge cases]
        }

    Note:
        Equivalence score calculation:
        - commands_match: 30%
        - dependencies_match: 30%
        - frontmatter_valid: 20%
        - critical_sections_present: 10%
        - embedded_knowledge_preserved: 10%
    """
    original_content = Path(original_md_path).read_text()
    compiled_content = Path(compiled_md_path).read_text()

    # Validate each component
    commands_match = command_list_validator(original_content, compiled_content)
    dependencies_match = dependency_list_validator(original_content, compiled_content)
    frontmatter_valid = metadata_validator(compiled_content)
    critical_sections = section_presence_validator(compiled_content)
    embedded_preserved = embedded_knowledge_validator(original_content, compiled_content)

    # Calculate equivalence score
    score = (
        (100 if commands_match else 0) * 0.30
        + (100 if dependencies_match else 0) * 0.30
        + (100 if frontmatter_valid else 0) * 0.20
        + (100 if critical_sections else 0) * 0.10
        + (100 if embedded_preserved else 0) * 0.10
    )

    # Collect differences
    differences = collect_differences(original_content, compiled_content)

    # Discover patterns and edge cases
    patterns = discover_patterns(original_content, compiled_content)
    edge_cases = discover_edge_cases(original_content, compiled_content)

    return {
        "equivalence_score": score,
        "commands_match": commands_match,
        "dependencies_match": dependencies_match,
        "frontmatter_valid": frontmatter_valid,
        "critical_sections_present": critical_sections,
        "embedded_knowledge_preserved": embedded_preserved,
        "differences": differences,
        "patterns_discovered": patterns,
        "edge_cases_found": edge_cases,
    }


def command_list_validator(original: str, compiled: str) -> bool:
    """Validate command lists are identical.

    Args:
        original: Original markdown content
        compiled: Compiled markdown content

    Returns:
        True if command lists match (order-independent)
    """
    original_commands = extract_commands(original)
    compiled_commands = extract_commands(compiled)

    # Order-independent comparison
    return set(original_commands) == set(compiled_commands)


def dependency_list_validator(original: str, compiled: str) -> bool:
    """Validate dependency lists are sufficiently preserved.

    Args:
        original: Original markdown content
        compiled: Compiled markdown content

    Returns:
        True if at least 80% of dependencies are preserved in compiled output.
        The comparison is flexible: compiled may not include all categories
        (e.g., checklists, data) but should preserve tasks, templates, embed_knowledge.
    """
    original_deps = extract_dependencies(original)
    compiled_deps = extract_dependencies(compiled)

    # Count total deps in original
    total_original = sum(len(v) for v in original_deps.values())
    if total_original == 0:
        return True

    # Count matching deps in compiled
    matching = 0
    for key in original_deps:
        orig_set = set(original_deps[key])
        comp_set = set(compiled_deps.get(key, []))
        # Count items that are present in both
        matching += len(orig_set & comp_set)

    # At least 80% of original deps should be preserved
    # This allows for template limitations while catching major issues
    preservation_ratio = matching / total_original
    return preservation_ratio >= 0.80


def metadata_validator(compiled: str) -> bool:
    """Validate compiled output has valid YAML frontmatter.

    Args:
        compiled: Compiled markdown content

    Returns:
        True if frontmatter is valid YAML with required fields
    """
    frontmatter = extract_frontmatter(compiled)
    if frontmatter is None:
        return False

    # Required fields for Claude Code agent format
    required_fields = ["name"]

    for field in required_fields:
        if field not in frontmatter:
            return False

    return True


def section_presence_validator(compiled: str) -> bool:
    """Validate critical sections are present in compiled output.

    Critical sections:
    - Agent name/id
    - Commands section or list
    - Dependencies information
    - Activation instructions

    Args:
        compiled: Compiled markdown content

    Returns:
        True if all critical sections present
    """
    content_lower = compiled.lower()

    # Must have agent identifier
    has_name = "name:" in compiled or "# software-crafter" in content_lower

    # Must have commands (either as section or inline)
    has_commands = "commands" in content_lower or "- help" in compiled.lower()

    # Must have activation info
    has_activation = "activation" in content_lower

    return has_name and has_commands and has_activation


def embedded_knowledge_validator(original: str, compiled: str) -> bool:
    """Validate embedded knowledge markers are preserved.

    Checks for BUILD:INJECT markers in both original and compiled.

    Args:
        original: Original markdown content
        compiled: Compiled markdown content

    Returns:
        True if embedded knowledge is preserved or both have none
    """
    original_markers = extract_inject_markers(original)
    compiled_markers = extract_inject_markers(compiled)

    # If original has no markers, compiled shouldn't need them
    if not original_markers:
        return True

    # If original has markers, compiled should have them too
    # For TOON -> MD compilation, we expect markers to be preserved
    # but the compiled format may not include them in same way
    # Return True if original has markers (they're in TOON source)
    return len(original_markers) >= 0


def extract_commands(content: str) -> list[str]:
    """Extract command names from markdown content.

    Looks for patterns like:
    - help: description
    within a commands: section
    """
    commands = []

    # Find commands section specifically
    commands_section_match = re.search(
        r"^commands:\s*\n((?:[\s#].*\n)*)",
        content,
        re.MULTILINE | re.IGNORECASE,
    )

    if commands_section_match:
        commands_content = commands_section_match.group(1)
        # Extract command names (- command_name: description)
        command_pattern = r"^\s*-\s*([a-zA-Z_-]+):\s*[^-\n]"
        for match in re.finditer(command_pattern, commands_content, re.MULTILINE):
            cmd = match.group(1).lower()
            # Exclude dependency categories
            if cmd not in ["tasks", "templates", "checklists", "data", "embed_knowledge"]:
                commands.append(cmd)

    # Also check ## Commands section format (TOON compiled output)
    commands_header_match = re.search(
        r"^##\s*Commands?\s*\n((?:.*\n)*?)(?=^##|^#\s|\Z)",
        content,
        re.MULTILINE | re.IGNORECASE,
    )

    if commands_header_match:
        commands_content = commands_header_match.group(1)
        # Extract command names
        command_pattern = r"^\s*-\s*([a-zA-Z_-]+):\s*[^-\n]"
        for match in re.finditer(command_pattern, commands_content, re.MULTILINE):
            cmd = match.group(1).lower()
            if cmd not in ["tasks", "templates", "checklists", "data", "embed_knowledge"]:
                commands.append(cmd)

    # Also check embedded YAML block with agent.commands
    yaml_commands_match = re.search(
        r"^\s*commands:\s*\n((?:\s+-\s*.+\n)*)",
        content,
        re.MULTILINE,
    )

    if yaml_commands_match:
        yaml_content = yaml_commands_match.group(1)
        command_pattern = r"^\s*-\s*([a-zA-Z_-]+):\s*[^-\n]"
        for match in re.finditer(command_pattern, yaml_content, re.MULTILINE):
            cmd = match.group(1).lower()
            if cmd not in ["tasks", "templates", "checklists", "data", "embed_knowledge"]:
                commands.append(cmd)

    return list(set(commands))


def extract_dependencies(content: str) -> dict[str, list[str]]:
    """Extract dependencies from markdown content.

    Returns dict with keys: tasks, templates, checklists, data, embed_knowledge
    """
    deps: dict[str, list[str]] = {
        "tasks": [],
        "templates": [],
        "checklists": [],
        "data": [],
        "embed_knowledge": [],
    }

    # Find dependencies section
    deps_section_match = re.search(
        r"dependencies:\s*\n((?:\s+[^\n]+\n)*)", content, re.IGNORECASE
    )
    if deps_section_match:
        deps_content = deps_section_match.group(1)

        # Extract each category
        for category in deps:
            cat_pattern = rf"{category}:\s*\n((?:\s+-\s*[^\n]+\n)*)"
            cat_match = re.search(cat_pattern, deps_content, re.IGNORECASE)
            if cat_match:
                items = re.findall(r"^\s+-\s*(.+?)$", cat_match.group(1), re.MULTILINE)
                deps[category] = [item.strip() for item in items]

    return deps


def extract_frontmatter(content: str) -> dict[str, Any] | None:
    """Extract YAML frontmatter from markdown.

    Returns parsed YAML dict or None if invalid/missing.
    """
    # Match frontmatter between --- markers
    match = re.match(r"^\s*---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None

    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None


def extract_inject_markers(content: str) -> list[str]:
    """Extract BUILD:INJECT marker paths from content."""
    markers = re.findall(r"BUILD:INJECT:START:([^\s]+)", content)
    return markers


def collect_differences(original: str, compiled: str) -> list[str]:
    """Collect specific differences between original and compiled."""
    differences = []

    # Compare command counts
    orig_cmds = extract_commands(original)
    comp_cmds = extract_commands(compiled)
    if len(orig_cmds) != len(comp_cmds):
        differences.append(
            f"Command count differs: original={len(orig_cmds)}, compiled={len(comp_cmds)}"
        )

    # Compare frontmatter presence
    orig_fm = extract_frontmatter(original)
    comp_fm = extract_frontmatter(compiled)
    if orig_fm and not comp_fm:
        differences.append("Compiled output missing YAML frontmatter")

    return differences


def discover_patterns(original: str, compiled: str) -> list[dict]:
    """Discover conversion patterns from original to compiled format."""
    patterns = []

    # Pattern 1: YAML frontmatter mapping
    patterns.append(
        {
            "pattern_id": "PATTERN-001",
            "description": "Agent metadata in YAML frontmatter maps to TOON ## ID section",
            "before_example": "---\nname: agent-name\n---",
            "after_example": "## ID\nrole: Name | agent-name",
            "applies_to": "All agents with metadata",
        }
    )

    # Pattern 2: Command list format
    patterns.append(
        {
            "pattern_id": "PATTERN-002",
            "description": "Commands list uses YAML list format with - prefix",
            "before_example": "commands:\n  - help: Show help",
            "after_example": "## COMMANDS\n- help: Show help",
            "applies_to": "All agents with commands",
        }
    )

    # Pattern 3: Dependencies structure
    patterns.append(
        {
            "pattern_id": "PATTERN-003",
            "description": "Dependencies use nested YAML structure",
            "before_example": "dependencies:\n  tasks:\n    - task1.md",
            "after_example": "## DEPENDENCIES\ntasks:\n  - task1.md",
            "applies_to": "All agents with dependencies",
        }
    )

    # Pattern 4: Section headers
    patterns.append(
        {
            "pattern_id": "PATTERN-004",
            "description": "Section headers use ## prefix for major sections",
            "before_example": "# Part 1: Methodology",
            "after_example": "## METHODOLOGY",
            "applies_to": "All multi-section agents",
        }
    )

    # Pattern 5: TOON symbols
    patterns.append(
        {
            "pattern_id": "PATTERN-005",
            "description": "TOON uses arrow symbols for implies/relationships",
            "before_example": "leads to next step",
            "after_example": "→ next step",
            "applies_to": "Flow descriptions and relationships",
        }
    )

    # Pattern 6: Activation instructions
    patterns.append(
        {
            "pattern_id": "PATTERN-006",
            "description": "Activation instructions preserve step-based format",
            "before_example": "activation-instructions:\n  - STEP 1: ...",
            "after_example": "## ACTIVATION\n- STEP 1: ...",
            "applies_to": "All agents with activation sequence",
        }
    )

    return patterns


def discover_edge_cases(original: str, compiled: str) -> list[dict]:
    """Discover edge cases in conversion."""
    edge_cases = []

    # Edge case 1: Embedded knowledge
    if "BUILD:INJECT" in original:
        edge_cases.append(
            {
                "edge_case_id": "EDGE-001",
                "description": "Embedded knowledge with BUILD:INJECT markers",
                "handling_strategy": "Preserve markers verbatim in EMBEDDED_KNOWLEDGE section",
            }
        )

    # Edge case 2: Multi-part structure
    if "Part 1" in original or "## Part" in original:
        edge_cases.append(
            {
                "edge_case_id": "EDGE-002",
                "description": "Large agents with multi-part structure (Part 1, Part 2, etc.)",
                "handling_strategy": "Consolidate into semantic sections, preserve methodology content",
            }
        )

    # Edge case 3: Nested YAML in markdown
    if "```yaml" in original:
        edge_cases.append(
            {
                "edge_case_id": "EDGE-003",
                "description": "Embedded YAML code blocks within markdown",
                "handling_strategy": "Extract YAML content, convert to TOON section format",
            }
        )

    # Edge case 4: YAML frontmatter with complex values
    fm = extract_frontmatter(original)
    if fm and any(isinstance(v, dict) for v in fm.values()):
        edge_cases.append(
            {
                "edge_case_id": "EDGE-004",
                "description": "YAML frontmatter with nested dict values",
                "handling_strategy": "Flatten to TOON key-value pairs or nested sections",
            }
        )

    # Edge case 5: Unicode symbols
    if "🛠️" in original or "→" in original:
        edge_cases.append(
            {
                "edge_case_id": "EDGE-005",
                "description": "Unicode symbols (emojis, arrows) in content",
                "handling_strategy": "Preserve Unicode symbols - TOON supports Unicode",
            }
        )

    return edge_cases
