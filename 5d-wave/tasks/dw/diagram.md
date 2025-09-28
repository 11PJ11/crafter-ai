# DIAGRAM: Visual Architecture Lifecycle Management and Evolution Tracking

## Overview
Execute comprehensive visual architecture lifecycle management through dynamic diagram generation, evolution tracking, and stakeholder communication using architecture-diagram-manager integration.

## Mandatory Pre-Execution Steps
1. **Architecture Context Establishment**: Complete architecture design and component identification
2. **Architecture Diagram Manager Activation**: Activate architecture-diagram-manager (Archer)
3. **Visual Lifecycle Infrastructure**: Establish diagram generation and evolution tracking systems

## Execution Flow

### Phase 1: Visual Architecture Foundation
**Primary Agent**: architecture-diagram-manager (Archer)
**Command**: `*create-diagrams`

**Visual Architecture Lifecycle Management**:
```
📊 DIAGRAM WAVE - VISUAL ARCHITECTURE LIFECYCLE

Comprehensive visual representation and evolution tracking:
- Dynamic diagram generation from architecture definitions
- Real-time evolution tracking throughout development
- Stakeholder-specific visualization and communication
- Automated synchronization with implementation reality
- Visual validation of architectural compliance

Visual architecture enables understanding and communication at all levels.
```

**Core Visual Architecture Principles**:
```yaml
visual_architecture_principles:
  stakeholder_communication:
    purpose: "Enable effective communication across different stakeholder groups"
    implementation: "Multiple diagram types for different audiences and purposes"
    validation: "Stakeholder feedback and comprehension validation"

  implementation_synchronization:
    purpose: "Maintain visual accuracy with actual implementation"
    implementation: "Automated diagram generation from code and configuration"
    validation: "Continuous synchronization and divergence detection"

  evolution_tracking:
    purpose: "Document and visualize architectural changes over time"
    implementation: "Version-controlled diagrams with change tracking"
    validation: "Historical analysis and trend identification"

  architectural_validation:
    purpose: "Visual validation of architectural compliance and patterns"
    implementation: "Automated compliance checking against visual standards"
    validation: "Architecture review and pattern adherence verification"
```

### Phase 2: Comprehensive Diagram Generation
**Agent Command**: `*generate-architecture-views`

**Multi-View Architecture Visualization**:
```yaml
diagram_categories:
  system_context_diagrams:
    purpose: "Show system boundaries and external interactions"
    audience: ["Business Stakeholders", "Product Managers", "Executives"]
    content:
      - "System boundaries and scope definition"
      - "External systems and integration points"
      - "User types and interaction patterns"
      - "Data flows and communication protocols"

  component_architecture_diagrams:
    purpose: "Show internal system structure and component relationships"
    audience: ["Architects", "Senior Developers", "Technical Leads"]
    content:
      - "Major components and their responsibilities"
      - "Component interfaces and dependencies"
      - "Data flow between components"
      - "Technology stack and platform choices"

  deployment_architecture_diagrams:
    purpose: "Show infrastructure and deployment topology"
    audience: ["DevOps Engineers", "Infrastructure Teams", "Operations"]
    content:
      - "Infrastructure components and topology"
      - "Deployment environments and configurations"
      - "Network architecture and security zones"
      - "Scaling and redundancy strategies"

  sequence_diagrams:
    purpose: "Show interaction flows and message passing"
    audience: ["Developers", "Integration Teams", "QA Engineers"]
    content:
      - "User workflow interactions"
      - "API call sequences and protocols"
      - "Error handling and exception flows"
      - "Performance critical paths"

  data_architecture_diagrams:
    purpose: "Show data structures, flows, and persistence"
    audience: ["Data Architects", "Database Administrators", "Developers"]
    content:
      - "Data models and entity relationships"
      - "Data flow and transformation pipelines"
      - "Storage technologies and partitioning"
      - "Data governance and compliance requirements"
```

### Phase 3: Dynamic Diagram Generation
**Agent Command**: `*implement-dynamic-generation`

