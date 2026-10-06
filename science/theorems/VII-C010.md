# VII-C010 — Source-independence gate

- **Phase-3 asset:** `FVII-SCI03-C010-SOURCE-INDEPENDENCE-GATE`
- **Terminal status:** `TERMINAL_PHASE3_ASSET_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`
- **Grade:** `SOURCE_INDEPENDENCE_GATE_AND_NO_GO_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`

## Formal surface

- Definitions: 14
- Theorems/lemmas/corollaries: 14
- Formalization targets: FT05
- Positive scenarios: TTW-S05
- Null/control scenarios: TTW-S11
- Countermodels: CM-01, CM-26
- Phase-3 finite envelopes: P3-E04
- Phase-3 bounded witnesses: P3-W10, P3-W11

## Public theorem declarations

- `FoundationsVII.HonestBridgeRecord.certified_preserves_kind_metadata`
- `FoundationsVII.HonestBridgeRecord.certified_records_bridged_kind`
- `FoundationsVII.HonestBridgeRecord.certified_records_declared_origin`
- `FoundationsVII.Models.Finite.Phase3.source_lineage_accepted_cardinality`
- `FoundationsVII.Models.Finite.Phase3.source_lineage_raw_cardinality`
- `FoundationsVII.NoGo.NGVII_02_escape_witnessed_independent_contact`
- `FoundationsVII.NoGo.NGVII_02_no_resemblance_only_independence_join`
- `FoundationsVII.NoGo.NGVII_08_escape_disjoint_root_certificate`
- `FoundationsVII.NoGo.NGVII_08_no_one_lineage_source_independence_credit`
- `FoundationsVII.SourceAncestry.independence_excludes_same_lineage`
- `FoundationsVII.SourceAncestry.same_lineage_excludes_independence`
- `FoundationsVII.SourceIndependenceGate.behavioral_nonfactorization_alone_is_insufficient`
- `FoundationsVII.SourceIndependenceGate.certified_gate_separates_source_and_behavior`
- `FoundationsVII.SourceIndependenceGate.same_lineage_fails_independence_sensitive_credit`

## Scientific boundary

Source independence is required only for independence-sensitive credit and is not equated with behavioral novelty or causal independence.

The Lean source is complete at text level. Kernel elaboration and executed `#print axioms` results remain the external replay gate.
