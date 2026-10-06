# VII-C007 — Join-entry record normal form

- **Phase-3 asset:** `FVII-SCI03-C007-JOIN-ENTRY-NORMAL-FORM`
- **Terminal status:** `TERMINAL_PHASE3_ASSET_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`
- **Grade:** `JOIN_ENTRY_NORMAL_FORM_AND_OMISSION_THEOREMS_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`

## Formal surface

- Definitions: 14
- Theorems/lemmas/corollaries: 18
- Formalization targets: FT06, FT07
- Positive scenarios: TTW-S06
- Null/control scenarios: TTW-S08, TTW-S12
- Countermodels: CM-02, CM-03, CM-14
- Phase-3 finite envelopes: P3-E01, P3-E02
- Phase-3 bounded witnesses: P3-W03

## Public theorem declarations

- `FoundationsVII.JoinEntryFieldProfile.weak_status_checker_has_budget_false_positive`
- `FoundationsVII.JoinEntryFieldProfile.weak_status_checker_has_contact_false_positive`
- `FoundationsVII.JoinEntryFieldProfile.weak_status_checker_has_source_false_positive`
- `FoundationsVII.JoinEntryRecord.completed_has_no_recorded_obstruction`
- `FoundationsVII.JoinEntryRecord.completed_has_witnessed_contact`
- `FoundationsVII.JoinEntryRecord.failed_ne_completed`
- `FoundationsVII.JoinEntryRecord.obstructed_has_obstruction`
- `FoundationsVII.JoinEntryRecord.obstructed_ne_completed`
- `FoundationsVII.JoinEntryRecord.pending_ne_completed`
- `FoundationsVII.JoinEntryRecord.wellFormed_has_append_only_audit_surface`
- `FoundationsVII.JoinEntryRecord.wellFormed_has_budget_ledger`
- `FoundationsVII.JoinEntryRecord.wellFormed_has_source_ledger`
- `FoundationsVII.JoinEntryRecord.wellFormed_has_two_parents`
- `FoundationsVII.JoinEntryRecord.wellFormed_has_typed_contact_surface`
- `FoundationsVII.JoinEntryRecord.witnessed_state_has_contact`
- `FoundationsVII.Models.Finite.Phase3.contact_transport_accepted_cardinality`
- `FoundationsVII.Models.Finite.Phase3.contact_transport_exhaustive`
- `FoundationsVII.Models.Finite.Phase3.contact_transport_raw_cardinality`

## Scientific boundary

A complete entry record makes a join attempt retrospectively auditable; it does not prove that contact, a composite, or strict join exists.

The Lean source is complete at text level. Kernel elaboration and executed `#print axioms` results remain the external replay gate.
