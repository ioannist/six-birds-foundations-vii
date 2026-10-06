# VII-C005 — Common-origin non-transfer law

**Phase-2 asset:** `FVII-SCI02-C005-ORIGIN-ACCESS-NONTRANSFER`  
**Terminal status:** `TERMINAL_PHASE2_ASSET_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`  
**Grade:** `NONTRANSFER_THEOREMS_AND_FINITE_COUNTERMODELS_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`

## Formal surface

- Definitions: 18
- Theorems/lemmas/corollaries: 16
- Formalization targets: FT05, FT17
- Positive scenarios: TTW-S05
- Null/control scenarios: TTW-S23
- Countermodels: CM-01, CM-12, CM-26
- New bounded witnesses: P2-W09, P2-W10, P2-W14

## Public theorem declarations

- `FoundationsVII.LensTransferCase.certified_adapter_licenses_totality_transfer`
- `FoundationsVII.LensTransferCase.no_automatic_total_lens_transfer`
- `FoundationsVII.LensTransferCase.nonpartial_target_licenses_totality_transfer`
- `FoundationsVII.Models.Finite.Phase2.origin_admissible_cardinality`
- `FoundationsVII.Models.Finite.Phase2.origin_canonical_cardinality`
- `FoundationsVII.Models.Finite.Phase2.origin_raw_labelled_cardinality`
- `FoundationsVII.Models.Finite.Phase2.source_independence_is_complementary_to_same_origin_in_canonical_family`
- `FoundationsVII.Models.Finite.Phase2.totality_admissible_cardinality`
- `FoundationsVII.Models.Finite.Phase2.totality_raw_cardinality`
- `FoundationsVII.Models.Finite.Phase2.totality_transfer_requires_adapter_on_partial_targets`
- `FoundationsVII.NoGo.NGVII_04_escape_certified_adapter`
- `FoundationsVII.NoGo.NGVII_04_no_automatic_total_lens_transfer`
- `FoundationsVII.PackageAccess.certified_peer_transport_is_sufficient_for_shared_access`
- `FoundationsVII.PackageAccess.common_origin_countermodel`
- `FoundationsVII.PackageAccess.common_origin_does_not_imply_shared_access`
- `FoundationsVII.PackageAccess.shared_access_does_not_imply_source_independence`

## Scientific boundary

Common origin, carrier, or instrument does not establish shared access or source independence; adapter theorems remain necessary.

The source proof is complete at the Lean text level. Kernel elaboration and `#print axioms` replay remain an explicit external execution gate.
