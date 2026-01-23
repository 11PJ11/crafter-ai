# nWave Version Update Experience - DISCUSS Wave Output

**Wave:** DISCUSS
**Status:** Requirements validated
**Next Wave:** DESIGN
**Feature:** Version delivery and update loop for end users
**Stakeholders:** Mike (framework maintainer + end user), Alessandro (collaborator)

---

## Business Objectives

1. **Version visibility** - Users know their installed version and available updates at a glance
2. **Safe updates** - Backup mechanism protects user configurations before any update
3. **Clear changelog** - Users understand what changed between versions
4. **Breaking change awareness** - Major version bumps clearly warn users of potential migration needs
5. **Self-service updates** - Users can update without developer intervention or git knowledge

---

## Problem Statement

Users who install nWave locally via `python scripts/install/install_nwave.py` have no clear update flow when new versions release on GitHub:

| Pain Point | Current State | Impact |
|------------|---------------|--------|
| No version awareness | Users don't know their installed version | Cannot report issues accurately |
| No update notifications | Users discover updates accidentally | Miss important fixes and features |
| No changelog | Users don't know what changed | Fear of updating, technical debt |
| No breaking change warnings | Major versions ship without migration guidance | Update failures, frustration |
| Developer-focused tooling | `update_nwave.py --force` requires git knowledge | Non-technical users excluded |

---

## Solution Overview

Close the "version delivery & update loop" with four components:

1. **GitHub semantic versioning** - Conventional commits + semantic-release for automated tags and changelog
2. **Version command** (`/nw:version`) - Show installed version, check for updates via GitHub API
3. **Update command** (`/nw:update`) - Safe auto-bump with backup and confirmation
4. **Documentation** - DIVIO-compliant README with install AND update instructions

---

## User Stories

### US-001: Check Installed Version

**As** an nWave user
**I want** to see my currently installed version
**So that** I can report issues accurately and know if I'm up to date

**Acceptance Criteria:**

```gherkin
Scenario: Display installed version when up to date
  Given nWave version 1.5.7 is installed locally
  And GitHub latest release is 1.5.7
  When I run /nw:version
  Then I see "nWave v1.5.7 (up to date)"

Scenario: Display installed version with update available
  Given nWave version 1.5.7 is installed locally
  And GitHub latest release is 1.6.0
  When I run /nw:version
  Then I see an attention-grabbing banner showing:
    | Current version  | 1.5.7 |
    | Available update | 1.6.0 |
    | Changelog highlights | 2-3 bullet points |
    | Update command | "Run /nw:update to upgrade" |

Scenario: Network failure during version check
  Given nWave version 1.5.7 is installed locally
  And GitHub API is unreachable
  When I run /nw:version
  Then I see "nWave v1.5.7 (installed)"
  And I see "Could not check for updates. Try again later or check manually at https://github.com/{org}/nwave/releases"
```

---

### US-002: Update nWave Safely

**As** an nWave user
**I want** to update to the latest version with a safety backup
**So that** I can recover if something goes wrong

**Acceptance Criteria:**

```gherkin
Scenario: Successful update with backup
  Given nWave version 1.5.7 is installed at ~/.claude/
  And GitHub latest release is 1.6.0
  When I run /nw:update
  Then the system creates backup at ~/.claude_bck_20260123/
  And I see warning: "Backup created at ~/.claude_bck_20260123/"
  And I see changelog showing what will change
  And I am prompted "Proceed with update? (Y/N)"
  When I confirm with Y
  Then nWave 1.6.0 is installed
  And I see summary:
    | Updated to     | 1.6.0 |
    | Key changes    | 2-3 bullet points |
    | Full changelog | https://github.com/{org}/nwave/releases/tag/v1.6.0 |

Scenario: Update cancelled by user
  Given nWave version 1.5.7 is installed
  And GitHub latest release is 1.6.0
  When I run /nw:update
  And I see the confirmation prompt
  And I respond with N
  Then no changes are made
  And backup is deleted (cleanup)
  And I see "Update cancelled. No changes made."

Scenario: Already up to date
  Given nWave version 1.6.0 is installed
  And GitHub latest release is 1.6.0
  When I run /nw:update
  Then I see "Already running latest version (1.6.0). No update needed."
```

