import FoundationsVII.Join.Source

/-!
# Typed join costs, payment, zero-cost channels, and capacity bounds

The ledger is resource-typed.  Summing costs is a local accounting projection,
not a claim that all interaction currencies are universally commensurable.
-/

namespace FoundationsVII

inductive JoinCostKind where
  | interfaceAccess
  | parentRetention
  | jointNovelty
  | observerOccupancy
  | crossCost
  deriving Repr, DecidableEq, BEq, Inhabited

structure JoinCostEntry where
  resourceId : ResourceId
  kind : JoinCostKind
  amount : Cost
  paid : Cost
  refunded : Cost
  zeroCostCertified : Bool
  disposition : AuditDisposition
  deriving Repr, DecidableEq, BEq

namespace JoinCostEntry

def Credited (entry : JoinCostEntry) : Prop :=
  (entry.amount = 0 ∧ entry.zeroCostCertified = true) ∨
  entry.amount ≤ entry.paid + entry.refunded

def PositiveCost (entry : JoinCostEntry) : Prop := 0 < entry.amount

theorem paid_entry_is_credited {entry : JoinCostEntry}
    (h : entry.amount ≤ entry.paid + entry.refunded) : Credited entry :=
  Or.inr h

theorem certified_zero_cost_channel_is_credited {entry : JoinCostEntry}
    (hZero : entry.amount = 0)
    (hCertificate : entry.zeroCostCertified = true) : Credited entry :=
  Or.inl ⟨hZero, hCertificate⟩

theorem positive_cost_without_payment_or_zero_channel_is_not_credited
    {entry : JoinCostEntry}
    (hPositive : PositiveCost entry)
    (hPaid : entry.paid = 0)
    (hRefunded : entry.refunded = 0)
    (hZeroChannel : entry.zeroCostCertified = false) :
    ¬ Credited entry := by
  intro hCredit
  rcases hCredit with hZero | hCovered
  · exact (Nat.ne_of_gt hPositive) hZero.1
  · rw [hPaid, hRefunded] at hCovered
    have hAmountZero : entry.amount = 0 := Nat.eq_zero_of_le_zero hCovered
    exact (Nat.ne_of_gt hPositive) hAmountZero

theorem positive_observer_cost_cannot_be_hidden
    {entry : JoinCostEntry}
    (hKind : entry.kind = JoinCostKind.observerOccupancy)
    (hPositive : PositiveCost entry)
    (hPaid : entry.paid = 0)
    (hRefunded : entry.refunded = 0)
    (hZeroChannel : entry.zeroCostCertified = false) :
    ¬ Credited entry := by
  exact positive_cost_without_payment_or_zero_channel_is_not_credited
    hPositive hPaid hRefunded hZeroChannel

end JoinCostEntry

structure JoinPaymentLedger where
  entries : List JoinCostEntry
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace JoinPaymentLedger

def WellFormed (ledger : JoinPaymentLedger) : Prop :=
  ledger.entries ≠ [] ∧ ledger.audit.entries ≠ []

instance (ledger : JoinPaymentLedger) : Decidable (WellFormed ledger) := by
  unfold WellFormed
  infer_instance

def FullyPaid (ledger : JoinPaymentLedger) : Prop :=
  WellFormed ledger ∧
  ∀ entry, entry ∈ ledger.entries → JoinCostEntry.Credited entry

def typedCosts (ledger : JoinPaymentLedger) : List (JoinCostKind × Cost) :=
  ledger.entries.map fun entry => (entry.kind, entry.amount)

theorem fullyPaid_entries_are_credited {ledger : JoinPaymentLedger}
    (h : FullyPaid ledger) {entry : JoinCostEntry}
    (hMem : entry ∈ ledger.entries) : JoinCostEntry.Credited entry :=
  h.2 entry hMem

theorem fullyPaid_has_audit {ledger : JoinPaymentLedger}
    (h : FullyPaid ledger) : ledger.audit.entries ≠ [] := h.1.2

theorem typed_cost_projection_preserves_kinds (ledger : JoinPaymentLedger) :
    typedCosts ledger = ledger.entries.map fun entry => (entry.kind, entry.amount) :=
  rfl

end JoinPaymentLedger

structure LiveJoinCapacity where
  capacity : Cost
  liveJoinCount : Nat
  minimumPositiveCost : Cost
  deriving Repr, DecidableEq, BEq

namespace LiveJoinCapacity

def Feasible (profile : LiveJoinCapacity) : Prop :=
  0 < profile.minimumPositiveCost ∧
  profile.liveJoinCount * profile.minimumPositiveCost ≤ profile.capacity

theorem finite_live_join_bound {profile : LiveJoinCapacity}
    (h : Feasible profile) : profile.liveJoinCount ≤ profile.capacity := by
  have hOne : 1 ≤ profile.minimumPositiveCost :=
    Nat.one_le_iff_ne_zero.mpr (Nat.ne_of_gt h.1)
  have hScale : profile.liveJoinCount * 1 ≤
      profile.liveJoinCount * profile.minimumPositiveCost :=
    Nat.mul_le_mul_left profile.liveJoinCount hOne
  have hBound : profile.liveJoinCount * 1 ≤ profile.capacity :=
    Nat.le_trans hScale h.2
  simpa using hBound

end LiveJoinCapacity

end FoundationsVII
