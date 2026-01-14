"""
Tests for devop roundtrip validation (MD <-> TOON equivalence).
Step 07-03: Roundtrip validation for devop.

TDD Phase: RED - Tests written before verification.
"""
import pytest
import os
import re

# Paths
MD_FILE = "nWave/agents/devop.md"
TOON_FILE = "nWave/agents/devop.toon"


class TestFilesExist:
    """Verify both source files exist."""

    def test_md_file_exists(self):
        """MD source file exists."""
        assert os.path.exists(MD_FILE), f"MD file not found: {MD_FILE}"

    def test_toon_file_exists(self):
        """TOON file exists."""
        assert os.path.exists(TOON_FILE), f"TOON file not found: {TOON_FILE}"


class TestIdentityPreserved:
    """Verify agent identity is preserved."""

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
        """Agent name 'devop' preserved."""
        assert 'devop' in md_content.lower()
        assert 'devop' in toon_content.lower()

    def test_persona_name_preserved(self, md_content, toon_content):
        """Persona name 'Dakota' preserved."""
        assert 'Dakota' in md_content
        assert 'Dakota' in toon_content

    def test_title_preserved(self, md_content, toon_content):
        """Title preserved."""
        assert 'Feature Completion' in md_content
        assert 'Feature Completion' in toon_content

    def test_icon_preserved(self, md_content, toon_content):
        """Rocket icon preserved."""
        assert '\U0001F680' in md_content  # Rocket emoji
        assert '\U0001F680' in toon_content


class TestCommandsPreserved:
    """Verify all commands are preserved."""

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

    def test_exit_command_preserved(self, md_content, toon_content):
        """Exit command preserved."""
        assert 'exit' in md_content.lower()
        assert 'exit' in toon_content.lower()

    def test_validate_completion_preserved(self, md_content, toon_content):
        """validate-completion command preserved."""
        assert 'validate-completion' in md_content.lower()
        assert 'validate-completion' in toon_content.lower()

    def test_orchestrate_deployment_preserved(self, md_content, toon_content):
        """orchestrate-deployment command preserved."""
        assert 'orchestrate-deployment' in md_content.lower()
        assert 'orchestrate-deployment' in toon_content.lower()

    def test_demonstrate_value_preserved(self, md_content, toon_content):
        """demonstrate-value command preserved."""
        assert 'demonstrate-value' in md_content.lower()
        assert 'demonstrate-value' in toon_content.lower()

    def test_validate_production_preserved(self, md_content, toon_content):
        """validate-production command preserved."""
        assert 'validate-production' in md_content.lower()
        assert 'validate-production' in toon_content.lower()


class TestCorePrinciplesPreserved:
    """Verify core principles are preserved."""

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
        assert 'token' in md_content.lower()
        assert 'token' in toon_content.lower()

    def test_document_control_preserved(self, md_content, toon_content):
        """Document Control principle preserved."""
        assert 'document' in md_content.lower()
        assert 'document' in toon_content.lower()

    def test_production_readiness_preserved(self, md_content, toon_content):
        """Production Readiness principle preserved."""
        assert 'production' in md_content.lower()
        assert 'production' in toon_content.lower()


class TestDependenciesPreserved:
    """Verify dependencies are preserved."""

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

    def test_tasks_dependency_preserved(self, md_content, toon_content):
        """Tasks dependency preserved."""
        assert 'demo.md' in md_content
        assert 'demo.md' in toon_content

    def test_checklists_preserved(self, md_content, toon_content):
        """Checklists preserved."""
        assert 'checklist' in md_content.lower()
        assert 'checklist' in toon_content.lower()


class TestWaveInformationPreserved:
    """Verify wave information is preserved."""

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

    def test_deliver_wave_preserved(self, md_content, toon_content):
        """DELIVER wave preserved."""
        assert 'DELIVER' in md_content
        assert 'DELIVER' in toon_content

    def test_develop_wave_orchestration_preserved(self, md_content, toon_content):
        """DEVELOP wave orchestration preserved."""
        assert 'DEVELOP' in md_content
        assert 'DEVELOP' in toon_content


class TestProductionFrameworksPreserved:
    """Verify production frameworks are preserved."""

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

    def test_observability_preserved(self, md_content, toon_content):
        """Observability preserved."""
        assert 'observability' in md_content.lower()
        assert 'observability' in toon_content.lower()

    def test_error_recovery_preserved(self, md_content, toon_content):
        """Error recovery preserved."""
        assert 'error' in md_content.lower() and 'recovery' in md_content.lower()
        assert 'error' in toon_content.lower() and 'recovery' in toon_content.lower()


class TestModelConfiguration:
    """Verify model configuration is preserved."""

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

    def test_model_inherit_preserved(self, md_content, toon_content):
        """Model: inherit preserved."""
        assert 'model:' in md_content.lower() and 'inherit' in md_content.lower()
        assert 'model:' in toon_content.lower() and 'inherit' in toon_content.lower()
