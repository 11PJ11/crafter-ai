---
description: 'Execute complete DEVELOP wave: baseline → roadmap → split → execute-all → finalize [feature-description]'
argument-hint: '[feature-description] - Example: "Implement user authentication with JWT"'
agent-activation:
  required: false
  agent-parameter: false
  agent-command: "*devop"
---

# DW-DEVELOP: Complete DEVELOP Wave Orchestrator

**Wave**: DEVELOP
**Agent**: DevOp Orchestrator
**Command**: `/nw:develop "{feature-description}"`

## Overview

The DEVELOP wave orchestrator automates the complete feature development lifecycle from problem measurement to production-ready code through disciplined Test-Driven Development with mandatory quality gates.

### What This Command Does

Execute a **complete DEVELOP wave** that orchestrates:

1. **Phase 1-2**: Baseline Creation + Review (measurement baseline)
2. **Phase 3-4**: Roadmap Creation + Dual Review (strategic planning)
3. **Phase 5-6**: Split into Atomic Steps + Review Each Step (task decomposition)
4. **Phase 7**: Execute All Steps (11-phase TDD per step)
5. **Phase 8**: Finalize (archival and cleanup)
6. **Phase 9**: Report Completion

### Key Features

- **Single Command**: One command executes entire wave (`/nw:develop "{description}"`)
- **Smart Skip Logic**: Skips creation if artifacts exist AND are approved
- **Mandatory Quality Gates**: 3 + 3N reviews per feature (N = number of steps)
- **Automatic Retry**: Max 2 attempts for each rejected review
- **Stop on Failure**: Immediate stop if review rejected after 2 attempts
- **Progress Tracking**: Resume capability via `.develop-progress.json`
- **Zero-Tolerance Validation**: All tests must pass, all reviews must approve

### Breaking Change Notice

**⚠️ BREAKING CHANGE**: This is a complete redesign of the `/nw:develop` command.

**OLD Signature** (DEPRECATED):
```bash
/nw:develop {feature-name} --step {step-id}
```

**NEW Signature**:
```bash
/nw:develop "{feature-description}"
```

**Migration**: For single-step execution, use `/nw:execute` instead (see Migration Guide below).

---

## CRITICAL: Orchestration Protocol

### Input Requirements

The command accepts a single parameter:

- `feature-description` (string, required): Natural language description of the feature to develop
  - Example: "Implement user authentication with JWT"
  - Example: "Add shopping cart with checkout validation"
  - Example: "Optimize database query performance for product listings"

### Output Artifacts

The orchestrator generates the following artifacts:

```
docs/feature/{project-id}/
├── baseline.yaml                    # Phase 1 output
├── roadmap.yaml                     # Phase 3 output
├── steps/
│   ├── 01-01.json                  # Phase 5 output (per step)
│   ├── 01-02.json
│   └── ...
├── .develop-progress.json          # Progress tracking
└── (archived to docs/evolution/    # Phase 8 output
     after finalization)
```

### Orchestration Flow

```
INPUT: "{feature-description}"
  ↓
STEP 1: Extract + Validate Input
  ↓
STEP 2: Derive Project ID (kebab-case)
  ↓
STEP 3: Phase 1 - Baseline Creation (with skip)
  ↓
STEP 4: Phase 2 - Review Baseline (retry max 2)
  ↓
STEP 5: Phase 3 - Roadmap Creation (with skip)
  ↓
STEP 6: Phase 4a - Review Roadmap - Product Owner (retry max 2)
  ↓
STEP 7: Phase 4b - Review Roadmap - Software Crafter (retry max 2)
  ↓
STEP 8: Phase 5 - Split into Atomic Steps (with skip)
  ↓
STEP 9: Phase 6 - Review Each Step File (retry max 2 per file)
  ↓
STEP 10: Phase 7 - Execute All Steps (11-phase TDD per step)
  ↓
STEP 11: Phase 8 - Finalize
  ↓
STEP 12: Phase 9 - Report Completion
```

---

## Agent Invocation Protocol

### STEP 1: Extract Feature Description and Validate Input

**Objective**: Parse command arguments and validate input completeness.

**Actions**:

1. Parse the command invocation:
   ```bash
   /nw:develop "{feature-description}"
   ```

2. Extract `feature-description` parameter

3. **Validation**:
   ```python
   if not feature_description or len(feature_description.strip()) < 10:
       ERROR: "Feature description too short. Provide detailed description (min 10 chars)"
       EXIT

   if feature_description.strip().startswith("--"):
       ERROR: "Invalid syntax. Use: /nw:develop \"{description}\" (not --step flag)"
       HINT: "For single step execution, use /nw:execute instead"
       EXIT
   ```

4. Log invocation:
   ```
   INFO: "Starting DEVELOP wave orchestration"
   INFO: "Feature: {feature_description}"
   ```

**Success Criteria**:
- Feature description extracted and valid
- No deprecated flags detected

---

### STEP 2: Derive Project ID

**Objective**: Generate consistent project identifier from feature description.

**Actions**:

1. **Transform description to kebab-case**:
   ```python
   import re

   def derive_project_id(description):
       """
       Convert natural language description to kebab-case project ID.

       Examples:
         "Implement user authentication with JWT" → "user-authentication"
         "Add shopping cart checkout" → "shopping-cart-checkout"
         "Optimize DB queries" → "optimize-db-queries"
       """
       # Remove common prefixes
       cleaned = description.lower()
       for prefix in ["implement ", "add ", "create ", "build ", "develop "]:
           if cleaned.startswith(prefix):
               cleaned = cleaned[len(prefix):]

       # Extract key words (remove articles, prepositions, conjunctions)
       stop_words = {"the", "a", "an", "with", "for", "and", "or", "in", "on", "at", "to", "from"}
       words = re.findall(r'\w+', cleaned)
       key_words = [w for w in words if w not in stop_words][:5]  # Max 5 words

       # Join with hyphens
       project_id = "-".join(key_words)

       return project_id
   ```

2. **Invoke transformation**:
   ```python
   project_id = derive_project_id(feature_description)

   INFO: f"Derived project ID: {project_id}"
   ```

3. **Check for existing project**:
   ```python
   project_dir = f"docs/feature/{project_id}"

   if os.path.exists(project_dir):
       INFO: f"Found existing project directory: {project_dir}"
       INFO: "Will use smart skip logic for existing artifacts"
   else:
       INFO: f"Creating new project directory: {project_dir}"
       os.makedirs(project_dir, exist_ok=True)
   ```

**Success Criteria**:
- Project ID derived successfully
- Project directory exists or created

---

### STEP 3: Phase 1 - Baseline Creation (with Skip Logic)

**Objective**: Establish quantitative measurement baseline, skip if already approved.

**Actions**:

1. **Check for existing baseline** (embedded script):
   ```python
   def check_artifact_skip(artifact_path, artifact_type):
       """
       Verify if an artifact can be skipped.

       Returns: (should_skip: bool, reason: str, validation_status: str)
       """
       import os
       import yaml

       if not os.path.exists(artifact_path):
           return False, f"{artifact_type} not found at {artifact_path}", "missing"

       with open(artifact_path, 'r') as f:
           data = yaml.safe_load(f)

       # Check validation status
       validation = data.get('baseline', {}).get('validation', {})
       status = validation.get('status', 'pending')

       if status == 'approved':
           return True, f"{artifact_type} exists and approved - skipping creation", "approved"
       elif status == 'complete':
           return False, f"{artifact_type} exists but not yet approved - needs review", "complete"
       elif status == 'draft':
           return False, f"{artifact_type} exists but is draft - needs completion", "draft"
       else:
           return False, f"{artifact_type} exists with unknown status: {status}", status

   # Execute skip check
   baseline_path = f'docs/feature/{project_id}/baseline.yaml'
   should_skip, reason, status = check_artifact_skip(baseline_path, 'Baseline')

   if should_skip:
       print(f"✓ {reason}")
       print(f"Loading existing baseline for context...")
       # Load baseline content for context
       with open(baseline_path, 'r') as f:
           baseline_data = yaml.safe_load(f)
       # Store in orchestrator context
       # Proceed directly to Phase 2 (review will re-verify approval)
   else:
       print(f"⚠ {reason}")
       if status == 'missing':
           print(f"Creating new baseline...")
           # Proceed with baseline creation
       elif status in ['complete', 'draft']:
           print(f"Baseline exists but needs approval. Skipping creation, proceeding to review...")
           # Skip creation, go directly to Phase 2 (review)
   ```

