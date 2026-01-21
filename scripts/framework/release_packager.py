"""Release packaging and validation system for nWave Framework."""

import json
import hashlib
import os
import shutil
import zipfile
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from enum import Enum


class Platform(Enum):
    """Supported platforms for release packages."""
    CLAUDE_CODE = "claude-code"
    CODEX = "codex"


@dataclass
class BuildValidationResult:
    """Result of build output validation."""
    valid: bool
    missing_files: List[str]
    error_message: Optional[str] = None


@dataclass
class ArchiveMetadata:
    """Metadata for generated archives."""
    platform: str
    version: str
    filename: str
    checksum: str
    size_bytes: int


class BuildValidator:
    """Validates that build outputs exist before packaging."""

    REQUIRED_ARTIFACTS = {
        Platform.CLAUDE_CODE: [
            "nWave/agents",
            "nWave/tasks",
            "nWave/templates",
            "nWave/data",
            "nWave/validators",
            "nWave/hooks",
            "nWave/framework-catalog.yaml",
            "tools/installers",
            "README.md",
        ],
        Platform.CODEX: [
            "nWave/data",
            "nWave/templates",
            "nWave/validators",
            "nWave/hooks",
            "docs",
            "tools/installers",
            "README.md",
        ],
    }

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)

    def validate_build_outputs(self) -> BuildValidationResult:
        """Validate that all required build artifacts exist."""
        missing_files = []

        # Check for both platform requirements
        for platform in Platform:
            required = self.REQUIRED_ARTIFACTS[platform]
            for artifact in required:
                artifact_path = self.project_root / artifact
                if not artifact_path.exists():
                    missing_files.append(f"{platform.value}: {artifact}")

        if missing_files:
            error_msg = (
                "Build validation failed. The following artifacts are missing:\n"
                + "\n".join(f"  - {f}" for f in missing_files)
            )
            return BuildValidationResult(
                valid=False,
                missing_files=missing_files,
                error_message=error_msg,
            )

        return BuildValidationResult(valid=True, missing_files=[])


class VersionReader:
    """Reads version from framework-catalog.yaml."""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.catalog_path = self.project_root / "nWave" / "framework-catalog.yaml"

    def read_version(self) -> str:
        """Read version from framework-catalog.yaml."""
        if not self.catalog_path.exists():
            raise FileNotFoundError(f"Catalog not found: {self.catalog_path}")

        import yaml

        with open(self.catalog_path) as f:
            catalog = yaml.safe_load(f)

        version = catalog.get("version")
        if not version:
            raise ValueError("Version not found in framework-catalog.yaml")

        return version


