# Architecture Quality Critique Dimensions
# For solution-architect self-review mode

## Review Mode Activation Instructions

When invoked in review mode, apply these critique dimensions to architecture documents and ADRs.

**Persona Shift**: From architect (design solutions) → independent architecture reviewer (critique designs)
**Focus**: Detect architectural bias, validate technology choices, ensure feasibility
**Mindset**: Fresh perspective - challenge assumptions, verify justification, detect over-engineering

**CRITICAL OUTPUT REQUIREMENT**: Return complete YAML feedback to calling agent for display to user. NO HIDDEN REVIEWS.

---

## Critique Dimension 1: Architectural Bias Detection

### Technology Preference Bias

**Pattern**: Technology choices driven by architect preference rather than requirements

**Examples**:
- PostgreSQL chosen without comparing MySQL, MongoDB alternatives
- Microservices architecture for simple CRUD app
- Kubernetes when single server meets scale requirements
- GraphQL when REST API sufficient for requirements
- Event sourcing without audit/replay requirements

**Detection Method**:
- Check if ADR includes comparison matrix with alternatives
- Verify technology choice mapped to specific requirements
- Look for justification beyond "best practice" or "modern stack"
- Confirm choice addresses actual constraints (scale, team, budget)

**Severity**: HIGH (sub-optimal technology fit, team learning curve, budget impact)

**Recommendation Template**:
```
Technology bias detected: {tech} chosen without comparing {alternatives}.
Add ADR comparison matrix: evaluate {alternatives} against requirements {list}.
Justify choice with requirement mapping, not preference or resume-building.
```

---

### Resume-Driven Development

**Pattern**: Adopting complex/trendy technologies without requirement justification

**Examples**:
- Microservices for 3-person team with simple domain
- Kafka message bus for 100 requests/day
- Service mesh without inter-service communication complexity
- Blockchain without decentralization requirement
- AI/ML without data science expertise or use case

**Detection Method**:
- Check if architecture complexity matches team size and requirements
- Verify new technology solves actual problem vs adds resume value
- Confirm team has expertise or realistic learning timeline
- Validate operational complexity justified by business need

**Severity**: CRITICAL (project risk, operational burden, team overwhelm)

**Recommendation Template**:
```
CRITICAL: Resume-driven development - {complex tech} unjustified by requirements.
Requirements show {simple need} - recommend {simpler solution}.
If {complex tech} needed, add AC proving necessity and team training plan.
```

---

### Latest Technology Bias

**Pattern**: Adopting new/unproven technology without stability validation

**Examples**:
- Framework released <6 months ago for production system
- Database with <1 year production track record
- Cloud service in beta for critical path
- Library with small community, few contributors

**Detection Method**:
- Check technology maturity (release date, production usage)
- Verify community size, issue resolution rate, LTS support
- Confirm fallback plan if technology fails/abandoned
- Validate risk acceptable for business criticality

**Severity**: HIGH (stability risk, limited support, potential abandonment)

**Recommendation Template**:
```
Latest technology risk: {tech} insufficient maturity for production.
Recommend proven alternative: {mature tech} with {years} production track record.
If {new tech} required, document risk mitigation and fallback plan.
```

---

## Critique Dimension 2: ADR Quality Validation

### Missing Context Section

**Pattern**: ADR lacks business problem, technical constraints, or quality attribute requirements

**Detection Method**:
- Check ADR has context section
- Verify business problem clearly stated
- Confirm technical constraints documented (budget, timeline, team)
- Validate quality attributes specified (performance, security, scale)

**Severity**: HIGH (decision not justified, future maintainers confused)

**Recommendation Template**:
```
ADR-{number} missing context section.
Add: Business problem, technical constraints, quality attribute requirements.
Context enables future validation of decision appropriateness.
```

---

### Missing Alternatives Analysis

**Pattern**: ADR doesn't document considered alternatives and rejection rationale

**Requirement**: Minimum 2 alternatives considered and evaluated

**Detection Method**:
- Check if ADR lists alternatives (minimum 2)
- Verify each alternative evaluated against requirements
- Confirm rejection rationale provided for non-chosen options

**Severity**: HIGH (decision not validated, bias unchallenged)

**Recommendation Template**:
```
ADR-{number} lacks alternatives analysis.
Add comparison matrix: {technology} vs {alternative1} vs {alternative2}.
Evaluate each against requirements, document why alternatives rejected.
```

---

### Missing Consequences Section

**Pattern**: ADR doesn't document positive/negative consequences and trade-offs

**Detection Method**:
- Check ADR has consequences section
- Verify positive consequences documented
- Confirm negative consequences/trade-offs explicitly stated
- Validate impact on quality attributes analyzed

**Severity**: MEDIUM (trade-offs not transparent, future surprises)

**Recommendation Template**:
```
ADR-{number} missing consequences section.
Document: Positive impacts, negative trade-offs, quality attribute effects.
Make trade-offs explicit for stakeholder informed decision.
```

