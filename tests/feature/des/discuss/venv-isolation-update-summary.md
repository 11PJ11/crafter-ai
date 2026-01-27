# Virtual Environment Isolation Update Summary

**Date:** 2026-01-23
**Updated By:** Riley (product-owner)
**Document:** installation-user-stories.md
**Version:** 1.0 → 1.1

---

## Business Value: Why Virtual Environment Isolation Matters

### User Pain Points Addressed

1. **Dependency Conflicts Prevention**
   - **Problem**: nWave might require specific library versions that conflict with user's global Python environment
   - **Solution**: Virtual environment isolates nWave dependencies completely

2. **Upgrade Safety**
   - **Problem**: Upgrading system Python breaks nWave installation
   - **Solution**: Virtual environment maintains its own Python interpreter reference

3. **Clean Uninstallation**
   - **Problem**: Uninstalling nWave leaves behind Python packages in global environment
   - **Solution**: Removing venv directory removes ALL nWave packages cleanly

4. **Multi-Project Isolation**
   - **Problem**: Different projects might need different nWave versions
   - **Solution**: Each nWave installation has isolated package versions

### Best Practice Compliance

Virtual environment usage is Python packaging best practice (PEP 405) and prevents pollution of user's global Python environment.

---

## Changes Summary

### Acceptance Criteria Added: 15 New Criteria

**US-INSTALL-001: One-Command Installation**
- AC-001.12: Virtual environment creation at ~/.claude/nwave/venv/
- AC-001.13: Installation output shows venv creation with isolation benefit explanation
- AC-001.14: nWave CLI automatic venv usage (no manual activation)
- AC-001.15: Global Python environment verification (no nWave packages)
- AC-001.16: Platform-specific recovery guidance for venv creation failures

**US-INSTALL-002: Clean Uninstallation**
- AC-002.11: Complete virtual environment removal
- AC-002.12: Post-uninstallation verification of clean global environment
- AC-002.13: Explicit confirmation that global Python unchanged

**US-INSTALL-003: Installation Verification & Health Check**
- AC-003.11: Virtual environment health validation (existence, Python version, isolation)
- AC-003.12: Explicit verification that no nWave packages in global environment
- AC-003.13: Virtual environment diagnostics (location, version, packages)

**US-INSTALL-004: Installation Upgrade & Migration**
- AC-004.12: Virtual environment preservation during upgrade (not recreated)
- AC-004.13: Only nWave packages upgraded in venv (Python interpreter unchanged)
- AC-004.14: Virtual environment corruption detection with automatic recreation
- AC-004.15: Rollback restores venv to pre-upgrade state

**Total Acceptance Criteria**: 42 → 57 (+15 new criteria)

---

## Domain Examples Updated

### US-INSTALL-001: Fresh Installation Example

**Added to output:**
```
Creating virtual environment...
✓ Virtual environment created at: /Users/marcus/.claude/nwave/venv/
✓ Virtual environment using Python 3.11.5
ℹ Benefits: Isolated from global Python (no dependency conflicts)

Installing components...
✓ nWave CLI installed to venv: /Users/marcus/.claude/nwave/venv/bin/nwave
✓ DES components installed to venv: /Users/marcus/.claude/nwave/venv/lib/python3.11/site-packages/nwave/

[...]

Virtual Environment Details:
  Location: ~/.claude/nwave/venv/
  Python: 3.11.5
  Packages: nwave==1.0.0 (zero external dependencies)
  Activation: Automatic (no manual activation needed for nwave commands)
  Manual activation: source ~/.claude/nwave/venv/bin/activate
```

**New Failure Scenario Added:**

Example 5: Virtual Environment Creation Failure
- Platform-specific diagnostics (Ubuntu/Debian missing python3-venv)
- macOS recovery (reinstall Python from python.org)
- Windows recovery (reinstall with pip option)
- Clear error message: "Cannot create virtual environment"

### US-INSTALL-002: Uninstallation Example

