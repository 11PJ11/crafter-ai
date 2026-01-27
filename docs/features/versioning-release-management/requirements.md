# nWave Versioning and Release Management

## Feature Overview

This feature introduces a comprehensive versioning, update, and release management system for nWave. It enables users to track installed versions, update to latest releases, build custom local distributions, and (for repository admins) publish official releases through a controlled CI/CD pipeline.

The system follows Semantic Versioning (SemVer) with pre-release support, uses `pyproject.toml` as the version source of truth synchronized with Git tags, and integrates with GitHub Releases for distribution.

### Design Principles

- **Separation of Concerns**: Build, install, and release are distinct operations
- **User Customization Preserved**: Non-nWave user creations in `~/.claude/` are never touched
- **Safe Updates**: Full backup before any update, atomic download-then-install
- **Minimal Toolchain**: Python 3 mandatory; optional tools enhance experience
- **Simple UX**: "Less is more" - clear messages, minimal output, actionable errors

---

## Commands Summary

| Command | Purpose | User Type | Prerequisites |
|---------|---------|-----------|---------------|
| `/nw:version` | Display installed version, check for updates | All users | Python 3 |
| `/nw:update` | Update nWave to latest GitHub Release | All users | Python 3, curl/wget, tar, shasum |
| `/nw:forge` | Build custom local distribution to `dist/` | All users | Python 3, all tests pass |
| `/nw:forge:install` | Install built distribution from `dist/` to `~/.claude/` | All users | Python 3, valid `dist/` exists |
| `/nw:forge:release` | Create PR, run release pipeline, publish GitHub Release | Repo admins | Git, gh CLI, repository write access |

---

## User Stories

### US-001: Check Installed Version

**Problem (The Pain)**

Developers using nWave need to know what version they have installed and whether updates are available. Without this, they cannot make informed decisions about updating or troubleshooting version-specific issues.

**Who (The User)**

- nWave user with framework installed in `~/.claude/`
- Wants to verify installation and check for updates
- May be offline or have network issues

**Solution (What We Build)**

The `/nw:version` command displays the currently installed version and checks GitHub Releases for available updates. It performs a daily automatic check on first nWave usage, storing results in a watermark file.

**Domain Examples**

### Example 1: User Checks Version with Update Available
Marco runs `/nw:version` on his MacBook. His installed version is 1.2.3. The command queries GitHub Releases, finds 1.3.0 is available, and displays: "nWave v1.2.3 (update available: v1.3.0)"

### Example 2: User Checks Version When Up-to-Date
Sofia runs `/nw:version`. Her installed version is 1.3.0, which matches the latest GitHub Release. Display shows: "nWave v1.3.0 (up to date)"

### Example 3: User Checks Version While Offline
Luca runs `/nw:version` without network connectivity. The command displays: "nWave v1.2.3 (Unable to check for updates)"

### Example 4: Daily Auto-Check Triggers
Elena runs `/nw:start` (her first nWave command today). The system checks `~/.claude/nwave.update` watermark, sees last check was yesterday, silently checks GitHub for updates, and updates the watermark file.

**UAT Scenarios (BDD)**

### Scenario: Display version with update available
```gherkin
Given Marco has nWave v1.2.3 installed in ~/.claude/
And GitHub Releases shows v1.3.0 as latest
When Marco runs /nw:version
Then the output displays "nWave v1.2.3 (update available: v1.3.0)"
And the watermark file is updated with current timestamp
```

### Scenario: Display version when up-to-date
```gherkin
Given Sofia has nWave v1.3.0 installed
And GitHub Releases shows v1.3.0 as latest
When Sofia runs /nw:version
Then the output displays "nWave v1.3.0 (up to date)"
```

### Scenario: Display version when offline
```gherkin
Given Luca has nWave v1.2.3 installed
And network connectivity is unavailable
When Luca runs /nw:version
Then the output displays "nWave v1.2.3 (Unable to check for updates)"
And no error is thrown
```

### Scenario: Daily auto-check updates watermark
```gherkin
Given Elena has nWave installed
And the watermark file shows last_check was more than 24 hours ago
When Elena runs any nWave command
Then the system checks GitHub Releases in the background
And updates ~/.claude/nwave.update with new timestamp and latest_version
```

