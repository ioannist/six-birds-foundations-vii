import FoundationsVII.Core.Admission
import FoundationsVII.Core.Ledgers

/-!
# Contact surfaces, witnesses, and interaction records

Compatibility, witnessed crossing, and interaction status are kept separate.
No constructor in this module turns contact into a strict join.
-/

namespace FoundationsVII

structure ContactSurface where
  leftTheory : TheoryId
  rightTheory : TheoryId
  leftInterface : InterfaceId
  rightInterface : InterfaceId
  crossingRelation : String
  admissible : Bool
  deriving Repr, DecidableEq, BEq

namespace ContactSurface

def WellFormed (surface : ContactSurface) : Prop :=
  surface.leftTheory ≠ surface.rightTheory ∧
  surface.crossingRelation ≠ ""

instance (surface : ContactSurface) : Decidable (WellFormed surface) := by
  unfold WellFormed
  infer_instance

theorem constructed_wellFormed (surface : ContactSurface)
    (hDistinct : surface.leftTheory ≠ surface.rightTheory)
    (hRelation : surface.crossingRelation ≠ "") : WellFormed surface := by
  exact ⟨hDistinct, hRelation⟩

end ContactSurface

structure ContactWitness where
  surface : ContactSurface
  eventId : EventId
  sourceId : SourceId
  crossed : Bool
  payloadDescription : String
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace ContactWitness

def WellFormed (witness : ContactWitness) : Prop :=
  ContactSurface.WellFormed witness.surface ∧
  witness.surface.admissible = true ∧
  witness.crossed = true ∧
  witness.payloadDescription ≠ "" ∧
  witness.audit.entries ≠ []

instance (witness : ContactWitness) : Decidable (WellFormed witness) := by
  unfold WellFormed
  infer_instance

theorem constructed_wellFormed (witness : ContactWitness)
    (hSurface : ContactSurface.WellFormed witness.surface)
    (hAdmissible : witness.surface.admissible = true)
    (hCrossed : witness.crossed = true)
    (hPayload : witness.payloadDescription ≠ "")
    (hAudit : witness.audit.entries ≠ []) : WellFormed witness := by
  exact ⟨hSurface, hAdmissible, hCrossed, hPayload, hAudit⟩

end ContactWitness

structure InteractionRecord where
  interactionId : RecordId
  parents : List TheoryId
  contact : Option ContactWitness
  transitions : List AdmissionTransition
  sources : SourceLedger
  budgets : BudgetLedger
  status : InteractionStatus
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace InteractionRecord

def WellFormed (record : InteractionRecord) : Prop :=
  record.parents ≠ [] ∧
  record.audit.entries ≠ [] ∧
  ((record.status = InteractionStatus.witnessedContact ∨
      record.status = InteractionStatus.compositeFormed ∨
      record.status = InteractionStatus.strictJoin) →
    record.contact.isSome = true)

instance (record : InteractionRecord) : Decidable (WellFormed record) := by
  unfold WellFormed
  infer_instance

theorem constructed_wellFormed (record : InteractionRecord)
    (hParents : record.parents ≠ [])
    (hAudit : record.audit.entries ≠ [])
    (hContact : (record.status = InteractionStatus.witnessedContact ∨
      record.status = InteractionStatus.compositeFormed ∨
      record.status = InteractionStatus.strictJoin) →
      record.contact.isSome = true) : WellFormed record := by
  exact ⟨hParents, hAudit, hContact⟩

theorem strict_join_status_requires_contact {record : InteractionRecord}
    (h : WellFormed record)
    (hStatus : record.status = InteractionStatus.strictJoin) :
    record.contact.isSome = true := by
  exact h.2.2 (Or.inr (Or.inr hStatus))

end InteractionRecord

end FoundationsVII
