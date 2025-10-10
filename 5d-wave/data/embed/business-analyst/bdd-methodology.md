# BDD for Business Analyst: Collaborative Discovery & Requirements Patterns

**Agent**: business-analyst
**Purpose**: Practical guidance for requirements discovery and collaborative specification using BDD
**Research Date**: 2025-10-09
**Sources**: Cucumber.io, Dan North, Liz Keogh, Gojko Adzic, Example Mapping

---

## Core Philosophy: Conversation Over Documentation

### The Fundamental Shift

**Traditional Requirements**: Documents written by BA, thrown over wall to development
**BDD Requirements**: Collaborative discovery through structured conversations with concrete examples

**"If you're not having conversations, you're not doing BDD."** - Liz Keogh

Source: https://lizkeogh.com/2011/09/22/conversational-patterns-in-bdd/ (Accessed 2025-10-09)

**Critical Insight**: BDD is fundamentally about discovering "what we don't know we don't know" through collaborative exploration, not about tools or formats.

---

## The Three Amigos: Collaborative Discovery Pattern

### Who Are The Three Amigos?

**The Three Core Perspectives**:
1. **The Problem Owner** (Product Owner, BA, Domain Expert)
   - Understands business need and desired outcomes
   - Defines acceptance criteria
   - Provides domain knowledge

2. **The Problem Solver** (Developer, Engineer)
   - Understands technical constraints and possibilities
   - Identifies implementation complexity
   - Reveals technical edge cases

3. **The Skeptic** (Tester, QA)
   - Thinks about what could go wrong
   - Identifies edge cases and boundary conditions
   - Challenges assumptions

**Why This Combination Works**: Each role brings unique blindspots to light. Developers think through implementation. Testers spot failure scenarios. Business experts clarify value and context.

Source: https://lizkeogh.com/2015/03/27/what-is-bdd/ (Accessed 2025-10-09)

### Three Amigos Session Structure

**Format**: 25-minute timeboxed collaborative workshop
**Materials**: Index cards (physical or digital), whiteboard
**Output**: Shared understanding captured as scenarios

**Standard Agenda**:
```
1. Read user story aloud (2 min)
   - Establish shared context
   - Clarify story goal

2. Identify acceptance criteria / rules (8 min)
   - What must be true for story to be "done"?
   - What business rules govern this behavior?
   - Capture on blue cards

3. Explore examples for each rule (12 min)
   - Given this rule, what are concrete examples?
   - Are there edge cases or alternatives?
   - Capture on green cards

4. Capture questions (ongoing)
   - What don't we know?
   - What needs research/decision?
   - Capture on red cards

5. Review and summarize (3 min)
   - Is the story well-understood?
   - Are there too many unknowns? (red cards)
   - Is the story too big? (too many rules/examples)
```

Source: https://cucumber.io/blog/bdd/example-mapping-introduction/ (Accessed 2025-10-09)

**Timebox Guidance**: If you can't map a story in ~25 minutes, the story is either:
- Too large (needs splitting)
- Too uncertain (needs more discovery)
- Too complex (team still learning the technique)

Source: https://cucumber.io/blog/bdd/example-mapping-introduction/ (Accessed 2025-10-09)

---

## Example Mapping: Structured Discovery Technique

### The Four Card Types

**Color-Coded System**:
- 🟨 **Yellow Card** (1 per session): User Story
- 🟦 **Blue Cards**: Business Rules / Acceptance Criteria
- 🟩 **Green Cards**: Concrete Examples illustrating rules
- 🟥 **Red Cards**: Questions / Unknowns

### Visual Layout Pattern

```
┌────────────────────────────────────────────┐
│  🟨 User Story: Transfer money between     │
│     my accounts                            │
└────────────────────────────────────────────┘
       │
       ├─ 🟦 Rule: Transfer amount must not exceed source account balance
       │    ├─ 🟩 Example: $500 balance, transfer $400 → succeeds
       │    ├─ 🟩 Example: $500 balance, transfer $500 → succeeds
       │    └─ 🟩 Example: $500 balance, transfer $501 → fails
       │    └─ 🟥 Question: What happens if balance changes during transfer?
       │
       ├─ 🟦 Rule: Both accounts must belong to same customer
       │    ├─ 🟩 Example: Transfer between my checking and savings → succeeds
       │    └─ 🟩 Example: Transfer to my friend's account → requires different flow
       │
       └─ 🟦 Rule: Transfer creates transaction records
            ├─ 🟩 Example: $100 transfer → 2 transactions (debit + credit)
            └─ 🟥 Question: What timezone for transaction timestamps?
```

