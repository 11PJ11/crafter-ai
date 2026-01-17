# Discovery Methodology

Practitioner guide for evidence-based product discovery. Apply these techniques to validate problems, prioritize opportunities, test solutions, and confirm market viability.

---

## Quick Reference: 4-Phase Workflow

```
PHASE 1              PHASE 2              PHASE 3              PHASE 4
Problem Validation   Opportunity Mapping  Solution Testing     Market Viability
      |                    |                    |                    |
      v                    v                    v                    v
"Is this real?"      "Which matters?"     "Does it work?"      "Viable business?"
```

### Phase Techniques

| Phase | Duration | Min Interviews | Primary Techniques |
|-------|----------|----------------|-------------------|
| 1. Problem | 1-2 weeks | 5 | Mom Test interviews, Job Mapping |
| 2. Opportunity | 1-2 weeks | 10 | Opportunity Solution Tree, Opportunity Algorithm |
| 3. Solution | 2-4 weeks | 5/iteration | Hypothesis testing, Prototypes |
| 4. Viability | 2-4 weeks | 5 + stakeholders | Lean Canvas, 4 Big Risks |

*Duration assumes 2-3 interviews/week pace. Adjust based on customer availability.*

---

## Decision Gates

| Gate | Proceed When | Pivot When | Kill When |
|------|--------------|------------|-----------|
| G1: Problem->Opportunity | 5+ confirm pain + willingness to pay | Problem exists but differs | <20% confirm problem |
| G2: Opportunity->Solution | Top 2-3 opportunities score >8* | New opportunities discovered | All opportunities low-value |
| G3: Solution->Viability | >80% task completion, usability validated | Works but needs refinement | Fundamental usability blocks |
| G4: Viability->Build | All 4 risks addressed, model validated | Model needs adjustment | No viable model found |

*Opportunity Score = Importance + Max(0, Importance - Satisfaction). Scale 1-10 each. Score >8 = underserved need worth pursuing.*

---

## Questioning Toolkit

### Problem Discovery
```
"Tell me about the last time you [encountered this problem]."
"What was the hardest part about that?"
"What did you do about it?"
"What don't you love about that solution?"
"What else have you tried?"
```

### Understanding the Job
```
"What are you ultimately trying to accomplish?"
"Walk me through your process step by step."
"At each step, how do you know if you've succeeded?"
"What slows you down or frustrates you most?"
"What workarounds have you created?"
```

### Probing Assumptions
```
"What makes you believe that?"
"What would need to be true for this to work?"
"What could we assume instead?"
"What would change your mind?"
```

### Testing Commitment
```
"Would you be willing to [specific action]?"
"What would you pay for this?"
"Can you introduce me to someone else with this problem?"
"When can we schedule a follow-up?"
```

### Exploring Implications
```
"If this were solved, what would change?"
"What would that enable you to do?"
"What would happen if we didn't solve this?"
```

---

## Assumption Testing Framework

### Assumption Categories
1. **Value** - Will customers want this?
2. **Usability** - Can customers use this?
3. **Feasibility** - Can we build this?
4. **Viability** - Does this work for our business?

### Risk Scoring

| Factor | Weight | Low (1) | Medium (2) | High (3) |
|--------|--------|---------|------------|----------|
| Impact if wrong | 3x | Minor adjustment | Significant rework | Solution fails |
| Uncertainty | 2x | Have data | Mixed signals | Speculation |
| Ease of testing | 1x | Days, low cost | Weeks, moderate | Months, high cost |

**Risk Score** = (Impact x 3) + (Uncertainty x 2) + (Ease x 1)
- Score >12: Test first
- Score 8-12: Test soon
- Score <8: Test later

### Hypothesis Template
```
We believe [doing X] for [user type] will achieve [outcome].
We will know this is true when we see [measurable signal].
```

### Test Methods by Type

| Assumption | Test Methods |
|------------|--------------|
| Value | Landing page, Fake door, Mom Test interviews |
| Usability | Prototype testing, 5-second tests, Task completion |
| Feasibility | Spike, Technical prototype, Expert review |
| Viability | Lean Canvas review, Stakeholder interviews |

### Decision Rules

| Outcome | Criteria | Action |
|---------|----------|--------|
| PROVEN | >80% meet success criteria | Proceed with confidence |
| DISPROVEN | <20% meet criteria | Pivot or kill |
| INCONCLUSIVE | 20-80% | Increase sample, try different method, segment results |

---

## Success Metrics

*These thresholds align with Decision Gates above. Use metrics to determine proceed/pivot/kill.*

### Phase 1: Problem Validation

