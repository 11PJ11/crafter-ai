"""
Unit tests for GitPort interface contract.

HEXAGONAL ARCHITECTURE:
- GitPort is a PORT (abstract interface at hexagon boundary)
- Defines contract for git operations (branch info, uncommitted changes, repo root)
- Adapters implement this port for actual git command execution

These tests verify the PORT CONTRACT:
- Abstract class cannot be instantiated
- All required methods are defined (get_current_branch, has_uncommitted_changes, get_repo_root)
- GitError exception type is defined
"""

from abc import ABC

import pytest


class TestGitPortIsAbstract:
    """Tests that GitPort is properly defined as an abstract class."""

    def test_git_port_is_abstract(self):
        """
        GIVEN: The GitPort class
        WHEN: Checking if it's abstract
        THEN: It should be an ABC that cannot be instantiated
        """
        # ARRANGE
        from nWave.core.versioning.ports.git_port import GitPort

        # ACT & ASSERT
        assert issubclass(GitPort, ABC)
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            GitPort()


class TestGetCurrentBranchMethodDefined:
    """Tests that get_current_branch method is properly defined."""

    def test_get_current_branch_method_exists(self):
        """
        GIVEN: The GitPort class
        WHEN: Checking for get_current_branch method
        THEN: It should exist
        """
        # ARRANGE
        from nWave.core.versioning.ports.git_port import GitPort

        # ACT & ASSERT
        assert hasattr(GitPort, "get_current_branch")

    def test_get_current_branch_is_abstract_method(self):
        """
        GIVEN: The GitPort class
        WHEN: Checking get_current_branch method
        THEN: It should be an abstract method
        """
        # ARRANGE
        from nWave.core.versioning.ports.git_port import GitPort

        # ACT
        method = getattr(GitPort, "get_current_branch", None)

        # ASSERT
        assert method is not None, "get_current_branch method must be defined"
        assert hasattr(method, "__isabstractmethod__")
        assert method.__isabstractmethod__ is True

    def test_get_current_branch_returns_str(self):
        """
        GIVEN: The GitPort class
        WHEN: Checking get_current_branch return type annotation
        THEN: It should return str
        """
        # ARRANGE
        from nWave.core.versioning.ports.git_port import GitPort
        from typing import get_type_hints

        # ACT
        hints = get_type_hints(GitPort.get_current_branch)

        # ASSERT
        assert hints.get("return") is str, "get_current_branch must return str"


class TestHasUncommittedChangesMethodDefined:
    """Tests that has_uncommitted_changes method is properly defined."""

    def test_has_uncommitted_changes_method_exists(self):
        """
        GIVEN: The GitPort class
        WHEN: Checking for has_uncommitted_changes method
        THEN: It should exist
        """
        # ARRANGE
        from nWave.core.versioning.ports.git_port import GitPort

        # ACT & ASSERT
        assert hasattr(GitPort, "has_uncommitted_changes")

    def test_has_uncommitted_changes_is_abstract_method(self):
        """
        GIVEN: The GitPort class
        WHEN: Checking has_uncommitted_changes method
        THEN: It should be an abstract method
        """
        # ARRANGE
        from nWave.core.versioning.ports.git_port import GitPort

        # ACT
        method = getattr(GitPort, "has_uncommitted_changes", None)

        # ASSERT
        assert method is not None, "has_uncommitted_changes method must be defined"
        assert hasattr(method, "__isabstractmethod__")
        assert method.__isabstractmethod__ is True

    def test_has_uncommitted_changes_returns_bool(self):
        """
        GIVEN: The GitPort class
        WHEN: Checking has_uncommitted_changes return type annotation
        THEN: It should return bool
        """
        # ARRANGE
        from nWave.core.versioning.ports.git_port import GitPort
        from typing import get_type_hints

        # ACT
        hints = get_type_hints(GitPort.has_uncommitted_changes)

        # ASSERT
        assert hints.get("return") is bool, "has_uncommitted_changes must return bool"


