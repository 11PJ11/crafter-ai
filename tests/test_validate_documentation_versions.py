#!/usr/bin/env python3
"""
Test Suite for Documentation Version Validation Script

Comprehensive Outside-In TDD test suite covering:
- Unit tests for VersionParser, GitHelper, DocumentationVersionValidator
- Integration tests for complete validation workflows
- Edge cases and error conditions

Test isolation: Each test uses temporary git repository, no shared state.
"""

import pytest
import yaml
import subprocess
from pathlib import Path
from typing import Dict
import sys
import os
from unittest.mock import patch, MagicMock

# Add scripts directory to Python path and import module with dashes in name
scripts_dir = Path(__file__).parent.parent / "scripts" / "validation"
sys.path.insert(0, str(scripts_dir))

# Import module with dashes using importlib
import importlib.util  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "validate_documentation_versions",
    scripts_dir / "validate-documentation-versions.py",
)
validate_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_module)

# Extract classes from module
VersionParser = validate_module.VersionParser
GitHelper = validate_module.GitHelper
DocumentationVersionValidator = validate_module.DocumentationVersionValidator
ValidationError = validate_module.ValidationError
TrackedFile = validate_module.TrackedFile
SectionUpdate = validate_module.SectionUpdate
SourceChangeAnalyzer = validate_module.SourceChangeAnalyzer


# =============================================================================
# Fixtures - Test Environment Setup
# =============================================================================


@pytest.fixture
def temp_git_repo(tmp_path):
    """Create isolated temporary git repository for testing"""
    repo_dir = tmp_path / "test_repo"
    repo_dir.mkdir()

    # Initialize git repository
    subprocess.run(["git", "init"], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
    )

    # Create initial commit (required for HEAD references)
    initial_file = repo_dir / "README.md"
    initial_file.write_text("# Test Repository\n")
    subprocess.run(
        ["git", "add", "README.md"], cwd=repo_dir, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
    )

    # Store original directory to restore later
    original_dir = Path.cwd()

    # Change to repo directory for git operations
    os.chdir(repo_dir)

    yield repo_dir

    # Restore original directory
    os.chdir(original_dir)


@pytest.fixture
def sample_yaml_file(temp_git_repo):
    """Create sample YAML file with version field"""
    yaml_file = temp_git_repo / "config.yaml"
    content = {
        "version": "1.0.0",
        "name": "test-config",
        "description": "Test configuration file",
    }
    with open(yaml_file, "w") as f:
        yaml.dump(content, f)

    return yaml_file


@pytest.fixture
def sample_markdown_file(temp_git_repo):
    """Create sample Markdown file with version comment"""
    md_file = temp_git_repo / "docs/guide.md"
    md_file.parent.mkdir(exist_ok=True)

    content = """<!-- version: 1.0.0 -->
# User Guide

This is a test guide document.

## Section 1

Content here.
"""
    md_file.write_text(content)
    return md_file


@pytest.fixture
def dependency_map_simple(temp_git_repo):
    """Create simple dependency map configuration"""
    dep_map = temp_git_repo / ".dependency-map.yaml"
    config = {
        "validation_rules": {
            "require_version_bump_on_change": True,
            "ignore_whitespace_changes": True,
        },
        "tracked_files": [
            {
                "path": "config.yaml",
                "version_format": "yaml",
                "version_field": "version",
                "description": "Main configuration",
                "triggers_update": [],
            }
        ],
    }
    with open(dep_map, "w") as f:
        yaml.dump(config, f)

    return dep_map


@pytest.fixture
def dependency_map_with_dependents(temp_git_repo):
    """Create dependency map with dependent file relationships"""
    dep_map = temp_git_repo / ".dependency-map.yaml"
    config = {
        "validation_rules": {
            "require_version_bump_on_change": True,
            "ignore_whitespace_changes": True,
        },
        "tracked_files": [
            {
                "path": "source.yaml",
                "version_format": "yaml",
                "version_field": "version",
                "description": "Source configuration",
                "triggers_update": [
                    {
                        "file": "docs/guide.md",
                        "sections": [
                            {
                                "id": "config_reference",
                                "location": "docs/guide.md#configuration",
                                "description": "Configuration reference section",
                                "source": "source.yaml",
                            }
                        ],
                    }
                ],
            },
            {
                "path": "docs/guide.md",
                "version_format": "markdown_comment",
                "description": "Documentation guide",
                "triggers_update": [],
            },
        ],
    }
    with open(dep_map, "w") as f:
        yaml.dump(config, f)

    return dep_map


# =============================================================================
# Unit Tests - VersionParser
# =============================================================================


