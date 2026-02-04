# Journey: Forge Build + Install TUI Redesign

## Visual Design System

### 1. Color Semantics (Minimal Palette)

| Color   | Semantic          | Rich Markup           | Usage                              |
|---------|-------------------|-----------------------|------------------------------------|
| Green   | Success/Pass      | `[green]`             | Passed checks, success messages    |
| Red     | Error/Fail/Block  | `[red]`               | Failed checks, blocking errors     |
| Yellow  | Warning           | `[yellow]`            | Non-blocking warnings              |
| Dim     | Secondary info    | `[dim]`               | Paths, sizes, durations, details   |
| Bold    | Primary content   | `[bold]`              | Version numbers, package names     |
| Default | Body text         | (no markup)           | Normal flowing text                |

**Rule**: Colors ONLY for pass/warn/fail semantics. Never decorative. Let emoji do the emotional work.

### 2. Emoji Vocabulary (Structured with Spark)

| Emoji | Meaning                | Context                         |
|-------|------------------------|---------------------------------|
| `🔨`  | Building               | Build phase header              |
| `📦`  | Packaging/Installing   | Install phase header            |
| `✅`  | Step passed/completed  | Completed check or phase        |
| `⚠️`   | Warning (non-blocking) | Warning checks (git dirty, etc) |
| `❌`  | Failed/Blocked         | Blocking failure                |
| `🔍`  | Checking/Verifying     | Pre-flight, verification        |
| `💾`  | Backup                 | Backup phase                    |
| `⚙️`  | Active operation       | Install-in-progress section     |
| `📋`  | Manifest/inventory     | SBOM "what was installed"       |
| `🩺`  | Health check           | Post-install verification       |
| `🎉`  | Celebration            | Final success moment ONLY       |
| `→`   | Version transition     | Version bump, install path      |

**Rule**: One emoji per line, always at the start. No emoji soup. Each emoji has exactly one meaning.

### 3. Typography Rules

| Element          | Style           | Example                                    |
|------------------|-----------------|--------------------------------------------|
| Phase header     | Bold + emoji    | `🔨 Building crafter-ai`                   |
| Check result     | Emoji + text    | `  ✅ pyproject.toml found`                |
| Summary label    | Bold            | `Version: 0.2.0`                           |
| Secondary detail | Dim             | `(104.1 KB, 3.04s)`                        |
| Section spacing  | 1 blank line    | Between phases, never inside               |
| Indent           | 2 spaces        | Check items under phase headers             |

**Rule**: No borders, no boxes, no panels, no tables, no horizontal rules, no `===` lines. Ever.

### 4. Spacing and Rhythm

```
[blank line]
Phase header (bold + emoji)
  Check line 1
  Check line 2
  Check line 3
  Phase summary line
[blank line]
Next phase header
```

- One blank line between phases
- Two-space indent for items within a phase
- No trailing blank lines within a phase
- The output reads like a well-formatted log, top to bottom


---

## Screen-by-Screen Mockups: Happy Path

### Full Build + Install Flow (continuous)

```
🔨 Building crafter-ai

  🔍 Pre-flight checks
  ✅ pyproject.toml found
  ✅ Build toolchain ready
  ✅ Source directory found
  ⚠️  Uncommitted changes detected
  ✅ Version available for release
  ✅ Pre-flight passed

  📐 Version
  0.1.0 → 0.2.0 (minor)

  ⏳ Compiling wheel...                    ← spinner (animated, replaces itself)
  ✅ Wheel built (1.2s)                    ← spinner resolves to this line

  🔍 Validating wheel
  ✅ PEP 427 format valid
  ✅ Metadata complete
  ✅ Wheel validated

  🔨 Build complete: crafter_ai-0.2.0-py3-none-any.whl

📦 Install crafter-ai 0.2.0? [Y/n]: y

📦 Installing crafter-ai

  🔍 Pre-flight checks
  ✅ Wheel file found
  ✅ Wheel format valid
  ✅ pipx environment ready
  ✅ Install path writable
  ✅ Pre-flight passed

  💾 Backing up configuration
  ⏳ Creating backup...                    ← spinner
  ✅ Backup saved (0.3s)                   ← spinner resolves
    agents, commands, templates → ~/.claude/backups/nwave-20260203-143022

  ⚙️ Installing
  ⏳ Installing via pipx...                ← spinner (animated during ~3s pipx install)
  ✅ nWave installed via pipx (2.9s)       ← spinner resolves to closure line

  📋 What was installed
    crafter-ai 0.2.0
    CLI: crafter-ai, nw
    12 agents, 8 commands, 5 templates
    → ~/.local/pipx/venvs/crafter-ai

  🩺 Verifying installation
  ✅ CLI responds to --version
  ✅ Core modules loadable
  ✅ Health: HEALTHY

🎉 nWave 0.2.0 installed and healthy!
   Ready to use in Claude Code.
```

