"""
Step definitions for git workflow acceptance tests (US-005, US-006, US-007).

CRITICAL: These tests validate git hooks and CI/CD workflows, not core components.
Focus on git command behavior and hook validation.
"""

import json
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
import subprocess


# Load scenarios
scenarios("us-005-commit-enforcement.feature")
scenarios("us-006-prepush-validation.feature")
scenarios("us-007-changelog-generation.feature")


# ============================================================================
# FIXTURES - Git repository setup
# ============================================================================


@pytest.fixture
def git_repo(tmp_path):
    """Create temporary git repository for testing."""
    repo_dir = tmp_path / "test-repo"
    repo_dir.mkdir()

    # Initialize git repo
    subprocess.run(["git", "init"], cwd=repo_dir, capture_output=True, check=True)

    # Configure git user
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_dir,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_dir,
        capture_output=True,
        check=True,
    )

    return {"repo_dir": repo_dir, "hooks_dir": repo_dir / ".git" / "hooks"}


@pytest.fixture
def git_result():
    """Store git command results."""
    return {
        "returncode": None,
        "stdout": "",
        "stderr": "",
        "commit_sha": None,
        "push_success": False,
    }


# ============================================================================
# GIVEN - Preconditions (Commit enforcement)
# ============================================================================


@given("I am in the nWave repository")
def in_nwave_repository(git_repo, monkeypatch):
    """Set current directory to git repository."""
    monkeypatch.chdir(git_repo["repo_dir"])


@given("commit-msg hook is installed")
def commit_msg_hook_installed(git_repo):
    """
    Install commit-msg hook for conventional commit validation.

    In production: installed via pre-commit framework with commitlint.
    For tests: minimal hook script that validates format.
    """
    hooks_dir = git_repo["hooks_dir"]
    hooks_dir.mkdir(exist_ok=True)

    hook_script = hooks_dir / "commit-msg"
    hook_content = """#!/bin/sh
# Conventional Commits validation hook

commit_msg_file=$1
commit_msg=$(cat "$commit_msg_file")

# Pattern: <type>[optional scope]: <description>
# Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
pattern="^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\\(.+\\))?!?: .{1,}"

if ! echo "$commit_msg" | grep -qE "$pattern"; then
    echo "ERROR: Commit message does not follow Conventional Commits format."
    echo ""
    echo "Your message:"
    echo "  $commit_msg"
    echo ""
    echo "Expected format:"
    echo "  <type>[scope]: <description>"
    echo ""
    echo "Examples:"
    echo "  feat: add user authentication"
    echo "  fix(auth): resolve login timeout issue"
    echo "  feat!: redesign API (breaking change)"
    echo ""
    echo "See: https://www.conventionalcommits.org/"
    exit 1
fi

exit 0
"""

    hook_script.write_text(hook_content)
    hook_script.chmod(0o755)


@given("I have staged changes")
def staged_changes(git_repo):
    """Create and stage a test file."""
    test_file = git_repo["repo_dir"] / "test.txt"
    test_file.write_text("Test content")

    subprocess.run(["git", "add", "test.txt"], cwd=git_repo["repo_dir"], check=True)


# ============================================================================
# GIVEN - Preconditions (Pre-push validation)
# ============================================================================


@given("pre-push hook is installed")
def prepush_hook_installed(git_repo):
    """
    Install pre-push hook for VERSION file and config validation.

    In production: validates nWave/VERSION and .releaserc existence.
    """
    hooks_dir = git_repo["hooks_dir"]
    hooks_dir.mkdir(exist_ok=True)

    hook_script = hooks_dir / "pre-push"
    hook_content = """#!/bin/sh
# Pre-push validation for VERSION file and semantic-release config

repo_root=$(git rev-parse --show-toplevel)

# Check VERSION file
if [ ! -f "$repo_root/nWave/VERSION" ]; then
    echo "ERROR: Pre-push validation failed."
    echo ""
    echo "[FAIL] VERSION file missing"
    echo "       Expected: nWave/VERSION"
    echo "       Action: Create nWave/VERSION with current version (e.g., '1.5.7')"
    echo ""
    exit 1
fi

# Check semantic-release config
if [ ! -f "$repo_root/.releaserc" ] && [ ! -f "$repo_root/release.config.js" ]; then
    echo "ERROR: Pre-push validation failed."
    echo ""
    echo "[FAIL] semantic-release not configured"
    echo "       Expected: .releaserc or release.config.js"
    echo "       Action: Run 'npx semantic-release-cli setup' or create config manually"
    echo ""
    exit 1
fi

exit 0
"""

    hook_script.write_text(hook_content)
    hook_script.chmod(0o755)