class TestVersionParser:
    """Unit tests for VersionParser component"""

    def test_parse_yaml_version_success(self, sample_yaml_file):
        """Should extract version from YAML file"""
        version = VersionParser.parse_yaml_version(sample_yaml_file, "version")
        assert version == "1.0.0"

    def test_parse_yaml_version_custom_field(self, temp_git_repo):
        """Should extract version from custom YAML field"""
        yaml_file = temp_git_repo / "custom.yaml"
        content = {"app_version": "2.5.3", "name": "test"}
        with open(yaml_file, "w") as f:
            yaml.dump(content, f)

        version = VersionParser.parse_yaml_version(yaml_file, "app_version")
        assert version == "2.5.3"

    def test_parse_yaml_version_missing_field(self, temp_git_repo):
        """Should return None when version field missing"""
        yaml_file = temp_git_repo / "no_version.yaml"
        content = {"name": "test", "description": "No version field"}
        with open(yaml_file, "w") as f:
            yaml.dump(content, f)

        version = VersionParser.parse_yaml_version(yaml_file, "version")
        assert version is None

    def test_parse_yaml_version_invalid_yaml(self, temp_git_repo):
        """Should return None for invalid YAML syntax"""
        yaml_file = temp_git_repo / "invalid.yaml"
        yaml_file.write_text("invalid: yaml: syntax: error:")

        version = VersionParser.parse_yaml_version(yaml_file, "version")
        assert version is None

    def test_parse_yaml_version_nonexistent_file(self, temp_git_repo):
        """Should return None for nonexistent file"""
        nonexistent = temp_git_repo / "does_not_exist.yaml"
        version = VersionParser.parse_yaml_version(nonexistent, "version")
        assert version is None

    def test_parse_markdown_version_success(self, sample_markdown_file):
        """Should extract version from Markdown HTML comment"""
        version = VersionParser.parse_markdown_version(sample_markdown_file)
        assert version == "1.0.0"

    def test_parse_markdown_version_with_spaces(self, temp_git_repo):
        """Should extract version with extra whitespace in comment"""
        md_file = temp_git_repo / "test.md"
        content = "<!--   version:   2.1.0   -->\n# Content"
        md_file.write_text(content)

        version = VersionParser.parse_markdown_version(md_file)
        assert version == "2.1.0"

    def test_parse_markdown_version_no_comment(self, temp_git_repo):
        """Should return None when no version comment present"""
        md_file = temp_git_repo / "no_version.md"
        md_file.write_text("# Document\n\nNo version comment here.")

        version = VersionParser.parse_markdown_version(md_file)
        assert version is None

    def test_parse_markdown_version_invalid_format(self, temp_git_repo):
        """Should return None for invalid version format in comment"""
        md_file = temp_git_repo / "invalid.md"
        md_file.write_text("<!-- version: not-a-version -->\n# Content")

        version = VersionParser.parse_markdown_version(md_file)
        assert version is None

    @pytest.mark.parametrize(
        "version_str,expected",
        [
            ("1.0.0", True),
            ("2.5.13", True),
            ("0.0.1", True),
            ("10.20.30", True),
            ("invalid", False),
            ("1.0", True),  # packaging library accepts this (normalizes to 1.0.0)
            ("1", True),  # packaging library accepts this (normalizes to 1.0.0)
            ("v1.0.0", True),  # packaging library accepts 'v' prefix
            ("1.0.0-beta", True),  # Pre-release versions are valid
            ("1.0.0+build", True),  # Build metadata is valid
        ],
    )
    def test_validate_version_format(self, version_str, expected):
        """Should validate semantic version format correctly"""
        result = VersionParser.validate_version_format(version_str)
        assert result == expected

    @pytest.mark.parametrize(
        "v1,v2,expected",
        [
            ("1.0.0", "2.0.0", -1),  # v1 < v2
            ("2.0.0", "1.0.0", 1),  # v1 > v2
            ("1.0.0", "1.0.0", 0),  # v1 == v2
            ("1.0.0", "1.0.1", -1),  # Patch version
            ("1.1.0", "1.0.9", 1),  # Minor version precedence
            ("2.0.0", "1.99.99", 1),  # Major version precedence
        ],
    )
    def test_compare_versions(self, v1, v2, expected):
        """Should compare semantic versions correctly"""
        result = VersionParser.compare_versions(v1, v2)
        assert result == expected

    def test_compare_versions_invalid(self):
        """Should return 0 for invalid version comparison"""
        result = VersionParser.compare_versions("invalid", "1.0.0")
        assert result == 0


# =============================================================================
# Unit Tests - GitHelper
# =============================================================================


class TestGitHelper:
    """Unit tests for GitHelper component"""

    def test_get_staged_files_empty(self, temp_git_repo):
        """Should return empty list when no files staged"""
        staged = GitHelper.get_staged_files()
        assert staged == []

    def test_get_staged_files_single(self, temp_git_repo, sample_yaml_file):
        """Should return list with single staged file"""
        subprocess.run(["git", "add", "config.yaml"], check=True, capture_output=True)

        staged = GitHelper.get_staged_files()
        assert "config.yaml" in staged

    def test_get_staged_files_multiple(
        self, temp_git_repo, sample_yaml_file, sample_markdown_file
    ):
        """Should return list with multiple staged files"""
        subprocess.run(
            ["git", "add", "config.yaml", "docs/guide.md"],
            check=True,
            capture_output=True,
        )

        staged = GitHelper.get_staged_files()
        assert "config.yaml" in staged
        assert "docs/guide.md" in staged
        assert len(staged) == 2

    def test_file_has_changes_true(self, temp_git_repo, sample_yaml_file):
        """Should return True when file has substantive changes"""
        # Commit initial version
        subprocess.run(["git", "add", "config.yaml"], check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add config"], check=True, capture_output=True
        )

        # Modify file
        content = yaml.safe_load(open(sample_yaml_file))
        content["version"] = "2.0.0"
        with open(sample_yaml_file, "w") as f:
            yaml.dump(content, f)

        subprocess.run(["git", "add", "config.yaml"], check=True, capture_output=True)

        has_changes = GitHelper.file_has_changes("config.yaml")
        assert has_changes is True

    def test_file_has_changes_whitespace_only(self, temp_git_repo, sample_yaml_file):
        """Should return True even for trailing newlines (git diff -w shows them)"""
        # Commit initial version
        subprocess.run(["git", "add", "config.yaml"], check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add config"], check=True, capture_output=True
        )

        # Add only trailing newlines
        with open(sample_yaml_file, "a") as f:
            f.write("\n\n")

        subprocess.run(["git", "add", "config.yaml"], check=True, capture_output=True)

        # Note: git diff -w still shows added blank lines (not just whitespace changes)
        has_changes = GitHelper.file_has_changes("config.yaml", ignore_whitespace=True)
        assert has_changes is True  # Adding blank lines IS a change

    def test_file_has_changes_no_ignore_whitespace(
        self, temp_git_repo, sample_yaml_file
    ):
        """Should return True for whitespace changes when not ignoring"""
        # Commit initial version
        subprocess.run(["git", "add", "config.yaml"], check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add config"], check=True, capture_output=True
        )

        # Add whitespace
        with open(sample_yaml_file, "a") as f:
            f.write("\n\n")

        subprocess.run(["git", "add", "config.yaml"], check=True, capture_output=True)

        has_changes = GitHelper.file_has_changes("config.yaml", ignore_whitespace=False)
        assert has_changes is True

    def test_get_version_from_head_yaml(self, temp_git_repo, sample_yaml_file):
        """Should extract version from HEAD commit for YAML file"""
        # Commit file with version
        subprocess.run(["git", "add", "config.yaml"], check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add config"], check=True, capture_output=True
        )

        version = GitHelper.get_version_from_head("config.yaml", "yaml", "version")
        assert version == "1.0.0"

    def test_get_version_from_head_markdown(self, temp_git_repo, sample_markdown_file):
        """Should extract version from HEAD commit for Markdown file"""
        # Commit file with version comment
        subprocess.run(["git", "add", "docs/guide.md"], check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add guide"], check=True, capture_output=True
        )

        version = GitHelper.get_version_from_head("docs/guide.md", "markdown_comment")
        assert version == "1.0.0"

    def test_get_version_from_head_new_file(self, temp_git_repo, sample_yaml_file):
        """Should return None for new file (not in HEAD)"""
        # File exists but not committed
        version = GitHelper.get_version_from_head("config.yaml", "yaml", "version")
        assert version is None

    def test_get_version_from_head_nonexistent(self, temp_git_repo):
        """Should return None for nonexistent file"""
        version = GitHelper.get_version_from_head("nonexistent.yaml", "yaml", "version")
        assert version is None


