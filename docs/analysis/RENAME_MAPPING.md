# Documentation Filename Rename Mapping

**Date**: 2026-01-21
**Implementation Status**: Ready to Execute
**Total Files to Rename**: 8
**Cross-Reference Files**: 7

---

## Quick Reference: Old → New

| Old Filename | New Filename | Directory | Reason |
|---|---|---|---|
| INSTALL.md | installation-guide.md | docs/installation/ | Kebab-case + clarify type (tutorial) |
| UNINSTALL.md | uninstall-guide.md | docs/installation/ | Kebab-case + clarify type |
| TROUBLESHOOTING.md | troubleshooting-guide.md | docs/troubleshooting/ | Kebab-case + clarify type |
| how-to-invoke-reviewers.md | invoke-reviewer-agents.md | docs/guides/ | Remove redundant "how-to", be more specific |
| LAYER_4_IMPLEMENTATION_SUMMARY.md | layer-4-implementation-summary.md | docs/guides/ | Kebab-case (was underscore) |
| QUICK_REFERENCE_VALIDATION.md | validation-checklist.md | docs/guides/ | Kebab-case + clarify actual purpose |
| CI-CD-README.md | ci-cd-integration-guide.md | docs/guides/ | Remove confusing "README" suffix |

---

## Detailed Rename Rationale

### 1. Installation Guide

**Old**: `docs/installation/INSTALL.md`
**New**: `docs/installation/installation-guide.md`

**Why**:
- UPPERCASE breaks kebab-case convention (should be all lowercase + hyphens)
- Generic "INSTALL" obscures that this is a tutorial for new users
- "installation-guide" clearly signals: step-by-step setup guide
- Parallel with "uninstall-guide" creates consistent pair
- More discoverable in ls/grep searches (lowercase)

**DIVIO Type**: Tutorial
**Audience**: New users installing nWave
**Content Focus**: Step-by-step instructions, prerequisites, troubleshooting

---

### 2. Uninstall Guide

**Old**: `docs/installation/UNINSTALL.md`
**New**: `docs/installation/uninstall-guide.md`

**Why**:
- UPPERCASE breaks kebab-case convention
- Parallel structure with installation-guide.md
- "guide" suffix signals: how-to document with steps
- More discoverable (lowercase searches)

**DIVIO Type**: How-to Guide
**Audience**: Users removing nWave
**Content Focus**: Uninstall steps, cleanup procedures

---

### 3. Troubleshooting Guide

**Old**: `docs/troubleshooting/TROUBLESHOOTING.md`
**New**: `docs/troubleshooting/troubleshooting-guide.md`

**Why**:
- UPPERCASE breaks kebab-case convention
- "guide" suffix clarifies this is a how-to problem-solving document
- More consistent with other guide filenames
- Easier to find (lowercase)

**DIVIO Type**: How-to Guide
**Audience**: Users experiencing issues
**Content Focus**: Diagnostic procedures, error solutions, FAQs

---

### 4. Invoke Reviewer Agents

**Old**: `docs/guides/how-to-invoke-reviewers.md`
**New**: `docs/guides/invoke-reviewer-agents.md`

**Why**:
- "how-to-" prefix is redundant (everything in guides/ is a how-to)
- "invoke-reviewer-agents" is more specific about what you're invoking (agents, not just reviewers)
- Shorter (4 words → 3 words) but more precise
- Better mirrors the content: "invoke", "Task tool", "examples"
- Avoids confusion with "request-peer-review" (different process)

**DIVIO Type**: How-to Guide
**Audience**: Developers invoking Layer 4 reviews via Task tool
**Content Focus**: Methods 1-3 for invocation, revision workflow, examples

**Cross-References to Update**:
- README.md line 76: "How to Invoke Reviewer Agents"
- docs/reference/reviewer-agents-reference.md: links to this guide
- docs/reference/nwave-commands-reference.md: links to this guide

---

### 5. Layer 4 Implementation Summary

