# DIVIO Documentation System: Documentarian Agent Specification Guide

**Purpose**: Distilled, actionable knowledge for designing and implementing a documentarian agent that understands and applies DIVIO principles effectively.

**Target Audience**: Solution architects, software engineers, and product designers creating documentation systems and agents.

---

## DIVIO Core Model: Four Documentation Types

The DIVIO system is built on a single insight: there are exactly **four types of documentation**, each serving distinct user needs and requiring different writing approaches.

### The Four Types (with agent responsibilities)

#### 1. Tutorials (Learning-Oriented)
- **User need**: Learn and get started
- **Content focus**: Guided, hands-on introduction
- **Key characteristic**: Pedagogical; instructor-led; prioritizes confidence building
- **Agent responsibility**:
  - Enforce: Must include step-by-step guidance
  - Prevent: Avoid assuming prior knowledge; avoid problem-oriented approach
  - Validate: Confirm new users can follow without external context

#### 2. How-to Guides (Task-Oriented)
- **User need**: Accomplish a specific task
- **Content focus**: Goal-directed step-by-step instructions
- **Key characteristic**: Assumes baseline knowledge; concentrates on specific objective
- **Agent responsibility**:
  - Enforce: Assume reader knows basics; focus on goal achievement
  - Prevent: Don't re-explain fundamentals; avoid comprehensive coverage of all scenarios
  - Validate: Confirm task completion is the measurable outcome

#### 3. Technical Reference (Information-Oriented)
- **User need**: Look up specific information
- **Content focus**: Accurate, organized details about APIs, functions, components
- **Key characteristic**: Concise, factual; serves as lookup material
- **Agent responsibility**:
  - Enforce: Completeness and accuracy; automated reference validation
  - Prevent: Avoid narrative explanation; avoid incomplete API documentation
  - Validate: CI/CD quality gates (spelling, formatting, style compliance)

#### 4. Explanation (Understanding-Oriented)
- **User need**: Understand concepts and reasoning
- **Content focus**: Context, background, design decisions, architecture
- **Key characteristic**: Addresses "why" and conceptual foundations
- **Agent responsibility**:
  - Enforce: Include reasoning and context; explain design decisions
  - Prevent: Avoid pure machinery description; avoid task-focused approach
  - Validate: Confirm conceptual understanding is achievable from content

### Critical Pattern: The Collapse Problem

**Warning**: Documentation types have a "natural gravitational pull" to merge into each other.

**When collapse happens**:
- Content becomes confused and loses clarity
- Documentation fails to serve any audience effectively
- Maintenance becomes increasingly difficult

**Agent prevention strategy**:
- Flag content mixing multiple types in same section
- Validate separation of concerns
- Suggest restructuring when types merge

---

## Architecture: The 2x2 Adjacency Model

The four types arrange in a matrix:

```
        Practical             Theoretical
Study:  Tutorials             Explanations
Work:   How-to Guides         Reference
```

**Navigation implication**: Adjacent types should be linked contextually:
- Tutorials → How-to Guides (progression from learning to working)
- How-to Guides ↔ Reference (working context, both practical)
- Reference ↔ Explanations (both informational depth)
- Explanations → Tutorials (both study-oriented)

**Agent responsibility**: Implement cross-referencing that follows this adjacency pattern.

---

## Quality Standards & Measurement

### The Six Core Quality Characteristics

All documentation must be evaluated against these measurable criteria:

1. **Accuracy**: Factually correct, current, technically sound
2. **Completeness**: All necessary topics covered; nothing important omitted
3. **Clarity**: Easy to understand; logical flow; good organization
4. **Consistency**: Uniform terminology, formatting, structure across documents
5. **Correctness**: Proper grammar, spelling, punctuation
6. **Usability**: Users can efficiently achieve their goals

**Agent responsibility**: Implement automated checks for each characteristic.

### Quantifiable Metrics

**Readability** (automated):
- Flesch Reading Ease Score: target 70-80 range for technical content
- Tools: Automated readability checkers

**Content quality** (measured):
- Error rate: Count of typos, grammatical mistakes, factual errors, technical inaccuracies
- Completeness rate: Percentage of necessary topics included
- Consistency score: Terminology usage compliance, formatting adherence