---

### US-003: Breaking Change Warning

**As** an nWave user
**I want** clear warning when updating across major versions
**So that** I understand migration may be required

**Acceptance Criteria:**

```gherkin
Scenario: Major version update warning
  Given nWave version 1.5.7 is installed
  And GitHub latest release is 2.0.0
  When I run /nw:version
  Then the banner includes prominent breaking change warning
  And changelog highlights include "BREAKING CHANGES" section

Scenario: Minor version update (no warning)
  Given nWave version 1.5.7 is installed
  And GitHub latest release is 1.6.0
  When I run /nw:version
  Then no breaking change warning is shown
  And changelog shows feature additions and fixes only
```

---

### US-004: Automatic Backup Cleanup

**As** an nWave user
**I want** old backups automatically cleaned up
**So that** my disk doesn't fill with stale backup directories

**Acceptance Criteria:**

```gherkin
Scenario: Cleanup backups older than 30 days
  Given these backup directories exist:
    | Directory                    | Age     |
    | ~/.claude_bck_20251201/      | 53 days |
    | ~/.claude_bck_20251215/      | 39 days |
    | ~/.claude_bck_20260110/      | 13 days |
  When I run /nw:update and confirm
  Then ~/.claude_bck_20251201/ is deleted (>30 days)
  And ~/.claude_bck_20251215/ is deleted (>30 days)
  And ~/.claude_bck_20260110/ is preserved (<30 days)
  And new backup ~/.claude_bck_20260123/ is created
```

---

## Technical Requirements

### TR-001: Version Source of Truth

| Component | Location | Purpose |
|-----------|----------|---------|
| Local version | `~/.claude/nWave/VERSION` file | Installed version |
| Remote version | GitHub API: latest release tag | Available version |
| Changelog | GitHub release notes OR `CHANGELOG.md` | What changed |

### TR-002: GitHub API Integration

**Endpoint:** `GET https://api.github.com/repos/{org}/nwave/releases/latest`

**Response parsing:**
- `tag_name` - Version string (e.g., "v1.6.0")
- `body` - Release notes (changelog)
- `published_at` - Release date

**Error handling:**
- Network timeout: 10 seconds
- Rate limiting: Graceful degradation with retry hint
- Invalid response: Show local version only with warning

### TR-003: Backup Specification

| Aspect | Specification |
|--------|---------------|
| Source | `~/.claude/` directory (entire contents) |
| Destination | `~/.claude_bck_YYYYMMDD/` (date of backup) |
| Naming | ISO date format, no time component |
| Retention | 30 days default (configurable via env var) |
| Cleanup trigger | During update process, after successful backup creation |

### TR-004: Semantic Versioning Detection

**Breaking change detection:** Major version bump only (1.x.x -> 2.x.x)

**Version comparison logic:**
```
current: 1.5.7
available: 2.0.0
comparison: MAJOR changed (1 -> 2) = BREAKING CHANGE WARNING
```

### TR-005: Conventional Commit Enforcement

**Purpose:** Semantic-release depends on structured git history. Enforcement happens at commit time, not CI.

**Flow:**
```
Developer commits → commit-msg hook validates format → reject or accept
```

**Commit message format (Conventional Commits 1.0.0):**
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Allowed types:**
| Type | Changelog Section | Version Bump |
|------|-------------------|--------------|
| `feat` | Features | MINOR |
| `fix` | Bug Fixes | PATCH |
| `docs` | Documentation | none |
| `style` | Styles | none |
| `refactor` | Code Refactoring | none |
| `perf` | Performance Improvements | PATCH |
| `test` | Tests | none |
| `build` | Build System | none |
| `ci` | CI | none |
| `chore` | Chores | none |
| `revert` | Reverts | PATCH |