| Metric | Threshold |
|--------|-----------|
| Problem confirmation | >60% (3+ of 5 interviews) |
| Frequency | Weekly+ occurrence |
| Current spending | >$0 on workarounds |
| Emotional intensity | Frustration evident |

**Done when**: 5+ interviews, >60% confirmation, can articulate in customer's words, 3+ specific examples.

### Phase 2: Opportunity Mapping

| Metric | Threshold |
|--------|-----------|
| Opportunities identified | 5+ distinct |
| Top opportunity scores | >8 (Importance + Max(0, Importance - Satisfaction)) |
| Job step coverage | 80%+ have identified needs |
| Strategic alignment | Stakeholder confirmed |

**Done when**: OST complete, top 2-3 prioritized, team aligned.

### Phase 3: Solution Testing

| Metric | Threshold |
|--------|-----------|
| Task completion | >80% |
| Value perception | >70% "would use/buy" |
| Comprehension | <10 sec to understand value |
| Key assumptions validated | >80% proven |

**Done when**: 5+ users tested, core flow usable, value + feasibility confirmed.

### Phase 4: Market Viability

| Metric | Threshold |
|--------|-----------|
| 4 Big Risks | All green/yellow |
| Channel validated | 1+ viable |
| Unit economics | LTV > 3x CAC (estimated) |
| Stakeholder sign-off | Legal, finance, ops |

**Done when**: Lean Canvas complete, all risks acceptable, go/no-go documented.

---

## Job Map Example: "Get Clothes Clean"

| Step | Goal | Desired Outcome |
|------|------|-----------------|
| Define | Determine what needs cleaning | Minimize time to identify items needing wash |
| Locate | Gather items and supplies | Minimize time to gather same-wash-type items |
| Prepare | Ready items for washing | Minimize likelihood of missing pocket items |
| Confirm | Verify settings correct | Minimize wrong water temperature likelihood |
| Execute | Run wash cycle | Minimize cycle completion time |
| Monitor | Track progress | Minimize not-knowing-when-done likelihood |
| Modify | Adjust if needed | Minimize effort to re-treat stains |
| Conclude | Complete and store | Minimize time to confirm all items dry |

**Outcome Format**: [Direction] + [Metric] + [Object] + [Clarifier]
Example: "Minimize the time it takes to determine what nutrition is needed"

---

## Anti-Patterns to Avoid

### Critical Conversation Anti-Patterns
| Do NOT | Do Instead |
|--------|-----------|
| Mention your idea early | Talk about their life first |
| Ask about future behavior | Ask about past specifics |
| Accept compliments as validation | Seek commitment |
| Talk more than listen | 80% listening, 20% talking |
| Use formal interview settings | Keep informal |
| Ask leading questions | Use open, non-directive questions |

### Critical Process Anti-Patterns
| Do NOT | Do Instead |
|--------|-----------|
| Skip to solutions | Map opportunity space first |
| Generate variations of same idea | Seek real diversity |
| Validate after building | Validate before code |
| Segment by demographics | Segment by job-to-be-done |
| Build too much before testing | MVP = smallest testable thing |
| Rely only on quant OR qual | Combine both |

### Critical Strategic Anti-Patterns
| Do NOT | Do Instead |
|--------|-----------|
| Pivot on 1-2 signals | Require 5+ signals minimum |
| Only talk to validating customers | Include skeptics, non-users |
| Discovery theater (rubber-stamp) | Track idea-in vs shipped ratio |
| Draw conclusions from 2-3 conversations | 5+ interviews per segment |
| Fall in love with solution | Fall in love with problem |
| Provide answers | Guide discovery through questions |

---

## Technique Selection

| Goal | Use |
|------|-----|
| Validate problem exists | Mom Test + Job Mapping |
| Understand customer needs | Outcome Statements + Opportunity Mapping |
| Prioritize opportunities | OST + Opportunity Algorithm |
| Generate solutions | Ideation with OST constraints |
| Validate solution value | Hypothesis Testing + Prototypes |
| Test usability | Prototype testing, task completion |
| Assess feasibility | 4 Risks framework, spikes |
| Structure business model | Lean Canvas |
| Continuous learning | Weekly customer touchpoints |

---

## Core Principles

1. **Talk less, ask more** - 80% listening
2. **Past behavior over future intent** - "When did you last..."
3. **Problems before solutions** - Validate opportunity space first
4. **Small, fast experiments** - 10-20 ideas tested per week target
5. **Outcomes over outputs** - Not "deliver X" but "achieve Y"
6. **Cross-functional collaboration** - PM + Designer + Engineer together
7. **Validate before building** - All 4 risks addressed pre-code
