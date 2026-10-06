# VII-C004 — Neutral seed and provisioning certificate

**Phase-2 asset:** `FVII-SCI02-C004-NEUTRAL-PROVISIONING`  
**Terminal status:** `TERMINAL_PHASE2_ASSET_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`  
**Grade:** `CERTIFICATE_SCHEMA_AND_ANTI_LAUNDERING_THEOREMS_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`

## Formal surface

- Definitions: 23
- Theorems/lemmas/corollaries: 21
- Formalization targets: FT04, FT05
- Positive scenarios: TTW-S02
- Null/control scenarios: TTW-S05
- Countermodels: CM-01, CM-19
- New bounded witnesses: none

## Public theorem declarations

- `FoundationsVII.AdmissionRegime.admitted_seed_authorizes_first_extension`
- `FoundationsVII.AdmissionRegime.bootstrap_no_go_applies_implies_no_first_extension`
- `FoundationsVII.AdmissionRegime.no_first_extension_without_seed_or_reachable_generator`
- `FoundationsVII.AdmissionRegime.open_external_provision_authorizes_first_extension`
- `FoundationsVII.AdmissionRegime.open_family_is_not_covered_by_closed_bootstrap_hypotheses`
- `FoundationsVII.AdmissionRegime.reachable_generator_authorizes_first_extension`
- `FoundationsVII.CommitmentUse.SameNeutralSeedClass.refl`
- `FoundationsVII.CommitmentUse.SameNeutralSeedClass.symm`
- `FoundationsVII.CommitmentUse.SameNeutralSeedClass.trans`
- `FoundationsVII.CommitmentUse.expired_commitment_is_not_active`
- `FoundationsVII.CommitmentUse.prospectively_certified_has_temporal_precedence`
- `FoundationsVII.CommitmentUse.prospectively_certified_is_neutral_seed_equivalent`
- `FoundationsVII.CommitmentUse.retrospective_predicate_cannot_discharge_prospective_certificate`
- `FoundationsVII.CommitmentUse.unused_reserved_budget_is_refunded`
- `FoundationsVII.Models.Finite.Phase2.commitment_admissible_cardinality`
- `FoundationsVII.Models.Finite.Phase2.commitment_raw_cardinality`
- `FoundationsVII.NeutralProvisioningCertificate.neutral_provisioning_authorizes_first_extension`
- `FoundationsVII.NeutralProvisioningCertificate.retrospective_stocking_cannot_earn_neutral_credit`
- `FoundationsVII.NeutralProvisioningCertificate.source_laundering_through_system_generation_fails`
- `FoundationsVII.NeutralProvisioningCertificate.system_generated_source_cannot_earn_neutral_credit`
- `FoundationsVII.PrecedenceCertificate.impossible_when_not_precedent`

## Scientific boundary

Neutral credit requires prospective, task-blind, outcome-independent provision; post-hoc stocking and system-generated laundering are excluded.

The source proof is complete at the Lean text level. Kernel elaboration and `#print axioms` replay remain an explicit external execution gate.
