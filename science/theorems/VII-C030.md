# VII-C030 — Parent refinement, retention, and join descent

- **Phase-3 asset:** `FVII-SCI03-C030-RETENTION-REFINEMENT`
- **Terminal status:** `TERMINAL_PHASE3_ASSET_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`
- **Grade:** `RETENTION_REFINEMENT_AND_NONMONOTONICITY_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`

## Formal surface

- Definitions: 16
- Theorems/lemmas/corollaries: 13
- Formalization targets: FT07, FT19
- Positive scenarios: TTW-S09
- Null/control scenarios: TTW-S24
- Countermodels: CM-05, CM-22
- Phase-3 finite envelopes: P3-E07
- Phase-3 bounded witnesses: P3-W16, P3-W17, P3-W18, P3-W19

## Public theorem declarations

- `FoundationsVII.JoinDescentCertificate.valid_accounts_for_all_parents`
- `FoundationsVII.Models.Finite.Phase3.refinement_accepted_cardinality`
- `FoundationsVII.Models.Finite.Phase3.refinement_raw_cardinality`
- `FoundationsVII.ParentRetentionMap.erased_parent_is_not_recoverable`
- `FoundationsVII.ParentRetentionMap.full_retention_is_recoverable`
- `FoundationsVII.composite_formation_does_not_imply_parent_retention`
- `FoundationsVII.full_and_partial_retention_are_explicit`
- `FoundationsVII.join_descent_certificate_accounts_for_retained_parents`
- `FoundationsVII.no_unconditional_join_monotonicity_under_refinement`
- `FoundationsVII.parentRetentionStatus_mem_all`
- `FoundationsVII.refinementEffect_mem_all`
- `FoundationsVII.refinement_effects_have_all_four_controls`
- `FoundationsVII.refinement_may_preserve_or_destroy_join_evidence`

## Scientific boundary

Parent refinement is not monotone for join evidence; preserving, strengthening, weakening, and destroying cases remain distinct.

The Lean source is complete at text level. Kernel elaboration and executed `#print axioms` results remain the external replay gate.
