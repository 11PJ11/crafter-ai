# Plugin Architecture for nWave Installation System

**Status**: Design Complete - Awaiting Implementation
**Priority**: Infrastructure Improvement
**Type**: Refactoring + New Feature (DES Integration)

## Overview

This feature transforms the nWave installation system from a hardcoded approach to a modular plugin-based architecture, enabling new features (like DES) to be added without modifying the core installer.

## Problem Statement

Current `install_nwave.py` has hardcoded methods for each component:
- `_install_agents()`
- `_install_commands()`
- `_install_templates()`
- `_install_utility_scripts()`

**Consequence**: Adding DES (or any new component) requires modifying the installer code, increasing coupling and maintenance burden.

## Solution

Plugin architecture where:
- Each component becomes a self-contained plugin implementing `InstallationPlugin` ABC
- `PluginRegistry` orchestrates installation with topological sort for dependency resolution
- Adding new features requires creating a plugin + 1 line registration (ZERO installer modifications)

## Key Benefits

1. **Extensibility**: Add DES with `DESPlugin` + 1 line in registry
2. **Dependency Management**: Automatic topological sort (Kahn's algorithm)
3. **Testability**: Each plugin unit-testable in isolation
4. **Modularity**: Clear separation of concerns

## Implementation Estimate

- **Time**: 20-27 hours
- **Phases**: 6 (infrastructure → migration → switchover → DES plugin → testing → deployment)
- **Risk**: Low (backward compatible, gradual migration)

## Next Steps

When ready to implement:
1. Read `design.md` for complete implementation plan
2. Follow 6-phase migration strategy
3. Create feature branch: `feature/plugin-architecture`
4. Implement incrementally with tests
5. Deploy as v1.7.0

## Related Documents

- `design.md` - Complete implementation plan with code examples
- `docs/CONTEXT_DRIFT_ANALYSIS.md` - Context on DES user stories
- `scripts/install/install_nwave.py` - Current installer to be refactored

## Dependencies

**Prerequisites**:
- DES implementation complete (`src/des/`)
- Schema v3.0 in use
- Installation scripts functional

**Blocks**:
- DES production deployment (blocked until plugin architecture implemented)
- Other component additions (benefits from modular approach)
