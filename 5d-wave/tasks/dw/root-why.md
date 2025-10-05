---
agent-activation:
  required: true
  agent-id: root-cause-analyzer
  agent-name: "Sage"
  agent-command: "*investigate-root-cause"
  auto-activate: true
---

**⚠️ AGENT ACTIVATION REQUIRED**

This task requires the **Sage** agent (root-cause-analyzer) for execution.

**To activate**: Type `@root-cause-analyzer` in the conversation.

Once activated, use the agent's `*help` command to see available operations.

---

# ROOT-WHY: Toyota 5 Whys Multi-Causal Root Cause Analysis

## Overview

Execute systematic root cause analysis using Toyota's enhanced 5 Whys technique with multi-causal investigation and evidence-based validation for complex system failures and architectural decisions.

## Mandatory Pre-Execution Steps

1. **Problem Definition**: Clear problem statement with observable symptoms
2. **Root Cause Analyzer Activation**: Activate root-cause-analyzer (Sage) with Toyota methodology
3. **Evidence Collection Setup**: Establish data collection and validation procedures

## Execution Flow

### Phase 1: Enhanced 5 Whys Foundation

**Primary Agent**: root-cause-analyzer (Sage)
**Command**: `*investigate-root-cause`

**Toyota 5 Whys Enhanced Methodology**:

```
🔍 ROOT-WHY INVESTIGATION - MULTI-CAUSAL ANALYSIS

Philosophy: "The basis of Toyota's scientific approach - by repeating why five times,
the nature of the problem as well as its solution becomes clear." - Taiichi Ohno

ENHANCED FEATURES:
- Multi-causal investigation at each WHY level
- Parallel investigation branches for complex problems
- Evidence-based validation for each causal chain
- Cross-validation between multiple root causes
- Comprehensive solution addressing ALL identified causes

Toyota methodology enhanced for complex software systems.
```

**Multi-Causal Investigation Framework**:

```yaml
enhanced_5_whys_methodology:
  multi_causal_approach:
    principle: "Complex issues often have multiple contributing root causes"
    implementation: "Investigate ALL observable symptoms and conditions"
    validation: "Each cause branch continues through all 5 WHY levels"
    outcome: "Multiple root causes acceptable and expected"

  parallel_investigation:
    principle: "Follow each WHY level cause through complete analysis"
    implementation: "Branch investigation for each identified cause"
    validation: "Cross-cause validation ensures no contradictions"
    outcome: "Comprehensive coverage of all contributing factors"

  evidence_requirements:
    principle: "Each WHY level must have verifiable evidence"
    implementation: "Support each claim with concrete data"
    validation: "Backwards chain validation from root cause to symptom"
    outcome: "Complete audit trail of causal reasoning"

  completeness_validation:
    principle: "Are we missing any contributing factors?"
    implementation: "Ask completeness question at each WHY level"
    validation: "All symptoms explained by collective root causes"
    outcome: "No missing causal factors in final analysis"
```

### Phase 2: Systematic Problem Investigation

**Agent Command**: `*analyze-symptoms`

**Multi-Causal Investigation Process**:

#### WHY Level 1: Direct Symptom Investigation

```yaml
why_level_1_symptoms:
  investigation_approach:
    - "Document ALL observable symptoms and immediate conditions"
    - "Identify multiple direct causes if they exist"
    - "Gather concrete evidence for each observed symptom"
    - "Avoid assumption-based reasoning without evidence"

  evidence_collection:
    - "Error logs and system messages"
    - "Performance metrics and monitoring data"
    - "User reports and behavioral observations"
    - "System state at time of problem occurrence"

  multiple_causes_handling:
    - "Investigate each observable symptom separately"
    - "Identify all immediate contributing conditions"
    - "Document evidence for each identified cause"
    - "Prepare for parallel investigation in WHY Level 2"

multi_causal_example_level_1:
  problem: "Application deployment failing with 'path not found' error"

  cause_a: "File exists but wrong context - Windows vs WSL paths"
  evidence_a: "File visible in Windows explorer but not accessible via WSL commands"

  cause_b: "Permission denied in some execution contexts"
  evidence_b: "Error logs show permission failures in specific user contexts"

  cause_c: "Timing issues with asynchronous file operations"
  evidence_c: "Intermittent failures correlate with concurrent file access"
```

#### WHY Level 2: Context Analysis

