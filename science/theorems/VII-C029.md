# VII-C029 — Observer and instrument occupancy law

**Phase-2 asset:** `FVII-SCI02-C029-OBSERVER-OCCUPANCY`  
**Terminal status:** `TERMINAL_PHASE2_ASSET_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`  
**Grade:** `OBSERVER_OCCUPANCY_NO_GO_AND_LEDGER_THEOREMS_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`

## Formal surface

- Definitions: 12
- Theorems/lemmas/corollaries: 17
- Formalization targets: FT16
- Positive scenarios: TTW-S22
- Null/control scenarios: TTW-S12
- Countermodels: CM-11, CM-21
- New bounded witnesses: P2-W15

## Public theorem declarations

- `FoundationsVII.BudgetEntry.failed_admission_conservation_accounting`
- `FoundationsVII.BudgetEntry.failed_unused_admission_full_refund_is_conserved`
- `FoundationsVII.BudgetEntry.settled_failure_refund_equation`
- `FoundationsVII.Models.Finite.Phase2.native_credit_requires_priced_occupancy`
- `FoundationsVII.Models.Finite.Phase2.observer_admissible_cardinality`
- `FoundationsVII.Models.Finite.Phase2.observer_raw_cardinality`
- `FoundationsVII.Models.Finite.Phase2.settled_failures_conserve_declared_budget`
- `FoundationsVII.Models.Finite.Phase2.settlement_admissible_cardinality`
- `FoundationsVII.Models.Finite.Phase2.settlement_raw_cardinality`
- `FoundationsVII.NoGo.NGVII_05_escape_external_observer`
- `FoundationsVII.NoGo.NGVII_05_escape_zero_occupancy`
- `FoundationsVII.NoGo.NGVII_05_no_unpriced_observer_native_credit`
- `FoundationsVII.ObserverOccupancyRecord.certified_external_observer_is_a_lawful_escape`
- `FoundationsVII.ObserverOccupancyRecord.certified_zero_occupancy_is_fully_priced`
- `FoundationsVII.ObserverOccupancyRecord.hidden_occupancy_is_not_fully_priced`
- `FoundationsVII.ObserverOccupancyRecord.unpriced_observer_invalidates_native_formation_credit`
- `FoundationsVII.ObserverOccupancyRecord.zero_occupancy_native_credit`

## Scientific boundary

Observer costs are ledger-relative; omitted resources falsify native/endogenous or zero-cost credit.

The source proof is complete at the Lean text level. Kernel elaboration and `#print axioms` replay remain an explicit external execution gate.
