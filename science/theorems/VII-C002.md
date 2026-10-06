# VII-C002 — Lawful admission transition system

**Phase-2 asset:** `FVII-SCI02-C002-ADMISSION-TRANSITIONS`  
**Terminal status:** `TERMINAL_PHASE2_ASSET_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`  
**Grade:** `TRANSITION_CALCULUS_AND_REPLAY_THEOREMS_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`

## Formal surface

- Definitions: 14
- Theorems/lemmas/corollaries: 27
- Formalization targets: FT01, FT02, FT17
- Positive scenarios: TTW-S19
- Null/control scenarios: TTW-S20, TTW-S21
- Countermodels: CM-08, CM-09, CM-18
- New bounded witnesses: none

## Public theorem declarations

- `FoundationsVII.AdmissionReplay.append`
- `FoundationsVII.AdmissionReplay.two_step`
- `FoundationsVII.Models.Finite.Phase2.coherent_transition_cardinality`
- `FoundationsVII.Models.Finite.Phase2.coherent_transitions_respect_operational_spine`
- `FoundationsVII.Models.Finite.Phase2.transition_raw_cardinality`
- `FoundationsVII.ReachabilityWitness.operationallyCertified_includes_execution`
- `FoundationsVII.ReachabilityWitness.operationallyCertified_is_wellFormed`
- `FoundationsVII.ReachabilityWitness.replay_has_nonempty_trace`
- `FoundationsVII.ReachabilityWitness.replay_starts_at_initial`
- `FoundationsVII.ReachabilityWitness.replay_transitions_are_wellFormed`
- `FoundationsVII.TransitionTrace.trace_head`
- `FoundationsVII.TransitionTrace.trace_ne_nil`
- `FoundationsVII.TransitionTrace.transitions_wellFormed`
- `FoundationsVII.TypedAdmissionStep.Lawful.authorized_source_entry_exists`
- `FoundationsVII.TypedAdmissionStep.Lawful.executable_is_sound`
- `FoundationsVII.TypedAdmissionStep.Lawful.fired_is_executable`
- `FoundationsVII.TypedAdmissionStep.Lawful.occurrence_is_fired`
- `FoundationsVII.TypedAdmissionStep.Lawful.old_audit_entry_survives`
- `FoundationsVII.TypedAdmissionStep.Lawful.old_budget_entry_survives`
- `FoundationsVII.TypedAdmissionStep.Lawful.old_source_entry_survives`
- `FoundationsVII.TypedAdmissionStep.Lawful.sourced_financed_and_audited`
- `FoundationsVII.TypedAdmissionStep.admit_sets_admissible`
- `FoundationsVII.TypedAdmissionStep.expiry_clears_admissible`
- `FoundationsVII.TypedAdmissionStep.retraction_clears_admissible`
- `FoundationsVII.TypedAdmissionStep.revocation_clears_admissible`
- `FoundationsVII.TypedAdmissionStep.revocation_clears_current_admissibility_but_preserves_history`
- `FoundationsVII.TypedAdmissionStep.rollback_clears_current_admissibility_but_preserves_history`

## Scientific boundary

A well-typed transition calculus does not establish soundness of an undeclared domain-specific rule.

The source proof is complete at the Lean text level. Kernel elaboration and `#print axioms` replay remain an explicit external execution gate.
