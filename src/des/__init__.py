"""DES (Deterministic Execution System) - Post-execution validation and phase tracking.

This package provides deterministic validation hooks that fire when sub-agents complete
execution, ensuring phase progression is tracked accurately and deviations are detected.

Core Components:
  - SubagentStopHook: Validates step file state after agent completion
  - HookResult: Encapsulates validation results and issue tracking

Note: SubagentStopHook and HookResult are defined in the root-level des module,
not within this src/des package. Import them from the root des package instead.
"""

__all__ = []
