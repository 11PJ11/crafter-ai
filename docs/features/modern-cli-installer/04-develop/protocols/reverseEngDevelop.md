❯ let's reverse engineer the /nw:develop flow, and inject into it the WIP

⏺ This is a design task: reverse-engineer /nw:develop, then design where WIP.yaml plugs in. Let me read the full execution
  flow first.

⏺ 2 Explore agents finished (ctrl+o to expand)
   ├─ Map full /nw:develop execution flow · 7 tool uses · 15.9k tokens
   │  ⎿
   Done
   └─ Map WIP contract protocol fully · 5 tool uses · 26.2k tokens
      ⎿  Done

⏺ Both maps are complete. Let me synthesize the integration design.

⏺ Updated plan
  ⎿  /plan to preview

⏺ Here's the synthesis. The integration point is clean: WIP.yaml replaces inline context in Phase 2's execution loop.

  The Core Change

  /nw:develop Phase 2 (Execute All Steps):

  CURRENT:  roadmap → extract context → embed in Task prompt → agent executes → check exec-status
  PROPOSED: roadmap → extract context → GENERATE WIP.yaml → agent reads WIP → Vera VERIFIES → update exec-status

  What WIP Adds to /nw:develop
  ┌──────────────────────────┬───────────────────────────────────────────────────────────┐
  │           Gain           │                            How                            │
  ├──────────────────────────┼───────────────────────────────────────────────────────────┤
  │ Physical contract        │ WIP.yaml on disk vs invisible prompt context              │
  ├──────────────────────────┼───────────────────────────────────────────────────────────┤
  │ Drift prevention         │ forbidden_actions block agent from reading roadmap        │
  ├──────────────────────────┼───────────────────────────────────────────────────────────┤
  │ Independent verification │ Vera runs pytest herself, doesn't trust agent's word      │
  ├──────────────────────────┼───────────────────────────────────────────────────────────┤
  │ Resumability             │ WIP.yaml survives session breaks                          │
  ├──────────────────────────┼───────────────────────────────────────────────────────────┤
  │ Token savings            │ ~500 token prompt ("read WIP.yaml") vs ~5k inline context │
  ├──────────────────────────┼───────────────────────────────────────────────────────────┤
  │ Parallel steps           │ Named files: WIP-09-03.yaml, WIP-09-04.yaml, etc.         │
  └──────────────────────────┴───────────────────────────────────────────────────────────┘
  What Stays Unchanged

  Phases 1, 2.25, 3, 3.5, 4 of /nw:develop are untouched. Only the Phase 2 step execution loop changes.

  Key Design Decision

  Who updates execution-status.yaml?
  - Current: Agent updates it during execution
  - Proposed: Vera reads WIP.yaml output section, verifies independently, THEN updates execution-status.yaml herself

  This is the trust boundary shift: execution-status.yaml becomes Vera's verified record, not the agent's self-report.

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 Ready to code?

 Here is Claude's plan:
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
 Plan: Inject WIP Contract into /nw:develop Flow

 The Problem

 /nw:develop Phase 2 (Execute All Steps) passes context inline via Task prompt:
 Orchestrator reads roadmap → extracts ~5k context → embeds in Task prompt → agent executes

 This works but context is invisible (hidden in prompt), non-resumable (lost on session break), and unverifiable (agent
 reports verbally).

 The WIP contract solves these problems but lives outside /nw:develop. Goal: merge them.

 Integration Point

 The WIP.yaml replaces the inline context extraction in Phase 2's step execution loop (Step 7.4 in develop.md).

 Current /nw:develop Flow (Step 7.4)

 FOR each step in sorted_steps:
   1. Check execution-status.yaml for skip (already completed)
   2. Extract step context from roadmap (~5k tokens)
   3. Invoke Task(software-crafter, prompt="...inline context...")
   4. Agent executes, verbally reports success
   5. Check execution-status.yaml for COMMIT/PASS
   6. Update .develop-progress.json

 Proposed Flow with WIP Integration

 FOR each step in sorted_steps:
   1. Check execution-status.yaml for skip                    ← SAME
   2. Extract step context from roadmap (~5k tokens)          ← SAME
   3. GENERATE WIP.yaml from extracted context + constraints  ← NEW
   4. Invoke Task(software-crafter, prompt="Read ONLY WIP.yaml") ← CHANGED
   5. Agent reads WIP.yaml, executes, fills output section    ← NEW
   6. VERIFY: run pytest independently, check git log         ← NEW
   7. Read WIP.yaml output section for completion contract    ← CHANGED
   8. Update execution-status.yaml from WIP.yaml output       ← SAME
   9. Update .develop-progress.json                           ← SAME

 What Changes in /nw:develop

 Step 7.3 → New: WIP Generation Function

 def generate_wip(project_id, step_def, roadmap, phase_id):
     """Generate WIP.yaml from roadmap step definition."""
     wip = {
         'meta': {
             'generated_at': now_iso8601(),
             'generated_by': 'vera-orchestrator',
             'project': project_id,
             'phase': phase_id,
             'schema_version': '0.2'  # bump from 0.1
         },
         'step': {
             'id': step_def['id'],
             'name': step_def['name'],
             'agent': step_def.get('agent', 'software-crafter'),
             'estimated_hours': step_def.get('estimated_hours', 2),
             'dependencies_satisfied': True  # orchestrator verified
         },
         'input': {
             'source_file': infer_source_path(step_def),
             'test_file': infer_test_path(step_def),
             'requirements': extract_requirements(step_def),
             'test_requirements': extract_test_requirements(step_def),
             'architecture_notes': extract_arch_notes(step_def)
         },
         'constraints': {
             'max_tool_calls': 15,
             'must_run_tests': True,
             'fail_fast': True,
             'forbidden_actions': [
                 'DO NOT read roadmap.yaml',
                 'DO NOT read execution-status.yaml',
                 'DO NOT implement other steps'
             ]
         },
         'output': {
             'status': None,
             'artifacts_created': [],
             'test_command': None,
             'test_result': None,
             'commit_hash': None,
             'commit_message': None,
             'notes': None
         }
     }
     write_yaml(f'docs/features/{project_id}/04-develop/WIP.yaml', wip)

 Step 7.4 → Changed: Agent Invocation

 # OLD: Inline context in prompt (~5k tokens of step context)
 Task(
     subagent_type="software-crafter",
     prompt=f"Execute step {step_id}. DESCRIPTION: ... CRITERIA: ..."
 )

 # NEW: Point to WIP.yaml (~100 tokens in prompt)
 Task(
     subagent_type="software-crafter",
     prompt=f"""Execute step {step_id} from the WIP contract.
     Read ONLY: docs/features/{project_id}/04-develop/WIP.yaml

     Rules:
     1. DO NOT read roadmap.yaml or execution-status.yaml
     2. Follow TDD: tests first, then implementation
     3. Run pytest to verify
     4. Commit with conventional format
     5. Fill output section in WIP.yaml"""
 )

 Step 7.5 → New: Independent Verification

 # OLD: Trust execution-status.yaml (agent updates it)
 # NEW: Vera verifies independently, THEN updates execution-status.yaml

 def verify_step_completion(wip_path, step_def):
     wip = read_yaml(wip_path)
     output = wip['output']

     checks = []
     # 1. Run tests independently
     test_result = bash(f"pytest {wip['input']['test_file']} -v")
     checks.append(('tests_pass', test_result.returncode == 0))

     # 2. Check commit exists
     commit_exists = bash(f"git log --oneline -1 | grep {output['commit_hash']}")
     checks.append(('commit_exists', commit_exists.returncode == 0))

     # 3. Check output section filled
     checks.append(('status_filled', output['status'] is not None))
     checks.append(('status_success', output['status'] == 'success'))

     return all(passed for _, passed in checks), checks

 Step 7.6 → Changed: execution-status.yaml Update

 # OLD: Agent updates execution-status.yaml directly
 # NEW: Vera reads WIP.yaml output, updates execution-status.yaml herself

 def update_execution_status(exec_status_path, step_id, wip_output):
     exec_status = read_yaml(exec_status_path)
     exec_status['completed_steps'].append({
         'step_id': step_id,
         'status': 'COMPLETED',
         'commit_hash': wip_output['commit_hash'],
         'artifacts': wip_output['artifacts_created'],
         'test_result': wip_output['test_result']
     })
     write_yaml(exec_status_path, exec_status)

 What DOESN'T Change
 ┌────────────────────────────────────┬────────────────────────────────────────────────────────────────┐
 │             Component              │                             Status                             │
 ├────────────────────────────────────┼────────────────────────────────────────────────────────────────┤
 │ Phase 1: Roadmap Creation + Review │ Unchanged                                                      │
 ├────────────────────────────────────┼────────────────────────────────────────────────────────────────┤
 │ Phase 2.25: Refactoring + Mutation │ Unchanged                                                      │
 ├────────────────────────────────────┼────────────────────────────────────────────────────────────────┤
 │ Phase 3: Finalize + Cleanup        │ Unchanged                                                      │
 ├────────────────────────────────────┼────────────────────────────────────────────────────────────────┤
 │ Phase 3.5: Retrospective           │ Unchanged                                                      │
 ├────────────────────────────────────┼────────────────────────────────────────────────────────────────┤
 │ Phase 4: Report                    │ Unchanged                                                      │
 ├────────────────────────────────────┼────────────────────────────────────────────────────────────────┤
 │ .develop-progress.json             │ Unchanged (orchestrator tracking)                              │
 ├────────────────────────────────────┼────────────────────────────────────────────────────────────────┤
 │ roadmap.yaml                       │ Unchanged (source of truth for step defs)                      │
 ├────────────────────────────────────┼────────────────────────────────────────────────────────────────┤
 │ execution-status.yaml              │ Structure unchanged, but now populated by Vera from WIP output │
 └────────────────────────────────────┴────────────────────────────────────────────────────────────────┘
 Key Differences: /nw:develop vs WIP-Enhanced Flow
 ┌─────────────────────────┬──────────────────────────────┬────────────────────────────────────────────┐
 │         Aspect          │     Original /nw:develop     │                WIP-Enhanced                │
 ├─────────────────────────┼──────────────────────────────┼────────────────────────────────────────────┤
 │ Context delivery        │ Inline in Task prompt (~5k)  │ Physical WIP.yaml file (~500 token prompt) │
 ├─────────────────────────┼──────────────────────────────┼────────────────────────────────────────────┤
 │ Agent scope             │ Prompt-bounded (can drift)   │ File-bounded + forbidden_actions           │
 ├─────────────────────────┼──────────────────────────────┼────────────────────────────────────────────┤
 │ Completion contract     │ Verbal/execution-status.yaml │ WIP.yaml output section                    │
 ├─────────────────────────┼──────────────────────────────┼────────────────────────────────────────────┤
 │ Verification            │ Check execution-status.yaml  │ Independent pytest + git log + WIP output  │
 ├─────────────────────────┼──────────────────────────────┼────────────────────────────────────────────┤
 │ Resumability            │ .develop-progress.json only  │ WIP.yaml persists across sessions          │
 ├─────────────────────────┼──────────────────────────────┼────────────────────────────────────────────┤
 │ Auditability            │ Invisible prompt context     │ Physical inspectable artifact              │
 ├─────────────────────────┼──────────────────────────────┼────────────────────────────────────────────┤
 │ Token cost per step     │ ~5k (context) + ~2k (prompt) │ ~500 (prompt pointing to file)             │
 ├─────────────────────────┼──────────────────────────────┼────────────────────────────────────────────┤
 │ Who updates exec-status │ Agent (during execution)     │ Vera (after verification)                  │
 └─────────────────────────┴──────────────────────────────┴────────────────────────────────────────────┘
 Parallel Steps Enhancement

 Current WIP is singleton (one file). For Phase 09's parallel steps (09-03 through 09-06):

 # Option A: Named WIP files
 WIP-09-03.yaml  # IdeBundleExistsCheck
 WIP-09-04.yaml  # IdeBundleBuildService
 WIP-09-05.yaml  # AssetDeploymentService
 WIP-09-06.yaml  # DeploymentValidationService

 # Agent invocation points to specific file
 Task(..., prompt="Read ONLY: .../WIP-09-03.yaml")

 This closes the "parallel steps" gap in WIP v0.1.

 Files to Modify

 1. ~/.claude/commands/nw/develop.md - Inject WIP generation + verification into Phase 2 loop
 2. docs/features/modern-cli-installer/04-develop/protocols/wip-contract-protocol.md - Promote from v0.1 to v0.2 with
 /nw:develop integration
 3. docs/features/modern-cli-installer/04-develop/protocols/wip-contract-template.yaml - Update schema to v0.2

 Verification

 After implementing the integration:
 1. Execute Phase 09 step 09-01 using the WIP-enhanced flow
 2. Verify WIP.yaml generated correctly from roadmap step
 3. Verify agent reads only WIP.yaml (check forbidden_actions work)
 4. Verify independent test verification catches real failures
 5. Verify execution-status.yaml updated from WIP output
 6. Compare token usage vs inline context approach
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

 Claude has written up a plan and is ready to execute. Would you like to proceed?

 ❯ 1. Yes, clear context and bypass permissions
   2. Yes, and bypass permissions
   3. Yes, manually approve edits
   4. Type here to tell Claude what to change

