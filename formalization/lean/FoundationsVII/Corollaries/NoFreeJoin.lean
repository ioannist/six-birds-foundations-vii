import FoundationsVII.NoGo.Admission
import FoundationsVII.NoGo.Join

/-!
# Combined bootstrap and payment obstruction
-/

namespace FoundationsVII

/-- A first join is doubly blocked when the declared closed regime has neither
seed nor reachable generator and the positive-cost channel is unpaid. -/
theorem no_free_first_join_two_gate_obstruction
    {regime : AdmissionRegime}
    (hClosed : regime.closedFamily = true)
    (hNoSeed : ¬ AdmissionRegime.HasAdmittedSeed regime)
    (hNoGenerator : ¬ AdmissionRegime.HasReachableGenerator regime)
    (transitionId : TransitionId)
    (payment : NoGo.PaymentJoinCredit)
    (hUnpaid : NoGo.PaymentJoinCredit.PositiveUnpaid payment) :
    (¬ AdmissionRegime.LawfulFirstExtension regime transitionId) ∧
      (¬ NoGo.PaymentJoinCredit.Eligible payment) := by
  exact ⟨NoGo.NGVII_01_no_first_extension_without_seed_or_generator
      hClosed hNoSeed hNoGenerator transitionId,
    NoGo.NGVII_09_no_positive_cost_join_credit_without_payment payment hUnpaid⟩

/-- The two obstruction families have independent escape routes: a lawful seed
or generator handles bootstrap, while a paid or certified zero-cost channel
handles payment. -/
theorem seeded_and_paid_first_join_escape
    {regime : AdmissionRegime} {transitionId : TransitionId}
    (hPermitted : transitionId ∈ regime.permittedFirstExtensions)
    (hSeed : AdmissionRegime.HasAdmittedSeed regime)
    {payment : NoGo.PaymentJoinCredit}
    (hPayment : NoGo.PaymentJoinCredit.Eligible payment) :
    AdmissionRegime.LawfulFirstExtension regime transitionId ∧
      NoGo.PaymentJoinCredit.Eligible payment := by
  exact ⟨AdmissionRegime.admitted_seed_authorizes_first_extension
      hPermitted hSeed, hPayment⟩

end FoundationsVII
