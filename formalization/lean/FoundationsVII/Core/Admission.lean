import FoundationsVII.Core.Domain

/-!
# Admission transitions and prospective commitments
-/

namespace FoundationsVII

structure AdmissionTransition where
  transitionId : TransitionId
  source : DomainState
  target : DomainState
  sourceId : SourceId
  guardDescription : String
  guardSatisfied : Bool
  cost : Cost
  effectDescription : String
  sound : Bool
  executable : Bool
  fired : Bool
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace AdmissionTransition

def WellFormed (transition : AdmissionTransition) : Prop :=
  DomainState.Coherent transition.source ∧
  DomainState.Coherent transition.target ∧
  transition.source.theoryId = transition.target.theoryId ∧
  transition.target.timestamp ≥ transition.source.timestamp ∧
  transition.guardDescription ≠ "" ∧
  transition.effectDescription ≠ "" ∧
  (transition.executable = true → transition.sound = true) ∧
  (transition.fired = true → transition.executable = true) ∧
  (transition.target.occurrent = true → transition.fired = true) ∧
  transition.audit.entries ≠ []

instance (transition : AdmissionTransition) : Decidable (WellFormed transition) := by
  unfold WellFormed
  infer_instance

theorem constructed_wellFormed (transition : AdmissionTransition)
    (hSource : DomainState.Coherent transition.source)
    (hTarget : DomainState.Coherent transition.target)
    (hTheory : transition.source.theoryId = transition.target.theoryId)
    (hTime : transition.target.timestamp ≥ transition.source.timestamp)
    (hGuard : transition.guardDescription ≠ "")
    (hEffect : transition.effectDescription ≠ "")
    (hSound : transition.executable = true → transition.sound = true)
    (hFiring : transition.fired = true → transition.executable = true)
    (hOccurrence : transition.target.occurrent = true → transition.fired = true)
    (hAudit : transition.audit.entries ≠ []) : WellFormed transition := by
  exact ⟨hSource, hTarget, hTheory, hTime, hGuard, hEffect, hSound, hFiring,
    hOccurrence, hAudit⟩

theorem fired_implies_executable {transition : AdmissionTransition}
    (h : WellFormed transition) (hFired : transition.fired = true) :
    transition.executable = true := h.2.2.2.2.2.2.2.1 hFired

end AdmissionTransition

structure ProspectiveCommitment where
  commitmentId : CommitmentId
  registeredAt : Timestamp
  validFrom : Timestamp
  expiresAt : Timestamp
  futureTransition : TransitionId
  reservedBudget : Cost
  sourceId : SourceId
  permittedSourceKinds : List SourceKind
  preregistered : Bool
  disposition : AuditDisposition
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace ProspectiveCommitment

def WellFormed (commitment : ProspectiveCommitment) : Prop :=
  commitment.registeredAt ≤ commitment.validFrom ∧
  commitment.validFrom ≤ commitment.expiresAt ∧
  commitment.permittedSourceKinds ≠ [] ∧
  commitment.preregistered = true ∧
  commitment.audit.entries ≠ []

instance (commitment : ProspectiveCommitment) : Decidable (WellFormed commitment) := by
  unfold WellFormed
  infer_instance

theorem constructed_wellFormed (commitment : ProspectiveCommitment)
    (hRegistration : commitment.registeredAt ≤ commitment.validFrom)
    (hExpiry : commitment.validFrom ≤ commitment.expiresAt)
    (hSources : commitment.permittedSourceKinds ≠ [])
    (hPreregistered : commitment.preregistered = true)
    (hAudit : commitment.audit.entries ≠ []) : WellFormed commitment := by
  exact ⟨hRegistration, hExpiry, hSources, hPreregistered, hAudit⟩

end ProspectiveCommitment

end FoundationsVII
