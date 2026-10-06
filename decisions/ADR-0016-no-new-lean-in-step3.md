# ADR-0016 — Keep Step 3 declaration-free

**Status:** Accepted  
**Date:** 2026-07-26

## Context

Step 3 is a dependency-closure and readiness phase. Adding Lean declarations before object signatures, statement scopes, countermodels, and adapter obligations were fixed would prematurely choose definitions and obscure the distinction between a planned target and a proved result.

## Decision

Step 3 adds no `.lean` file and no Foundations VII declaration. It records 20 future targets and resolves each inherited dependency to exact fully qualified declarations in the imported Foundations I–VI spine.

## Consequences

- The cumulative inherited index remains unchanged.
- Planned module names are ownership proposals, not existing modules.
- A later proof phase must create VII-owned wrappers/adapters and record statement deltas and trust assumptions.
- No fresh Lean 4.28.0 kernel claim is made in this stage.