```yaml
why_level_2_context:
  investigation_approach:
    - "Analyze why each WHY Level 1 condition exists"
    - "Branch investigation for each identified cause"
    - "Cross-validate context factors between causes"
    - "Identify systemic conditions enabling multiple failures"

  context_factors:
    - "Environmental conditions and configurations"
    - "System architecture and component interactions"
    - "Process workflows and operational procedures"
    - "User behavior patterns and usage contexts"

multi_causal_example_level_2:
  cause_a_context: "Why wrong context?"
  evidence_a: "Process spawned from Windows host executing in WSL environment"

  cause_b_context: "Why permission issues?"
  evidence_b: "Different user contexts between host system and container"

  cause_c_context: "Why timing issues?"
  evidence_c: "Asynchronous file operations without proper synchronization primitives"
```

#### WHY Level 3: System Analysis

```yaml
why_level_3_system:
  investigation_approach:
    - "Examine why problematic conditions persist in the system"
    - "Analyze system-wide factors enabling multiple failure modes"
    - "Identify interconnections between multiple causes"
    - "Evaluate system design and architectural factors"

  system_factors:
    - "System architecture and design decisions"
    - "Component integration and communication patterns"
    - "Error handling and recovery mechanisms"
    - "Monitoring and detection capabilities"

multi_causal_example_level_3:
  cause_a_system: "Why context mismatch persists?"
  evidence_a: "No context translation layer in system architecture"

  cause_b_system: "Why permission mismatches persist?"
  evidence_b: "No unified permission model across execution environments"

  cause_c_system: "Why timing issues persist?"
  evidence_c: "No synchronization primitives in async file operation design"
```

#### WHY Level 4: Design Analysis

```yaml
why_level_4_design:
  investigation_approach:
    - "Analyze why problems weren't anticipated in design"
    - "Examine design assumptions and blind spots"
    - "Identify all contributing design decisions"
    - "Evaluate design process and validation methods"

  design_factors:
    - "Original design assumptions and constraints"
    - "Design validation and testing approaches"
    - "Stakeholder involvement and requirements gathering"
    - "Design review and approval processes"

multi_causal_example_level_4:
  cause_a_design: "Why no context translation anticipated?"
  evidence_a: "Single-environment design assumption during architecture phase"

  cause_b_design: "Why no unified permission model?"
  evidence_b: "Simplified security model assumption in original design"

  cause_c_design: "Why no synchronization primitives?"
  evidence_c: "Synchronous execution model assumed during design"
```

#### WHY Level 5: Root Cause Analysis

```yaml
why_level_5_root_causes:
  investigation_approach:
    - "Identify fundamental conditions enabling all symptoms"
    - "Accept multiple root causes for complex problems"
    - "Ensure comprehensive coverage of all contributing factors"
    - "Validate that root causes explain ALL observed symptoms"

  root_cause_validation:
    - "Each root cause must trace to observable symptoms"
    - "Multiple root causes should not contradict each other"
    - "Collective root causes must explain complete problem"
    - "Solutions must address ALL identified root causes"

multi_causal_example_level_5:
  root_cause_1: "Design failure to consider hybrid execution contexts"
  explanation_1: "Leads to context mismatch and path resolution failures"

  root_cause_2: "Insufficient cross-platform security analysis during design"
  explanation_2: "Leads to permission mismatches across environments"

  root_cause_3: "Lack of concurrency considerations in file system operations"
  explanation_3: "Leads to timing issues and race conditions"

  completeness_validation: "All three root causes collectively explain path errors, permission failures, and timing issues"
```

### Phase 3: Evidence-Based Validation

**Agent Command**: `*validate-evidence`

**Evidence Collection and Validation**:

```yaml
evidence_framework:
  quantitative_evidence:
    requirements:
      - "Measurable data supporting each causal claim"
      - "Statistical correlation between causes and symptoms"
      - "Performance metrics and system monitoring data"
      - "Error rates and failure pattern analysis"

    validation_criteria:
      - "Data reproducibility and consistency"
      - "Statistical significance of correlations"
      - "Measurement methodology documentation"
      - "Baseline comparisons and trend analysis"

  qualitative_evidence:
    requirements:
      - "Expert testimony and stakeholder observations"
      - "Process documentation and workflow analysis"
      - "Historical incident reports and lessons learned"
      - "Architectural documentation and design rationale"

    validation_criteria:
      - "Source credibility and expertise validation"
      - "Consistency across multiple sources"
      - "Triangulation with quantitative data"
      - "Bias recognition and mitigation"

  backwards_chain_validation:
    methodology:
      - "Start from each root cause"
      - "Trace forward through WHY levels to symptoms"
      - "Verify each causal link has supporting evidence"
      - "Ensure complete path from root cause to observable problem"

    validation_requirements:
      - "Every causal link must be independently verifiable"
      - "No gaps in causal reasoning chain"
      - "Evidence supports causal relationship, not just correlation"
      - "Alternative explanations considered and ruled out"
```

### Phase 4: Comprehensive Solution Development

**Agent Command**: `*develop-solutions`

**Multi-Root-Cause Solution Strategy**:

```yaml
solution_development:
  comprehensive_approach:
    principle: "Solutions must address ALL identified root causes"
    implementation: "Develop integrated solution addressing each root cause"
    validation: "Solution effectiveness measured against each root cause"
    outcome: "Prevention of problem recurrence through complete coverage"

  solution_categories:
    immediate_fixes:
      scope: "Address symptoms and immediate causes"
      timeline: "Hours to days"
      purpose: "Restore system functionality quickly"

    system_improvements:
      scope: "Address systemic issues and WHY Level 3 factors"
      timeline: "Weeks to months"
      purpose: "Improve system resilience and error handling"

    design_enhancements:
      scope: "Address design gaps and WHY Level 4-5 factors"
      timeline: "Months to quarters"
      purpose: "Prevent similar problem classes in future"

    process_improvements:
      scope: "Address organizational and process factors"
      timeline: "Quarters to years"
      purpose: "Improve problem prevention and detection capabilities"

comprehensive_solution_example:
  immediate_fixes:
    fix_1: "Implement context-aware path resolution with wsl bash prefix"
    addresses: "Root Cause 1 - hybrid execution context failure"

    fix_2: "Add unified permission validation across environments"
    addresses: "Root Cause 2 - cross-platform security gaps"

    fix_3: "Implement proper synchronization for async file operations"
    addresses: "Root Cause 3 - concurrency consideration lack"

  system_improvements:
    improvement_1: "Design cross-platform abstraction layer"
    addresses: "System-wide context translation needs"

    improvement_2: "Implement unified security model"
    addresses: "Cross-environment permission consistency"

    improvement_3: "Add comprehensive async operation management"
    addresses: "Concurrency and timing issue prevention"

  design_enhancements:
    enhancement_1: "Multi-environment design validation process"
    addresses: "Design assumption validation gap"

    enhancement_2: "Cross-platform security analysis methodology"
    addresses: "Security design review inadequacy"

    enhancement_3: "Concurrency analysis integration in design reviews"
    addresses: "Concurrent operation design oversight"
```

### Phase 5: Prevention Strategy Implementation

**Agent Command**: `*implement-prevention`

**Kaizen Integration and Continuous Improvement**:

```yaml
kaizen_integration:
  problem_prevention:
    methodology: "Use findings to prevent future similar occurrences"
    implementation:
      - "Design review checklists incorporating lessons learned"
      - "Architectural decision records documenting considerations"
      - "Testing strategies addressing identified risk patterns"
      - "Monitoring and alerting for early problem detection"

  organizational_learning:
    knowledge_capture:
      - "Document complete investigation methodology and findings"
      - "Create searchable knowledge base of root cause analyses"
      - "Develop pattern libraries for similar problem types"
      - "Train team members on enhanced 5 Whys methodology"

    process_improvements:
      - "Integrate root cause analysis into incident response"
      - "Establish regular problem analysis and prevention reviews"
      - "Create early warning systems based on identified patterns"
      - "Implement feedback loops for solution effectiveness validation"

  continuous_validation:
    effectiveness_monitoring:
      - "Track recurrence rates of similar problems"
      - "Monitor effectiveness of implemented solutions"
      - "Measure prevention strategy success metrics"
      - "Validate root cause analysis accuracy over time"

    methodology_refinement:
      - "Improve investigation techniques based on experience"
      - "Enhance evidence collection and validation methods"
      - "Refine multi-causal analysis approaches"
      - "Update training and documentation based on lessons learned"
```

## Advanced Root Cause Analysis Techniques

### Cross-Validation Methods

```yaml
cross_validation_techniques:
  multiple_investigator_validation:
    approach: "Independent investigation by different team members"
    validation: "Compare findings and reconcile differences"
    benefit: "Reduces investigator bias and blind spots"

  timeline_correlation_analysis:
    approach: "Map all symptoms and causes to timeline"
    validation: "Verify temporal relationships support causal claims"
    benefit: "Identifies sequence dependencies and correlation patterns"

  similar_incident_analysis:
    approach: "Compare with historical similar incidents"
    validation: "Identify common patterns and root cause similarities"
    benefit: "Validates findings against known problem patterns"

  stakeholder_perspective_integration:
    approach: "Gather input from all affected stakeholders"
    validation: "Triangulate findings across different viewpoints"
    benefit: "Ensures comprehensive problem understanding"
```

### Complex System Analysis Patterns

