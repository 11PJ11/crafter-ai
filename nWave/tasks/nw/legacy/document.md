# NW-DOCUMENT: Evidence-Based DIVIO Documentation Creation

**Wave**: CROSS_WAVE
**Agents**: Nova (nw-researcher) + Quill (nw-documentarist)
**Command**: `*document`

## Overview

Execute systematic documentation creation through evidence-based research followed by DIVIO-compliant documentation validation. This command orchestrates two specialized agents to ensure documentation is both factually accurate (research-backed) and structurally sound (DIVIO-compliant).

Cross-wave support capability providing truthful, well-structured documentation for any nWave phase requiring documentation of features, components, or architectural decisions.

## Layer 4 Peer Review Integration

This command implements **Layer 4: Adversarial Verification** through peer review at two critical quality gates:

1. **Research Review Gate** (Phase 1.5): nw-researcher-reviewer validates research quality before documentation
2. **Documentation Review Gate** (Phase 2.5): nw-documentarist-reviewer validates documentation quality before handoff

### Review Architecture

**Equal-Expertise Validation**: Reviewers are specialist agents with equal domain expertise running on Haiku model for cost efficiency:
- `nw-researcher-reviewer` (Scholar persona) - validates research quality, evidence, bias, cross-referencing
- `nw-documentarist-reviewer` (Quill persona) - validates DIVIO compliance, collapse detection, classification accuracy

**Independent Analysis Protocol**: Reviewers perform independent verification BEFORE comparing to original agent output:
1. Read artifact and original source material
2. Perform independent analysis (classification, validation, collapse detection)
3. Compare findings to original agent's findings
4. Flag discrepancies as issues with severity levels

**Embedded Invocation**: Orchestrator embeds complete review procedures inline using Task tool (reviewers cannot access Skill tool):
- No external /nw:review command references in agent prompts
- Complete review criteria embedded in Task invocation
- Review metadata appended to original artifact files
- Iteration limits enforced (max 2 cycles per phase)

### Review Workflow

```
Phase 1: Research
  ├─> researcher (Nova) produces research document
  │
Phase 1.5: Research Review
  ├─> nw-researcher-reviewer (Scholar) performs independent validation
  ├─> If APPROVED → proceed to Phase 2
  ├─> If NEEDS_REVISION → iterate (max 2 cycles)
  └─> If REJECTED → escalate to user

Phase 2: Documentation
  ├─> nw-documentarist (Quill) produces documentation
  │
Phase 2.5: Documentation Review
  ├─> nw-documentarist-reviewer (Quill) performs independent validation
  ├─> If APPROVED → proceed to handoff
  ├─> If NEEDS_REVISION → iterate (max 2 cycles)
  └─> If RESTRUCTURE_REQUIRED → escalate to user

Handoff: Both reviews approved, documentation ready
```

### Quality Gates Enforced by Review

**Research Review Quality Gates**:
- All sources independently verifiable (URLs resolve, content matches claims)
- No bias detected (multiple perspectives, contradictory evidence acknowledged)
- Evidence quality meets standards (peer-reviewed, authoritative sources)
- Cross-reference validation (≥3 independent sources per claim)
- Research organized for documentation transformation

**Documentation Review Quality Gates**:
- Classification accuracy (correct DIVIO type assignment)
- Validation completeness (all type-specific criteria checked)
- Collapse detection (no anti-patterns, type purity ≥80%)
- Recommendation quality (specific, actionable, prioritized)
- Quality scores accurate (readability, spelling, style compliance)
- Verdict appropriate (matches issues found)

### Error Handling and Escalation

**Iteration Limits**: Maximum 2 revision cycles per phase
- Cycle 1: Agent produces → Reviewer critiques → Agent addresses feedback
- Cycle 2: Reviewer validates revisions
- After Cycle 2: If issues persist → Escalate to user

**Escalation Conditions**:
- Research REJECTED (fundamental flaws)
- Documentation RESTRUCTURE_REQUIRED (collapse detected)
- Review iteration limit exceeded (2 cycles)
- Persistent issues after revision

**User Options on Escalation**:
- Fix manually and continue
- Accept with known issues (documented)
- Restart from earlier phase
- Cancel documentation creation

## Orchestrator Briefing

**CRITICAL ARCHITECTURAL CONSTRAINT**: Sub-agents launched via Task tool have NO ACCESS to the Skill tool. They can ONLY use: Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch.

### What Orchestrator Must Do

1. **Read configuration files and embed complete specifications inline**
2. **Create complete agent prompts** that include:
   - Full topic definition and documentation scope (inline)
   - Complete trusted-source-domains.yaml content (inline, not path reference)
   - Research depth requirements based on documentation type
   - DIVIO framework principles and validation rules (inline)
   - Documentation type selection criteria
   - Research-to-documentation transformation procedures
   - All procedural steps for research, review, documentation, and review phases
   - **Complete review procedures embedded in Task invocations** (no /nw:review references)
