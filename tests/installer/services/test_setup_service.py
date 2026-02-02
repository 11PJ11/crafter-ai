"""Tests for SetupService application service.

TDD approach: Tests verify setup logic using InMemoryFileSystemAdapter
for isolated testing without real file system operations.
"""

from pathlib import Path

from crafter_ai.installer.services.setup_service import (
    DEFAULT_CLAUDE_LOCAL_MD,
    DEFAULT_CLAUDE_MD,
    SetupResult,
    SetupService,
)

# Import from conftest for isolated testing
from tests.installer.conftest import InMemoryFileSystemAdapter


class TestSetupResultDataclass:
    """Test SetupResult dataclass structure."""

    def test_setup_result_has_success_field(self) -> None:
        """SetupResult should have a success boolean field."""
        result = SetupResult(success=True)
        assert hasattr(result, "success")
        assert result.success is True

    def test_setup_result_has_created_paths_field(self) -> None:
        """SetupResult should have created_paths list field."""
        result = SetupResult(success=True)
        assert hasattr(result, "created_paths")
        assert isinstance(result.created_paths, list)

    def test_setup_result_has_errors_field(self) -> None:
        """SetupResult should have errors list field."""
        result = SetupResult(success=True)
        assert hasattr(result, "errors")
        assert isinstance(result.errors, list)

    def test_setup_result_defaults_to_empty_lists(self) -> None:
        """SetupResult should default to empty lists."""
        result = SetupResult(success=True)
        assert result.created_paths == []
        assert result.errors == []


class TestSetupServiceInit:
    """Test SetupService initialization."""

    def test_setup_service_accepts_filesystem_port(self) -> None:
        """SetupService should accept FileSystemPort in constructor."""
        filesystem = InMemoryFileSystemAdapter()
        service = SetupService(filesystem)
        assert service is not None


class TestSetupServiceClaudeConfig:
    """Test setup_claude_config() for user-level ~/.claude/ setup."""

    def test_creates_claude_directory(self) -> None:
        """setup_claude_config should create ~/.claude/ directory."""
        filesystem = InMemoryFileSystemAdapter()
        service = SetupService(filesystem)
        home_dir = Path("/home/testuser")

        result = service.setup_claude_config(home_dir)

        assert result.success is True
        assert filesystem.exists(home_dir / ".claude")

    def test_creates_commands_directory(self) -> None:
        """setup_claude_config should create ~/.claude/commands/ directory."""
        filesystem = InMemoryFileSystemAdapter()
        service = SetupService(filesystem)
        home_dir = Path("/home/testuser")

        result = service.setup_claude_config(home_dir)

        assert result.success is True
        assert filesystem.exists(home_dir / ".claude" / "commands")

    def test_creates_claude_md_file(self) -> None:
        """setup_claude_config should create ~/.claude/CLAUDE.md file."""
        filesystem = InMemoryFileSystemAdapter()
        service = SetupService(filesystem)
        home_dir = Path("/home/testuser")

        result = service.setup_claude_config(home_dir)

        assert result.success is True
        claude_md = home_dir / ".claude" / "CLAUDE.md"
        assert filesystem.exists(claude_md)
        content = filesystem.read_text(claude_md)
        assert "CLAUDE.md" in content

    def test_reports_created_paths(self) -> None:
        """setup_claude_config should report all created paths."""
        filesystem = InMemoryFileSystemAdapter()
        service = SetupService(filesystem)
        home_dir = Path("/home/testuser")

        result = service.setup_claude_config(home_dir)

        assert len(result.created_paths) == 3
        created_strs = [str(p) for p in result.created_paths]
        assert any(".claude" in s and "commands" not in s for s in created_strs)
        assert any("commands" in s for s in created_strs)
        assert any("CLAUDE.md" in s for s in created_strs)

    def test_skips_existing_directories(self) -> None:
        """setup_claude_config should skip creating existing directories."""
        filesystem = InMemoryFileSystemAdapter()
        service = SetupService(filesystem)
        home_dir = Path("/home/testuser")

        # Pre-create directories
        filesystem.mkdir(home_dir / ".claude", parents=True)
        filesystem.mkdir(home_dir / ".claude" / "commands", parents=True)

        result = service.setup_claude_config(home_dir)

        assert result.success is True
        # Only CLAUDE.md should be reported as created
        assert len(result.created_paths) == 1
        assert "CLAUDE.md" in str(result.created_paths[0])

    def test_skips_existing_claude_md_without_force(self) -> None:
        """setup_claude_config should skip existing CLAUDE.md without force flag."""
        filesystem = InMemoryFileSystemAdapter()
        service = SetupService(filesystem)
        home_dir = Path("/home/testuser")

        # Pre-create everything
        filesystem.mkdir(home_dir / ".claude" / "commands", parents=True)
        filesystem.write_text(home_dir / ".claude" / "CLAUDE.md", "existing content")

        result = service.setup_claude_config(home_dir, force=False)

        assert result.success is True
        assert len(result.created_paths) == 0
        # Content should be unchanged
        content = filesystem.read_text(home_dir / ".claude" / "CLAUDE.md")
        assert content == "existing content"

    def test_overwrites_claude_md_with_force(self) -> None:
        """setup_claude_config should overwrite CLAUDE.md with force flag."""
        filesystem = InMemoryFileSystemAdapter()
        service = SetupService(filesystem)
        home_dir = Path("/home/testuser")

        # Pre-create everything
        filesystem.mkdir(home_dir / ".claude" / "commands", parents=True)
        filesystem.write_text(home_dir / ".claude" / "CLAUDE.md", "old content")

        result = service.setup_claude_config(home_dir, force=True)

        assert result.success is True
        assert len(result.created_paths) == 1
        # Content should be overwritten with default template
        content = filesystem.read_text(home_dir / ".claude" / "CLAUDE.md")
        assert content == DEFAULT_CLAUDE_MD


