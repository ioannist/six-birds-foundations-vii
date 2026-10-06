import FoundationsVII.Core.Ledgers

/-!
# Observer and instrument occupancy
-/

namespace FoundationsVII

structure ObserverOccupancyRecord where
  observerId : ObserverId
  sourceKind : SourceKind
  visibleInterfaces : List InterfaceId
  capacity : Cost
  occupied : Cost
  charged : Cost
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace ObserverOccupancyRecord

def WellFormed (record : ObserverOccupancyRecord) : Prop :=
  record.occupied ≤ record.capacity ∧
  record.visibleInterfaces ≠ [] ∧
  record.audit.entries ≠ []

instance (record : ObserverOccupancyRecord) : Decidable (WellFormed record) := by
  unfold WellFormed
  infer_instance

theorem constructed_wellFormed (record : ObserverOccupancyRecord)
    (hCapacity : record.occupied ≤ record.capacity)
    (hVisible : record.visibleInterfaces ≠ [])
    (hAudit : record.audit.entries ≠ []) : WellFormed record := by
  exact ⟨hCapacity, hVisible, hAudit⟩

end ObserverOccupancyRecord

end FoundationsVII
