# VII-C014 — Birth/contact-surface classification

- **Phase-4 asset:** `FVII-SCI04-C014-BIRTH-PARTICIPANT-CLASSIFICATION`
- **Terminal status:** `TERMINAL_PHASE4_ASSET_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`
- **Grade:** `BIRTH_RELATION_PARTICIPANT_CLASSIFICATION_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`

## Formal surface

- Definitions: 22
- Theorems/lemmas/corollaries: 20
- Formalization targets: FT11, FT12
- Step-3 scenario references: TTW-S06, TTW-S08
- Countermodels: CM-02, CM-17
- Phase-4 finite envelopes: P4-E03
- Phase-4 bounded witnesses: P4-W09, P4-W10, P4-W11, P4-W12

## Public theorem declarations

- `FoundationsVII.BirthRecord.participant_credit_requires_closure_survival`
- `FoundationsVII.BirthRecord.participant_credit_requires_objecthood`
- `FoundationsVII.BirthRecord.relation_only_has_no_participant_credit`
- `FoundationsVII.Models.Finite.Phase4.all_phase4_countermodels_pass`
- `FoundationsVII.Models.Finite.Phase4.all_phase4_scenarios_pass`
- `FoundationsVII.Models.Finite.Phase4.birth_accepted_cardinality`
- `FoundationsVII.Models.Finite.Phase4.birth_exhaustive`
- `FoundationsVII.Models.Finite.Phase4.birth_raw_cardinality`
- `FoundationsVII.Models.Finite.Phase4.phase4_countermodel_count`
- `FoundationsVII.Models.Finite.Phase4.phase4_scenario_count`
- `FoundationsVII.ReachableBirthEvidence.valid_requires_reachable_generator`
- `FoundationsVII.closure_performed_and_closure_undergone_are_distinct`
- `FoundationsVII.contact_can_remain_relation_only`
- `FoundationsVII.every_inherited_birth_class_activates_packaging`
- `FoundationsVII.inheritedBirthClass_mem_all`
- `FoundationsVII.inherited_activation_class_does_not_by_itself_create_participant`
- `FoundationsVII.inherited_birth_class_signatures_are_injective`
- `FoundationsVII.participant_creation_is_conditional_not_automatic`
- `FoundationsVII.system_performed_birth_control`
- `FoundationsVII.system_underwent_birth_control`

## Scientific boundary

Contact may remain relation-only. A newly credited participant requires closure survival and objecthood rather than contact alone.

The Lean source is complete at text level. Kernel elaboration and executed `#print axioms` results remain the external replay gate.