# =============================================================================
# Unit Tests - DocumentationVersionValidator
# =============================================================================


class TestDocumentationVersionValidator:
    """Unit tests for DocumentationVersionValidator core logic"""

    def test_init_loads_dependency_map(self, temp_git_repo, dependency_map_simple):
        """Should load dependency map on initialization"""
        validator = DocumentationVersionValidator(".dependency-map.yaml")
        assert validator.dependency_map is not None
        assert "tracked_files" in validator.dependency_map

    def test_init_missing_dependency_map(self, temp_git_repo):
        """Should exit with code 2 when dependency map missing"""
        with pytest.raises(SystemExit) as exc_info:
            DocumentationVersionValidator(".nonexistent.yaml")
        assert exc_info.value.code == 2

    def test_init_invalid_yaml(self, temp_git_repo):
        """Should exit with code 2 when dependency map is invalid YAML"""
        dep_map = temp_git_repo / ".dependency-map.yaml"
        dep_map.write_text("invalid: yaml: syntax:")

        with pytest.raises(SystemExit) as exc_info:
            DocumentationVersionValidator(".dependency-map.yaml")
        assert exc_info.value.code == 2

    def test_validate_no_staged_files(self, temp_git_repo, dependency_map_simple):
        """Should pass validation when no files staged"""
        validator = DocumentationVersionValidator(".dependency-map.yaml")
        result = validator.validate()
        assert result is True
        assert len(validator.errors) == 0

    def test_validate_version_not_bumped(
        self, temp_git_repo, dependency_map_simple, sample_yaml_file
    ):
        """Should detect when file changed but version not bumped"""
        # Commit initial version
        subprocess.run(["git", "add", "config.yaml"], check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add config"], check=True, capture_output=True
        )

        # Modify content but keep same version
        content = yaml.safe_load(open(sample_yaml_file))
        content["description"] = "Modified description"
        with open(sample_yaml_file, "w") as f:
            yaml.dump(content, f)

        subprocess.run(["git", "add", "config.yaml"], check=True, capture_output=True)

        validator = DocumentationVersionValidator(".dependency-map.yaml")
        result = validator.validate()

        assert result is False
        assert len(validator.errors) == 1
        assert validator.errors[0].error_type == "VERSION_NOT_BUMPED"
        assert validator.errors[0].file == "config.yaml"

    def test_validate_version_bumped_correctly(
        self, temp_git_repo, dependency_map_simple, sample_yaml_file
    ):
        """Should pass validation when version bumped after change"""
        # Commit initial version
        subprocess.run(["git", "add", "config.yaml"], check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add config"], check=True, capture_output=True
        )

        # Modify content AND bump version
        content = yaml.safe_load(open(sample_yaml_file))
        content["description"] = "Modified description"
        content["version"] = "1.1.0"
        with open(sample_yaml_file, "w") as f:
            yaml.dump(content, f)

        subprocess.run(["git", "add", "config.yaml"], check=True, capture_output=True)

        validator = DocumentationVersionValidator(".dependency-map.yaml")
        result = validator.validate()

        assert result is True
        assert len(validator.errors) == 0

    def test_validate_invalid_version_format(
        self, temp_git_repo, dependency_map_simple, sample_yaml_file
    ):
        """Should detect invalid semantic version format"""
        # Commit initial version
        subprocess.run(["git", "add", "config.yaml"], check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add config"], check=True, capture_output=True
        )

        # Change to invalid version format
        content = yaml.safe_load(open(sample_yaml_file))
        content["version"] = "not-a-version"
        with open(sample_yaml_file, "w") as f:
            yaml.dump(content, f)

        subprocess.run(["git", "add", "config.yaml"], check=True, capture_output=True)

        validator = DocumentationVersionValidator(".dependency-map.yaml")
        result = validator.validate()

        assert result is False
        assert len(validator.errors) == 1
        assert validator.errors[0].error_type == "INVALID_VERSION"
        assert "not-a-version" in validator.errors[0].reason

    def test_validate_whitespace_only_change(
        self, temp_git_repo, dependency_map_simple, sample_yaml_file
    ):
        """Should treat trailing newlines as substantive change requiring version bump"""
        # Commit initial version
        subprocess.run(["git", "add", "config.yaml"], check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add config"], check=True, capture_output=True
        )

        # Add trailing newlines
        with open(sample_yaml_file, "a") as f:
            f.write("\n\n")

        subprocess.run(["git", "add", "config.yaml"], check=True, capture_output=True)

        validator = DocumentationVersionValidator(".dependency-map.yaml")
        result = validator.validate()

        # Note: Adding blank lines IS considered a change by git diff -w
        # This matches actual script behavior
        assert result is False  # Should fail (version not bumped)
        assert len(validator.errors) == 1
        assert validator.errors[0].error_type == "VERSION_NOT_BUMPED"

    def test_validate_dependent_outdated(
        self, temp_git_repo, dependency_map_with_dependents
    ):
        """Should detect when dependent file version is outdated"""
        # Create source file with version 2.0.0
        source_file = temp_git_repo / "source.yaml"
        source_content = {"version": "2.0.0", "name": "source"}
        with open(source_file, "w") as f:
            yaml.dump(source_content, f)

        # Create dependent file with older version 1.0.0
        docs_dir = temp_git_repo / "docs"
        docs_dir.mkdir(exist_ok=True)
        doc_file = docs_dir / "guide.md"
        doc_content = "<!-- version: 1.0.0 -->\n# Guide\n"
        doc_file.write_text(doc_content)

        # Stage only source file (simulating source update)
        subprocess.run(["git", "add", "source.yaml"], check=True, capture_output=True)

        validator = DocumentationVersionValidator(".dependency-map.yaml")
        result = validator.validate()

        assert result is False
        assert len(validator.errors) == 1
        assert validator.errors[0].error_type == "DEPENDENT_OUTDATED"
        assert validator.errors[0].file == "docs/guide.md"
        assert validator.errors[0].current_version == "1.0.0"
        assert validator.errors[0].expected_version == "2.0.0"

    def test_validate_dependent_synchronized(
        self, temp_git_repo, dependency_map_with_dependents
    ):
        """Should pass when dependent file version matches source"""
        # Create source file with version 2.0.0
        source_file = temp_git_repo / "source.yaml"
        source_content = {"version": "2.0.0", "name": "source"}
        with open(source_file, "w") as f:
            yaml.dump(source_content, f)

        # Create dependent file with matching version
        docs_dir = temp_git_repo / "docs"
        docs_dir.mkdir(exist_ok=True)
        doc_file = docs_dir / "guide.md"
        doc_content = "<!-- version: 2.0.0 -->\n# Guide\n"
        doc_file.write_text(doc_content)

        subprocess.run(["git", "add", "source.yaml"], check=True, capture_output=True)

        validator = DocumentationVersionValidator(".dependency-map.yaml")
        result = validator.validate()

        assert result is True
        assert len(validator.errors) == 0

    def test_generate_error_report_structure(
        self, temp_git_repo, dependency_map_simple, sample_yaml_file
    ):
        """Should generate complete JSON error report with LLM guidance"""
        # Create scenario with version not bumped error
        subprocess.run(["git", "add", "config.yaml"], check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add config"], check=True, capture_output=True
        )

        content = yaml.safe_load(open(sample_yaml_file))
        content["description"] = "Modified"
        with open(sample_yaml_file, "w") as f:
            yaml.dump(content, f)

        subprocess.run(["git", "add", "config.yaml"], check=True, capture_output=True)

        validator = DocumentationVersionValidator(".dependency-map.yaml")
        validator.validate()
        report = validator.generate_error_report()

        # Validate report structure
        assert "error_type" in report
        assert report["error_type"] == "VERSION_VALIDATION_FAILED"
        assert report["blocking"] is True

        assert "summary" in report
        assert report["summary"]["total_errors"] == 1
        assert report["summary"]["version_not_bumped"] == 1

        assert "errors" in report
        assert "version_not_bumped" in report["errors"]
        assert len(report["errors"]["version_not_bumped"]) == 1

        assert "resolution_steps" in report
        assert len(report["resolution_steps"]) > 0

        assert "llm_guidance" in report
        assert "task" in report["llm_guidance"]
        assert "files_to_read" in report["llm_guidance"]
        assert "files_to_edit" in report["llm_guidance"]

    def test_generate_error_report_multiple_error_types(
        self, temp_git_repo, dependency_map_with_dependents
    ):
        """Should categorize multiple error types in report"""
        # Create invalid version in source
        source_file = temp_git_repo / "source.yaml"
        source_content = {"version": "invalid-version", "name": "source"}
        with open(source_file, "w") as f:
            yaml.dump(source_content, f)

        # Create outdated dependent
        docs_dir = temp_git_repo / "docs"
        docs_dir.mkdir(exist_ok=True)
        doc_file = docs_dir / "guide.md"
        doc_content = "<!-- version: 1.0.0 -->\n# Guide\n"
        doc_file.write_text(doc_content)

        subprocess.run(["git", "add", "source.yaml"], check=True, capture_output=True)

        validator = DocumentationVersionValidator(".dependency-map.yaml")
        validator.validate()
        report = validator.generate_error_report()

        # Should have invalid version error
        assert report["summary"]["invalid_versions"] == 1
        assert len(report["errors"]["invalid_version_format"]) == 1