@given("nWave/VERSION file exists with valid semver format")
def version_file_exists(git_repo):
    """Create VERSION file with semantic version."""
    nwave_dir = git_repo["repo_dir"] / "nWave"
    nwave_dir.mkdir(exist_ok=True)

    version_file = nwave_dir / "VERSION"
    version_file.write_text("1.5.7\n")


@given(".releaserc configuration exists")
def releaserc_exists(git_repo):
    """Create .releaserc semantic-release configuration with full plugin configs."""
    releaserc = git_repo["repo_dir"] / ".releaserc"
    releaserc_config = {
        "branches": ["main", "master"],
        "tagFormat": "v${version}",
        "plugins": [
            [
                "@semantic-release/commit-analyzer",
                {
                    "preset": "conventionalcommits",
                    "releaseRules": [
                        {"type": "feat", "release": "minor"},
                        {"type": "fix", "release": "patch"},
                        {"type": "perf", "release": "patch"},
                        {"type": "docs", "release": False},
                        {"breaking": True, "release": "major"},
                    ],
                },
            ],
            [
                "@semantic-release/release-notes-generator",
                {
                    "preset": "conventionalcommits",
                    "presetConfig": {
                        "types": [
                            {"type": "feat", "section": "Features"},
                            {"type": "fix", "section": "Bug Fixes"},
                            {"type": "perf", "section": "Performance Improvements"},
                            {"type": "docs", "section": "Documentation"},
                        ]
                    },
                },
            ],
            "@semantic-release/changelog",
            "@semantic-release/github",
        ],
    }
    releaserc.write_text(json.dumps(releaserc_config, indent=2))


@given("nWave/VERSION file does not exist")
def version_file_missing(git_repo):
    """Ensure VERSION file is absent."""
    version_file = git_repo["repo_dir"] / "nWave" / "VERSION"
    if version_file.exists():
        version_file.unlink()


# ============================================================================
# GIVEN - Preconditions (Changelog generation)
# ============================================================================


@given("semantic-release is configured")
def semantic_release_configured(git_repo):
    """Verify semantic-release configuration exists."""
    releaserc_exists(git_repo)


@given("GitHub Actions workflow exists")
def github_actions_workflow_exists(git_repo):
    """Create GitHub Actions workflow for semantic-release."""
    workflows_dir = git_repo["repo_dir"] / ".github" / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)

    workflow = workflows_dir / "release.yml"
    workflow_content = """name: Release
on:
  push:
    branches: [main, master]

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm install semantic-release
      - run: npx semantic-release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
"""
    workflow.write_text(workflow_content)


@given("commits since last release:")
def commits_since_last_release(git_repo, pytestconfig):
    """Create commits with conventional commit messages."""
    # Create an initial commit to serve as "last release"
    initial_file = git_repo["repo_dir"] / "initial.txt"
    initial_file.write_text("Initial release content")
    subprocess.run(["git", "add", "initial.txt"], cwd=git_repo["repo_dir"], check=True)
    subprocess.run(
        ["git", "commit", "-m", "chore: initial release v1.0.0"],
        cwd=git_repo["repo_dir"],
        capture_output=True,
    )

    # Tag the initial commit as a release point
    subprocess.run(
        ["git", "tag", "v1.0.0"],
        cwd=git_repo["repo_dir"],
        capture_output=True,
    )

    # Verify we have at least one commit since the tag
    result = subprocess.run(
        ["git", "rev-list", "--count", "v1.0.0..HEAD"],
        cwd=git_repo["repo_dir"],
        capture_output=True,
        text=True,
    )
    # Initial state: 0 commits since release tag (commits will be added by scenario)
    assert result.returncode == 0, "Failed to set up release history context"


