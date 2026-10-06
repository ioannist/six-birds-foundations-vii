import FoundationsVII.Core.Ledgers
import FoundationsVII.Core.Domain

/-!
# Enablement records

An enablement record records attribution and execution.  This module does not
identify enablement with descent, sufficiency, causation, or endogeny.
-/

namespace FoundationsVII

structure EnablementRecord where
  enablementId : RecordId
  enabledOperation : String
  sourceId : SourceId
  executed : Bool
  targetBefore : DomainState
  targetAfter : DomainState
  budgets : BudgetLedger
  attribution : SourceKind
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace EnablementRecord

def WellFormed (record : EnablementRecord) : Prop :=
  record.enabledOperation ≠ "" ∧
  record.targetBefore.theoryId = record.targetAfter.theoryId ∧
  record.targetAfter.timestamp ≥ record.targetBefore.timestamp ∧
  record.audit.entries ≠ []

instance (record : EnablementRecord) : Decidable (WellFormed record) := by
  unfold WellFormed
  infer_instance

theorem constructed_wellFormed (record : EnablementRecord)
    (hOperation : record.enabledOperation ≠ "")
    (hTheory : record.targetBefore.theoryId = record.targetAfter.theoryId)
    (hTime : record.targetAfter.timestamp ≥ record.targetBefore.timestamp)
    (hAudit : record.audit.entries ≠ []) : WellFormed record := by
  exact ⟨hOperation, hTheory, hTime, hAudit⟩

end EnablementRecord

end FoundationsVII
