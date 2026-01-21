"""Tests for release packaging and validation system."""

import json
import zipfile
from pathlib import Path

import pytest

from scripts.framework.release_packager import (
    BuildValidator,
    VersionReader,
    ArchiveCreator,
    ChecksumGenerator,
    ReadmeGenerator,
    ReleasePackager,
    Platform,
)


class TestBuildValidator:
    """Tests for build output validation."""

    def test_validate_build_outputs_success(self, tmp_path):
        """Test successful build validation when all artifacts exist."""
        # Create required artifacts
        (tmp_path / "nWave" / "agents").mkdir(parents=True, exist_ok=True)
        (tmp_path / "nWave" / "tasks").mkdir(parents=True, exist_ok=True)
        (tmp_path / "nWave" / "templates").mkdir(parents=True, exist_ok=True)
        (tmp_path / "nWave" / "data").mkdir(parents=True, exist_ok=True)
        (tmp_path / "nWave" / "validators").mkdir(parents=True, exist_ok=True)
        (tmp_path / "nWave" / "hooks").mkdir(parents=True, exist_ok=True)
        (tmp_path / "nWave" / "framework-catalog.yaml").touch()
        (tmp_path / "tools" / "installers").mkdir(parents=True, exist_ok=True)
        (tmp_path / "README.md").touch()
        (tmp_path / "docs").mkdir(parents=True, exist_ok=True)

        validator = BuildValidator(tmp_path)
        result = validator.validate_build_outputs()

        assert result.valid is True
        assert result.missing_files == []
        assert result.error_message is None

    def test_validate_build_outputs_missing_artifacts(self, tmp_path):
        """Test validation fails when artifacts are missing."""
        # Create minimal directory
        (tmp_path / "nWave").mkdir(parents=True, exist_ok=True)

        validator = BuildValidator(tmp_path)
        result = validator.validate_build_outputs()

        assert result.valid is False
        assert len(result.missing_files) > 0
        assert result.error_message is not None
        assert "Build validation failed" in result.error_message

    def test_validate_build_outputs_partial_artifacts(self, tmp_path):
        """Test validation fails when only some artifacts exist."""
        # Create partial artifacts
        (tmp_path / "nWave" / "agents").mkdir(parents=True, exist_ok=True)
        (tmp_path / "nWave" / "tasks").mkdir(parents=True, exist_ok=True)
        (tmp_path / "README.md").touch()

        validator = BuildValidator(tmp_path)
        result = validator.validate_build_outputs()

        assert result.valid is False
        assert len(result.missing_files) > 0


class TestVersionReader:
    """Tests for version reading."""

    def test_read_version_success(self, tmp_path):
        """Test successful version reading."""
        # Create framework-catalog.yaml
        catalog_dir = tmp_path / "nWave"
        catalog_dir.mkdir()
        catalog_content = """
name: "nWave"
version: "1.2.57"
description: "Test framework"
"""
        catalog_path = catalog_dir / "framework-catalog.yaml"
        catalog_path.write_text(catalog_content)

        reader = VersionReader(tmp_path)
        version = reader.read_version()

        assert version == "1.2.57"

    def test_read_version_missing_file(self, tmp_path):
        """Test reading version when catalog doesn't exist."""
        reader = VersionReader(tmp_path)

        with pytest.raises(FileNotFoundError):
            reader.read_version()

    def test_read_version_missing_version_key(self, tmp_path):
        """Test reading version when version key is missing."""
        catalog_dir = tmp_path / "nWave"
        catalog_dir.mkdir()
        catalog_content = """
name: "nWave"
description: "Test framework"
"""
        catalog_path = catalog_dir / "framework-catalog.yaml"
        catalog_path.write_text(catalog_content)

        reader = VersionReader(tmp_path)

        with pytest.raises(ValueError, match="Version not found"):
            reader.read_version()


