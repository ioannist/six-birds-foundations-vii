# VII-C017 — Interaction-order residue and holonomy

- **Phase-4 asset:** `FVII-SCI04-C017-ORDER-RESIDUE-HOLONOMY`
- **Terminal status:** `TERMINAL_PHASE4_ASSET_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`
- **Grade:** `ORDER_RESIDUE_AND_INTERACTION_HOLONOMY_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`

## Formal surface

- Definitions: 27
- Theorems/lemmas/corollaries: 19
- Formalization targets: FT14, FT15
- Step-3 scenario references: TTW-S16, TTW-S17, TTW-S18
- Countermodels: CM-10, CM-24
- Phase-4 finite envelopes: P4-E09, P4-E10
- Phase-4 bounded witnesses: P4-W26

## Public theorem declarations

- `FoundationsVII.Models.Finite.Phase4.all_phase4_countermodels_pass`
- `FoundationsVII.Models.Finite.Phase4.all_phase4_scenarios_pass`
- `FoundationsVII.Models.Finite.Phase4.arrow_accepted_cardinality`
- `FoundationsVII.Models.Finite.Phase4.arrow_exhaustive`
- `FoundationsVII.Models.Finite.Phase4.arrow_raw_cardinality`
- `FoundationsVII.Models.Finite.Phase4.finite_holonomy_zero_arrow_exists`
- `FoundationsVII.Models.Finite.Phase4.holonomy_accepted_cardinality`
- `FoundationsVII.Models.Finite.Phase4.holonomy_exhaustive`
- `FoundationsVII.Models.Finite.Phase4.holonomy_raw_cardinality`
- `FoundationsVII.Models.Finite.Phase4.phase4_countermodel_count`
- `FoundationsVII.Models.Finite.Phase4.phase4_scenario_count`
- `FoundationsVII.NoGo.NGVII_10_escape_independent_driven_arrow`
- `FoundationsVII.NoGo.NGVII_10_holonomy_zero_arrow_control`
- `FoundationsVII.NoGo.NGVII_10_no_arrow_from_holonomy_alone`
- `FoundationsVII.constructive_interaction_holonomy`
- `FoundationsVII.driven_arrow_positive_control`
- `FoundationsVII.driven_arrow_requires_independent_drive_certificate`
- `FoundationsVII.holonomy_with_zero_arrow_witness`
- `FoundationsVII.reversal_null_and_driven_controls_are_distinct`

## Scientific boundary

Order residue and holonomy are route effects on one typed target; neither supplies directionality.

The Lean source is complete at text level. Kernel elaboration and executed `#print axioms` results remain the external replay gate.
