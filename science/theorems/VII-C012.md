# VII-C012 — Enablement record and attribution calculus

- **Phase-4 asset:** `FVII-SCI04-C012-ENABLEMENT-ATTRIBUTION`
- **Terminal status:** `TERMINAL_PHASE4_ASSET_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`
- **Grade:** `SOURCE_TYPED_ENABLEMENT_ATTRIBUTION_CALCULUS_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`

## Formal surface

- Definitions: 21
- Theorems/lemmas/corollaries: 18
- Formalization targets: FT11
- Step-3 scenario references: TTW-S02, TTW-S21, TTW-S22
- Countermodels: CM-06, CM-07, CM-17
- Phase-4 finite envelopes: P4-E01
- Phase-4 bounded witnesses: P4-W01, P4-W02, P4-W03, P4-W04

## Public theorem declarations

- `FoundationsVII.AttributedEnablement.hidden_execution_defeats_attribution`
- `FoundationsVII.AttributedEnablement.wellFormed_has_audit_accounting`
- `FoundationsVII.AttributedEnablement.wellFormed_has_budget_accounting`
- `FoundationsVII.AttributedEnablement.wellFormed_has_execution_witness`
- `FoundationsVII.AttributedEnablement.wellFormed_has_no_hidden_executor`
- `FoundationsVII.AttributedEnablement.wellFormed_has_typed_source`
- `FoundationsVII.AttributionEvidence.honest_refinement_preserves_source_root`
- `FoundationsVII.AttributionEvidence.valid_has_no_hidden_executor`
- `FoundationsVII.AttributionRefinement.stable_preserves_attribution_root`
- `FoundationsVII.Models.Finite.Phase4.all_phase4_countermodels_pass`
- `FoundationsVII.Models.Finite.Phase4.all_phase4_scenarios_pass`
- `FoundationsVII.Models.Finite.Phase4.attribution_accepted_cardinality`
- `FoundationsVII.Models.Finite.Phase4.attribution_exhaustive`
- `FoundationsVII.Models.Finite.Phase4.attribution_raw_cardinality`
- `FoundationsVII.Models.Finite.Phase4.phase4_countermodel_count`
- `FoundationsVII.Models.Finite.Phase4.phase4_scenario_count`
- `FoundationsVII.attribution_does_not_imply_descent_sufficiency_causation_or_endogeny`
- `FoundationsVII.enablementSource_mem_all`

## Scientific boundary

Attribution records provenance and execution responsibility; it does not by itself establish descent, sufficiency, causation, or endogeny.

The Lean source is complete at text level. Kernel elaboration and executed `#print axioms` results remain the external replay gate.