**Breaking changes:** Append `!` after type (e.g., `feat!:`) or include `BREAKING CHANGE:` in footer.

**Hook behavior:**
- **Valid commit:** Accept silently
- **Invalid commit:** Reject with helpful error message showing:
  - What was wrong
  - Expected format with examples
  - Link to Conventional Commits spec

**Error message example:**
```
ERROR: Commit message does not follow Conventional Commits format.

Your message:
  "fixed the login bug"

Expected format:
  <type>[scope]: <description>

Examples:
  feat: add user authentication
  fix(auth): resolve login timeout issue
  feat!: redesign API (breaking change)

See: https://www.conventionalcommits.org/
```

### TR-006: Pre-push Validation

**Purpose:** Ensure version/changelog coherence before code reaches remote.

**Flow:**
```
Developer pushes → pre-push hook validates → reject or accept
```

**Validation checks:**

| Check | Validation | On Failure |
|-------|------------|------------|
| VERSION file exists | `nWave/VERSION` present in repo | Reject push with instructions |
| VERSION format valid | Semantic version format (X.Y.Z) | Reject push with format guidance |
| semantic-release configured | `.releaserc` or `release.config.js` exists | Reject push with setup instructions |

**Hook behavior:**
- **All checks pass:** Push proceeds
- **Any check fails:** Reject with specific error and remediation steps

**Error message example:**
```
ERROR: Pre-push validation failed.

[FAIL] VERSION file missing
       Expected: nWave/VERSION
       Action: Create VERSION file with current version (e.g., "1.5.7")

[FAIL] semantic-release not configured
       Expected: .releaserc or release.config.js
       Action: Run 'npx semantic-release-cli setup' or create config manually

Push rejected. Fix the above issues and try again.
```

---

## Non-Functional Requirements

### NFR-001: Performance

| Metric | Target |
|--------|--------|
| Version check response | < 3 seconds (including API call) |
| Backup creation | < 30 seconds for typical ~/.claude/ size |
| Update installation | < 60 seconds |

### NFR-002: Reliability

| Scenario | Behavior |
|----------|----------|
| Network failure | Graceful degradation, show local version |
| Partial update failure | Rollback from backup, clear error message |
| Disk full during backup | Fail before update, clear error message |

### NFR-003: Security

| Concern | Mitigation |
|---------|------------|
| GitHub API rate limiting | Cache-free design (real-time check only) |
| Man-in-the-middle | HTTPS only for GitHub API |
| Backup permissions | Match original ~/.claude/ permissions |

---

## Artifacts Required

### Documentation Artifacts

| Artifact | Location | Purpose |
|----------|----------|---------|
| CHANGELOG.md | Repository root | Version history (AUTO-GENERATED by semantic-release) |
| VERSION file | `~/.claude/nWave/VERSION` | Local version tracking |
| README update | Repository README.md | Install AND update instructions |

### Git Hooks Configuration

| Artifact | Location | Purpose |
|----------|----------|---------|
| `.pre-commit-config.yaml` | Repository root | Hook orchestration (commit-msg, pre-push) |
| `commitlint.config.js` | Repository root | Conventional commit validation rules |
| `.commitlintrc` (alternative) | Repository root | Commitlint configuration (YAML/JSON) |

**Pre-commit config additions:**
```yaml
repos:
  - repo: https://github.com/commitizen-tools/commitizen
    rev: v3.x.x
    hooks:
      - id: commitizen
        stages: [commit-msg]

  # Alternative: commitlint
  - repo: https://github.com/alessandrojcm/commitlint-pre-commit-hook
    rev: v9.x.x
    hooks:
      - id: commitlint
        stages: [commit-msg]
        additional_dependencies: ['@commitlint/config-conventional']
```

**Commitlint config:**
```javascript
// commitlint.config.js
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [2, 'always', [
      'feat', 'fix', 'docs', 'style', 'refactor',
      'perf', 'test', 'build', 'ci', 'chore', 'revert'
    ]],
    'subject-case': [2, 'always', 'lower-case'],
    'header-max-length': [2, 'always', 100]
  }
};
```