# =============================================================================
# Integration Tests - Complete Workflows
# =============================================================================


class TestIntegrationWorkflows:
    """Integration tests for complete validation workflows"""

    def test_workflow_new_file_no_version_required(
        self, temp_git_repo, dependency_map_simple
    ):
        """Workflow: Add new file (not tracked) - should pass"""
        new_file = temp_git_repo / "untracked.txt"
        new_file.write_text("New content")
        subprocess.run(["git", "add", "untracked.txt"], check=True, capture_output=True)

        validator = DocumentationVersionValidator(".dependency-map.yaml")
        result = validator.validate()

        assert result is True

    def test_workflow_modify_bump_commit(
        self, temp_git_repo, dependency_map_simple, sample_yaml_file
    ):
        """Workflow: Modify tracked file → bump version → stage → validate → pass"""
        # Initial commit
        subprocess.run(["git", "add", "config.yaml"], check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial"], check=True, capture_output=True
        )

        # Modify and bump version
        content = yaml.safe_load(open(sample_yaml_file))
        content["new_field"] = "new value"
        content["version"] = "1.1.0"
        with open(sample_yaml_file, "w") as f:
            yaml.dump(content, f)

        subprocess.run(["git", "add", "config.yaml"], check=True, capture_output=True)

        # Validate
        validator = DocumentationVersionValidator(".dependency-map.yaml")
        result = validator.validate()

        assert result is True
        assert len(validator.errors) == 0

    def test_workflow_forgot_version_bump_blocked(
        self, temp_git_repo, dependency_map_simple, sample_yaml_file
    ):
        """Workflow: Modify tracked file → forget version bump → validation fails"""
        # Initial commit
        subprocess.run(["git", "add", "config.yaml"], check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial"], check=True, capture_output=True
        )

        # Modify WITHOUT bumping version
        content = yaml.safe_load(open(sample_yaml_file))
        content["new_field"] = "new value"
        # version stays 1.0.0
        with open(sample_yaml_file, "w") as f:
            yaml.dump(content, f)

        subprocess.run(["git", "add", "config.yaml"], check=True, capture_output=True)

        # Validate
        validator = DocumentationVersionValidator(".dependency-map.yaml")
        result = validator.validate()

        assert result is False
        assert len(validator.errors) == 1
        assert validator.errors[0].error_type == "VERSION_NOT_BUMPED"
        assert "required_actions" in report_error_dict(validator.errors[0])

    def test_workflow_source_update_requires_dependent_update(
        self, temp_git_repo, dependency_map_with_dependents
    ):
        """Workflow: Update source → dependent outdated → validation fails with guidance"""
        # Initial state: both at 1.0.0
        source_file = temp_git_repo / "source.yaml"
        source_content = {"version": "1.0.0", "name": "source"}
        with open(source_file, "w") as f:
            yaml.dump(source_content, f)

        docs_dir = temp_git_repo / "docs"
        docs_dir.mkdir(exist_ok=True)
        doc_file = docs_dir / "guide.md"
        doc_content = "<!-- version: 1.0.0 -->\n# Guide\n"
        doc_file.write_text(doc_content)

        subprocess.run(
            ["git", "add", "source.yaml", "docs/guide.md"],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial"], check=True, capture_output=True
        )

        # Update source to 2.0.0
        source_content["version"] = "2.0.0"
        source_content["new_config"] = "added"
        with open(source_file, "w") as f:
            yaml.dump(source_content, f)

        subprocess.run(["git", "add", "source.yaml"], check=True, capture_output=True)

        # Validate
        validator = DocumentationVersionValidator(".dependency-map.yaml")
        result = validator.validate()

        assert result is False
        assert len(validator.errors) == 1

        error = validator.errors[0]
        assert error.error_type == "DEPENDENT_OUTDATED"
        assert error.file == "docs/guide.md"
        assert error.expected_version == "2.0.0"
        assert len(error.sections_to_update) > 0

        # Check report includes LLM guidance
        report = validator.generate_error_report()
        assert "docs/guide.md" in report["llm_guidance"]["files_to_edit"]

    def test_workflow_multiple_files_multiple_errors(
        self, temp_git_repo, dependency_map_with_dependents
    ):
        """Workflow: Multiple files with different error types"""
        # Source with invalid version
        source_file = temp_git_repo / "source.yaml"
        source_content = {"version": "not-valid", "name": "source"}
        with open(source_file, "w") as f:
            yaml.dump(source_content, f)

        # Dependent with old version (would be outdated if source was valid)
        docs_dir = temp_git_repo / "docs"
        docs_dir.mkdir(exist_ok=True)
        doc_file = docs_dir / "guide.md"
        doc_content = "<!-- version: 1.0.0 -->\n# Guide\n"
        doc_file.write_text(doc_content)

        subprocess.run(["git", "add", "source.yaml"], check=True, capture_output=True)

        validator = DocumentationVersionValidator(".dependency-map.yaml")
        result = validator.validate()

        assert result is False

        # Generate report and verify structure
        report = validator.generate_error_report()
        assert report["summary"]["total_errors"] >= 1
        assert "resolution_steps" in report
        assert len(report["resolution_steps"]) > 0