**Automated Diagram Generation Pipeline**:
```yaml
generation_pipeline:
  source_analysis:
    code_analysis:
      - "Parse source code for component structure"
      - "Extract interface definitions and dependencies"
      - "Identify design patterns and architectural styles"
      - "Map business logic to architectural components"

    configuration_analysis:
      - "Parse deployment configurations and manifests"
      - "Extract infrastructure definitions and topology"
      - "Identify service registration and discovery patterns"
      - "Map environment-specific configurations"

    documentation_analysis:
      - "Parse architectural decision records (ADRs)"
      - "Extract design rationale and context"
      - "Identify architectural principles and constraints"
      - "Map business requirements to technical components"

  diagram_synthesis:
    template_based_generation:
      - "Apply stakeholder-specific diagram templates"
      - "Customize visualization based on audience needs"
      - "Generate multiple views from single source model"
      - "Ensure consistency across different diagram types"

    content_optimization:
      - "Filter information based on diagram purpose"
      - "Adjust detail level for target audience"
      - "Highlight critical paths and relationships"
      - "Optimize layout for readability and comprehension"

    format_generation:
      - "Generate diagrams in multiple formats (SVG, PNG, PDF)"
      - "Create interactive diagrams with drill-down capabilities"
      - "Generate print-friendly and presentation formats"
      - "Ensure accessibility and responsive design"
```

### Phase 4: Evolution Tracking and Version Control
**Agent Command**: `*track-evolution`

**Architecture Evolution Management**:
```yaml
evolution_tracking:
  change_detection:
    source_monitoring:
      - "Monitor code changes affecting architectural structure"
      - "Track configuration changes in deployment manifests"
      - "Detect new components and interface modifications"
      - "Identify deprecated components and sunset patterns"

    impact_analysis:
      - "Analyze impact of changes on existing diagrams"
      - "Identify affected stakeholders and communication needs"
      - "Assess compliance with architectural principles"
      - "Evaluate security and performance implications"

  version_management:
    diagram_versioning:
      - "Version control all diagrams with semantic versioning"
      - "Tag diagrams with release and milestone information"
      - "Maintain historical versions for reference and rollback"
      - "Generate changelog documentation for diagram evolution"

    baseline_management:
      - "Establish architectural baselines at major milestones"
      - "Track deviations from approved baseline architectures"
      - "Validate changes against architectural governance policies"
      - "Maintain approved reference architectures"

  evolution_analysis:
    trend_identification:
      - "Analyze architectural evolution patterns over time"
      - "Identify recurring change patterns and hotspots"
      - "Track component lifecycle and deprecation trends"
      - "Measure architectural complexity evolution"

    decision_tracking:
      - "Link diagram changes to architectural decision records"
      - "Track rationale and context for architectural changes"
      - "Identify decision consequences and validation outcomes"
      - "Maintain traceability from requirements to implementation"
```

### Phase 5: Stakeholder Communication and Validation
**Agent Command**: `*facilitate-communication`

**Stakeholder-Specific Communication Strategy**:
```yaml
communication_strategy:
  executive_communication:
    diagram_focus:
      - "High-level system context and business value"
      - "Technology investment and strategic alignment"
      - "Risk mitigation and compliance demonstration"
      - "Resource allocation and timeline visualization"

    presentation_format:
      - "Executive summary dashboards"
      - "Strategic roadmap visualization"
      - "Risk and compliance heat maps"
      - "Investment and ROI tracking charts"

  technical_communication:
    diagram_focus:
      - "Detailed component architecture and interfaces"
      - "Implementation patterns and technology choices"
      - "Performance characteristics and optimization opportunities"
      - "Integration patterns and API specifications"

    presentation_format:
      - "Interactive technical documentation"
      - "Drill-down capability for detailed exploration"
      - "Code-to-diagram traceability links"
      - "Technical decision rationale and alternatives"

  operational_communication:
    diagram_focus:
      - "Deployment topology and infrastructure requirements"
      - "Monitoring and alerting architecture"
      - "Disaster recovery and business continuity"
      - "Security controls and compliance validation"

    presentation_format:
      - "Operational runbooks with visual guides"
      - "Infrastructure as code visualization"
      - "Monitoring dashboard architecture"
      - "Incident response flow diagrams"

  business_communication:
    diagram_focus:
      - "User journey and workflow visualization"
      - "Business capability mapping to technical components"
      - "Feature delivery pipeline and release planning"
      - "Customer experience and value stream mapping"

    presentation_format:
      - "Business process flow diagrams"
      - "Customer journey visualization"
      - "Feature dependency and delivery timelines"
      - "Business value and impact measurement"
```

### Phase 6: Implementation Reality Synchronization
**Agent Command**: `*synchronize-reality`