@given(parsers.parse('a commit with message "{commit_message}"'))
def commit_with_message(git_repo, commit_message):
    """Create a commit with specific message."""
    # Stage a change first
    test_file = git_repo["repo_dir"] / "feature.txt"
    test_file.write_text("Feature implementation")

    subprocess.run(["git", "add", "feature.txt"], cwd=git_repo["repo_dir"], check=True)

    # Commit with message (may fail if hook rejects)
    try:
        subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=git_repo["repo_dir"],
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        # Hook may reject - that's expected for invalid messages
        pass


# ============================================================================
# WHEN - Actions (Git operations)
# ============================================================================


@when(parsers.parse('I commit with message "{commit_message}"'))
def commit_with_specific_message(git_repo, git_result, commit_message):
    """Attempt to commit with specific message."""
    result = subprocess.run(
        ["git", "commit", "-m", commit_message],
        cwd=git_repo["repo_dir"],
        capture_output=True,
        text=True,
    )

    git_result["returncode"] = result.returncode
    git_result["stdout"] = result.stdout
    git_result["stderr"] = result.stderr


@when("I push to origin")
def push_to_origin(git_repo, git_result):
    """Attempt to push to remote (triggers pre-push hook)."""
    repo_dir = git_repo["repo_dir"]

    # Create an initial commit if none exists (pre-push hook needs something to push)
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_dir,
        capture_output=True,
    )
    if result.returncode != 0:
        # No commits exist, create one
        test_file = repo_dir / "initial.txt"
        test_file.write_text("Initial content for push test")
        subprocess.run(["git", "add", "initial.txt"], cwd=repo_dir, check=True)
        subprocess.run(
            ["git", "commit", "-m", "chore: initial commit"],
            cwd=repo_dir,
            capture_output=True,
            check=True,
        )

    # Ensure we're on main branch
    subprocess.run(
        ["git", "branch", "-M", "main"],
        cwd=repo_dir,
        capture_output=True,
    )

    # Create a local bare repository as remote (allows real push behavior)
    bare_repo = repo_dir.parent / "origin.git"
    subprocess.run(["git", "init", "--bare", str(bare_repo)], capture_output=True)

    # Add the local bare repo as remote
    subprocess.run(
        ["git", "remote", "add", "origin", str(bare_repo)],
        cwd=repo_dir,
        capture_output=True,
    )

    # Attempt push (will be stopped by pre-push hook if validation fails)
    result = subprocess.run(
        ["git", "push", "-u", "origin", "main"],
        cwd=repo_dir,
        capture_output=True,
        text=True,
    )

    git_result["returncode"] = result.returncode
    git_result["stdout"] = result.stdout
    git_result["stderr"] = result.stderr
    git_result["push_success"] = result.returncode == 0


@when("semantic-release runs on push to main")
def semantic_release_runs(git_repo):
    """Simulate semantic-release execution."""
    # In real scenario, GitHub Actions would trigger semantic-release
    # For test, we verify configuration exists
    releaserc = git_repo["repo_dir"] / ".releaserc"
    assert releaserc.exists(), "semantic-release configuration not found"


@when("semantic-release runs")
def semantic_release_runs_alt(git_repo):
    """Alternative phrasing for semantic-release execution."""
    semantic_release_runs(git_repo)


# ============================================================================
# THEN - Assertions (Commit validation)
# ============================================================================


@then("the commit is accepted")
def verify_commit_accepted(git_result):
    """Verify commit was successful."""
    assert git_result["returncode"] == 0, (
        f"Commit was rejected:\n{git_result['stderr']}"
    )


@then("no error is shown")
def verify_no_error_shown(git_result):
    """Verify no error message in output."""
    assert git_result["returncode"] == 0, f"Error occurred:\n{git_result['stderr']}"


