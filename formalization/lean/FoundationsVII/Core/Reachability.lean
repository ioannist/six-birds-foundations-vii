import FoundationsVII.Core.Admission

/-!
# Reachability witnesses

A reachability witness records an executable path.  It does not by itself assert
that the terminal transition fired or that an event occurred.
-/

namespace FoundationsVII

structure ReachabilityWitness where
  initial : DomainState
  transitions : List AdmissionTransition
  trace : List DomainState
  guardsSatisfied : Bool
  resourcesAvailable : Bool
  executable : Bool
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace ReachabilityWitness

def WellFormed (witness : ReachabilityWitness) : Prop :=
  witness.trace ≠ [] ∧
  witness.trace.head? = some witness.initial ∧
  witness.guardsSatisfied = true ∧
  witness.resourcesAvailable = true ∧
  witness.executable = true ∧
  witness.audit.entries ≠ []

instance (witness : ReachabilityWitness) : Decidable (WellFormed witness) := by
  unfold WellFormed
  infer_instance

theorem constructed_wellFormed (witness : ReachabilityWitness)
    (hTrace : witness.trace ≠ [])
    (hInitial : witness.trace.head? = some witness.initial)
    (hGuards : witness.guardsSatisfied = true)
    (hResources : witness.resourcesAvailable = true)
    (hExecutable : witness.executable = true)
    (hAudit : witness.audit.entries ≠ []) : WellFormed witness := by
  exact ⟨hTrace, hInitial, hGuards, hResources, hExecutable, hAudit⟩

end ReachabilityWitness

end FoundationsVII