**Continuous Synchronization Framework**:
```yaml
synchronization_framework:
  automated_discovery:
    runtime_analysis:
      - "Discover actual component deployment and topology"
      - "Monitor real-time service interactions and dependencies"
      - "Analyze actual data flows and API usage patterns"
      - "Detect configuration drift and deployment variations"

    code_analysis:
      - "Parse codebase for architectural structure changes"
      - "Extract actual interface implementations and contracts"
      - "Identify design pattern usage and architectural styles"
      - "Map business logic distribution across components"

  divergence_detection:
    compliance_monitoring:
      - "Compare actual implementation with designed architecture"
      - "Identify deviations from approved architectural patterns"
      - "Flag violations of architectural principles and constraints"
      - "Detect unauthorized technology introductions"

    quality_assessment:
      - "Measure architectural quality metrics and trends"
      - "Assess technical debt accumulation and impact"
      - "Evaluate security posture and compliance status"
      - "Monitor performance characteristics and bottlenecks"

  correction_strategies:
    automated_updates:
      - "Auto-generate diagrams reflecting current reality"
      - "Update documentation with discovered changes"
      - "Sync configuration management with actual deployment"
      - "Propagate approved changes across all environments"

    governance_enforcement:
      - "Flag unauthorized changes for architectural review"
      - "Trigger approval workflows for significant deviations"
      - "Enforce rollback procedures for non-compliant changes"
      - "Escalate compliance violations to appropriate stakeholders"
```

## Advanced Visual Architecture Patterns

### Interactive Diagram Systems
```yaml
interactive_capabilities:
  drill_down_navigation:
    implementation: "Hierarchical navigation from system to component level"
    features:
      - "Click-through from context to detailed component diagrams"
      - "Zoom capabilities for large-scale system visualization"
      - "Breadcrumb navigation for context preservation"
      - "Cross-reference linking between related diagrams"

  real_time_updates:
    implementation: "Live synchronization with system state"
    features:
      - "Real-time status indicators for component health"
      - "Live performance metrics overlay on architecture"
      - "Dynamic highlighting of active communication paths"
      - "Alert integration for component failures and issues"

  collaborative_annotation:
    implementation: "Multi-stakeholder collaboration on diagrams"
    features:
      - "Stakeholder-specific annotation layers"
      - "Comment threads and discussion tracking"
      - "Approval workflows and sign-off processes"
      - "Change request and review management"

  accessibility_features:
    implementation: "Universal design for diagram accessibility"
    features:
      - "Screen reader compatible diagram descriptions"
      - "High contrast and colorblind-friendly palettes"
      - "Keyboard navigation and interaction support"
      - "Alternative text and semantic markup"
```

### Architecture Compliance Validation
```yaml
compliance_validation:
  pattern_enforcement:
    validation_rules:
      - "Hexagonal architecture port/adapter compliance"
      - "Microservices decomposition and boundary respect"
      - "Security pattern implementation validation"
      - "Performance pattern and optimization compliance"

    automated_checking:
      - "Static analysis of architectural pattern adherence"
      - "Runtime validation of component interactions"
      - "Configuration compliance with architectural standards"
      - "Documentation consistency with implementation"

  quality_metrics:
    architectural_metrics:
      - "Component coupling and cohesion measurements"
      - "Interface complexity and stability tracking"
      - "Dependency cycle detection and resolution"
      - "Architectural technical debt quantification"

    evolution_metrics:
      - "Change frequency and impact analysis"
      - "Component lifecycle and maturity tracking"
      - "Architecture stability and volatility measurement"
      - "Technical decision effectiveness validation"
```

## Output Artifacts

### Visual Architecture Documentation
1. **SYSTEM_CONTEXT.svg** - High-level system boundaries and external interactions
2. **COMPONENT_ARCHITECTURE.svg** - Detailed component structure and relationships
3. **DEPLOYMENT_ARCHITECTURE.svg** - Infrastructure topology and deployment patterns
4. **SEQUENCE_DIAGRAMS.svg** - Critical workflow and interaction patterns
5. **DATA_ARCHITECTURE.svg** - Data models, flows, and persistence patterns

### Evolution and Tracking
1. **ARCHITECTURE_EVOLUTION.md** - Historical changes and evolution analysis
2. **VERSION_HISTORY.md** - Diagram versioning and change tracking
3. **COMPLIANCE_REPORT.md** - Architectural compliance validation results
4. **QUALITY_METRICS.md** - Architecture quality measurements and trends
5. **DECISION_TRACEABILITY.md** - Architectural decisions to implementation mapping