**Old**: `docs/guides/LAYER_4_IMPLEMENTATION_SUMMARY.md`
**New**: `docs/guides/layer-4-implementation-summary.md`

**Why**:
- UPPERCASE with underscores breaks kebab-case convention
- Should use hyphens, not underscores
- Maintains full descriptive name (important for clarity)
- Lowercase makes it searchable and consistent

**DIVIO Type**: Explanation
**Audience**: Users wanting to understand Layer 4 architecture
**Content Focus**: How peer review reduces bias, implementation decisions

**Cross-References to Update**:
- README.md: Link in "Understanding Concepts" section
- docs/guides/layer-4-for-developers.md
- docs/guides/layer-4-for-users.md
- docs/guides/layer-4-for-cicd.md

---

### 6. Validation Checklist

**Old**: `docs/guides/QUICK_REFERENCE_VALIDATION.md`
**New**: `docs/guides/validation-checklist.md`

**Why**:
- UPPERCASE with underscores breaks convention
- "validation-checklist" more accurately describes content (checklist items)
- "quick-reference" is vague and less helpful than specific "checklist"
- Lowercase + kebab-case for consistency
- "checklist" accurately reflects DIVIO classification (reference/verification)

**DIVIO Type**: Reference
**Audience**: Users verifying completeness of work
**Content Focus**: Checklist items, verification steps

---

### 7. CI/CD Integration Guide

**Old**: `docs/guides/CI-CD-README.md`
**New**: `docs/guides/ci-cd-integration-guide.md`

