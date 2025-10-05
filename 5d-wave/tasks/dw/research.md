---
agent-activation:
  required: true
  agent-id: knowledge-researcher
  agent-name: "Nova"
  agent-command: "*research"
  auto-activate: true
---

**⚠️ AGENT ACTIVATION REQUIRED**

This task requires the **Nova** agent (knowledge-researcher) for execution.

**To activate**: Type `@knowledge-researcher` in the conversation.

Once activated, use the agent's `*help` command to see available operations.

---

# DW-RESEARCH: Evidence-Driven Knowledge Research

## Overview

Execute systematic evidence-based research with source verification, gathering knowledge from web and files while ensuring highest quality through clarification questions and reputable sources only.

## Mandatory Pre-Execution Steps

1. **Output Directory**: Verify docs/research/ exists (request permission if not)
2. **Source Validation**: Ensure trusted-source-domains.yaml is accessible
3. **Research Scope**: Clear understanding of topic, depth, and quality requirements

## Execution Flow

### Phase 1: Research Planning & Clarification

**Primary Agent**: knowledge-researcher (Nova)
**Command**: `*research`

**Research Foundation**:

```
🔍 RESEARCH - EVIDENCE-DRIVEN KNOWLEDGE GATHERING

Systematic approach to gathering verified knowledge using:
- Source reputation validation (academic, official, industry leaders)
- Multi-source cross-referencing (minimum 3 independent sources)
- Evidence-backed findings with full citations
- Clarification questions for scope refinement
- Critical analysis of bias and reliability
- Output restriction to docs/research/ directory only

All sources verified against trusted-source-domains.yaml
```

**Clarification Elicitation**:

```yaml
required_clarifications:
  research_topic:
    question: "What specific aspect should I research?"
    examples:
      - "Research hexagonal architecture patterns"
      - "Investigate outside-in TDD best practices"
      - "Study microservices communication patterns"
    validation: "Specific, focused topic or question"

  research_depth:
    question: "What depth of research do you need?"
    options:
      - overview: "High-level summary from 3-5 sources"
      - detailed: "Comprehensive analysis from 5-10 sources"
      - comprehensive: "Exhaustive research from 10-15 sources"
      - deep-dive: "In-depth academic research from 15+ sources"
    default: "detailed"

  source_preferences:
    question: "What types of sources do you prefer?"
    options:
      - academic: "Peer-reviewed papers, research institutions"
      - official: "Standards bodies, government sources, official docs"
      - industry: "Established companies, recognized experts"
      - technical_docs: "Official technical documentation"
    default: ["academic", "official", "technical_docs"]

  intended_use:
    question: "How will you use this research?"
    examples:
      - "Inform architecture decision"
      - "Support requirements analysis"
      - "Guide implementation approach"
      - "Create documentation"
    purpose: "Helps determine appropriate detail level and focus areas"

  quality_threshold:
    question: "What minimum confidence level do you require?"
    options:
      - high: "Only findings with 3+ reputable sources"
      - medium: "Findings with 2+ sources, gaps documented"
    default: "high"
```

**Output Directory Verification**:

```yaml
directory_check:
  if_not_exists:
    action: "Request user permission"
    message: "The docs/research/ directory doesn't exist. May I create it to store research outputs? (y/n)"

  if_permission_granted:
    action: "mkdir -p docs/research"
    confirm: "✓ Created docs/research/ directory"

  if_permission_denied:
    action: "Request alternative output location"
    fallback: "Store research in memory and display inline"
```

**Output Artifacts**:
- Research scope document
- Clarification Q&A record
- Output directory confirmed/created
- Success criteria defined

---

### Phase 2: Source Discovery & Validation

**Agent Command**: `*verify-sources`

**Source Discovery Process**:

```
📚 SOURCE DISCOVERY - FINDING REPUTABLE KNOWLEDGE

Execute multi-channel source discovery:

1. Academic Search:
   - Search academic databases (scholar.google.com, arxiv.org)
   - Filter for peer-reviewed sources
   - Check publication date (prefer recent, note if outdated)

2. Official Documentation:
   - Search official docs (docs.{technology}.com)
   - Verify standards bodies (W3C, IEEE, ISO)
   - Check government sources (.gov domains)

3. Industry Leader Content:
   - Search recognized expert sites (martinfowler.com, etc.)
   - Verify author credentials
   - Check community consensus (GitHub stars, references)

4. Technical Documentation:
   - Official API docs
   - Framework/library documentation
   - Version-specific information
```