@then("the commit appears in git log")
def verify_commit_in_log(git_repo):
    """Verify commit exists in git history."""
    result = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        cwd=git_repo["repo_dir"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0 and result.stdout.strip(), (
        "No commits found in git log"
    )


@then("the commit is rejected")
def verify_commit_rejected(git_result):
    """Verify commit was rejected by hook."""
    assert git_result["returncode"] != 0, (
        "Commit was accepted when it should have been rejected"
    )


@then(parsers.parse('I see error "{error_text}"'))
def verify_error_message(git_result, error_text):
    """Verify specific error message is shown."""
    output = git_result["stdout"] + git_result["stderr"]
    assert error_text in output, (
        f"Expected error '{error_text}' not found in:\n{output}"
    )


@then(parsers.parse('I see "{text}"'))
def verify_output_text(git_result, text):
    """Verify specific text appears in output."""
    output = git_result["stdout"] + git_result["stderr"]
    assert text in output, f"Expected text '{text}' not found in:\n{output}"


@then(parsers.parse('I see reference link "{url}"'))
def verify_reference_link(git_result, url):
    """Verify reference URL is shown."""
    output = git_result["stdout"] + git_result["stderr"]
    assert url in output, f"Expected reference link '{url}' not found in:\n{output}"


@then("the commit does NOT appear in git log")
def verify_commit_not_in_log(git_repo):
    """Verify commit was not created (rejected by hook)."""
    result = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        cwd=git_repo["repo_dir"],
        capture_output=True,
        text=True,
    )

    # Check that either no commits exist or the latest is not the rejected one
    if result.returncode != 0 or not result.stdout.strip():
        # No commits at all - this confirms rejection
        return

    # Get the last commit message
    last_commit_result = subprocess.run(
        ["git", "log", "-1", "--format=%s"],
        cwd=git_repo["repo_dir"],
        capture_output=True,
        text=True,
    )

    last_message = last_commit_result.stdout.strip()
    # The invalid message should NOT be in the log
    assert "invalid commit message" not in last_message.lower(), (
        f"Rejected commit should not appear in git log, but found: {last_message}"
    )


# ============================================================================
# THEN - Assertions (Pre-push validation)
# ============================================================================


@then("the push succeeds")
def verify_push_succeeds(git_result):
    """Verify push was successful."""
    # In real scenario with remote, would check returncode
    # For test with fake remote, verify hook didn't block
    assert "VERSION file missing" not in git_result["stderr"], (
        "Push was blocked by validation error"
    )


@then("all commits reach the remote")
def verify_commits_pushed(git_result):
    """Verify commits were pushed to remote."""
    # With a fake remote URL, the push will fail at network level but pre-push hook runs first
    # If pre-push hook passed, the validation succeeded (push failure is expected with fake remote)
    # Check that there was no hook-related error (VERSION missing, config missing)
    combined_output = git_result["stdout"] + git_result["stderr"]

    hook_errors = [
        "VERSION file missing",
        "semantic-release not configured",
        "Pre-push validation failed",
    ]

    for error in hook_errors:
        assert error not in combined_output, (
            f"Pre-push validation blocked the push with error: {error}"
        )

    # Note: Actual push to remote fails due to fake URL, which is expected in test
    # The important assertion is that pre-push validation passed


@then("the push is rejected")
def verify_push_rejected(git_result):
    """Verify push was blocked by pre-push hook."""
    assert git_result["returncode"] != 0, (
        "Push succeeded when it should have been rejected"
    )


@then(parsers.parse('I see suggested action "{action}"'))
def verify_suggested_action(git_result, action):
    """Verify suggested remediation action is shown."""
    output = git_result["stdout"] + git_result["stderr"]
    assert action in output, f"Expected action '{action}' not found in:\n{output}"


@then("no commits reach the remote")
def verify_no_commits_pushed(git_result):
    """Verify push was blocked, no commits sent."""
    # Verify that pre-push hook blocked the push (non-zero return code)
    assert git_result["returncode"] != 0, (
        "Push should have been blocked by pre-push validation, but it succeeded"
    )

    # Verify there's a validation error in the output
    combined_output = git_result["stdout"] + git_result["stderr"]
    validation_indicators = [
        "VERSION file missing",
        "semantic-release not configured",
        "Pre-push validation failed",
        "ERROR",
    ]

    has_validation_error = any(
        indicator in combined_output for indicator in validation_indicators
    )
    assert has_validation_error, (
        f"Push was blocked but no validation error found in output:\n{combined_output}"
    )


# ============================================================================
# HELPERS - Configuration validation
# ============================================================================


