# VII-C019 — Access/join residual and obstruction-dissolution ledger

- **Phase-3 asset:** `FVII-SCI03-C019-RESIDUAL-LEDGER`
- **Terminal status:** `TERMINAL_PHASE3_ASSET_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`
- **Grade:** `APPEND_ONLY_RESIDUAL_AND_DISSOLUTION_LEDGER_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`

## Formal surface

- Definitions: 15
- Theorems/lemmas/corollaries: 10
- Formalization targets: FT09, FT20
- Positive scenarios: TTW-S10
- Null/control scenarios: TTW-S24
- Countermodels: CM-22, CM-25
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

Residual bookkeeping is scoped to declared ledgers and does not assert that all obstructions are additive or monotonically removed by joining.

The Lean source is complete at text level. Kernel elaboration and executed `#print axioms` results remain the external replay gate.
