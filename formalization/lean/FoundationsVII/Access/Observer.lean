import FoundationsVII.Access.Reachability
import FoundationsVII.Core.Observer

/-!
# Observer/instrument occupancy and failed-admission settlement

This module closes VII-C029.  Native or endogenous formation credit requires
observer occupancy to be explicitly priced.  External provision and genuine
zero occupancy are separate positive escape cases.
-/

namespace FoundationsVII

namespace ObserverOccupancyRecord

def FullyPriced (record : ObserverOccupancyRecord) : Prop :=
  record.charged = record.occupied

def NativeOrEndogenous (record : ObserverOccupancyRecord) : Prop :=
  record.sourceKind = SourceKind.native ∨
  record.sourceKind = SourceKind.endogenous

def NativeFormationCredit (record : ObserverOccupancyRecord) : Prop :=
  ObserverOccupancyRecord.WellFormed record ∧
  NativeOrEndogenous record ∧
  FullyPriced record

def ExternalObserverCredit (record : ObserverOccupancyRecord) : Prop :=
  ObserverOccupancyRecord.WellFormed record ∧
  (record.sourceKind = SourceKind.observer ∨
    record.sourceKind = SourceKind.externalProvision) ∧
  FullyPriced record

theorem hidden_occupancy_is_not_fully_priced
    {record : ObserverOccupancyRecord}
    (hHidden : record.charged < record.occupied) :
    ¬ FullyPriced record := by
  intro hPriced
  change record.charged = record.occupied at hPriced
  rw [hPriced] at hHidden
  exact (Nat.lt_irrefl record.occupied) hHidden

theorem unpriced_observer_invalidates_native_formation_credit
    {record : ObserverOccupancyRecord}
    (hHidden : record.charged < record.occupied) :
    ¬ NativeFormationCredit record := by
  intro hCredit
  exact hidden_occupancy_is_not_fully_priced hHidden hCredit.2.2

theorem certified_external_observer_is_a_lawful_escape
    {record : ObserverOccupancyRecord}
    (hWellFormed : ObserverOccupancyRecord.WellFormed record)
    (hExternal : record.sourceKind = SourceKind.observer ∨
      record.sourceKind = SourceKind.externalProvision)
    (hPriced : record.charged = record.occupied) :
    ExternalObserverCredit record :=
  ⟨hWellFormed, hExternal, hPriced⟩

theorem certified_zero_occupancy_is_fully_priced
    {record : ObserverOccupancyRecord}
    (hOccupied : record.occupied = 0)
    (hCharged : record.charged = 0) :
    FullyPriced record := by
  rw [FullyPriced, hOccupied, hCharged]

theorem zero_occupancy_native_credit
    {record : ObserverOccupancyRecord}
    (hWellFormed : ObserverOccupancyRecord.WellFormed record)
    (hNative : NativeOrEndogenous record)
    (hOccupied : record.occupied = 0)
    (hCharged : record.charged = 0) :
    NativeFormationCredit record :=
  ⟨hWellFormed, hNative,
    certified_zero_occupancy_is_fully_priced hOccupied hCharged⟩

end ObserverOccupancyRecord

namespace BudgetEntry

def Conserved (entry : BudgetEntry) : Prop :=
  entry.spent + entry.occupied + entry.refunded = entry.allocated

instance (entry : BudgetEntry) : Decidable (Conserved entry) := by
  unfold Conserved
  infer_instance

def FailedAdmissionSettled (entry : BudgetEntry) : Prop :=
  entry.disposition = AuditDisposition.failed ∧ Conserved entry

theorem failed_unused_admission_full_refund_is_conserved
    {entry : BudgetEntry}
    (hFailed : entry.disposition = AuditDisposition.failed)
    (hSpent : entry.spent = 0)
    (hOccupied : entry.occupied = 0)
    (hRefunded : entry.refunded = entry.allocated) :
    FailedAdmissionSettled entry := by
  constructor
  · exact hFailed
  · simp [Conserved, hSpent, hOccupied, hRefunded]

theorem failed_admission_conservation_accounting
    {entry : BudgetEntry}
    (hFailed : entry.disposition = AuditDisposition.failed)
    (hConserved : entry.spent + entry.occupied + entry.refunded =
      entry.allocated) :
    FailedAdmissionSettled entry :=
  ⟨hFailed, hConserved⟩

theorem settled_failure_refund_equation
    {entry : BudgetEntry}
    (hSettled : FailedAdmissionSettled entry) :
    entry.spent + entry.occupied + entry.refunded = entry.allocated :=
  hSettled.2

end BudgetEntry

end FoundationsVII