class ArchiveCreator:
    """Creates ZIP archives for release packages."""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.dist_dir = self.project_root / "dist"

    def ensure_dist_directory(self):
        """Ensure dist directory exists."""
        self.dist_dir.mkdir(parents=True, exist_ok=True)

    def create_claude_code_archive(self, version: str) -> str:
        """Create archive for Claude Code platform."""
        self.ensure_dist_directory()
        archive_name = f"nwave-claude-code-{version}.zip"
        archive_path = self.dist_dir / archive_name

        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # Add agents
            agents_dir = self.project_root / "nWave" / "agents"
            if agents_dir.exists():
                for agent_file in agents_dir.glob("**/*.yaml"):
                    arcname = f"nWave/agents/{agent_file.relative_to(agents_dir)}"
                    zf.write(agent_file, arcname)

            # Add tasks
            tasks_dir = self.project_root / "nWave" / "tasks"
            if tasks_dir.exists():
                for task_file in tasks_dir.glob("**/*.md"):
                    arcname = f"nWave/tasks/{task_file.relative_to(tasks_dir)}"
                    zf.write(task_file, arcname)

            # Add framework catalog
            catalog = self.project_root / "nWave" / "framework-catalog.yaml"
            if catalog.exists():
                zf.write(catalog, "nWave/framework-catalog.yaml")

            # Add templates
            templates_dir = self.project_root / "nWave" / "templates"
            if templates_dir.exists():
                for template_file in templates_dir.glob("**/*"):
                    if template_file.is_file():
                        arcname = f"nWave/templates/{template_file.relative_to(templates_dir)}"
                        zf.write(template_file, arcname)

            # Add data
            data_dir = self.project_root / "nWave" / "data"
            if data_dir.exists():
                for data_file in data_dir.glob("**/*"):
                    if data_file.is_file():
                        arcname = f"nWave/data/{data_file.relative_to(data_dir)}"
                        zf.write(data_file, arcname)

            # Add validators
            validators_dir = self.project_root / "nWave" / "validators"
            if validators_dir.exists():
                for validator_file in validators_dir.glob("**/*.py"):
                    arcname = f"nWave/validators/{validator_file.relative_to(validators_dir)}"
                    zf.write(validator_file, arcname)

            # Add hooks
            hooks_dir = self.project_root / "nWave" / "hooks"
            if hooks_dir.exists():
                for hook_file in hooks_dir.glob("**/*.py"):
                    arcname = f"nWave/hooks/{hook_file.relative_to(hooks_dir)}"
                    zf.write(hook_file, arcname)

            # Add installers
            installers_dir = self.project_root / "tools" / "installers"
            if installers_dir.exists():
                for installer in installers_dir.glob("**/*"):
                    if installer.is_file():
                        arcname = f"tools/installers/{installer.relative_to(installers_dir)}"
                        zf.write(installer, arcname)

            # Add documentation and version file
            readme = self.project_root / "README.md"
            if readme.exists():
                zf.write(readme, "README.md")

            version_file_content = f"nWave Framework v{version}"
            zf.writestr("VERSION.txt", version_file_content)

        return str(archive_path)

    def create_codex_archive(self, version: str) -> str:
        """Create archive for Codex platform."""
        self.ensure_dist_directory()
        archive_name = f"nwave-codex-{version}.zip"
        archive_path = self.dist_dir / archive_name

        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # Add data
            data_dir = self.project_root / "nWave" / "data"
            if data_dir.exists():
                for data_file in data_dir.glob("**/*"):
                    if data_file.is_file():
                        arcname = f"nWave/data/{data_file.relative_to(data_dir)}"
                        zf.write(data_file, arcname)

            # Add templates
            templates_dir = self.project_root / "nWave" / "templates"
            if templates_dir.exists():
                for template_file in templates_dir.glob("**/*"):
                    if template_file.is_file():
                        arcname = f"nWave/templates/{template_file.relative_to(templates_dir)}"
                        zf.write(template_file, arcname)

            # Add validators
            validators_dir = self.project_root / "nWave" / "validators"
            if validators_dir.exists():
                for validator_file in validators_dir.glob("**/*.py"):
                    arcname = f"nWave/validators/{validator_file.relative_to(validators_dir)}"
                    zf.write(validator_file, arcname)

            # Add hooks
            hooks_dir = self.project_root / "nWave" / "hooks"
            if hooks_dir.exists():
                for hook_file in hooks_dir.glob("**/*.py"):
                    arcname = f"nWave/hooks/{hook_file.relative_to(hooks_dir)}"
                    zf.write(hook_file, arcname)

            # Add docs
            docs_dir = self.project_root / "docs"
            if docs_dir.exists():
                for doc_file in docs_dir.glob("**/*"):
                    if doc_file.is_file():
                        arcname = f"docs/{doc_file.relative_to(docs_dir)}"
                        zf.write(doc_file, arcname)

            # Add installers
            installers_dir = self.project_root / "tools" / "installers"
            if installers_dir.exists():
                for installer in installers_dir.glob("**/*"):
                    if installer.is_file():
                        arcname = f"tools/installers/{installer.relative_to(installers_dir)}"
                        zf.write(installer, arcname)

            # Add documentation and version file
            readme = self.project_root / "README.md"
            if readme.exists():
                zf.write(readme, "README.md")

            version_file_content = f"nWave Framework v{version}"
            zf.writestr("VERSION.txt", version_file_content)

        return str(archive_path)


class ChecksumGenerator:
    """Generates SHA256 checksums for release archives."""

    @staticmethod
    def generate_checksum(file_path: Path) -> str:
        """Generate SHA256 checksum for a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    @staticmethod
    def generate_checksums_file(
        archive_paths: List[str], output_path: Path
    ) -> str:
        """Generate checksums file in standard format."""
        checksums = {}
        for archive_path in archive_paths:
            path = Path(archive_path)
            checksum = ChecksumGenerator.generate_checksum(path)
            checksums[path.name] = checksum

        checksums_json = json.dumps(checksums, indent=2)

        # Write JSON format
        json_path = output_path / "CHECKSUMS.json"
        with open(json_path, "w") as f:
            f.write(checksums_json)

        # Write standard sha256sum format for compatibility
        sha256_path = output_path / "SHA256SUMS"
        with open(sha256_path, "w") as f:
            for filename, checksum in checksums.items():
                f.write(f"{checksum}  {filename}\n")

        return str(json_path)


class ReadmeGenerator:
    """Generates platform-specific README files."""

    INSTALLATION_TEMPLATES = {
        Platform.CLAUDE_CODE: """# nWave Framework - Claude Code Installation

