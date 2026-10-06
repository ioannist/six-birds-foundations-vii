# VII-C001 — Accessible-domain state normal form

**Phase-2 asset:** `FVII-SCI02-C001-ACCESS-NORMAL-FORM`  
**Terminal status:** `TERMINAL_PHASE2_ASSET_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`  
**Grade:** `DEFINITION_AND_THEOREM_SET_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`

## Formal surface

- Definitions: 25
- Theorems/lemmas/corollaries: 23
- Formalization targets: FT01, FT02
- Positive scenarios: TTW-S19
- Null/control scenarios: TTW-S20, TTW-S21
- Countermodels: CM-08, CM-09, CM-12
- New bounded witnesses: P2-W01, P2-W02, P2-W06

## Public theorem declarations

- `FoundationsVII.DomainState.AccessRigid.refl`
- `FoundationsVII.DomainState.AccessRigid.symm`
- `FoundationsVII.DomainState.AccessRigid.trans`
- `FoundationsVII.DomainState.AuxiliaryRecoveryCertificate.absent_operation_blocks_valid_recovery`
- `FoundationsVII.DomainState.AuxiliaryRecoveryCertificate.spurious_rigidity_is_not_a_recovery_certificate`
- `FoundationsVII.DomainState.AuxiliaryRecoveryCertificate.valid_recovery_has_present_operation_and_adapter`
- `FoundationsVII.DomainState.ScopeChange.preserves_theory_and_interface`
- `FoundationsVII.DomainState.admissibility_does_not_imply_reachability`
- `FoundationsVII.DomainState.admissibility_does_not_imply_recoverability`
- `FoundationsVII.DomainState.exposure_does_not_imply_recoverability`
- `FoundationsVII.DomainState.expressibility_does_not_imply_presence`
- `FoundationsVII.DomainState.normalForm_eq`
- `FoundationsVII.DomainState.normalForm_idempotent`
- `FoundationsVII.DomainState.presence_does_not_imply_exposure`
- `FoundationsVII.DomainState.reachability_does_not_imply_occurrence`
- `FoundationsVII.DomainState.recoverability_and_admissibility_are_incomparable`
- `FoundationsVII.DomainState.recoverability_does_not_imply_admissibility`
- `FoundationsVII.DomainState.same_determination_can_have_different_exposure`
- `FoundationsVII.DomainState.statusVector_withStatusVector`
- `FoundationsVII.DomainState.withStatusVector_statusVector`
- `FoundationsVII.Models.Finite.Phase2.access_raw_cardinality`
- `FoundationsVII.Models.Finite.Phase2.coherent_access_cardinality`
- `FoundationsVII.Models.Finite.Phase2.coherent_access_cases_respect_implication_spine`

## Scientific boundary

The Boolean normal form is a typed finite representation, not a universal claim that all access phenomena reduce to seven bits.

The source proof is complete at the Lean text level. Kernel elaboration and `#print axioms` replay remain an explicit external execution gate.
