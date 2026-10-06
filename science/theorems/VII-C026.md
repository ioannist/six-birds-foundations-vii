# VII-C026 — Categorical reduction decision

- **Phase-3 asset:** `FVII-SCI03-C026-CATEGORICAL-DECISION`
- **Terminal status:** `TERMINAL_PHASE3_ASSET_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`
- **Grade:** `UNCONDITIONAL_CATEGORICAL_REDUCTION_REJECTED_SPECIAL_CASE_THEOREMS_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`

## Formal surface

- Definitions: 10
- Theorems/lemmas/corollaries: 11
- Formalization targets: FT07
- Positive scenarios: TTW-S07
- Null/control scenarios: TTW-S08
- Countermodels: CM-13, CM-27
- Phase-3 finite envelopes: P3-E10
- Phase-3 bounded witnesses: P3-W25, P3-W26

## Public theorem declarations

- `FoundationsVII.FinitePackageCategory.wellFormed_has_checked_category_laws`
- `FoundationsVII.Models.Finite.Phase3.categorical_accepted_cardinality`
- `FoundationsVII.Models.Finite.Phase3.categorical_raw_cardinality`
- `FoundationsVII.Models.Finite.Phase3.strict_join_without_listed_universal_construction_exists`
- `FoundationsVII.UniversalConstructionCertificate.representation_preserves_declared_parents`
- `FoundationsVII.UniversalConstructionCertificate.representation_requires_explicit_universal_property`
- `FoundationsVII.UniversalConstructionCertificate.represents_strict_join_iff_valid_and_independently_novel`
- `FoundationsVII.finite_package_category_control_is_well_formed`
- `FoundationsVII.mere_product_is_not_strict_join_credit`
- `FoundationsVII.special_case_categorical_representation_is_conditional`
- `FoundationsVII.unconditional_categorical_reduction_countermodel`

## Scientific boundary

No unconditional product, pullback, or pushout representation is claimed; only explicitly checked special cases receive categorical credit.

The Lean source is complete at text level. Kernel elaboration and executed `#print axioms` results remain the external replay gate.