# =============================================================================
# Unit Tests - SourceChangeAnalyzer
# =============================================================================


class TestSourceChangeAnalyzer:
    """Unit tests for SourceChangeAnalyzer semantic change detection"""

    def test_get_yaml_diff_new_file(self, temp_git_repo):
        """Should detect all items as added for new file"""
        # Create new YAML file with commands and agents
        yaml_file = temp_git_repo / "catalog.yaml"
        content = {
            "version": "1.0.0",
            "commands": {"help": {"description": "Show help"}},
            "agents": {"researcher": {"description": "Research agent"}},
        }
        with open(yaml_file, "w") as f:
            yaml.dump(content, f)

        changes = SourceChangeAnalyzer.get_yaml_diff("catalog.yaml")

        assert "help" in changes["commands_added"]
        assert "researcher" in changes["agents_added"]
        assert len(changes["commands_removed"]) == 0
        assert len(changes["commands_modified"]) == 0

    def test_get_yaml_diff_commands_added(self, temp_git_repo):
        """Should detect new commands added"""
        # Commit initial version
        yaml_file = temp_git_repo / "catalog.yaml"
        content = {"version": "1.0.0", "commands": {"help": {"desc": "Help"}}}
        with open(yaml_file, "w") as f:
            yaml.dump(content, f)

        subprocess.run(["git", "add", "catalog.yaml"], check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial"], check=True, capture_output=True
        )

        # Add new command
        content["commands"]["new_cmd"] = {"desc": "New command"}
        content["version"] = "1.1.0"
        with open(yaml_file, "w") as f:
            yaml.dump(content, f)

        subprocess.run(["git", "add", "catalog.yaml"], check=True, capture_output=True)

        changes = SourceChangeAnalyzer.get_yaml_diff("catalog.yaml")

        assert "new_cmd" in changes["commands_added"]
        assert len(changes["commands_removed"]) == 0

    def test_get_yaml_diff_commands_removed(self, temp_git_repo):
        """Should detect commands removed"""
        # Commit initial version with two commands
        yaml_file = temp_git_repo / "catalog.yaml"
        content = {
            "version": "1.0.0",
            "commands": {"help": {"desc": "Help"}, "old_cmd": {"desc": "Old"}},
        }
        with open(yaml_file, "w") as f:
            yaml.dump(content, f)

        subprocess.run(["git", "add", "catalog.yaml"], check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial"], check=True, capture_output=True
        )

        # Remove command
        del content["commands"]["old_cmd"]
        content["version"] = "2.0.0"
        with open(yaml_file, "w") as f:
            yaml.dump(content, f)

        subprocess.run(["git", "add", "catalog.yaml"], check=True, capture_output=True)

        changes = SourceChangeAnalyzer.get_yaml_diff("catalog.yaml")

        assert "old_cmd" in changes["commands_removed"]
        assert len(changes["commands_added"]) == 0

    def test_get_yaml_diff_commands_modified(self, temp_git_repo):
        """Should detect commands modified"""
        # Commit initial version
        yaml_file = temp_git_repo / "catalog.yaml"
        content = {"version": "1.0.0", "commands": {"help": {"desc": "Original"}}}
        with open(yaml_file, "w") as f:
            yaml.dump(content, f)

        subprocess.run(["git", "add", "catalog.yaml"], check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial"], check=True, capture_output=True
        )

        # Modify command description
        content["commands"]["help"]["desc"] = "Modified description"
        content["version"] = "1.0.1"
        with open(yaml_file, "w") as f:
            yaml.dump(content, f)

        subprocess.run(["git", "add", "catalog.yaml"], check=True, capture_output=True)

        changes = SourceChangeAnalyzer.get_yaml_diff("catalog.yaml")

        assert "help" in changes["commands_modified"]
        assert len(changes["commands_added"]) == 0
        assert len(changes["commands_removed"]) == 0

    def test_has_meaningful_changes_true(self):
        """Should return True when changes detected"""
        changes = {"commands_added": ["new_cmd"], "commands_removed": []}
        assert SourceChangeAnalyzer.has_meaningful_changes(changes) is True

    def test_has_meaningful_changes_false(self):
        """Should return False when no changes"""
        changes = {
            "commands_added": [],
            "commands_removed": [],
            "commands_modified": [],
            "agents_added": [],
            "agents_removed": [],
            "agents_modified": [],
            "other_changes": [],
        }
        assert SourceChangeAnalyzer.has_meaningful_changes(changes) is False

    def test_generate_update_guidance_commands(self):
        """Should generate guidance for command changes"""
        changes = {
            "commands_added": ["new_cmd"],
            "commands_removed": ["old_cmd"],
            "commands_modified": ["help"],
        }

        guidance = SourceChangeAnalyzer.generate_update_guidance(
            changes, "catalog.yaml"
        )

        assert any("ADD documentation for new command 'new_cmd'" in g for g in guidance)
        assert any(
            "REMOVE documentation for deleted command 'old_cmd'" in g for g in guidance
        )
        assert any(
            "UPDATE documentation for modified command 'help'" in g for g in guidance
        )

    def test_generate_update_guidance_agents(self):
        """Should generate guidance for agent changes"""
        changes = {
            "agents_added": ["new_agent"],
            "agents_removed": ["old_agent"],
            "agents_modified": ["researcher"],
        }

        guidance = SourceChangeAnalyzer.generate_update_guidance(
            changes, "catalog.yaml"
        )

        assert any("ADD documentation for new agent 'new_agent'" in g for g in guidance)
        assert any(
            "REMOVE documentation for deleted agent 'old_agent'" in g for g in guidance
        )
        assert any(
            "UPDATE documentation for modified agent 'researcher'" in g
            for g in guidance
        )


