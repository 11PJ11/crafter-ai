"""
Tests for devop-reviewer roundtrip validation.
Step 08-03: Validate semantic equivalence between MD and TOON.

TDD Phase: Tests that verify MD → TOON preserves all semantic content.
"""
import pytest
import os
import re

# Paths
MD_FILE = "nWave/agents/devop-reviewer.md"
TOON_FILE = "nWave/agents/devop-reviewer.toon"


class TestFilesExist:
    """Verify both source files exist for comparison."""

    def test_md_file_exists(self):
        """MD source file exists."""
        assert os.path.exists(MD_FILE), f"MD file not found: {MD_FILE}"

    def test_toon_file_exists(self):
        """TOON file exists."""
        assert os.path.exists(TOON_FILE), f"TOON file not found: {TOON_FILE}"


class TestAgentIdentity:
    """Verify agent identity preserved."""

    @pytest.fixture
    def md_content(self):
        """Load MD content."""
        with open(MD_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    @pytest.fixture
    def toon_content(self):
        """Load TOON content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_agent_name_preserved(self, md_content, toon_content):
        """Agent name 'devop-reviewer' preserved."""
        assert 'devop-reviewer' in md_content.lower()
        assert 'devop-reviewer' in toon_content.lower()

    def test_persona_name_preserved(self, md_content, toon_content):
        """Persona name 'Dakota' preserved."""
        assert 'Dakota' in md_content
        assert 'Dakota' in toon_content

    def test_icon_preserved(self, md_content, toon_content):
        """Icon preserved."""
        # Both should have rocket icon
        assert '🚀' in md_content
        assert '🚀' in toon_content

    def test_model_haiku_preserved(self, md_content, toon_content):
        """Model haiku preserved."""
        assert 'haiku' in md_content.lower()
        assert 'haiku' in toon_content.lower()


class TestCorePrinciples:
    """Verify core principles preserved."""

    @pytest.fixture
    def md_content(self):
        """Load MD content."""
        with open(MD_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    @pytest.fixture
    def toon_content(self):
        """Load TOON content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_token_economy_preserved(self, md_content, toon_content):
        """Token Economy principle preserved."""
        assert 'Token Economy' in md_content
        assert 'Token Economy' in toon_content

    def test_document_control_preserved(self, md_content, toon_content):
        """Document Control principle preserved."""
        # Both should mention document control
        assert 'Document' in md_content
        assert 'Document' in toon_content

    def test_production_readiness_preserved(self, md_content, toon_content):
        """Production Readiness Validation preserved."""
        assert 'Production' in md_content
        assert 'Production' in toon_content


class TestCommands:
    """Verify commands preserved."""

    @pytest.fixture
    def md_content(self):
        """Load MD content."""
        with open(MD_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    @pytest.fixture
    def toon_content(self):
        """Load TOON content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_help_command_preserved(self, md_content, toon_content):
        """Help command preserved."""
        assert 'help' in md_content.lower()
        assert 'help' in toon_content.lower()

    def test_validate_completion_preserved(self, md_content, toon_content):
        """validate-completion command preserved."""
        assert 'validate-completion' in md_content
        assert 'validate-completion' in toon_content

    def test_exit_command_preserved(self, md_content, toon_content):
        """Exit command preserved."""
        assert 'exit' in md_content.lower()
        assert 'exit' in toon_content.lower()

    def test_demonstrate_value_preserved(self, md_content, toon_content):
        """demonstrate-value command preserved."""
        assert 'demonstrate-value' in md_content
        assert 'demonstrate-value' in toon_content


class TestReviewerSpecialization:
    """Verify reviewer-specific content preserved."""

    @pytest.fixture
    def md_content(self):
        """Load MD content."""
        with open(MD_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    @pytest.fixture
    def toon_content(self):
        """Load TOON content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_cost_efficiency_preserved(self, md_content, toon_content):
        """Cost efficiency mention preserved."""
        assert 'cost' in md_content.lower()
        assert 'cost' in toon_content.lower()

    def test_review_expert_preserved(self, md_content, toon_content):
        """Review expert role preserved."""
        # Both should mention review
        assert 'review' in md_content.lower()
        assert 'review' in toon_content.lower()


class TestDeploymentContent:
    """Verify deployment-related content preserved."""

    @pytest.fixture
    def md_content(self):
        """Load MD content."""
        with open(MD_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    @pytest.fixture
    def toon_content(self):
        """Load TOON content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_deployment_preserved(self, md_content, toon_content):
        """Deployment content preserved."""
        assert 'deployment' in md_content.lower()
        assert 'deployment' in toon_content.lower()

    def test_rollback_preserved(self, md_content, toon_content):
        """Rollback content preserved."""
        assert 'rollback' in md_content.lower()
        assert 'rollback' in toon_content.lower()

    def test_canary_preserved(self, md_content, toon_content):
        """Canary deployment preserved."""
        assert 'canary' in md_content.lower()
        assert 'canary' in toon_content.lower()


class TestSafetyFramework:
    """Verify safety framework preserved."""

    @pytest.fixture
    def md_content(self):
        """Load MD content."""
        with open(MD_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    @pytest.fixture
    def toon_content(self):
        """Load TOON content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_safety_framework_preserved(self, md_content, toon_content):
        """Safety framework preserved."""
        assert 'safety' in md_content.lower()
        assert 'safety' in toon_content.lower()

    def test_tool_restrictions_preserved(self, md_content, toon_content):
        """Tool restrictions preserved."""
        # Both should mention allowed/forbidden tools
        assert 'Read' in md_content and 'Read' in toon_content
        assert 'Write' in md_content and 'Write' in toon_content


class TestTOONCompression:
    """Verify TOON achieves compression while preserving content."""

    def test_toon_smaller_bytes(self):
        """TOON file is smaller in bytes."""
        md_size = os.path.getsize(MD_FILE)
        toon_size = os.path.getsize(TOON_FILE)
        assert toon_size < md_size

    def test_toon_fewer_lines(self):
        """TOON has fewer lines."""
        with open(MD_FILE, 'r', encoding='utf-8') as f:
            md_lines = len(f.readlines())
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            toon_lines = len(f.readlines())
        assert toon_lines < md_lines

    def test_compression_ratio_reasonable(self):
        """Compression ratio is reasonable (>2:1)."""
        md_size = os.path.getsize(MD_FILE)
        toon_size = os.path.getsize(TOON_FILE)
        ratio = md_size / toon_size
        assert ratio > 2.0, f"Compression ratio {ratio:.2f}:1 below minimum 2:1"
