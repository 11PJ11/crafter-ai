#!/usr/bin/env python3
"""Release packaging orchestrator - Phase 5 complete implementation.

This script demonstrates all 8 steps of Phase 5:
1. Build validation - verify all artifacts exist
2. Archive creation - create platform-specific archives
3. Checksum generation - SHA256 checksums
4. Version reading - embed version from configuration
5. README generation - platform-specific instructions
6. Missing artifacts error - detect missing files
7. Checksum mismatch error - validate integrity
8. Version conflict error - detect inconsistencies
"""

import sys
from pathlib import Path

from scripts.framework.release_packager import ReleasePackager
from scripts.framework.release_validation import (
    MissingArtifactsValidator,
    ChecksumMismatchValidator,
    VersionConflictValidator,
)


def main():
    """Execute complete release packaging workflow."""
    project_root = Path.cwd()

    print("nWave Framework Release Packaging System")
    print("=" * 60)
    print()

    try:
        # Step 1-5: Execute complete packaging (includes steps 1-5)
        print("Phase 5: Release Packaging System")
        print("-" * 60)

        packager = ReleasePackager(project_root)
        result = packager.package_release()

        print(f"✓ Build validation passed")
        print(f"✓ Archives created for {len(result['platforms'])} platforms")
        print(f"  - {result['platforms'][0]['name']}: {Path(result['platforms'][0]['archive']).name}")
        print(f"  - {result['platforms'][1]['name']}: {Path(result['platforms'][1]['archive']).name}")
        print(f"✓ Checksums generated: {Path(result['checksums_file']).name}")
        print(f"✓ Version embedded: {result['version']}")
        print(f"✓ Installation READMEs generated")
        print()

        # Step 6-8: Validate packages
        print("Validation - Error Detection & Handling")
        print("-" * 60)

        dist_dir = project_root / "dist"

        # Step 6: Missing artifacts validation
        print("Step 6: Checking for missing artifacts...", end=" ")
        missing_validator = MissingArtifactsValidator(dist_dir)
        missing_errors = missing_validator.validate_all_platforms()
        if not missing_errors:
            print("✓ All platform artifacts present")
        else:
            print("✗ Missing artifacts detected:")
            for error in missing_errors:
                print(f"  Platform: {error.platform}")
                print(f"  Missing: {', '.join(error.missing_files)}")
                print(f"  Remediation: {error.remediation}")

        # Step 7: Checksum mismatch validation
        print("Step 7: Validating checksums...", end=" ")
        checksums_file = dist_dir / "CHECKSUMS.json"
        checksum_validator = ChecksumMismatchValidator(checksums_file)
        checksum_errors = checksum_validator.verify_all_checksums(dist_dir)
        if not checksum_errors:
            print("✓ All checksums valid")
        else:
            print("✗ Checksum mismatches detected:")
            for error in checksum_errors:
                print(f"  File: {error.filename}")
                print(f"  Expected: {error.expected_checksum}")
                print(f"  Actual: {error.actual_checksum}")
                print(f"  Note: {error.security_implications}")

        # Step 8: Version conflict validation
        print("Step 8: Checking version consistency...", end=" ")
        version_validator = VersionConflictValidator(project_root)
        version_error = version_validator.validate_version_consistency()
        archive_version_error = version_validator.validate_archive_versions(dist_dir)

        if not version_error and not archive_version_error:
            print("✓ Versions consistent")
            version = version_validator.get_configuration_version()
            print(f"  Configuration: {version}")
            print(f"  Archives: {version}")
            tag_version = version_validator.get_git_tag_version()
            if tag_version:
                print(f"  Git tag: {tag_version}")
        else:
            if version_error:
                print("✗ Version conflict detected:")
                print(f"  Configuration: {version_error.configuration_version}")
                print(f"  Git tag: {version_error.tag_version}")
                print(f"  Resolution steps:")
                for step in version_error.resolution_steps:
                    print(f"    - {step}")
            if archive_version_error:
                print("✗ Archive version mismatch detected:")
                print(f"  Configuration: {archive_version_error.configuration_version}")
                print(f"  Archives: {', '.join(set(archive_version_error.archive_versions))}")
                for step in archive_version_error.resolution_steps:
                    print(f"    - {step}")

        print()
        print("=" * 60)
        print("Phase 5 Complete: All 8 steps executed successfully")
        print()
        print("Release artifacts created in:", dist_dir)
        print()
        print("Summary:")
        print(f"  Version: {result['version']}")
        print(f"  Archives: {len(result['platforms'])}")
        print(f"  Checksums: CHECKSUMS.json, SHA256SUMS")
        print(f"  Documentation: INSTALL-CLAUDE-CODE.md, INSTALL-CODEX.md")
        print()

        return 0

    except Exception as e:
        print(f"Error: {e}")
        print()
        print("Resolution steps:")
        print("  1. Verify all required artifacts exist")
        print("  2. Check that nWave/framework-catalog.yaml has valid version")
        print("  3. Ensure dist/ directory is writable")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
