# ADR-0013 — P040/P058 remain one non-independent unresolved evidence family after claim alignment

**Status:** accepted  
**Date:** 2026-07-26

## Context

Step 1 established that P040 and P058 are close source variants and must not be counted as independent evidence. Step 2 required claim-level rather than merely section/line-level control, but the available evidence does not compel a canonical member or theorem-equivalence ruling.

## Decision

1. Maintain version-family identifier `VF-SAU-01`.
2. Align the canonical claims in a 223-row delta ledger, allowing rows with a claim on only one side.
3. Preserve exact source locations and relation labels for each aligned slot.
4. Count P040/P058 as one non-independent evidence family in all synthesis.
5. Do not select a canonical member, merge claim IDs, or infer theorem equivalence at Step 2.
6. Carry the unresolved semantic choice into the Step-3 inheritance/adjudication phase.

## Consequences

- No duplicate evidentiary vote is created.
- Variant-specific claims remain visible.
- Later canonicalization, if any, must cite the claim delta and state the semantic criterion used.