**Added to output:**
```
Uninstalling components...
✓ Virtual environment removed from: /Users/priya/.claude/nwave/venv/
✓ nWave CLI removed (from venv)
✓ DES components removed (from venv)

Environment verification...
✓ Global Python environment unchanged (no nWave packages found)
✓ No orphaned Python packages remaining

[...]

Your global Python environment is clean (no nWave packages were installed globally).
```

### US-INSTALL-003: Health Check Example

**New Component Added (now 6 components total):**

```
[1/6] Virtual Environment
  ✓ Virtual environment exists: ~/.claude/nwave/venv/
  ✓ Python version in venv: 3.11.5 (matches system Python)
  ✓ venv activation works: source ~/.claude/nwave/venv/bin/activate
  ✓ nWave packages in venv: nwave==1.0.0
  ✓ No nWave packages in global Python environment (isolation verified)
```

**Updated summary:**
```
Virtual Environment Status:
  Location: ~/.claude/nwave/venv/
  Python: 3.11.5
  Packages: nwave==1.0.0 (isolated from global environment)
  Global environment: Clean (no nWave packages)
```

### US-INSTALL-004: Upgrade Example

**Added to upgrade output:**
```
Analyzing migration requirements...
✓ Virtual environment: Preserved (Python 3.11.5 remains unchanged)
  - Strategy: Upgrade packages in existing venv (no venv recreation)

Upgrading components...
✓ Virtual environment preserved (no recreation)
✓ nWave packages upgraded in venv (v0.9.2 → v1.0.0)
✓ DES library upgraded in venv (v1.3 → v1.4)

[...]

Virtual Environment Status:
  Location: ~/.claude/nwave/venv/ (preserved)
  Python: 3.11.5 (unchanged)
  Packages: nwave==1.0.0 (upgraded from 0.9.2)
```

**New Failure Scenario Added:**

Example 5: Virtual Environment Corruption During Upgrade
- Detects corrupted venv (missing Python executable, broken imports)
- Provides 3 recovery options with clear recommendations
- Automatic venv recreation with user data preservation
- Explicit backup creation before any venv manipulation

---

## Failure Scenarios Matrix Updated

**New Row Added:**

| Failure Type | Detection Method | Error Message | Recovery Suggestion |
|--------------|------------------|---------------|---------------------|
| **venv Module Missing** | Import venv module | "Cannot create virtual environment (venv module unavailable)" | Ubuntu/Debian: sudo apt install python3-venv; macOS/Windows: Reinstall Python |

---

## Technical Notes Added to Stories

### US-INSTALL-001 Technical Notes

**Added:**
- Virtual environment isolation: All Python packages installed in ~/.claude/nwave/venv/ (not globally)
- Zero external dependencies: nWave uses only Python stdlib, reducing venv size
- Automatic venv activation: nWave CLI wrapper activates venv transparently

### US-INSTALL-002 Technical Notes

**Added:**
- Virtual environment removal: Complete directory deletion ensures no orphaned packages
- Global environment verification: Post-uninstall check confirms clean state

### US-INSTALL-004 Technical Notes

**Added:**
- Upgrade strategy: Preserve existing venv, upgrade packages only (avoids Python version changes)
- Corruption detection: Health check venv integrity before upgrade
- Recreation fallback: Automatic venv recreation if corruption detected

---

## User-Visible Transparency Improvements

### Installation Phase
1. **Explicit venv creation message**: Users see virtual environment being created
2. **Benefit explanation**: "Benefits: Isolated from global Python (no dependency conflicts)"
3. **Location disclosure**: Full path shown (~/.claude/nwave/venv/)
4. **Activation transparency**: "Automatic (no manual activation needed)"

### Health Check Phase
1. **Isolation verification**: Explicitly confirms no global packages
2. **Detailed diagnostics**: Python version, package list, activation command
3. **Component-level validation**: Virtual environment is first health check component