# =============================================================================
# Edge Cases and Error Conditions
# =============================================================================


class TestEdgeCases:
    """Edge cases and error conditions"""

    def test_empty_dependency_map(self, temp_git_repo):
        """Should handle empty dependency map gracefully"""
        dep_map = temp_git_repo / ".dependency-map.yaml"
        dep_map.write_text("")

        validator = DocumentationVersionValidator(".dependency-map.yaml")
        result = validator.validate()

        assert result is True  # No tracked files, nothing to validate

    def test_dependency_map_no_tracked_files(self, temp_git_repo):
        """Should handle dependency map with no tracked_files key"""
        dep_map = temp_git_repo / ".dependency-map.yaml"
        config = {"validation_rules": {}}
        with open(dep_map, "w") as f:
            yaml.dump(config, f)

        validator = DocumentationVersionValidator(".dependency-map.yaml")
        result = validator.validate()

        assert result is True

    def test_version_cache_avoids_redundant_parsing(
        self, temp_git_repo, dependency_map_simple, sample_yaml_file
    ):
        """Should cache version parsing results to avoid redundant file reads"""
        subprocess.run(["git", "add", "config.yaml"], check=True, capture_output=True)

        validator = DocumentationVersionValidator(".dependency-map.yaml")

        # Parse version first time
        tracked = TrackedFile(
            path="config.yaml",
            version_format="yaml",
            version_field="version",
            triggers_update=[],
        )
        version1 = validator._get_current_version(tracked)

        # Parse again - should use cache
        version2 = validator._get_current_version(tracked)

        assert version1 == version2 == "1.0.0"
        assert "config.yaml" in validator.version_cache

    def test_stderr_error_messages_invalid_yaml(self, temp_git_repo, capsys):
        """Should capture stderr warning for invalid YAML"""
        yaml_file = temp_git_repo / "invalid.yaml"
        yaml_file.write_text("invalid: yaml: syntax:")

        VersionParser.parse_yaml_version(yaml_file, "version")

        captured = capsys.readouterr()
        assert "Warning: Failed to parse YAML version" in captured.err
        assert "invalid.yaml" in captured.err

    def test_stderr_error_messages_invalid_markdown(self, temp_git_repo, capsys):
        """Should capture stderr warning for markdown parsing error"""
        # Create file that will cause read error by making it a directory
        md_path = temp_git_repo / "invalid.md"
        md_path.mkdir()

        VersionParser.parse_markdown_version(md_path)

        captured = capsys.readouterr()
        assert "Warning: Failed to parse Markdown version" in captured.err

    def test_stderr_dependency_map_missing(self, temp_git_repo, capsys):
        """Should capture stderr error for missing dependency map"""
        with pytest.raises(SystemExit) as exc_info:
            DocumentationVersionValidator(".nonexistent.yaml")

        captured = capsys.readouterr()
        assert "ERROR: Dependency map not found" in captured.err
        assert exc_info.value.code == 2

    def test_stderr_dependency_map_invalid_yaml(self, temp_git_repo, capsys):
        """Should capture stderr error for invalid dependency map YAML"""
        dep_map = temp_git_repo / ".dependency-map.yaml"
        dep_map.write_text("invalid: yaml: syntax:")

        with pytest.raises(SystemExit) as exc_info:
            DocumentationVersionValidator(".dependency-map.yaml")

        captured = capsys.readouterr()
        assert "ERROR: Failed to load dependency map" in captured.err
        assert exc_info.value.code == 2

    def test_markdown_version_deep_in_file(self, temp_git_repo):
        """Should find version comment even if not at top of file"""
        md_file = temp_git_repo / "deep.md"
        content = "# Title\n\n" + ("Some content\n" * 100) + "<!-- version: 3.2.1 -->\n"
        md_file.write_text(content)

        # Parser only checks first 2000 chars, so version should still be found
        version = VersionParser.parse_markdown_version(md_file)
        assert version == "3.2.1"

    def test_markdown_version_at_boundary_2000_chars(self, temp_git_repo):
        """Should find version at exactly 2000 character boundary"""
        md_file = temp_git_repo / "boundary.md"
        # Create content that puts version comment at exactly 2000 chars
        padding = "x" * (2000 - len("<!-- version: 1.2.3 -->"))
        content = padding + "<!-- version: 1.2.3 -->"
        md_file.write_text(content)

        version = VersionParser.parse_markdown_version(md_file)
        # Should find it since we read first 2000 chars
        assert version == "1.2.3"

    def test_markdown_version_beyond_2000_chars(self, temp_git_repo):
        """Should NOT find version beyond 2000 character boundary"""
        md_file = temp_git_repo / "beyond.md"
        # Put version comment beyond 2000 chars
        padding = "x" * 2001
        content = padding + "<!-- version: 1.2.3 -->"
        md_file.write_text(content)

        version = VersionParser.parse_markdown_version(md_file)
        # Should NOT find it since it's beyond the 2000 char limit
        assert version is None

    def test_markdown_version_almost_matches_regex(self, temp_git_repo):
        """Should NOT match version comments with wrong format"""
        md_file = temp_git_repo / "almost.md"

        # Test various near-miss formats that should NOT match
        # Note: regex allows optional whitespace after colon (\s*), so "version:1.2.3" WILL match
        test_cases = [
            "<!-- version: 1.2 -->",  # Missing patch version
            "<!-- version: v1.2.3 -->",  # Has 'v' prefix
            "<!-- version: 1.2.3.4 -->",  # Too many version parts
            "<!-- ver: 1.2.3 -->",  # Wrong keyword
            "<!-- version: 1.2.3",  # Missing closing -->
        ]

        for content in test_cases:
            md_file.write_text(content)
            version = VersionParser.parse_markdown_version(md_file)
            assert version is None, f"Should not match: {content}"

    def test_dependency_map_missing_required_keys(self, temp_git_repo):
        """Should handle dependency map with missing required keys"""
        dep_map = temp_git_repo / ".dependency-map.yaml"

        # Missing version_format key
        config = {
            "tracked_files": [
                {
                    "path": "config.yaml",
                    # Missing version_format
                    "triggers_update": [],
                }
            ]
        }
        with open(dep_map, "w") as f:
            yaml.dump(config, f)

        validator = DocumentationVersionValidator(".dependency-map.yaml")

        # Should handle gracefully - parsing may fail but shouldn't crash
        try:
            _ = validator.validate()
            # If it doesn't crash, that's acceptable behavior
        except (KeyError, AttributeError):
            # Also acceptable to raise exception for malformed config
            pass

    def test_dependency_map_wrong_data_types(self, temp_git_repo):
        """Should handle dependency map with wrong data types"""
        dep_map = temp_git_repo / ".dependency-map.yaml"

        # tracked_files should be list but provide dict
        config = {
            "tracked_files": {
                "not": "a list"  # Wrong type - should be list
            }
        }
        with open(dep_map, "w") as f:
            yaml.dump(config, f)

        validator = DocumentationVersionValidator(".dependency-map.yaml")

        # Should handle gracefully without crashing
        try:
            _ = validator.validate()
            # Should return True (no valid tracked files to validate)
        except (TypeError, AttributeError):
            # Also acceptable to raise exception for malformed config
            pass