### Key Design Decisions Explained

**Phase headers** (`🔨 Building crafter-ai`, `📦 Installing crafter-ai`)
use bold text and a tool emoji. They establish WHERE you are in the journey.

**Check lines** are indented 2 spaces with a status emoji. Each reads as a
complete sentence fragment: `✅ pyproject.toml found`. No labels, no columns,
no "Check: ... Status: ... Details: ..." structure.

**Spinners** appear as `⏳ Compiling wheel...` and when the operation completes,
the spinner line is REPLACED (Rich `console.status`) with the persistent result
line: `✅ Wheel built (1.2s)`. The key insight: the spinner uses `console.status()`
which replaces itself, but we ALSO print the completed line AFTER stopping the
spinner, so the result persists in stdout.

**The version line** is minimal: `0.1.0 → 0.2.0 (minor)`. No panel, no box.
Just the information.

**The confirmation prompt** appears between build and install as a natural
decision point: `📦 Install crafter-ai 0.2.0? [Y/n]: y`. The `📦` emoji
signals we are transitioning to the install phase. Default is yes (capital Y).
No box, no panel. Just a prompt in the flow. When the user confirms, the
install phase header follows immediately.

**The celebration** is the final two lines. Short, warm, actionable. The `🎉`
emoji appears ONLY here, making it special. "Ready to use in Claude Code" tells
the user their next step.

**The backup section** (upgrade path) has a sub-phase header `💾 Backing up
configuration` followed by a spinner that resolves, then a dim detail line
showing what was backed up and where. This builds trust: the user sees their
data is safe BEFORE the destructive install operation begins.

**The install section** uses `⚙️ Installing` as a sub-phase header, creating
a named container for the operation. The spinner runs during the ~3-second
pipx install, eliminating the silence gap. The closure line `✅ nWave installed
via pipx (2.9s)` confirms completion with timing. Note: "nWave" is the
product brand name; "crafter-ai" is the Python package name.

**The SBOM manifest** (`📋 What was installed`) appears immediately after the
install closure. It answers the user's implicit question: "what just happened
to my system?" Without this, a silent install that modifies system paths looks
suspicious. The manifest shows: package identity, CLI entry points registered,
component counts (agents, commands, templates), and install location. All items
are dim text at 4-space indent (sub-items under the section header). No emojis
on manifest lines; they are informational, not status indicators.


### Fresh Install Variant

When no previous version exists, the backup section is a single informational
line (no spinner needed, nothing to back up):

```
📦 Installing crafter-ai

  🔍 Pre-flight checks
  ✅ Wheel file found
  ✅ Wheel format valid
  ✅ pipx environment ready
  ✅ Install path writable
  ✅ Pre-flight passed

  💾 Fresh install, no backup needed

  ⚙️ Installing
  ⏳ Installing via pipx...                ← spinner (animated during ~3s pipx install)
  ✅ nWave installed via pipx (2.9s)       ← spinner resolves to closure line

  📋 What was installed
    crafter-ai 0.2.0
    CLI: crafter-ai, nw
    → ~/.local/pipx/venvs/crafter-ai

  🩺 Verifying installation
  ✅ CLI responds to --version
  ✅ Core modules loadable
  ✅ Health: HEALTHY

🎉 nWave 0.2.0 installed and healthy!
   Ready to use in Claude Code.
```

Note: For fresh installs, the manifest omits agent/command/template counts
because those are deployed by `nw setup`, not by `pipx install`. Only the
package identity, CLI entry points, and install path are shown. The upgrade
variant includes component counts because the user is replacing an existing
set of components and wants to verify the new set matches expectations.


---

## Error State Mockups

### Blocking Pre-flight Failure (Build)

```
🔨 Building crafter-ai

  🔍 Pre-flight checks
  ❌ pyproject.toml not found
  ✅ Build toolchain ready
  ❌ Source directory not found
  ⚠️  Uncommitted changes detected
  ✅ Version available for release

  Build blocked: 2 checks failed

  ❌ pyproject.toml not found
     Fix: Create pyproject.toml in project root
     See: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/

  ❌ Source directory not found
     Fix: Create a src/ directory with your package structure
```

