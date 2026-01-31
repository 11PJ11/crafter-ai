"""
Single Source of Truth: TDD Phase Constants

This module defines the canonical 7-phase TDD cycle (schema v2.0).
All validators and tests should import from here.

Schema v2.0 (7 phases) - Optimized from 14-phase v1.0:
- GREEN: Merges GREEN_UNIT + CHECK_ACCEPTANCE + GREEN_ACCEPTANCE
- REVIEW: Expanded scope, covers both implementation AND post-refactoring
- REFACTOR_CONTINUOUS: Merges REFACTOR_L1 + L2 + L3
- COMMIT: Absorbs FINAL_VALIDATE metadata checks
- REFACTOR_L4: Moved to orchestrator Phase 2.25 (not part of step cycle)
"""

# Canonical 7-phase TDD cycle (schema v2.0)
REQUIRED_PHASES = [
    "PREPARE",
    "RED_ACCEPTANCE",
    "RED_UNIT",
    "GREEN",
    "REVIEW",
    "REFACTOR_CONTINUOUS",
    "COMMIT",
]

PHASE_COUNT = 7

# Phase descriptions for documentation and validation messages
PHASE_DESCRIPTIONS = {
    "PREPARE": "Remove @skip, verify only 1 scenario enabled",
    "RED_ACCEPTANCE": "Test must FAIL initially",
    "RED_UNIT": "Write failing unit tests",
    "GREEN": "Implement minimum code + verify acceptance (green acceptance is consequence of green unit)",
    "REVIEW": "Self-review: SOLID, coverage, acceptance criteria, refactoring quality (MANDATORY)",
    "REFACTOR_CONTINUOUS": "Progressive refactoring: L1 (naming) + L2 (complexity) + L3 (organization)",
    "COMMIT": "Commit with detailed message (absorbs FINAL_VALIDATE metadata checks)",
}

# Legacy 14-phase cycle (schema v1.0) - for backward compatibility
LEGACY_PHASES_V1 = [
    "PREPARE",
    "RED_ACCEPTANCE",
    "RED_UNIT",
    "GREEN_UNIT",
    "CHECK_ACCEPTANCE",
    "GREEN_ACCEPTANCE",
    "REVIEW",
    "REFACTOR_L1",
    "REFACTOR_L2",
    "REFACTOR_L3",
    "REFACTOR_L4",
    "POST_REFACTOR_REVIEW",
    "FINAL_VALIDATE",
    "COMMIT",
]

LEGACY_PHASE_COUNT_V1 = 14
