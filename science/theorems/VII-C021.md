# VII-C021 — Reachability, guard activity, and horizon law

**Phase-2 asset:** `FVII-SCI02-C021-REACHABILITY-NEGATIVE-FORCE`  
**Terminal status:** `TERMINAL_PHASE2_ASSET_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`  
**Grade:** `REACHABILITY_SEPARATION_AND_NEGATIVE_FORCE_THEOREMS_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING`

## Formal surface

- Definitions: 18
- Theorems/lemmas/corollaries: 27
- Formalization targets: FT02, FT17
- Positive scenarios: TTW-S19
- Null/control scenarios: TTW-S20, TTW-S21
- Countermodels: CM-08, CM-09, CM-18
- New bounded witnesses: P2-W07, P2-W08, P2-W11

## Public theorem declarations

- `FoundationsVII.HorizonObservation.bounded_null_does_not_imply_unrestricted_nonoccurrence`
- `FoundationsVII.HorizonObservation.closed_family_detector_power_and_complete_null_are_sufficient`
- `FoundationsVII.HorizonObservation.detector_weakness_blocks_closed_family_negative_certificate`
- `FoundationsVII.HorizonObservation.finite_horizon_null_is_only_horizon_qualified`
- `FoundationsVII.HorizonObservation.open_family_cannot_receive_closed_family_negative_certificate`
- `FoundationsVII.Models.Finite.Phase2.coherent_transition_cardinality`
- `FoundationsVII.Models.Finite.Phase2.coherent_transitions_respect_operational_spine`
- `FoundationsVII.Models.Finite.Phase2.horizon_admissible_cardinality`
- `FoundationsVII.Models.Finite.Phase2.horizon_raw_cardinality`
- `FoundationsVII.Models.Finite.Phase2.negative_force_requires_closed_powerful_complete_null`
- `FoundationsVII.Models.Finite.Phase2.transition_raw_cardinality`
- `FoundationsVII.NoGo.NGVII_11_escape_fired_occurrence`
- `FoundationsVII.NoGo.NGVII_11_no_occurrence_from_reachability_alone`
- `FoundationsVII.OperationalProfile.firing_requires_reachability`
- `FoundationsVII.OperationalProfile.no_occurrence_from_reachability_alone`
- `FoundationsVII.OperationalProfile.occurrence_requires_firing`
- `FoundationsVII.OperationalProfile.reachability_does_not_imply_firing_or_occurrence`
- `FoundationsVII.OperationalProfile.reachability_requires_active_guard_and_execution`
- `FoundationsVII.OperationalProfile.soundness_does_not_imply_reachability`
- `FoundationsVII.ReachabilityWitness.operationallyCertified_includes_execution`
- `FoundationsVII.ReachabilityWitness.operationallyCertified_is_wellFormed`
- `FoundationsVII.ReachabilityWitness.replay_has_nonempty_trace`
- `FoundationsVII.ReachabilityWitness.replay_starts_at_initial`
- `FoundationsVII.ReachabilityWitness.replay_transitions_are_wellFormed`
- `FoundationsVII.TransitionTrace.trace_head`
- `FoundationsVII.TransitionTrace.trace_ne_nil`
- `FoundationsVII.TransitionTrace.transitions_wellFormed`

## Scientific boundary

A bounded null remains horizon-qualified unless family closure and detector power are certified.

The source proof is complete at the Lean text level. Kernel elaboration and `#print axioms` replay remain an explicit external execution gate.