3. **Do NOT reference any /nw:* commands** in agent prompts (agents cannot invoke them)
4. **Embed all procedures** - agents execute directly, no command delegation
5. **Orchestrate review workflow**:
   - Invoke nw-researcher-reviewer after research phase completion
   - Handle review feedback iteration (max 2 cycles)
   - Invoke nw-documentarist-reviewer after documentation phase completion
   - Handle review feedback iteration (max 2 cycles)
   - Escalate to user if iteration limits exceeded or critical failures

### Agent Prompt Must Contain

**Phase 1: Research (Nova @nw-researcher)**
- Full topic definition with documentation context (inline)
- Complete trusted-source-domains.yaml content (inline, not path reference)
- Research depth specification:
  - tutorial: overview (introductory concepts, getting started context)
  - howto: detailed (task-specific knowledge, prerequisites, outcomes)
  - reference: comprehensive (complete API/parameter coverage, all edge cases)
  - explanation: deep-dive (architectural reasoning, design decisions, trade-offs)
- Source verification procedures with reputation thresholds (inline)
- Research output structure focused on documentation needs
- Expected research deliverable location: data/research/

**Phase 1.5: Research Review (Scholar @nw-researcher-reviewer)**
- Complete review focus areas (source verification, bias detection, evidence quality, cross-reference validation, documentation readiness)
- Quality gates enforcement (all criteria embedded inline)
- Review output format (append metadata to research document)
- Severity determination framework (CRITICAL, HIGH, MEDIUM, LOW)
- Approval decision logic (APPROVED, NEEDS_REVISION, REJECTED)
- **NO /nw:review command references** - complete procedures embedded

**Phase 2: Documentation (Quill @nw-documentarist)**
- Complete DIVIO framework principles (inline)
- Documentation type validation rules (inline)
- Collapse detection anti-patterns (inline)
- Quality gate criteria (readability, completeness, type purity)
- Research artifact integration procedures
- Documentation output location based on type
- Validation checklist for final approval

**Phase 2.5: Documentation Review (Quill @nw-documentarist-reviewer)**
- Complete review focus areas (classification accuracy, validation completeness, collapse detection, recommendation quality, quality scores, verdict appropriateness)
- Quality gates enforcement (all criteria embedded inline)
- Review output format (append metadata to documentation file)
- Severity determination framework (CRITICAL, HIGH, MEDIUM, LOW)
- Approval decision logic (APPROVED, NEEDS_REVISION, RESTRUCTURE_REQUIRED)
- Independent verification protocol (analyze first, then compare)
- **NO /nw:review command references** - complete procedures embedded

### What NOT to Include

- ❌ "Agent should invoke /nw:document on related topics" (agent handles topic only)
- ❌ "Use /nw:research to gather data" (orchestrator handles research, not agent)
- ❌ "Use /nw:review to validate output" (orchestrator handles review invocation)
- ❌ Any reference to skills or other commands the agent should call
- ❌ Path references without complete content embedded (agents need inline data)
- ❌ External links or tool references without complete procedures embedded
- ❌ References to /nw:* commands in reviewer prompts (embed procedures inline instead)

### Example: What TO Do

✅ "Research this topic using only these trusted sources: [COMPLETE DOMAINS WITH REPUTATION SCORES]"
✅ "Create [tutorial|howto|reference|explanation] documentation following these DIVIO principles: [COMPLETE FRAMEWORK]"
✅ "Validate documentation against these criteria: [COMPLETE CHECKLIST]"
✅ "Detect collapse patterns using these rules: [COMPLETE ANTI-PATTERNS]"
✅ "Review research for source verification, bias detection, evidence quality: [COMPLETE REVIEW CRITERIA]"
✅ "Review documentation for classification accuracy, collapse detection: [COMPLETE REVIEW CRITERIA]"
✅ "Append review metadata to artifact: [COMPLETE OUTPUT FORMAT]"
✅ "Provide outputs: research in data/research/, documentation in [docs/tutorials/|docs/howto/|docs/reference/|docs/explanation/]"

## Context Files Required

- nWave/data/config/trusted-source-domains.yaml - Source reputation validation
- nWave/agents/nw-researcher.md - Research agent DIVIO framework knowledge (for extraction)
- nWave/agents/nw-documentarist.md - Documentation agent validation rules (for extraction)

## Previous Artifacts (Wave Handoff)

- Varies based on documentation topic and invoking wave
- May include: architecture documents, code implementations, design decisions

## Command Invocation

### Syntax

```bash
/nw:document [topic/component] [options]
```

### Arguments

- **topic/component** (required): The subject to document
- **--type=[tutorial|howto|reference|explanation]** (optional): DIVIO documentation type
  - If not specified, orchestrator will ask user which type
- **--research-depth=[overview|detailed|comprehensive|deep-dive]** (optional): Research depth
  - Default: Auto-selected based on documentation type
  - tutorial → overview
  - howto → detailed
  - reference → comprehensive
  - explanation → deep-dive

