#!/usr/bin/env python3
"""
Documentation Version Validation

Ensures documentation stays synchronized with source configurations via version tracking.

Usage:
    Called automatically by pre-commit hook
    Can also run manually: python3 scripts/validate-documentation-versions.py

Exit Codes:
    0 - All validations passed
    1 - Validation failures (commit should be blocked)
    2 - Configuration error (dependency map missing/invalid)
"""

import sys
import json
import yaml
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from packaging import version

# =============================================================================
# Data Models
# =============================================================================


@dataclass
class SectionUpdate:
    """Represents a section that needs updating in a dependent file"""

    section_id: str
    location: str
    description: str
    source: str
    update_instructions: str = ""


@dataclass
class ValidationError:
    """Represents a validation error"""

    error_type: str  # "VERSION_NOT_BUMPED" | "DEPENDENT_OUTDATED" | "INVALID_VERSION"
    file: str
    current_version: Optional[str]
    expected_version: Optional[str] = None
    reason: str = ""
    sections_to_update: List[SectionUpdate] = None
    required_actions: List[str] = None

    def __post_init__(self):
        if self.sections_to_update is None:
            self.sections_to_update = []
        if self.required_actions is None:
            self.required_actions = []


@dataclass
class TrackedFile:
    """Represents a file tracked in dependency map"""

    path: str
    version_format: str
    version_field: Optional[str]
    triggers_update: List[Dict]
    description: str = ""


# =============================================================================
# Version Parser
# =============================================================================


class VersionParser:
    """Parse version strings from different file formats"""

    @staticmethod
    def parse_yaml_version(file_path: Path, field: str = "version") -> Optional[str]:
        """Extract version from YAML file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data.get(field)
        except Exception as e:
            print(
                f"Warning: Failed to parse YAML version from {file_path}: {e}",
                file=sys.stderr,
            )
            return None

    @staticmethod
    def parse_markdown_version(file_path: Path) -> Optional[str]:
        """Extract version from Markdown HTML comment"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                # Only check first 2000 characters for performance
                content = f.read(2000)
                match = re.search(
                    r"<!--\s*version:\s*([0-9]+\.[0-9]+\.[0-9]+)\s*-->", content
                )
                return match.group(1) if match else None
        except Exception as e:
            print(
                f"Warning: Failed to parse Markdown version from {file_path}: {e}",
                file=sys.stderr,
            )
            return None

    @staticmethod
    def parse_version(
        file_path: Path, format_type: str, field: Optional[str] = None
    ) -> Optional[str]:
        """Parse version based on file format"""
        if format_type == "yaml":
            return VersionParser.parse_yaml_version(file_path, field or "version")
        elif format_type == "markdown_comment":
            return VersionParser.parse_markdown_version(file_path)
        else:
            print(f"Warning: Unknown version format: {format_type}", file=sys.stderr)
            return None

    @staticmethod
    def validate_version_format(version_str: str) -> bool:
        """Validate semantic version format"""
        try:
            version.parse(version_str)
            return True
        except Exception:
            return False

    @staticmethod
    def compare_versions(v1: str, v2: str) -> int:
        """Compare two semantic versions. Returns: -1 if v1<v2, 0 if equal, 1 if v1>v2"""
        try:
            ver1 = version.parse(v1)
            ver2 = version.parse(v2)
            if ver1 < ver2:
                return -1
            elif ver1 > ver2:
                return 1
            else:
                return 0
        except Exception as e:
            print(
                f"Warning: Version comparison failed for {v1} vs {v2}: {e}",
                file=sys.stderr,
            )
            return 0


# =============================================================================
# Git Integration
# =============================================================================