**Acceptance Criteria**

- [ ] Command displays installed version from `pyproject.toml`
- [ ] Command compares local version against latest GitHub Release tag
- [ ] Output format is "nWave v{version} ({status})" where status is "up to date", "update available: v{new}", or "Unable to check for updates"
- [ ] Watermark file `~/.claude/nwave.update` stores `last_check` timestamp and `latest_version`
- [ ] Daily auto-check runs on first nWave usage if last check > 24 hours ago
- [ ] Offline mode gracefully shows local version without error

**Technical Notes**

- Version source: `pyproject.toml` in installed nWave
- Watermark file format: minimal key-value (`last_check`, `latest_version`)
- GitHub API used for release comparison (no authentication required for public repos)

---

### US-002: Update nWave to Latest Release

**Problem (The Pain)**

Giulia has nWave v1.2.3 installed but v1.3.0 is available with bug fixes she needs. Manually downloading and installing updates is error-prone and risks losing her configuration. She needs a safe, automated update process with rollback capability.

**Who (The User)**

- nWave user wanting to update to latest official release
- Has custom non-nWave agents/commands they want preserved
- Needs safety net in case update causes issues

**Solution (What We Build)**

The `/nw:update` command downloads the latest GitHub Release, creates a full backup of `~/.claude/`, validates the download via SHA256 checksum, and installs the new version. It warns about breaking changes (major version bumps) and prompts for confirmation. Rolling retention keeps the last 3 backups.

**Domain Examples**

### Example 1: Standard Update
Giulia runs `/nw:update`. The command shows "Downloading nWave v1.3.0...", creates backup at `~/.claude.backup.20260127143022/`, validates checksum, installs, shows "Update complete. View changelog in browser? [y/N]"

### Example 2: Breaking Change Warning
Paolo runs `/nw:update`. His version is 1.3.0, available is 2.0.0. Command displays: "Major version change detected (1.x to 2.x). This may break existing workflows. Continue? [y/N]". Paolo types 'y' to proceed.

### Example 3: Update with Local RC Detected
Francesca has a local RC version from `/nw:forge`. She runs `/nw:update`. Warning displays: "Local customizations detected. Update will overwrite." She can proceed or cancel.

### Example 4: Network Failure During Download
Antonio runs `/nw:update`. Network drops mid-download. Error displays: "Download failed: network error. Your nWave installation is unchanged." No backup was modified.

### Example 5: Checksum Mismatch
Chiara runs `/nw:update`. Downloaded file fails SHA256 validation. Error displays: "Download corrupted (checksum mismatch). Update aborted. Your nWave installation is unchanged."

**UAT Scenarios (BDD)**

### Scenario: Successful update with changelog prompt
```gherkin
Given Giulia has nWave v1.2.3 installed
And GitHub Releases has v1.3.0 available with SHA256 checksum
When Giulia runs /nw:update
Then a full backup is created at ~/.claude.backup.{timestamp}/
And the release asset is downloaded from GitHub
And the download is validated against SHA256 checksum
And nWave is updated to v1.3.0 in ~/.claude/
And the output displays "Update complete. View changelog in browser? [y/N]"
```

### Scenario: Major version requires confirmation
```gherkin
Given Paolo has nWave v1.3.0 installed
And GitHub Releases has v2.0.0 available
When Paolo runs /nw:update
Then a warning displays "Major version change detected (1.x to 2.x). This may break existing workflows. Continue? [y/N]"
And the update only proceeds if Paolo confirms with 'y'
```

### Scenario: Local customizations warning
```gherkin
Given Francesca has a local RC version installed (v1.2.3-rc.main.20260127.1)
When Francesca runs /nw:update
Then a warning displays "Local customizations detected. Update will overwrite."
And Francesca can choose to proceed or cancel
```

### Scenario: Network failure leaves installation unchanged
```gherkin
Given Antonio has nWave v1.2.3 installed
And network fails during download
When Antonio runs /nw:update
Then an error displays "Download failed: network error. Your nWave installation is unchanged."
And ~/.claude/ contains the original v1.2.3 installation
And no backup was consumed or corrupted
```