### Uninstallation Phase
1. **Removal confirmation**: "Virtual environment removed"
2. **Global environment verification**: "Global Python environment unchanged"
3. **Clean state assurance**: "No orphaned Python packages remaining"

### Upgrade Phase
1. **Preservation notice**: "Virtual environment preserved (no recreation)"
2. **Package-only upgrade**: "nWave packages upgraded in venv"
3. **Python version stability**: "Python 3.11.5 (unchanged)"

---

## Implementation Impact

### Developer Implications

**Installation Logic Changes:**
1. Create virtual environment BEFORE installing packages
2. Install all Python packages to venv (not global)
3. Create CLI wrapper that auto-activates venv

**Health Check Logic Changes:**
1. Add virtual environment as first validation component
2. Verify venv existence, Python version, package isolation
3. Confirm global environment has no nWave packages

**Uninstallation Logic Changes:**
1. Remove entire venv directory (recursive delete)
2. Verify no global packages remain
3. Report clean global environment state

**Upgrade Logic Changes:**
1. Preserve existing venv (don't recreate)
2. Upgrade packages in-place within venv
3. Detect venv corruption and recreate if needed
4. Rollback must restore venv state

### Testing Requirements

**New test scenarios required:**
1. Installation creates venv successfully
2. Installation fails gracefully if venv module missing
3. Uninstallation removes venv completely
4. Health check validates venv isolation
5. Upgrade preserves venv and upgrades packages only
6. Upgrade detects and recovers from venv corruption
7. Rollback restores pre-upgrade venv state

---

## Documentation Requirements

**User-facing documentation needs updates:**
1. Installation guide: Explain virtual environment concept and benefits
2. Troubleshooting guide: Add venv-related issues (missing venv module, corruption)
3. FAQ: "Why does nWave use a virtual environment?"
4. Architecture docs: Document venv structure and CLI wrapper mechanism

---

## Backward Compatibility Considerations

**Existing installations (pre-venv):**
- Upgrade path needed: Detect global installation → migrate to venv
- Migration strategy: Create venv, reinstall packages, update CLI wrapper
- Rollback: Support restoring global installation if migration fails

**Future consideration:**
- Add migration story (US-INSTALL-005) for users upgrading from pre-venv versions
- Define clear migration path with data preservation

---

## Quality Gates

**All 4 user stories now enforce:**
1. ✅ Virtual environment isolation (no global Python pollution)
2. ✅ Explicit user communication about venv benefits
3. ✅ Platform-specific recovery guidance for venv failures
4. ✅ Health check validation of venv integrity
5. ✅ Complete removal during uninstallation
6. ✅ Preservation during upgrade (package-level upgrades only)

---

## Success Metrics (Updated)

**Installation success metrics:**
- Virtual environment creation success rate: > 98%
- Global environment pollution rate: 0% (all packages in venv)
- venv-related installation failures: < 2% (mostly missing venv module)

**User experience metrics:**
- Time to understand venv isolation: < 30 seconds (clear output messages)
- Manual venv activation attempts: 0% (automatic activation works)
- Global environment conflict reports: 0% (isolation prevents conflicts)

---

## Next Steps

**For DESIGN wave:**
1. Design venv creation mechanism (Python stdlib venv module)
2. Design CLI wrapper for automatic venv activation
3. Design health check venv validation logic
4. Design upgrade venv preservation strategy
5. Design migration path for pre-venv installations

**For DISTILL wave:**
1. Create UAT scenarios for venv creation
2. Create UAT scenarios for venv isolation verification
3. Create UAT scenarios for venv corruption recovery
4. Create UAT scenarios for platform-specific failures

**For DEVELOP wave:**
1. Implement venv creation during installation
2. Implement CLI wrapper with auto-activation
3. Implement health check venv validation
4. Implement upgrade venv preservation
5. Implement platform-specific error handling

---

*Update completed by Riley (product-owner) on 2026-01-23 in response to requirement: "tutte le installazioni dovrebbero creare un ambiente virtuale per evitare di inquinare l'ambiente python globale dell'utente"*
