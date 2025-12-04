---
agent-activation:
  required: true
  agent-id: researcher
  agent-name: "Nova"
  agent-command: "*research"
  auto-activate: true
---

# DW-RESEARCH: Evidence-Driven Knowledge Research

**Wave**: CROSS_WAVE
**Agent**: Nova (researcher)
**Command**: `*research`

## Overview

Execute systematic evidence-based research with source verification, gathering knowledge from web and files while ensuring highest quality through clarification questions and reputable sources only.

Cross-wave support capability providing evidence-driven insights for any 5D-Wave phase requiring research-backed decision making using trusted academic, official, and industry sources.

## Context Files Required

- 5d-wave/data/trusted-source-domains.yaml - Source reputation validation

## Previous Artifacts (Wave Handoff)

- Varies based on research topic and invoking wave

## Agent Invocation

@researcher

Execute \*research on {topic} [--embed-for={agent-name}].

**Context Files:**

- 5d-wave/data/trusted-source-domains.yaml

**Configuration:**

- research_depth: detailed # overview/detailed/comprehensive/deep-dive
- source_preferences: ["academic", "official", "technical_docs"]
- quality_threshold: high
- output_directory: docs/research/
- embed_for: {agent-name} # Optional: Creates distilled embed for specified agent
- embed_output_directory: 5d-wave/data/embed/{agent-name}/

**Workflow:**

1. **Research Phase**: Create comprehensive research in data/research/
2. **Distillation Phase** (if --embed-for specified):
   - Distill research into practitioner-focused embed
   - Save to 5d-wave/data/embed/{agent-name}/
   - Validate distillation quality (100% essential concepts preserved)
   - Invoke @agent-forger for peer review if requested

## Success Criteria

Refer to Nova's quality gates in 5d-wave/agents/researcher.md.

**Research Phase Validations:**

- [ ] All sources from trusted-source-domains.yaml
- [ ] Cross-reference performed (≥3 sources per major claim)
- [ ] Comprehensive research file created in data/research/
- [ ] Citation coverage > 95%
- [ ] Average source reputation ≥ 0.80

**Distillation Phase Validations** (if --embed-for specified):

- [ ] Distilled embed file created in 5d-wave/data/embed/{agent-name}/
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
- Distilled embed in 5d-wave/data/embed/{agent}/ (if --embed-for specified)

# Expected outputs (reference only):

# Research only:

# - data/research/{category}/{topic}-comprehensive-research.md

#

# Research + Embed (with --embed-for={agent}):

# - data/research/{category}/{topic}-comprehensive-research.md

# - 5d-wave/data/embed/{agent}/{topic}-methodology.md

#

# Examples:

# /dw:research "Residuality Theory" --embed-for=solution-architect

# → data/research/architecture-patterns/residuality-theory-comprehensive-research.md

# → 5d-wave/data/embed/solution-architect/residuality-theory-methodology.md