### Examples

```bash
# Tutorial documentation with automatic research depth (overview)
/nw:document "Getting Started with nWave" --type=tutorial

# How-to guide with specified research depth
/nw:document "Configure Multi-Tenant Authentication" --type=howto --research-depth=detailed

# Reference documentation with comprehensive research
/nw:document "nWave Agent API" --type=reference

# Explanation with deep-dive research
/nw:document "Why nWave Uses 5-Layer Safety Framework" --type=explanation --research-depth=deep-dive

# Interactive (no type specified - orchestrator asks)
/nw:document "Mikado Method Integration"
```

## Orchestration Workflow

**Enhanced with Layer 4 Peer Review**: This workflow integrates peer review at two critical points - after research completion (nw-researcher-reviewer validates research quality) and after documentation completion (nw-documentarist-reviewer validates documentation quality). Reviews are mandatory quality gates that must pass before proceeding to the next phase.

### Step 1: Pre-Flight Validation

**Orchestrator performs:**

1. **Argument Validation**:
   - Topic/component is non-empty
   - Documentation type is valid (if specified)
   - Research depth is valid (if specified)

2. **Type Selection** (if not specified):
   ```
   What type of documentation do you need for "{topic}"?

   1. TUTORIAL - "Teach me" (Learning-oriented, for newcomers)
      Purpose: Enable newcomer to achieve first success
      Example: "Getting Started with nWave"

   2. HOW-TO GUIDE - "Help me do X" (Task-oriented, for practitioners)
      Purpose: Help user accomplish specific objective
      Example: "How to Configure Authentication"

   3. REFERENCE - "What is X?" (Information-oriented, for lookup)
      Purpose: Provide accurate lookup for specific information
      Example: "nWave Agent API Reference"

   4. EXPLANATION - "Why is X?" (Understanding-oriented, for context)
      Purpose: Build conceptual understanding and design rationale
      Example: "Why nWave Uses Hexagonal Architecture"

   Select type [1/2/3/4]:
   ```

3. **Research Depth Auto-Selection** (if not specified):
   - tutorial → overview
   - howto → detailed
   - reference → comprehensive
   - explanation → deep-dive

4. **Output Location Determination**:
   - tutorial → docs/tutorials/{topic-kebab-case}.md
   - howto → docs/howto/{topic-kebab-case}.md
   - reference → docs/reference/{topic-kebab-case}.md
   - explanation → docs/explanation/{topic-kebab-case}.md

### Step 2: Phase 1 - Research (Nova @nw-researcher)

**Orchestrator invokes researcher with COMPLETE INLINE PROMPT**:

```
You are Nova, the Evidence-Driven Knowledge Researcher.

TASK: Gather factual, evidence-based information about "{topic}" to support creation of {type} documentation.

DOCUMENTATION CONTEXT:
- Documentation Type: {tutorial|howto|reference|explanation}
- User Need: {Teach me|Help me do X|What is X?|Why is X?}
- Research Focus: {type-specific focus areas}

RESEARCH DEPTH: {overview|detailed|comprehensive|deep-dive}

TRUSTED SOURCES (inline - complete list):
[COMPLETE CONTENTS OF trusted-source-domains.yaml]

RESEARCH PROCEDURES:
1. Source Verification:
   - Check against trusted domains list above
   - Verify domain reputation (high/medium-high/medium only)
   - Cross-reference with ≥3 independent sources per major claim

2. Documentation-Focused Research:
   For {type} documentation, prioritize:
   {type-specific research priorities - see below}

3. Research Output Structure:
   - Executive summary with key findings for documentation
   - Detailed findings organized by documentation needs
   - Complete citations with URLs and access dates
   - Knowledge gaps explicitly documented

4. Quality Gates:
   - All sources from trusted domains
   - ≥3 sources per major claim
   - Citation coverage > 95%
   - Average source reputation ≥ 0.80

OUTPUT LOCATION: data/research/{topic-kebab-case}-for-{type}-doc.md

DELIVERABLE: Comprehensive research document ready for documentation transformation.
```

**Type-Specific Research Priorities**:

```yaml
tutorial:
  focus:
    - "Prerequisite concepts (what newcomer needs to know)"
    - "First success examples (proven introductory paths)"
    - "Common newcomer pitfalls and solutions"
    - "Step-by-step progression patterns"
  depth: overview

howto:
  focus:
    - "Task prerequisites and baseline knowledge"
    - "Step-by-step procedures with outcomes"
    - "Common task variations and edge cases"
    - "Success indicators and completion criteria"
  depth: detailed

reference:
  focus:
    - "Complete API/function/parameter specifications"
    - "Return values and error conditions"
    - "Type signatures and constraints"
    - "All edge cases and exceptions"
  depth: comprehensive

explanation:
  focus:
    - "Design decisions and architectural reasoning"
    - "Trade-offs and alternatives considered"
    - "Context and historical evolution"
    - "Cross-cutting concerns and implications"
  depth: deep-dive
```