### GitHub Configuration

| Artifact | Purpose |
|----------|---------|
| Conventional commits enforcement | Git hooks validate format at commit time |
| semantic-release config | Automated version bumping and changelog generation |
| GitHub Actions workflow | Release automation on tag push |

**semantic-release config (`.releaserc`):**
```json
{
  "branches": ["main", "master"],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    "@semantic-release/changelog",
    ["@semantic-release/npm", { "npmPublish": false }],
    "@semantic-release/github",
    ["@semantic-release/git", {
      "assets": ["CHANGELOG.md", "package.json"],
      "message": "chore(release): ${nextRelease.version} [skip ci]"
    }]
  ]
}
```

### Commands

| Command | Purpose |
|---------|---------|
| `/nw:version` | Display version status and update availability |
| `/nw:update` | Perform safe update with backup |

---

## Scope Definition

### MVP (Must Have)

- [ ] `/nw:version` command with GitHub API check
- [ ] `/nw:update` command with backup and confirmation
- [ ] Attention-grabbing update notification banner
- [ ] Breaking change warning on major version bump
- [ ] Backup creation at `~/.claude_bck_YYYYMMDD/`
- [ ] Backup retention policy (30 days auto-cleanup)
- [ ] Network failure graceful degradation
- [ ] README documentation for install and update
- [ ] Conventional commit enforcement via commit-msg hook
- [ ] Pre-push validation for VERSION file and semantic-release config
- [ ] semantic-release configuration for auto-generated changelog

### Nice to Have (Future)

- [ ] Configurable backup retention period (env var)
- [ ] `--dry-run` flag for update command
- [ ] Rollback command to restore from specific backup
- [ ] Update notifications in other nWave commands (passive)
- [ ] Offline changelog cache

### Out of Scope

- [ ] Automatic updates (always require user confirmation)
- [ ] GUI/visual installer
- [ ] Multiple version management (like nvm/pyenv)
- [ ] Partial/selective updates

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| GitHub API rate limiting | Low | Medium | No caching, real-time checks only |
| Backup disk space | Medium | Low | 30-day auto-cleanup |
| Update fails mid-process | Low | High | Backup-first, atomic operations |
| Breaking change not detected | Low | Medium | Semantic versioning discipline |

---

## Validation Decisions (from stakeholder discussion)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Version source | GitHub API (real-time) | Always accurate, no stale cache |
| Network failure | Fail gracefully with retry hint | Clear user guidance |
| Notification style | Attention-grabbing banner | Users won't miss updates |
| Breaking change detection | Semantic version only | Simple, reliable |
| Update confirmation | Always confirm (Y/N) | Safe default |
| Post-update feedback | Summary with changelog link | Informative but not verbose |
| Backup naming | `~/.claude_bck_YYYYMMDD/` | Clear, sortable, predictable |
| Backup retention | 30 days auto-cleanup | Balance disk space and safety |

---

## DISCUSS Wave Handoff

### Requirements Summary

| Requirement | Priority | Status |
|-------------|----------|--------|
| Version command with GitHub API | HIGH | Defined |
| Update command with backup | HIGH | Defined |
| Attention-grabbing notification | HIGH | Defined |
| Breaking change warning | HIGH | Defined |
| Backup creation and naming | HIGH | Defined |
| Conventional commit enforcement (TR-005) | HIGH | Defined |
| Pre-push validation (TR-006) | HIGH | Defined |
| semantic-release auto-changelog | HIGH | Defined |
| Backup auto-cleanup (30 days) | MEDIUM | Defined |
| Network failure handling | MEDIUM | Defined |
| README documentation | MEDIUM | Defined |
| Configurable retention | LOW | Deferred |
| Rollback command | LOW | Deferred |

### Open Questions for DESIGN Wave

