"""
Unit Tests: ScopeValidator - Post-Execution Scope Validation

Tests ScopeValidator class that runs git diff to detect out-of-scope file modifications.
Business context: Prevent agents from "helpfully" modifying files outside step scope.

Domain Language:
- allowed_patterns: Glob patterns defining in-scope files
- out_of_scope_files: Files modified that don't match allowed patterns
- scope violation: Modification of file outside allowed patterns
- validation_skipped: Git command unavailable, validation not performed
"""

import json
import subprocess
from unittest.mock import Mock, patch

from src.des.adapters.driven.validation.scope_validator import ScopeValidator


class TestScopeValidatorGitIntegration:
    """Test git diff execution and error handling."""

    def test_git_timeout_configured_to_5_seconds(self):
        """
        GIVEN ScopeValidator initialized
        WHEN checking git timeout configuration
        THEN timeout is exactly 5 seconds (not mutated to other values)
        """
        validator = ScopeValidator()
        assert validator.git_timeout == 5

    def test_executes_git_diff_command_successfully(self, tmp_path):
        """
        GIVEN ScopeValidator initialized
        WHEN validate_scope called
        THEN git diff --name-only HEAD executed successfully
        """
        # Arrange
        step_file = tmp_path / "step.json"
        step_file.write_text(
            json.dumps(
                {
                    "scope": {
                        "allowed_patterns": ["**/UserRepository*"],
                        "target_files": ["src/repositories/UserRepository.py"],
                    }
                }
            )
        )
        validator = ScopeValidator()

        # Mock git command to return modified files
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                stdout="src/repositories/UserRepository.py\n", returncode=0
            )

            # Act
            result = validator.validate_scope(
                step_file_path=str(step_file), project_root=tmp_path
            )

            # Assert: Git command called with correct parameters
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert call_args[0][0] == ["git", "diff", "--name-only", "HEAD"]
            assert call_args[1]["capture_output"] is True
            assert call_args[1]["timeout"] == 5
            assert call_args[1]["check"] is True
            assert call_args[1]["text"] is True
            # Verify result is valid (git succeeded)
            assert result.validation_skipped is False

    def test_git_timeout_returns_validation_skipped(self, tmp_path):
        """
        GIVEN ScopeValidator initialized
        WHEN git diff times out after 5 seconds
        THEN ValidationResult has validation_skipped=True with timeout reason
        """
        # Arrange
        step_file = tmp_path / "step.json"
        step_file.write_text(
            json.dumps(
                {
                    "scope": {
                        "allowed_patterns": ["**/UserRepository*"],
                        "target_files": ["src/repositories/UserRepository.py"],
                    }
                }
            )
        )
        validator = ScopeValidator()

        # Mock git timeout
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(
                cmd=["git", "diff"], timeout=5
            )

            # Act
            result = validator.validate_scope(
                step_file_path=str(step_file), project_root=tmp_path
            )

            # Assert: Validation skipped with timeout reason
            assert result.has_violations is False
            assert result.validation_skipped is True
            assert "timeout" in result.reason.lower()

    def test_git_unavailable_returns_validation_skipped(self, tmp_path):
        """
        GIVEN ScopeValidator initialized
        WHEN git diff fails (CalledProcessError)
        THEN ValidationResult has validation_skipped=True with unavailable reason
        """
        # Arrange
        step_file = tmp_path / "step.json"
        step_file.write_text(
            json.dumps(
                {
                    "scope": {
                        "allowed_patterns": ["**/UserRepository*"],
                        "target_files": ["src/repositories/UserRepository.py"],
                    }
                }
            )
        )
        validator = ScopeValidator()

        # Mock git command failure
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                returncode=128, cmd=["git", "diff"]
            )

            # Act
            result = validator.validate_scope(
                step_file_path=str(step_file), project_root=tmp_path
            )

            # Assert: Validation skipped with unavailable reason
            assert result.has_violations is False
            assert result.validation_skipped is True
            assert (
                "unavailable" in result.reason.lower()
                or "failed" in result.reason.lower()
            )

    def test_empty_lines_in_git_output_all_files_still_processed(self, tmp_path):
        """
        GIVEN git output with empty lines interspersed
        WHEN validate_scope processes modified files
        THEN all files are processed (continue skips empty, doesn't break loop)
        """
        step_file = tmp_path / "step.json"
        step_file.write_text(json.dumps({"scope": {"allowed_patterns": ["**/User*"]}}))
        validator = ScopeValidator()

        with patch("subprocess.run") as mock_run:
            # Git output: in-scope file, empty lines, out-of-scope file
            mock_run.return_value = Mock(
                stdout="src/UserRepo.py\n\n\nsrc/OrderService.py\n\n", returncode=0
            )

            result = validator.validate_scope(str(step_file), tmp_path)

            # Must detect OrderService (second file after empty lines)
            # This proves continue (not break) was used
            assert result.has_violations is True
            assert "src/OrderService.py" in result.out_of_scope_files


