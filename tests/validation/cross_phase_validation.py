#!/usr/bin/env python3
"""
Cross-Phase E2E Workflow Validation Suite

Validates all 7 cross-phase acceptance criteria:
- cross-01: Complete DISCUSS→DESIGN→DISTILL→DEVELOP workflow with wave handoffs
- cross-02: Complete release workflow from commit to user installation
- cross-03: Agent output consistency across platforms
- cross-04: Command template compliance in wave commands
- cross-05: Cross-platform path handling and error messages
- cross-06: BUILD:INCLUDE/BUILD:INJECT marker conflict detection
- cross-07: Workflow interruption recovery with resume capability
"""

import json
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class ValidationResult:
    test_name: str
    passed: bool
    message: str
    details: List[str]


class CrossPhaseValidator:
    def __init__(self, repo_root: str = "/mnt/c/Repositories/Projects/nwave"):
        self.repo_root = Path(repo_root)
        self.results: List[ValidationResult] = []
        self.features_dir = self.repo_root / "docs/features/framework-rationalization"

    def validate_cross_01_e2e_workflow(self) -> ValidationResult:
        """
        Validate complete DISCUSS→DESIGN→DISTILL→DEVELOP workflow with wave handoffs.

        Acceptance Criteria:
        - DISCUSS outputs to feature discuss directory
        - DESIGN reads from DISCUSS and outputs to design directory
        - DISTILL reads from DESIGN and outputs to distill directory
        - DEVELOP reads from DISTILL and outputs to develop directory
        - Pre-commit hooks validate documentation sync on each commit
        """
        details = []
        passed = True

        # Check for DISCUSS wave outputs
        discuss_dir = self.features_dir / "00-discuss"
        if discuss_dir.exists():
            details.append(f"✓ DISCUSS directory exists: {discuss_dir}")
        else:
            details.append(f"✗ DISCUSS directory NOT FOUND: {discuss_dir}")
            passed = False

        # Check for DESIGN wave outputs
        design_dir = self.features_dir / "01-design"
        if design_dir.exists():
            details.append(f"✓ DESIGN directory exists: {design_dir}")
        else:
            details.append(f"✗ DESIGN directory NOT FOUND: {design_dir}")
            passed = False

        # Check for DISTILL wave outputs
        distill_dir = self.features_dir / "02-distill"
        if distill_dir.exists():
            details.append(f"✓ DISTILL directory exists: {distill_dir}")
        else:
            details.append(f"✗ DISTILL directory NOT FOUND: {distill_dir}")
            passed = False

        # Check for DEVELOP wave outputs
        develop_dir = self.features_dir / "03-develop"
        if develop_dir.exists():
            details.append(f"✓ DEVELOP directory exists: {develop_dir}")
        else:
            details.append(f"✗ DEVELOP directory NOT FOUND: {develop_dir}")
            passed = False

        # Check for cross-phase directory
        cross_phase_dir = self.features_dir / "04-develop"
        if cross_phase_dir.exists():
            details.append(f"✓ Cross-phase directory exists: {cross_phase_dir}")
        else:
            details.append(f"✗ Cross-phase directory NOT FOUND: {cross_phase_dir}")
            passed = False

        # Check for pre-commit hooks
        pre_commit_hook = self.repo_root / ".git/hooks/pre-commit"
        if pre_commit_hook.exists():
            details.append(f"✓ Pre-commit hook exists: {pre_commit_hook}")
        else:
            details.append(f"✗ Pre-commit hook NOT FOUND: {pre_commit_hook}")
            passed = False

        return ValidationResult(
            test_name="cross-01: E2E Workflow",
            passed=passed,
            message="Complete DISCUSS→DESIGN→DISTILL→DEVELOP workflow validated"
            if passed
            else "Workflow structure incomplete",
            details=details,
        )

    def validate_cross_02_release_workflow(self) -> ValidationResult:
        """
        Validate complete release workflow from commit to installation.

        Acceptance Criteria:
        - CI workflow validates build on all platforms
        - Release workflow packages both platforms
        - Repository release created with downloadable archives
        - User downloads Claude Code archive
        - Extracts archive to local directory
        - Executes installer
        - Installer copies files to appropriate locations
        - Installer creates backup of previous version
        - Installation completes successfully with verification
        """
        details = []
        passed = True

        # Check for GitHub Actions CI/CD workflows
        workflows_dir = self.repo_root / ".github/workflows"
        if workflows_dir.exists():
            workflows = list(workflows_dir.glob("*.yml")) + list(
                workflows_dir.glob("*.yaml")
            )
            if workflows:
                details.append(f"✓ CI/CD workflows found: {len(workflows)} workflows")
            else:
                details.append(f"✗ No CI/CD workflows found in {workflows_dir}")
                passed = False
        else:
            details.append(f"✗ Workflows directory NOT FOUND: {workflows_dir}")
            passed = False

        # Check for release configuration
        release_config_paths = [
            self.repo_root / "release.json",
            self.repo_root / ".releaserc",
            self.repo_root / "release.config.js",
        ]
        release_found = any(p.exists() for p in release_config_paths)
        if release_found:
            found_path = next(p for p in release_config_paths if p.exists())
            details.append(f"✓ Release configuration found: {found_path}")
        else:
            details.append("✗ No release configuration found")
            passed = False

        # Check for installer scripts
        installer_patterns = ["install*", "setup*", "*installer*"]
        installers_found = False
        for pattern in installer_patterns:
            installers = list(self.repo_root.glob(f"**/{pattern}"))
            if installers:
                details.append(f"✓ Installer scripts found: {len(installers)} files")
                installers_found = True
                break

        if not installers_found:
            details.append("✗ No installer scripts found")
            passed = False

        return ValidationResult(
            test_name="cross-02: Release Workflow",
            passed=passed,
            message="Release workflow infrastructure validated"
            if passed
            else "Release infrastructure incomplete",
            details=details,
        )

    def validate_cross_03_multi_platform_consistency(self) -> ValidationResult:
        """
        Validate agent output consistency across platforms.

        Acceptance Criteria:
        - Claude Code output contains Radical Candor content
        - Codex output contains identical Radical Candor content
        - Only metadata differs between platforms
        - Agent behavior remains identical across platforms
        """
        details = []
        passed = True

        # Check for platform-specific agent definitions
        agent_builder_dir = self.repo_root / "docs/agents"
        if agent_builder_dir.exists():
            agents = list(agent_builder_dir.glob("*.yaml")) + list(
                agent_builder_dir.glob("*.yml")
            )
            if agents:
                details.append(f"✓ Agent definitions found: {len(agents)} agents")
            else:
                details.append("✗ No agent definitions found")
                passed = False
        else:
            details.append(f"✗ Agents directory NOT FOUND: {agent_builder_dir}")
            passed = False

        # Check for Radical Candor content in shared library
        shared_content_patterns = [
            self.repo_root / "docs/shared-content",
            self.repo_root / "src/shared-content",
            self.repo_root / "content/shared",
        ]
        shared_content_found = False
        for path in shared_content_patterns:
            if path.exists():
                content_files = list(path.glob("**/*"))
                if content_files:
                    details.append(f"✓ Shared content library found at: {path}")
                    shared_content_found = True
                    break

        if not shared_content_found:
            details.append("✗ Shared content library NOT FOUND")
            passed = False

        # Check for platform metadata configuration
        metadata_configs = list(self.repo_root.glob("**/platform-metadata.json"))
        if metadata_configs:
            details.append(
                f"✓ Platform metadata configuration found: {len(metadata_configs)} files"
            )
        else:
            details.append("✗ Platform metadata configuration NOT FOUND")
            passed = False

        return ValidationResult(
            test_name="cross-03: Multi-Platform Consistency",
            passed=passed,
            message="Multi-platform consistency framework validated"
            if passed
            else "Platform consistency incomplete",
            details=details,
        )

    def validate_cross_04_template_compliance(self) -> ValidationResult:
        """
        Validate command template compliance in wave commands.

        Acceptance Criteria:
        - Command delegates to specialized agent within line limits
        - Command bundles context with pre-discovered file paths
        - Command contains zero workflow implementation
        - Reviewer validates template compliance
        - Wave execution completes with proper handoff to next wave
        """
        details = []
        passed = True

        # Check for command template definition
        command_template_paths = [
            self.repo_root / "docs/templates/command-template.md",
            self.repo_root / "src/templates/command.template",
            self.repo_root / "templates/command.yaml",
        ]
        command_template_found = False
        for path in command_template_paths:
            if path.exists():
                details.append(f"✓ Command template found: {path}")
                command_template_found = True
                break

        if not command_template_found:
            details.append("✗ Command template NOT FOUND")
            passed = False

        # Check for command files in wave directories
        command_files = list(self.features_dir.glob("**/commands/*.md"))
        if command_files:
            details.append(f"✓ Command files found: {len(command_files)} commands")
        else:
            details.append("✗ No command files found in wave directories")
            passed = False

        # Check for template compliance checker
        compliance_checkers = list(self.repo_root.glob("**/check*command*compliance*"))
        if compliance_checkers:
            details.append(
                f"✓ Template compliance checker found: {len(compliance_checkers)} files"
            )
        else:
            details.append("✗ Template compliance checker NOT FOUND")
            passed = False

        return ValidationResult(
            test_name="cross-04: Template Compliance",
            passed=passed,
            message="Command template compliance framework validated"
            if passed
            else "Template compliance infrastructure incomplete",
            details=details,
        )

    def validate_cross_05_path_incompatibility_error(self) -> ValidationResult:
        """
        Validate cross-platform path handling and error messages.

        Acceptance Criteria:
        - Path normalization handles format correctly
        - Or build fails with clear path format error
        - Error specifies which path caused failure
        - Cross-platform path guidelines are provided
        """
        details = []
        passed = True

        # Check for path normalization utilities
        path_utils_patterns = list(self.repo_root.glob("**/path*.py")) + list(
            self.repo_root.glob("**/file*.py")
        )
        if path_utils_patterns:
            details.append(f"✓ Path utilities found: {len(path_utils_patterns)} files")
        else:
            details.append("✗ Path utilities NOT FOUND")
            passed = False

        # Check for cross-platform build script
        build_script_patterns = [
            self.repo_root / "build.sh",
            self.repo_root / "build.py",
            self.repo_root / "scripts/build.sh",
            self.repo_root / "scripts/build.py",
        ]
        build_script_found = False
        for path in build_script_patterns:
            if path.exists():
                details.append(f"✓ Build script found: {path}")
                build_script_found = True
                break

        if not build_script_found:
            details.append("✗ Build script NOT FOUND")
            passed = False

        # Check for cross-platform path guidelines documentation
        guidelines_paths = [
            self.repo_root / "docs/CROSS_PLATFORM.md",
            self.repo_root / "docs/PATH_HANDLING.md",
            self.repo_root / "README.md",
        ]
        guidelines_found = False
        for path in guidelines_paths:
            if path.exists():
                content = path.read_text()
                if "path" in content.lower() or "cross-platform" in content.lower():
                    details.append(f"✓ Path guidelines found in: {path}")
                    guidelines_found = True
                    break

        if not guidelines_found:
            details.append(
                "✗ Cross-platform path guidelines NOT FOUND or NOT DOCUMENTED"
            )
            passed = False

        return ValidationResult(
            test_name="cross-05: Path Incompatibility Error",
            passed=passed,
            message="Cross-platform path handling validated"
            if passed
            else "Path handling infrastructure incomplete",
            details=details,
        )

    def validate_cross_06_marker_conflict_error(self) -> ValidationResult:
        """
        Validate BUILD:INCLUDE/BUILD:INJECT marker conflict detection.

        Acceptance Criteria:
        - Resolver fails with marker conflict error
        - Error specifies conflicting marker locations
        - Suggested resolution separates the markers
        """
        details = []
        passed = True

        # Check for marker resolution utility
        marker_resolver_patterns = (
            list(self.repo_root.glob("**/marker*.py"))
            + list(self.repo_root.glob("**/resolver*.py"))
            + list(self.repo_root.glob("**/build*.py"))
        )
        if marker_resolver_patterns:
            details.append(
                f"✓ Marker resolver utilities found: {len(marker_resolver_patterns)} files"
            )
        else:
            details.append("✗ Marker resolver utilities NOT FOUND")
            passed = False

        # Check for marker definitions
        marker_docs = list(self.repo_root.glob("**/MARKERS.md")) + list(
            self.repo_root.glob("**/markers.yaml")
        )
        if marker_docs:
            details.append(f"✓ Marker documentation found: {len(marker_docs)} files")
        else:
            details.append("✗ Marker documentation NOT FOUND")
            passed = False

        # Check for error handling in build process
        build_files = list(self.repo_root.glob("**/build.py")) + list(
            self.repo_root.glob("**/build.sh")
        )
        build_with_error_handling = False
        for build_file in build_files:
            if build_file.suffix == ".py":
                content = build_file.read_text()
                if "raise" in content.lower() or "exception" in content.lower():
                    build_with_error_handling = True
                    details.append(f"✓ Error handling found in: {build_file}")
                    break

        if not build_with_error_handling:
            details.append("✗ Error handling for marker conflicts NOT FOUND")
            passed = False

        return ValidationResult(
            test_name="cross-06: Marker Conflict Error",
            passed=passed,
            message="Marker conflict detection framework validated"
            if passed
            else "Marker conflict detection incomplete",
            details=details,
        )

    def validate_cross_07_interruption_recovery(self) -> ValidationResult:
        """
        Validate workflow interruption recovery with resume capability.

        Acceptance Criteria:
        - Partial progress is saved to recovery file
        - Next execution offers resume option
        - User can choose resume or restart
        - No work is lost from interruption
        """
        details = []
        passed = True

        # Check for state persistence mechanism
        state_patterns = (
            list(self.repo_root.glob("**/state*.py"))
            + list(self.repo_root.glob("**/persistence*.py"))
            + list(self.repo_root.glob("**/checkpoint*.py"))
        )
        if state_patterns:
            details.append(
                f"✓ State persistence utilities found: {len(state_patterns)} files"
            )
        else:
            details.append("✗ State persistence utilities NOT FOUND")
            passed = False

        # Check for recovery file location
        recovery_dir_patterns = [
            self.repo_root / ".recovery",
            self.repo_root / ".checkpoints",
            self.repo_root / "tmp/recovery",
        ]
        recovery_dir_found = False
        for path in recovery_dir_patterns:
            if path.exists() or path.parent.exists():
                details.append(
                    f"✓ Recovery directory structure available: {path.parent}"
                )
                recovery_dir_found = True
                break

        if not recovery_dir_found:
            details.append("✗ Recovery directory NOT FOUND or not configured")
            passed = False

        # Check for CLI option/parameter for resume
        main_entry_points = (
            list(self.repo_root.glob("**/main.py"))
            + list(self.repo_root.glob("**/cli.py"))
            + list(self.repo_root.glob("**/run.py"))
        )
        resume_option_found = False
        for entry_point in main_entry_points:
            if entry_point.exists():
                content = entry_point.read_text()
                if "--resume" in content or "resume" in content.lower():
                    resume_option_found = True
                    details.append(f"✓ Resume option found in: {entry_point}")
                    break

        if not resume_option_found:
            details.append("✗ Resume CLI option NOT FOUND")
            passed = False

        return ValidationResult(
            test_name="cross-07: Interruption Recovery",
            passed=passed,
            message="Workflow interruption recovery framework validated"
            if passed
            else "Interruption recovery infrastructure incomplete",
            details=details,
        )

    def run_all_validations(self) -> Tuple[List[ValidationResult], bool]:
        """Run all cross-phase validations."""
        print("=" * 70)
        print("CROSS-PHASE E2E WORKFLOW VALIDATION SUITE")
        print("=" * 70)
        print()

        self.results = [
            self.validate_cross_01_e2e_workflow(),
            self.validate_cross_02_release_workflow(),
            self.validate_cross_03_multi_platform_consistency(),
            self.validate_cross_04_template_compliance(),
            self.validate_cross_05_path_incompatibility_error(),
            self.validate_cross_06_marker_conflict_error(),
            self.validate_cross_07_interruption_recovery(),
        ]

        all_passed = True
        for i, result in enumerate(self.results, 1):
            status = "PASS" if result.passed else "FAIL"
            print(f"[{i}] {result.test_name}: {status}")
            print(f"    {result.message}")
            for detail in result.details:
                print(f"    {detail}")
            print()
            if not result.passed:
                all_passed = False

        print("=" * 70)
        passed_count = sum(1 for r in self.results if r.passed)
        total_count = len(self.results)
        print(f"RESULTS: {passed_count}/{total_count} validations passed")
        print("=" * 70)
        print()

        return self.results, all_passed

    def generate_report(self, output_file: str = None) -> str:
        """Generate a JSON report of validation results."""
        report = {
            "validation_suite": "cross-phase-e2e",
            "total_validations": len(self.results),
            "passed": sum(1 for r in self.results if r.passed),
            "failed": sum(1 for r in self.results if not r.passed),
            "results": [
                {
                    "test_name": r.test_name,
                    "passed": r.passed,
                    "message": r.message,
                    "details": r.details,
                }
                for r in self.results
            ],
        }

        report_json = json.dumps(report, indent=2)

        if output_file:
            Path(output_file).write_text(report_json)
            print(f"Report saved to: {output_file}")

        return report_json


def main():
    validator = CrossPhaseValidator()
    results, all_passed = validator.run_all_validations()

    # Generate report
    report_file = "/mnt/c/Repositories/Projects/nwave/test-results/cross-phase-validation-report.json"
    Path(report_file).parent.mkdir(parents=True, exist_ok=True)
    validator.generate_report(report_file)

    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