### Scenario: Checksum validation failure
```gherkin
Given Chiara runs /nw:update
And the downloaded file has incorrect SHA256 checksum
When checksum validation runs
Then an error displays "Download corrupted (checksum mismatch). Update aborted. Your nWave installation is unchanged."
And the corrupted download is deleted
```

### Scenario: Backup rotation maintains 3 copies
```gherkin
Given Roberto has 3 existing backups in ~/.claude.backup.*/
When Roberto runs /nw:update successfully
Then a new backup is created
And the oldest backup is deleted
And exactly 3 backups remain
```

### Scenario: Non-nWave user content preserved
```gherkin
Given Maria has custom agents in ~/.claude/agents/ (not prefixed with "nw")
And custom commands in ~/.claude/commands/ (not prefixed with "nw")
When Maria runs /nw:update
Then her custom agents and commands remain untouched
And only nWave-prefixed content is replaced
```

**Acceptance Criteria**

- [ ] Downloads latest release from GitHub Releases
- [ ] Creates full backup of `~/.claude/` before installation
- [ ] Validates download using SHA256 checksum
- [ ] Warns and requires confirmation for major version changes
- [ ] Warns when local RC version detected
- [ ] Preserves non-nWave user content (agents/commands not prefixed with "nw")
- [ ] Replaces all nWave-prefixed content with new version
- [ ] Shows progress with modern ASCII UI and animated indicators
- [ ] Prompts "View changelog in browser? [y/N]" on success
- [ ] Network/download failures leave installation unchanged
- [ ] Maintains rolling retention of last 3 backups

**Technical Notes**

- Atomic update: download completes fully before any installation begins
- Backup location: `~/.claude.backup.{YYYYMMDDHHMMSS}/`
- Core identification: everything the build process creates with "nw" prefix
- Manual rollback: user can restore from backup directory themselves

---

### US-003: Build Custom Local Distribution

**Problem (The Pain)**

Alessandro wants to customize nWave for his team's specific workflow. He needs to modify agents, add new commands, and test changes locally before sharing. He needs a build process that validates his changes and creates a clean distribution.

**Who (The User)**

- nWave power user wanting to customize the framework
- May modify existing agents or add new ones
- Needs validation that changes don't break functionality

**Solution (What We Build)**

The `/nw:forge` command runs all tests and hooks, and if green, builds a custom distribution to `dist/`. The version becomes an RC with format `-rc.{branch}.{YYYYMMDD}.{N}` where N increments per day. After build, user is prompted to install.

**Domain Examples**

### Example 1: Successful Build
Alessandro runs `/nw:forge` on the main branch. All tests pass. Output shows build progress, creates `dist/` with built distribution, version becomes `1.2.3-rc.main.20260127.1`. Prompts: "Install: [Y/n]"

### Example 2: Tests Fail
Benedetta runs `/nw:forge`. Unit tests fail with 3 errors. Build aborts with message: "Build failed: 3 test failures. Fix tests before building."

### Example 3: Multiple Builds Same Day
Carlo runs `/nw:forge` twice on January 27th. First build: `1.2.3-rc.main.20260127.1`. Second build: `1.2.3-rc.main.20260127.2`. Counter resets next day.

### Example 4: Build on Feature Branch
Daniela runs `/nw:forge` on branch `feature/new-agent`. Version becomes `1.2.3-rc.feature-new-agent.20260127.1`.

**UAT Scenarios (BDD)**

### Scenario: Successful build with install prompt
```gherkin
Given Alessandro is on the main branch
And all tests and hooks pass
When Alessandro runs /nw:forge
Then dist/ is cleaned and rebuilt
And version is set to {base-version}-rc.main.{YYYYMMDD}.1
And build progress shows with animated ASCII UI
And prompt displays "Install: [Y/n]"
```

### Scenario: Build fails when tests fail
```gherkin
Given Benedetta has failing tests in her codebase
When Benedetta runs /nw:forge
Then the build process runs tests first
And build aborts when tests fail
And error displays "Build failed: {N} test failures. Fix tests before building."
And dist/ is not modified
```