### Step 3: Phase 1.5 - Research Review (Scholar @nw-researcher-reviewer)

**Orchestrator invokes nw-researcher-reviewer for quality assurance**:

**CRITICAL**: Use Task tool to invoke nw-researcher-reviewer agent (NOT /nw:review command). Sub-agents cannot execute skills.

```
Task: "You are the nw-researcher-reviewer agent acting as an expert reviewer.

Your specific role for this command: Provide expert critique and quality assurance for research artifacts

Task type: review

Perform a comprehensive research review of: data/research/{topic-kebab-case}-for-{type}-doc.md

## REVIEW FOCUS AREAS

Source Verification:
- Can all cited sources be independently verified by different agent?
- Do provided URLs resolve and contain claimed information?
- Are citations complete with all required metadata (title, author, date, URL)?
- Are paywalled sources clearly marked with access restrictions?
- Can sources be accessed without special credentials?

Bias Detection:
- Are sources cherry-picked to support predetermined narrative?
- Is contradictory evidence from reputable sources acknowledged?
- Are multiple perspectives represented (not just single viewpoint)?
- Is publication date distribution balanced or skewed to specific era?
- Are sources geographically diverse or limited to single region?

Evidence Quality:
- Is evidence strong (peer-reviewed, authoritative) or circumstantial?
- Are logical fallacies present (correlation as causation, appeal to authority)?
- Are sample sizes adequate for claims made?
- Are confidence levels explicitly stated with rationale?
- Is statistical significance properly interpreted?

Cross-Reference Validation:
- Do minimum 3 independent sources support each major claim?
- Are sources truly independent or citing each other (circular)?
- Are primary sources used where possible vs secondary interpretations?
- Is source independence verified (not all from same publisher/author)?

Documentation Readiness:
- Is research organized for {type} documentation transformation?
- Are findings focused on documentation type needs (not generic research)?
- Is information depth appropriate for {type}?

## QUALITY GATES

- All sources from trusted-source-domains.yaml: REQUIRED
- Cross-reference performed (≥3 sources per major claim): REQUIRED
- Citation coverage > 95%: REQUIRED
- Average source reputation ≥ 0.80: REQUIRED
- Research focused on documentation type needs: REQUIRED

## OUTPUT REQUIREMENTS

Update the research document by appending review metadata:

```yaml
reviews:
  - reviewer: "nw-researcher-reviewer"
    date: "{ISO-8601-timestamp}"
    overall_assessment: "APPROVED|NEEDS_REVISION|REJECTED"
    critiques:
      - aspect: "{source_verification|bias_detection|evidence_quality|cross_reference|doc_readiness}"
        issue: "{specific issue description}"
        severity: "HIGH|MEDIUM|LOW"
        recommendation: "{actionable fix}"
    approval_status:
      ready_for_documentation: {true|false}
      blocking_issues: ["{issue if not ready}"]
```

Assign overall assessment:
- APPROVED: Research meets all quality gates, ready for documentation phase
- NEEDS_REVISION: Issues found that must be addressed before documentation
- REJECTED: Fundamental flaws requiring research restart

For HIGH severity issues, mark ready_for_documentation: false"
```

**Review Iteration Handling**:

1. **If Review APPROVED**:
   - Proceed to Phase 2 (Documentation)
   - No iteration needed

2. **If Review NEEDS_REVISION**:
   - Extract critique issues from review metadata
   - Re-invoke researcher (Nova) with feedback:
     ```
     "Address review feedback from nw-researcher-reviewer:
     {list of critiques with severity and recommendations}

     Update research document to resolve these issues."
     ```
   - Re-invoke nw-researcher-reviewer for validation
   - Maximum 2 iteration cycles
   - If still failing after 2 cycles: Escalate to user

3. **If Review REJECTED**:
   - Report to user immediately
   - Ask: "Research fundamentally flawed. Options: 1) Restart research, 2) Adjust topic scope, 3) Cancel"
   - Do not proceed to documentation phase

### Step 4: Phase 2 - Documentation (Quill @nw-documentarist)

**Orchestrator invokes nw-documentarist with COMPLETE INLINE PROMPT**:

