# ADR-0008 — Reconcile Step 1 against the imported formal scaffold before Step 2

**Status:** accepted  
**Date:** 2026-07-26

## Context

Step 1 was completed before the Foundations VI/Collatz repository was supplied. The imported repository contains exact theorem ledgers, Lean modules, trust-base records, gates, laboratories, and prior-Foundations assets. The original Step-1 validation checked coverage and registry presence but did not compare canonical reading statements against this newly available proof surface.

A direct audit found several material risks: Foundations-II typed infrastructure could be mistaken for strongest-form derivation; paper-wide Foundations-IV/V formalization reports could be mistaken for locally available assets; G theorem/schema grades had been flattened; paper-side artifact disclosures were not explicit in every survey card; the promised paper-dependency field had only TeX include trees rather than a corpus-paper citation view; and the P040/P058 version family lacked both a structural delta and exact line-by-line source control.

## Decision

1. Reopen Step 1 only for formalization-aware reconnaissance and status correction.
2. Preserve the existing semantic model unless contradicted by exact source or formal evidence.
3. Introduce a three-axis evidence discipline: paper claim grade, statement fidelity, and local verification state.
4. Reconcile Foundations I–VI and the no-go paper against the supplied scaffold in separate supplements.
5. Record complete F/E/G paper-versus-local disclosure matrices.
6. Add explicit artifact/formalization disclosure sections to all 58 survey cards.
7. Restore the exact wish-list coverage vocabulary required by the original plan.
8. Add source-located citation-dependency reconnaissance to every paper card, preserving unresolved and out-of-corpus keys and prohibiting theorem-dependency or bridge inference from citation alone.
9. Produce both structural and exact raw-source P040/P058 deltas while deferring theorem/claim-level canonicalization to Step 2.
10. Reject any remediation that creates all-paper claim records, bridge verdicts, VII candidate laws, or new VII Lean declarations.

## Consequences

Step 1 is now proof-aware enough to support Step 2 without treating paper report, local file presence, import resolution, kernel proof, and finite computation as interchangeable. The canonical SBT interpretation is retained, but later reuse must cite exact declaration fidelity, trust/host premises, and local evidence state.

The repository remains at 20 `DEEP_READ` and 38 `SURVEYED` papers; Step 2 has not begun. P039, unavailable Lean/Lake, unavailable PySAT tests, absent Foundations-V E assets, the partial Foundations-IV import, unresolved citation keys, and the deferred semantic P040/P058 canonicalization remain explicit limitations.
