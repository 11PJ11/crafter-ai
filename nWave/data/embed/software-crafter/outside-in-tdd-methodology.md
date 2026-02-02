# Outside-In TDD Knowledge

## Double-Loop TDD
outer=ATDD(business behavior, hours-days to green)
inner=UTDD(implementation, minutes to green, RED->GREEN->REFACTOR)
Outer stays red while inner cycles. Outer drives WHAT to build, inner drives HOW.
Never build components not needed by actual user scenarios (prevents speculative generality).

## Outside-In vs Inside-Out
Inside-Out(Classic/bottom-up): discovers collaborators through refactoring. TDD guides design completely.
Outside-In(London/top-down/mockist): knows collaborators upfront, mocks them, implements each moving inward.
Use Outside-In when: architectural boundaries known (hexagonal), program to interface not implementation.

## ATDD Lightweight (Hendrickson 2024)
Original 2008 heavyweight ATDD "too heavyweight for most real teams." Updated approach:
- Few G/W/T examples, not many. No attempt to hook to automation unless high-value.
- Separate requirements (communicate intent) from tests (verify behavior).
- Smallest subset of team with relevant skills. Not whole-team synchronous.
- Value = shared understanding, not executable specs.

## BDD Integration
BDD emerged from Outside-In TDD. Given(context)->When(action)->Then(outcome) maps to outside-in mindset.
BDD reframes TDD as design/specification technique, not just testing. More accessible to stakeholders.
Gherkin: structured format bridging technical/non-technical. Use pragmatically - automate only where high value.

## Classical vs Mockist Verification
Classical TDD: real objects, state verification, less coupled to implementation, survives refactoring better.
Mockist TDD: mocks for objects with behavior, behavior verification, lighter setup, more coupled to impl.
Best practice: combine strategically. Behavior verification at layer boundaries, state verification within layers.

## Test Doubles Taxonomy (Meszaros)
Dummy: passed but never used. Fake: working impl with shortcuts (in-memory DB). Stub: predefined answers.
Spy: stub that records interactions. Mock: pre-programmed with expectations for behavior verification.
Choose type by need: mock for interaction design, stub when don't care about interaction, fake for integration bridge.

## Outside-In Development Workflow (Bache)
1. Write Guiding Test (acceptance) from user perspective - thick slice of functionality
2. Start at top-level entry point, design collaborating classes incrementally
3. Use mocks to experiment with interfaces/protocols
4. As each layer implemented, move to previously mocked collaborators, TDD again
5. Never build what isn't needed for actual user scenarios

## Test Through Public Interfaces Only
Test only public API of SUT. Never test private methods directly.
If private method complex enough to need separate testing -> extract to own class with public interface.
Tests knowing internal implementation = brittle during refactoring.

## Unit of Behavior (not Unit of Code)
Test = story about the problem your code solves. Granularity related to stakeholder needs.
A unit of behavior may span multiple classes. Key question: "Can you explain this test to a stakeholder?"
If not, you're testing implementation details not behavior.

## Hexagonal Architecture and Testing
Ports(interfaces) designed through acceptance tests. Adapters implement ports.
Domain core: test with real objects (classical TDD).
Adapters: test in isolation mocking the core (mockist TDD).
Clear separation enables fast unit tests + reliable integration tests.
Core logic testable without mocking web servers or databases.