### Scenario: RC counter increments within same day
```gherkin
Given Carlo built version 1.2.3-rc.main.20260127.1 earlier today
When Carlo runs /nw:forge again on the same day
Then version becomes 1.2.3-rc.main.20260127.2
And previous dist/ is cleaned before new build
```

### Scenario: RC counter resets on new day
```gherkin
Given Carlo built version 1.2.3-rc.main.20260127.3 yesterday
When Carlo runs /nw:forge today (January 28th)
Then version becomes 1.2.3-rc.main.20260128.1
```

### Scenario: Branch name included in RC version
```gherkin
Given Daniela is on branch feature/new-agent
When Daniela runs /nw:forge
Then version becomes {base-version}-rc.feature-new-agent.{YYYYMMDD}.{N}
And special characters in branch name are normalized to hyphens
```

**Acceptance Criteria**

- [ ] Runs all tests and hooks before building
- [ ] Build only proceeds if all tests are green
- [ ] Cleans `dist/` directory before building
- [ ] Version format: `{base}-rc.{branch}.{YYYYMMDD}.{N}`
- [ ] RC counter increments per day, resets on new day
- [ ] Branch name normalized (slashes to hyphens)
- [ ] Shows progress with modern ASCII UI
- [ ] Prompts "Install: [Y/n]" on successful build
- [ ] If user selects Y, invokes `/nw:forge:install`

**Technical Notes**

- Base version read from `pyproject.toml`
- RC counter stored in build metadata or derived from existing `dist/` version
- Branch name from `git branch --show-current`
- Full modification allowed: users can change anything in their local copy

---

### US-004: Install Built Distribution

**Problem (The Pain)**

Elena has built a custom nWave distribution with `/nw:forge` and wants to install it to her `~/.claude/` directory. She needs a clean installation process that doesn't leave her system in a broken state.

**Who (The User)**

- nWave user who has successfully run `/nw:forge`
- Has a valid `dist/` directory with built distribution
- Wants to install custom version to `~/.claude/`

**Solution (What We Build)**

The `/nw:forge:install` command copies the contents of `dist/` to `~/.claude/`, replacing all nWave-prefixed content while preserving non-nWave user content. A smoke test verifies the installation.

**Domain Examples**

### Example 1: Successful Installation
Elena runs `/nw:forge:install`. Distribution copies from `dist/` to `~/.claude/`. Smoke test runs `/nw:version` which displays the RC version. Success message shows.

### Example 2: No dist/ Directory
Fabio runs `/nw:forge:install` without running `/nw:forge` first. Error: "No distribution found. Run /nw:forge first to build."

### Example 3: Corrupt dist/ Directory
Greta runs `/nw:forge:install` but `dist/` is missing key files. Error: "Invalid distribution: missing required files. Rebuild with /nw:forge."

**UAT Scenarios (BDD)**

### Scenario: Successful installation with smoke test
```gherkin
Given Elena has a valid dist/ directory from /nw:forge
When Elena runs /nw:forge:install
Then the contents of dist/ are copied to ~/.claude/
And nWave-prefixed content in ~/.claude/ is replaced
And non-nWave user content is preserved
And smoke test runs /nw:version successfully
And success message displays "Installation complete."
```

### Scenario: Installation fails without dist/
```gherkin
Given Fabio has no dist/ directory
When Fabio runs /nw:forge:install
Then error displays "No distribution found. Run /nw:forge first to build."
And ~/.claude/ is unchanged
```

### Scenario: Installation fails with invalid dist/
```gherkin
Given Greta has a dist/ directory missing required files
When Greta runs /nw:forge:install
Then error displays "Invalid distribution: missing required files. Rebuild with /nw:forge."
And ~/.claude/ is unchanged
```

**Acceptance Criteria**

- [ ] Validates `dist/` directory exists and contains required files
- [ ] Copies `dist/` contents to `~/.claude/`
- [ ] Replaces all nWave-prefixed content
- [ ] Preserves non-nWave user content
- [ ] Runs smoke test (`/nw:version`) after installation
- [ ] Displays simple success message on completion
- [ ] Shows actionable error if `dist/` missing or invalid

**Technical Notes**

- Required files validation: check for essential nWave structure
- Smoke test: run `/nw:version` to verify installation works
- No backup created (user can run `/nw:update` to restore official version)

