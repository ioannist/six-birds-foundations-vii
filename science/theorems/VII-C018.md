# VII-C018 — Admission confluence and seed-dependence law

- **Phase-4 asset:** `FVII-SCI04-C018-CONFLUENCE-SEED-DEPENDENCE`
- **Terminal status:** `TERMINAL_PHASE4_ASSET_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`
- **Grade:** `DECLARED_FINITE_CONFLUENCE_AND_SEED_DEPENDENCE_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`

## Formal surface

- Definitions: 22
- Theorems/lemmas/corollaries: 17
- Formalization targets: FT14
- Step-3 scenario references: TTW-S16, TTW-S24
- Countermodels: CM-23, CM-24
- Phase-4 finite envelopes: P4-E07, P4-E08
- Phase-4 bounded witnesses: P4-W22, P4-W23, P4-W24, P4-W25

## Public theorem declarations

- `FoundationsVII.CriticalPair.resolved_of_joinable_audit_equivalent`
- `FoundationsVII.FiniteAdmissionSystem.finite_critical_pair_criterion_iff_confluent`
- `FoundationsVII.Models.Finite.Phase4.all_phase4_countermodels_pass`
- `FoundationsVII.Models.Finite.Phase4.all_phase4_scenarios_pass`
- `FoundationsVII.Models.Finite.Phase4.confluence_accepted_cardinality`
- `FoundationsVII.Models.Finite.Phase4.confluence_exhaustive`
- `FoundationsVII.Models.Finite.Phase4.confluence_raw_cardinality`
- `FoundationsVII.Models.Finite.Phase4.phase4_countermodel_count`
- `FoundationsVII.Models.Finite.Phase4.phase4_scenario_count`
- `FoundationsVII.Models.Finite.Phase4.seed_accepted_cardinality`
- `FoundationsVII.Models.Finite.Phase4.seed_exhaustive`
- `FoundationsVII.Models.Finite.Phase4.seed_raw_cardinality`
- `FoundationsVII.finite_confluent_positive_model`
- `FoundationsVII.finite_nonconfluent_countermodel`
- `FoundationsVII.one_commuting_square_does_not_establish_global_confluence`
- `FoundationsVII.presentation_difference_is_not_seed_dependence`
- `FoundationsVII.seed_partition_can_change_terminal_package`

## Scientific boundary

Confluence is proved only for the declared closed finite system, and seed dependence is separated from presentation-only differences.

The Lean source is complete at text level. Kernel elaboration and executed `#print axioms` results remain the external replay gate.
