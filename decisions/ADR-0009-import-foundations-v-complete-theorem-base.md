# ADR-0009 — Import and complete the Foundations V theorem-base surface

**Status:** accepted
**Date:** 2026-07-26

## Context

ADR-0007 imported the Foundations VI/Collatz repository and correctly recorded that **that archive** did not contain a dedicated Foundations V E-series library. Before Step 2, the user supplied `six-birds-cognition_v45(2).zip`, which contains the Foundations V theorem ledger, complete D/E Lean source tree, declaration manifest, gates, examples, sweeps, labs, tests, and vendored dependencies.

Foundations VII is expected to depend materially on endogenous closure, carried records, repair joins, probe economies, cognition/institution laws, offline reclosure, and adaptability. Reconstructing those objects from paper prose would create unnecessary type drift and would discard existing theorem, gate, and finite-evidence infrastructure.

The supplied source also contains a discoverability inconsistency: the E16 module is present and substantial, but the upstream root import and declaration manifest omit it.

## Decision

1. Retain the complete supplied cognition archive, its SHA-256, and its upstream commit identity under `formalization/_provenance/`.
2. Extract a curated, byte-exact 372-file active baseline to `formalization/foundations_v_scaffold/`, including **every Lean source** and all theorem/gate/example/sweep/lab/traceability assets.
3. Treat the imported subtree as immutable. Foundations VII work must extend it from `formalization/lean/`.
4. Index the entire archive and the authored Foundations V subset separately. Preserve the exact census: 70 archive modules / 1,758 declarations and 22 authored modules / 1,261 declarations / 187 theorems.
5. Preserve the upstream root and 1,141-row manifest unchanged. Repair E16 discoverability only through:
   - the declaration-free `FoundationsVII.PriorFoundationsVComplete` import wrapper;
   - a VII-owned 1,261-row completed declaration manifest.
6. Deduplicate the byte-identical Foundations III module copy at the active Lake layer while retaining both source copies and their hashes for provenance.
7. Produce cumulative module/declaration/theorem/import indexes across Foundations V, Foundations VI, prior dependencies, and the VII shell.
8. Preserve paper-side theorem grades, complete-evidence assumptions, conditional-classification semantics, open bridges, and empirical nonclaims. Local source presence does not upgrade them.
9. Keep Step 2 unstarted: no claim corpus, bridge verdict, VII object model, candidate law, or new VII theorem is authorized by this integration alone.

## Consequences

- ADR-0007's statement that the **Collatz archive** lacked the E series remains historically true, but its repository-wide import-gap consequence is superseded.
- Foundations VII can now reuse exact D1–D6 and E1–E16 declarations rather than reconstructing them.
- E16 cannot be silently lost through the upstream root import.
- The completed manifest is an integration index, not a modification or retroactive claim about the upstream manifest.
- The active graph records one inherited F13a axiom and five opaque constants from the VI/prior scaffold; the Foundations V archive adds no lexical axioms or opaque declarations.
- Lean kernel compilation remains unverified locally until the pinned Lean/Lake toolchain is available.