class TestScopeValidatorPatternMatching:
    """Test file pattern matching against allowed patterns."""

    def test_in_scope_files_pass_validation(self, tmp_path):
        """
        GIVEN step allows **/UserRepository* files
        WHEN git diff shows only UserRepository.py modified
        THEN validation passes (has_violations=False)
        """
        # Arrange
        step_file = tmp_path / "step.json"
        step_file.write_text(
            json.dumps(
                {
                    "scope": {
                        "allowed_patterns": ["**/UserRepository*"],
                        "target_files": ["src/repositories/UserRepository.py"],
                    }
                }
            )
        )
        validator = ScopeValidator()

        # Mock git showing in-scope file
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                stdout="src/repositories/UserRepository.py\n", returncode=0
            )

            # Act
            result = validator.validate_scope(
                step_file_path=str(step_file), project_root=tmp_path
            )

            # Assert: No violations for in-scope file
            assert result.has_violations is False
            assert len(result.out_of_scope_files) == 0

    def test_out_of_scope_files_detected(self, tmp_path):
        """
        GIVEN step allows only **/UserRepository* files
        WHEN git diff shows OrderService.py modified (out of scope)
        THEN validation detects violation with OrderService in out_of_scope_files
        """
        # Arrange
        step_file = tmp_path / "step.json"
        step_file.write_text(
            json.dumps(
                {
                    "scope": {
                        "allowed_patterns": ["**/UserRepository*"],
                        "target_files": ["src/repositories/UserRepository.py"],
                    }
                }
            )
        )
        validator = ScopeValidator()

        # Mock git showing out-of-scope file
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                stdout="src/repositories/UserRepository.py\nsrc/services/OrderService.py\n",
                returncode=0,
            )

            # Act
            result = validator.validate_scope(
                step_file_path=str(step_file), project_root=tmp_path
            )

            # Assert: Violation detected for OrderService
            assert result.has_violations is True
            assert "src/services/OrderService.py" in result.out_of_scope_files
            assert "OrderService" in result.violation_message
            assert result.violation_severity == "WARNING"

    def test_multiple_out_of_scope_files_all_detected(self, tmp_path):
        """
        GIVEN step allows only **/UserRepository* files
        WHEN git diff shows multiple out-of-scope files
        THEN all violations detected in out_of_scope_files list
        """
        # Arrange
        step_file = tmp_path / "step.json"
        step_file.write_text(
            json.dumps(
                {
                    "scope": {
                        "allowed_patterns": ["**/UserRepository*"],
                        "target_files": ["src/repositories/UserRepository.py"],
                    }
                }
            )
        )
        validator = ScopeValidator()

        # Mock git showing multiple out-of-scope files
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                stdout="src/services/OrderService.py\nsrc/controllers/PaymentController.py\n",
                returncode=0,
            )

            # Act
            result = validator.validate_scope(
                step_file_path=str(step_file), project_root=tmp_path
            )

            # Assert: All violations detected
            assert result.has_violations is True
            assert len(result.out_of_scope_files) == 2
            assert "src/services/OrderService.py" in result.out_of_scope_files
            assert "src/controllers/PaymentController.py" in result.out_of_scope_files

    def test_multiple_patterns_any_match_passes(self, tmp_path):
        """
        GIVEN step allows multiple patterns: **/UserRepository*, **/test_user_repository*
        WHEN git diff shows files matching different patterns
        THEN all files pass validation (each matches at least one pattern)
        """
        # Arrange
        step_file = tmp_path / "step.json"
        step_file.write_text(
            json.dumps(
                {
                    "scope": {
                        "allowed_patterns": [
                            "**/UserRepository*",
                            "**/test_user_repository*",
                        ],
                        "target_files": [
                            "src/repositories/UserRepository.py",
                            "tests/unit/test_user_repository.py",
                        ],
                    }
                }
            )
        )
        validator = ScopeValidator()

        # Mock git showing files matching different patterns
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                stdout="src/repositories/UserRepository.py\ntests/unit/test_user_repository.py\n",
                returncode=0,
            )

            # Act
            result = validator.validate_scope(
                step_file_path=str(step_file), project_root=tmp_path
            )

            # Assert: All files pass (each matches at least one pattern)
            assert result.has_violations is False
            assert len(result.out_of_scope_files) == 0

    def test_glob_pattern_matches_nested_directories(self, tmp_path):
        """
        GIVEN step allows **/ UserRepository* pattern
        WHEN git diff shows UserRepository in deeply nested path
        THEN validation passes (** matches any directory depth)
        """
        # Arrange
        step_file = tmp_path / "step.json"
        step_file.write_text(
            json.dumps(
                {
                    "scope": {
                        "allowed_patterns": ["**/UserRepository*"],
                        "target_files": ["src/repositories/UserRepository.py"],
                    }
                }
            )
        )
        validator = ScopeValidator()

        # Mock git showing file in deeply nested path
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                stdout="src/deep/nested/path/to/repositories/UserRepository.py\n",
                returncode=0,
            )

            # Act
            result = validator.validate_scope(
                step_file_path=str(step_file), project_root=tmp_path
            )

            # Assert: Nested path matches pattern
            assert result.has_violations is False
            assert len(result.out_of_scope_files) == 0

    def test_wildcard_suffix_matches_extensions(self, tmp_path):
        """
        GIVEN step allows **/UserRepository* pattern (ends with *)
        WHEN git diff shows UserRepository files with different extensions
        THEN all extensions pass validation (* matches any suffix)
        """
        # Arrange
        step_file = tmp_path / "step.json"
        step_file.write_text(
            json.dumps(
                {
                    "scope": {
                        "allowed_patterns": ["**/UserRepository*"],
                        "target_files": ["src/repositories/UserRepository.py"],
                    }
                }
            )
        )
        validator = ScopeValidator()

        # Mock git showing files with different extensions
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                stdout="src/repositories/UserRepository.py\nsrc/repositories/UserRepositoryTest.cs\n",
                returncode=0,
            )

            # Act
            result = validator.validate_scope(
                step_file_path=str(step_file), project_root=tmp_path
            )

            # Assert: Both files match pattern (suffix wildcard)
            assert result.has_violations is False
            assert len(result.out_of_scope_files) == 0

    def test_partial_name_match_fails_without_wildcard(self, tmp_path):
        """
        GIVEN step allows UserRepository.py (exact, no wildcards)
        WHEN git diff shows src/repositories/UserRepository.py (different path)
        THEN validation detects violation (exact match required without wildcards)
        """
        # Arrange
        step_file = tmp_path / "step.json"
        step_file.write_text(
            json.dumps(
                {
                    "scope": {
                        "allowed_patterns": ["UserRepository.py"],  # No wildcards
                        "target_files": ["src/repositories/UserRepository.py"],
                    }
                }
            )
        )
        validator = ScopeValidator()

        # Mock git showing file with path prefix
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                stdout="src/repositories/UserRepository.py\n", returncode=0
            )

            # Act
            result = validator.validate_scope(
                step_file_path=str(step_file), project_root=tmp_path
            )

            # Assert: Violation detected (path doesn't match exactly)
            assert result.has_violations is True
            assert "src/repositories/UserRepository.py" in result.out_of_scope_files

    def test_file_matches_pattern_returns_true_not_inverted(self):
        """
        GIVEN file matches allowed pattern
        WHEN _file_matches_any_pattern called
        THEN returns True (not inverted to False with 'not')
        """
        validator = ScopeValidator()

        # Test positive case explicitly
        matches = validator._file_matches_any_pattern(
            "src/repositories/UserRepository.py", ["**/UserRepository*"]
        )
        assert matches is True  # Explicit True check (not just truthy)

        # Test negative case explicitly
        no_match = validator._file_matches_any_pattern(
            "src/services/OrderService.py", ["**/UserRepository*"]
        )
        assert no_match is False  # Explicit False check (not just falsy)