**Design decisions for errors**:
- All checks still run and display (user sees the full picture)
- A summary line counts failures: `Build blocked: 2 checks failed`
- Then ONLY the failures are repeated with remediation details
- Remediation is indented under the failure with `Fix:` label
- URLs are on a separate `See:` line (keeps lines scannable)
- No red boxes. No panels. Just clear, actionable text.

### Blocking Pre-flight Failure (Install)

```
📦 Installing crafter-ai

  🔍 Pre-flight checks
  ❌ No wheel file found in dist/
  ❌ pipx is not installed
  ✅ Install path writable

  Install blocked: 2 checks failed

  ❌ No wheel file found in dist/
     Fix: Run 'crafter-ai forge build' first

  ❌ pipx is not installed
     Fix: pip install pipx && pipx ensurepath
```

### Build Failure (compilation error)

```
🔨 Building crafter-ai

  🔍 Pre-flight checks
  ✅ pyproject.toml found
  ✅ Build toolchain ready
  ✅ Source directory found
  ✅ Git status clean
  ✅ Version available for release
  ✅ Pre-flight passed

  📐 Version
  0.1.0 → 0.2.0 (minor)

  ⏳ Compiling wheel...
  ❌ Build failed

  Error: Invalid package metadata in pyproject.toml
  Fix: Check [project] section in pyproject.toml
```

### Install Failure (pipx error)

```
📦 Installing crafter-ai

  🔍 Pre-flight checks
  ✅ Wheel file found
  ✅ Wheel format valid
  ✅ pipx environment ready
  ✅ Install path writable
  ✅ Pre-flight passed

  💾 Backing up configuration
  ⏳ Creating backup...
  ✅ Backup saved (0.3s)
    agents, commands, templates → ~/.claude/backups/nwave-20260203-143022

  ⚙️ Installing
  ⏳ Installing via pipx...
  ❌ Installation failed

  Error: pipx install failed: dependency conflict
  Fix: Try 'pipx install --force' or check dependency versions
```

### Degraded Health (post-install warning)

```
📦 Installing crafter-ai

  ...checks and install as normal...

  🩺 Verifying installation
  ✅ CLI responds to --version
  ⚠️  Some optional modules not found
  ✅ Health: DEGRADED

⚠️  crafter-ai 0.2.0 installed with warnings
   Some features may be limited. Run 'crafter-ai doctor' for details.
```

Note: When health is DEGRADED, the celebration downgrades from `🎉` to `⚠️`
and the message is honest but not alarming. The tool is usable.


---

## Interaction Patterns

### Pattern 1: Spinner to Persistent Line

```python
# BEFORE (current - line disappears)
with console.status("Installing..."):
    result = do_install()
# Nothing persists in stdout

# AFTER (new design - line persists)
status = console.status("⏳ Installing via pipx...")
status.start()
result = do_install()
status.stop()
console.print("📦 Installed via pipx (3.04s)")  # This line PERSISTS
```

The key: after `status.stop()`, print the completed result as a normal line.
The spinner vanishes, but the result line stays forever in the scrollback.

### Pattern 2: Check List Display

```python
# Print each check as it completes (streaming feel)
for check in results:
    if check.passed:
        if check.severity == CheckSeverity.WARNING:
            # Passed warning-level checks still show as success
            console.print(f"  ✅ {check.message}")
        else:
            console.print(f"  ✅ {check.message}")
    elif check.severity == CheckSeverity.WARNING:
        console.print(f"  ⚠️  {check.message}")
    else:
        console.print(f"  ❌ {check.message}")
```

### Pattern 3: Phase Header

```python
console.print()  # blank line before phase
console.print(f"[bold]🔨 Building crafter-ai[/bold]")
```

No panel. No box. Bold text with emoji. That's it.

### Pattern 4: Confirmation Prompt

```
📦 Install crafter-ai 0.2.0? [Y/n]:
```

One line. Emoji matches the phase. Default is yes (capital Y).
No box around it. Flows naturally in the stream.

### Pattern 5: Celebration Moment

```python
console.print()
if health_status == "HEALTHY":
    console.print(f"[bold green]🎉 nWave {version} installed and healthy![/bold green]")
    console.print("[dim]   Ready to use in Claude Code.[/dim]")
elif health_status == "DEGRADED":
    console.print(f"[bold yellow]⚠️  nWave {version} installed with warnings[/bold yellow]")
    console.print("[dim]   Some features may be limited. Run 'crafter-ai doctor' for details.[/dim]")
```