Source: https://cucumber.io/blog/bdd/example-mapping-introduction/ (Accessed 2025-10-09)

### When to Run Example Mapping

**Optimal Timing**: Every other day, just-in-time before development
- Not too early (requirements might change)
- Not too late (development already started)

**Triggers for Example Mapping**:
- Story about to enter sprint/iteration
- Story has multiple edge cases or rules
- Team uncertain about story scope
- Cross-functional clarification needed

**Skip Example Mapping When**:
- Story is trivial and well-understood
- Story is pure technical refactoring with no behavior change
- Team has strong shared understanding already

---

## Conversational Patterns: Discovering What You Don't Know

### Pattern 1: Context Questioning

**Question Template**:
> "Is there any other context which, when this event happens, will produce a different outcome?"

**Purpose**: Discover edge cases and alternative scenarios

**Example Dialogue**:
```
BA: "When a customer submits an order, the order is confirmed."

Tester (using context questioning): "Is there any other context where submitting
an order produces a different outcome?"

Developer: "What if the item is out of stock?"
BA: "Good point - then the order goes to backorder status."

Tester: "What if the customer's payment method is declined?"
BA: "Then the order is pending payment."

Developer: "What if it's after business hours?"
BA: "Order still confirms immediately - we process 24/7."
```

**Result**: Three rules discovered, each needing examples:
1. Rule: Sufficient inventory → immediate confirmation
2. Rule: Insufficient inventory → backorder status
3. Rule: Payment declined → pending payment status

Source: https://lizkeogh.com/2011/09/22/conversational-patterns-in-bdd/ (Accessed 2025-10-09)

### Pattern 2: Outcome Questioning

**Question Template**:
> "Given this context, when this event happens, is there another outcome that's important?"

**Playful Variation**:
> "If pixies were doing this instead of software, would it be enough?"

**Purpose**: Challenge whether proposed solution is complete

**Example Dialogue**:
```
BA: "When an admin deletes a user account, the account is deleted."

Tester (using outcome questioning): "Is there another outcome that's important?"

Developer: "We should probably log the deletion for audit purposes."

BA: "Right, and we need to notify the user by email."

Tester: "What about the user's data? GDPR requires we delete all personal data."

Developer: "And what about resources owned by that user - documents, uploaded files?"

BA: "Good questions. We need to decide: cascade delete or orphan with ownership transfer?"
```

**Result**: One simple statement revealed five important outcomes to consider.

Source: https://lizkeogh.com/2011/09/22/conversational-patterns-in-bdd/ (Accessed 2025-10-09)

### Pattern 3: Challenging Abstractions with Concrete Examples

**Problem**: Abstract rules don't reveal hidden assumptions

**Technique**: Force concrete examples to expose gaps

**Example**:
```
BA: "User can search for products by category."

Developer: "Can you give me a concrete example?"

BA: "User selects 'Electronics' category."

Tester: "What if the Electronics category has 10,000 products?
What do we show?"

BA: "We'll paginate. Show 20 per page."

Developer: "What's the sorting? Price? Name? Relevance?"

BA: "Hmm, I need to ask stakeholders. That's actually important."
[🟥 Red card: "Default sort order for category browsing?"]
```

**Pattern**: Concrete examples force decisions. Abstract statements hide decisions.

Source: https://gojko.net/2020/03/17/sbe-10-years.html (Accessed 2025-10-09)

---

## From User Stories to Scenarios: The Workflow

### Step 1: User Story Format

**Standard Template**:
```
As a [role/persona]
I want [capability]
So that [business value/outcome]
```

**BDD Enhancement - Add Examples Inline**:
```
User Story: Transfer money between accounts

As an account holder
I want to transfer money between my accounts
So that I can manage my finances flexibly

Examples:
- Transfer $100 from checking to savings
- Transfer with insufficient funds → rejection
- Transfer exact balance amount → succeeds
- Transfer between accounts in different currencies → needs conversion

Questions:
- What's the maximum transfer amount?
- Are there transfer fees?
- How long does transfer take to process?
```

### Step 2: Rules Discovery

**Technique**: Ask "What must be true for this story to be done?"

**Example - Transfer Money Story**:

**Rules Identified**:
1. Source account must have sufficient balance
2. Both accounts must belong to authenticated user
3. Transfer amount must be positive and non-zero
4. Transfer creates transaction records for both accounts
5. Account balances update atomically (both or neither)