```
You are Quill, the Documentation Quality Guardian.

TASK: Create DIVIO-compliant {type} documentation for "{topic}" based on research findings.

RESEARCH INPUT: data/research/{topic-kebab-case}-for-{type}-doc.md

DIVIO FRAMEWORK (inline - complete principles):
[COMPLETE DIVIO FRAMEWORK FROM nw-documentarist.md]

DOCUMENTATION TYPE: {type}

TYPE-SPECIFIC REQUIREMENTS:
[TYPE-SPECIFIC VALIDATION RULES FROM nw-documentarist.md]

COLLAPSE PREVENTION:
[COMPLETE ANTI-PATTERNS FROM nw-documentarist.md]

QUALITY GATES:
- Readability: Flesch score 70-80
- Type purity: 80%+ single quadrant content
- Spelling errors: 0
- Broken links: 0
- Style compliance: 95%+
- All claims backed by research citations

WORKFLOW:
1. Read research document from data/research/
2. Extract information relevant to {type} documentation
3. Structure content following {type} template (see below)
4. Cite research sources for factual claims
5. Validate against type-specific criteria
6. Detect collapse anti-patterns
7. Assess quality against six characteristics
8. Write documentation to: {output-location}
9. Create validation report

OUTPUT LOCATIONS:
- Documentation: {output-location}
- Validation Report: {output-location}.validation.yaml

DELIVERABLE: DIVIO-compliant {type} documentation with validation report.
```

**Type-Specific Documentation Templates**:

```markdown
# TUTORIAL TEMPLATE
# {Topic} - Getting Started

## What You'll Learn
- {Objective 1}
- {Objective 2}
- {Objective 3}

## Prerequisites
None - this tutorial assumes no prior knowledge.

## Step 1: {First Action}
{Clear instruction}

**You should see:**
{Expected outcome}

## Step 2: {Next Action}
{Clear instruction}

**You should see:**
{Expected outcome}

[Continue steps...]

## What You've Accomplished
{Summary of what user can now do}

## Next Steps
Ready for more? See:
- [How-to: {Related Task}](../howto/{link}.md)
- [Explanation: {Deeper Context}](../explanation/{link}.md)

---

# HOW-TO TEMPLATE
# How to {Specific Task}

## Goal
{Clear, measurable objective}

## Prerequisites
- {Required knowledge/tools}
- {Baseline understanding expected}

## Steps

### 1. {Action}
{Instruction}

**Result:** {What happens}

### 2. {Next Action}
{Instruction}

**Result:** {What happens}

[Continue steps...]

## Done
You have successfully {task completed}.

## Related
- [Tutorial: {Basics}](../tutorials/{link}.md) - New to this?
- [Reference: {API}](../reference/{link}.md) - API details

---

# REFERENCE TEMPLATE
# {Function/API/Component} Reference

## Overview
{Brief factual description}

## Signature
```
{type signature or function declaration}
```

## Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| {name} | {type} | {yes/no} | {description} |

## Return Value
{Type and description}

## Errors
| Error | Condition | Description |
|-------|-----------|-------------|
| {error} | {when} | {what it means} |

## Examples
```
{code example 1}
```

```
{code example 2}
```

## See Also
- [Explanation: {Why This Exists}](../explanation/{link}.md)

---

# EXPLANATION TEMPLATE
# {Concept/Decision/Architecture}

## Context
{Background and situational context}

## Problem Statement
{What problem does this address?}

## Design Rationale
{Why this approach was chosen}

## Alternatives Considered
### Alternative 1: {Name}
- **Description**: {What it is}
- **Pros**: {Benefits}
- **Cons**: {Drawbacks}
- **Why Not Chosen**: {Reason}

### Alternative 2: {Name}
[Same structure]

## Trade-offs
{What we gain and what we lose}

## Implications
{Cross-cutting concerns, long-term effects}

## Related Concepts
{Connections to other architectural decisions}

## Further Learning
- [Tutorial: {Hands-On}](../tutorials/{link}.md)
- [How-to: {Practical Application}](../howto/{link}.md)
```

### Step 5: Phase 2.5 - Documentation Review (Quill @nw-documentarist-reviewer)

**Orchestrator invokes nw-documentarist-reviewer for quality assurance**:

**CRITICAL**: Use Task tool to invoke nw-documentarist-reviewer agent (NOT /nw:review command). Sub-agents cannot execute skills.

