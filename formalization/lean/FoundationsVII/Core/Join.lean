import FoundationsVII.Core.Contact

/-!
# Join candidates, certificates, obstructions, and scoped non-interaction

These are distinct records.  A candidate does not become a strict join by
construction, and a negative certificate is coverage-qualified.
-/

namespace FoundationsVII

structure JoinCandidate where
  candidateId : RecordId
  interaction : InteractionRecord
  compositeTheory : TheoryId
  comparisonBaseline : String
  deriving Repr, DecidableEq, BEq

namespace JoinCandidate

def WellFormed (candidate : JoinCandidate) : Prop :=
  InteractionRecord.WellFormed candidate.interaction ∧
  candidate.comparisonBaseline ≠ ""

instance (candidate : JoinCandidate) : Decidable (WellFormed candidate) := by
  unfold WellFormed
  infer_instance

theorem constructed_wellFormed (candidate : JoinCandidate)
    (hInteraction : InteractionRecord.WellFormed candidate.interaction)
    (hBaseline : candidate.comparisonBaseline ≠ "") : WellFormed candidate := by
  exact ⟨hInteraction, hBaseline⟩

end JoinCandidate

structure JoinCertificate where
  certificateId : CertificateId
  candidate : JoinCandidate
  objecthoodWitness : String
  retentionWitnesses : List String
  sourceWitnesses : List SourceId
  budgetWitnesses : List ResourceId
  strictnessWitness : String
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace JoinCertificate

def WellFormed (certificate : JoinCertificate) : Prop :=
  JoinCandidate.WellFormed certificate.candidate ∧
  certificate.objecthoodWitness ≠ "" ∧
  certificate.retentionWitnesses ≠ [] ∧
  certificate.sourceWitnesses ≠ [] ∧
  certificate.budgetWitnesses ≠ [] ∧
  certificate.strictnessWitness ≠ "" ∧
  certificate.audit.entries ≠ []

instance (certificate : JoinCertificate) : Decidable (WellFormed certificate) := by
  unfold WellFormed
  infer_instance

theorem constructed_wellFormed (certificate : JoinCertificate)
    (hCandidate : JoinCandidate.WellFormed certificate.candidate)
    (hObjecthood : certificate.objecthoodWitness ≠ "")
    (hRetention : certificate.retentionWitnesses ≠ [])
    (hSource : certificate.sourceWitnesses ≠ [])
    (hBudget : certificate.budgetWitnesses ≠ [])
    (hStrict : certificate.strictnessWitness ≠ "")
    (hAudit : certificate.audit.entries ≠ []) : WellFormed certificate := by
  exact ⟨hCandidate, hObjecthood, hRetention, hSource, hBudget, hStrict, hAudit⟩

end JoinCertificate

structure JoinObstruction where
  obstructionId : ObstructionId
  candidate : JoinCandidate
  kind : JoinObstructionKind
  witnessDescription : String
  escapeRoutes : List String
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace JoinObstruction

def WellFormed (obstruction : JoinObstruction) : Prop :=
  JoinCandidate.WellFormed obstruction.candidate ∧
  obstruction.witnessDescription ≠ "" ∧
  obstruction.escapeRoutes ≠ [] ∧
  obstruction.audit.entries ≠ []

instance (obstruction : JoinObstruction) : Decidable (WellFormed obstruction) := by
  unfold WellFormed
  infer_instance

theorem constructed_wellFormed (obstruction : JoinObstruction)
    (hCandidate : JoinCandidate.WellFormed obstruction.candidate)
    (hWitness : obstruction.witnessDescription ≠ "")
    (hEscape : obstruction.escapeRoutes ≠ [])
    (hAudit : obstruction.audit.entries ≠ []) : WellFormed obstruction := by
  exact ⟨hCandidate, hWitness, hEscape, hAudit⟩

end JoinObstruction

structure NonInteractionCertificate where
  certificateId : CertificateId
  leftTheory : TheoryId
  rightTheory : TheoryId
  coveredFamily : String
  familyClosed : Bool
  detectorId : DetectorId
  detectorPowerDescription : String
  budget : Cost
  horizon : Nat
  observedContact : Bool
  escapeRoutes : List String
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace NonInteractionCertificate

def WellFormed (certificate : NonInteractionCertificate) : Prop :=
  certificate.leftTheory ≠ certificate.rightTheory ∧
  certificate.coveredFamily ≠ "" ∧
  certificate.familyClosed = true ∧
  certificate.detectorPowerDescription ≠ "" ∧
  certificate.horizon > 0 ∧
  certificate.observedContact = false ∧
  certificate.escapeRoutes ≠ [] ∧
  certificate.audit.entries ≠ []

instance (certificate : NonInteractionCertificate) : Decidable (WellFormed certificate) := by
  unfold WellFormed
  infer_instance

theorem constructed_wellFormed (certificate : NonInteractionCertificate)
    (hDistinct : certificate.leftTheory ≠ certificate.rightTheory)
    (hFamily : certificate.coveredFamily ≠ "")
    (hClosed : certificate.familyClosed = true)
    (hDetector : certificate.detectorPowerDescription ≠ "")
    (hHorizon : certificate.horizon > 0)
    (hNoContact : certificate.observedContact = false)
    (hEscape : certificate.escapeRoutes ≠ [])
    (hAudit : certificate.audit.entries ≠ []) : WellFormed certificate := by
  exact ⟨hDistinct, hFamily, hClosed, hDetector, hHorizon, hNoContact,
    hEscape, hAudit⟩

theorem wellFormed_implies_no_observed_contact
    {certificate : NonInteractionCertificate}
    (h : WellFormed certificate) : certificate.observedContact = false :=
  h.2.2.2.2.2.1

end NonInteractionCertificate

end FoundationsVII