class TestArchiveCreator:
    """Tests for archive creation."""

    def test_ensure_dist_directory(self, tmp_path):
        """Test that dist directory is created."""
        creator = ArchiveCreator(tmp_path)
        creator.ensure_dist_directory()

        assert (tmp_path / "dist").exists()
        assert (tmp_path / "dist").is_dir()

    def test_create_claude_code_archive(self, tmp_path):
        """Test creating Claude Code archive."""
        # Set up required directories and files
        (tmp_path / "nWave" / "agents").mkdir(parents=True, exist_ok=True)
        (tmp_path / "nWave" / "agents" / "test.yaml").write_text("test")
        (tmp_path / "nWave" / "tasks").mkdir(parents=True, exist_ok=True)
        (tmp_path / "nWave" / "templates").mkdir(parents=True, exist_ok=True)
        (tmp_path / "nWave" / "data").mkdir(parents=True, exist_ok=True)
        (tmp_path / "nWave" / "validators").mkdir(parents=True, exist_ok=True)
        (tmp_path / "nWave" / "hooks").mkdir(parents=True, exist_ok=True)
        (tmp_path / "nWave" / "framework-catalog.yaml").write_text("test")
        (tmp_path / "tools" / "installers").mkdir(parents=True, exist_ok=True)
        (tmp_path / "README.md").write_text("# Test")

        creator = ArchiveCreator(tmp_path)
        archive_path = creator.create_claude_code_archive("1.2.57")

        assert Path(archive_path).exists()
        assert archive_path.endswith("nwave-claude-code-1.2.57.zip")

        # Verify archive contents
        with zipfile.ZipFile(archive_path, "r") as zf:
            names = zf.namelist()
            assert any("nWave/agents" in n for n in names)
            assert any("VERSION.txt" in n for n in names)

    def test_create_codex_archive(self, tmp_path):
        """Test creating Codex archive."""
        # Set up required directories and files with content
        (tmp_path / "nWave" / "data").mkdir(parents=True, exist_ok=True)
        (tmp_path / "nWave" / "data" / "test.md").write_text("test")
        (tmp_path / "nWave" / "templates").mkdir(parents=True, exist_ok=True)
        (tmp_path / "nWave" / "templates" / "test.yaml").write_text("test")
        (tmp_path / "nWave" / "validators").mkdir(parents=True, exist_ok=True)
        (tmp_path / "nWave" / "validators" / "test.py").write_text("test")
        (tmp_path / "nWave" / "hooks").mkdir(parents=True, exist_ok=True)
        (tmp_path / "nWave" / "hooks" / "test.py").write_text("test")
        (tmp_path / "docs").mkdir(parents=True, exist_ok=True)
        (tmp_path / "docs" / "test.md").write_text("test")
        (tmp_path / "tools" / "installers").mkdir(parents=True, exist_ok=True)
        (tmp_path / "tools" / "installers" / "test.sh").write_text("test")
        (tmp_path / "README.md").write_text("# Test")

        creator = ArchiveCreator(tmp_path)
        archive_path = creator.create_codex_archive("1.2.57")

        assert Path(archive_path).exists()
        assert archive_path.endswith("nwave-codex-1.2.57.zip")

        # Verify archive contents
        with zipfile.ZipFile(archive_path, "r") as zf:
            names = zf.namelist()
            assert any("nWave/data" in n for n in names)
            assert any("VERSION.txt" in n for n in names)


class TestChecksumGenerator:
    """Tests for checksum generation."""

    def test_generate_checksum(self, tmp_path):
        """Test checksum generation."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        checksum = ChecksumGenerator.generate_checksum(test_file)

        assert isinstance(checksum, str)
        assert len(checksum) == 64  # SHA256 produces 64 hex characters

    def test_generate_checksums_file(self, tmp_path):
        """Test checksums file generation."""
        # Create test files
        file1 = tmp_path / "file1.txt"
        file1.write_text("content1")
        file2 = tmp_path / "file2.txt"
        file2.write_text("content2")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        ChecksumGenerator.generate_checksums_file([str(file1), str(file2)], output_dir)

        # Verify JSON file
        json_file = output_dir / "CHECKSUMS.json"
        assert json_file.exists()

        with open(json_file) as f:
            checksums = json.load(f)
        assert "file1.txt" in checksums
        assert "file2.txt" in checksums

        # Verify SHA256 format file
        sha256_file = output_dir / "SHA256SUMS"
        assert sha256_file.exists()
        content = sha256_file.read_text()
        assert "file1.txt" in content
        assert "file2.txt" in content

    def test_generate_checksum_consistency(self, tmp_path):
        """Test that checksums are consistent."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        checksum1 = ChecksumGenerator.generate_checksum(test_file)
        checksum2 = ChecksumGenerator.generate_checksum(test_file)

        assert checksum1 == checksum2


class TestReadmeGenerator:
    """Tests for README generation."""

    def test_generate_readme_claude_code(self, tmp_path):
        """Test README generation for Claude Code platform."""
        readme_path = ReadmeGenerator.generate_readme(
            Platform.CLAUDE_CODE, "1.2.57", tmp_path
        )

        assert Path(readme_path).exists()
        content = Path(readme_path).read_text()
        assert "Claude Code" in content
        assert "1.2.57" in content
        assert "Installation" in content

    def test_generate_readme_codex(self, tmp_path):
        """Test README generation for Codex platform."""
        readme_path = ReadmeGenerator.generate_readme(
            Platform.CODEX, "1.2.57", tmp_path
        )

        assert Path(readme_path).exists()
        content = Path(readme_path).read_text()
        assert "Codex" in content
        assert "1.2.57" in content
        assert "Installation" in content

    def test_readme_contains_version(self, tmp_path):
        """Test that README contains version number."""
        readme_path = ReadmeGenerator.generate_readme(
            Platform.CLAUDE_CODE, "1.2.57", tmp_path
        )
        content = Path(readme_path).read_text()

        assert "1.2.57" in content