**How to Find Rules**:
- Ask "What could prevent this from succeeding?"
- Ask "What business constraints apply?"
- Ask "What validations are needed?"
- Ask "What are the system responsibilities?"

### Step 3: Examples for Each Rule

**For Each Rule, Create 2-3 Examples**:
- Typical/happy path example
- Boundary condition example
- Error/alternative path example

**Example - Rule: "Source account must have sufficient balance"**

Examples:
1. 🟩 Balance $500, transfer $300 → succeeds (typical)
2. 🟩 Balance $500, transfer $500 → succeeds (boundary - exact balance)
3. 🟩 Balance $500, transfer $501 → fails "insufficient funds" (error)

**Naming Examples**: Use "friends episode" style names for easy reference:
- "The One Where Balance Is Exact"
- "The One With Insufficient Funds"
- "The One With Negative Transfer Amount"

Source: https://cucumber.io/blog/bdd/example-mapping-introduction/ (Accessed 2025-10-09)

### Step 4: Translate to Given-When-Then

**Example → Scenario Translation**:

**Example Card**: Balance $500, transfer $300 → succeeds
**Scenario**:
```gherkin
Scenario: Successful transfer with sufficient balance
  Given my checking account balance is $500.00
  And my savings account exists
  When I transfer $300.00 from checking to savings
  Then my checking balance is $200.00
  And my savings balance increases by $300.00
  And I receive a confirmation message
```

**Translation Rules**:
- **Given** = Context from example (preconditions, system state)
- **When** = Event/action from example (user action, system trigger)
- **Then** = Outcome from example (observable results, state changes)

---

## Business Outcome Focus: The "Five Whys" Technique

### Ensuring Requirements Connect to Business Value

**Problem**: Teams build features without understanding business value
**Solution**: Apply "Five Whys" to each user story

**Example Dialogue**:
```
Story: "Add export to CSV feature for reports"

Why? "So users can export their data"
Why do users need to export data? "So they can analyze it in Excel"
Why do they need Excel? "Because our reporting doesn't have pivot tables"
Why do they need pivot tables? "To slice data by different dimensions"
Why is that important? "To identify trends and make business decisions"

REAL NEED: Better analytical capabilities, not CSV export
ALTERNATIVE: Add pivot table functionality to our app
```

**BDD Principle**: Focus on behaviors that directly contribute to business results. Challenge features that don't tie to clear outcomes.

Source: Web search - BDD business outcomes focus (Accessed 2025-10-09)

### Acceptance Criteria with Business Value

**Traditional AC** (implementation-focused):
```
- API endpoint accepts POST requests
- Response returns JSON with 201 status
- Data persisted to database
```

**BDD-Style AC** (outcome-focused):
```
- Customer can submit order even when offline
- Order confirmed within 2 seconds
- Customer receives email confirmation
- Order appears in customer's order history immediately
```

**Transformation**: Shift from "system does X" to "user achieves Y"

---

## Handling Ambiguity and Uncertainty

### Red Cards: Making Unknowns Visible

**Red Card Triggers**:
- Question nobody in room can answer
- Decision requiring stakeholder input
- Technical research needed
- Dependency on external team
- Ambiguity in requirements

**Examples of Good Red Cards**:
- 🟥 "What's the character limit for product descriptions?"
- 🟥 "Can users upload PDFs or only images?"
- 🟥 "What happens to orders if payment gateway is down?"
- 🟥 "Do we support international phone number formats?"

**Red Card Resolution Process**:
1. Capture question on red card during session
2. Assign owner (usually BA or Product Owner)
3. Set deadline for resolution (before development starts)
4. Follow-up session if answer reveals new complexity

**Critical Rule**: Never proceed to development with unresolved red cards. Unknowns lead to rework.

### Dealing with "We'll Figure It Out Later"

**Anti-Pattern**: Accepting vague requirements with plan to clarify during development

**BDD Approach**: Use example mapping to surface ambiguity early

**Dialogue Example**:
```
Developer: "We'll just make it configurable and let admins decide."

BA: "Let's think through a concrete example. If we have an admin
named Sarah configuring fraud detection..."

Developer: "She'd set a threshold, like $1000."

Tester: "What if she sets it to $0? Or negative? Or $999,999,999?"

Developer: "We'd need validation rules."

BA: "And what if two admins set conflicting values?"

Developer: "We'd need permissions and audit log."

Tester: "This is more complex than we thought. Maybe we need
a simpler approach first?"
```

**Outcome**: Concrete examples revealed hidden complexity, enabling better decision-making.