The celebration is the ONLY place where the full line is colored (green for
healthy, yellow for degraded). Everywhere else, only the emoji carries emotion.
Note: Uses "nWave" (product brand) not "crafter-ai" (package name).

### Pattern 6: Error Detail Block

```python
# After the check list, if there are blocking failures:
console.print()
console.print(f"[red]  Build blocked: {count} checks failed[/red]")
console.print()
for failure in blocking_failures:
    console.print(f"  [red]❌ {failure.message}[/red]")
    if failure.remediation:
        console.print(f"[dim]     Fix: {failure.remediation}[/dim]")
```

Errors are shown in red. Remediation is dim (secondary information).
Indentation creates visual hierarchy without borders.

### Pattern 7: Sub-phase with Spinner and Detail

Used for operations that have a section header, a spinner during work,
a closure line, and optional detail lines afterward.

```python
# Backup section (upgrade path)
console.print()
console.print("  💾 Backing up configuration")
status = console.status("  ⏳ Creating backup...")
status.start()
backup_result = do_backup()
status.stop()
console.print(f"  ✅ Backup saved ({duration})")
console.print(f"[dim]    {backed_up_items} → {backup_result.backup_path}[/dim]")

# Install section
console.print()
console.print("  ⚙️ Installing")
status = console.status("  ⏳ Installing via pipx...")
status.start()
install_result = do_install()
status.stop()
console.print(f"  ✅ nWave installed via pipx ({duration})")
```

The section header (💾 or ⚙️) names the operation. The spinner provides
active feedback. The closure line (✅) confirms completion. Detail lines
(dim, 4-space indent) provide supporting information.

### Pattern 8: SBOM Manifest Display

Shows what was installed, using dim text at 4-space indent. No emojis on
individual manifest lines; they are informational, not status indicators.

```python
# After install closure line
console.print()
console.print("  📋 What was installed")
console.print(f"[dim]    {package_name} {version}[/dim]")
console.print(f"[dim]    CLI: {', '.join(entry_points)}[/dim]")
if component_counts:  # only for upgrades
    console.print(f"[dim]    {agents} agents, {commands} commands, {templates} templates[/dim]")
console.print(f"[dim]    → {install_path}[/dim]")
```

The manifest answers "what just happened to my system?" and builds trust.
The `→` prefix on the install path mirrors the version transition arrow,
here meaning "installed to this location".


---

## Anti-Patterns: What to NEVER Do

### 1. NO Tables for Sequential Data

```
WRONG:
┏━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Check         ┃ Status ┃ Details                  ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ pyproject.toml│   ✓    │ Found                    │
└───────────────┴────────┴─────────────────────────┘

RIGHT:
  ✅ pyproject.toml found
```

Tables add friction. Every border character is noise. The CLI is sequential;
the output should be sequential.

### 2. NO Panels or Boxes for Simple Messages

```
WRONG:
╭───────────── Build Summary ─────────────╮
│ FORGE: BUILD COMPLETE                    │
│ Wheel: crafter_ai-0.2.0-py3-none-any.whl│
│ Version: 0.2.0                           │
╰──────────────────────────────────────────╯

RIGHT:
🔨 Build complete: crafter_ai-0.2.0-py3-none-any.whl
```

One line. Contains everything you need. No visual overhead.

### 3. NO Vanishing Spinners

```
WRONG:
with console.status("Installing..."):
    do_install()
# Spinner vanishes. No trace it ever ran. User wonders "did it work?"

RIGHT:
spinner.start()
do_install()
spinner.stop()
console.print("📦 Installed via pipx (3.04s)")
# Result persists in terminal scrollback forever
```

### 4. NO Mixed Visual Languages

```
WRONG:
╭─── Version Analysis ───╮   ← Rich Panel
┏━━━━━━━━━┳━━━━━━━━━━━━━┓  ← Rich Table
============ COMPLETE ====  ← ASCII block
---                         ← Markdown rule

RIGHT:
Every section uses the same pattern:
  Emoji + text for items
  Bold for headers
  Dim for details
```

### 5. NO Redundant Labels

```
WRONG:
  Check: Pyproject.toml Exists   Status: ✓   Details: pyproject.toml found

RIGHT:
  ✅ pyproject.toml found
```

The emoji IS the status. The text IS the detail. The check name is
implied by the message. Three columns compressed to one clear line.

### 6. NO "FORGE:" Prefix Shouting

```
WRONG:
FORGE: BUILD COMPLETE
FORGE: INSTALL COMPLETE

RIGHT:
🔨 Build complete: crafter_ai-0.2.0-py3-none-any.whl
🎉 crafter-ai 0.2.0 installed and healthy!
```

