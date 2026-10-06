# VII-C003 — Bootstrap obstruction theorem

**Phase-2 asset:** `FVII-SCI02-C003-BOOTSTRAP-OBSTRUCTION`  
**Terminal status:** `TERMINAL_PHASE2_ASSET_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`  
**Grade:** `NO_GO_AND_ESCAPE_THEOREMS_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`

## Formal surface

- Definitions: 14
- Theorems/lemmas/corollaries: 17
- Formalization targets: FT03, FT18
- Positive scenarios: TTW-S01
- Null/control scenarios: TTW-S02
- Countermodels: CM-19, CM-20
- New bounded witnesses: P2-W12

## Public theorem declarations

- `FoundationsVII.AdmissionRegime.admitted_seed_authorizes_first_extension`
- `FoundationsVII.AdmissionRegime.bootstrap_no_go_applies_implies_no_first_extension`
- `FoundationsVII.AdmissionRegime.no_first_extension_without_seed_or_reachable_generator`
- `FoundationsVII.AdmissionRegime.open_external_provision_authorizes_first_extension`
- `FoundationsVII.AdmissionRegime.open_family_is_not_covered_by_closed_bootstrap_hypotheses`
- `FoundationsVII.AdmissionRegime.reachable_generator_authorizes_first_extension`
- `FoundationsVII.Models.Finite.Phase2.bootstrap_admissible_cardinality`
- `FoundationsVII.Models.Finite.Phase2.bootstrap_law_exhaustive`
- `FoundationsVII.Models.Finite.Phase2.bootstrap_raw_cardinality`
- `FoundationsVII.NeutralProvisioningCertificate.neutral_provisioning_authorizes_first_extension`
- `FoundationsVII.NeutralProvisioningCertificate.retrospective_stocking_cannot_earn_neutral_credit`
- `FoundationsVII.NeutralProvisioningCertificate.source_laundering_through_system_generation_fails`
- `FoundationsVII.NeutralProvisioningCertificate.system_generated_source_cannot_earn_neutral_credit`
- `FoundationsVII.NoGo.NGVII_01_escape_admitted_seed`
- `FoundationsVII.NoGo.NGVII_01_escape_open_external_provision`
- `FoundationsVII.NoGo.NGVII_01_escape_reachable_generator`
- `FoundationsVII.NoGo.NGVII_01_no_first_extension_without_seed_or_generator`

## Scientific boundary

The bootstrap obstruction is scoped to a declared closed family and permits admitted seeds, reachable generators, and explicit external provision.

The source proof is complete at the Lean text level. Kernel elaboration and `#print axioms` replay remain an explicit external execution gate.