---

❯ let's reverse engineer the /nw:develop flow, and inject into it the WIP

⏺ This is a design task: reverse-engineer /nw:develop, then design where WIP.yaml plugs in. Let me read the full execution
  flow first.

⏺ 2 Explore agents finished (ctrl+o to expand)
   ├─ Map full /nw:develop execution flow · 7 tool uses · 15.9k tokens
   │  ⎿  Done
   └─ Map WIP contract protocol fully · 5 tool uses · 26.2k tokens
      ⎿  Done

⏺ Both maps are complete. Let me synthesize the integration design.

⏺ Updated plan
  ⎿  /plan to preview

⏺ Here's the synthesis. The integration point is clean: WIP.yaml replaces inline context in Phase 2's execution loop.

  The Core Change

  /nw:develop Phase 2 (Execute All Steps):

  CURRENT:  roadmap → extract context → embed in Task prompt → agent executes → check exec-status
  PROPOSED: roadmap → extract context → GENERATE WIP.yaml → agent reads WIP → Vera VERIFIES → update exec-status

  What WIP Adds to /nw:develop
  ┌──────────────────────────┬───────────────────────────────────────────────────────────┐
  │           Gain           │                            How                            │
  ├──────────────────────────┼───────────────────────────────────────────────────────────┤
  │ Physical contract        │ WIP.yaml on disk vs invisible prompt context              │
  ├──────────────────────────┼───────────────────────────────────────────────────────────┤
  │ Drift prevention         │ forbidden_actions block agent from reading roadmap        │
  ├──────────────────────────┼───────────────────────────────────────────────────────────┤
  │ Independent verification │ Vera runs pytest herself, doesn't trust agent's word      │
  ├──────────────────────────┼───────────────────────────────────────────────────────────┤
  │ Resumability             │ WIP.yaml survives session breaks                          │
  ├──────────────────────────┼───────────────────────────────────────────────────────────┤
  │ Token savings            │ ~500 token prompt ("read WIP.yaml") vs ~5k inline context │
  ├──────────────────────────┼───────────────────────────────────────────────────────────┤
  │ Parallel steps           │ Named files: WIP-09-03.yaml, WIP-09-04.yaml, etc.         │
  └──────────────────────────┴───────────────────────────────────────────────────────────┘
  What Stays Unchanged

  Phases 1, 2.25, 3, 3.5, 4 of /nw:develop are untouched. Only the Phase 2 step execution loop changes.

  Key Design Decision

  Who updates execution-status.yaml?
  - Current: Agent updates it during execution
  - Proposed: Vera reads WIP.yaml output section, verifies independently, THEN updates execution-status.yaml herself

  This is the trust boundary shift: execution-status.yaml becomes Vera's verified record, not the agent's self-report.
  ⎿ Tool use rejected with user message: this is the branch of the installare and this plan should have a fully structure
    experiment into a separated branch. Mixing the 2 things while we are running on nWave installation coming from master
    branch is highly risky. I would prefer you to create a detailed report about how in the branch I'll create later name
    WIP, we wanna try to enhance the dev wave with our WIP technique. For the moment can you orchestrate the new flow
    manually with a clear structure that we save in the CLAUDE.local.md to avoid we miss it in the context compacting?

