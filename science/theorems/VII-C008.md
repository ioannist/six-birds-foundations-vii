# VII-C008 — Join existence and obstruction status calculus

- **Phase-3 asset:** `FVII-SCI03-C008-JOIN-STATUS-CALCULUS`
- **Terminal status:** `TERMINAL_PHASE3_ASSET_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`
- **Grade:** `SCOPED_JOIN_STATUS_CALCULUS_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`

## Formal surface

- Definitions: 21
- Theorems/lemmas/corollaries: 19
- Formalization targets: FT09, FT10
- Positive scenarios: TTW-S06
- Null/control scenarios: TTW-S07, TTW-S08, TTW-S10, TTW-S13
- Countermodels: CM-02, CM-13, CM-27
- Phase-3 finite envelopes: P3-E02
- Phase-3 bounded witnesses: P3-W04, P3-W05

## Public theorem declarations

- `FoundationsVII.JoinAssessment.commonRefinement_ne_strictJoin`
- `FoundationsVII.JoinAssessment.contact_ne_strictJoin`
- `FoundationsVII.JoinAssessment.contact_refinement_and_composite_axes_may_overlap`
- `FoundationsVII.JoinAssessment.noContact_ne_contact`
- `FoundationsVII.JoinAssessment.noninteraction_status_constructor`
- `FoundationsVII.JoinAssessment.obstructed_ne_certifiedNoninteraction`
- `FoundationsVII.JoinAssessment.obstruction_status_constructor`
- `FoundationsVII.JoinAssessment.overlapping_axes_classify_as_lawful_composite`
- `FoundationsVII.JoinAssessment.strictEligibleB_eq_true_iff`
- `FoundationsVII.JoinAssessment.strict_status_constructor`
- `FoundationsVII.Models.Finite.Phase3.all_phase3_countermodels_pass`
- `FoundationsVII.Models.Finite.Phase3.all_phase3_scenarios_pass`
- `FoundationsVII.Models.Finite.Phase3.join_status_accepted_cardinality`
- `FoundationsVII.Models.Finite.Phase3.join_status_canonical_cardinality`
- `FoundationsVII.Models.Finite.Phase3.join_status_raw_labelled_cardinality`
- `FoundationsVII.Models.Finite.Phase3.phase3_countermodel_count`
- `FoundationsVII.Models.Finite.Phase3.phase3_scenario_count`
- `FoundationsVII.Models.Finite.Phase3.phase3_source_control_22_pass`
- `FoundationsVII.Models.Finite.Phase3.status_partition_complete`

## Scientific boundary

The status classifier is total only over the declared finite evidence family and is not a universal classification of every possible theory interaction.

The Lean source is complete at text level. Kernel elaboration and executed `#print axioms` results remain the external replay gate.
