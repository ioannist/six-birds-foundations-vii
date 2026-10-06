# VII-C013 — Endogenous enablement criterion

- **Phase-4 asset:** `FVII-SCI04-C013-ENDOGENOUS-CRITERION`
- **Terminal status:** `TERMINAL_PHASE4_ASSET_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`
- **Grade:** `EXACT_DECLARED_BOUNDARY_ENDOGENOUS_CRITERION_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`

## Formal surface

- Definitions: 15
- Theorems/lemmas/corollaries: 20
- Formalization targets: FT12, FT16
- Step-3 scenario references: TTW-S02, TTW-S22
- Countermodels: CM-11, CM-17
- Phase-4 finite envelopes: P4-E02
- Phase-4 bounded witnesses: P4-W05, P4-W06, P4-W07, P4-W08

## Public theorem declarations

- `FoundationsVII.EndogenousEnablementProfile.eligible_iff_exact_criterion`
- `FoundationsVII.EndogenousEnablementProfile.eligible_requires_audit`
- `FoundationsVII.EndogenousEnablementProfile.eligible_requires_budget`
- `FoundationsVII.EndogenousEnablementProfile.eligible_requires_carried_generator`
- `FoundationsVII.EndogenousEnablementProfile.eligible_requires_execution`
- `FoundationsVII.EndogenousEnablementProfile.eligible_requires_reachable_generator`
- `FoundationsVII.EndogenousEnablementProfile.hidden_observer_execution_defeats_endogenous_credit`
- `FoundationsVII.EndogenousEnablementProfile.hidden_theorist_execution_defeats_endogenous_credit`
- `FoundationsVII.Models.Finite.Phase4.all_phase4_countermodels_pass`
- `FoundationsVII.Models.Finite.Phase4.all_phase4_scenarios_pass`
- `FoundationsVII.Models.Finite.Phase4.endogenous_accepted_cardinality`
- `FoundationsVII.Models.Finite.Phase4.endogenous_exhaustive`
- `FoundationsVII.Models.Finite.Phase4.endogenous_raw_cardinality`
- `FoundationsVII.Models.Finite.Phase4.phase4_countermodel_count`
- `FoundationsVII.Models.Finite.Phase4.phase4_scenario_count`
- `FoundationsVII.accounted_environmental_input_is_compatible_with_endogeny`
- `FoundationsVII.constructive_endogenous_enablement_exists`
- `FoundationsVII.endogenous_does_not_mean_environmentally_isolated_or_uncaused`
- `FoundationsVII.hidden_observer_enablement_is_not_endogenous`
- `FoundationsVII.theorist_triggered_enablement_is_not_endogenous`

## Scientific boundary

Endogenous means carried, reachable, executed, audited, budgeted, and source-closed at the declared boundary; it does not mean uncaused or environmentally isolated.

The Lean source is complete at text level. Kernel elaboration and executed `#print axioms` results remain the external replay gate.