```
Task: "You are the nw-documentarist-reviewer agent acting as an expert reviewer.

Your specific role for this command: Provide expert critique and quality assurance for documentation artifacts

Task type: review

Perform a comprehensive {type} documentation review of: {output-location}

## REVIEW FOCUS AREAS

Classification Accuracy:
- Is the document correctly classified as {type}?
- Are classification signals present in the content?
- Are there contradicting signals for other types?
- Is the decision tree classification correct?
- Are edge cases properly handled?

Validation Completeness:
- Were ALL {type}-specific validation criteria checked?
- Are checklist results accurate (pass/fail correctly assigned)?
- Are issues properly located (line/section references)?
- Are fixes actionable and specific?
- Were any validation criteria missed?

Collapse Detection:
- Are collapse anti-patterns correctly identified?
- Is type purity ≥ 80% (single quadrant content)?
- Are false positives present?
- Are split recommendations appropriate?
- Is the 20% threshold applied correctly using line count?

Recommendation Quality:
- Is each recommendation specific (not vague)?
- Is each recommendation actionable (clear next step)?
- Are priorities correct (critical issues first)?
- Is effort estimation reasonable?
- Do recommendations address root cause?

Quality Score Accuracy:
- Is readability score (Flesch) accurately calculated or estimated?
- Is spelling error count correct?
- Is style compliance measured correctly?
- Is type purity checked using line count method?
- Are scores supported by evidence?

Verdict Appropriateness:
- Does verdict match the issues found?
- Should 'approved' really pass given issues?
- Is 'restructure-required' warranted by collapse evidence?
- Are minor issues blocking approval inappropriately?
- Are major issues being overlooked?

## QUALITY GATES

- Documentation follows DIVIO {type} template: REQUIRED
- Type purity ≥ 80% (single quadrant content): REQUIRED
- No collapse anti-patterns detected: REQUIRED
- Readability Flesch score 70-80: RECOMMENDED
- Zero spelling errors: RECOMMENDED
- Zero broken links: REQUIRED
- Style compliance ≥ 95%: RECOMMENDED
- All factual claims cited from research: REQUIRED

## OUTPUT REQUIREMENTS

Update the documentation file by appending review metadata:

```yaml
reviews:
  - reviewer: "nw-documentarist-reviewer"
    date: "{ISO-8601-timestamp}"
    overall_assessment: "APPROVED|NEEDS_REVISION|RESTRUCTURE_REQUIRED"
    critiques:
      - aspect: "{classification|validation|collapse|recommendations|quality|verdict}"
        issue: "{specific issue description}"
        severity: "CRITICAL|HIGH|MEDIUM|LOW"
        recommendation: "{actionable fix}"
    approval_status:
      ready_for_handoff: {true|false}
      blocking_issues: ["{issue if not ready}"]
```

Assign overall assessment:
- APPROVED: Documentation meets all quality gates, ready for handoff
- NEEDS_REVISION: Issues found that must be addressed
- RESTRUCTURE_REQUIRED: Collapse detected; document needs split

For CRITICAL or HIGH severity issues, mark ready_for_handoff: false"
```

**Review Iteration Handling**:

1. **If Review APPROVED**:
   - Proceed to Step 6 (Validation and Handoff)
   - No iteration needed

2. **If Review NEEDS_REVISION**:
   - Extract critique issues from review metadata
   - Re-invoke nw-documentarist (Quill) with feedback:
     ```
     "Address review feedback from nw-documentarist-reviewer:
     {list of critiques with severity and recommendations}

     Update documentation to resolve these issues."
     ```
   - Re-invoke nw-documentarist-reviewer for validation
   - Maximum 2 iteration cycles
   - If still failing after 2 cycles: Escalate to user

3. **If Review RESTRUCTURE_REQUIRED**:
   - Report to user immediately
   - Ask: "Documentation has collapse issues. Options: 1) Split into separate docs, 2) Revise research focus, 3) Accept with issues"
   - If user chooses split: Re-invoke nw-documentarist with split instructions

### Step 6: Validation and Handoff

**Orchestrator performs final checks:**

1. **Verify Deliverables**:
   - Research document exists: data/research/{topic}-for-{type}-doc.md
   - Research review metadata present in research document
   - Documentation exists: {output-location}
   - Documentation review metadata present in documentation file
   - Validation report exists: {output-location}.validation.yaml

2. **Quality Validation**:
   - Read research review metadata: Check overall_assessment = APPROVED
   - Read documentation review metadata: Check overall_assessment = APPROVED
   - Read validation report
   - Check verdict: approved | needs-revision | restructure-required
   - If any review not approved or needs-revision or restructure-required:
     - Display issues and recommendations
     - Ask user: "Fix now | Save with issues | Iterate phase"

3. **Success Report**:
   ```
   ✅ Documentation Created Successfully

   Type: {type}
   Topic: {topic}

   Deliverables:
   - Research: data/research/{filename}
   - Documentation: {output-location}
   - Validation: {output-location}.validation.yaml

   Quality Gates:
   - Type purity: {percentage}%
   - Readability: {flesch-score}
   - Collapse detected: {yes/no}
   - Verdict: {verdict}

   Layer 4 Peer Review:
   - Research review: {APPROVED|NEEDS_REVISION|REJECTED}
   - Documentation review: {APPROVED|NEEDS_REVISION|RESTRUCTURE_REQUIRED}
   - Total review iterations: {count}

   {If issues exist, list top 3 with fix recommendations}
   ```

## Success Criteria

### Research Phase (Nova)

- [ ] All sources from trusted-source-domains.yaml
- [ ] Cross-reference performed (≥3 sources per major claim)
- [ ] Research document created in data/research/
- [ ] Citation coverage > 95%
- [ ] Average source reputation ≥ 0.80
- [ ] Research focused on documentation type needs

### Research Review Phase (Scholar @nw-researcher-reviewer)

- [ ] Research passes peer review (nw-researcher-reviewer approval)
- [ ] All sources independently verifiable
- [ ] No bias detected (multiple perspectives represented)
- [ ] Evidence quality meets standards (peer-reviewed, authoritative)
- [ ] Cross-reference validation passed (≥3 independent sources)
- [ ] Research organized for documentation transformation
- [ ] Review metadata appended to research document
- [ ] overall_assessment = APPROVED