---

## Confirmation Bias Reduction Through Examples

### The Bias Problem

**Confirmation Bias**: Tendency to seek examples that confirm our assumptions and ignore contradictory evidence

**How It Manifests in Requirements**:
- BA documents only happy path scenarios
- Stakeholders describe ideal customer behavior
- Team assumes users will use feature as intended

### BDD Defense: Deliberate Adversarial Thinking

**Technique 1: Reverse Assumptions**
```
Assumption: "Users will fill out the form correctly"

Reverse Examples:
- User submits empty form
- User enters "asdfasdf" in every field
- User copy-pastes 50,000 characters into text field
- User submits form 100 times in 10 seconds (bot)
```

**Technique 2: "Evil User" Persona**
```
Create anti-persona: "Malicious Mike" or "Careless Cathy"

Mike's behaviors:
- Tries SQL injection in input fields
- Attempts to access other users' data
- Manipulates URLs to bypass validation
- Uses developer tools to modify client-side code

Cathy's behaviors:
- Never reads instructions
- Clicks "back" button mid-process
- Refreshes page constantly
- Has JavaScript disabled
```

**Technique 3: Example Mapping Diversity**

**For Each Rule, Force Examples From Three Categories**:
1. ✅ Happy path (typical success)
2. ⚠️ Edge case (boundary, unusual but valid)
3. ❌ Error case (invalid, failure condition)

**Example**:
```
Rule: Password must be strong

✅ Happy: "MyP@ssw0rd123" → accepted
⚠️ Edge: "Aa1!" (minimum length) → accepted or rejected?
⚠️ Edge: "🔐🔑🗝️💻🖥️⌨️" (all emojis) → accepted or rejected?
❌ Error: "password" → rejected "too weak"
❌ Error: "" (empty) → rejected "required"
```

**Forcing diversity prevents echo chamber thinking.**

Source: https://lizkeogh.com/2012/09/21/the-deliberate-discovery-workshop/ (Accessed 2025-10-09)

---

## Stakeholder Communication Techniques

### Speaking Multiple Languages

**Challenge**: Different stakeholders speak different languages
- **Business**: Revenue, customers, market share, ROI
- **Technical**: Architecture, APIs, data models, performance
- **User**: Tasks, workflows, pain points, goals

**BDD Bridge**: Scenarios use business domain language that translates to technical implementation

**Example Scenario - Multi-Audience**:
```gherkin
Scenario: High-value customer receives priority support

  Given I am a customer with "Platinum" membership
  And I submit a support ticket with priority "urgent"
  When the support team reviews new tickets
  Then my ticket appears at the top of the queue
  And I receive automated acknowledgment within 1 minute
```

**What Each Stakeholder Sees**:
- **Executive**: "Platinum customers get priority" (business rule)
- **Customer**: "My urgent issues get fast response" (user benefit)
- **Developer**: "Filter tickets by membership tier and priority, sort accordingly" (implementation)
- **Tester**: "Verify queue ordering and SLA compliance" (test case)

**Key**: Same scenario, multiple valid interpretations at different abstraction levels.

### Facilitating Discovery Sessions

**BA's Role as Facilitator**:

**Before Session**:
- [ ] Prepare user story in advance
- [ ] Identify and invite three amigos
- [ ] Set up materials (cards, whiteboard, shared doc)
- [ ] Time-box session (25 minutes)
- [ ] Share story with attendees beforehand

**During Session**:
- [ ] Keep energy high and focused
- [ ] Enforce timeboxing strictly
- [ ] Capture all contributions visibly (cards/board)
- [ ] Encourage equal participation (draw out quiet members)
- [ ] Challenge abstractions with "give me a concrete example"
- [ ] Use context and outcome questioning patterns
- [ ] Make red cards visible and explicit
- [ ] Prevent solution discussion (focus on understanding problem)

**After Session**:
- [ ] Take photo of card layout (if physical)
- [ ] Transcribe to scenarios (Given-When-Then)
- [ ] Assign owners to red cards
- [ ] Schedule follow-up if needed
- [ ] Share scenarios with stakeholders for validation

**Signs of Good Facilitation**:
- All three amigos contributed actively
- At least one new insight discovered
- Questions (red cards) made explicit
- Concrete examples captured, not just abstract rules
- Session stayed within timebox

**Signs of Poor Facilitation**:
- One person dominated conversation
- No new insights (just confirming assumptions)
- Abstract discussion without concrete examples
- Session ran over time significantly
- Team left with confusion, not clarity

