# VII-C011 — Join budget and payment ledger

- **Phase-3 asset:** `FVII-SCI03-C011-JOIN-BUDGET-LEDGER`
- **Terminal status:** `TERMINAL_PHASE3_ASSET_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`
- **Grade:** `TYPED_JOIN_BUDGET_AND_BOUNDEDNESS_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`

## Formal surface

- Definitions: 17
- Theorems/lemmas/corollaries: 15
- Formalization targets: FT09, FT16
- Positive scenarios: TTW-S10
- Null/control scenarios: TTW-S22
- Countermodels: CM-11, CM-21
- Phase-3 finite envelopes: P3-E05, P3-E06
- Phase-3 bounded witnesses: P3-W12, P3-W14, P3-W15

## Public theorem declarations

- `FoundationsVII.JoinCostEntry.certified_zero_cost_channel_is_credited`
- `FoundationsVII.JoinCostEntry.paid_entry_is_credited`
- `FoundationsVII.JoinCostEntry.positive_cost_without_payment_or_zero_channel_is_not_credited`
- `FoundationsVII.JoinCostEntry.positive_observer_cost_cannot_be_hidden`
- `FoundationsVII.JoinPaymentLedger.fullyPaid_entries_are_credited`
- `FoundationsVII.JoinPaymentLedger.fullyPaid_has_audit`
- `FoundationsVII.JoinPaymentLedger.typed_cost_projection_preserves_kinds`
- `FoundationsVII.LiveJoinCapacity.finite_live_join_bound`
- `FoundationsVII.Models.Finite.Phase3.capacity_accepted_cardinality`
- `FoundationsVII.Models.Finite.Phase3.capacity_raw_cardinality`
- `FoundationsVII.Models.Finite.Phase3.payment_accepted_cardinality`
- `FoundationsVII.Models.Finite.Phase3.payment_raw_cardinality`
- `FoundationsVII.NoGo.NGVII_09_escape_certified_zero_cost_channel`
- `FoundationsVII.NoGo.NGVII_09_escape_paid_channel`
- `FoundationsVII.NoGo.NGVII_09_no_positive_cost_join_credit_without_payment`

## Scientific boundary

The typed ledger and finite capacity theorem do not identify a universal scalar currency or a domain-independent minimum cost.

The Lean source is complete at text level. Kernel elaboration and executed `#print axioms` results remain the external replay gate.