class TestSetupServiceProjectConfig:
    """Test setup_project_config() for project-level .claude/ setup."""

    def test_creates_project_claude_directory(self) -> None:
        """setup_project_config should create .claude/ directory."""
        filesystem = InMemoryFileSystemAdapter()
        service = SetupService(filesystem)
        project_dir = Path("/projects/my-project")

        result = service.setup_project_config(project_dir)

        assert result.success is True
        assert filesystem.exists(project_dir / ".claude")

    def test_creates_claude_local_md_file(self) -> None:
        """setup_project_config should create .claude/CLAUDE.local.md file."""
        filesystem = InMemoryFileSystemAdapter()
        service = SetupService(filesystem)
        project_dir = Path("/projects/my-project")

        result = service.setup_project_config(project_dir)

        assert result.success is True
        local_md = project_dir / ".claude" / "CLAUDE.local.md"
        assert filesystem.exists(local_md)
        content = filesystem.read_text(local_md)
        assert "CLAUDE.local.md" in content

    def test_reports_created_paths(self) -> None:
        """setup_project_config should report all created paths."""
        filesystem = InMemoryFileSystemAdapter()
        service = SetupService(filesystem)
        project_dir = Path("/projects/my-project")

        result = service.setup_project_config(project_dir)

        assert len(result.created_paths) == 2
        created_strs = [str(p) for p in result.created_paths]
        assert any(".claude" in s and "CLAUDE" not in s for s in created_strs)
        assert any("CLAUDE.local.md" in s for s in created_strs)

    def test_skips_existing_without_force(self) -> None:
        """setup_project_config should skip existing files without force."""
        filesystem = InMemoryFileSystemAdapter()
        service = SetupService(filesystem)
        project_dir = Path("/projects/my-project")

        # Pre-create everything
        filesystem.mkdir(project_dir / ".claude", parents=True)
        filesystem.write_text(project_dir / ".claude" / "CLAUDE.local.md", "existing")

        result = service.setup_project_config(project_dir, force=False)

        assert result.success is True
        assert len(result.created_paths) == 0

    def test_overwrites_with_force(self) -> None:
        """setup_project_config should overwrite with force flag."""
        filesystem = InMemoryFileSystemAdapter()
        service = SetupService(filesystem)
        project_dir = Path("/projects/my-project")

        # Pre-create everything
        filesystem.mkdir(project_dir / ".claude", parents=True)
        filesystem.write_text(project_dir / ".claude" / "CLAUDE.local.md", "old")

        result = service.setup_project_config(project_dir, force=True)

        assert result.success is True
        content = filesystem.read_text(project_dir / ".claude" / "CLAUDE.local.md")
        assert content == DEFAULT_CLAUDE_LOCAL_MD