**User satisfaction** (collected):
- Net Promoter Score (NPS): Recommendation likelihood
- Customer Satisfaction (CSAT): Satisfaction with documentation
- Customer Effort (CES): Ease of finding/using content

### Implementation Reference: Django's CI Approach

Django implements automated quality gates:
- Spelling validation
- Code block formatting checks
- reStructuredText style validation (trailing whitespace, line length, structure)
- All checks must pass before documentation merges

**Agent pattern**: Implement similar CI/CD integration for quality enforcement.

---

## User Journey & Navigation Strategy

### Documentation in User's Journey

Users need different documentation types at different journey stages:

1. **Entry/Learning Phase**:
   - Users need: Tutorials
   - Navigation: Clear path to getting started
   - Agent role: Surface tutorial resources first

2. **Working/Task Phase**:
   - Users need: How-to guides + Reference
   - Navigation: Quick lookup for specific tasks
   - Agent role: Provide contextual reference material and task guides

3. **Understanding Phase**:
   - Users need: Explanations
   - Navigation: Conceptual depth and reasoning
   - Agent role: Link to architectural and design context

### Information Architecture Principles

**Core principles**:
- Intuitive hierarchy: Users understand category relationships
- Plain language: Use simple terms for headings/labels; avoid jargon
- Visual prominence: Navigation is distinct from content
- Logical connections: Readers understand topic relationships

**Cross-referencing best practices**:
- Use descriptive link text that accurately reflects content
- Provide links to both more basic (prerequisites) and advanced (extensions) information
- Implement automated cross-reference updating when content changes

---

## Implementation Tools

### Primary Documentation Generators

#### Sphinx (Industry Standard for Complex APIs)
- **Strengths**: Automatic API documentation, multiple output formats (HTML, PDF, ePub), mature ecosystem
- **Best for**: Large projects with extensive API documentation (Python, Django, Flask)
- **Markup**: reStructuredText
- **Developer experience**: Requires `make html` rebuild; slower iteration

#### MkDocs (Industry adoption trending)
- **Strengths**: Hot-reload development server, cleaner UI, accessibility, modern adoption
- **Best for**: Developer-focused teams prioritizing experience (Google, SAP, Uber, Pydantic)
- **Markup**: Markdown (simpler, more accessible)
- **Developer experience**: Automatic refresh on file changes; faster iteration

#### Read the Docs Platform
- **Role**: Hosting and automation layer
- **Supports**: Sphinx, MkDocs, Jupyter Book
- **Capabilities**: Git integration, automated building, version management, development version hiding

**Agent recommendation**: Choose based on project characteristics:
- API-heavy project → Sphinx
- Team prioritizing experience → MkDocs + Material theme

---

## Style Guides & Consistency

### Style Guide Adoption Strategy

**Best practice**: Don't create proprietary style guides. Instead:
1. Adopt established guide (Google Style Guide or Microsoft Writing Style Guide)
2. Create supplemental terminology guide only if needed for project-specific terms
3. Maintain consistency across all documentation

### Style Guide Components

- Voice and tone: Brand personality and formality level
- Structure: Document templates and hierarchy patterns
- Technical conventions: Code formatting, screenshot standards, diagram specs
- Grammar mechanics: Capitalization, hyphenation, serialization conventions
- Terminology: Consistent terminology for technical concepts

**Agent responsibility**: Enforce style guide adherence through automated linting and rules.

---

## Maintenance & Versioning

### Documentation Lifecycle Management

**Version control basics**:
- Use consistent naming conventions (first step)
- Include both version number and date
- Maintain changelog documenting all modifications
- Create archiving policy for old versions

**Update triggers**:
- Scheduled review cycles (time-based)
- System upgrades or new features
- Breaking changes
- Community feedback

**Maintenance workflow**:
1. Update documentation
2. Communicate changes appropriately
3. Run quality validation (if major update)
4. Archive outdated versions
5. Track changes with editor name, timestamp, modification summary

### Automation Integration