1. **VERSION file format:** Plain text version string or structured (JSON/YAML)?
2. **Changelog source:** semantic-release auto-generates CHANGELOG.md; do we also parse GitHub release body?
3. **Hook tooling choice:** commitlint vs commitizen vs custom script?
4. **Backup atomicity:** Use temp directory then rename, or direct copy?
5. **CI/CD pipeline:** GitHub Actions workflow design for semantic-release execution

### Next Steps (DESIGN Wave)

1. Design VERSION file format and location
2. Design GitHub API integration module
3. Design backup/restore mechanism
4. Design semantic-release configuration
5. Create technical architecture for commands

---

## Appendix: User Flow Diagrams

### Version Check Flow

```
User runs /nw:version
        │
        ▼
Read local VERSION file
        │
        ▼
Query GitHub API for latest release
        │
        ├─── Success ──────────────────┐
        │                              ▼
        │                    Compare versions
        │                              │
        │                    ┌─────────┴─────────┐
        │                    │                   │
        │              Up to date          Update available
        │                    │                   │
        │                    ▼                   ▼
        │              "v1.5.7              Show banner:
        │              (up to date)"        - Version diff
        │                                   - Changelog highlights
        │                                   - Breaking change warning?
        │                                   - Update command hint
        │
        └─── Failure ──────────────────┐
                                       ▼
                              "v1.5.7 (installed)
                              Could not check for updates.
                              Try again later or check:
                              https://github.com/.../releases"
```

### Update Flow

```
User runs /nw:update
        │
        ▼
Check for updates (same as /nw:version)
        │
        ├─── Already up to date ───────┐
        │                              ▼
        │                    "Already running latest (1.6.0)"
        │
        └─── Update available ─────────┐
                                       ▼
                              Create backup ~/.claude_bck_YYYYMMDD/
                                       │
                                       ▼
                              Show: "Backup created at..."
                              Show: Changelog (what will change)
                              Prompt: "Proceed? (Y/N)"
                                       │
                              ┌────────┴────────┐
                              │                 │
                           Y (confirm)       N (cancel)
                              │                 │
                              ▼                 ▼
                    Clean up old backups   Delete new backup
                    (>30 days)             "Update cancelled"
                              │
                              ▼
                    Download and install
                    new version
                              │
                              ▼
                    Show summary:
                    - "Updated to 1.6.0"
                    - Key changes (bullets)
                    - Full changelog link
```

### Commit-to-Release Pipeline (Developer Side)

```
Developer writes code
        │
        ▼
git commit -m "feat: add user dashboard"
        │
        ▼
┌───────────────────────────────────────┐
│  commit-msg hook (commitlint)         │
│  Validates conventional commit format │
└───────────────────────────────────────┘
        │
        ├─── Invalid format ───────────┐
        │                              ▼
        │                    REJECT with helpful error:
        │                    - What was wrong
        │                    - Expected format
        │                    - Examples
        │                    (Commit does not proceed)
        │
        └─── Valid format ─────────────┐
                                       ▼
                              Commit accepted locally
                                       │
                                       ▼
                              git push origin main
                                       │
                                       ▼
┌───────────────────────────────────────┐
│  pre-push hook                        │
│  Validates:                           │
│  - VERSION file exists                │
│  - semantic-release configured        │
└───────────────────────────────────────┘
        │
        ├─── Validation fails ─────────┐
        │                              ▼
        │                    REJECT with specific errors:
        │                    - Missing VERSION file
        │                    - Missing .releaserc
        │                    (Push does not proceed)
        │
        └─── Validation passes ────────┐
                                       ▼
                              Push to GitHub
                                       │
                                       ▼
┌───────────────────────────────────────┐
│  GitHub Actions (CI/CD)               │
│  semantic-release executes:           │
│  1. Analyze commits since last tag    │
│  2. Determine version bump            │
│  3. Generate CHANGELOG.md             │
│  4. Create git tag (v1.6.0)           │
│  5. Create GitHub Release             │
└───────────────────────────────────────┘
                                       │
                                       ▼
                              New release available
                              Users see via /nw:version
```
