# VII-C022 — Exposure, recoverability, admissibility, and rigidity calculus

**Phase-2 asset:** `FVII-SCI02-C022-ACCESS-RIGIDITY`  
**Terminal status:** `TERMINAL_PHASE2_ASSET_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`  
**Grade:** `ACCESS_SEPARATION_AND_RIGIDITY_CALCULUS_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`

## Formal surface

- Definitions: 25
- Theorems/lemmas/corollaries: 23
- Formalization targets: FT01, FT17
- Positive scenarios: TTW-S15
- Null/control scenarios: TTW-S19
- Countermodels: CM-03, CM-12
- New bounded witnesses: P2-W03, P2-W04, P2-W05

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

No total order among exposure, recoverability, and admissibility is asserted.

The source proof is complete at the Lean text level. Kernel elaboration and `#print axioms` replay remain an explicit external execution gate.
