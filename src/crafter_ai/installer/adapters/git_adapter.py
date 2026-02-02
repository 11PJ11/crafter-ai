"""SubprocessGitAdapter - subprocess-based implementation of GitPort.

This adapter implements the GitPort protocol using subprocess to execute
git commands. It provides safe error handling for non-git repositories
and missing tags.
"""

import subprocess


class SubprocessGitAdapter:
    """Subprocess-based git adapter implementing GitPort.

    This adapter executes git commands via subprocess.run() and parses
    their output. It handles error cases gracefully.

    Used by:
        - VersionBumpService for conventional commit analysis
        - build_checks for clean git status verification
    """

    def get_current_branch(self) -> str:
        """Return the current git branch name.

        Returns:
            The name of the current branch (e.g., 'main', 'feature/foo').
        """
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout.strip()

    def get_commits_since_tag(self, tag: str) -> list[str]:
        """Return commit messages since the specified tag.

        Args:
            tag: The git tag to start from (e.g., 'v0.1.0').

        Returns:
            List of commit messages from tag to HEAD.
        """
        result = subprocess.run(
            ["git", "log", f"{tag}..HEAD", "--pretty=format:%s"],
            capture_output=True,
            text=True,
            check=False,
        )
        output = result.stdout.strip()
        if not output:
            return []
        return output.split("\n")

    def get_latest_tag(self) -> str | None:
        """Return the most recent tag in the repository.

        Returns:
            The latest tag name, or None if no tags exist.
        """
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return None
        return result.stdout.strip()

    def get_commit_hash(self, short: bool = True) -> str:
        """Return the current commit hash.

        Args:
            short: If True, return short hash (7 chars). If False, full hash.

        Returns:
            The commit hash string.
        """
        cmd = ["git", "rev-parse"]
        if short:
            cmd.append("--short")
        cmd.append("HEAD")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout.strip()

    def has_uncommitted_changes(self) -> bool:
        """Check if there are uncommitted changes in the working tree.

        Returns:
            True if there are uncommitted changes, False if clean.
        """
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=False,
        )
        return bool(result.stdout.strip())

    def is_git_repo(self) -> bool:
        """Check if the current directory is inside a git repository.

        Returns:
            True if inside a git repo, False otherwise.
        """
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0