**Source Validation Workflow**:

```yaml
for_each_potential_source:
  step_1_domain_check:
    action: "Extract domain from URL"
    validation: "Check against trusted-source-domains.yaml"
    outcomes:
      high_reputation: "Proceed to content extraction"
      medium_high_reputation: "Proceed but require additional cross-reference"
      medium_reputation: "Require 3+ cross-references"
      excluded: "Reject and log warning"

  step_2_reputation_scoring:
    academic: 1.0
    official: 1.0
    industry_leaders: 0.8
    technical_documentation: 1.0
    open_source: 1.0
    medium_trust: 0.6

  step_3_metadata_collection:
    required:
      - source_url: "Full URL"
      - domain: "Extracted domain"
      - access_date: "ISO 8601 timestamp"
      - reputation_score: "From scoring rules"
      - source_type: "academic/official/industry/technical/opensource"

  step_4_verification_requirements:
    if_academic:
      - "Check for peer review"
      - "Verify publication venue"
      - "Note author credentials"

    if_official:
      - "Confirm official publication"
      - "Check version/date"
      - "Verify standards compliance"

    if_industry:
      - "Validate author expertise"
      - "Check cross-references"
      - "Verify community consensus"
```

**Quality Gate: Source Validation**:
- ✅ All sources from trusted-source-domains.yaml
- ✅ Average reputation score ≥ 0.80
- ✅ Minimum 3 sources per research topic
- ✅ Excluded domains rejected

**Output Artifacts**:
- Validated source list with reputation scores
- Source metadata collection
- Rejected sources log with reasons

---

### Phase 3: Evidence Collection & Verification

**Agent Command**: `*cross-reference`

**Evidence Collection Process**:

```
🎯 EVIDENCE COLLECTION - EXTRACTING VERIFIED FACTS

Systematic evidence gathering with verification:

For each potential finding:

1. Extract Evidence:
   - Direct quote or specific data point
   - Context and relevance
   - Publication/source information

2. Cross-Reference (Minimum 3 sources):
   Source 1: {finding} from {high-reputation source}
   Source 2: {corroboration} from {independent source}
   Source 3: {verification} from {different source type}

3. Assess Confidence:
   - High: 3+ sources, avg reputation ≥ 0.90, no conflicts
   - Medium: 2-3 sources, avg reputation ≥ 0.70, minor conflicts noted
   - Low: 1-2 sources, reputation ≥ 0.60, significant conflicts

4. Document Conflicts:
   - Note all conflicting information
   - Compare source credibility
   - Present both perspectives with analysis
```

**Cross-Reference Validation**:

```yaml
for_each_major_claim:
  minimum_sources: 3

  cross_reference_requirements:
    source_independence:
      - "Different domains (not all from same site)"
      - "Different source types (academic + official + industry)"
      - "Different publication dates (not all from same year)"

    verification_method:
      direct_confirmation:
        - "Multiple sources state same fact"
        - "Evidence points to same conclusion"

      indirect_confirmation:
        - "Sources cite same primary research"
        - "Findings from different approaches align"

    conflict_handling:
      if_conflicting_sources:
        - "Document all perspectives"
        - "Compare source reputation scores"
        - "Analyze potential bias or context"
        - "Note which is more authoritative and why"

  confidence_assessment:
    high_confidence:
      criteria:
        - sources_count: "≥ 3"
        - avg_reputation: "≥ 0.90"
        - conflicts: "none"
        - cross_reference_quality: "direct confirmation"

    medium_confidence:
      criteria:
        - sources_count: "2-3"
        - avg_reputation: "≥ 0.70"
        - conflicts: "minor, noted"
        - cross_reference_quality: "indirect confirmation acceptable"

    low_confidence:
      criteria:
        - sources_count: "1-2"
        - avg_reputation: "≥ 0.60"
        - conflicts: "significant, documented"
      action: "Note as knowledge gap, recommend further research"
```

**Quality Gate: Evidence Verification**:
- ✅ All major claims have ≥3 source citations
- ✅ Cross-reference performed for each finding
- ✅ Confidence ratings assigned
- ✅ Conflicts documented and analyzed

**Output Artifacts**:
- Evidence collection with citations
- Cross-reference verification matrix
- Confidence assessments
- Conflict analysis documentation

---

### Phase 4: Critical Analysis & Synthesis

**Agent Command**: `*synthesize-findings`

**Critical Analysis Process**:

```
🔬 CRITICAL ANALYSIS - EVALUATING SOURCE RELIABILITY

Systematic bias detection and reliability assessment:

1. Source Bias Analysis:
   - Commercial interests: Check for sponsorship, affiliations
   - Author conflicts: Identify potential conflicts of interest
   - Publication bias: Note if source promotes specific products/services
   - Date relevance: Assess if information is current or outdated

2. Consistency Evaluation:
   - Agreement level: How many sources confirm finding?
   - Divergence patterns: Where do sources disagree?
   - Context dependency: Are differences due to context/use-case?

3. Knowledge Gap Identification:
   - Insufficient evidence: Claims with < 3 reputable sources
   - Conflicting evidence: Contradictions from credible sources
   - Missing information: Areas with no authoritative sources

4. Reliability Scoring:
   - Source reputation + evidence quality + cross-verification
   - Bias assessment (low/medium/high bias detected)
   - Final confidence rating
```

**Synthesis Workflow**:

```yaml
findings_synthesis:
  organize_by_theme:
    - "Group related findings together"
    - "Identify main themes/patterns"
    - "Note relationships between findings"

  assess_overall_quality:
    evidence_strength:
      strong: "Multiple high-reputation sources, direct evidence"
      moderate: "Some high-reputation sources, indirect evidence"
      weak: "Limited sources, circumstantial evidence"

    knowledge_completeness:
      comprehensive: "< 10% knowledge gaps"
      substantial: "10-30% knowledge gaps"
      partial: "> 30% knowledge gaps"

  document_limitations:
    methodology:
      - "Search constraints (time, access)"
      - "Source availability limitations"
      - "Scope boundaries"

    findings:
      - "Knowledge gaps explicitly listed"
      - "Conflicting information noted"
      - "Confidence levels provided"
      - "Recommendations for further research"
```

**Quality Gate: Critical Analysis**:
- ✅ Bias assessment completed for all sources
- ✅ Consistency evaluation performed
- ✅ Knowledge gaps explicitly identified
- ✅ Limitations documented

**Output Artifacts**:
- Bias analysis report
- Consistency evaluation
- Knowledge gap documentation
- Synthesized findings by theme

---

### Phase 5: Documentation & Citation

**Agent Command**: `*cite-sources`

**Documentation Workflow**:

```
📝 DOCUMENTATION - STRUCTURED RESEARCH OUTPUT

Create comprehensive research document with:

1. Executive Summary:
   - 2-3 paragraphs summarizing key findings
   - Overall confidence assessment
   - Main insights and conclusions

2. Research Methodology:
   - Search strategy explanation
   - Source selection criteria
   - Quality standards applied
   - Verification methods used

3. Findings (Structured):
   For each finding:
   - Descriptive title
   - Direct evidence (quote/data)
   - Source citation with URL and access date
   - Confidence rating (high/medium/low)
   - Cross-reference verification notes
   - Brief analysis/context

4. Source Analysis Table:
   | Source | Domain | Reputation | Type | Access Date | Verification |
   |--------|--------|------------|------|-------------|--------------|
   | ...    | ...    | ...        | ...  | ...         | ...          |

5. Knowledge Gaps:
   - What information is missing
   - What was searched
   - Recommendations to address gaps

6. Conflicting Information (if applicable):
   - Different perspectives documented
   - Source credibility comparison
   - Assessment of which is more authoritative

7. Recommendations for Further Research

8. Full Citations (Formatted):
   [1] Author/Org. "Title". Publication. Date. URL. Accessed YYYY-MM-DD.
```

**Output File Creation**:

```yaml
output_file:
  directory: "docs/research/"
  filename_pattern: "{topic}-{timestamp}.md"
  filename_example: "hexagonal-architecture-20250103-143022.md"

  directory_safety_check:
    allowed: "docs/research/ ONLY"
    forbidden:
      - "Any parent directory (../)"
      - "Absolute paths outside docs/research/"
      - "System directories"
      - "Configuration directories"

  write_process:
    step_1: "Validate output path is within docs/research/"
    step_2: "Apply research_output_template structure"
    step_3: "Populate all sections with findings"
    step_4: "Generate full citations"
    step_5: "Write file to docs/research/{filename}"
    step_6: "Confirm file creation with path"

  error_handling:
    if_directory_not_writable:
      action: "Request permission, try alternative location"

    if_path_validation_fails:
      action: "Deny write, explain restriction, suggest correct path"
```