### Stakeholder Communication
1. **EXECUTIVE_DASHBOARD.html** - Executive-level architecture visualization
2. **TECHNICAL_DOCUMENTATION.html** - Interactive technical documentation
3. **OPERATIONAL_RUNBOOKS.html** - Operations-focused visual guides
4. **BUSINESS_PROCESS_MAPS.html** - Business capability and process visualization

### Integration and Automation
1. **GENERATION_PIPELINE.yaml** - Automated diagram generation configuration
2. **SYNCHRONIZATION_CONFIG.yaml** - Reality synchronization settings
3. **COMPLIANCE_RULES.yaml** - Architectural compliance validation rules
4. **STAKEHOLDER_TEMPLATES.yaml** - Audience-specific diagram templates

## Quality Gates

### Visual Architecture Quality Validation
- [ ] **Stakeholder Comprehension**: Diagrams accessible and understandable by target audiences
- [ ] **Implementation Accuracy**: Visual representation matches actual implementation
- [ ] **Evolution Tracking**: Changes properly tracked and documented over time
- [ ] **Compliance Validation**: Architectural patterns and principles visually validated
- [ ] **Cross-Reference Integrity**: Consistent representation across multiple diagram types

### Communication Effectiveness Validation
- [ ] **Audience Alignment**: Diagrams appropriately tailored for specific stakeholder groups
- [ ] **Decision Support**: Visual information effectively supports architectural decisions
- [ ] **Change Communication**: Evolution and changes clearly communicated to stakeholders
- [ ] **Feedback Integration**: Stakeholder feedback incorporated into visual design
- [ ] **Accessibility Compliance**: Universal design principles applied for inclusive access

### Technical Integration Validation
- [ ] **Automated Generation**: Reliable automated diagram generation from source artifacts
- [ ] **Synchronization Accuracy**: Continuous synchronization with implementation reality
- [ ] **Version Control**: Proper versioning and historical tracking implementation
- [ ] **Tool Integration**: Seamless integration with development and deployment tools
- [ ] **Performance Optimization**: Efficient generation and rendering of complex diagrams

## Success Criteria

- Comprehensive visual architecture documentation covering all stakeholder needs
- Automated diagram generation and synchronization with implementation reality
- Effective stakeholder communication through audience-specific visualizations
- Continuous evolution tracking and architectural compliance validation
- Interactive and accessible diagram systems supporting collaborative decision-making
- Integration with development workflow and architectural governance processes
- Quality metrics and validation ensuring architectural excellence

## Failure Recovery

If visual architecture lifecycle management fails:
1. **Generation Issues**: Simplify diagram complexity and improve source parsing
2. **Synchronization Problems**: Strengthen integration with source systems and validation
3. **Stakeholder Communication**: Refine audience analysis and diagram customization
4. **Evolution Tracking**: Improve change detection and version control integration
5. **Compliance Validation**: Enhance pattern recognition and automated checking

## Integration with 5D-Wave Methodology

### Visual Lifecycle Integration
```yaml
discuss_integration:
  stakeholder_alignment: "Visual requirements gathering and stakeholder communication"
  context_documentation: "System context and boundary visualization"

design_integration:
  architecture_visualization: "Design decisions and component structure representation"
  technology_mapping: "Technology choices and integration pattern visualization"

distill_integration:
  acceptance_visualization: "Test scenario and workflow diagram generation"
  business_validation: "Business process and value stream visualization"

develop_integration:
  implementation_tracking: "Code-to-diagram synchronization and validation"
  progress_visualization: "Development progress and component completion tracking"

demo_integration:
  stakeholder_presentation: "Production architecture and business value demonstration"
  operational_documentation: "Deployment and operational procedure visualization"
```

### Cross-Agent Collaboration
```yaml
agent_collaboration:
  solution_architect_integration:
    collaboration: "Architecture design to visual representation translation"
    deliverables: "Design decisions visualized and communicated to stakeholders"

  test_first_developer_integration:
    collaboration: "Implementation progress reflected in architecture diagrams"
    deliverables: "Code structure and test coverage visualization"

  walking_skeleton_helper_integration:
    collaboration: "Minimal implementation and deployment pipeline visualization"
    deliverables: "End-to-end system flow and deployment architecture diagrams"

  mikado_refactoring_specialist_integration:
    collaboration: "Refactoring progress and dependency visualization"
    deliverables: "Mikado graph and refactoring impact visualization"
```

## Methodology Completion

**Visual architecture lifecycle management successfully implemented with comprehensive diagram generation, evolution tracking, stakeholder communication, and implementation synchronization for effective architectural understanding and governance.**