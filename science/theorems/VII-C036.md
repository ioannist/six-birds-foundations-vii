# VII-C036 — Join-created obstruction and needle law

- **Phase-3 asset:** `FVII-SCI03-C036-JOIN-CREATED-NEEDLE`
- **Terminal status:** `TERMINAL_PHASE3_ASSET_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`
- **Grade:** `JOIN_CREATED_CROSS_TERM_NEEDLE_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`

## Formal surface

- Definitions: 15
- Theorems/lemmas/corollaries: 10
- Formalization targets: FT08, FT20
- Positive scenarios: TTW-S08
- Null/control scenarios: TTW-S24
- Countermodels: CM-25, CM-03
- Phase-3 finite envelopes: P3-E08
- Phase-3 bounded witnesses: P3-W20, P3-W21

## Public theorem declarations

- `FoundationsVII.Models.Finite.Phase3.residual_accepted_cardinality`
- `FoundationsVII.Models.Finite.Phase3.residual_raw_cardinality`
- `FoundationsVII.ResidualLedger.append_extends`
- `FoundationsVII.ResidualLedger.mem_of_extends`
- `FoundationsVII.ResidualLedger.no_silent_residual_deletion_under_scope_change`
- `FoundationsVII.constructive_join_created_cross_term_needle`
- `FoundationsVII.join_can_dissolve_and_create_residuals_simultaneously`
- `FoundationsVII.joining_is_not_monotonically_obstruction_reducing`
- `FoundationsVII.relabeling_does_not_count_as_new_cross_term`
- `FoundationsVII.residualKind_mem_all`

## Scientific boundary

A join-created needle requires an active sourced cross-term; relabeling alone does not count as a new obstruction.

The Lean source is complete at text level. Kernel elaboration and executed `#print axioms` results remain the external replay gate.
