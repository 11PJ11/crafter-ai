"""
Unit tests for GitAdapter used by Forge.

Tests for Step 05-01: Get current branch

GitAdapter implements GitPort for actual git command execution.

HEXAGONAL ARCHITECTURE:
- GitAdapter is an INFRASTRUCTURE ADAPTER (outside the hexagon)
- Implements GitPort interface
- Tests verify correct branch retrieval
"""

import pytest
from unittest.mock import patch, MagicMock


class TestGitAdapterGetCurrentBranch:
    """Test that GitAdapter correctly retrieves current branch."""

    def test_git_adapter_gets_current_branch(self, tmp_path, monkeypatch):
        """
        GIVEN a git repository on branch "main"
        WHEN get_current_branch() is called
        THEN it returns "main"
        """
        # Arrange
        from nWave.infrastructure.versioning.git_adapter import GitAdapter

        # Create GitAdapter
        adapter = GitAdapter()

        # Mock subprocess to return "main" branch
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "main\n"
            mock_run.return_value = mock_result

            # Act
            branch = adapter.get_current_branch()

            # Assert
            assert branch == "main"
            mock_run.assert_called_once()