**CI/CD tooling** (GitHub Actions, CircleCI, Jenkins):
- Automated quality gate checking
- Version synchronization with codebase
- Automated changelog generation
- Broken link detection

**Agent responsibility**: Integrate with CI/CD for automated quality assurance and enforcement.

---

## User Feedback Integration

### Feedback Collection

**Feedback metrics**:
- Net Promoter Score (NPS)
- Customer Satisfaction Score (CSAT)
- Customer Effort Score (CES)

**Collection methods**:
- In-documentation feedback forms
- User analytics (page engagement, task success rates)
- Support ticket analysis
- Community forum feedback

### Feedback-Driven Improvement

**Process**:
1. Categorize feedback to identify trends
2. Map feedback to user behavior using analytics
3. Prioritize improvements based on impact and feasibility
4. Track updates through version control
5. Measure outcomes

**Agent responsibility**: Collect feedback signals and surface improvement opportunities.

---

## Documentarian Agent: Core Responsibilities

### 1. Documentation Type Enforcement
- Validate each piece of content matches its intended type (tutorial/how-to/reference/explanation)
- Flag content mixing multiple types inappropriately
- Prevent the "collapse problem"
- Suggest restructuring when types merge

### 2. Quality Assurance
- Enforce the six core characteristics (accuracy, completeness, clarity, consistency, correctness, usability)
- Implement automated metrics (readability scoring, error detection)
- Run CI/CD quality gates before publication
- Track quality trends over time

### 3. User Journey Optimization
- Map documentation types to user journey stages
- Implement cross-referencing following the 2x2 adjacency model
- Suggest navigation improvements based on user flow
- Surface appropriate documentation type for user context

### 4. Style & Consistency
- Enforce adopted style guide
- Validate terminology consistency
- Check formatting compliance
- Flag deviations from established standards

### 5. Maintenance & Versioning
- Track documentation version currency
- Monitor for outdated content
- Integrate with CI/CD for automated validation
- Maintain change audit trails

### 6. Feedback & Measurement
- Collect user satisfaction metrics
- Identify documentation gaps from user feedback
- Recommend improvements based on usage data
- Measure outcomes of documentation updates

---

## Key Insights for Implementation

### Most Impactful Pattern
The four-type separation is the single highest-impact pattern. Organizations that respect this distinction immediately benefit, even with incomplete implementations. Do not collapse types.

### Real-World Validation
The DIVIO/Diátaxis approach is documented in use at:
- Django (official framework documentation)
- Gatsby (open-source documentation redesign)
- Vonage (enterprise communications platform)
- Cloudflare (infrastructure provider)
- Hundreds of additional projects

### Automation Opportunity
Documentation quality enforcement works best when automated through CI/CD pipelines. Django's model (automated spelling, formatting, style checks before merge) is evidence-based best practice.

### Tool Selection Won't Define Success
Success is determined by adherence to the four-type model and quality enforcement, not tool choice. Both Sphinx and MkDocs support DIVIO implementation effectively; choose based on team needs, not architectural constraints.

### User Feedback Loop is Essential
The framework is most effective when integrated with user feedback collection and measurement. Track outcomes of documentation changes; use data to inform priorities.

---

## Next Steps for Agent Design

1. **Model implementation**: Implement the four documentation types as core data types in the agent
2. **Quality rules**: Encode the six characteristics as validation rules
3. **Separation enforcement**: Implement content type classification and cross-type mixing detection
4. **CI/CD integration**: Design agent to work within documentation build pipelines
5. **Metrics collection**: Build feedback collection and measurement capabilities
6. **User journey mapping**: Implement navigation optimization based on user stage
7. **Measurement**: Track agent effectiveness through documentation quality metrics and user satisfaction

---

## Essential References

- **Official DIVIO documentation**: https://docs.divio.com/documentation-system/
- **Diátaxis framework**: https://diataxis.fr/
- **Write the Docs community**: https://www.writethedocs.org/
- **Django documentation standards**: https://docs.djangoproject.com/en/dev/internals/contributing/writing-documentation/
- **Google Developer Style Guide**: https://developers.google.com/style
- **Read the Docs best practices**: https://docs.readthedocs.com/platform/stable/guides/best-practice/index.html