### Documentation Phase (Quill)

- [ ] Documentation follows DIVIO type template
- [ ] Type purity ≥ 80% (single quadrant content)
- [ ] No collapse anti-patterns detected
- [ ] Readability Flesch score 70-80
- [ ] Zero spelling errors
- [ ] Zero broken links
- [ ] Style compliance ≥ 95%
- [ ] All factual claims cited from research
- [ ] Validation report generated

### Documentation Review Phase (Quill @nw-documentarist-reviewer)

- [ ] Documentation passes peer review (nw-documentarist-reviewer approval)
- [ ] Classification accuracy verified (correct type assignment)
- [ ] Validation completeness confirmed (all criteria checked)
- [ ] Collapse detection verified (no false positives/negatives)
- [ ] Recommendation quality validated (specific, actionable, prioritized)
- [ ] Quality scores accurate (readability, type purity, style)
- [ ] Verdict appropriate (matches issues found)
- [ ] Review metadata appended to documentation file
- [ ] overall_assessment = APPROVED
- [ ] No critical issues detected

### Integration Success

- [ ] Research findings successfully transformed to documentation
- [ ] Documentation readable without accessing research
- [ ] Research provides sufficient depth for documentation type
- [ ] Documentation location correct for type
- [ ] Cross-references follow DIVIO linking patterns
- [ ] Both reviews detect no critical issues
- [ ] Review iterations ≤ 2 per phase (research and documentation)

## Error Handling

### Research Phase Failures

**Insufficient Sources**:
```
WARNING: Research phase incomplete - insufficient reputable sources found.

Knowledge Gaps:
- {gap 1 description}
- {gap 2 description}

Options:
1. Continue with partial research (documentation will note gaps)
2. Expand research scope (retry with broader search)
3. Cancel and revise topic

Select option [1/2/3]:
```

**Source Reputation Too Low**:
```
ERROR: Average source reputation {score} below threshold 0.80.

Recommendation: Expand search to academic and official sources.

Retry research? [yes/no]:
```

### Research Review Phase Failures

**Review NEEDS_REVISION**:
```
WARNING: Research review identified issues requiring correction.

Critique Summary:
- HIGH severity: {count} issues
- MEDIUM severity: {count} issues
- LOW severity: {count} issues

Top Issues:
1. {issue 1 with recommendation}
2. {issue 2 with recommendation}
3. {issue 3 with recommendation}

Action: Re-invoking researcher with feedback (Iteration {X}/2)
```

**Review REJECTED**:
```
ERROR: Research fundamentally flawed - reviewer rejected.

Critical Issues:
- {critical issue 1}
- {critical issue 2}

Options:
1. Restart research with revised scope
2. Adjust topic to be more specific
3. Cancel documentation creation

Select option [1/2/3]:
```

**Review Iteration Limit Exceeded**:
```
ERROR: Research review failed after 2 iteration cycles.

Persistent Issues:
- {issue 1 still present}
- {issue 2 still present}

Escalating to user for manual resolution.

Options:
1. Manually fix research and continue
2. Accept research with known issues
3. Cancel documentation creation

Select option [1/2/3]:
```

### Documentation Phase Failures

**Collapse Detected**:
```
WARNING: Documentation contains collapse anti-patterns.

Violations:
- {violation 1}: {location} - {description}
- {violation 2}: {location} - {description}

Recommendation: {fix-collapse recommendations}

Options:
1. Fix collapse (split into separate documents)
2. Save with issues (user will fix manually)
3. Revise research focus

Select option [1/2/3]:
```

**Quality Gate Failure**:
```
ERROR: Documentation failed quality gates.

Failed Gates:
- {gate 1}: {actual} (required: {threshold})
- {gate 2}: {actual} (required: {threshold})

Recommendations:
- {fix 1}
- {fix 2}

Retry documentation phase with fixes? [yes/no]:
```

### Documentation Review Phase Failures

**Review NEEDS_REVISION**:
```
WARNING: Documentation review identified issues requiring correction.

Critique Summary:
- CRITICAL severity: {count} issues
- HIGH severity: {count} issues
- MEDIUM severity: {count} issues
- LOW severity: {count} issues

Top Issues:
1. {issue 1 with recommendation}
2. {issue 2 with recommendation}
3. {issue 3 with recommendation}

Action: Re-invoking nw-documentarist with feedback (Iteration {X}/2)
```

**Review RESTRUCTURE_REQUIRED**:
```
ERROR: Documentation review detected collapse - restructuring required.

Collapse Issues:
- Type purity: {percentage}% (threshold: 80%)
- Anti-patterns detected: {list}

Recommendations:
- {split recommendation 1}
- {split recommendation 2}

Options:
1. Split into separate documents (recommended)
2. Revise research focus to single type
3. Accept with issues (not recommended)

Select option [1/2/3]:
```