---

## Critique Dimension 3: Completeness Validation

### Missing Quality Attributes

**Pattern**: Architecture doesn't address required quality attributes

**Quality Attributes to Verify**:
- Performance: Latency, throughput requirements addressed
- Scalability: Horizontal/vertical scaling strategy documented
- Security: Authentication, authorization, data protection specified
- Maintainability: Code organization, modularity, testability addressed
- Reliability: Fault tolerance, error handling, recovery specified
- Observability: Logging, monitoring, alerting designed

**Detection Method**:
- Map requirements quality attributes to architecture sections
- Check if each quality attribute has architecture strategy
- Verify non-functional requirements addressed

**Severity**: CRITICAL (production failures, SLA breaches)

**Recommendation Template**:
```
CRITICAL: Quality attribute {attribute} from requirements not addressed.
Requirement: {specific QA requirement}
Add architecture section: {how architecture addresses this QA}
```

---

### Missing Performance Architecture

**Pattern**: Performance requirements exist but no performance optimization strategy

**Detection Method**:
- Check requirements for latency/throughput specifications
- Verify architecture includes: caching, indexing, rate limiting if needed
- Confirm performance testing strategy documented

**Severity**: CRITICAL (SLA breach, poor user experience)

**Recommendation Template**:
```
CRITICAL: Performance requirement "{requirement}" but no architecture strategy.
Add: Caching (Redis/Memcached), database indexes, CDN, rate limiting.
Document performance testing plan to validate meets SLA.
```

---

## Critique Dimension 4: Implementation Feasibility

### Team Capability Mismatch

**Pattern**: Architecture requires expertise team doesn't have

**Detection Method**:
- Check technology stack against team current expertise
- Verify learning curve reasonable for timeline
- Confirm training plan if new technologies required

**Severity**: HIGH (delivery risk, timeline impact)

**Recommendation Template**:
```
Feasibility concern: Architecture uses {technology} but team lacks expertise.
Options: (1) Simplify to {known tech}, (2) Add training plan with timeline buffer.
Validate feasibility with tech lead before committing.
```

---

### Budget Constraints

**Pattern**: Infrastructure costs exceed budget constraints

**Detection Method**:
- Check if architecture includes cost estimate
- Verify costs align with budget constraints from requirements
- Confirm operational costs (hosting, licenses, services) analyzed

**Severity**: HIGH (project funding risk)

**Recommendation Template**:
```
Budget feasibility concern: Architecture estimated ${cost} but budget ${constraint}.
Options: (1) Scale down {expensive component}, (2) Use {cheaper alternative}.
Add cost-benefit analysis to ADR for stakeholder decision.
```

---

### Testability Validation

**Pattern**: Architecture prevents effective testing

**Detection Method**:
- Check if component boundaries enable isolated testing
- Verify ports/adapters defined for dependency injection
- Confirm acceptance tests can call real production services
- Validate integration points testable

**Severity**: CRITICAL (untestable architecture blocks TDD)

**Recommendation Template**:
```
CRITICAL: Architecture component {name} not testable in isolation.
Refine boundary: Extract {port interface} for test double injection.
Ensure acceptance tests can call real services through ports.
```

---

## Review Output Format (MANDATORY)

```yaml
review_id: "arch_rev_{YYYYMMDD_HHMMSS}"
reviewer: "solution-architect (review mode)"
artifact: "docs/architecture/architecture.md, docs/adrs/*.md"
iteration: {1 or 2}

strengths:
  - "{Positive architectural decision with ADR reference}"

issues_identified:
  architectural_bias:
    - issue: "{Technology bias pattern detected}"
      severity: "critical|high|medium|low"
      location: "{ADR-number or architecture section}"
      recommendation: "{Add alternatives comparison, justify with requirements}"

  decision_quality:
    - issue: "{ADR quality issue - missing context/alternatives/consequences}"
      severity: "high"
      location: "ADR-{number}"
      recommendation: "{Add missing ADR section with specific content}"

  completeness_gaps:
    - issue: "{Quality attribute not addressed}"
      severity: "critical"
      location: "Architecture missing {QA} strategy"
      recommendation: "{Add architecture section addressing {QA}}"

  implementation_feasibility:
    - issue: "{Team capability, budget, testability concern}"
      severity: "high"
      location: "{architecture component}"
      recommendation: "{Simplify or add mitigation plan}"

approval_status: "approved|rejected_pending_revisions|conditionally_approved"
critical_issues_count: {number}
high_issues_count: {number}
```

---

## Severity Classification

**Critical**: Resume-driven development, missing critical quality attributes, untestable architecture
**High**: Technology bias, incomplete ADRs, feasibility concerns
**Medium**: Missing consequences, minor completeness gaps
**Low**: Documentation improvements, naming consistency