## Quick Start

### Installation

1. Extract the archive to your desired location:
   ```bash
   unzip nwave-claude-code-{version}.zip -d /path/to/installation
   ```

2. Set up your environment:
   ```bash
   cd /path/to/installation
   pip install -r requirements.txt
   ```

3. Configure Claude Code integration:
   ```bash
   export CLAUDE_CODE_PATH="/path/to/installation"
   ```

### Platform Selection

This package supports multiple platforms. Select your installation method:

- **Unix/Linux**: Use the bash installer scripts in `tools/installers/`
- **Windows**: Use the PowerShell installer scripts in `tools/installers/`
- **Python**: Use the Python-based installation for platform-agnostic setup

### Verification

Verify your installation:
```bash
python -m nWave --version
```

Expected output: `nWave Framework v{version}`

## Documentation

For complete documentation, refer to:
- Main documentation: See included `README.md`
- Framework guide: See `nWave/README.md`
- API reference: See `nWave/data/` directory

## Support

For issues and support, refer to the official documentation and community resources.
""",
        Platform.CODEX: """# nWave Framework - Codex Installation

## Quick Start

### Installation

1. Extract the archive:
   ```bash
   unzip nwave-codex-{version}.zip -d /path/to/codex/extensions
   ```

2. Register the extension:
   ```bash
   codex register /path/to/codex/extensions/nwave
   ```

3. Activate the framework:
   ```bash
   codex activate nwave
   ```

### Platform Selection

The Codex platform provides integrated architecture visualization and documentation.

Select features:
- **Templates**: Highly interactive workflow templates
- **Validators**: Automated framework compliance checking
- **Data**: Comprehensive methodology knowledge base

### Verification

Verify installation:
```bash
codex extension info nwave
```

Expected output should show version: {version}

## Documentation

Comprehensive documentation available in the `docs/` directory:
- Architecture patterns: `docs/architecture/`
- Implementation guides: `docs/guides/`
- Best practices: `docs/practices/`

## Configuration

Configuration files are located in `nWave/templates/` and `nWave/data/`.

## Support

Refer to the integrated documentation and configuration guides.
""",
    }

    @staticmethod
    def generate_readme(
        platform: Platform, version: str, output_path: Path
    ) -> str:
        """Generate platform-specific README."""
        template = ReadmeGenerator.INSTALLATION_TEMPLATES[platform]
        content = template.format(version=version)

        readme_path = output_path / f"INSTALL-{platform.value.upper()}.md"
        with open(readme_path, "w") as f:
            f.write(content)

        return str(readme_path)


class ReleasePackager:
    """Main orchestrator for release packaging."""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.builder = BuildValidator(self.project_root)
        self.version_reader = VersionReader(self.project_root)
        self.archive_creator = ArchiveCreator(self.project_root)
        self.checksum_gen = ChecksumGenerator()
        self.readme_gen = ReadmeGenerator()
        self.dist_dir = self.project_root / "dist"

    def package_release(self) -> Dict:
        """Execute complete release packaging workflow."""
        # Validate build outputs
        validation = self.builder.validate_build_outputs()
        if not validation.valid:
            raise RuntimeError(validation.error_message)

        # Read version
        version = self.version_reader.read_version()

        # Create archives
        claude_code_archive = self.archive_creator.create_claude_code_archive(
            version
        )
        codex_archive = self.archive_creator.create_codex_archive(version)

        # Generate checksums
        self.dist_dir.mkdir(parents=True, exist_ok=True)
        self.checksum_gen.generate_checksums_file(
            [claude_code_archive, codex_archive], self.dist_dir
        )

        # Generate READMEs
        self.readme_gen.generate_readme(Platform.CLAUDE_CODE, version, self.dist_dir)
        self.readme_gen.generate_readme(Platform.CODEX, version, self.dist_dir)

        return {
            "version": version,
            "platforms": [
                {
                    "name": Platform.CLAUDE_CODE.value,
                    "archive": claude_code_archive,
                    "checksum": self.checksum_gen.generate_checksum(Path(claude_code_archive)),
                },
                {
                    "name": Platform.CODEX.value,
                    "archive": codex_archive,
                    "checksum": self.checksum_gen.generate_checksum(Path(codex_archive)),
                },
            ],
            "checksums_file": str(self.dist_dir / "CHECKSUMS.json"),
        }
