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


from src.des.validation.scope_validator import ScopeValidator


class TestScopeValidatorGitIntegration:
    """Test git diff execution and error handling."""

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
