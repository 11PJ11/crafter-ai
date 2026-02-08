# DW-DISCOVER: Evidence-Based Product Discovery

**Wave**: DISCOVER
**Agent**: Scout (nw-product-discoverer)
**Command**: `*discover`

## Overview

Execute DISCOVER wave of nWave methodology through evidence-based product discovery, assumption testing, and market validation. Establishes product-market fit foundation through rigorous customer development before requirements gathering using Mom Test interviewing principles and continuous discovery practices.

This is the FIRST wave in nWave (6 waves total: DISCOVER → DISCUSS → DESIGN → DISTILL → DEVELOP → DELIVER).

## Orchestrator Briefing

**CRITICAL ARCHITECTURAL CONSTRAINT**: Sub-agents launched via Task tool have NO ACCESS to the Skill tool. They can ONLY use: Read, Write, Edit, Bash, Glob, Grep.

### What Orchestrator Must Do

When delegating this command to an agent via Task tool:

1. **Read project context files** and embed complete product vision inline
2. **Load product-discoverer.md agent specification** and embed Scout's discovery_methodology section inline (lines 484-540 contain 4-phase workflow, decision gates G1-G4, evidence quality standards)
3. **Create a complete agent prompt** that includes:
   - Full project-brief.md content (inline, not paths)
   - Market context and competitive landscape
   - Scout's 4-phase discovery workflow (embedded from product-discoverer.md)
   - Scout's evidence quality standards (embedded from product-discoverer.md)
   - Scout's decision gate criteria G1-G4 (embedded from product-discoverer.md)
   - All deliverable formats and templates
4. **Do NOT reference any /nw:* commands** in the agent prompt (agent cannot invoke them)
5. **Embed all discovery procedures** - agent executes directly, no command delegation

### What NOT to Include

- ❌ "Agent should invoke /nw:discuss after discovery"
- ❌ "Use /nw:opportunity to map solution tree"
- ❌ Any reference to skills or other commands the agent should call
- ❌ References to next wave invocation (orchestrator handles wave transitions)
- ❌ Path references without full content embedded (agent needs content, not file paths)

### Example: What TO Do

✅ "Validate the problem through customer interviews using Scout's Mom Test principles: [EMBED FROM product-discoverer.md]"
✅ "Create Opportunity Solution Tree based on these validated problems: [SPECIFIC PROBLEMS WITH EVIDENCE]"
✅ "Test solution hypotheses following Scout's framework: [EMBED FROM product-discoverer.md]"
✅ "Build Lean Canvas using these validated assumptions: [EVIDENCE-BACKED ASSUMPTIONS]"
✅ "Provide these discovery outputs: problem-validation.md, opportunity-tree.md, solution-testing.md, lean-canvas.md"

## Context Files Required

- docs/project-brief.md - Initial product vision (if available)
- docs/market-context.md - Market research and competitive landscape (if available)

## Previous Artifacts

None (DISCOVER is the first wave in nWave)

**Note**: If greenfield project detected during discovery, Scout will facilitate Walking Skeleton decision (see discuss.md Walking Skeleton section for identical detection logic and decision workflow).

## Agent Invocation

@nw-product-discoverer

Execute \*discover for {product-concept-name}.

**Context Files:**
- docs/project-brief.md (if available)
- docs/market-context.md (if available)

**Configuration:**
- interactive: high
- output_format: markdown
- interview_depth: comprehensive
- evidence_standard: past_behavior

## Success Criteria

Refer to Scout's quality gates in dist/ide/agents/nw/nw-product-discoverer.md.

**Key Validations:**
- [ ] All 4 decision gates passed (G1: Problem Validation, G2: Opportunity Mapping, G3: Solution Testing, G4: Market Viability)
- [ ] Minimum interview thresholds met per phase (5-7 for validation, 3-5 for mapping/viability)
- [ ] Evidence quality standards met (past behavior documented, not future intent)
- [ ] Mom Test principles applied throughout discovery
- [ ] Handoff accepted by product-owner (DISCUSS wave)
- [ ] Layer 4 peer review approval obtained (if reviewer agent available)

## Next Wave

**Handoff To**: nw-product-owner (DISCUSS wave)
**Deliverables**: See Scout's handoff package specification in agent file

# Expected outputs (reference only):
# - docs/discovery/problem-validation.md
# - docs/discovery/opportunity-tree.md
# - docs/discovery/solution-testing.md
# - docs/discovery/lean-canvas.md
# - docs/discovery/interview-log.md
# - docs/discovery/discovery-decisions.md (if Walking Skeleton selected)