**Why**:
- "README" suffix is confusing (README is for directories, not files in docs/)
- "CI-CD" should be lowercase with hyphens (not mixed case)
- "integration-guide" clearly signals: how to integrate with CI/CD
- More discoverable and follows all naming conventions
- Removes redundancy (we know it's documentation in docs/)

**DIVIO Type**: How-to Guide
**Audience**: DevOps/Platform engineers
**Content Focus**: GitHub Actions, GitLab CI, Jenkins integration steps

**Cross-References to Update**:
- README.md: Installation or Integration section (if referenced)
- .dependency-map.yaml: If this file is tracked

---

## Files NOT Being Renamed

These maintain good naming and require no changes:

| Filename | Directory | Status | Reason |
|---|---|---|---|
| layer-4-for-developers.md | docs/guides/ | ✓ KEEP | Audience-specific, clear purpose |
| layer-4-for-users.md | docs/guides/ | ✓ KEEP | Audience-specific, clear purpose |
| layer-4-for-cicd.md | docs/guides/ | ✓ KEEP | Audience-specific, clear purpose |
| ide-bundling-algorithm.md | docs/guides/ | ✓ KEEP | Descriptive, technical |
| knowledge-architecture-analysis.md | docs/guides/ | ✓ KEEP | Descriptive, clear |
| knowledge-architecture-integration-summary.md | docs/guides/ | ✓ KEEP | Descriptive, clear |
| jobs-to-be-done-guide.md | docs/guides/ | ✓ KEEP | Methodology name (acceptable) |
| layer-4-api-reference.md | docs/reference/ | ✓ KEEP | Standard reference format |
| reviewer-agents-reference.md | docs/reference/ | ✓ KEEP | Clear lookup document |
| nwave-commands-reference.md | docs/reference/ | ✓ KEEP | Standard reference format |

---

## Cross-Reference Update Plan

### File 1: README.md

**Current references**:

Line 34:
```markdown
Full installation details: [Installation Guide](docs/installation/INSTALL.md)
```
**Change to**:
```markdown
Full installation details: [Installation Guide](docs/installation/installation-guide.md)
```

Line 71:
```markdown
- **[How to Invoke Reviewer Agents](docs/guides/how-to-invoke-reviewers.md)** - Request peer reviews for quality assurance
```
**Change to**:
```markdown
- **[Invoke Reviewer Agents](docs/guides/invoke-reviewer-agents.md)** - Request peer reviews for quality assurance
```

Line 90:
```markdown
- **[Layer 4 Implementation Summary](docs/guides/LAYER_4_IMPLEMENTATION_SUMMARY.md)** - How peer review by equal-expertise agents reduces bias
```
**Change to**:
```markdown
- **[Layer 4 Implementation Summary](docs/guides/layer-4-implementation-summary.md)** - How peer review by equal-expertise agents reduces bias
```

Line 86:
```markdown
- **[Troubleshooting Guide](docs/troubleshooting/TROUBLESHOOTING.md)** - Common issues and solutions
```
**Change to**:
```markdown
- **[Troubleshooting Guide](docs/troubleshooting/troubleshooting-guide.md)** - Common issues and solutions
```

**Version bump**:
Change from `<!-- version: 1.4.0 -->` to `<!-- version: 1.4.0 -->`

---

### File 2: docs/reference/reviewer-agents-reference.md

**Line 10**:
```markdown
- [How to invoke reviewers](../guides/how-to-invoke-reviewers.md) (how-to)
```
**Change to**:
```markdown
- [Invoke reviewer agents](../guides/invoke-reviewer-agents.md) (how-to)
```

---

### File 3: docs/reference/nwave-commands-reference.md

**Line 11**:
```markdown
- [How to Invoke Reviewers](../guides/how-to-invoke-reviewers.md) (how-to)
```
**Change to**:
```markdown
- [Invoke Reviewer Agents](../guides/invoke-reviewer-agents.md) (how-to)
```

---

### File 4: docs/guides/layer-4-for-developers.md

**Line 10**:
```markdown
- [For Users](layer-4-for-users.md) (how-to)
- [For CI/CD](layer-4-for-cicd.md) (how-to)
```
No changes needed (these files are being renamed to keep their names consistent).

---

### File 5: docs/guides/layer-4-for-users.md

**Line 12**:
```markdown
- [API Reference](../reference/layer-4-api-reference.md) (contracts)
- [For Developers](layer-4-for-developers.md) (code)
- [For CI/CD](layer-4-for-cicd.md) (pipelines)
```
No changes needed.

---

### File 6: docs/guides/layer-4-for-cicd.md

**Line 11-13**:
```markdown
- [API Reference](../reference/layer-4-api-reference.md) (contracts)
- [For Developers](layer-4-for-developers.md) (code)
- [For Users](layer-4-for-users.md) (CLI)
```
No changes needed.

---

### File 7: .dependency-map.yaml

**Check if any renames are tracked**:
Current file doesn't explicitly track individual guide filenames, so no changes needed.

---

## Implementation Order

1. **Backup** - Git commit current state (if not already)
2. **Rename files** - Execute 8 file renames
3. **Update README.md** - Update 4 link references + version bump
4. **Update reference files** - Update 2 files
5. **Verify links** - Check all markdown links resolve
6. **Commit** - Single commit with message

---

## Verification Checklist

After implementation, verify:

- [ ] All 8 files renamed successfully
- [ ] No duplicate filenames created
- [ ] README.md links updated (4 changes)
- [ ] Reference file links updated (2 changes)
- [ ] Version bumped to 1.3.1
- [ ] Git status shows 8 renames + 3 modified files
- [ ] No broken links in documentation
- [ ] Installation guide still references correctly
- [ ] All guides cross-reference properly

---

## Quick Test: Link Verification

After renames, run:
```bash
# Check for broken references
grep -r "INSTALL.md\|UNINSTALL.md\|TROUBLESHOOTING.md\|how-to-invoke-reviewers.md\|LAYER_4_IMPLEMENTATION\|QUICK_REFERENCE\|CI-CD-README" docs/ README.md --include="*.md"

# Should return only in this mapping document, not in active docs
```

---

**Created**: 2026-01-21
**Author**: documentarist (Quill)
**Status**: READY FOR IMPLEMENTATION
