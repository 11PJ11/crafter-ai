@horizontal @e2e @tui-redesign
Feature: Forge Build + Install TUI Journey
  As a developer using crafter-ai
  I want the build and install CLI output to feel like a modern, frictionless stream
  So that I feel confident and engaged throughout the process

  Background:
    Given the project has a valid pyproject.toml
    And the build toolchain is installed
    And the src/ directory exists

  # ─── VISUAL DESIGN SYSTEM ───────────────────────────────────────────

  @design-system
  Scenario: Output uses no tables, panels, or borders
    When any forge command produces output
    Then the output contains no Rich Table borders
    And the output contains no Rich Panel borders
    And the output contains no "===" horizontal rules
    And the output contains no "---" horizontal rules
    And the output contains no "╭" or "╰" box-drawing characters
    And the output contains no "┏" or "┗" table characters

  @design-system
  Scenario: Emoji vocabulary is consistent
    When any forge command produces output
    Then "✅" means a check passed or phase completed
    And "❌" means a check failed or operation blocked
    And "⚠️" means a non-blocking warning
    And "🔨" appears only for build phase headers
    And "📦" appears only for install phase headers
    And "🎉" appears only in the final celebration on healthy install
    And each output line contains at most one status emoji

  @design-system
  Scenario: Colors are semantic only
    When any forge command produces output
    Then green markup is used only for success states
    And red markup is used only for error states
    And yellow markup is used only for warning states
    And dim markup is used only for secondary information
    And no color is used for decorative purposes

  # ─── BUILD HAPPY PATH ───────────────────────────────────────────────

  @build @happy-path
  Scenario: Build phase header displays correctly
    When I run "crafter-ai forge build"
    Then the first non-blank line contains "🔨" and "Building crafter-ai"
    And the line is bold

  @build @happy-path
  Scenario: Build pre-flight checks display as streaming list
    When I run "crafter-ai forge build"
    Then I see "🔍 Pre-flight checks" indented 2 spaces
    And each check result appears on its own line indented 2 spaces
    And passed checks show "✅" followed by a descriptive message
    And warning checks show "⚠️" followed by a descriptive message
    And a summary line "✅ Pre-flight passed" appears after all checks

  @build @happy-path
  Scenario: Version display is minimal
    Given the current version is "0.1.0"
    And the calculated next version is "0.2.0" with bump type "minor"
    When I run "crafter-ai forge build"
    Then I see "📐 Version" indented 2 spaces
    And I see "0.1.0 → 0.2.0 (minor)" indented 2 spaces
    And no panel or box surrounds the version information

  @build @happy-path
  Scenario: Build spinner resolves to persistent line
    When I run "crafter-ai forge build"
    Then a spinner appears with text "⏳ Compiling wheel..."
    And when compilation completes the spinner is replaced
    And a persistent line "✅ Wheel built" with duration appears in output
    And the duration is shown in parentheses like "(1.2s)"

  @build @happy-path
  Scenario: Build complete line is concise
    When the build succeeds with wheel "crafter_ai-0.2.0-py3-none-any.whl"
    Then I see "🔨 Build complete: crafter_ai-0.2.0-py3-none-any.whl"
    And no summary panel or box is displayed

  # ─── INSTALL CONFIRMATION PROMPT ─────────────────────────────────────

  @build @install @happy-path
  Scenario: Install prompt appears after build success
    Given a build just completed successfully with version "0.2.0"
    When the build complete line has been displayed
    Then a blank line separates build from the prompt
    And I see "📦 Install crafter-ai 0.2.0? [Y/n]: "
    And the prompt uses the 📦 emoji
    And the version in the prompt matches the version from wheel METADATA
    And the default answer is "Y" (yes)
    And no panel or box surrounds the prompt

  @build @install @happy-path
  Scenario: User declines install at prompt
    Given a build just completed successfully
    When the user answers "n" to the install prompt
    Then I see "Install skipped." in dim
    And the process exits with code 0
    And no install phase runs

  # ─── INSTALL HAPPY PATH ─────────────────────────────────────────────

  @install @happy-path
  Scenario: Install phase continues seamlessly from build
    Given a build just completed successfully
    When the install phase begins
    Then one blank line separates build from install
    And I see "📦 Installing crafter-ai" as the install header
    And no repeated title or border from the build phase appears

  @install @happy-path
  Scenario: Install pre-flight checks display as streaming list
    When I run "crafter-ai forge install"
    Then I see "🔍 Pre-flight checks" indented 2 spaces
    And each install check appears on its own line indented 2 spaces
    And passed checks show "✅" followed by a descriptive message
    And a summary line "✅ Pre-flight passed" appears after all checks

  # ─── BACKUP SECTION ─────────────────────────────────────────────────

  @install @happy-path @backup
  Scenario: Upgrade backup shows section header with spinner and detail
    Given this is an upgrade from a previous version
    And agents, commands, and templates exist in ~/.claude/
    When the backup phase runs
    Then I see "💾 Backing up configuration" indented 2 spaces as a section header
    And a spinner appears with text "⏳ Creating backup..."
    And when backup completes a persistent line "✅ Backup saved" with duration appears
    And a dim detail line shows backed-up items and backup path
    And the backup path follows the pattern "~/.claude/backups/nwave-YYYYMMDD-HHMMSS"

  @install @happy-path @backup
  Scenario: Fresh install shows single backup skip line
    Given this is a fresh install with no previous version
    When the backup phase runs
    Then I see "💾 Fresh install, no backup needed" indented 2 spaces
    And no section header appears for backup
    And no spinner appears for backup
    And no detail line appears for backup

  # ─── INSTALLATION PROGRESS SECTION ─────────────────────────────────

  @install @happy-path @install-progress
  Scenario: Install section has header and spinner during pipx install
    When the install phase runs
    Then I see "⚙️ Installing" indented 2 spaces as a section header
    And a spinner appears with text "⏳ Installing via pipx..."
    And the spinner is visible during the pipx install operation
    And when install completes the spinner resolves to "✅ nWave installed via pipx" with duration
    And no silence gap exists between pre-flight checks and install completion

  @install @happy-path @install-progress
  Scenario: Install closure line uses product brand name
    When the install phase completes successfully
    Then the closure line says "nWave installed via pipx" not "crafter-ai installed via pipx"
    And the duration is shown in parentheses like "(2.9s)"

  # ─── SBOM MANIFEST SECTION ────────────────────────────────────────

  @install @happy-path @sbom
  Scenario: SBOM manifest shows what was installed
    When the install phase completes successfully
    Then I see "📋 What was installed" indented 2 spaces
    And I see the package name and version in dim text at 4-space indent
    And I see CLI entry points in dim text at 4-space indent
    And I see the install path prefixed with "→" in dim text at 4-space indent
    And no emojis appear on individual manifest lines

  @install @happy-path @sbom
  Scenario: SBOM manifest for fresh install omits component counts
    Given this is a fresh install with no previous version
    When the SBOM manifest displays
    Then I see "crafter-ai 0.2.0" as the package identity
    And I see "CLI: crafter-ai, nw" as the entry points
    And I see "→" followed by the pipx venv path as the install location
    And no agent, command, or template counts are shown

  @install @happy-path @sbom
  Scenario: SBOM manifest for upgrade includes component counts
    Given this is an upgrade from a previous version
    And agents, commands, and templates exist in ~/.claude/
    When the SBOM manifest displays
    Then I see agent, command, and template counts in dim text
    And the counts reflect actual files in ~/.claude/ subdirectories

  @install @happy-path @sbom
  Scenario: SBOM manifest data comes from correct sources
    When the SBOM manifest displays
    Then the package name originates from pyproject.toml [project].name
    And the version originates from wheel METADATA
    And the install path originates from pipx list_packages()

  # ─── HEALTH VERIFICATION ──────────────────────────────────────────

  @install @happy-path
  Scenario: Health verification displays as check list
    When post-install verification runs
    Then I see "🩺 Verifying installation"
    And individual health checks appear as "✅" lines
    And a summary line shows "✅ Health: HEALTHY" in green

  # ─── CELEBRATION MOMENT ──────────────────────────────────────────────

  @celebration @happy-path
  Scenario: Healthy installation celebration uses product brand
    Given the build and install completed successfully
    And the health status is "HEALTHY"
    When the celebration displays
    Then I see "🎉 nWave 0.2.0 installed and healthy!" in bold green
    And I see "Ready to use in Claude Code." in dim on the next line
    And the celebration is exactly 2 lines
    And the celebration uses "nWave" not "crafter-ai"
    And shared artifact "version" matches the version from the build phase

  @celebration
  Scenario: Degraded installation celebration
    Given the install completed with degraded health
    When the celebration displays
    Then I see "⚠️" instead of "🎉"
    And the message says "installed with warnings" instead of "installed and healthy"
    And a hint says "Run 'crafter-ai doctor' for details."

  # ─── ERROR STATES ────────────────────────────────────────────────────

  @error @build
  Scenario: Blocking build pre-flight failure
    Given pyproject.toml does not exist
    And the src/ directory does not exist
    When I run "crafter-ai forge build"
    Then all checks still display (both passed and failed)
    And I see "Build blocked: 2 checks failed" in red
    And each failure is repeated below with "❌" and its message
    And each failure has a "Fix:" line with remediation in dim
    And the process exits with code 1
    And no table or panel is used for error display

  @error @install
  Scenario: Blocking install pre-flight failure
    Given no wheel file exists in dist/
    When I run "crafter-ai forge install"
    Then all checks display
    And I see "Install blocked:" with failure count in red
    And remediation is shown for each failure
    And the process exits with code 1

  @error @build
  Scenario: Build compilation failure
    When the wheel compilation fails
    Then the spinner resolves to "❌ Build failed"
    And an "Error:" line shows the failure reason
    And a "Fix:" line shows remediation if available
    And the process exits with code 1

  @error @install
  Scenario: pipx install failure
    When the pipx installation fails
    Then the spinner resolves to "❌ Installation failed"
    And an "Error:" line shows the failure reason
    And a "Fix:" line shows remediation if available
    And the process exits with code 1

  # ─── SPINNER BEHAVIOR ───────────────────────────────────────────────

  @interaction
  Scenario: Every spinner leaves a trace in stdout
    When any operation uses a spinner
    Then after the spinner completes
    And a permanent line with result emoji and duration is printed
    And the line remains visible in terminal scrollback
    And the spinner animation itself is cleared

  # ─── SHARED ARTIFACT CONSISTENCY ─────────────────────────────────────

  @horizontal @integration
  Scenario: Version is consistent across all displays
    Given the determined version is "0.2.0"
    When the full build + install flow completes
    Then the version line shows "0.2.0"
    And the wheel filename contains "0.2.0"
    And the install prompt contains "0.2.0"
    And the SBOM manifest contains "0.2.0"
    And the celebration message contains "0.2.0"
    And all five originate from wheel METADATA as the single source of truth

  @horizontal @integration
  Scenario: Health status drives celebration variant
    When the install completes
    Then the health verification result determines the celebration emoji
    And "HEALTHY" produces "🎉"
    And "DEGRADED" produces "⚠️"
    And the same HealthStatus value is used for both displays

  # ─── WALKING SKELETON: FULL E2E FLOW ──────────────────────────────

  @walking-skeleton @e2e @horizontal
  Scenario: Complete build-to-install flow as one continuous journey
    Given the project has a valid pyproject.toml with version "0.1.0"
    And the build toolchain is installed
    And the src/ directory exists with valid Python package code
    And git working directory has uncommitted changes
    And no previous version of crafter-ai is installed via pipx

    # ── BUILD PHASE ──
    When I run "crafter-ai forge build"

    # Step 1: Build header
    Then the first non-blank output line is "🔨 Building crafter-ai" in bold

    # Step 2: Build pre-flight checks (streaming list, no table)
    And I see "🔍 Pre-flight checks" indented 2 spaces
    And I see "✅ pyproject.toml found"
    And I see "✅ Build toolchain ready"
    And I see "✅ Source directory found"
    And I see "⚠️  Uncommitted changes detected" as a non-blocking warning
    And I see "✅ Version available for release"
    And I see "✅ Pre-flight passed"
    And no Rich Table or Panel borders appear in the output

    # Step 3: Version display (minimal, no box)
    And I see "📐 Version"
    And I see "0.1.0 → 0.2.0 (minor)"

    # Step 4: Build spinner resolves to persistent line
    And a spinner "⏳ Compiling wheel..." appears during compilation
    And the spinner resolves to a persistent line "✅ Wheel built" with duration

    # Step 5: Wheel validation
    And I see "🔍 Validating wheel"
    And I see "✅ PEP 427 format valid"
    And I see "✅ Metadata complete"
    And I see "✅ Wheel validated"

    # Step 6: Build complete (single line, no panel)
    And I see "🔨 Build complete: crafter_ai-0.2.0-py3-none-any.whl"

    # ── TRANSITION: CONFIRMATION PROMPT ──

    # Step 7: Install prompt (version from wheel METADATA)
    And I see "📦 Install crafter-ai 0.2.0? [Y/n]: "
    And the version "0.2.0" in the prompt matches the wheel METADATA

    When the user confirms with "y"

    # ── INSTALL PHASE ──

    # Step 8: Install header (seamless continuation)
    Then I see "📦 Installing crafter-ai" in bold

    # Step 9: Install pre-flight checks
    And I see "🔍 Pre-flight checks"
    And I see "✅ Wheel file found"
    And I see "✅ Wheel format valid"
    And I see "✅ pipx environment ready"
    And I see "✅ Install path writable"
    And I see "✅ Pre-flight passed"

    # Step 10: Backup (fresh install, single line)
    And I see "💾 Fresh install, no backup needed"
    And no backup spinner or detail line appears

    # Step 11: Installation progress (spinner fills the silence gap)
    And I see "⚙️ Installing" as a section header indented 2 spaces
    And a spinner "⏳ Installing via pipx..." appears during installation
    And the spinner resolves to "✅ nWave installed via pipx" with duration

    # Step 12: SBOM manifest (transparency)
    And I see "📋 What was installed" indented 2 spaces
    And I see "crafter-ai 0.2.0" in dim at 4-space indent
    And I see "CLI: crafter-ai, nw" in dim at 4-space indent
    And I see "→" followed by the pipx install path in dim at 4-space indent
    And no component counts appear (fresh install, nw setup not yet run)

    # Step 13: Health verification
    And I see "🩺 Verifying installation"
    And I see "✅ CLI responds to --version"
    And I see "✅ Core modules loadable"
    And I see "✅ Health: HEALTHY"

    # ── CELEBRATION ──

    # Step 14: The wow moment
    And I see "🎉 nWave 0.2.0 installed and healthy!" in bold green
    And I see "Ready to use in Claude Code." in dim

    # ── SHARED ARTIFACT CONSISTENCY ──
    And the version "0.2.0" appears consistently in:
      | Location              | Expected                                        |
      | Version display       | 0.1.0 → 0.2.0 (minor)                           |
      | Wheel filename        | crafter_ai-0.2.0-py3-none-any.whl                |
      | Install prompt        | Install crafter-ai 0.2.0?                        |
      | SBOM manifest         | crafter-ai 0.2.0                                 |
      | Celebration           | nWave 0.2.0 installed and healthy!                |
    And all version displays originate from wheel METADATA as single source of truth

    # ── EMOTIONAL ARC VALIDATION ──
    And the output reads as a continuous top-to-bottom stream with no visual breaks
    And the emotional arc progresses: anticipation → confidence → tension → trust → joy
    And the process exits with code 0

  # ─── WALKING SKELETON: UPGRADE FLOW ──────────────────────────────

  @walking-skeleton @e2e @horizontal @upgrade
  Scenario: Upgrade install flow with backup and SBOM component counts
    Given the project has a valid pyproject.toml with version "0.1.0"
    And crafter-ai 0.1.0 is already installed via pipx
    And agents, commands, and templates exist in ~/.claude/
    And a wheel for version 0.2.0 exists in dist/

    When I run "crafter-ai forge install"

    # Step 8: Install header
    Then I see "📦 Installing crafter-ai" in bold

    # Step 9: Install pre-flight checks
    And I see "🔍 Pre-flight checks"
    And I see "✅ Pre-flight passed"

    # Step 10: Backup (upgrade path, full section)
    And I see "💾 Backing up configuration" as a section header
    And a spinner "⏳ Creating backup..." appears during backup
    And the spinner resolves to "✅ Backup saved" with duration
    And a dim detail line shows "agents, commands, templates → ~/.claude/backups/nwave-" with timestamp

    # Step 11: Installation progress
    And I see "⚙️ Installing" as a section header
    And a spinner "⏳ Installing via pipx..." fills the silence gap
    And the spinner resolves to "✅ nWave installed via pipx" with duration

    # Step 12: SBOM manifest (upgrade variant with component counts)
    And I see "📋 What was installed"
    And I see "crafter-ai 0.2.0" in dim
    And I see "CLI: crafter-ai, nw" in dim
    And I see agent, command, and template counts in dim
    And I see "→" followed by the pipx install path in dim

    # Step 13: Health verification
    And I see "🩺 Verifying installation"
    And I see "✅ Health: HEALTHY"

    # Step 14: Celebration
    And I see "🎉 nWave 0.2.0 installed and healthy!" in bold green
    And the process exits with code 0

  # ─── SBOM INTEGRATION CONSISTENCY ──────────────────────────────────

  @horizontal @integration @sbom
  Scenario: SBOM install path matches actual pipx venv location
    When the full install flow completes
    Then the path shown in SBOM manifest matches pipx list_packages() path for crafter-ai
    And the path is a real directory on disk

  @horizontal @integration @sbom
  Scenario: SBOM entry points match wheel METADATA
    When the full install flow completes
    Then the CLI entry points shown in SBOM match the wheel METADATA console_scripts
    And the listed commands are executable from PATH
