# DW-RESEARCH: Evidence-Driven Knowledge Research

**Wave**: CROSS_WAVE
**Agent**: Nova (nw-researcher)
**Command**: `*research`

## Overview

Execute systematic evidence-based research with source verification, gathering knowledge from web and files while ensuring highest quality through clarification questions and reputable sources only.

Cross-wave support capability providing evidence-driven insights for any nWave phase requiring research-backed decision making using trusted academic, official, and industry sources.

## Orchestrator Briefing

**CRITICAL ARCHITECTURAL CONSTRAINT**: Sub-agents launched via Task tool have NO ACCESS to the Skill tool. They can ONLY use: Read, Write, Edit, Bash, Glob, Grep.

### What Orchestrator Must Do

1. **Read trusted source domains and research topic context** and embed complete specifications inline
2. **Create a complete agent prompt** that includes:
   - Full research topic definition and scope (inline)
   - Complete trusted-source-domains.yaml content (inline, not path reference)
   - Research depth requirements (overview/detailed/comprehensive/deep-dive)
   - Source verification procedures and reputation thresholds (inline)
   - Cross-reference requirements (minimum 3 sources per major claim)
   - Distillation procedures if --embed-for specified (academic to actionable transformation)
   - Research output structure with Impact Summary requirements
   - All procedural steps for evidence gathering, citation, and validation
3. **Do NOT reference any /nw:* commands** in the agent prompt (agent cannot invoke them)
4. **Embed all research procedures** - agent executes directly, no command delegation

### Agent Prompt Must Contain

- Full research topic definition with clear boundaries (inline)
- Complete trusted-source-domains.yaml content with reputation scores (inline, not path reference)
- Research depth specifications:
  - overview: Surface-level introduction to topic
  - detailed: Comprehensive coverage with practical applications
  - comprehensive: Full deep-dive with academic rigor and cross-disciplinary perspectives
  - deep-dive: Exhaustive analysis with original research implications
- Source verification procedures:
  - Domain reputation scoring from trusted-source-domains.yaml
  - Cross-reference requirement (≥3 sources per major claim)
  - Citation quality threshold (> 95% coverage)
  - Average reputation requirement (≥ 0.80)
- Research output structure:
  - Executive summary with key findings
  - Detailed findings organized by topic area
  - Impact Summary table (Component, Metric, Impact, Priority)
  - Largest Bottleneck identification with evidence
  - Quick Wins section with effort/impact analysis
  - Complete citations and source documentation
- Distillation procedures (if --embed-for specified):
  - Transform academic findings to practitioner-focused actionable insights
  - Preserve 100% of essential concepts (NO compression)
  - Create self-contained embed file with no external references
  - Token budget management (<5000 tokens per embed file)
- Quantitative research requirements (for performance/impact research):
  - Collect timing data, not just categorization
  - Rank impact by quantitative measures (time, count, frequency)
  - Identify quick wins with effort/impact analysis
- Expected deliverables and file locations

### What NOT to Include

- ❌ "Agent should invoke /nw:research on related topics" (agent handles topic only)
- ❌ "Use /nw:execute to validate research" (agent validates directly)
- ❌ Any reference to skills or other commands the agent should call
- ❌ References to next wave or @agent-forger peer review (orchestrator handles handoffs)
- ❌ Path references without complete content embedded (agent needs trusted domains inline)
- ❌ External links or tool references without complete procedures embedded (WebSearch, WebFetch)

### Example: What TO Do

✅ "Research this topic using only these trusted sources: [COMPLETE DOMAINS WITH REPUTATION SCORES]"
✅ "Gather evidence ensuring ≥3 cross-references per major claim using this procedure: [COMPLETE PROCEDURE]"
✅ "Create Impact Summary following this structure: [COMPLETE TABLE FORMAT WITH EXAMPLES]"
✅ "Distill research for {agent-name} by transforming findings to actionable insights: [COMPLETE DISTILLATION PROCEDURE]"
✅ "Provide outputs: comprehensive-research.md in data/research/, embed file in nWave/data/embed/{agent}/"

## Context Files Required

- nWave/data/trusted-source-domains.yaml - Source reputation validation

## Previous Artifacts (Wave Handoff)

- Varies based on research topic and invoking wave

## Agent Invocation

@nw-researcher

Execute \*research on {topic} [--embed-for={agent-name}].

**Context Files:**

- nWave/data/trusted-source-domains.yaml

**Configuration:**

- research_depth: detailed # overview/detailed/comprehensive/deep-dive
- source_preferences: ["academic", "official", "technical_docs"]
- quality_threshold: high
- output_directory: docs/research/
- embed_for: {agent-name} # Optional: Creates distilled embed for specified agent
- embed_output_directory: nWave/data/embed/{agent-name}/

**Workflow:**

1. **Research Phase**: Create comprehensive research in data/research/
2. **Distillation Phase** (if --embed-for specified):
   - Distill research into practitioner-focused embed
   - Save to nWave/data/embed/{agent-name}/
   - Validate distillation quality (100% essential concepts preserved)
   - Invoke @agent-forger for peer review if requested

## Success Criteria

Refer to Nova's quality gates in nWave/agents/nw-researcher.md.

**Research Phase Validations:**

- [ ] All sources from trusted-source-domains.yaml
- [ ] Cross-reference performed (≥3 sources per major claim)
- [ ] Comprehensive research file created in data/research/
- [ ] Citation coverage > 95%
- [ ] Average source reputation ≥ 0.80

**Distillation Phase Validations** (if --embed-for specified):

- [ ] Distilled embed file created in nWave/data/embed/{agent-name}/
- [ ] 100% of essential concepts preserved (NO compression)
- [ ] Practitioner-focused transformation (academic → actionable)
- [ ] Self-contained (no external file references)
- [ ] Token budget respected (<5000 tokens per embed file recommended)
- [ ] agent-forger peer review approval (optional but recommended)

**Quantitative Research Validations (for performance-related research):**

- [ ] Timing data collected (not just categorization)
- [ ] Impact ranking by quantitative measure (time, count, frequency)
- [ ] Quick win opportunities identified with effort/impact analysis
- [ ] Largest bottleneck explicitly stated with evidence
- [ ] Research includes "Impact Summary" with percentages

**Research Output Should Include:**

```markdown
## Impact Summary

| Component | Metric | Impact | Priority |
|-----------|--------|--------|----------|
| {comp}    | {time/count} | {%} | {1/2/3} |

### Largest Bottleneck
{Component X} accounts for {Y}% of {metric}

### Quick Wins
1. {Action}: {impact} for {effort}
```

## Next Wave

**Handoff To**: {invoking-agent-returns-to-workflow}
**Deliverables**:

- Comprehensive research in data/research/
- Distilled embed in nWave/data/embed/{agent}/ (if --embed-for specified)

# Expected outputs (reference only):

# Research only:

# - data/research/{category}/{topic}-comprehensive-research.md

#

# Research + Embed (with --embed-for={agent}):

# - data/research/{category}/{topic}-comprehensive-research.md

# - nWave/data/embed/{agent}/{topic}-methodology.md

#

# Examples:

# /nw:research "Residuality Theory" --embed-for=solution-architect

# → data/research/architecture-patterns/residuality-theory-comprehensive-research.md

# → nWave/data/embed/solution-architect/residuality-theory-methodology.md