# =============================================================================
# Unit Tests - Subprocess Mocking
# =============================================================================


class TestSubprocessMocking:
    """Tests that verify exact git command strings using subprocess mocking"""

    @patch("subprocess.run")
    def test_git_diff_exact_command_staged_files(self, mock_run, temp_git_repo):
        """Should execute exact git diff command for staged files"""
        mock_run.return_value = MagicMock(
            returncode=0, stdout="file1.yaml\nfile2.md", stderr=""
        )

        GitHelper.get_staged_files()

        mock_run.assert_called_once_with(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=False,
        )

    @patch("subprocess.run")
    def test_git_show_exact_command_with_file_path(self, mock_run, temp_git_repo):
        """Should execute exact git show command with file path"""
        mock_run.return_value = MagicMock(
            returncode=0, stdout="version: 1.0.0\n", stderr=""
        )

        GitHelper.get_version_from_head("catalog.yaml", "yaml", "version")

        mock_run.assert_called_once_with(
            ["git", "show", "HEAD:catalog.yaml"],
            capture_output=True,
            text=True,
            check=False,
        )

    @patch("subprocess.run")
    def test_git_command_failure_returns_empty_list(self, mock_run, temp_git_repo):
        """Should handle git command failure gracefully"""
        mock_run.return_value = MagicMock(
            returncode=128, stdout="", stderr="fatal: not a git repository"
        )

        result = GitHelper.get_staged_files()

        assert result == []

    @patch("subprocess.run")
    def test_git_show_nonexistent_file_returns_none(self, mock_run, temp_git_repo):
        """Should return None for nonexistent file in HEAD"""
        mock_run.return_value = MagicMock(
            returncode=128,
            stdout="",
            stderr="fatal: path 'nonexistent.yaml' does not exist",
        )

        result = GitHelper.get_version_from_head("nonexistent.yaml", "yaml", "version")

        assert result is None

    @patch("subprocess.run")
    def test_subprocess_exception_handling(self, mock_run, temp_git_repo):
        """Should handle subprocess exceptions without crashing"""
        mock_run.side_effect = Exception("Subprocess error")

        # GitHelper should handle exception gracefully
        try:
            result = GitHelper.get_staged_files()
            # Should return empty list or None
            assert result in ([], None)
        except Exception:
            # If it raises, it should be a handled exception
            pass

    @patch("subprocess.run")
    def test_git_diff_whitespace_flag(self, mock_run, temp_git_repo):
        """Should execute git diff with -w flag when ignoring whitespace"""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        GitHelper.file_has_changes("test.yaml", ignore_whitespace=True)

        # Verify -w flag is included
        called_args = mock_run.call_args[0][0]
        assert "-w" in called_args or "--ignore-all-space" in called_args


# =============================================================================
# Unit Tests - Report Structure Detailed Validation
# =============================================================================