The tool name is in the command the user typed. No need to shout it back.

### 7. NO Information Dump in Celebration

```
WRONG:
  Version:       0.2.0
  Install Path:  /Users/mike/.local/bin
  Wheel:         crafter_ai-0.2.0-py3-none-any.whl
  Wheel Size:    104.1 KB (106622 bytes)
  Duration:      3.04s
  Phases:        5 completed
  Health Status: HEALTHY

RIGHT:
🎉 crafter-ai 0.2.0 installed and healthy!
   Ready to use in Claude Code.
```

The celebration is a FEELING, not a report. Version + health is the signal.
Everything else is noise at this moment. The user wants the "wow", not a receipt.


---

## Emotional Arc

```
Phase                   Emotion              Visual Signal
─────────────────────────────────────────────────────────────
Start                   Anticipation         🔨 bold header
Pre-flight checks       Building confidence  ✅ ✅ ✅ rapid green
Warning (if any)        Brief attention       ⚠️  acknowledged, moves on
Version display         Clarity              Clean, simple line
Build spinner           Tension/waiting      ⏳ animated dots
Build complete          Relief               ✅ + time confirms speed
Install prompt          Decision moment      📦 user confirms, feels in control
Install header          Momentum continues   📦 seamless transition
Install checks          Confidence again     ✅ ✅ ✅ ✅ more green
Backup (upgrade)        Safety/trust         💾 your data is safe, spinner + detail
Backup (fresh)          Acknowledged         💾 brief line, nothing to worry about
Install section header  Orientation          ⚙️ container for the big operation
Install spinner         Peak tension         ⏳ active feedback during ~3s wait
Install closure         Relief               ✅ nWave installed, with timing
SBOM manifest           Trust/transparency   📋 "here's what happened to your system"
Health verification     Final validation     🩺 professional care
CELEBRATION             Peak joy             🎉 THE moment. Bold green.
```

The user's journey: Anticipation, growing confidence, brief tension during
compilation and installation, then transparent confirmation of what was
installed, and a clear, warm, satisfying resolution.

The critical emotional gap that was fixed: the 3-second silence during pipx
install created anxiety ("is it frozen?"). The spinner provides active feedback.
The SBOM manifest creates trust ("I can see exactly what changed on my system").
Together they transform a suspicious black-box operation into a transparent,
confidence-building experience.


---

## Shared Artifacts

| Artifact         | Source of Truth               | Appears In                                                    |
|------------------|-------------------------------|---------------------------------------------------------------|
| `version`        | Wheel METADATA (canonical)    | Version line, prompt, build complete, SBOM manifest, celebration |
| `package_name`   | `pyproject.toml`              | Phase headers, wheel name, SBOM manifest                      |
| `product_name`   | Hardcoded: "nWave"            | Install closure line, celebration message                     |
| `wheel_name`     | Build output                  | Build complete line                                           |
| `install_path`   | pipx list_packages()          | SBOM manifest (install location)                              |
| `cli_entry_points`| Wheel METADATA entry_points  | SBOM manifest (CLI commands registered)                       |
| `component_counts`| Post-install scan of ~/.claude| SBOM manifest (agents, commands, templates; upgrade only)     |
| `backup_path`    | BackupResult.backup_path      | Backup detail line                                            |
| `health_status`  | HealthChecker                 | Verification line, celebration message tone                   |
| `duration`       | Timer                         | Spinner resolution lines                                      |

**Version data flow** (single canonical path, no ambiguity):
```
pyproject.toml → build process → wheel METADATA → all displays
```
The version displayed in the build summary, the install prompt, the SBOM
manifest, and the celebration MUST all come from the same
`InstallResult.version` value, which is parsed from the wheel's METADATA
file. There is no "or". The wheel metadata is the single source of truth
because that is what the user will actually get when they install the package.

**Product name vs package name**: The celebration and install closure use
"nWave" (the product brand), while the package identity in the SBOM uses
"crafter-ai" (the PyPI package name). This is intentional: "nWave" is what
the user thinks they installed; "crafter-ai" is the technical package name
that pipx and pip use.

**SBOM data sources** (what needs to be gathered post-install):
```
pipx install result → version, success
pipx list --json    → install_path (venv path)
wheel METADATA      → entry_points (CLI commands: crafter-ai, nw)
~/.claude/ scan     → agent_count, command_count, template_count (upgrade only)
```
For fresh installs, component counts are omitted because `nw setup` has not
yet deployed agents/commands/templates. The SBOM shows only what pipx itself
installed.