2. **If baseline creation needed** (status == 'missing'):

   a. Invoke baseline command:
   ```bash
   /nw:baseline "{feature_description}"
   ```

   b. Wait for completion

   c. Verify baseline.yaml created:
   ```python
   if not os.path.exists(baseline_path):
       ERROR: "Baseline creation failed - file not found"
       EXIT

   INFO: "✅ Baseline created successfully"
   ```

3. **Update progress tracking**:
   ```python
   update_progress_state(
       project_id,
       current_phase='Phase 1: Baseline Creation',
       skip_flags={'baseline': should_skip}
   )

   if should_skip or status in ['complete', 'draft']:
       # Mark phase complete if skipped or already done
       mark_phase_complete(project_id, 'Phase 1: Baseline Creation')
   ```

**Success Criteria**:
- Baseline exists (either created or pre-existing)
- Baseline file path: `docs/feature/{project-id}/baseline.yaml`
- Progress state updated

---

### STEP 4: Phase 2 - Review Baseline (with Retry)

**Objective**: Ensure baseline quality through mandatory review with automatic retry.

**Actions**:

1. **Execute review with retry loop** (embedded script):

   See [Enforcement Scripts](#enforcement-scripts-embedded-python) section for complete `execute_review_with_retry()` implementation.

   ```python
   approved, attempts, final_status, rejection_reasons = execute_review_with_retry(
       reviewer_agent='@software-crafter-reviewer',
       artifact_type='Baseline',
       artifact_path=f'docs/feature/{project_id}/baseline.yaml',
       project_description=feature_description,
       project_id=project_id,
       max_attempts=2
   )

   if not approved:
       print("\n" + "="*60)
       print("ERROR: Baseline review failed after 2 attempts")
       print("="*60)
       print("\nRejection history:")
       for rejection in rejection_reasons:
           print(f"\nAttempt {rejection['attempt']}:")
           print(f"  {rejection['reason']}")

       print("\nManual intervention required:")
       print("1. Review rejection feedback above")
       print("2. Fix baseline.yaml manually")
       print("3. Re-run: /nw:develop \"{feature_description}\"")
       print("\nThe command will skip baseline creation and proceed to review again.")

       # Update progress with failure
       update_progress_state(
           project_id,
           current_phase='Phase 2: Review Baseline',
           failed_phase='Phase 2: Review Baseline',
           failure_reason=f"Review rejected after {attempts} attempts"
       )

       EXIT
   else:
       print(f"\n✓ Baseline approved after {attempts} attempt(s)")
       print("Proceeding to Phase 3 (roadmap creation)...")

       # Mark phase complete
       mark_phase_complete(project_id, 'Phase 2: Review Baseline')
   ```

**Success Criteria**:
- Baseline reviewed and approved
- validation.status == "approved" in baseline.yaml
- Progress state updated

---

### STEP 5: Phase 3 - Roadmap Creation (with Skip Logic)

**Objective**: Create strategic implementation roadmap, skip if already approved.

**Actions**:

1. **Check for existing roadmap**:
   ```python
   roadmap_path = f'docs/feature/{project_id}/roadmap.yaml'
   should_skip, reason, status = check_artifact_skip(roadmap_path, 'Roadmap')

   if should_skip:
       print(f"✓ {reason}")
       print(f"Loading existing roadmap for context...")
       with open(roadmap_path, 'r') as f:
           roadmap_data = yaml.safe_load(f)
       # Store in context, proceed to Phase 4
   else:
       print(f"⚠ {reason}")
       if status == 'missing':
           print(f"Creating new roadmap...")
       elif status in ['complete', 'draft']:
           print(f"Roadmap exists but needs approval. Skipping creation, proceeding to review...")
   ```

2. **If roadmap creation needed**:

   a. Invoke roadmap command:
   ```bash
   /nw:roadmap @solution-architect "{feature_description}"
   ```

   b. Wait for completion

   c. Verify roadmap.yaml created:
   ```python
   if not os.path.exists(roadmap_path):
       ERROR: "Roadmap creation failed - file not found"
       EXIT

   INFO: "✅ Roadmap created successfully"
   ```

3. **Update progress tracking**:
   ```python
   update_progress_state(
       project_id,
       current_phase='Phase 3: Roadmap Creation',
       skip_flags={'roadmap': should_skip}
   )

   if should_skip or status in ['complete', 'draft']:
       mark_phase_complete(project_id, 'Phase 3: Roadmap Creation')
   ```

**Success Criteria**:
- Roadmap exists (created or pre-existing)
- Roadmap file path: `docs/feature/{project-id}/roadmap.yaml`
- Progress state updated

---

### STEP 6: Phase 4a - Review Roadmap - Product Owner (with Retry)

**Objective**: Validate roadmap against business requirements through Product Owner review.

**Actions**:

1. **Execute Product Owner review with retry**:
   ```python
   approved, attempts, final_status, rejection_reasons = execute_review_with_retry(
       reviewer_agent='@product-owner-reviewer',
       artifact_type='Roadmap',
       artifact_path=f'docs/feature/{project_id}/roadmap.yaml',
       project_description=feature_description,
       project_id=project_id,
       max_attempts=2
   )

   if not approved:
       print("\n" + "="*60)
       print("ERROR: Roadmap Product Owner review failed after 2 attempts")
       print("="*60)
       print("\nRejection history:")
       for rejection in rejection_reasons:
           print(f"\nAttempt {rejection['attempt']}:")
           print(f"  {rejection['reason']}")

       print("\nManual intervention required:")
       print("1. Review Product Owner feedback above")
       print("2. Fix roadmap.yaml manually")
       print("3. Re-run: /nw:develop \"{feature_description}\"")

       update_progress_state(
           project_id,
           failed_phase='Phase 4a: Review Roadmap - Product Owner',
           failure_reason=f"Product Owner review rejected after {attempts} attempts"
       )

       EXIT
   else:
       print(f"\n✓ Roadmap approved by Product Owner after {attempts} attempt(s)")
       print("Proceeding to Phase 4b (Software Crafter review)...")

       mark_phase_complete(project_id, 'Phase 4a: Review Roadmap - Product Owner')
   ```

**Success Criteria**:
- Roadmap approved by Product Owner
- Business requirements validated
- Progress state updated

---

### STEP 7: Phase 4b - Review Roadmap - Software Crafter (with Retry)

**Objective**: Validate roadmap technical feasibility and implementation approach.

**Actions**:

1. **Execute Software Crafter review with retry**:
   ```python
   approved, attempts, final_status, rejection_reasons = execute_review_with_retry(
       reviewer_agent='@software-crafter-reviewer',
       artifact_type='Roadmap',
       artifact_path=f'docs/feature/{project_id}/roadmap.yaml',
       project_description=feature_description,
       project_id=project_id,
       max_attempts=2
   )

   if not approved:
       print("\n" + "="*60)
       print("ERROR: Roadmap Software Crafter review failed after 2 attempts")
       print("="*60)
       print("\nRejection history:")
       for rejection in rejection_reasons:
           print(f"\nAttempt {rejection['attempt']}:")
           print(f"  {rejection['reason']}")

       print("\nManual intervention required:")
       print("1. Review Software Crafter feedback above")
       print("2. Fix roadmap.yaml manually (technical aspects)")
       print("3. Re-run: /nw:develop \"{feature_description}\"")

       update_progress_state(
           project_id,
           failed_phase='Phase 4b: Review Roadmap - Software Crafter',
           failure_reason=f"Software Crafter review rejected after {attempts} attempts"
       )

       EXIT
   else:
       print(f"\n✓ Roadmap approved by Software Crafter after {attempts} attempt(s)")
       print("Proceeding to Phase 5 (split into atomic steps)...")

       mark_phase_complete(project_id, 'Phase 4b: Review Roadmap - Software Crafter')
   ```

**Success Criteria**:
- Roadmap approved by Software Crafter
- Technical approach validated
- Both Product Owner and Software Crafter approvals obtained
- Progress state updated

---

### STEP 8: Phase 5 - Split into Atomic Steps (with Skip Logic)

**Objective**: Decompose roadmap into atomic, executable steps.

**Actions**:

1. **Check for existing step files**:
   ```python
   steps_dir = f'docs/feature/{project_id}/steps'

   if os.path.exists(steps_dir):
       existing_steps = glob.glob(os.path.join(steps_dir, '*.json'))

       if existing_steps:
           print(f"✓ Found {len(existing_steps)} existing step files")

           # Check if ALL steps are approved
           all_approved = True
           for step_file in existing_steps:
               with open(step_file, 'r') as f:
                   step_data = json.load(f)
               validation = step_data.get('validation', {})
               if validation.get('status') != 'approved':
                   all_approved = False
                   break

           if all_approved:
               print(f"✓ All {len(existing_steps)} step files approved - skipping split")
               should_skip = True
           else:
               print(f"⚠ Some step files not approved - skipping split, proceeding to review")
               should_skip = False
       else:
           print(f"⚠ Steps directory exists but empty - creating steps")
           should_skip = False
   else:
       print(f"⚠ No steps directory found - creating steps")
       should_skip = False
   ```

2. **If split needed** (!should_skip):

   a. Invoke split command:
   ```bash
   /nw:split @devop "{project_id}"
   ```

   b. Wait for completion

   c. Verify step files created:
   ```python
   step_files = glob.glob(f'docs/feature/{project_id}/steps/*.json')

   if not step_files:
       ERROR: "Split command completed but no step files found"
       EXIT

   INFO: f"✅ Split created {len(step_files)} step files"
   ```

3. **Update progress tracking**:
   ```python
   update_progress_state(
       project_id,
       current_phase='Phase 5: Split into Atomic Steps',
       skip_flags={'split': should_skip}
   )

   if should_skip:
       mark_phase_complete(project_id, 'Phase 5: Split into Atomic Steps')
   ```

**Success Criteria**:
- Step files exist in `docs/feature/{project-id}/steps/`
- At least 1 step file created
- Progress state updated

---

### STEP 9: Phase 6 - Review Each Step File (with Retry per File)

**Objective**: Ensure each generated step meets quality standards before execution.

**Actions**:

1. **Get all step files**:
   ```python
   step_files = sorted(glob.glob(f'docs/feature/{project_id}/steps/*.json'))

   print(f"\n{'='*60}")
   print(f"Phase 6: Reviewing {len(step_files)} step files")
   print(f"{'='*60}\n")
   ```

2. **Review each step file with retry**:
   ```python
   failed_reviews = []

   for i, step_file in enumerate(step_files, 1):
       step_id = os.path.basename(step_file).replace('.json', '')

       print(f"\n[{i}/{len(step_files)}] Reviewing step: {step_id}")
       print("-" * 40)

       # Check if already approved (skip logic)
       with open(step_file, 'r') as f:
           step_data = json.load(f)

       validation = step_data.get('validation', {})
       if validation.get('status') == 'approved':
           print(f"✓ Step {step_id} already approved - skipping review")
           continue

       # Execute review with retry
       approved, attempts, final_status, rejection_reasons = execute_review_with_retry(
           reviewer_agent='@software-crafter-reviewer',
           artifact_type=f'Step {step_id}',
           artifact_path=step_file,
           project_description=feature_description,
           project_id=project_id,
           max_attempts=2,
           regenerate_command=f'/nw:split @devop "{project_id}" --regenerate-step {step_id}'
       )

       if not approved:
           failed_reviews.append({
               'step_id': step_id,
               'step_file': step_file,
               'attempts': attempts,
               'rejection_reasons': rejection_reasons
           })
       else:
           print(f"✓ Step {step_id} approved after {attempts} attempt(s)")

   # Check if any reviews failed
   if failed_reviews:
       print("\n" + "="*60)
       print(f"ERROR: {len(failed_reviews)} step file(s) failed review")
       print("="*60)

       for failure in failed_reviews:
           print(f"\nStep {failure['step_id']}:")
           for rejection in failure['rejection_reasons']:
               print(f"  Attempt {rejection['attempt']}: {rejection['reason']}")

       print("\nManual intervention required:")
       print("1. Review rejection feedback above")
       print("2. Fix step files manually OR regenerate with feedback")
       print("3. Re-run: /nw:develop \"{feature_description}\"")

       update_progress_state(
           project_id,
           failed_phase='Phase 6: Review Each Step File',
           failure_reason=f"{len(failed_reviews)} step(s) rejected after 2 attempts"
       )

       EXIT
   else:
       print(f"\n✅ All {len(step_files)} step files approved")
       print("Proceeding to Phase 7 (execute all steps)...")

       mark_phase_complete(project_id, 'Phase 6: Review Each Step File')
   ```

**Success Criteria**:
- All step files reviewed
- All step files approved (validation.status == "approved")
- Progress state updated

---

### STEP 10: Phase 7 - Execute All Steps (11-Phase TDD per Step)

**Objective**: Execute all atomic steps in dependency order using complete 11-phase TDD.

**Actions**:

1. **Validate all steps approved** (embedded script - see Enforcement Scripts section):
   ```python
   all_approved, unapproved_steps, error_message = validate_all_steps_approved(
       f'docs/feature/{project_id}/steps/'
   )

   if not all_approved:
       print(error_message)
       EXIT
   else:
       print(error_message)  # "✓ All N step files approved"
   ```

2. **Sort steps by dependency order** (embedded script - see Enforcement Scripts section):
   ```python
   sorted_step_files, error = topological_sort_steps(f'docs/feature/{project_id}/steps/')

   if error:
       print(error)
       EXIT
   else:
       print(f"✓ Steps sorted by dependency order:")
       for i, step_file in enumerate(sorted_step_files, 1):
           print(f"  {i}. {os.path.basename(step_file)}")
   ```

3. **Execute each step in order**:
   ```python
   print(f"\n{'='*60}")
   print(f"Executing {len(sorted_step_files)} steps with 11-phase TDD")
   print(f"{'='*60}\n")

   completed_steps = []
   failed_step = None

   for i, step_file in enumerate(sorted_step_files, 1):
       step_id = os.path.basename(step_file).replace('.json', '')

       print(f"\n[{i}/{len(sorted_step_files)}] Executing step: {step_id}")
       print("-" * 40)

       # Check if step already completed (resume capability)
       with open(step_file, 'r') as f:
           step_data = json.load(f)

       tdd_tracking = step_data.get('tdd_cycle', {}).get('tdd_phase_tracking', {})
       phase_log = tdd_tracking.get('phase_execution_log', [])

       commit_phase = next((p for p in phase_log if p['phase_name'] == 'COMMIT'), None)
       if commit_phase and commit_phase.get('outcome') == 'PASS':
           print(f"✓ Step {step_id} already completed - skipping")
           completed_steps.append(step_id)
           continue

       # Execute step with 11-phase TDD
       print(f"Invoking: /nw:execute @software-crafter \"{step_file}\"")

       # Use Task tool to invoke execute command
       # (In real implementation, this would be actual Task tool invocation)
       result = execute_step_with_11_phases(step_file)

       if result['success']:
           print(f"✓ Step {step_id} completed successfully")
           completed_steps.append(step_id)

           # Update progress
           update_progress_state(
               project_id,
               completed_steps=completed_steps
           )
       else:
           print(f"❌ Step {step_id} failed: {result['error']}")
           failed_step = step_id

           # Update progress with failure
           update_progress_state(
               project_id,
               failed_step=failed_step,
               failed_phase='Phase 7: Execute All Steps',
               failure_reason=f"Step {step_id} execution failed: {result['error']}"
           )

           print("\n" + "="*60)
           print(f"ERROR: Step execution failed at {step_id}")
           print("="*60)
           print(f"\nCompleted steps: {len(completed_steps)}/{len(sorted_step_files)}")
           print(f"Failed step: {step_id}")
           print(f"Error: {result['error']}")
           print("\nManual intervention required:")
           print("1. Review error above")
           print("2. Fix implementation issues")
           print("3. Re-run: /nw:develop \"{feature_description}\"")
           print("\nThe command will resume from the failed step.")

           EXIT

   print(f"\n✅ All {len(sorted_step_files)} steps completed successfully")
   print("Proceeding to Phase 8 (finalize)...")

   mark_phase_complete(project_id, 'Phase 7: Execute All Steps')
   ```

**Success Criteria**:
- All steps executed with 11-phase TDD
- All steps have COMMIT phase with outcome == "PASS"
- All commits created (one per step)
- No steps failed
- Progress state updated

---

### STEP 11: Phase 8 - Finalize

**Objective**: Archive results and clean up workflow files.

**Actions**:

1. **Validate commits for completed steps** (embedded script - see Enforcement Scripts section):
   ```python
   all_committed, missing_commits, error_message = validate_commits_for_completed_steps(
       f'docs/feature/{project_id}/steps/'
   )

   if not all_committed:
       print(error_message)
       EXIT
   else:
       print(error_message)  # "✓ All completed steps have git commits"
   ```

2. **Invoke finalize command**:
   ```bash
   /nw:finalize @devop "{project_id}"
   ```

3. **Wait for completion and verify**:
   ```python
   evolution_files = glob.glob(f'docs/evolution/*{project_id}*.md')

   if not evolution_files:
       WARN: "Finalize completed but no evolution document found"
   else:
       INFO: f"✅ Evolution document created: {evolution_files[0]}"

   # Verify cleanup
   if os.path.exists(f'docs/feature/{project_id}/.develop-progress.json'):
       INFO: "Progress tracking file archived"

   mark_phase_complete(project_id, 'Phase 8: Finalize')
   ```

**Success Criteria**:
- Finalize command executed successfully
- Evolution document created in `docs/evolution/`
- Workflow files cleaned up or archived
- Progress state updated

---

### STEP 12: Phase 9 - Report Completion

**Objective**: Provide comprehensive summary of DEVELOP wave execution.

**Actions**:

1. **Load final progress state**:
   ```python
   progress = load_or_create_progress_state(project_id)
   ```

2. **Count final statistics**:
   ```python
   baseline_path = f'docs/feature/{project_id}/baseline.yaml'
   roadmap_path = f'docs/feature/{project_id}/roadmap.yaml'
   steps_dir = f'docs/feature/{project_id}/steps'

   step_files = glob.glob(os.path.join(steps_dir, '*.json'))

   # Count commits
   commit_count = len(progress.get('completed_steps', []))

   # Count reviews
   total_reviews = (
       1 +  # Baseline review
       2 +  # Roadmap reviews (Product Owner + Software Crafter)
       len(step_files) +  # Step file reviews
       (commit_count * 2)  # TDD phase reviews (REVIEW + POST-REFACTOR REVIEW per step)
   )
   ```

3. **Display comprehensive report**:
   ```python
   print("\n" + "="*60)
   print("🎉 DEVELOP WAVE COMPLETED SUCCESSFULLY!")
   print("="*60)
   print()
   print("Summary:")
   print(f"  - Feature: {feature_description}")
   print(f"  - Project ID: {project_id}")
   print()
   print("Phase Execution:")
   for phase in progress['completed_phases']:
       print(f"  ✓ {phase}")
   print()
   print("Artifacts Created:")
   print(f"  - Baseline: docs/feature/{project_id}/baseline.yaml")
   print(f"  - Roadmap: docs/feature/{project_id}/roadmap.yaml")
   print(f"  - Steps: {len(step_files)} atomic steps")
   print(f"  - Commits: {commit_count} (one per step)")
   print()
   print("Quality Gates Passed:")
   print(f"  - Total reviews: {total_reviews}")
   print(f"    • 1 baseline review")
   print(f"    • 2 roadmap reviews (business + technical)")
   print(f"    • {len(step_files)} step file reviews")
   print(f"    • {commit_count * 2} TDD phase reviews ({commit_count} steps × 2 reviews)")
   print()
   print("💾 All changes committed locally (not pushed)")
   print()
   print("Next Steps:")
   print("  1. Review evolution document:")
   print(f"     docs/evolution/*{project_id}*.md")
   print("  2. Push commits when ready:")
   print("     git push")
   print("  3. Proceed to DEMO wave:")
   print(f"     /nw:demo \"{project_id}\"")
   print()
   print("="*60)
   ```

4. **Mark orchestration complete**:
   ```python
   update_progress_state(
       project_id,
       current_phase=None,
       orchestration_complete=True
   )
   ```

**Success Criteria**:
- Comprehensive report displayed
- All statistics accurate
- Next steps clearly communicated
- Progress state finalized

---

## Enforcement Scripts (Embedded Python)

The following Python scripts are executed at runtime by the devop orchestrator to **enforce** workflow compliance. These are NOT external files - they are embedded in this command specification and executed inline.

### Script Locations

| Script | Invoked At | Purpose |
|--------|-----------|---------|
| `check_artifact_skip()` | STEP 3, 5, 8 | Validate skip logic for baseline/roadmap/steps |
| `validate_all_steps_approved()` | STEP 10 | Block execution if steps not approved |
| `topological_sort_steps()` | STEP 10 | Sort steps by dependencies (Kahn's algorithm) |
| `validate_commits_for_completed_steps()` | STEP 11 | Verify commits before finalize |
| `execute_review_with_retry()` | STEP 4, 6, 7, 9 | Retry loop for reviews (max 2 attempts) |
| `load_or_create_progress_state()` | Start of command | Resume capability and progress tracking |

---

### Script 1: Artifact Skip Logic Validation

**Purpose**: Verify if an artifact can be skipped (exists AND approved).

**Invoked At**: STEP 3 (baseline), STEP 5 (roadmap), STEP 8 (steps)

```python
def check_artifact_skip(artifact_path, artifact_type):
    """
    Verify if an artifact can be skipped.

    Args:
        artifact_path: Path to the artifact file (YAML or JSON)
        artifact_type: Human-readable type name ("Baseline", "Roadmap", etc.)

    Returns:
        tuple: (should_skip: bool, reason: str, validation_status: str)

    Examples:
        >>> check_artifact_skip('docs/feature/auth/baseline.yaml', 'Baseline')
        (True, 'Baseline exists and approved - skipping creation', 'approved')

        >>> check_artifact_skip('docs/feature/auth/baseline.yaml', 'Baseline')
        (False, 'Baseline exists but not yet approved - needs review', 'complete')
    """
    import os
    import yaml
    import json

    # Check if file exists
    if not os.path.exists(artifact_path):
        return False, f"{artifact_type} not found at {artifact_path}", "missing"

    # Load artifact data
    try:
        if artifact_path.endswith('.yaml') or artifact_path.endswith('.yml'):
            with open(artifact_path, 'r') as f:
                data = yaml.safe_load(f)
            # For YAML artifacts (baseline, roadmap), validation is nested
            if 'baseline' in data:
                validation = data['baseline'].get('validation', {})
            elif 'roadmap' in data:
                validation = data['roadmap'].get('validation', {})
            else:
                validation = data.get('validation', {})
        else:  # JSON
            with open(artifact_path, 'r') as f:
                data = json.load(f)
            validation = data.get('validation', {})
    except Exception as e:
        return False, f"Error reading {artifact_type}: {str(e)}", "error"

    # Check validation status
    status = validation.get('status', 'pending')

    if status == 'approved':
        return True, f"{artifact_type} exists and approved - skipping creation", "approved"
    elif status == 'complete':
        return False, f"{artifact_type} exists but not yet approved - needs review", "complete"
    elif status == 'draft':
        return False, f"{artifact_type} exists but is draft - needs completion", "draft"
    elif status == 'pending':
        return False, f"{artifact_type} exists but validation pending", "pending"
    else:
        return False, f"{artifact_type} exists with unknown status: {status}", status
```

**Usage Example** (in STEP 3):
```python
baseline_path = f'docs/feature/{project_id}/baseline.yaml'
should_skip, reason, status = check_artifact_skip(baseline_path, 'Baseline')

if should_skip:
    print(f"✓ {reason}")
    # Load existing baseline and proceed to Phase 2
    with open(baseline_path, 'r') as f:
        baseline_data = yaml.safe_load(f)
else:
    print(f"⚠ {reason}")
    if status == 'missing':
        # Create new baseline
        pass
    elif status in ['complete', 'draft', 'pending']:
        # Skip creation, go directly to review
        pass
```

---

### Script 2: Multi-Artifact Approval Status Validation

**Purpose**: Verify that ALL step files are approved before execution.

**Invoked At**: STEP 10 (before execute all steps)

```python
def validate_all_steps_approved(steps_directory):
    """
    Verify that all step files are approved before execution.

    Args:
        steps_directory: Path to directory containing step JSON files

    Returns:
        tuple: (all_approved: bool, unapproved_steps: list, error_message: str)

    Example:
        >>> validate_all_steps_approved('docs/feature/auth/steps/')
        (False, [{'step_id': '01-02', ...}], 'ERROR: Cannot execute...')
    """
    import os
    import json
    import glob

    if not os.path.exists(steps_directory):
        return False, [], f"Steps directory not found: {steps_directory}"

    step_files = sorted(glob.glob(os.path.join(steps_directory, '*.json')))

    if not step_files:
        return False, [], f"No step files found in {steps_directory}"

    unapproved_steps = []

    for step_file in step_files:
        try:
            with open(step_file, 'r') as f:
                step_data = json.load(f)
        except Exception as e:
            unapproved_steps.append({
                'step_id': os.path.basename(step_file).replace('.json', ''),
                'file': os.path.basename(step_file),
                'status': 'error',
                'reason': f'Error reading file: {str(e)}'
            })
            continue

        step_id = step_data.get('task_specification', {}).get('task_id', 'unknown')
        validation = step_data.get('validation', {})
        status = validation.get('status', 'pending')

        if status != 'approved':
            unapproved_steps.append({
                'step_id': step_id,
                'file': os.path.basename(step_file),
                'status': status,
                'reason': validation.get('notes', 'No reason provided')
            })

    if unapproved_steps:
        error_lines = [
            f"ERROR: Cannot execute steps - {len(unapproved_steps)} steps not approved:",
            ""
        ]
        for step_info in unapproved_steps:
            error_lines.append(f"  • Step {step_info['step_id']} ({step_info['file']})")
            error_lines.append(f"    Status: {step_info['status']}")
            error_lines.append(f"    Reason: {step_info['reason']}")
            error_lines.append("")

        error_lines.append("BLOCKER: All step files must be approved before execution.")
        error_lines.append("Run Phase 6 (review each step file) to approve pending steps.")

        return False, unapproved_steps, "\n".join(error_lines)

    return True, [], f"✓ All {len(step_files)} step files approved"
```

**Usage Example** (in STEP 10):
```python
all_approved, unapproved, message = validate_all_steps_approved(
    f'docs/feature/{project_id}/steps/'
)

if not all_approved:
    print(message)
    exit(1)  # BLOCK execution
else:
    print(message)
    print(f"Proceeding to execute {len(glob.glob(f'docs/feature/{project_id}/steps/*.json'))} steps...")
```

---

### Script 3: Topological Sort for Dependency Order

**Purpose**: Sort step files respecting the `requires` field using Kahn's algorithm.

**Invoked At**: STEP 10 (before iterating over steps)

```python
def topological_sort_steps(steps_directory):
    """
    Sort step files based on dependencies ('requires' field) using Kahn's algorithm.

    Args:
        steps_directory: Path to directory containing step JSON files

    Returns:
        tuple: (sorted_files: list, error: str | None)

    Example:
        >>> topological_sort_steps('docs/feature/auth/steps/')
        (['docs/.../01-01.json', 'docs/.../01-02.json', ...], None)
    """
    import os
    import json
    import glob
    from collections import defaultdict, deque

    step_files = glob.glob(os.path.join(steps_directory, '*.json'))

    if not step_files:
        return [], "No step files found in directory"

    # Build dependency graph
    graph = defaultdict(list)  # step_id -> [dependent_step_ids]
    in_degree = defaultdict(int)  # step_id -> count of dependencies
    step_id_to_file = {}  # step_id -> file_path

    for step_file in step_files:
        try:
            with open(step_file, 'r') as f:
                step_data = json.load(f)
        except Exception as e:
            return [], f"Error reading {step_file}: {str(e)}"

        step_id = step_data['task_specification']['task_id']
        step_id_to_file[step_id] = step_file
        requires = step_data['task_specification'].get('requires', [])

        # Initialize in-degree for this step
        if step_id not in in_degree:
            in_degree[step_id] = 0

        # Add edges for dependencies
        for required_step in requires:
            graph[required_step].append(step_id)
            in_degree[step_id] += 1

    # Kahn's algorithm for topological sort
    queue = deque([step_id for step_id in step_id_to_file.keys() if in_degree[step_id] == 0])
    sorted_step_ids = []

    while queue:
        current = queue.popleft()
        sorted_step_ids.append(current)

        for dependent in graph[current]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)

    # Check for cycles
    if len(sorted_step_ids) != len(step_id_to_file):
        remaining = set(step_id_to_file.keys()) - set(sorted_step_ids)
        cycle_info = []
        for step_id in remaining:
            try:
                with open(step_id_to_file[step_id], 'r') as f:
                    requires = json.load(f)['task_specification'].get('requires', [])
                cycle_info.append(f"  • {step_id} requires: {requires}")
            except:
                cycle_info.append(f"  • {step_id} (error reading dependencies)")

        error = (
            f"ERROR: Circular dependency detected in steps!\n"
            f"\n"
            f"Steps involved in cycle:\n" +
            "\n".join(cycle_info) +
            f"\n\n"
            f"Fix the 'requires' field in step files to remove circular dependencies."
        )
        return [], error

    # Convert sorted step IDs to file paths
    sorted_files = [step_id_to_file[step_id] for step_id in sorted_step_ids]

    return sorted_files, None
```

**Usage Example** (in STEP 10):
```python
sorted_step_files, error = topological_sort_steps(f'docs/feature/{project_id}/steps/')

if error:
    print(error)
    exit(1)  # BLOCK execution
else:
    print(f"✓ Steps sorted by dependency order:")
    for i, step_file in enumerate(sorted_step_files, 1):
        print(f"  {i}. {os.path.basename(step_file)}")

    # Proceed with execution in this order
    for step_file in sorted_step_files:
        # Execute step...
        pass
```

---

### Script 4: Git Commits Validation for Completed Steps

**Purpose**: Verify that each completed step has a corresponding git commit.

**Invoked At**: STEP 11 (pre-finalize validation)

```python
def validate_commits_for_completed_steps(steps_directory):
    """
    Verify that each completed step has a corresponding git commit.

    Args:
        steps_directory: Path to directory containing step JSON files

    Returns:
        tuple: (all_committed: bool, missing_commits: list, error_message: str)

    Example:
        >>> validate_commits_for_completed_steps('docs/feature/auth/steps/')
        (False, [{'step_id': '01-02', ...}], 'ERROR: Cannot finalize...')
    """
    import os
    import json
    import glob
    import subprocess

    step_files = glob.glob(os.path.join(steps_directory, '*.json'))

    if not step_files:
        return True, [], "No step files to validate"

    missing_commits = []

    for step_file in step_files:
        try:
            with open(step_file, 'r') as f:
                step_data = json.load(f)
        except Exception as e:
            missing_commits.append({
                'step_id': os.path.basename(step_file).replace('.json', ''),
                'file': os.path.basename(step_file),
                'reason': f'Error reading file: {str(e)}'
            })
            continue

        step_id = step_data.get('task_specification', {}).get('task_id', 'unknown')

        # Check if step is marked as completed
        tdd_phases = step_data.get('tdd_cycle', {}).get('tdd_phase_tracking', {})
        phase_log = tdd_phases.get('phase_execution_log', [])

        commit_phase = next((p for p in phase_log if p['phase_name'] == 'COMMIT'), None)

        if not commit_phase:
            # Step not completed yet - skip validation
            continue

        if commit_phase.get('outcome') != 'PASS':
            missing_commits.append({
                'step_id': step_id,
                'file': os.path.basename(step_file),
                'reason': 'COMMIT phase exists but outcome != PASS'
            })
            continue

        # Check if commit exists in git history
        notes = commit_phase.get('notes', {})
        commit_hash = notes.get('commit_hash') if isinstance(notes, dict) else None

        if not commit_hash:
            missing_commits.append({
                'step_id': step_id,
                'file': os.path.basename(step_file),
                'reason': 'COMMIT phase marked PASS but no commit_hash recorded'
            })
            continue

        # Verify commit exists in git
        try:
            result = subprocess.run(
                ['git', 'cat-file', '-e', commit_hash],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                missing_commits.append({
                    'step_id': step_id,
                    'file': os.path.basename(step_file),
                    'reason': f'Commit hash {commit_hash[:7]} not found in git history'
                })
        except subprocess.TimeoutExpired:
            missing_commits.append({
                'step_id': step_id,
                'file': os.path.basename(step_file),
                'reason': 'Git verification timeout'
            })
        except Exception as e:
            missing_commits.append({
                'step_id': step_id,
                'file': os.path.basename(step_file),
                'reason': f'Error verifying commit: {str(e)}'
            })

    if missing_commits:
        error_lines = [
            f"ERROR: Cannot finalize - {len(missing_commits)} completed steps missing commits:",
            ""
        ]
        for commit_info in missing_commits:
            error_lines.append(f"  • Step {commit_info['step_id']} ({commit_info['file']})")
            error_lines.append(f"    Reason: {commit_info['reason']}")
            error_lines.append("")

        error_lines.append("BLOCKER: All completed steps must have corresponding git commits.")
        error_lines.append("Re-run failed steps or create missing commits before finalize.")

        return False, missing_commits, "\n".join(error_lines)

    return True, [], "✓ All completed steps have git commits"
```

**Usage Example** (in STEP 11):
```python
all_committed, missing, message = validate_commits_for_completed_steps(
    f'docs/feature/{project_id}/steps/'
)

if not all_committed:
    print(message)
    exit(1)  # BLOCK finalize
else:
    print(message)
    print("Proceeding to finalize...")
```

---

### Script 5: Review Retry Loop Logic

**Purpose**: Implement automatic retry with max 2 attempts for review rejections.

**Invoked At**: STEP 4, 6, 7, 9 (all review phases)

```python
def execute_review_with_retry(reviewer_agent, artifact_type, artifact_path,
                              project_description, project_id, max_attempts=2,
                              regenerate_command=None):
    """
    Execute review with automatic retry on rejection.

    Args:
        reviewer_agent: Agent to perform review (e.g., '@software-crafter-reviewer')
        artifact_type: Type of artifact ('Baseline', 'Roadmap', 'Step 01-02', etc.)
        artifact_path: Path to artifact file
        project_description: Original feature description (for regeneration context)
        project_id: Project identifier
        max_attempts: Maximum review attempts (default: 2)
        regenerate_command: Command to regenerate artifact (if applicable)

    Returns:
        tuple: (approved: bool, attempts_used: int, final_status: str, rejection_reasons: list)

    Example:
        >>> execute_review_with_retry('@software-crafter-reviewer', 'Baseline',
        ...                           'docs/feature/auth/baseline.yaml',
        ...                           'user authentication', 'auth', 2)
        (True, 1, 'approved', [])
    """
    import subprocess
    import json
    import yaml
    import os
    import time

    rejection_reasons = []

    for attempt in range(1, max_attempts + 1):
        print(f"\n{'='*60}")
        print(f"Review Attempt {attempt}/{max_attempts}: {artifact_type}")
        print(f"{'='*60}\n")

        # Invoke review command
        review_cmd = f'/nw:review {reviewer_agent} {artifact_type.lower().replace(" ", "-")} "{artifact_path}"'
        print(f"Invoking: {review_cmd}")

        # In real implementation, use Task tool to invoke review command
        # Here we simulate by checking artifact's validation status after review

        # Simulate waiting for review completion
        print("Waiting for review completion...")
        time.sleep(1)  # In real implementation, this would be actual Task tool wait

        # Read artifact after review
        try:
            if artifact_path.endswith('.yaml') or artifact_path.endswith('.yml'):
                with open(artifact_path, 'r') as f:
                    artifact_data = yaml.safe_load(f)
                # Navigate to validation section
                if 'baseline' in artifact_data:
                    validation = artifact_data['baseline'].get('validation', {})
                elif 'roadmap' in artifact_data:
                    validation = artifact_data['roadmap'].get('validation', {})
                else:
                    validation = artifact_data.get('validation', {})
            else:  # JSON
                with open(artifact_path, 'r') as f:
                    artifact_data = json.load(f)
                validation = artifact_data.get('validation', {})
        except Exception as e:
            print(f"⚠ Error reading artifact after review: {str(e)}")
            if attempt < max_attempts:
                continue
            else:
                return False, attempt, 'error_reading_artifact', rejection_reasons

        review_status = validation.get('status', 'pending')
        review_notes = validation.get('notes', '')

        if review_status == 'approved':
            print(f"\n✓ {artifact_type} APPROVED (attempt {attempt})")
            return True, attempt, 'approved', rejection_reasons

        elif review_status in ['rejected', 'needs_revision']:
            rejection_reason = review_notes or 'No specific reason provided'
            rejection_reasons.append({
                'attempt': attempt,
                'reason': rejection_reason
            })

            print(f"\n⚠ {artifact_type} REJECTED (attempt {attempt})")
            print(f"Rejection reason: {rejection_reason}")

            if attempt < max_attempts:
                print(f"\nRegenerating {artifact_type} with feedback...")

                # Regenerate artifact with feedback
                if regenerate_command:
                    # Use custom regenerate command (for steps)
                    regen_cmd = f'{regenerate_command} --feedback "{rejection_reason}"'
                else:
                    # Use standard regeneration based on artifact type
                    if artifact_type == 'Baseline':
                        regen_cmd = f'/nw:baseline "{project_description}" --regenerate --feedback "{rejection_reason}"'
                    elif artifact_type == 'Roadmap':
                        regen_cmd = f'/nw:roadmap @solution-architect "{project_description}" --regenerate --feedback "{rejection_reason}"'
                    else:
                        print(f"⚠ No regeneration command available for {artifact_type}")
                        continue

                print(f"Invoking: {regen_cmd}")
                # In real implementation, invoke via Task tool
                time.sleep(1)  # Simulate regeneration

                print(f"\n{artifact_type} regenerated. Proceeding to attempt {attempt + 1}...")
            else:
                # Max attempts reached
                print(f"\n❌ {artifact_type} rejected after {max_attempts} attempts")
                return False, attempt, 'rejected_max_attempts', rejection_reasons

        else:
            print(f"\n⚠ Unknown review status: {review_status}")
            if attempt == max_attempts:
                return False, attempt, f'unknown_status_{review_status}', rejection_reasons

    # Should not reach here
    return False, max_attempts, 'unexpected_end', rejection_reasons
```

**Usage Example** (in STEP 4):
```python
approved, attempts, status, reasons = execute_review_with_retry(
    reviewer_agent='@software-crafter-reviewer',
    artifact_type='Baseline',
    artifact_path=f'docs/feature/{project_id}/baseline.yaml',
    project_description=feature_description,
    project_id=project_id,
    max_attempts=2
)

if not approved:
    print("\n" + "="*60)
    print("ERROR: Baseline review failed after 2 attempts")
    print("="*60)
    print("\nRejection history:")
    for rejection in reasons:
        print(f"\nAttempt {rejection['attempt']}:")
        print(f"  {rejection['reason']}")

    print("\nManual intervention required:")
    print("1. Review rejection feedback above")
    print("2. Fix baseline.yaml manually")
    print("3. Re-run: /nw:develop \"{feature_description}\"")

    exit(1)
else:
    print(f"\n✓ Baseline approved after {attempts} attempt(s)")
```

---

### Script 6: Progress Tracking and Resume Detection

**Purpose**: Track workflow progress and enable resume from interruptions.

**Invoked At**: Beginning of command and each phase

```python
def load_or_create_progress_state(project_id):
    """
    Load workflow progress state or create new one.

    Args:
        project_id: Project identifier

    Returns:
        dict: Progress state with structure:
            {
                'project_id': str,
                'started_at': str (ISO datetime),
                'last_updated': str (ISO datetime),
                'completed_phases': list of str,
                'current_phase': str | None,
                'failed_phase': str | None,
                'failure_reason': str | None,
                'completed_steps': list of str,
                'failed_step': str | None,
                'skip_flags': {'baseline': bool, 'roadmap': bool, 'split': bool},
                'orchestration_complete': bool
            }

    Example:
        >>> load_or_create_progress_state('user-authentication')
        {
            'project_id': 'user-authentication',
            'started_at': '2025-01-13T10:30:00',
            'completed_phases': ['Phase 1: Baseline Creation'],
            ...
        }
    """
    import os
    import json
    from datetime import datetime

    progress_file = f'docs/feature/{project_id}/.develop-progress.json'

    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            state = json.load(f)

        print(f"\n✓ Found existing progress state (last updated: {state['last_updated']})")
        print(f"  Completed phases: {', '.join(state['completed_phases'])}")

        if state.get('failed_phase'):
            print(f"  ⚠ Previous run failed at: {state['failed_phase']}")
            print(f"  Failure reason: {state.get('failure_reason', 'Unknown')}")

        if state.get('orchestration_complete'):
            print(f"  ✓ Orchestration already complete")

        return state
    else:
        # Create new progress state
        state = {
            'project_id': project_id,
            'started_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'completed_phases': [],
            'current_phase': None,
            'failed_phase': None,
            'failure_reason': None,
            'completed_steps': [],
            'failed_step': None,
            'skip_flags': {
                'baseline': False,
                'roadmap': False,
                'split': False
            },
            'orchestration_complete': False
        }

        # Create progress file
        os.makedirs(os.path.dirname(progress_file), exist_ok=True)
        with open(progress_file, 'w') as f:
            json.dump(state, f, indent=2)

        print(f"\n✓ Created new progress state")
        return state


def update_progress_state(project_id, **updates):
    """
    Update workflow progress state.

    Args:
        project_id: Project identifier
        **updates: Fields to update in progress state

    Example:
        >>> update_progress_state('user-auth', current_phase='Phase 3: Roadmap Creation')
        >>> update_progress_state('user-auth', completed_steps=['01-01', '01-02'])
    """
    import os
    import json
    from datetime import datetime

    progress_file = f'docs/feature/{project_id}/.develop-progress.json'

    if not os.path.exists(progress_file):
        print(f"⚠ Progress file not found, creating new state")
        load_or_create_progress_state(project_id)

    with open(progress_file, 'r') as f:
        state = json.load(f)

    # Update fields
    state.update(updates)
    state['last_updated'] = datetime.now().isoformat()

    # Write back
    with open(progress_file, 'w') as f:
        json.dump(state, f, indent=2)


def mark_phase_complete(project_id, phase_name):
    """
    Mark a phase as completed.

    Args:
        project_id: Project identifier
        phase_name: Name of completed phase

    Example:
        >>> mark_phase_complete('user-auth', 'Phase 1: Baseline Creation')
    """
    import os
    import json
    from datetime import datetime

    progress_file = f'docs/feature/{project_id}/.develop-progress.json'

    with open(progress_file, 'r') as f:
        state = json.load(f)

    if phase_name not in state['completed_phases']:
        state['completed_phases'].append(phase_name)

    state['current_phase'] = None
    state['last_updated'] = datetime.now().isoformat()

    with open(progress_file, 'w') as f:
        json.dump(state, f, indent=2)

    print(f"✓ Phase '{phase_name}' marked complete")
```

**Usage Example** (at command start):
```python
progress = load_or_create_progress_state(project_id)

# Before each phase
if 'Phase 1: Baseline Creation' in progress['completed_phases']:
    print("✓ Phase 1 already complete - skipping")
else:
    print("Starting Phase 1: Baseline Creation...")
    update_progress_state(project_id, current_phase='Phase 1: Baseline Creation')
    # Execute Phase 1...
    mark_phase_complete(project_id, 'Phase 1: Baseline Creation')
```

---

## Usage Examples

### Example 1: Complete Feature Development

Develop a complete feature from natural language description:

```bash
/nw:develop "Implement user authentication with JWT tokens and session management"
```

**What happens**:
1. Creates baseline measurement (`docs/feature/user-authentication/baseline.yaml`)
2. Reviews baseline (1 review)
3. Creates roadmap (`docs/feature/user-authentication/roadmap.yaml`)
4. Reviews roadmap (2 reviews: Product Owner + Software Crafter)
5. Splits into atomic steps (`docs/feature/user-authentication/steps/*.json`)
6. Reviews each step file (N reviews, one per step)
7. Executes all steps with 11-phase TDD (2N reviews: REVIEW + POST-REFACTOR per step)
8. Finalizes and archives to `docs/evolution/`
9. Reports completion

**Total quality gates**: 3 + 3N reviews (where N = number of steps)

---

### Example 2: Resume After Interruption

If the orchestration was interrupted (e.g., review rejection, step failure):

```bash
# Same command - smart resume
/nw:develop "Implement user authentication with JWT tokens and session management"
```

**What happens**:
- Loads `.develop-progress.json`
- Skips completed phases
- Resumes from failure point
- Example: If baseline approved, roadmap approved, but step 01-02 review rejected:
  - Skips baseline creation (approved)
  - Skips roadmap creation (approved)
  - Skips split (completed)
  - Re-reviews step 01-02 (needs approval)
  - Continues from there

---

### Example 3: Fresh Start on Existing Project

If you want to restart from scratch (e.g., requirements changed):

```bash
# Delete progress and artifacts
rm -rf docs/feature/user-authentication/

# Run command - creates everything fresh
/nw:develop "Implement user authentication with JWT tokens and session management"
```

---

## Complete Workflow Integration

### Greenfield Project - Full nWave

```bash
# Wave 1: DISCUSS (optional - can skip if requirements clear)
/nw:discuss "User authentication system requirements"

# Wave 2: DESIGN (optional - can skip if architecture defined)
/nw:design "Microservices with hexagonal architecture for auth"

# Wave 3: DISTILL (optional - acceptance tests from design)
/nw:distill "User can register and login securely"

# Wave 4: DEVELOP (THIS COMMAND - fully automated)
/nw:develop "Implement user authentication with JWT tokens"
# Automatically: baseline → roadmap → split → execute all → finalize

# Wave 5: DEMO
/nw:demo "user-authentication"
```

---

### Brownfield Enhancement - DEVELOP Wave Only

```bash
# If you already have baseline and roadmap from previous work:
/nw:develop "Add password reset functionality to existing auth system"

# Smart skip logic:
# - Finds existing baseline.yaml (approved) → skips creation, uses it
# - Finds existing roadmap.yaml (approved) → skips creation, uses it
# - Creates new step files for password reset feature
# - Executes only new steps
# - Commits incrementally
```

---

## Breaking Changes and Migration

### Breaking Change Summary

**⚠️ BREAKING CHANGE**: Complete redesign of `/nw:develop` command.

**REMOVED Functionality**:
- ❌ `/nw:develop {feature} --step {id}` syntax
- ❌ Granular single step execution via develop command

**NEW Functionality**:
- ✅ `/nw:develop "{description}"` for complete wave orchestration
- ✅ Automatic baseline → roadmap → split → execute-all → finalize
- ✅ Mandatory quality gates (3 + 3N reviews per feature)
- ✅ Smart skip logic for approved artifacts
- ✅ Automatic retry (max 2 attempts per review)
- ✅ Progress tracking and resume capability

---

### Migration Guide

#### Scenario 1: Single Step Execution with 11-Phase TDD

**OLD** (no longer works):
```bash
/nw:develop order-management --step 01-02
```

**NEW** (use `/nw:execute` instead):
```bash
/nw:execute @software-crafter "docs/feature/order-management/steps/01-02.json"
```

**Explanation**: The `/nw:execute` command now provides the complete 11-phase TDD execution for a single step that `/nw:develop --step` used to provide.

---

#### Scenario 2: Manual Granular Workflow Control

**OLD** (manual multi-command workflow):
```bash
/nw:baseline "goal description"
/nw:roadmap @solution-architect "goal description"
/nw:split @devop "project-id"
/nw:develop feature-name --step 01-01  # ❌ NO LONGER WORKS
/nw:develop feature-name --step 01-02  # ❌ NO LONGER WORKS
/nw:develop feature-name --step 01-03  # ❌ NO LONGER WORKS
/nw:finalize @devop "project-id"
```

**NEW** (two options):

**Option A - Fully Automated** (recommended):
```bash
/nw:develop "goal description"
# Automatically executes entire workflow with quality gates
```

**Option B - Manual Granular Control** (advanced):
```bash
/nw:baseline "goal description"
/nw:roadmap @solution-architect "goal description"
/nw:split @devop "project-id"
/nw:execute @software-crafter "docs/feature/{id}/steps/01-01.json"  # ✅ NEW
/nw:execute @software-crafter "docs/feature/{id}/steps/01-02.json"  # ✅ NEW
/nw:execute @software-crafter "docs/feature/{id}/steps/01-03.json"  # ✅ NEW
/nw:finalize @devop "project-id"
```

---

#### Scenario 3: Complete Feature Development

**OLD** (manual orchestration required):
```bash
# User had to manually run each command:
/nw:baseline "implement shopping cart"
# ... wait ...
/nw:roadmap @solution-architect "implement shopping cart"
# ... wait ...
/nw:split @devop "shopping-cart"
# ... wait ...
/nw:develop shopping-cart --step 01-01
# ... wait ...
/nw:develop shopping-cart --step 01-02
# ... (repeat for all steps) ...
/nw:finalize @devop "shopping-cart"
```

**NEW** (single command):
```bash
/nw:develop "Implement shopping cart with checkout validation"
# Automatically orchestrates entire workflow ✓
```

---

### Quality Gates Comparison

**OLD Workflow** (manual):
- User manually invoked reviews (optional, often skipped)
- No enforcement of review approvals
- No automatic retry on rejection
- Easy to skip quality checks

**NEW Workflow** (automatic):
- **Mandatory reviews**: 3 + 3N per feature (enforced)
  - 1 baseline review
  - 2 roadmap reviews (Product Owner + Software Crafter)
  - N step file reviews
  - 2N TDD phase reviews (REVIEW + POST-REFACTOR per step)
- **Automatic retry**: Max 2 attempts per review
- **Zero-tolerance**: All reviews must approve before proceeding
- **Cannot skip**: Quality gates enforced via embedded Python scripts

---

## Context Files Required

- None initially - command creates all artifacts
- After creation:
  - `docs/feature/{project-id}/baseline.yaml`
  - `docs/feature/{project-id}/roadmap.yaml`
  - `docs/feature/{project-id}/steps/*.json`
  - `docs/feature/{project-id}/.develop-progress.json` (progress tracking)

---

## Success Criteria

### Phase Completion Criteria

- [ ] **Phase 1-2**: Baseline created OR skipped (if approved), reviewed and approved
- [ ] **Phase 3-4**: Roadmap created OR skipped (if approved), dual reviewed and approved
- [ ] **Phase 5-6**: Steps created OR skipped (if all approved), each reviewed and approved
- [ ] **Phase 7**: All steps executed with 11-phase TDD, all commits created
- [ ] **Phase 8**: Finalize executed, evolution document created
- [ ] **Phase 9**: Completion report displayed

### Overall Success Criteria

- [ ] All quality gates passed (3 + 3N reviews)
- [ ] All artifacts created and approved
- [ ] All step files executed successfully
- [ ] All commits created (one per step, local only)
- [ ] No failing tests
- [ ] Progress tracking complete
- [ ] Evolution document created

---

## Next Wave

**After DEVELOP completes**: `/nw:demo "{project-id}"` → DEMO wave
**Handoff**: feature-completion-coordinator

**Before pushing to remote**:
1. Review evolution document
2. Verify all commits present
3. Run final integration tests (if any)
4. Push when ready: `git push`

---

## Notes

### Design Decisions

1. **Breaking Change Rationale**: Perfect semantics over backwards compatibility - `/nw:develop` should develop the COMPLETE feature, not a single step
2. **Smart Skip Logic**: Enables resume and incremental updates - skip artifact creation if exists AND approved
3. **Mandatory Quality Gates**: Zero-tolerance quality ensures production-ready code - 3 + 3N reviews per feature
4. **Automatic Retry**: Graceful handling of review rejections - max 2 attempts prevents infinite loops
5. **Progress Tracking**: Resume capability for long-running workflows - .develop-progress.json enables recovery
6. **Local Commits Only**: User controls when to push - automatic commits per step, manual push after finalize

### Performance Expectations

- **Baseline + Review**: 10-20 minutes
- **Roadmap + Dual Review**: 20-30 minutes
- **Split + Review Each Step**: 5-10 minutes per step
- **Execute Each Step** (11-phase TDD): 30-60 minutes per step
- **Finalize**: 5-10 minutes

**Total for N steps**: ~60 + (40-70 minutes × N)
- Example: 5 steps = ~5-6 hours total
- Example: 10 steps = ~8-12 hours total

### Error Recovery

If orchestration fails:
1. **Check progress state**: `cat docs/feature/{project-id}/.develop-progress.json`
2. **Review failure reason**: Look for `failed_phase` and `failure_reason`
3. **Fix issue**: Address rejection feedback or implementation error
4. **Re-run command**: `/nw:develop "{description}"` (resumes from failure point)

### Embedded Python Scripts

All enforcement scripts are embedded in this file - **DO NOT** create external .py files. Scripts are executed inline by the devop orchestrator using:
```bash
python3 -c "$(cat << 'SCRIPT'
# Embedded Python script here
SCRIPT
)"
```

This ensures:
- No external dependencies
- Scripts always available
- Version control with command specification
- Runtime enforcement cannot be bypassed

---

**End of DW-DEVELOP Command Specification**