class GitHelper:
    """Helper methods for Git operations"""

    @staticmethod
    def get_staged_files() -> List[str]:
        """Get list of staged files"""
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return []
        return [f for f in result.stdout.strip().split("\n") if f]

    @staticmethod
    def file_has_changes(file_path: str, ignore_whitespace: bool = True) -> bool:
        """Check if file has staged changes"""
        cmd = ["git", "diff", "--cached"]
        if ignore_whitespace:
            cmd.append("-w")  # Ignore whitespace
        cmd.extend(["--", file_path])

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return bool(result.stdout.strip())

    @staticmethod
    def get_version_from_head(
        file_path: str, format_type: str, field: Optional[str] = None
    ) -> Optional[str]:
        """Get version from HEAD commit (previous version)"""
        result = subprocess.run(
            ["git", "show", f"HEAD:{file_path}"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            return None  # File doesn't exist in HEAD (new file)

        content = result.stdout

        if format_type == "yaml":
            try:
                data = yaml.safe_load(content)
                return data.get(field or "version")
            except Exception:
                return None
        elif format_type == "markdown_comment":
            match = re.search(
                r"<!--\s*version:\s*([0-9]+\.[0-9]+\.[0-9]+)\s*-->", content
            )
            return match.group(1) if match else None

        return None


# =============================================================================
# Main Validator
# =============================================================================


class DocumentationVersionValidator:
    """Main validation logic"""

    def __init__(self, dependency_map_path: str = ".dependency-map.yaml"):
        self.dependency_map_path = Path(dependency_map_path)
        self.dependency_map = self._load_dependency_map()
        self.errors: List[ValidationError] = []
        self.version_cache: Dict[str, str] = {}

    def _load_dependency_map(self) -> Dict:
        """Load and validate dependency map"""
        if not self.dependency_map_path.exists():
            print(
                f"ERROR: Dependency map not found: {self.dependency_map_path}",
                file=sys.stderr,
            )
            sys.exit(2)

        try:
            with open(self.dependency_map_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"ERROR: Failed to load dependency map: {e}", file=sys.stderr)
            sys.exit(2)

    def _get_current_version(self, tracked_file: TrackedFile) -> Optional[str]:
        """Get current version from working tree"""
        if tracked_file.path in self.version_cache:
            return self.version_cache[tracked_file.path]

        file_path = Path(tracked_file.path)
        if not file_path.exists():
            return None

        ver = VersionParser.parse_version(
            file_path, tracked_file.version_format, tracked_file.version_field
        )

        if ver:
            self.version_cache[tracked_file.path] = ver

        return ver

    def validate(self) -> bool:
        """
        Main validation logic
        Returns True if all validations pass, False otherwise
        """
        staged_files = GitHelper.get_staged_files()
        if not staged_files:
            return True  # No files staged, nothing to validate

        tracked_files = self._parse_tracked_files()
        validation_rules = self.dependency_map.get("validation_rules", {})

        # Step 1: Check if tracked files changed but version not bumped
        for tracked in tracked_files:
            if tracked.path not in staged_files:
                continue

            if not GitHelper.file_has_changes(
                tracked.path, validation_rules.get("ignore_whitespace_changes", True)
            ):
                continue  # No substantive changes

            # File has changes - check if version was bumped
            current_version = self._get_current_version(tracked)
            head_version = GitHelper.get_version_from_head(
                tracked.path, tracked.version_format, tracked.version_field
            )

            # Validate version format
            if current_version and not VersionParser.validate_version_format(
                current_version
            ):
                self.errors.append(
                    ValidationError(
                        error_type="INVALID_VERSION",
                        file=tracked.path,
                        current_version=current_version,
                        reason=f"Invalid semantic version format: '{current_version}'. Expected MAJOR.MINOR.PATCH (e.g., '1.0.0')",
                    )
                )
                continue

            # Check if version bumped
            if head_version and current_version == head_version:
                if validation_rules.get("require_version_bump_on_change", True):
                    self.errors.append(
                        ValidationError(
                            error_type="VERSION_NOT_BUMPED",
                            file=tracked.path,
                            current_version=current_version,
                            reason="File content changed but version field not updated",
                            required_actions=[
                                "1. Determine change type: breaking change (MAJOR), new feature (MINOR), or bug fix (PATCH)",
                                f"2. Update version field in {tracked.path} from '{current_version}' to next appropriate version",
                                f"3. Stage the version change: git add {tracked.path}",
                                "4. Retry commit",
                            ],
                        )
                    )

        # Step 2: Check dependent file versions
        for tracked in tracked_files:
            if tracked.path not in staged_files:
                continue

            current_version = self._get_current_version(tracked)
            if not current_version:
                continue

            # Check each dependent
            for dependent_config in tracked.triggers_update:
                dependent_file = dependent_config["file"]
                dependent_tracked = next(
                    (t for t in tracked_files if t.path == dependent_file), None
                )

                if not dependent_tracked:
                    continue

                dependent_version = self._get_current_version(dependent_tracked)

                if not dependent_version:
                    # Dependent has no version - should it?
                    continue

                # Compare versions
                comparison = VersionParser.compare_versions(
                    dependent_version, current_version
                )

                if comparison < 0:  # dependent_version < source_version
                    # Build section update instructions
                    sections = []
                    for section in dependent_config.get("sections", []):
                        sections.append(
                            SectionUpdate(
                                section_id=section.get("id", "unknown"),
                                location=section.get("location", "unknown"),
                                description=section.get("description", ""),
                                source=section.get("source", ""),
                                update_instructions=f"Update from {section.get('source', tracked.path)}",
                            )
                        )

                    self.errors.append(
                        ValidationError(
                            error_type="DEPENDENT_OUTDATED",
                            file=dependent_file,
                            current_version=dependent_version,
                            expected_version=current_version,
                            reason=f"Dependency {tracked.path} updated to {current_version}",
                            sections_to_update=sections,
                            required_actions=[
                                f"1. Update {dependent_file} sections based on {tracked.path}",
                                f"2. Update {dependent_file} version to '{current_version}'",
                                f"3. Stage changes: git add {dependent_file}",
                                "4. Retry commit",
                            ],
                        )
                    )

        return len(self.errors) == 0

    def _parse_tracked_files(self) -> List[TrackedFile]:
        """Parse tracked files from dependency map"""
        tracked = []
        for file_config in self.dependency_map.get("tracked_files", []):
            tracked.append(
                TrackedFile(
                    path=file_config["path"],
                    version_format=file_config["version_format"],
                    version_field=file_config.get("version_field"),
                    triggers_update=file_config.get("triggers_update", []),
                    description=file_config.get("description", ""),
                )
            )
        return tracked

    def generate_error_report(self) -> Dict:
        """Generate LLM-interpretable error report"""
        # Separate errors by type
        version_not_bumped = [
            e for e in self.errors if e.error_type == "VERSION_NOT_BUMPED"
        ]
        dependent_outdated = [
            e for e in self.errors if e.error_type == "DEPENDENT_OUTDATED"
        ]
        invalid_version = [e for e in self.errors if e.error_type == "INVALID_VERSION"]

        # Build resolution steps
        resolution_steps = []
        step_num = 1

        for error in invalid_version:
            resolution_steps.append(
                f"{step_num}. Fix invalid version format in {error.file}"
            )
            step_num += 1

        for error in version_not_bumped:
            resolution_steps.append(f"{step_num}. Update version in {error.file}")
            step_num += 1

        for error in dependent_outdated:
            resolution_steps.append(
                f"{step_num}. Update {error.file} sections and version to {error.expected_version}"
            )
            step_num += 1

        resolution_steps.append(f"{step_num}. Stage all changes: git add <files>")
        resolution_steps.append(f"{step_num + 1}. Retry commit")

        # Build LLM guidance
        files_to_read = list(
            set(e.file for e in version_not_bumped if e.current_version)
        )
        files_to_edit = list(
            set(e.file for e in version_not_bumped + dependent_outdated)
        )

        return {
            "error_type": "VERSION_VALIDATION_FAILED",
            "blocking": True,
            "validation_timestamp": subprocess.run(
                ["date", "-Iseconds"], capture_output=True, text=True
            ).stdout.strip(),
            "summary": {
                "total_errors": len(self.errors),
                "invalid_versions": len(invalid_version),
                "version_not_bumped": len(version_not_bumped),
                "dependents_outdated": len(dependent_outdated),
            },
            "errors": {
                "invalid_version_format": [
                    {
                        "file": e.file,
                        "current_version": e.current_version,
                        "reason": e.reason,
                    }
                    for e in invalid_version
                ],
                "version_not_bumped": [
                    {
                        "file": e.file,
                        "current_version": e.current_version,
                        "reason": e.reason,
                        "required_actions": e.required_actions,
                    }
                    for e in version_not_bumped
                ],
                "dependents_outdated": [
                    {
                        "file": e.file,
                        "current_version": e.current_version,
                        "required_version_minimum": e.expected_version,
                        "reason": e.reason,
                        "sections_to_update": [
                            {
                                "section_id": s.section_id,
                                "location": s.location,
                                "description": s.description,
                                "source": s.source,
                                "update_instructions": s.update_instructions,
                            }
                            for s in e.sections_to_update
                        ],
                        "required_actions": e.required_actions,
                    }
                    for e in dependent_outdated
                ],
            },
            "resolution_steps": resolution_steps,
            "llm_guidance": {
                "task": "Update documentation files to match source configuration versions",
                "files_to_read": files_to_read,
                "files_to_edit": files_to_edit,
                "validation": "Ensure all version fields are updated and dependencies synchronized",
            },
        }


# =============================================================================
# Main Entry Point
# =============================================================================


def main():
    """Main execution"""
    print("Running documentation version validation...", file=sys.stderr)

    validator = DocumentationVersionValidator()

    if validator.validate():
        print("✓ Documentation version validation passed", file=sys.stderr)
        sys.exit(0)
    else:
        print("\n" + "=" * 80, file=sys.stderr)
        print(
            "✗ COMMIT BLOCKED: Documentation version validation failed", file=sys.stderr
        )
        print("=" * 80 + "\n", file=sys.stderr)

        error_report = validator.generate_error_report()
        print(json.dumps(error_report, indent=2), file=sys.stderr)

        print("\n" + "=" * 80, file=sys.stderr)
        print("Fix the issues above and retry your commit.", file=sys.stderr)
        print("=" * 80 + "\n", file=sys.stderr)

        sys.exit(1)


if __name__ == "__main__":
    main()
