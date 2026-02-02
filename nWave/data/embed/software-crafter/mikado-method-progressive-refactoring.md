# Mikado Method and Progressive Refactoring Knowledge

## Mikado Method Core Process
Cycle: Set Goal -> Experiment -> Visualize prerequisites -> Revert to working state.
Treats compilation/test failures as valuable information (reveals prerequisites).
Each failure = prerequisite node in graph. Revert keeps codebase shippable while preserving learning.

## Mikado Graph Structure
DAG: nodes=goals/subgoals, edges=dependencies. Grows organically through experimentation.
Purposes: (1) capture system structure knowledge, (2) enable parallelization of independent branches,
(3) progress tracking via completed nodes, (4) document refactoring rationale for future reference.

## Timeboxed Experimentation
10-min timebox per attempt. If can't make change in 10 min -> too complex, break down further.
Success: commit changes, check off goal, move to next. Fail: revert, identify missing, write subgoals.
Combats sunk cost fallacy. Adjust timebox: 5 min for known code, 15 for exploratory.

## Baby Steps Integration
Baby steps = small increments of working software. Test-commit-integrate every small change.
Mikado provides the roadmap (which steps, what order). Baby steps defines the rhythm (frequent commits).
Combination = "always green" refactoring. Never more than one revert from working system.

## Opportunistic Refactoring + Boy Scout Rule
Opportunistic: improve code "along the way" during feature work. Boy Scout: "leave code better than found."
Use opportunistic for small improvements encountered. Use Mikado when they reveal larger structural problems.
Continuous small improvements prevent technical bankruptcy requiring large-scale refactoring.

## Three Refactoring Timings (Fowler)
1. Preparatory: "Make the change easy, then make the easy change" (Kent Beck). Use Mikado for complex prep.
2. Concurrent: improvements while implementing features. Boy Scout Rule. Near-zero marginal cost.
3. Comprehension: improving code as you learn its purpose. Capture insights in Mikado graph if pattern found.

## Behavior-Preserving Transformations
Refactoring = behavior-preserving change. If behavior changes, it's not refactoring.
Safety net = automated tests (especially acceptance). Modern IDEs automate many provably safe refactorings.
Version control should show "pure refactoring" commits (no behavior change).

## Automated Tool Support
IDE automated refactorings: Rename, Extract Method, Inline, Move (guaranteed safe).
Usually safe: Extract Interface, Change Method Signature. Require judgment: Extract Superclass, Pull Up.
Prioritize automated over manual. IDEs can't automate architectural refactorings -> Mikado adds value here.

## Progressive Refactoring Strategy
Progressive = doesn't block delivering business value. Series of mini-refactors under shared vision.
Key patterns: Strangler Fig (incrementally replace old), Branch by Abstraction (hide behind interface),
Feature Toggles (control migration pace). Mikado documents the migration path.

## Mikado + TDD Integration
1. Write failing test for desired state (outer loop goal)
2. Try to make it pass (inner loop)
3. If blocked by architecture: comment out test, start Mikado graph
4. Work through prerequisites with TDD at each step
5. Uncomment original test - should now pass
Failing test = goal node. Each prerequisite gets its own TDD cycle.

## Continuous Refactoring Culture
Cultural elements needed: permission to refactor without approval, DoD includes refactoring,
tech debt visibility to stakeholders, celebrate improvements not just features.
Mikado graph helps communicate refactoring progress to non-technical stakeholders.

## Safe Refactorings for Legacy Code (without tests)
Safe automated refactorings for untested code: Rename, Extract Variable, Extract Method (if tool-supported),
Introduce Parameter Object, Remove Dead Code (via static analysis).
These can be first Mikado nodes, creating space to add tests before invasive refactoring.
