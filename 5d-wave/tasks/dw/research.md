---
agent-activation:
  required: true
  agent-id: knowledge-researcher
  agent-name: "Nova"
  agent-command: "*research"
  auto-activate: true
---

# DW-RESEARCH: Evidence-Driven Knowledge Research

**Wave**: CROSS_WAVE
**Agent**: Nova (knowledge-researcher)
**Command**: `*research`

## Overview

Execute systematic evidence-based research with source verification, gathering knowledge from web and files while ensuring highest quality through clarification questions and reputable sources only.

Cross-wave support capability providing evidence-driven insights for any 5D-Wave phase requiring research-backed decision making using trusted academic, official, and industry sources.

## Context Files Required

- 5d-wave/data/trusted-source-domains.yaml - Source reputation validation

## Previous Artifacts (Wave Handoff)

- Varies based on research topic and invoking wave

## Agent Invocation

@knowledge-researcher

Execute *research on {topic}.

**Context Files:**
- 5d-wave/data/trusted-source-domains.yaml

**Configuration:**
- research_depth: detailed  # overview/detailed/comprehensive/deep-dive
- source_preferences: ["academic", "official", "technical_docs"]
- quality_threshold: high
- output_directory: docs/research/

## Success Criteria

Refer to Nova's quality gates in 5d-wave/agents/knowledge-researcher.md.

**Key Validations:**
- [ ] All sources from trusted-source-domains.yaml
- [ ] Cross-reference performed (≥3 sources per major claim)
- [ ] Output file created in docs/research/ only
- [ ] Citation coverage > 95%
- [ ] Average source reputation ≥ 0.80

## Next Wave

**Handoff To**: {invoking-agent-returns-to-workflow}
**Deliverables**: Research document in docs/research/

# Expected outputs (reference only):
# - docs/research/{topic}-{timestamp}.md