---

## Requirements Gathering Through BDD Lens

### Discovery Over Elicitation

**Traditional Approach**: BA elicits requirements from stakeholders, documents them, delivers to team

**BDD Approach**: Cross-functional team discovers requirements together through examples

**Shift in Mindset**:
```
FROM: "Tell me what you want"
TO:   "Let's explore concrete examples together"

FROM: "Here's what the system will do"
TO:   "Here's what the user can achieve"

FROM: "These are the requirements"
TO:   "This is our shared understanding"
```

### Discovery Workshop Format

**Participant Mix** (6-8 people ideal):
- Product Owner / Business Stakeholder
- Business Analyst (facilitator)
- 2-3 Developers
- 1-2 Testers
- Subject Matter Expert (optional, for complex domains)

**Workshop Structure** (90 minutes):
```
1. Context Setting (10 min)
   - Present business problem/opportunity
   - Share background research
   - Define success criteria

2. Story Writing (15 min)
   - Brainstorm user stories
   - Write on yellow cards
   - Prioritize for deep-dive

3. Example Mapping - Round 1 (25 min)
   - Top priority story
   - Rules, examples, questions
   - Scenario drafting

4. Break (5 min)

5. Example Mapping - Round 2 (25 min)
   - Second priority story
   - Focus on differences from first story

6. Review & Next Steps (10 min)
   - Summarize discoveries
   - Assign red card owners
   - Schedule follow-up if needed
```

**Output**:
- 2-3 stories mapped with examples
- 10-15 scenarios drafted
- Red cards assigned for resolution

---

## Documentation: Structured Business Requirements

### From Examples to Requirements Document

**BDD Hierarchy**:
```
Business Capability (Epic)
└── Feature (Theme)
    └── User Story
        └── Acceptance Criteria (Rules)
            └── Scenarios (Examples)
```

**Example Structure**:

```markdown
# Customer Account Management (Capability)

## Account Transfers (Feature)

### User Story: Transfer Between Own Accounts

**As** an account holder
**I want** to transfer money between my accounts
**So that** I can manage my finances flexibly

**Business Rules**:
1. Transfer amount must not exceed source account balance
2. Both accounts must belong to authenticated user
3. Transfer amount must be positive
4. Transfer creates audit trail

**Acceptance Criteria**:

✅ **Given** sufficient balance, **when** valid transfer, **then** succeeds
✅ **Given** insufficient balance, **when** transfer attempt, **then** rejected
✅ **Given** accounts belong to different users, **when** transfer attempt, **then** rejected

**Scenarios**:

#### Scenario 1: Successful transfer with sufficient balance
```gherkin
Given my checking account balance is $500.00
And my savings account balance is $100.00
When I transfer $200.00 from checking to savings
Then my checking balance is $300.00
And my savings balance is $300.00
And a transfer record is created
```

#### Scenario 2: Transfer rejected due to insufficient funds
[... detailed scenario ...]

**Questions**:
- 🟥 Maximum transfer amount? (Owner: Product, Due: 2025-10-15)
- 🟥 Transfer fees apply? (Owner: Finance, Due: 2025-10-15)
```

**Key Components**:
1. Business capability → why this feature exists
2. User story → who, what, why
3. Business rules → constraints and policies
4. Acceptance criteria → high-level pass/fail conditions
5. Scenarios → concrete examples with Given-When-Then
6. Questions → unresolved items with owners and deadlines

### Living Documentation Principle

**Traditional Docs**: Written once, become outdated quickly
**Living Documentation**: Generated from executable scenarios, always current

**Benefits**:
- Requirements and tests are same artifact
- Documentation updates automatically when behavior changes
- Stakeholders see real system behavior, not outdated specs
- Examples serve as regression suite

**Tool Support**:
- Cucumber/SpecFlow: Generate HTML reports from scenarios
- Serenity BDD: Hierarchical living documentation with test results
- pytest-bdd: Markdown reports with scenario outcomes

Source: https://serenity-bdd.github.io/docs/reporting/living_documentation (Accessed 2025-10-09)

---

## Bridging Business and Technical Perspectives

### Translation Challenges

**Business Language**:
- Customer, Order, Invoice, Shipment
- High-level workflows and outcomes
- Regulatory compliance, business policies

**Technical Language**:
- REST APIs, database tables, microservices
- Low-level operations and algorithms
- Performance, scalability, security

**BDD's Role**: Use ubiquitous language (domain terms) that both audiences understand

