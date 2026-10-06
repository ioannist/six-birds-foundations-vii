# VII-C032 — Interaction arrow, irreversibility, and cross-time contact

- **Phase-4 asset:** `FVII-SCI04-C032-ARROW-CROSS-TIME`
- **Terminal status:** `TERMINAL_PHASE4_ASSET_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`
- **Grade:** `INDEPENDENT_DRIVE_ARROW_AND_CROSS_TIME_WITNESS_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`

## Formal surface

- Definitions: 32
- Theorems/lemmas/corollaries: 26
- Formalization targets: FT15
- Step-3 scenario references: TTW-S17, TTW-S18
- Countermodels: CM-10, CM-24
- Phase-4 finite envelopes: P4-E10, P4-E11
- Phase-4 bounded witnesses: P4-W27, P4-W28, P4-W29, P4-W30

## Public theorem declarations

- `FoundationsVII.CrossTimeContact.valid_under_admissible_reparameterization`
- `FoundationsVII.Models.Finite.Phase4.all_phase4_countermodels_pass`
- `FoundationsVII.Models.Finite.Phase4.all_phase4_scenarios_pass`
- `FoundationsVII.Models.Finite.Phase4.arrow_accepted_cardinality`
- `FoundationsVII.Models.Finite.Phase4.arrow_exhaustive`
- `FoundationsVII.Models.Finite.Phase4.arrow_raw_cardinality`
- `FoundationsVII.Models.Finite.Phase4.cross_time_accepted_cardinality`
- `FoundationsVII.Models.Finite.Phase4.cross_time_exhaustive`
- `FoundationsVII.Models.Finite.Phase4.cross_time_raw_cardinality`
- `FoundationsVII.Models.Finite.Phase4.finite_driven_arrow_exists`
- `FoundationsVII.Models.Finite.Phase4.finite_holonomy_zero_arrow_exists`
- `FoundationsVII.Models.Finite.Phase4.phase4_countermodel_count`
- `FoundationsVII.Models.Finite.Phase4.phase4_scenario_count`
- `FoundationsVII.NoGo.NGVII_10_escape_independent_driven_arrow`
- `FoundationsVII.NoGo.NGVII_10_holonomy_zero_arrow_control`
- `FoundationsVII.NoGo.NGVII_10_no_arrow_from_holonomy_alone`
- `FoundationsVII.constructive_interaction_holonomy`
- `FoundationsVII.driven_arrow_positive_control`
- `FoundationsVII.driven_arrow_requires_independent_drive_certificate`
- `FoundationsVII.holonomy_with_zero_arrow_witness`
- `FoundationsVII.incommensurable_times_require_explicit_order_witness`
- `FoundationsVII.partial_order_contact_survives_clock_reparameterization`
- `FoundationsVII.partial_order_cross_time_contact_exists`
- `FoundationsVII.reversal_null_and_driven_controls_are_distinct`
- `FoundationsVII.synchronization_does_not_require_equal_local_clock_readings`
- `FoundationsVII.synchronized_cross_time_contact_exists`

## Scientific boundary

Holonomy alone carries zero arrow credit. Cross-time contact uses explicit synchronization or partial-order witnesses and assumes no universal simultaneity.

The Lean source is complete at text level. Kernel elaboration and executed `#print axioms` results remain the external replay gate.
