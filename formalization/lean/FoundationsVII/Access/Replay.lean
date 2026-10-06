import FoundationsVII.Access.Transitions
import FoundationsVII.Core.Reachability

/-!
# Reachability-witness replay and soundness

A reachability witness is accepted only when its declared transition list and
state trace replay under well-formed transitions.  The replay certificate still
asserts neither firing nor occurrence.
-/

namespace FoundationsVII

inductive TransitionTrace :
    DomainState → List AdmissionTransition → List DomainState → Prop
  | nil (state : DomainState) : TransitionTrace state [] [state]
  | cons {start middle : DomainState}
      {transition : AdmissionTransition}
      {tail : List AdmissionTransition}
      {trace : List DomainState}
      (hSource : transition.source = start)
      (hTarget : transition.target = middle)
      (hWellFormed : AdmissionTransition.WellFormed transition)
      (hTail : TransitionTrace middle tail trace) :
      TransitionTrace start (transition :: tail) (start :: trace)

namespace TransitionTrace

theorem trace_ne_nil {start : DomainState}
    {transitions : List AdmissionTransition} {trace : List DomainState}
    (h : TransitionTrace start transitions trace) : trace ≠ [] := by
  cases h <;> simp

theorem trace_head {start : DomainState}
    {transitions : List AdmissionTransition} {trace : List DomainState}
    (h : TransitionTrace start transitions trace) :
    trace.head? = some start := by
  cases h <;> rfl

theorem transitions_wellFormed {start : DomainState}
    {transitions : List AdmissionTransition} {trace : List DomainState}
    (h : TransitionTrace start transitions trace) :
    ∀ transition ∈ transitions, AdmissionTransition.WellFormed transition := by
  induction h with
  | nil => intro transition hMem; cases hMem
  | cons hSource hTarget hWellFormed hTail ih =>
      intro transition hMem
      cases hMem with
      | head => exact hWellFormed
      | tail _ hTailMem => exact ih transition hTailMem

end TransitionTrace

namespace ReachabilityWitness

/-- Exact replay of the witness's transition list against its declared trace. -/
def Replays (witness : ReachabilityWitness) : Prop :=
  TransitionTrace witness.initial witness.transitions witness.trace

structure OperationallyCertified (witness : ReachabilityWitness) : Prop where
  replays : Replays witness
  guardsSatisfied : witness.guardsSatisfied = true
  resourcesAvailable : witness.resourcesAvailable = true
  executable : witness.executable = true
  auditPresent : witness.audit.entries ≠ []

theorem replay_has_nonempty_trace {witness : ReachabilityWitness}
    (hReplay : Replays witness) : witness.trace ≠ [] :=
  TransitionTrace.trace_ne_nil hReplay

theorem replay_starts_at_initial {witness : ReachabilityWitness}
    (hReplay : Replays witness) :
    witness.trace.head? = some witness.initial :=
  TransitionTrace.trace_head hReplay

theorem replay_transitions_are_wellFormed {witness : ReachabilityWitness}
    (hReplay : Replays witness) :
    ∀ transition ∈ witness.transitions,
      AdmissionTransition.WellFormed transition :=
  TransitionTrace.transitions_wellFormed hReplay

theorem operationallyCertified_is_wellFormed {witness : ReachabilityWitness}
    (h : OperationallyCertified witness) : WellFormed witness := by
  exact ReachabilityWitness.constructed_wellFormed witness
    (replay_has_nonempty_trace h.replays)
    (replay_starts_at_initial h.replays)
    h.guardsSatisfied h.resourcesAvailable h.executable h.auditPresent

theorem operationallyCertified_includes_execution
    {witness : ReachabilityWitness}
    (_h : OperationallyCertified witness) :
    witness.executable = true :=
  _h.executable

end ReachabilityWitness

end FoundationsVII