### Example: Same Requirement, Two Languages

**Business Perspective**:
```
"When a customer places an order, we need to verify their
payment method and reserve inventory, then send them a
confirmation email with expected delivery date."
```

**Technical Perspective**:
```
"POST /api/orders triggers payment validation via Stripe API,
decrements inventory counters in Products table, publishes
OrderCreated event to RabbitMQ, which triggers email service
worker to send confirmation via SendGrid."
```

**BDD Scenario (Shared Language)**:
```gherkin
Scenario: Customer places order with valid payment
  Given I have a valid payment method on file
  And the product "Laptop X200" is in stock
  When I place an order for "Laptop X200"
  Then my order is confirmed
  And I receive a confirmation email
  And the product inventory is reserved
```

**What This Achieves**:
- Business stakeholder recognizes the workflow
- Developer understands what services to integrate
- Tester knows what to verify
- **No translation loss** - shared understanding

### Domain-Driven Design Integration

**BDD and DDD Together**:
- **Ubiquitous Language**: Terms used in scenarios = terms in code
- **Bounded Contexts**: Features organized by business domains
- **Domain Events**: When steps often describe domain events

**Example - E-commerce Bounded Context**:

**Ubiquitous Language**:
- Order (not "transaction")
- Catalog (not "product database")
- Cart (not "session shopping items")
- Fulfillment (not "shipping process")

**Scenario Using Ubiquitous Language**:
```gherkin
Scenario: Customer adds out-of-stock item to cart
  Given the product "Widget" is out of stock
  When I attempt to add "Widget" to my cart
  Then "Widget" is not added to my cart
  And I see message "This item is currently unavailable"
  And I am offered similar in-stock alternatives
```

**Code Uses Same Language**:
```python
class Cart:
    def add_product(self, product: Product) -> AddToCartResult:
        if not product.is_in_stock():
            return AddToCartResult.failure(
                reason="Product is currently unavailable",
                alternatives=self.catalog.find_similar_in_stock(product)
            )
```

**Benefit**: BA's scenarios directly inform developer's domain model. No "translation tax."

---

## Specification by Example: Key Principles

### Principle 1: Derive Scope From Goals

**Start With Business Goal**, not solution:

**Wrong Starting Point**: "We need a search feature"
**Right Starting Point**: "Customers can't find products easily, losing sales"

**Discovery Questions**:
- What's the business impact? (quantify: lost revenue, support tickets)
- What user behavior would achieve the goal? (find products faster)
- What's the minimum valuable solution? (category browsing vs. full-text search)

**Outcome**: User stories with clear business value, prioritized by impact

Source: https://gojko.net/books/specification-by-example/ (Accessed 2025-10-09)

### Principle 2: Specify Collaboratively

**Pattern**: Cross-functional collaboration, not serial handoffs

**Traditional Workflow** (Serial):
```
Business → Requirements Doc → BA → Specs → Dev → Code → QA → Testing
         (3 days)           (2 days)      (5 days)    (3 days)
```

**BDD Workflow** (Collaborative):
```
Business + BA + Dev + QA → Discovery Workshop → Scenarios
(2 hours)                                      (shared understanding)
         ↓
    Development (with scenarios guiding implementation)
         ↓
    Automated Tests (scenarios executed)
```

**Time Savings**: Hours instead of days for requirements
**Quality Improvement**: Shared understanding prevents rework

Source: https://gojko.net/2020/03/17/sbe-10-years.html (Accessed 2025-10-09)

### Principle 3: Illustrate Using Examples

**Abstract Rule** (Hard to understand):
```
"Payment processing must handle various payment methods
with appropriate validation."
```

**Concrete Examples** (Clear understanding):
```
Example 1: Credit card 4111-1111-1111-1111 with CVV 123 → accepted
Example 2: Credit card 4111-1111-1111-1111 with CVV 12 → rejected (invalid CVV)
Example 3: Expired credit card (exp 01/2020) → rejected (expired)
Example 4: PayPal account with verified email → accepted
Example 5: PayPal account with unverified email → requires verification step
```

**Examples Reveal**:
- Different payment types need different validation
- CVV format varies by card type
- Expiration checking is required
- PayPal has verification workflow
- Each rule needs implementation

Source: https://gojko.net/books/specification-by-example/ (Accessed 2025-10-09)

### Principle 4: Refine Specification

**Iterative Refinement Process**:
1. **First Pass**: High-level examples in workshop
2. **Refinement**: Add detail, remove ambiguity
3. **Automation**: Translate to executable scenarios
4. **Feedback**: Run scenarios, discover gaps
5. **Update**: Refine based on feedback