⏺ Totally right. Mixing nWave framework changes with feature work on the same branch is asking for trouble. Two
  deliverables:

  1. Report for the future WIP branch (design document, saved in docs)
  2. CLAUDE.local.md update with the manual orchestration protocol I'll follow for Phase 09

⏺ Recalled 1 memory, wrote 1 memory (ctrl+o to expand)

⏺ Now let me write the detailed report for the future WIP branch.

⏺ Write(docs/features/modern-cli-installer/04-develop/protocols/wip-develop-integration-report.md)
  ⎿  Wrote 330 lines to docs/features/modern-cli-installer/04-develop/protocols/wip-develop-integration-report.md
       1 # WIP Contract + /nw:develop Integration Report
       2
       3 > This report documents how to integrate the WIP.yaml contract pattern
       4 > into the /nw:develop command. Implementation should happen in a dedicated
       5 > "WIP" branch, NOT in the installer branch.
       6
       7 ## Status
       8
       9 - **Report date:** 2026-02-05
      10 - **Target branch:** WIP (to be created from master)
     … +320 lines (ctrl+o to expand)
  ⎿  Found 11 new diagnostic issues in 1 file (ctrl+o to expand)

⏺ Done. Two deliverables:

  1. CLAUDE.local.md (updated)

  Added Phase 09 Manual Orchestration Protocol with:
  - Execution state tracker (survives context compaction)
  - Dependency graph with ASCII art
  - 6-step execution protocol per step (pre-flight, generate WIP, invoke, verify, update, on-failure)
  - Parallel execution strategy (named WIP files)
  - Integration steps special handling (existing test suite verification)
  - Quality gates checklist

  2. Integration Report (new)

  docs/features/modern-cli-installer/04-develop/protocols/wip-develop-integration-report.md

  Documents exactly what to change in /nw:develop for the future WIP branch:
  - 4 specific code changes with before/after
  - What stays unchanged (Phases 1, 2.25, 3, 3.5, 4)
  - Parallel WIP file convention
  - Path convention fix (feature vs features)
  - Token impact analysis
  - Validation plan
  - Implementation checklist

  The key insight: only Phase 2's step execution loop changes. Everything else stays the same. When you create the WIP
  branch, the report has the exact surgical modifications needed.

  For now, I'll follow the manual protocol in CLAUDE.local.md to execute Phase 09. Ready when you are.

✻ Brewed for 5m 11s