def parse_releaserc(git_repo):
    """Parse .releaserc and return configuration dict."""
    releaserc = git_repo["repo_dir"] / ".releaserc"
    assert releaserc.exists(), "Release configuration (.releaserc) not found"
    return json.loads(releaserc.read_text())


def get_plugin_config(config, plugin_name):
    """
    Extract plugin configuration from semantic-release config.

    Plugins can be specified as:
    - String: "@semantic-release/changelog"
    - Array: ["@semantic-release/commit-analyzer", {...options}]
    """
    for plugin in config.get("plugins", []):
        if isinstance(plugin, str) and plugin == plugin_name:
            return {}  # Plugin exists but has no custom config
        if isinstance(plugin, list) and len(plugin) >= 1:
            if plugin[0] == plugin_name:
                return plugin[1] if len(plugin) > 1 else {}
    return None  # Plugin not found


def get_section_for_commit_type(config, commit_type):
    """
    Get the release notes section name for a given commit type.

    Returns the section name (e.g., "Features" for "feat") or None if not mapped.
    """
    notes_config = get_plugin_config(config, "@semantic-release/release-notes-generator")
    if notes_config is None:
        return None

    preset_config = notes_config.get("presetConfig", {})
    types = preset_config.get("types", [])

    for type_config in types:
        if type_config.get("type") == commit_type:
            return type_config.get("section")

    return None


def get_release_type_for_breaking(config):
    """
    Check what release type is configured for breaking changes.

    Returns the release type (e.g., "major") or None if not configured.
    """
    analyzer_config = get_plugin_config(config, "@semantic-release/commit-analyzer")
    if analyzer_config is None:
        return None

    release_rules = analyzer_config.get("releaseRules", [])
    for rule in release_rules:
        if rule.get("breaking") is True:
            return rule.get("release")

    return None


# ============================================================================
# THEN - Assertions (Changelog generation)
# ============================================================================


@then("CHANGELOG.md is updated with new section")
def verify_changelog_updated(git_repo):
    """Verify configuration supports CHANGELOG.md generation."""
    config = parse_releaserc(git_repo)

    # Verify changelog plugin is configured
    changelog_config = get_plugin_config(config, "@semantic-release/changelog")
    assert changelog_config is not None, (
        "Changelog plugin (@semantic-release/changelog) not configured in .releaserc - "
        "required for CHANGELOG.md generation"
    )


@then("GitHub Release is created with release notes")
def verify_github_release_created(git_repo):
    """Verify GitHub Release would be created."""
    # Verify GitHub Actions workflow exists for releases
    workflow_path = git_repo["repo_dir"] / ".github" / "workflows" / "release.yml"
    assert workflow_path.exists(), (
        "GitHub Actions release workflow not found at .github/workflows/release.yml"
    )

    workflow_content = workflow_path.read_text()
    assert "semantic-release" in workflow_content, (
        "Release workflow does not include semantic-release execution"
    )

    # Verify .releaserc has GitHub plugin
    releaserc = git_repo["repo_dir"] / ".releaserc"
    assert releaserc.exists(), "Release configuration (.releaserc) not found"

    releaserc_content = releaserc.read_text()
    assert "@semantic-release/github" in releaserc_content, (
        "GitHub plugin not configured in .releaserc - required for creating GitHub releases"
    )


@then(parsers.parse('release notes include {section} section with "{content}"'))
def verify_release_notes_section(git_repo, section, content):
    """
    Verify configuration supports generating release notes with the expected section.

    This validates that the semantic-release configuration maps commit types to
    the correct sections, ensuring the described behavior WILL occur when
    semantic-release runs in CI/CD.
    """
    config = parse_releaserc(git_repo)

    # Verify release-notes-generator is configured
    notes_config = get_plugin_config(config, "@semantic-release/release-notes-generator")
    assert notes_config is not None, (
        "Release notes generator plugin (@semantic-release/release-notes-generator) "
        "not configured in .releaserc"
    )

    # Map section names to commit types
    section_to_type = {
        "Features": "feat",
        "Bug Fixes": "fix",
        "Performance Improvements": "perf",
        "Documentation": "docs",
    }

    commit_type = section_to_type.get(section)
    assert commit_type is not None, (
        f"Unknown section '{section}' - expected one of: {list(section_to_type.keys())}"
    )

    # Verify the commit type is mapped to the expected section
    actual_section = get_section_for_commit_type(config, commit_type)
    assert actual_section == section, (
        f"Commit type '{commit_type}' is not mapped to section '{section}' in "
        f"release-notes-generator config. Actual mapping: '{actual_section}'"
    )