**Example Evolution**:

**First Pass** (Workshop):
```
"Customer transfers money between accounts"
```

**Refinement** (Adding Detail):
```
Scenario: Transfer with sufficient balance
  Given account A has $500
  When transfer $200 to account B
  Then account A has $300
```

**Automation Feedback** (Developer Questions):
```
- What's account B's starting balance?
- Is there a transfer fee?
- What confirmation does user receive?
- How long does transfer take?
```

**Final Refinement**:
```gherkin
Scenario: Instant transfer with sufficient balance
  Given my checking account has balance $500.00
  And my savings account has balance $100.00
  When I transfer $200.00 from checking to savings
  Then the transfer completes instantly
  And my checking balance is $300.00
  And my savings balance is $300.00
  And I receive confirmation "Transfer successful"
  And no fees are charged
```

**Pattern**: Iterative refinement driven by concrete questions from implementation.

---

## Example Mapping Anti-Patterns and Solutions

### Anti-Pattern 1: No Examples, Just Rules

**Problem**: Blue cards with no green cards underneath

**Example**:
```
🟦 Rule: User must be authenticated
🟦 Rule: Order must be valid
🟦 Rule: Payment must succeed
```

**Why It's Bad**: Rules are abstract. No shared understanding of "valid order" or "payment succeeds."

**Solution**: Force concrete examples for each rule
```
🟦 Rule: Order must be valid
  🟩 Example: Order with in-stock items → valid
  🟩 Example: Order with out-of-stock items → invalid
  🟩 Example: Order with negative quantities → invalid
  🟩 Example: Order total exceeds credit limit → invalid (wait, new rule!)
```

### Anti-Pattern 2: Too Many Rules (Story Too Big)

**Indicator**: More than 5-6 blue cards for single story

**Example**: "User registration" story with 12 rules:
- Email validation
- Password strength
- Username uniqueness
- Terms acceptance
- Email verification
- Profile completion
- ... (6 more rules)

**Solution**: Split story into smaller stories
```
Story 1: Basic registration (email, password, terms)
Story 2: Email verification
Story 3: Profile setup
```

**Rule of Thumb**: If example mapping takes >30 minutes, story is too big.

### Anti-Pattern 3: Implementation Details in Examples

**Problem**: Examples describe "how" not "what"

**Bad Example**:
```gherkin
When I POST to /api/users with {"email": "test@example.com"}
Then response status is 201
And database users table has new row
```

**Good Example**:
```gherkin
When I register with email "test@example.com"
Then my account is created
And I receive a welcome email
```

**Difference**: Good example describes user-observable behavior, not implementation.

### Anti-Pattern 4: Ignoring Red Cards

**Problem**: Proceeding to development with unresolved questions

**Example**:
```
Story ready for development with red cards:
🟥 "What's the maximum file upload size?"
🟥 "Do we support international addresses?"
🟥 "What happens if external API is down?"
```

**Consequence**: Developers make assumptions, rework required when stakeholders clarify later

**Solution**: **Red cards are blockers.** Resolve before development or explicitly defer with risk acceptance.

---

## Practical Checklist for Business Analysts

### Before Discovery Session
- [ ] User story prepared (Who, What, Why)
- [ ] Three amigos identified and invited
- [ ] Background research completed
- [ ] Materials ready (cards, whiteboard, tools)
- [ ] Timebox communicated (25 minutes)
- [ ] Pre-reading shared with participants

### During Discovery Session
- [ ] Story goal clarified upfront
- [ ] Rules captured on blue cards
- [ ] Each rule has 2-3 concrete examples (green cards)
- [ ] Questions captured on red cards
- [ ] Context questioning used to find edge cases
- [ ] Outcome questioning used to ensure completeness
- [ ] All three amigos contributed
- [ ] Timebox respected (ended at 25 min or less)

### After Discovery Session
- [ ] Cards photographed / documented
- [ ] Scenarios written in Given-When-Then format
- [ ] Red cards assigned owners and deadlines
- [ ] Scenarios shared with stakeholders for validation
- [ ] Scenarios shared with team for estimation
- [ ] Acceptance criteria clear to all roles

### Scenario Quality Gates
- [ ] Uses business domain language (ubiquitous language)
- [ ] Describes behavior, not implementation
- [ ] Focused on single behavior per scenario
- [ ] Concrete examples with specific values
- [ ] Readable by non-technical stakeholders
- [ ] Each scenario traces to business rule
- [ ] Success and failure cases covered
- [ ] Edge cases and boundary conditions included

