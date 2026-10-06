import FoundationsVII.Join.Strictness
import FoundationsVII.Join.Budget

/-!
# Source-independent strict joins under finite budget
-/

namespace FoundationsVII

structure IndependentBudgetedJoin where
  evidence : StrictJoinEvidence
  payment : JoinPaymentLedger
  capacity : LiveJoinCapacity

namespace IndependentBudgetedJoin

structure Certified (profile : IndependentBudgetedJoin) : Prop where
  strictJoin : StrictJoinEvidence.Certified profile.evidence
  paymentSettled : JoinPaymentLedger.FullyPaid profile.payment
  capacityFeasible : LiveJoinCapacity.Feasible profile.capacity

/-- A certified independent strict join has both source and payment gates, and
its live count is bounded by the declared finite capacity. -/
theorem certified_has_independence_payment_and_capacity_bound
    {profile : IndependentBudgetedJoin}
    (h : Certified profile) :
    profile.evidence.sourceIndependent = true ∧
      profile.evidence.budgetSettled = true ∧
      (∀ entry, entry ∈ profile.payment.entries → JoinCostEntry.Credited entry) ∧
      profile.capacity.liveJoinCount ≤ profile.capacity.capacity := by
  have hGates := StrictJoinEvidence.certified_has_source_and_budget_gates h.strictJoin
  exact ⟨hGates.1, hGates.2,
    fun entry hEntry =>
      JoinPaymentLedger.fullyPaid_entries_are_credited h.paymentSettled hEntry,
    LiveJoinCapacity.finite_live_join_bound h.capacityFeasible⟩

/-- Source independence does not replace payment, and payment does not replace
source independence. -/
theorem source_and_payment_gates_remain_distinct
    {profile : IndependentBudgetedJoin}
    (h : Certified profile) :
    profile.evidence.sourceIndependent = true ∧
      JoinPaymentLedger.FullyPaid profile.payment := by
  exact ⟨(StrictJoinEvidence.certified_has_source_and_budget_gates
    h.strictJoin).1, h.paymentSettled⟩

end IndependentBudgetedJoin

end FoundationsVII
