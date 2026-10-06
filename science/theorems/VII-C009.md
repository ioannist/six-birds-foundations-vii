# VII-C009 — Strict join certificate and anti-product witness

- **Phase-3 asset:** `FVII-SCI03-C009-STRICT-JOIN-CERTIFICATE`
- **Terminal status:** `TERMINAL_PHASE3_ASSET_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`
- **Grade:** `STRICT_JOIN_CERTIFICATE_AND_ANTI_PRODUCT_THEOREMS_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`

## Formal surface

- Definitions: 16
- Theorems/lemmas/corollaries: 28
- Formalization targets: FT07, FT08
- Positive scenarios: TTW-S07
- Null/control scenarios: TTW-S08, TTW-S15
- Countermodels: CM-03, CM-13, CM-14, CM-16
- Phase-3 finite envelopes: P3-E03, P3-E10
- Phase-3 bounded witnesses: P3-W06, P3-W07, P3-W08, P3-W09

## Public theorem declarations

- `FoundationsVII.AntiProductWitness.coarsening_only_fails`
- `FoundationsVII.AntiProductWitness.relabel_only_fails`
- `FoundationsVII.AntiProductWitness.scheduling_only_fails`
- `FoundationsVII.AntiProductWitness.valid_is_nonfactorizing`
- `FoundationsVII.CompositeClosureWitness.certified_has_objecthood`
- `FoundationsVII.CompositeClosureWitness.certified_of_proof_carrying_witness`
- `FoundationsVII.CompositeClosureWitness.certified_retains_both_parents`
- `FoundationsVII.CompositeClosureWitness.left_retention_from_embedding`
- `FoundationsVII.CompositeClosureWitness.objecthood_from_fixed_point`
- `FoundationsVII.CompositeClosureWitness.right_retention_from_embedding`
- `FoundationsVII.Models.Finite.Phase3.directionless_strict_case_exists`
- `FoundationsVII.Models.Finite.Phase3.strict_join_status_count`
- `FoundationsVII.Models.Finite.Phase3.strictness_accepted_cardinality`
- `FoundationsVII.Models.Finite.Phase3.strictness_canonical_cardinality`
- `FoundationsVII.Models.Finite.Phase3.strictness_raw_labelled_cardinality`
- `FoundationsVII.NoGo.NGVII_06_escape_complete_strict_join_certificate`
- `FoundationsVII.NoGo.NGVII_06_no_join_from_contact_alone`
- `FoundationsVII.NoGo.NGVII_07_escape_anti_product_witness`
- `FoundationsVII.NoGo.NGVII_07_no_product_common_refinement_strictness_credit`
- `FoundationsVII.StrictJoinEvidence.certified_does_not_supply_directionality`
- `FoundationsVII.StrictJoinEvidence.certified_has_anti_product_novelty`
- `FoundationsVII.StrictJoinEvidence.certified_has_objecthood`
- `FoundationsVII.StrictJoinEvidence.certified_has_source_and_budget_gates`
- `FoundationsVII.StrictJoinEvidence.certified_retains_both_parents`
- `FoundationsVII.StrictJoinProfile.anti_product_does_not_imply_objecthood`
- `FoundationsVII.StrictJoinProfile.directionless_strict_profile_exists`
- `FoundationsVII.StrictJoinProfile.strictness_does_not_imply_parent_retention`
- `FoundationsVII.finite_composite_objecthood_control`

## Scientific boundary

Strictness remains separate from objecthood and directionality; anti-product evidence alone supplies neither.

The Lean source is complete at text level. Kernel elaboration and executed `#print axioms` results remain the external replay gate.