### Documentation Standards
- [ ] Hierarchical organization (Capability → Feature → Story → Scenario)
- [ ] Business value stated for each feature
- [ ] Rules extracted and documented explicitly
- [ ] Examples linked to rules
- [ ] Questions tracked with resolution status
- [ ] Living documentation generated from scenarios
- [ ] Stakeholder sign-off obtained

---

## Integration with Development Workflow

### BDD in Agile Sprint

**Sprint Planning**:
- Stories presented with example mapping results
- Scenarios used for estimation
- Red cards resolved before commitment

**Development**:
- Scenarios guide TDD (outer loop)
- Developers write unit tests (inner loop)
- Scenarios executed as acceptance tests

**Review**:
- Demo using scenarios as script
- Stakeholders validate against examples
- Living documentation shared

**Retrospective**:
- Review scenario quality
- Identify missed examples
- Improve discovery process

### Continuous Refinement

**Pattern**: Example mapping is continuous, not one-time

**Triggers for Re-mapping**:
- Scenario fails during development (assumption wrong)
- New edge case discovered
- Stakeholder changes requirement
- Production bug reveals gap in examples

**Process**:
1. Capture new learning as example
2. Add to scenario suite
3. Update living documentation
4. Share with team

**Principle**: **Examples accumulate over time**, becoming comprehensive specification and regression suite.

---

## Key Takeaways for Business Analysts

1. **Conversation over documentation** - BDD is about discovery, not deliverables
2. **Three Amigos collaboration** - cross-functional discovery prevents gaps
3. **Example Mapping technique** - structured 25-minute workshop format
4. **Concrete examples reveal assumptions** - abstract rules hide complexity
5. **Context and outcome questioning** - patterns to discover edge cases
6. **Red cards are blockers** - never proceed with unresolved questions
7. **Business outcome focus** - apply "Five Whys" to ensure value
8. **Ubiquitous language** - bridge business and technical perspectives
9. **Iterative refinement** - examples evolve through feedback
10. **Living documentation** - scenarios are specification AND tests
11. **Confirmation bias defense** - force diverse examples (happy, edge, error)
12. **Facilitate, don't dictate** - BA guides discovery, doesn't prescribe solution

---

## Collaboration Patterns Summary

### Effective Discovery Conversation
```
BA: "Let's explore with a concrete example..."
Developer: "What if [technical constraint]?"
Tester: "I'm thinking about [edge case]..."
BA: "Good point, let's capture that as an example."
Product Owner: "The business rule is actually [clarification]."
BA: "So we have a new rule. Let me add a blue card..."
```

### Ineffective Discussion (Anti-Pattern)
```
BA: "The system will do X, Y, and Z."
Developer: "OK, I'll build that."
Tester: "I'll test it when it's done."
(No examples, no questions, no shared understanding)
```

**Difference**: Effective conversations are explorative. Ineffective conversations are prescriptive.

---

## References

- Cucumber BDD Documentation: https://cucumber.io/docs/bdd/ (Accessed 2025-10-09)
- Example Mapping Introduction (Matt Wynne): https://cucumber.io/blog/bdd/example-mapping-introduction/ (Accessed 2025-10-09)
- Liz Keogh - What is BDD?: https://lizkeogh.com/2015/03/27/what-is-bdd/ (Accessed 2025-10-09)
- Liz Keogh - Conversational Patterns in BDD: https://lizkeogh.com/2011/09/22/conversational-patterns-in-bdd/ (Accessed 2025-10-09)
- Liz Keogh - Deliberate Discovery Workshop: https://lizkeogh.com/2012/09/21/the-deliberate-discovery-workshop/ (Accessed 2025-10-09)
- Gojko Adzic - Specification by Example: https://gojko.net/books/specification-by-example/ (Accessed 2025-10-09)
- Gojko Adzic - Specification by Example 10 Years Later: https://gojko.net/2020/03/17/sbe-10-years.html (Accessed 2025-10-09)
- Dan North - Introducing BDD: https://dannorth.net/blog/introducing-bdd/ (Referenced in search results, Accessed 2025-10-09)
- Web Search - BDD Business Outcomes Focus: Multiple sources (Accessed 2025-10-09)
- Web Search - Three Amigos Collaboration: Multiple sources (Accessed 2025-10-09)
- Web Search - BDD Stakeholder Involvement: Multiple sources (Accessed 2025-10-09)