class TestViolationMessageFormatting:
    """Test violation message formatting with specific file counts."""

    def test_single_violation_uses_singular_message_format(self, tmp_path):
        """
        GIVEN exactly 1 out-of-scope file
        WHEN building violation message
        THEN message uses singular format (not plural)
        """
        step_file = tmp_path / "step.json"
        step_file.write_text(json.dumps({"scope": {"allowed_patterns": ["**/User*"]}}))
        validator = ScopeValidator()

        with patch("subprocess.run") as mock_run:
            # Exactly 1 out-of-scope file
            mock_run.return_value = Mock(stdout="src/OrderService.py\n", returncode=0)

            result = validator.validate_scope(str(step_file), tmp_path)

            # Verify singular format used (not plural)
            assert result.has_violations is True
            assert result.violation_message.startswith("Scope violation:")
            assert "src/OrderService.py" in result.violation_message
            assert "modified outside allowed patterns" in result.violation_message

    def test_multiple_violations_use_plural_message_format(self, tmp_path):
        """
        GIVEN exactly 2 out-of-scope files
        WHEN building violation message
        THEN message uses plural format with count and file list
        """
        step_file = tmp_path / "step.json"
        step_file.write_text(json.dumps({"scope": {"allowed_patterns": ["**/User*"]}}))
        validator = ScopeValidator()

        with patch("subprocess.run") as mock_run:
            # Exactly 2 out-of-scope files
            mock_run.return_value = Mock(
                stdout="src/OrderService.py\nsrc/PaymentService.py\n", returncode=0
            )

            result = validator.validate_scope(str(step_file), tmp_path)

            # Verify plural format used (not singular)
            assert result.has_violations is True
            assert result.violation_message.startswith("Scope violations:")
            assert "2 files" in result.violation_message
            assert "src/OrderService.py" in result.violation_message
            assert "src/PaymentService.py" in result.violation_message