---

### US-005: Create Official Release

**Problem (The Pain)**

Matteo is a repository admin who needs to publish a new official nWave release. He needs an automated pipeline that validates the release, creates proper versioning, generates changelog, and publishes to GitHub Releases.

**Who (The User)**

- GitHub repository administrator with write access
- Has changes in `development` branch ready for release
- Needs controlled release process with proper versioning

**Solution (What We Build)**

The `/nw:forge:release` command creates a PR from `development` to `main`. The PR triggers the CI/CD pipeline which runs all tests. On merge to `main`, the release pipeline bumps the version, builds `dist/`, generates changelog from conventional commits, creates a Git tag, and publishes a GitHub Release with the distribution assets.

**Domain Examples**

### Example 1: Successful Release
Matteo runs `/nw:forge:release` on development branch. PR is created to main. Pipeline runs, all tests pass. Matteo approves and merges. Release pipeline bumps version to 1.3.0, generates changelog, creates tag v1.3.0, publishes GitHub Release with dist/ contents.

### Example 2: Pipeline Fails
Nicoletta runs `/nw:forge:release`. PR is created, but pipeline fails due to test errors. PR cannot be merged until tests pass.

### Example 3: User Lacks Permission
Oscar runs `/nw:forge:release` but doesn't have repository write access. Git rejects the push. Error displays: "Permission denied. You don't have access to create releases for this repository."

### Example 4: Not on Development Branch
Paola runs `/nw:forge:release` from `main` branch. Error: "Release must be initiated from the development branch."

**UAT Scenarios (BDD)**

### Scenario: Successful release workflow
```gherkin
Given Matteo has repository admin access
And he is on the development branch with committed changes
When Matteo runs /nw:forge:release
Then a PR is created from development to main
And the CI/CD pipeline runs all tests
And when Matteo approves and merges the PR
Then the release pipeline triggers
And version is bumped in pyproject.toml
And changelog is generated from conventional commits
And a Git tag is created (v{version})
And a GitHub Release is published with dist/ contents
```

### Scenario: Pipeline failure blocks merge
```gherkin
Given Nicoletta creates a PR via /nw:forge:release
And the pipeline has failing tests
When pipeline completes
Then the PR shows failed status
And merge is blocked until tests pass
```

### Scenario: Permission denied for non-admin
```gherkin
Given Oscar does not have repository write access
When Oscar runs /nw:forge:release
Then Git rejects the operation
And error displays "Permission denied. You don't have access to create releases for this repository."
```

### Scenario: Wrong branch error
```gherkin
Given Paola is on the main branch
When Paola runs /nw:forge:release
Then error displays "Release must be initiated from the development branch."
And no PR is created
```

**Acceptance Criteria**

- [ ] Command only runs from `development` branch
- [ ] Creates PR from `development` to `main`
- [ ] PR triggers CI/CD pipeline with full test suite
- [ ] On merge, release pipeline bumps version in `pyproject.toml`
- [ ] Changelog generated from conventional commits
- [ ] Git tag created with version (v{version})
- [ ] GitHub Release created with `dist/` contents as assets
- [ ] Permission errors trapped and shown with clear message
- [ ] Branch protection on `main` enforced via repository settings

**Technical Notes**

- Requires: Git, gh CLI, repository write access
- Version bump happens post-merge in release pipeline
- Changelog format derived from conventional commits (feat:, fix:, breaking:, etc.)
- Release assets: contents of `dist/` that get copied to user's `~/.claude/`
- Repository requirements: protected main branch, PRs required for merging

---

## Technical Requirements

### Prerequisites by Command

| Command | Python 3 | curl/wget | tar | shasum | git | gh CLI |
|---------|----------|-----------|-----|--------|-----|--------|
| `/nw:version` | Required | - | - | - | - | - |
| `/nw:update` | Required | Required | Required | Required | - | - |
| `/nw:forge` | Required | - | - | - | Required | - |
| `/nw:forge:install` | Required | - | - | - | - | - |
| `/nw:forge:release` | Required | - | - | - | Required | Required |

### Directory Structure