class TestGetRepoRootMethodDefined:
    """Tests that get_repo_root method is properly defined."""

    def test_get_repo_root_method_exists(self):
        """
        GIVEN: The GitPort class
        WHEN: Checking for get_repo_root method
        THEN: It should exist
        """
        # ARRANGE
        from nWave.core.versioning.ports.git_port import GitPort

        # ACT & ASSERT
        assert hasattr(GitPort, "get_repo_root")

    def test_get_repo_root_is_abstract_method(self):
        """
        GIVEN: The GitPort class
        WHEN: Checking get_repo_root method
        THEN: It should be an abstract method
        """
        # ARRANGE
        from nWave.core.versioning.ports.git_port import GitPort

        # ACT
        method = getattr(GitPort, "get_repo_root", None)

        # ASSERT
        assert method is not None, "get_repo_root method must be defined"
        assert hasattr(method, "__isabstractmethod__")
        assert method.__isabstractmethod__ is True

    def test_get_repo_root_returns_path(self):
        """
        GIVEN: The GitPort class
        WHEN: Checking get_repo_root return type annotation
        THEN: It should return Path
        """
        # ARRANGE
        from nWave.core.versioning.ports.git_port import GitPort
        from pathlib import Path
        from typing import get_type_hints

        # ACT
        hints = get_type_hints(GitPort.get_repo_root)

        # ASSERT
        assert hints.get("return") == Path, "get_repo_root must return Path"


class TestGitErrorExceptionDefined:
    """Tests that GitError exception is properly defined."""

    def test_git_error_class_exists(self):
        """
        GIVEN: The git_port module
        WHEN: Checking for GitError class
        THEN: It should exist
        """
        # ARRANGE & ACT
        from nWave.core.versioning.ports.git_port import GitError

        # ASSERT
        assert GitError is not None

    def test_git_error_is_exception(self):
        """
        GIVEN: The GitError class
        WHEN: Checking its inheritance
        THEN: It should be a subclass of Exception
        """
        # ARRANGE
        from nWave.core.versioning.ports.git_port import GitError

        # ACT & ASSERT
        assert issubclass(GitError, Exception), "GitError must inherit from Exception"

    def test_git_error_can_be_raised_with_message(self):
        """
        GIVEN: A GitError exception
        WHEN: Raising it with a message
        THEN: It should be catchable and contain the message
        """
        # ARRANGE
        from nWave.core.versioning.ports.git_port import GitError

        # ACT & ASSERT
        with pytest.raises(GitError) as exc_info:
            raise GitError("Not a git repository")

        assert "Not a git repository" in str(exc_info.value)


class TestGitPortErrorHandling:
    """Tests for error handling contracts documented in docstrings."""

    def test_get_current_branch_documents_git_error(self):
        """
        GIVEN: The GitPort interface contract
        WHEN: Checking get_current_branch docstring
        THEN: It should document GitError in Raises section
        """
        # ARRANGE
        from nWave.core.versioning.ports.git_port import GitPort

        # ACT
        docstring = GitPort.get_current_branch.__doc__ or ""

        # ASSERT
        assert "GitError" in docstring, \
            "get_current_branch must document GitError in docstring"

    def test_has_uncommitted_changes_documents_git_error(self):
        """
        GIVEN: The GitPort interface contract
        WHEN: Checking has_uncommitted_changes docstring
        THEN: It should document GitError in Raises section
        """
        # ARRANGE
        from nWave.core.versioning.ports.git_port import GitPort

        # ACT
        docstring = GitPort.has_uncommitted_changes.__doc__ or ""

        # ASSERT
        assert "GitError" in docstring, \
            "has_uncommitted_changes must document GitError in docstring"

    def test_get_repo_root_documents_git_error(self):
        """
        GIVEN: The GitPort interface contract
        WHEN: Checking get_repo_root docstring
        THEN: It should document GitError in Raises section
        """
        # ARRANGE
        from nWave.core.versioning.ports.git_port import GitPort

        # ACT
        docstring = GitPort.get_repo_root.__doc__ or ""

        # ASSERT
        assert "GitError" in docstring, \
            "get_repo_root must document GitError in docstring"