class TestReleasePackager:
    """Tests for complete release packaging workflow."""

    def setup_valid_project(self, tmp_path):
        """Set up a valid project structure."""
        # Create all required directories and files
        (tmp_path / "nWave" / "agents").mkdir(parents=True, exist_ok=True)
        (tmp_path / "nWave" / "agents" / "test.yaml").write_text("test")
        (tmp_path / "nWave" / "tasks").mkdir(parents=True, exist_ok=True)
        (tmp_path / "nWave" / "templates").mkdir(parents=True, exist_ok=True)
        (tmp_path / "nWave" / "data").mkdir(parents=True, exist_ok=True)
        (tmp_path / "nWave" / "validators").mkdir(parents=True, exist_ok=True)
        (tmp_path / "nWave" / "hooks").mkdir(parents=True, exist_ok=True)

        catalog_content = """
name: "nWave"
version: "1.2.57"
description: "Test framework"
"""
        (tmp_path / "nWave" / "framework-catalog.yaml").write_text(catalog_content)
        (tmp_path / "tools" / "installers").mkdir(parents=True, exist_ok=True)
        (tmp_path / "README.md").write_text("# Test")
        (tmp_path / "docs").mkdir(parents=True, exist_ok=True)

    def test_package_release_success(self, tmp_path):
        """Test successful complete release packaging."""
        self.setup_valid_project(tmp_path)

        packager = ReleasePackager(tmp_path)
        result = packager.package_release()

        assert result["version"] == "1.2.57"
        assert len(result["platforms"]) == 2
        assert result["platforms"][0]["name"] == "claude-code"
        assert result["platforms"][1]["name"] == "codex"
        assert "checksums_file" in result

    def test_package_release_invalid_project(self, tmp_path):
        """Test packaging fails when build artifacts missing."""
        packager = ReleasePackager(tmp_path)

        with pytest.raises(RuntimeError, match="Build validation failed"):
            packager.package_release()

    def test_package_release_creates_archives(self, tmp_path):
        """Test that archives are created."""
        self.setup_valid_project(tmp_path)

        packager = ReleasePackager(tmp_path)
        result = packager.package_release()

        archive1 = Path(result["platforms"][0]["archive"])
        archive2 = Path(result["platforms"][1]["archive"])

        assert archive1.exists()
        assert archive2.exists()

    def test_package_release_checksums(self, tmp_path):
        """Test that checksums are generated."""
        self.setup_valid_project(tmp_path)

        packager = ReleasePackager(tmp_path)
        result = packager.package_release()

        assert result["platforms"][0]["checksum"]
        assert result["platforms"][1]["checksum"]
        assert len(result["platforms"][0]["checksum"]) == 64  # SHA256


class TestBuildValidationIntegration:
    """Integration tests for build validation."""

    def test_build_validation_error_message(self, tmp_path):
        """Test that build validation provides clear error messages."""
        # Create minimal structure
        (tmp_path / "nWave").mkdir()

        validator = BuildValidator(tmp_path)
        result = validator.validate_build_outputs()

        assert not result.valid
        assert "Build validation failed" in result.error_message
        assert "missing" in result.error_message.lower()


class TestVersionConsistency:
    """Tests for version consistency across packaging."""

    def test_version_in_filenames(self, tmp_path):
        """Test that version appears in archive filenames."""
        self.setup_valid_project(tmp_path)

        packager = ReleasePackager(tmp_path)
        result = packager.package_release()

        assert "1.2.57" in result["platforms"][0]["archive"]
        assert "1.2.57" in result["platforms"][1]["archive"]

    def test_version_in_archives(self, tmp_path):
        """Test that version file is in archives."""
        self.setup_valid_project(tmp_path)

        packager = ReleasePackager(tmp_path)
        result = packager.package_release()

        archive_path = Path(result["platforms"][0]["archive"])
        with zipfile.ZipFile(archive_path, "r") as zf:
            version_file = zf.read("VERSION.txt").decode("utf-8")
            assert "1.2.57" in version_file

    def setup_valid_project(self, tmp_path):
        """Set up a valid project structure."""
        # Create all required directories and files
        (tmp_path / "nWave" / "agents").mkdir(parents=True, exist_ok=True)
        (tmp_path / "nWave" / "agents" / "test.yaml").write_text("test")
        (tmp_path / "nWave" / "tasks").mkdir(parents=True, exist_ok=True)
        (tmp_path / "nWave" / "templates").mkdir(parents=True, exist_ok=True)
        (tmp_path / "nWave" / "data").mkdir(parents=True, exist_ok=True)
        (tmp_path / "nWave" / "validators").mkdir(parents=True, exist_ok=True)
        (tmp_path / "nWave" / "hooks").mkdir(parents=True, exist_ok=True)

        catalog_content = """
name: "nWave"
version: "1.2.57"
description: "Test framework"
"""
        (tmp_path / "nWave" / "framework-catalog.yaml").write_text(catalog_content)
        (tmp_path / "tools" / "installers").mkdir(parents=True, exist_ok=True)
        (tmp_path / "README.md").write_text("# Test")
        (tmp_path / "docs").mkdir(parents=True, exist_ok=True)
