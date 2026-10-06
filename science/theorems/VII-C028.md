# VII-C028 — Primitive-operation algebra readiness criterion

- **Phase-4 asset:** `FVII-SCI04-C028-PRIMITIVE-ALGEBRA-DECISION`
- **Terminal status:** `TERMINAL_PHASE4_ASSET_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`
- **Grade:** `FULL_PRIMITIVE_ALGEBRA_DEFERRED_SMALL_RESOURCE_FRAGMENT_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`

## Formal surface

- Definitions: 13
- Theorems/lemmas/corollaries: 13
- Formalization targets: FT14
- Step-3 scenario references: TTW-S16, TTW-S12
- Countermodels: CM-24
- Phase-4 finite envelopes: P4-E12
- Phase-4 bounded witnesses: P4-W31, P4-W32

## Public theorem declarations

- `FoundationsVII.Models.Finite.Phase4.algebra_accepted_cardinality`
- `FoundationsVII.Models.Finite.Phase4.algebra_exhaustive`
- `FoundationsVII.Models.Finite.Phase4.algebra_raw_cardinality`
- `FoundationsVII.Models.Finite.Phase4.all_phase4_countermodels_pass`
- `FoundationsVII.Models.Finite.Phase4.all_phase4_scenarios_pass`
- `FoundationsVII.Models.Finite.Phase4.phase4_countermodel_count`
- `FoundationsVII.Models.Finite.Phase4.phase4_scenario_count`
- `FoundationsVII.current_full_primitive_algebra_is_not_ready`
- `FoundationsVII.full_algebra_reopen_condition_is_exact`
- `FoundationsVII.full_generators_relations_program_deferred_with_formal_reopen_condition`
- `FoundationsVII.resource_delta_fragment_has_left_identity`
- `FoundationsVII.resource_delta_fragment_has_right_identity`
- `FoundationsVII.resource_delta_fragment_is_associative`

## Scientific boundary

The full generators-and-relations program remains deferred. The landed resource-delta fragment does not establish a complete universal interaction algebra.

The Lean source is complete at text level. Kernel elaboration and executed `#print axioms` results remain the external replay gate.