**Quality Gate: Documentation**:
- ✅ All required sections present
- ✅ Findings properly structured with evidence
- ✅ All sources cited with full metadata
- ✅ Output file created in docs/research/ only
- ✅ Research summary provided to user

**Output Artifacts**:
- Complete research document: docs/research/{topic}-{timestamp}.md
- Research summary with output location
- Citation count and source statistics

---

## Success Criteria

**Research Complete When**:

1. ✅ **Clarification Completed**
   - Research scope clearly defined
   - Quality requirements understood
   - Output location confirmed

2. ✅ **Source Validation Passed**
   - All sources from trusted-source-domains.yaml
   - Average reputation score ≥ 0.80
   - Minimum sources per claim met (≥3 for high confidence)

3. ✅ **Evidence Collection Complete**
   - All findings evidence-backed with citations
   - Cross-reference performed (≥3 sources per major claim)
   - Confidence ratings assigned
   - Conflicts documented and analyzed

4. ✅ **Critical Analysis Done**
   - Bias assessment completed
   - Source reliability evaluated
   - Knowledge gaps identified
   - Limitations documented

5. ✅ **Documentation Generated**
   - Structured markdown with all sections
   - Comprehensive citations with metadata
   - Output file created in docs/research/
   - Research summary provided

6. ✅ **Quality Standards Met**
   - Citation coverage > 95%
   - Source reputation average ≥ 0.80
   - Output path compliance 100% (docs/research/ only)
   - No unsupported claims

---

## Quality Gates

**Pre-Research**:
- [ ] docs/research/ directory exists or permission granted
- [ ] trusted-source-domains.yaml accessible
- [ ] Research scope clearly defined through clarifications
- [ ] Quality threshold set (high/medium confidence)

**During Research**:
- [ ] All sources validated against trusted domains
- [ ] Excluded domains rejected (0 tolerance)
- [ ] Cross-reference performed (≥3 sources per claim)
- [ ] Confidence ratings assigned to all findings

**Post-Research**:
- [ ] All findings have evidence and citations
- [ ] Knowledge gaps explicitly documented
- [ ] Conflicting information analyzed
- [ ] Output file created in docs/research/ ONLY
- [ ] All quality metrics met:
  - Citation coverage > 95%
  - Avg source reputation ≥ 0.80
  - Cross-reference rate 100% for major claims

**Safety Compliance**:
- [ ] No writes outside docs/research/ directory
- [ ] No sensitive data in output
- [ ] All tool access restrictions followed
- [ ] Audit logging complete

---

## Handoff to Next Wave

**Next Agent**: Any 5D-Wave agent can use research findings

**Handoff Package**:
- Research document: docs/research/{topic}-{timestamp}.md
- Research summary with key findings
- Source quality assessment
- Knowledge gaps and limitations
- Recommendations for further research

**Validation**:
- All quality gates passed
- Sources verified from trusted domains
- Evidence-backed findings only
- Output path compliance confirmed

---

## Example Usage

```bash
# User requests research
$ dw-research

# Agent asks clarifications
Nova: "What specific aspect should I research?"
User: "Research hexagonal architecture patterns"

Nova: "What depth of research do you need? (overview/detailed/comprehensive/deep-dive)"
User: "detailed"

Nova: "What types of sources do you prefer? (academic/official/industry/technical_docs)"
User: "academic and official"

Nova: "How will you use this research?"
User: "Inform architecture decision for new microservice"

Nova: "What minimum confidence level do you require? (high/medium)"
User: "high"

# Agent executes research
Nova: "Executing evidence-driven research on hexagonal architecture patterns..."
Nova: "✓ Validated 12 sources against trusted-source-domains.yaml"
Nova: "✓ Cross-referenced findings across 8 high-reputation sources"
Nova: "✓ Generated research document: docs/research/hexagonal-architecture-20250103-143022.md"

# Agent provides summary
Nova: "Research complete! Key findings:
1. Hexagonal architecture (Ports & Adapters) isolates business logic from external concerns [High confidence: 5 academic sources]
2. Primary adapters (drivers) initiate use cases, secondary adapters (driven) are dependencies [High confidence: 4 official sources]
3. Implementation patterns vary by language/framework [Medium confidence: 3 sources, some variation noted]

Full research with citations: docs/research/hexagonal-architecture-20250103-143022.md
Sources consulted: 12 (academic: 5, official: 4, industry: 3)
Average source reputation: 0.92
Knowledge gaps: Real-world performance metrics (limited empirical data)"
```
