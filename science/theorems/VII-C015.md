# VII-C015 — Typed transmission and descent-fidelity law

- **Phase-4 asset:** `FVII-SCI04-C015-TRANSMISSION-DESCENT-FIDELITY`
- **Terminal status:** `TERMINAL_PHASE4_ASSET_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`
- **Grade:** `TYPED_TRANSMISSION_DESCENT_FIDELITY_AND_CAUSAL_SEPARATION_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`

## Formal surface

- Definitions: 26
- Theorems/lemmas/corollaries: 20
- Formalization targets: FT13, FT19
- Step-3 scenario references: TTW-S16, TTW-S24
- Countermodels: CM-06, CM-22, CM-23
- Phase-4 finite envelopes: P4-E04
- Phase-4 bounded witnesses: P4-W13, P4-W14, P4-W15, P4-W16, P4-W17

## Public theorem declarations

- `FoundationsVII.DescentSquare.fidelity_is_commuting_square`
- `FoundationsVII.Models.Finite.Phase4.all_phase4_countermodels_pass`
- `FoundationsVII.Models.Finite.Phase4.all_phase4_scenarios_pass`
- `FoundationsVII.Models.Finite.Phase4.phase4_countermodel_count`
- `FoundationsVII.Models.Finite.Phase4.phase4_scenario_count`
- `FoundationsVII.Models.Finite.Phase4.transmission_accepted_cardinality`
- `FoundationsVII.Models.Finite.Phase4.transmission_exhaustive`
- `FoundationsVII.Models.Finite.Phase4.transmission_raw_cardinality`
- `FoundationsVII.ResidualFlow.accounted_balance`
- `FoundationsVII.ResidualFlow.composed_debt_accumulates`
- `FoundationsVII.ResidualFlow.settled_debt_bounded`
- `FoundationsVII.TransmissionFidelity.valid_preserves_budget`
- `FoundationsVII.TransmissionFidelity.valid_preserves_source`
- `FoundationsVII.TransmissionFidelity.valid_records_ambiguity`
- `FoundationsVII.TransmissionFidelity.valid_records_loss`
- `FoundationsVII.TransmissionRecord.pure_downward_selection_cannot_create_absent_lower_fact`
- `FoundationsVII.TransmissionRecord.pure_downward_selection_preserves_present_lower_facts`
- `FoundationsVII.all_three_transmission_directions_have_positive_controls`
- `FoundationsVII.structural_downward_selection_is_not_automatically_causal`
- `FoundationsVII.transmissionDirection_mem_all`

## Scientific boundary

Faithful downward structural selection is not automatically a top-down causal channel and cannot create an absent lower-carrier fact without an explicit insertion source.

The Lean source is complete at text level. Kernel elaboration and executed `#print axioms` results remain the external replay gate.