```
~/.claude/                          # Installation root
  agents/
    nw/                            # nWave agents (core)
    {user-custom}/                 # User agents (preserved)
  commands/
    nw/                            # nWave commands (core)
    {user-custom}/                 # User commands (preserved)
  nwave.update                     # Watermark file

~/.claude.backup.{timestamp}/      # Backup directories (max 3 retained)

{repo}/
  dist/                            # Build output (cleaned on each build)
  pyproject.toml                   # Version source of truth
```

### File Formats

**Watermark File (`~/.claude/nwave.update`)**
```
last_check: 2026-01-27T14:30:22Z
latest_version: 1.3.0
```

**Version Format**
- Official: `MAJOR.MINOR.PATCH` (e.g., `1.2.3`)
- Pre-release: `MAJOR.MINOR.PATCH-rc.{branch}.{YYYYMMDD}.{N}` (e.g., `1.2.3-rc.main.20260127.1`)

### Core Identification

Content is considered "core" (nWave-owned) if:
- It is prefixed with `nw` (e.g., `agents/nw/`, `commands/nw/`)
- It is produced by the build process and included in `dist/`

User content without `nw` prefix is never touched by update/install operations.

---

## Error Handling

### Network Errors

| Scenario | Behavior |
|----------|----------|
| Network unavailable during version check | Show local version + "Unable to check for updates" |
| Network fails during download | Error message, installation unchanged, no partial state |
| GitHub API rate limited | Error message with retry suggestion |

### Validation Errors

| Scenario | Behavior |
|----------|----------|
| SHA256 checksum mismatch | Abort update, delete corrupted download, clear error message |
| Invalid `dist/` structure | Block installation, list missing required files |
| Tests fail during forge | Abort build, show failure count and message |

### Permission Errors

| Scenario | Behavior |
|----------|----------|
| No write access to `~/.claude/` | Error with permission fix suggestion |
| No repository access for release | Trap Git error, show "Permission denied" message |
| Cannot create backup directory | Error before any modification attempted |

### State Conflicts

| Scenario | Behavior |
|----------|----------|
| Local RC version when running update | Warn "Local customizations detected. Update will overwrite." |
| Uncommitted `dist/` when running update | Warn and block, let user take action |
| Update interrupted mid-process | Download-first approach ensures no partial state |

---

## User Experience

### Progress Feedback

All long-running operations show modern ASCII UI with animated progress indicators:
- Downloading...
- Validating...
- Installing...
- Running tests...

### Output Philosophy

"Less is more" - simple, clear messages:
- Success: "Update complete." with optional changelog prompt
- Failure: "Update failed: {specific reason}"
- Actionable: errors include what to do next

### Confirmation Prompts

| Prompt | Default | When |
|--------|---------|------|
| "Continue? [y/N]" | No | Breaking changes (major version) |
| "Install: [Y/n]" | Yes | After successful forge build |
| "View changelog in browser? [y/N]" | No | After successful update |

---

## Future Considerations

Items explicitly parked for future development:

- **`/nw:doctor`**: Health check command to validate installation integrity, verify all required files present, check for corruption, validate agent schemas
- **`/nw:rollback`**: Automated rollback command (currently manual via backup restoration)
- **Configurable backup retention**: Currently fixed at 3, could be user-configurable
- **Update channels**: Stable vs. pre-release update channels
- **Offline installation**: Install from local archive without network

---

## Appendix: Conventional Commits for Changelog

The release pipeline generates changelog from commit messages following conventional commits:

| Prefix | Changelog Section |
|--------|------------------|
| `feat:` | Features |
| `fix:` | Bug Fixes |
| `breaking:` or `BREAKING CHANGE:` | Breaking Changes |
| `docs:` | Documentation |
| `chore:` | Maintenance |
| `refactor:` | Refactoring |
| `test:` | Tests |
| `perf:` | Performance |

Example commit: `feat(agents): add new researcher agent for deep analysis`

---

## Document Metadata

| Field | Value |
|-------|-------|
| Feature | nWave Versioning and Release Management |
| Wave | DISCUSS |
| Status | Requirements Complete |
| Author | Riley (product-owner) |
| Stakeholder | Mike |
| Created | 2026-01-27 |
| Version | 1.0.0 |