**Review Iteration Limit Exceeded**:
```
ERROR: Documentation review failed after 2 iteration cycles.

Persistent Issues:
- {issue 1 still present}
- {issue 2 still present}

Escalating to user for manual resolution.

Options:
1. Manually fix documentation and continue
2. Accept documentation with known issues
3. Restart from research phase

Select option [1/2/3]:
```

## Next Wave

**Handoff To**: {invoking-agent-returns-to-workflow}

**Deliverables**:
- Research document: data/research/{topic}-for-{type}-doc.md
- DIVIO documentation: {output-location based on type}
- Validation report: {output-location}.validation.yaml

**Integration Points**:
- Documentation can be referenced from code comments
- Documentation can be linked from architecture diagrams
- Documentation can inform test scenarios
- Documentation serves as onboarding material

## Implementation Notes

### Directory Structure

```
docs/
├── tutorials/           # Tutorial documentation (Teach me)
├── howto/              # How-to guides (Help me do X)
├── reference/          # Reference documentation (What is X?)
└── explanation/        # Explanation documentation (Why is X?)

data/
└── research/           # Research artifacts supporting documentation
```

### Documentation Type Decision Matrix

| User Ask | User Knows | Type | Output Dir |
|----------|-----------|------|------------|
| "Teach me" | Nothing | Tutorial | docs/tutorials/ |
| "Help me do X" | Basics | How-to | docs/howto/ |
| "What is X?" | What to look for | Reference | docs/reference/ |
| "Why is X?" | Basics, wants depth | Explanation | docs/explanation/ |

### Research Depth Justification

- **Tutorial (overview)**: Newcomers don't need deep research - surface-level understanding sufficient
- **How-to (detailed)**: Task completion requires practical, detailed knowledge
- **Reference (comprehensive)**: Complete API coverage demands exhaustive research
- **Explanation (deep-dive)**: Architectural reasoning requires thorough investigation

### Cross-Reference Patterns (DIVIO Compliance)

✅ **Correct**:
- Tutorial → How-to (progression to practical use)
- How-to → Tutorial (backfill basics) + Reference (API lookup)
- Reference → Explanation (why it exists)
- Explanation → Tutorial (hands-on learning)

❌ **Incorrect** (collapse indicators):
- Tutorial → Explanation (teaching should stay practical)
- How-to → Explanation (task focus, not theory)
- Reference → Tutorial (lookup, not teaching)

## Complete Workflow Integration

```bash
# Standalone documentation creation
/nw:document "nWave Agent Safety Framework" --type=explanation

# Documentation after architecture (DESIGN wave)
/nw:design "Hexagonal Architecture for nWave"
/nw:document "Why nWave Uses Hexagonal Architecture" --type=explanation

# Documentation during development (DEVELOP wave)
/nw:develop "Multi-Tenant Authentication"
/nw:document "Configure Multi-Tenant Auth" --type=howto

# Documentation for onboarding (any wave)
/nw:document "Getting Started with nWave" --type=tutorial
```

## Observability

### Metrics Tracked

- Documentation type distribution (count by type)
- Research depth distribution
- Average time: research phase
- Average time: research review phase
- Average time: documentation phase
- Average time: documentation review phase
- Collapse detection rate
- Quality gate pass rate
- Research citation coverage
- Documentation readability scores
- **Review metrics (Layer 4)**:
  - Research review approval rate
  - Documentation review approval rate
  - Average review iterations (research)
  - Average review iterations (documentation)
  - Review failure reasons distribution
  - Escalation rate (review iteration limit exceeded)

### Success Indicators

- Type purity ≥ 80%
- Collapse rate < 10%
- Quality gate pass rate ≥ 90%
- Citation coverage > 95%
- User satisfaction with documentation clarity
- **Layer 4 Review indicators**:
  - Research review approval rate ≥ 85% (first attempt)
  - Documentation review approval rate ≥ 85% (first attempt)
  - Average review iterations ≤ 1.2 per phase
  - Escalation rate < 5%
  - Zero critical issues in approved documentation

## Compliance Validation

This command implements:

✅ Evidence-based research (no speculative documentation)
✅ DIVIO framework compliance (four types, no hybrids)
✅ Collapse prevention (systematic anti-pattern detection)
✅ Quality gates (readability, completeness, correctness)
✅ Source verification (trusted-source-domains.yaml)
✅ Cross-wave capability (usable from any nWave phase)
✅ Agent orchestration (researcher → nw-researcher-reviewer → nw-documentarist → nw-documentarist-reviewer)
✅ **Layer 4 Peer Review** (equal-expertise reviewer validation at two quality gates)
✅ Production readiness (error recovery, validation, observability)
✅ Review iteration limits (max 2 cycles per phase with escalation)
✅ Independent verification (reviewers do independent analysis before comparison)