```yaml
complex_system_patterns:
  emergent_behavior_analysis:
    focus: "Problems arising from component interactions"
    methodology: "Analyze system behavior at different scales"
    validation: "Test hypotheses in controlled environments"

  cascade_failure_investigation:
    focus: "How single failures propagate through system"
    methodology: "Map failure propagation paths and amplification points"
    validation: "Simulate cascade scenarios and validate predictions"

  feedback_loop_identification:
    focus: "Positive and negative feedback loops affecting problem"
    methodology: "Model system dynamics and loop interactions"
    validation: "Test loop breaking interventions"

  constraint_analysis:
    focus: "System constraints that enable or prevent problems"
    methodology: "Theory of Constraints applied to problem analysis"
    validation: "Test constraint removal or modification effects"
```

## Output Artifacts

### Investigation Documentation

1. **ROOT_CAUSE_ANALYSIS.md** - Complete 5 Whys investigation with evidence
2. **EVIDENCE_COLLECTION.md** - All supporting data and validation methods
3. **CAUSAL_ANALYSIS.md** - Multi-causal investigation findings
4. **SOLUTION_STRATEGY.md** - Comprehensive solution addressing all root causes
5. **PREVENTION_PLAN.md** - Prevention strategy and implementation roadmap

### Organizational Learning

1. **LESSONS_LEARNED.md** - Key insights and organizational knowledge
2. **METHODOLOGY_GUIDE.md** - Enhanced 5 Whys methodology documentation
3. **PATTERN_LIBRARY.md** - Problem patterns and solution templates
4. **TRAINING_MATERIALS.md** - Educational resources for team development

### Process Improvement

1. **PROCESS_IMPROVEMENTS.md** - Organizational process enhancements
2. **MONITORING_STRATEGY.md** - Early warning and detection systems
3. **VALIDATION_FRAMEWORK.md** - Solution effectiveness measurement
4. **CONTINUOUS_IMPROVEMENT.md** - Kaizen integration and methodology refinement

## Quality Gates

### Investigation Quality Validation

- [ ] **Multi-Causal Analysis**: All contributing causes identified and validated
- [ ] **Evidence-Based Reasoning**: Each WHY level supported by verifiable evidence
- [ ] **Backwards Chain Validation**: Complete causal chains from root causes to symptoms
- [ ] **Cross-Validation**: Findings validated through multiple investigation methods
- [ ] **Completeness Check**: All observed symptoms explained by identified root causes

### Solution Quality Validation

- [ ] **Comprehensive Coverage**: Solutions address ALL identified root causes
- [ ] **Implementation Feasibility**: Solutions are practical and achievable
- [ ] **Effectiveness Validation**: Solution success metrics defined and measurable
- [ ] **Prevention Integration**: Solutions include prevention strategy for similar problems
- [ ] **Organizational Learning**: Findings integrated into organizational knowledge base

### Toyota Methodology Compliance

- [ ] **Systematic Approach**: Structured investigation methodology followed
- [ ] **Evidence-Based**: All conclusions supported by concrete data
- [ ] **Kaizen Integration**: Findings used for continuous improvement
- [ ] **Prevention Focus**: Solutions address fundamental issues, not just symptoms
- [ ] **Backwards Validation**: Root cause → symptom chains independently verifiable

## Success Criteria

- Complete multi-causal root cause analysis following Toyota methodology
- All contributing root causes identified with supporting evidence
- Comprehensive solution strategy addressing all identified causes
- Prevention strategy implemented to avoid similar future problems
- Organizational learning captured and integrated into processes
- Investigation methodology validated and refined for future use
- Quality gates passed with evidence-based validation

## Failure Recovery

If root cause analysis fails:

1. **Incomplete Investigation**: Continue evidence collection and analysis
2. **Contradictory Evidence**: Re-examine assumptions and validate data sources
3. **Solution Ineffectiveness**: Reassess root causes and develop alternative solutions
4. **Prevention Failures**: Strengthen monitoring and early detection systems
5. **Methodology Issues**: Refine investigation techniques and training

## Integration with 5D-Wave Methodology

### Root Cause Analysis Applications

```yaml
discuss_integration:
  requirements_analysis: "Root cause analysis of requirements gaps and conflicts"
  stakeholder_alignment: "Investigate communication and collaboration failures"

design_integration:
  architecture_analysis: "Root cause analysis of architectural issues and risks"
  technology_validation: "Investigate technology choice risks and limitations"

distill_integration:
  test_analysis: "Root cause analysis of test failures and quality issues"
  acceptance_validation: "Investigate acceptance criteria gaps and ambiguities"

develop_integration:
  implementation_analysis: "Root cause analysis of development issues and blockers"
  quality_investigation: "Investigate code quality problems and technical debt"

demo_integration:
  production_analysis: "Root cause analysis of production issues and failures"
  stakeholder_feedback: "Investigate user adoption and satisfaction issues"
```

## Methodology Completion

**Enhanced Toyota 5 Whys methodology successfully executed with multi-causal investigation, evidence-based validation, comprehensive solution development, and organizational learning integration for systematic problem prevention.**