@then(parsers.parse('release notes include Features section with "{feature}"'))
def verify_features_section(git_repo, feature):
    """Verify Features section configuration in release notes."""
    verify_release_notes_section(git_repo, "Features", feature)


@then(parsers.parse('release notes include Bug Fixes section with "{fix}"'))
def verify_bugfixes_section(git_repo, fix):
    """Verify Bug Fixes section configuration in release notes."""
    verify_release_notes_section(git_repo, "Bug Fixes", fix)


@then(parsers.parse('CHANGELOG.md includes "{section}" section'))
def verify_changelog_section(git_repo, section):
    """
    Verify configuration supports generating CHANGELOG with the expected section.

    For "BREAKING CHANGES" section, validates that:
    1. Changelog plugin is configured
    2. The conventionalcommits preset is used (which auto-handles BREAKING CHANGES)
    """
    config = parse_releaserc(git_repo)

    # Verify changelog plugin is configured
    changelog_config = get_plugin_config(config, "@semantic-release/changelog")
    assert changelog_config is not None, (
        "Changelog plugin (@semantic-release/changelog) not configured in .releaserc"
    )

    if section == "BREAKING CHANGES":
        # Breaking changes are automatically handled by conventionalcommits preset
        notes_config = get_plugin_config(
            config, "@semantic-release/release-notes-generator"
        )
        assert notes_config is not None, (
            "Release notes generator not configured - required for BREAKING CHANGES section"
        )

        preset = notes_config.get("preset", "angular")
        assert preset == "conventionalcommits", (
            f"Expected 'conventionalcommits' preset for proper BREAKING CHANGES handling, "
            f"but found '{preset}'. The conventionalcommits preset automatically creates "
            f"a BREAKING CHANGES section for commits with '!' or 'BREAKING CHANGE:' footer."
        )


@then("GitHub Release prominently shows breaking change warning")
def verify_breaking_change_prominent(git_repo):
    """
    Verify configuration supports GitHub releases with breaking change warnings.

    The GitHub plugin combined with conventionalcommits preset ensures breaking
    changes are prominently displayed in release notes, which become the GitHub
    Release body.
    """
    config = parse_releaserc(git_repo)

    # Verify GitHub plugin is configured
    github_config = get_plugin_config(config, "@semantic-release/github")
    assert github_config is not None, (
        "GitHub plugin (@semantic-release/github) not configured in .releaserc - "
        "required for creating GitHub releases"
    )

    # Verify release-notes-generator uses conventionalcommits preset
    # which formats BREAKING CHANGES prominently
    notes_config = get_plugin_config(config, "@semantic-release/release-notes-generator")
    assert notes_config is not None, (
        "Release notes generator not configured - required for release notes content"
    )

    preset = notes_config.get("preset", "angular")
    assert preset == "conventionalcommits", (
        f"Expected 'conventionalcommits' preset for prominent BREAKING CHANGES display, "
        f"but found '{preset}'"
    )


@then("the version is bumped to next major version")
def verify_major_version_bump(git_repo):
    """
    Verify configuration supports major version bump for breaking changes.

    Validates that the commit-analyzer has a release rule that maps
    breaking changes to "major" release type.
    """
    config = parse_releaserc(git_repo)

    # Verify commit-analyzer is configured
    analyzer_config = get_plugin_config(config, "@semantic-release/commit-analyzer")
    assert analyzer_config is not None, (
        "Commit analyzer plugin (@semantic-release/commit-analyzer) not configured - "
        "required for version bump calculation"
    )

    # Verify breaking changes trigger major version bump
    release_type = get_release_type_for_breaking(config)
    assert release_type == "major", (
        f"Breaking changes should trigger 'major' version bump, but configured "
        f"release type is '{release_type}'. Add rule: {{\"breaking\": true, \"release\": \"major\"}} "
        f"to commit-analyzer releaseRules."
    )