class TestStepFileImplicitAllowlist:
    """Test step file modification is implicitly allowed regardless of patterns."""

    def test_step_file_modification_always_allowed(self, tmp_path):
        """
        GIVEN step file with restricted allowed_patterns (**/UserRepository*)
        WHEN git diff shows step file itself was modified
        THEN validation passes (step file implicitly allowed)
        """
        # Arrange
        step_file = tmp_path / "steps" / "01-01.json"
        step_file.parent.mkdir(parents=True, exist_ok=True)
        step_file.write_text(
            json.dumps(
                {
                    "scope": {
                        "allowed_patterns": [
                            "**/UserRepository*"
                        ],  # Step file not in patterns
                        "target_files": ["src/repositories/UserRepository.py"],
                    }
                }
            )
        )
        validator = ScopeValidator()

        # Mock git showing step file modified
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(stdout=f"{step_file!s}\n", returncode=0)

            # Act
            result = validator.validate_scope(
                step_file_path=str(step_file), project_root=tmp_path
            )

            # Assert: Step file modification is allowed
            assert result.has_violations is False
            assert str(step_file) not in result.out_of_scope_files

    def test_step_file_plus_out_of_scope_file_detects_violation(self, tmp_path):
        """
        GIVEN step file with restricted patterns
        WHEN git diff shows step file AND out-of-scope file
        THEN step file passes, out-of-scope file detected
        """
        # Arrange
        step_file = tmp_path / "steps" / "01-01.json"
        step_file.parent.mkdir(parents=True, exist_ok=True)
        step_file.write_text(
            json.dumps(
                {
                    "scope": {
                        "allowed_patterns": ["**/UserRepository*"],
                        "target_files": ["src/repositories/UserRepository.py"],
                    }
                }
            )
        )
        validator = ScopeValidator()

        # Mock git showing step file + out-of-scope file
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                stdout=f"{step_file!s}\nsrc/services/OrderService.py\n",
                returncode=0,
            )

            # Act
            result = validator.validate_scope(
                step_file_path=str(step_file), project_root=tmp_path
            )

            # Assert: OrderService violation, step file allowed
            assert result.has_violations is True
            assert "src/services/OrderService.py" in result.out_of_scope_files
            assert str(step_file) not in result.out_of_scope_files

    def test_step_file_implicitly_allowed_even_with_no_patterns(self, tmp_path):
        """
        GIVEN step file with empty allowed_patterns
        WHEN git diff shows step file modified
        THEN validation passes (step file always implicitly allowed)
        """
        # Arrange
        step_file = tmp_path / "steps" / "01-01.json"
        step_file.parent.mkdir(parents=True, exist_ok=True)
        step_file.write_text(
            json.dumps(
                {
                    "scope": {
                        "allowed_patterns": [],  # Empty patterns
                        "target_files": [],
                    }
                }
            )
        )
        validator = ScopeValidator()

        # Mock git showing step file modified
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(stdout=f"{step_file!s}\n", returncode=0)

            # Act
            result = validator.validate_scope(
                step_file_path=str(step_file), project_root=tmp_path
            )

            # Assert: Step file allowed even with empty patterns
            assert result.has_violations is False
            assert str(step_file) not in result.out_of_scope_files