class TestSetupServiceVerifySetup:
    """Test verify_setup() for checking setup completion."""

    def test_verify_global_setup_success(self) -> None:
        """verify_setup should return success when global setup is complete."""
        filesystem = InMemoryFileSystemAdapter()
        service = SetupService(filesystem)
        home_dir = Path("/home/testuser")

        # Create complete setup
        filesystem.mkdir(home_dir / ".claude" / "commands", parents=True)
        filesystem.write_text(home_dir / ".claude" / "CLAUDE.md", "content")

        result = service.verify_setup(home_dir=home_dir)

        assert result.success is True
        assert len(result.errors) == 0

    def test_verify_global_setup_detects_missing_directory(self) -> None:
        """verify_setup should detect missing .claude directory."""
        filesystem = InMemoryFileSystemAdapter()
        service = SetupService(filesystem)
        home_dir = Path("/home/testuser")

        result = service.verify_setup(home_dir=home_dir)

        assert result.success is False
        assert any(".claude" in error for error in result.errors)

    def test_verify_global_setup_detects_missing_commands(self) -> None:
        """verify_setup should detect missing commands directory."""
        filesystem = InMemoryFileSystemAdapter()
        service = SetupService(filesystem)
        home_dir = Path("/home/testuser")

        # Create .claude but not commands
        filesystem.mkdir(home_dir / ".claude", parents=True)
        filesystem.write_text(home_dir / ".claude" / "CLAUDE.md", "content")

        result = service.verify_setup(home_dir=home_dir)

        assert result.success is False
        assert any("commands" in error for error in result.errors)

    def test_verify_global_setup_detects_missing_claude_md(self) -> None:
        """verify_setup should detect missing CLAUDE.md file."""
        filesystem = InMemoryFileSystemAdapter()
        service = SetupService(filesystem)
        home_dir = Path("/home/testuser")

        # Create directories but not file
        filesystem.mkdir(home_dir / ".claude" / "commands", parents=True)

        result = service.verify_setup(home_dir=home_dir)

        assert result.success is False
        assert any("CLAUDE.md" in error for error in result.errors)

    def test_verify_project_setup_success(self) -> None:
        """verify_setup should return success when project setup is complete."""
        filesystem = InMemoryFileSystemAdapter()
        service = SetupService(filesystem)
        project_dir = Path("/projects/my-project")

        # Create complete setup
        filesystem.mkdir(project_dir / ".claude", parents=True)
        filesystem.write_text(project_dir / ".claude" / "CLAUDE.local.md", "content")

        result = service.verify_setup(project_dir=project_dir)

        assert result.success is True
        assert len(result.errors) == 0

    def test_verify_project_setup_detects_missing_local_md(self) -> None:
        """verify_setup should detect missing CLAUDE.local.md file."""
        filesystem = InMemoryFileSystemAdapter()
        service = SetupService(filesystem)
        project_dir = Path("/projects/my-project")

        # Create directory but not file
        filesystem.mkdir(project_dir / ".claude", parents=True)

        result = service.verify_setup(project_dir=project_dir)

        assert result.success is False
        assert any("CLAUDE.local.md" in error for error in result.errors)

    def test_verify_both_setups(self) -> None:
        """verify_setup should check both global and project when both provided."""
        filesystem = InMemoryFileSystemAdapter()
        service = SetupService(filesystem)
        home_dir = Path("/home/testuser")
        project_dir = Path("/projects/my-project")

        # Create complete setups
        filesystem.mkdir(home_dir / ".claude" / "commands", parents=True)
        filesystem.write_text(home_dir / ".claude" / "CLAUDE.md", "content")
        filesystem.mkdir(project_dir / ".claude", parents=True)
        filesystem.write_text(project_dir / ".claude" / "CLAUDE.local.md", "content")

        result = service.verify_setup(home_dir=home_dir, project_dir=project_dir)

        assert result.success is True
        # Should report all found paths
        assert len(result.created_paths) == 5  # 3 global + 2 project