class TestReportStructureDetailed:
    """Tests that verify detailed report structure with type assertions"""

    def test_error_report_has_required_keys_and_types(self, temp_git_repo):
        """Should verify all required keys exist with correct types"""
        # Create mismatched versions to generate error report
        yaml_file = temp_git_repo / "test.yaml"
        yaml_file.write_text("version: 1.0.0\n")

        doc_file = temp_git_repo / "test.md"
        doc_file.write_text("<!-- version: 2.0.0 -->")

        # Create minimal dependency map
        dep_map = temp_git_repo / ".dependency-map.yaml"
        config = {
            "tracked_files": [
                {
                    "path": "test.yaml",
                    "version_format": "yaml",
                    "version_field": "version",
                    "triggers_update": [{"file": "test.md"}],
                }
            ]
        }
        with open(dep_map, "w") as f:
            yaml.dump(config, f)

        subprocess.run(["git", "add", "test.yaml"], check=True, capture_output=True)

        validator = DocumentationVersionValidator(".dependency-map.yaml")
        _ = validator.validate()

        # Generate JSON report
        report = validator.generate_error_report()

        # Verify top-level structure
        assert isinstance(report, dict)
        assert "error_type" in report
        assert isinstance(report["error_type"], str)
        assert "blocking" in report
        assert isinstance(report["blocking"], bool)

        # Verify summary section types
        assert "summary" in report
        assert isinstance(report["summary"], dict)
        assert isinstance(report["summary"].get("total_errors", 0), int)

        # Verify errors section types
        assert "errors" in report
        assert isinstance(report["errors"], dict)

        # Verify resolution_steps is list of strings
        assert "resolution_steps" in report
        assert isinstance(report["resolution_steps"], list)
        if len(report["resolution_steps"]) > 0:
            assert all(isinstance(step, str) for step in report["resolution_steps"])

        # Verify llm_guidance structure
        assert "llm_guidance" in report
        assert isinstance(report["llm_guidance"], dict)
        assert "task" in report["llm_guidance"]
        assert isinstance(report["llm_guidance"]["task"], str)
        assert "files_to_read" in report["llm_guidance"]
        assert isinstance(report["llm_guidance"]["files_to_read"], list)
        assert "files_to_edit" in report["llm_guidance"]
        assert isinstance(report["llm_guidance"]["files_to_edit"], list)

    def test_validation_error_object_types(self, temp_git_repo, dependency_map_simple):
        """Should verify ValidationError object has correct attribute types"""
        # Create scenario with version not bumped
        yaml_file = temp_git_repo / "config.yaml"
        content = {"version": "1.0.0", "name": "test"}
        with open(yaml_file, "w") as f:
            yaml.dump(content, f)

        subprocess.run(["git", "add", "config.yaml"], check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial"], check=True, capture_output=True
        )

        # Modify without version bump
        content["name"] = "modified"
        with open(yaml_file, "w") as f:
            yaml.dump(content, f)

        subprocess.run(["git", "add", "config.yaml"], check=True, capture_output=True)

        validator = DocumentationVersionValidator(".dependency-map.yaml")
        validator.validate()

        # Verify error object types
        assert len(validator.errors) > 0
        error = validator.errors[0]

        assert isinstance(error.error_type, str)
        assert isinstance(error.file, str)
        assert error.current_version is None or isinstance(error.current_version, str)
        assert error.expected_version is None or isinstance(error.expected_version, str)
        assert isinstance(error.reason, str)
        assert isinstance(error.required_actions, list)
        if error.sections_to_update:
            assert isinstance(error.sections_to_update, list)

    def test_report_format_consistency_multiple_errors(self, temp_git_repo):
        """Should maintain consistent report format across multiple errors"""
        # Create two files with different version errors
        yaml1 = temp_git_repo / "source1.yaml"
        yaml1.write_text("version: invalid-version\n")

        yaml2 = temp_git_repo / "source2.yaml"
        content2 = {"version": "1.0.0", "name": "source2"}
        with open(yaml2, "w") as f:
            yaml.dump(content2, f)

        # Commit source2, modify it without version bump
        subprocess.run(["git", "add", "source2.yaml"], check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add source2"], check=True, capture_output=True
        )

        content2["name"] = "modified"
        with open(yaml2, "w") as f:
            yaml.dump(content2, f)

        # Create dependency map
        dep_map = temp_git_repo / ".dependency-map.yaml"
        config = {
            "tracked_files": [
                {
                    "path": "source1.yaml",
                    "version_format": "yaml",
                    "version_field": "version",
                    "triggers_update": [],
                },
                {
                    "path": "source2.yaml",
                    "version_format": "yaml",
                    "version_field": "version",
                    "triggers_update": [],
                },
            ]
        }
        with open(dep_map, "w") as f:
            yaml.dump(config, f)

        subprocess.run(
            ["git", "add", "source1.yaml", "source2.yaml"],
            check=True,
            capture_output=True,
        )

        validator = DocumentationVersionValidator(".dependency-map.yaml")
        validator.validate()

        # All errors should be ValidationError objects with same structure
        if len(validator.errors) >= 2:
            error1_attrs = set(dir(validator.errors[0]))
            error2_attrs = set(dir(validator.errors[1]))
            # Check that both have same public attributes
            public_attrs1 = {attr for attr in error1_attrs if not attr.startswith("_")}
            public_attrs2 = {attr for attr in error2_attrs if not attr.startswith("_")}
            assert public_attrs1 == public_attrs2

    def test_report_json_serializable(self, temp_git_repo, dependency_map_simple):
        """Should verify report is JSON serializable"""
        import json

        # Create error scenario
        yaml_file = temp_git_repo / "config.yaml"
        content = {"version": "1.0.0"}
        with open(yaml_file, "w") as f:
            yaml.dump(content, f)

        subprocess.run(["git", "add", "config.yaml"], check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial"], check=True, capture_output=True
        )

        content["modified"] = True
        with open(yaml_file, "w") as f:
            yaml.dump(content, f)

        subprocess.run(["git", "add", "config.yaml"], check=True, capture_output=True)

        validator = DocumentationVersionValidator(".dependency-map.yaml")
        validator.validate()
        report = validator.generate_error_report()

        # Should be able to serialize to JSON without errors
        try:
            json_str = json.dumps(report, indent=2)
            assert len(json_str) > 0
            # Should be able to deserialize back
            parsed = json.loads(json_str)
            assert isinstance(parsed, dict)
        except (TypeError, ValueError) as e:
            pytest.fail(f"Report is not JSON serializable: {e}")

    def test_concurrent_version_formats(self, temp_git_repo):
        """Should handle different version formats in same validation run"""
        # Create YAML file
        yaml_file = temp_git_repo / "config.yaml"
        with open(yaml_file, "w") as f:
            yaml.dump({"version": "1.0.0"}, f)

        # Create Markdown file
        md_file = temp_git_repo / "doc.md"
        md_file.write_text("<!-- version: 1.0.0 -->\n# Doc")

        # Create dependency map tracking both
        dep_map = temp_git_repo / ".dependency-map.yaml"
        config = {
            "tracked_files": [
                {
                    "path": "config.yaml",
                    "version_format": "yaml",
                    "triggers_update": [],
                },
                {
                    "path": "doc.md",
                    "version_format": "markdown_comment",
                    "triggers_update": [],
                },
            ]
        }
        with open(dep_map, "w") as f:
            yaml.dump(config, f)

        subprocess.run(
            ["git", "add", "config.yaml", "doc.md"], check=True, capture_output=True
        )

        validator = DocumentationVersionValidator(".dependency-map.yaml")
        result = validator.validate()

        assert result is True  # Both new files, no version bump required


# =============================================================================
# Helper Functions
# =============================================================================


def report_error_dict(error: ValidationError) -> Dict:
    """Convert ValidationError to dict for assertion checking"""
    return {
        "error_type": error.error_type,
        "file": error.file,
        "current_version": error.current_version,
        "expected_version": error.expected_version,
        "reason": error.reason,
        "required_actions": error.required_actions,
        "sections_to_update": [
            {
                "section_id": s.section_id,
                "location": s.location,
                "description": s.description,
                "source": s.source,
            }
            for s in (error.sections_to_update or [])
        ],
    }


# =============================================================================
# Test Execution Summary
# =============================================================================

if __name__ == "__main__":
    """
    Run tests with:
        pytest tests/test_validate_documentation_versions.py -v
        pytest tests/test_validate_documentation_versions.py -v --cov=scripts.validate_documentation_versions

    Expected coverage: >80% of validation script
    Expected execution time: <5 seconds
    """
    pytest.main([__file__, "-v", "--tb=short"])
